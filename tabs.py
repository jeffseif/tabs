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

    @classmethod
    def from_short_name(cls, short_name: str) -> Quality:
        for quality in cls:
            if quality.value.short_name == short_name:
                return quality
        else:
            raise ValueError(f"Could not find quality for {short_name=:s}")


@dataclasses.dataclass
class Tab:
    frets: tuple[int, ...]
    strings: tuple[Note, ...]

    def __repr__(self) -> str:
        lines = []
        length = max(self.frets)
        for fret, string in zip(self.frets, self.strings):
            chars = [" " if fret else "○"]
            chars.extend("-" * (fret - 1))
            chars.extend(("●",) if fret else ())
            chars.extend("-" * (length - fret))
            lines.append(f"{fret:d}\t" + " | ".join(chars) + f"\t\t({string + fret!r})")

        return "\n".join(reversed(lines))


MAX_OFFSETS = 7


def unzip_to_tuples(it) -> collections.abc.Iterable[tuple]:
    return map(tuple, more_itertools.unzip(it))


def note_frets_cost(fret_set: tuple[Note, int]) -> tuple[int, ...]:
    notes, frets = unzip_to_tuples(fret_set)
    return (-len(set(notes)), statistics.mean(frets), statistics.variance(frets))


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
        number_of_notes = len(ordered)
        rotations = (
            itertools.islice(
                itertools.cycle(ordered), index, index + number_of_notes + 1
            )
            for index in range(number_of_notes)
        )

        for rotation in rotations:
            (root,), rotation = more_itertools.spy(rotation, n=1)
            intervals = tuple(
                itertools.starmap(
                    operator.sub, map(reversed, itertools.pairwise(rotation))
                )
            )
            for quality in Quality:
                if quality.value.intervals == tuple(intervals):
                    return cls(root=root, quality=quality)
        else:
            raise ValueError(f"Could not find the chord for {ordered:}")

    @classmethod
    def from_note_str(cls, note_str: str) -> Chord:
        return cls.from_notes(notes=map(Note.__getitem__, note_str.split()))

    def get_tabs_for_strings(self, strings: tuple[Note]) -> Tab:
        def iter_fret_for_string(
            string: Note,
        ) -> collections.abc.Iterator[tuple[Note, int]]:
            for offset in range(MAX_OFFSETS):
                if (note := string + offset) in self.notes:
                    yield (note, offset)

        note_frets: list[tuple[Note, int]] = min(
            itertools.product(*map(iter_fret_for_string, strings)),  # type: ignore
            key=note_frets_cost,  # type: ignore
        )
        _, frets = unzip_to_tuples(note_frets)
        return Tab(frets=frets, strings=strings)

    @property
    def ukulele_tabs(self):
        return self.get_tabs_for_strings(strings=(Note.G, Note.C, Note.E, Note.A))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chord")
    parser.add_argument("--notes")
    args = parser.parse_args()

    if args.chord is not None:
        chord = Chord.from_name(name=args.chord)
    elif args.notes is not None:
        chord = Chord.from_note_str(note_str=args.notes)
    else:
        raise ValueError("Either --chore or --notes must be provided")
    tabs = chord.ukulele_tabs
    print(f"{chord=!r}")
    print()
    print(tabs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
