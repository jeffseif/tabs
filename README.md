# tabs

CLI tool for ukulele tabs

## Example

### Show the frets for a chord

```shell
> ./cli --chord=C
chord=C
  | - | - | ● | - | - | -       (C)
○ | - | - | - | - | - | -       (E)
○ | - | - | - | - | - | -       (C)
○ | - | - | - | - | - | -       (G)
```

```shell
> ./cli --chord=AB7
chord=A♯|B♭7
  | ● | - | - | - | - | -       (A♯|B♭)
  | ● | - | - | - | - | -       (F)
  | - | ● | - | - | - | -       (D)
  | ● | - | - | - | - | -       (G♯|A♭)
```

### Show the chord for frets

```shell
> ./cli --frets=0211
chord=Gmin7
  | ● | - | - | - | - | -       (A♯|B♭)
  | ● | - | - | - | - | -       (F)
  | - | ● | - | - | - | -       (D)
○ | - | - | - | - | - | -       (G)
```

### Show the chord and frets for notes

```shell
> ./cli --notes='D G A'
chord=Dsus4
○ | - | - | - | - | - | -       (A)
  | - | - | ● | - | - | -       (G)
  | - | ● | - | - | - | -       (D)
○ | - | - | - | - | - | -       (G)
```
