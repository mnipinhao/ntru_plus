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

The benchmark-only intrinsic prototype now links both terminal paths in one
binary.  The old boundary performs two AVX2 16x16 transposes, the frozen
zero-spill quartic `R^-1` BM, and a reverse transpose.  The new boundary performs
two split passes, QBM-PREWEIGHT, and the scale-2 merge contract.  Exact
old/new congruence, alias cases, scalar differential, and ASan/UBSan pass.

Ten AB/BA process samples on the local Intel Core Ultra 7 155H record medians
of 601.868 TSC ticks for the old boundary and 553.028 for the four-vector QBM
candidate: an 8.115% improvement, clearing the direct 5% cycle gate.  The
vector-at-a-time QBM is spill-free; GCC spills two data values in the selected
four-vector schedule but it is still 2.87% faster.  The eight-vector schedule
spills heavily and is rejected.

This is preliminary local evidence, not a promotion result: the host uses the
powersave governor and differs from the frozen Ryzen benchmark machine.  There
is still no executable vertical forward/inverse chain, serialization consumer,
or quadratic baseinv/keygen benchmark.  Assembly remains unauthorized until
those caller gates pass in a same-binary `2F+B+I` measurement.
