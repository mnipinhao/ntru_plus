# NTRU+768 AVX2 quadratic-terminal GT16 experiment

Round 4C replaces each terminal `Fq[x]/(x^4-alpha)` with its two irreducible
quadratic factors.  This is the first GT16 terminal ABI that preserves the
vertical `k16` vector axis through multiplication:

```text
batch  = k3
vector = k16
lane   = 4*branch + 2*sign + quadratic_degree
```

All 192 generated `alpha` values have order 576, are squares, and are not
fourth powers.  For a selected `s^2=alpha`, both `s` and `-s` are nonsquares,
so `x^4-alpha=(x^2-s)(x^2+s)` is a product of two irreducible quadratics.

The scalar oracle passes split/merge, quadratic-versus-quartic multiplication,
quadratic base inversion, reducer scale/range, and full quotient-ring
schoolbook multiplication.  The selected static QBM uses weighted-operand
preparation, two `vpmaddwd`, and two five-instruction signed-32 Montgomery
reducers.  It costs an optimistic 22 instructions for each of 48 vectors.

The provisional complete-chain projection clears the 5% instruction gate, but
does not authorize assembly.  Its vertical inverse is a symmetry floor and its
frozen comparison uses a historical hybrid-inverse dynamic count.  Direct
serialization and the 384-norm baseinv path remain mandatory consumer gates.
Only a benchmark-only intrinsic QBM plus a concrete paired inverse schedule may
promote this result to an assembly experiment.
