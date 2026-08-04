# Quadratic factorization and scale law

For every generated terminal, `ord(alpha)=576`.  Since `576` divides
`(q-1)/2=1728`, `alpha` is a square.  It is not a fourth power because
`alpha^((q-1)/4)=-1`.  If `s^2=alpha`, then `s` is a nonsquare; because
`q=1 mod 4`, `-1` is a square and `-s` is also a nonsquare.  Hence both
`x^2-s` and `x^2+s` are irreducible.

The CRT maps are

```text
u+ = (a0+s*a2) + (a1+s*a3)x
u- = (a0-s*a2) + (a1-s*a3)x
```

and

```text
a0 = (u+0+u-0)/2       a2 = (u+0-u-0)/(2s)
a1 = (u+1+u-1)/2       a3 = (u+1-u-1)/(2s).
```

The external split is unit-scale.  The selected QBM reducer emits `R^-1`; its
paired inverse must absorb that Montgomery power exactly as the frozen
`c0-lazy R^-1` path does.  The generator records scale and Montgomery power per
factor rather than inferring them from the parent quartic representation.
