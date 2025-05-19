# tabs

CLI tool for ukulele tabs

## Example

### Show the frets for a chord

```shell
> ./cli --chord=C
chord=C

3         | - | - | ●           (C)
0       ○ | - | - | -           (E)
0       ○ | - | - | -           (C)
0       ○ | - | - | -           (G)
```

```shell
> ./cli --chord=AB7
chord=A♯|B♭7

1         | ● | -               (A♯|B♭)
1         | ● | -               (F)
2         | - | ●               (D)
1         | ● | -               (G♯|A♭)
```

### Show the chord for frets

```shell
> ./cli --frets=0211
chord=Gmin7

1         | ● | -               (A♯|B♭)
1         | ● | -               (F)
2         | - | ●               (D)
0       ○ | - | -               (G)
```

### Show the chord and frets for notes

```shell
> ./cli --notes='D G A'
chord=Dsus4

0       ○ | - | - | -           (A)
3         | - | - | ●           (G)
2         | - | ● | -           (D)
0       ○ | - | - | -           (G)
```
