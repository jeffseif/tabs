import collections.abc

from tabs import (
    UKULELE_STRINGS,
    Chord,
    Intervals,
    Note,
    Quality,
    Tab,
    iter_rotation,
    note_frets_cost,
    unzip_to_tuples,
)

import pytest


def test_notes() -> None:
    assert len(Note) == 12
    assert min(Note) == Note.C
    assert max(Note) == Note.B
    assert Note.C - Note.B == 1
    assert Note.B + 1 == Note.C


def test_iter_rotation() -> None:
    assert list(iter_rotation(it=range(5))) == [
        (0, 1, 2, 3, 4, 0),
        (1, 2, 3, 4, 0, 1),
        (2, 3, 4, 0, 1, 2),
        (3, 4, 0, 1, 2, 3),
        (4, 0, 1, 2, 3, 4),
    ]


@pytest.mark.parametrize(
    ("intervals", "notes", "expected"),
    (
        (Quality.MAJOR, {Note.C, Note.E, Note.G}, [Note.C]),
        (Quality.MAJOR, {Note.CD, Note.E, Note.A}, [Note.A]),
        (Quality.SUSPENDED_FOURTH, {Note.C, Note.F, Note.G}, [Note.C]),
        (Quality.SUSPENDED_SECOND, {Note.C, Note.F, Note.G}, [Note.F]),
        (
            Quality.DIMINISHED_SEVENTH,
            {Note.C, Note.DE, Note.FG, Note.A},
            [Note.C, Note.DE, Note.FG, Note.A],
        ),
        (Quality.MAJOR, {Note.C, Note.CD, Note.D}, []),
    ),
)
def test_interval_iter_root(
    intervals: Intervals,
    notes: collections.abc.Iterable[Note],
    expected: list[Note],
) -> None:
    assert list(intervals.iter_root(notes=notes)) == expected


def test_unzip_to_tuples() -> None:
    left, right = unzip_to_tuples(zip(range(5), range(5, 10)))
    assert left == tuple(range(5))
    assert right == tuple(range(5, 10))


@pytest.mark.parametrize(
    ("lesser", "greater"),
    (
        pytest.param(
            [(Note.C, 0), (Note.E, 0)], [(Note.C, 0), (Note.C, 0)], id="More notes"
        ),
        pytest.param(
            [(Note.C, 0), (Note.E, 0)], [(Note.C, 1), (Note.E, 1)], id="More left"
        ),
        pytest.param(
            [(Note.C, 1), (Note.E, 1)], [(Note.C, 0), (Note.E, 2)], id="Less spread"
        ),
    ),
)
def test_note_frets_cost(
    lesser: list[tuple[Note, int]], greater: list[tuple[Note, int]]
) -> None:
    assert note_frets_cost(note_frets=lesser) < note_frets_cost(note_frets=greater)


TABS_TO_NOTES = {
    (0, 0, 0, 0): {Note.G, Note.C, Note.E, Note.A},
    (0, 0, 0, 1): {Note.G, Note.C, Note.E, Note.AB},
    (0, 0, 1, 0): {Note.G, Note.C, Note.F, Note.A},
    (0, 1, 0, 0): {Note.G, Note.CD, Note.E, Note.A},
    (1, 0, 0, 0): {Note.GA, Note.C, Note.E, Note.A},
}


@pytest.mark.parametrize(("frets", "expected"), TABS_TO_NOTES.items())
def test_tab_notes(frets: tuple[int, int, int, int], expected: set[Note]) -> None:
    assert Tab(frets=frets, strings=UKULELE_STRINGS).notes == expected


CHORD_NAME_TO_NOTES = {
    "C": {Note.C, Note.E, Note.G},
    "D": {Note.D, Note.FG, Note.A},
    "E": {Note.E, Note.GA, Note.B},
    "F": {Note.F, Note.A, Note.C},
    "G": {Note.G, Note.B, Note.D},
    "A": {Note.A, Note.CD, Note.E},
    "B": {Note.B, Note.DE, Note.FG},
    "Cdim": {Note.C, Note.DE, Note.FG},
    "Cmin7": {Note.C, Note.DE, Note.G, Note.AB},
    "Cmin": {Note.C, Note.DE, Note.G},
    "Cdom7": {Note.C, Note.E, Note.G, Note.AB},
    "Cmaj7": {Note.C, Note.E, Note.G, Note.B},
}


@pytest.mark.parametrize(
    ("name", "expected"),
    CHORD_NAME_TO_NOTES.items(),
)
def test_chord_from_name(name: str, expected: set[Note]) -> None:
    assert Chord.from_name(name=name).notes == expected


def test_chord_from_name_raises() -> None:
    name = "Csuper"
    with pytest.raises(ValueError, match=f"Could not find the chord for {name=:s}"):
        Chord.from_name(name=name)


@pytest.mark.parametrize("notes", CHORD_NAME_TO_NOTES.values())
def test_chord_from_notes(notes: set[Note]) -> None:
    (chord,) = Chord.iter_from_notes(notes=notes)
    assert chord.notes == notes


@pytest.mark.parametrize("notes", CHORD_NAME_TO_NOTES.values())
def test_chord_ukulele_tabs(notes: set[Note]) -> None:
    (chord,) = Chord.iter_from_notes(notes=notes)
    assert chord.ukulele_tab.notes == notes


@pytest.mark.parametrize(
    ("notes", "expected"),
    (
        (
            {Note.C, Note.DE, Note.FG, Note.A},
            {"Cdim7", "DEdim7", "FGdim7", "Adim7"},
        ),
        (
            {Note.C, Note.E, Note.GA},
            {"Caug", "GAaug", "Eaug"},
        ),
        (
            {Note.C, Note.F, Note.G},
            {"Csus4", "Fsus2"},
        ),
        (
            {Note.C, Note.D, Note.G},
            {"Csus2", "Gsus4"},
        ),
    ),
)
def test_notes_to_multiple_chords(notes: set[Note], expected: set[str]) -> None:
    chords = set(Chord.iter_from_notes(notes=notes))
    assert set(chords) == set(map(Chord.from_name, expected))
    assert all(chord.notes == notes for chord in chords)
