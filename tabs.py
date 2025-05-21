from __future__ import annotations
import argparse
import dataclasses
import collections.abc
import enum
import functools
import itertools
import operator
import statistics

import more_itertools


class Note(enum.Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[int]
    ) -> int:
        return len(last_values)

    def __repr__(self) -> str:
        return self.name if len(self.name) == 1 else "{:s}♯|{:s}♭".format(*self.name)

    def __lt__(self, other: Note) -> bool:
        return self.value < other.value

    def __add__(self, other: int) -> Note:
        value = (self.value + other) % 12
        return Note(value=value)

    __radd__ = __add__

    def __sub__(self, other: Note) -> int:
        return (self.value - other.value) % 12

    C = enum.auto()
    CD = enum.auto()
    D = enum.auto()
    DE = enum.auto()
    E = enum.auto()
    F = enum.auto()
    FG = enum.auto()
    G = enum.auto()
    GA = enum.auto()
    A = enum.auto()
    AB = enum.auto()
    B = enum.auto()


@dataclasses.dataclass
class IntervalsShortName:
    intervals: tuple[int, ...]
    short_name: str

    def __post_init__(self) -> None:
        assert sum(self.intervals) == 12


class Quality(IntervalsShortName, enum.Enum):
    DIMINISHED = ((3, 3, 6), "dim")
    MINOR_SEVENTH = ((3, 4, 3, 2), "min7")
    MINOR = ((3, 4, 5), "min")
    AUGMENTED = ((4, 2, 6), "aug")
    SEVENTH = ((4, 3, 3, 2), "7")
    MAJOR_SEVENTH = ((4, 3, 4, 1), "maj7")
    MAJOR = ((4, 3, 5), "")
    SUSPENDED_FOURTH = ((5, 2, 5), "sus4")
    SUSPENDED_SECOND = ((2, 5, 5), "sus2")  # This is a rotation of sus4


HIGHEST_FRET = 6


@dataclasses.dataclass
class Tab:
    frets: tuple[int, ...]
    strings: tuple[Note, ...]

    def __repr__(self) -> str:
        def pad(
            delimiter: str,
            s: collections.abc.Iterable[str],
        ) -> str:
            return delimiter + delimiter.join(s) + delimiter

        def iter_lines() -> collections.abc.Iterator[str]:
            yield ""
            yield pad(delimiter=" ", s=map(str, self.frets))
            yield ""
            yield pad(
                delimiter=" ",
                s=("○" if fret == 0 else " " for fret in self.frets),
            )
            yield pad(delimiter="=", s="=" * len(self.strings))
            for idx in range(1, HIGHEST_FRET):
                yield pad(
                    delimiter=" ",
                    s=("●" if fret == idx else "│" for fret in self.frets),
                )
                yield pad(delimiter="—", s="—" * len(self.strings))

        return "\n".join(iter_lines())

    @property
    def notes(self) -> set[Note]:
        return {string + fret for fret, string in zip(self.frets, self.strings)}


def unzip_to_tuples(it) -> collections.abc.Iterable[tuple]:
    return map(tuple, more_itertools.unzip(it))


def note_frets_cost(note_frets: list[tuple[Note, int]]) -> tuple[int, ...]:
    notes, frets = unzip_to_tuples(note_frets)
    return (
        # Maximize the number of notes covered
        -len(set(notes)),
        # Minimize the average fret number
        statistics.mean(frets),
        # Minimize the spread of frets
        statistics.variance(fret or statistics.mean(frets) for fret in frets),
    )


UKULELE_STRINGS = (Note.G, Note.C, Note.E, Note.A)


def iter_rotations(it: collections.abc.Sequence) -> collections.abc.Iterator[tuple]:
    n = len(it)
    for idx in range(n):
        yield tuple(itertools.islice(itertools.cycle(it), idx, idx + n + 1))


@dataclasses.dataclass
class Chord:
    root: Note
    quality: Quality

    def __repr__(self) -> str:
        return f"{self.root!r}{self.quality.value.short_name:s}"

    @functools.cached_property
    def notes(self) -> set[Note]:
        return {
            (self.root + interval)
            for interval in itertools.accumulate(self.quality.intervals)
        }

    @classmethod
    def from_name(cls, name: str) -> Chord:
        for quality in Quality:
            if len(sep := quality.value.short_name):
                note_str, _, _ = name.rpartition(sep)
            else:
                note_str = name
            try:
                root = Note[note_str]
            except KeyError:
                continue
            else:
                return cls(root=root, quality=quality)
        else:
            raise ValueError(f"Could not find chord for {name=:s}")

    @classmethod
    def from_notes(cls, notes: collections.abc.Iterable[Note]) -> Chord:
        ordered = sorted(set(notes))
        for quality in Quality:
            for rotation in iter_rotations(it=ordered):
                (root,), rotation = more_itertools.spy(rotation, n=1)
                intervals = tuple(
                    itertools.starmap(
                        operator.sub, map(reversed, itertools.pairwise(rotation))
                    )
                )
                if quality.value.intervals == intervals:
                    return cls(root=root, quality=quality)
        else:
            raise ValueError(f"Could not find the chord for {ordered:}")

    @classmethod
    def from_note_str(cls, note_str: str) -> Chord:
        return cls.from_notes(notes=map(Note.__getitem__, note_str.split()))

    @staticmethod
    def get_tabs_for_strings(notes: set[Note], strings: tuple[Note, ...]) -> Tab:
        def iter_note_fret(string: Note) -> collections.abc.Iterator[tuple[Note, int]]:
            for fret in range(HIGHEST_FRET):
                if (note := string + fret) in notes:
                    yield (note, fret)

        note_frets: list[tuple[Note, int]] = min(
            map(list, itertools.product(*map(iter_note_fret, strings))),
            key=note_frets_cost,
        )
        _, frets = unzip_to_tuples(note_frets)
        return Tab(frets=frets, strings=strings)

    @property
    def ukulele_tabs(self):
        return self.get_tabs_for_strings(notes=self.notes, strings=UKULELE_STRINGS)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chord")
    group.add_argument("--frets")
    group.add_argument("--notes")
    args = parser.parse_args()

    if args.chord is not None:
        chord = Chord.from_name(name=args.chord)
        tabs = chord.ukulele_tabs
    elif args.frets is not None:
        tabs = Tab(frets=tuple(map(int, args.frets)), strings=UKULELE_STRINGS)
        chord = Chord.from_notes(notes=tabs.notes)
    elif args.notes is not None:
        chord = Chord.from_note_str(note_str=args.notes)
        tabs = chord.ukulele_tabs
    else:
        raise ValueError("Either --chord or --frets or --notes must be provided")

    print(f"{chord=!r}")
    print(tabs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
