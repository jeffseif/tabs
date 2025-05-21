# tabs

CLI tool for ukulele tabs

## Example

### Show the frets for a chord

```shell
> ./cli --chord=C
chord=C

 0 0 0 3

 ○ ○ ○
=========
 │ │ │ │
—————————
 │ │ │ │
—————————
 │ │ │ ●
—————————
 │ │ │ │
—————————
 │ │ │ │
—————————
```

```shell
> ./cli --chord=AB7
chord=A♯|B♭7

 1 2 1 1


=========
 ● │ ● ●
—————————
 │ ● │ │
—————————
 │ │ │ │
—————————
 │ │ │ │
—————————
 │ │ │ │
—————————
```

### Show the chord for frets

```shell
> ./cli --frets=0211
chord=Gmin7

 0 2 1 1

 ○
=========
 │ │ ● ●
—————————
 │ ● │ │
—————————
 │ │ │ │
—————————
 │ │ │ │
—————————
 │ │ │ │
—————————
```

### Show the chord and frets for notes

```shell
> ./cli --notes='D G A'
chord=Dsus4

 0 2 3 0

 ○     ○
=========
 │ │ │ │
—————————
 │ ● │ │
—————————
 │ │ ● │
—————————
 │ │ │ │
—————————
 │ │ │ │
—————————
```
