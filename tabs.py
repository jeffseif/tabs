from __future__ import annotations
import argparse
import dataclasses
import collections.abc
import enum
import functools
import itertools
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


def iter_rotation(it: collections.abc.Iterable) -> collections.abc.Iterator[tuple]:
    ordered = sorted(set(it))
    for idx in range(n := len(ordered)):
        yield tuple(itertools.islice(itertools.cycle(ordered), idx, idx + n + 1))


@dataclasses.dataclass
class Intervals:
    values: tuple[int, ...]
    suffix: str

    def __post_init__(self) -> None:
        assert sum(self.values) == 12

    def get_root(self, notes: collections.abc.Iterable[Note]) -> Note:
        for inversion in iter_rotation(it=notes):
            intervals = tuple(
                right - left for left, right in itertools.pairwise(inversion)
            )
            if intervals == self.values:
                return inversion[0]
        else:
            raise ValueError(f"Could not find root for {notes=:}")


class Quality(Intervals, enum.Enum):
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


def unzip_to_tuples(it) -> collections.abc.Iterable[tuple]:
    return map(tuple, more_itertools.unzip(it))


def note_frets_cost(note_frets: list[tuple[Note, int]]) -> tuple[int, ...]:
    notes, frets = unzip_to_tuples(note_frets)
    return (
        # The number of missing notes
        -len(set(notes)),
        # The average fret number
        statistics.mean(frets),
        # The spread of frets
        statistics.variance(fret or statistics.mean(frets) for fret in frets),
    )


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

    @classmethod
    def from_notes_strings(cls, notes: set[Note], strings: tuple[Note, ...]) -> Tab:
        def iter_note_fret(string: Note) -> collections.abc.Iterator[tuple[Note, int]]:
            for fret in range(HIGHEST_FRET):
                if (note := string + fret) in notes:
                    yield (note, fret)

        note_frets: list[tuple[Note, int]] = min(
            map(list, itertools.product(*map(iter_note_fret, strings))),
            key=note_frets_cost,
        )
        _, frets = unzip_to_tuples(note_frets)
        return cls(frets=frets, strings=strings)

    @property
    def notes(self) -> set[Note]:
        return {string + fret for fret, string in zip(self.frets, self.strings)}


UKULELE_STRINGS = (Note.G, Note.C, Note.E, Note.A)


@dataclasses.dataclass
class Chord:
    root: Note
    quality: Quality

    def __repr__(self) -> str:
        return f"{self.root!r}{self.quality.value.suffix:s}"

    @functools.cached_property
    def notes(self) -> set[Note]:
        return {
            (self.root + interval)
            for interval in itertools.accumulate(self.quality.values)
        }

    @classmethod
    def from_name(cls, name: str) -> Chord:
        for quality in Quality:
            if len(sep := quality.value.suffix):
                notes_str, _, _ = name.rpartition(sep)
            else:
                notes_str = name
            try:
                root = Note[notes_str]
            except KeyError:
                continue
            else:
                return cls(root=root, quality=quality)
        else:
            raise ValueError(f"Could not find the chord for {name=:s}")

    @classmethod
    def from_notes(cls, notes: collections.abc.Iterable[Note]) -> Chord:
        notes = tuple(notes)
        for quality in Quality:
            try:
                root = quality.get_root(notes=notes)
            except ValueError:
                continue
            else:
                return cls(root=root, quality=quality)
        else:
            raise ValueError(f"Could not find the chord for {notes=:}")

    @property
    def ukulele_tabs(self):
        return Tab.from_notes_strings(notes=self.notes, strings=UKULELE_STRINGS)


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
        notes = map(Note.__getitem__, args.notes.split())
        chord = Chord.from_notes(notes=notes)
        tabs = chord.ukulele_tabs
    else:
        raise ValueError("Either --chord or --frets or --notes must be provided")

    print(f"{chord=!r}")
    print(tabs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
