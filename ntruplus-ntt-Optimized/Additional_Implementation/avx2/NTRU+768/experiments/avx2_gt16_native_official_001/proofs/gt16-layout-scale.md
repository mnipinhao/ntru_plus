# GT16 layout, wrap correction, and scale

Input and output coordinates are

```text
i = (16*i3 + 33*i16) mod 48
k = (16*k3 +  3*k16) mod 48
```

The native word is

```text
((branch*3+k3)*4+degree)*16+k16
```

so one degree plane and GT row is one horizontal YMM.

If `16*i3+33*i16=i+48*t`, the forward preweight obeys

```text
F^-i = F^(-16*i3) F^(-33*i16) beta^-t.
```

The generator emits the complete matrix and its row, column, and residual
factorization.  For every selected branch, 33 of 48 entries are covered by
the rank-one row/column factors; the remaining 15 entries use one distinct
branch-specific residual constant.  This is a useful structure, not a claim
that those 15 multiplies survive instruction selection.

The first pre-kernel ABI deliberately uses canonical component scale `s=1`
and Montgomery power zero.  This prevents a transform-only optimization from
silently transferring compensation into consumers.  Deferred non-unit scales
may be explored only as a separately type-checked candidate.
