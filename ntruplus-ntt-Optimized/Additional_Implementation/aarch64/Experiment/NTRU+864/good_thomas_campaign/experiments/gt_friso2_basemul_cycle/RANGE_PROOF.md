# Range and Montgomery-scale proof

Both kernels consume the M5R-D/M5U-A bounds:

```text
|component 0| <= 26306
|component 1/2| <= 5185
```

The direct schedule forms:

```text
p0 = a0*b0 + z0*(a1*b2+a2*b1)
p1 = a0*b1 + a1*b0 + z0*a2*b2
p2 = a0*b2 + a1*b1 + a2*b0
```

For `z0=9`, the largest absolute accumulator is `1,175,921,686`; for
`z0=3`, it is `853,310,986`.  Both are below `2^31`.  The exact
`-qinv/add` envelope proves the first R-minus-1 reduction fits signed
halfwords.  Multiplication by `RSQ=R^2` and the final Montgomery reduction
returns R0.  BaseMulAdd includes `c*R` in that same final wide accumulator.

The staged schedule uses `z0*R = -1323/-441`, reduces its two initial cross
terms to R-minus-1, reconstructs an R0 wide accumulator, and reaches the same
pre-finish R-minus-1 scale.  `prove_ranges.py` machine-checks both schedules.
