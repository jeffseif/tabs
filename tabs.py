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


@dataclasses.dataclass(frozen=True)
class Intervals:
    values: tuple[int, ...]
    suffix: str

    def __post_init__(self) -> None:
        assert sum(self.values) == 12

    def iter_root(
        self, notes: collections.abc.Iterable[Note]
    ) -> collections.abc.Iterator[Note]:
        for inversion in iter_rotation(it=notes):
            intervals = tuple(
                right - left for left, right in itertools.pairwise(inversion)
            )
            if intervals == self.values:
                yield inversion[0]


class Quality(Intervals, enum.Enum):
    DIMINISHED = ((3, 3, 6), "dim")
    DIMINISHED_SEVENTH = ((3, 3, 3, 3), "dim7")
    MINOR_SEVENTH = ((3, 4, 3, 2), "min7")
    MINOR = ((3, 4, 5), "min")
    DOMINANT_SEVENTH = ((4, 3, 3, 2), "dom7")
    MAJOR_SEVENTH = ((4, 3, 4, 1), "maj7")
    MAJOR = ((4, 3, 5), "")
    AUGMENTED = ((4, 4, 4), "aug")
    SUSPENDED_FOURTH = ((5, 2, 5), "sus4")
    SUSPENDED_SECOND = ((2, 5, 5), "sus2")


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
        def iter_line() -> collections.abc.Iterator[str]:
            for fret, string in more_itertools.always_reversible(
                zip(self.frets, self.strings)
            ):
                yield (
                    " | ".join(
                        (
                            " " if fret else "○",
                            *("-" * (fret - 1)),
                            *("●" * (bool(fret))),
                            *("-" * (HIGHEST_FRET - fret)),
                        )
                    )
                    + f"\t({string + fret!r})"
                )

        return "\n".join(iter_line())

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


@dataclasses.dataclass(frozen=True)
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
            if not len(sep := quality.value.suffix):
                notes_str = name
            elif name.endswith(quality.value.suffix):
                notes_str, _, _ = name.rpartition(sep)
            else:
                continue
            try:
                root = Note[notes_str]
            except KeyError:
                continue
            else:
                return cls(root=root, quality=quality)
        else:
            raise ValueError(f"Could not find the chord for {name=:s}")

    @classmethod
    def iter_from_notes(
        cls, notes: collections.abc.Iterable[Note]
    ) -> collections.abc.Iterator[Chord]:
        notes = tuple(notes)
        for quality in Quality:
            for root in quality.iter_root(notes=notes):
                yield cls(root=root, quality=quality)

    @property
    def ukulele_tab(self):
        return Tab.from_notes_strings(notes=self.notes, strings=UKULELE_STRINGS)


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    chords_parser = subparsers.add_parser(name="chords")
    chords_parser.add_argument("chords", nargs="+", type=str)

    frets_parser = subparsers.add_parser(name="frets")
    frets_parser.add_argument("frets", nargs="+", type=lambda s: tuple(map(int, s)))
    frets_parser.add_argument("--maximum-count", default=1, type=int)

    notes_parser = subparsers.add_parser(name="notes")
    notes_parser.add_argument("notes", nargs="+", type=str.split)
    notes_parser.add_argument("--maximum-count", default=1, type=int)

    args = parser.parse_args()

    def report(chord: Chord, tab: Tab) -> None:
        print(f"{chord=!r}")
        print(tab)
        print()

    if hasattr(args, "chords"):
        for name in args.chords:
            chord = Chord.from_name(name=name)
            report(chord=chord, tab=chord.ukulele_tab)
    elif hasattr(args, "frets"):
        for frets in args.frets:
            tab = Tab(frets=frets, strings=UKULELE_STRINGS)
            for chord in itertools.islice(
                Chord.iter_from_notes(notes=tab.notes), args.maximum_count
            ):
                report(chord=chord, tab=tab)
    elif hasattr(args, "notes"):
        for notes in args.notes:
            for chord in itertools.islice(
                Chord.iter_from_notes(notes=map(Note.__getitem__, notes)),
                args.maximum_count,
            ):
                report(chord=chord, tab=chord.ukulele_tab)
    else:
        raise ValueError("Either --chord or --frets or --notes must be provided")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
