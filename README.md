# tabs

CLI tool for ukulele tabs

## Example

### Show the tab for chords

```shell
> ./cli chords Amin D G Emin7
chord=Amin
○ | - | - | - | - | - | -       (A)
○ | - | - | - | - | - | -       (E)
○ | - | - | - | - | - | -       (C)
  | - | ● | - | - | - | -       (A)

chord=D
○ | - | - | - | - | - | -       (A)
  | - | ● | - | - | - | -       (F♯|G♭)
  | - | ● | - | - | - | -       (D)
  | - | ● | - | - | - | -       (A)

chord=G
  | - | ● | - | - | - | -       (B)
  | - | - | ● | - | - | -       (G)
  | - | ● | - | - | - | -       (D)
○ | - | - | - | - | - | -       (G)

chord=Emin7
  | - | ● | - | - | - | -       (B)
○ | - | - | - | - | - | -       (E)
  | - | ● | - | - | - | -       (D)
○ | - | - | - | - | - | -       (G)
```

### Show the chords for frets

```shell
> ./cli frets --maximum-count=2 0013
chord=Csus4
  | - | - | ● | - | - | -       (C)
  | ● | - | - | - | - | -       (F)
○ | - | - | - | - | - | -       (C)
○ | - | - | - | - | - | -       (G)

chord=Fsus2
  | - | - | ● | - | - | -       (C)
  | ● | - | - | - | - | -       (F)
○ | - | - | - | - | - | -       (C)
○ | - | - | - | - | - | -       (G)
```

### Show the chords and frets for notes

```shell
> ./cli notes --maximum-count=4 'C DE FG A'
chord=Cdim7
  | - | - | ● | - | - | -       (C)
  | - | ● | - | - | - | -       (F♯|G♭)
  | - | - | ● | - | - | -       (D♯|E♭)
  | - | ● | - | - | - | -       (A)

chord=D♯|E♭dim7
  | - | - | ● | - | - | -       (C)
  | - | ● | - | - | - | -       (F♯|G♭)
  | - | - | ● | - | - | -       (D♯|E♭)
  | - | ● | - | - | - | -       (A)

chord=F♯|G♭dim7
  | - | - | ● | - | - | -       (C)
  | - | ● | - | - | - | -       (F♯|G♭)
  | - | - | ● | - | - | -       (D♯|E♭)
  | - | ● | - | - | - | -       (A)

chord=Adim7
  | - | - | ● | - | - | -       (C)
  | - | ● | - | - | - | -       (F♯|G♭)
  | - | - | ● | - | - | -       (D♯|E♭)
  | - | ● | - | - | - | -       (A)
```
