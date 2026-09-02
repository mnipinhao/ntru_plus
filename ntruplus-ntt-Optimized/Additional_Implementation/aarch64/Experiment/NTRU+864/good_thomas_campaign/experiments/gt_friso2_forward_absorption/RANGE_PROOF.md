# Range, scale, and layout proof

For physical slot

```text
group = top*18 + row*2 + column/8
index = 24*group + 8*component + column%8
```

the candidate keeps component 0 and applies

```text
component 1: tau(top,row,column)
component 2: tau(top,row,column)^2
```

where

```text
alpha: tau = theta^(2*column + 32*row)
beta:  tau = 27*theta^(2*column + 32*row)
```

The generator emits constants in the exact M5R-D store order: rows 0..8 of
columns 0..7, followed by rows 0..8 of columns 8..15.  Thus no permutation or
lane extraction is introduced.

`prove_absorption.py` exhaustively checks every integer in `[-26306,26306]`
for every one of the 576 `(leaf,component)` scale uses: 30,305,088 exact
Algorithm-10 simulations.  Every output is congruent to the mathematical
product modulo 3457, remains R0, and has absolute value at most 3102, strictly
below `3q/2`.  All 288 `tau^3*z0=z_leaf` identities also pass.
