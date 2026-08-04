# Benchmark-only intrinsic terminal result

The same binary links two mathematically equivalent terminal paths.

The control converts both vertical quartic inputs with an AVX2 16x16
transpose, calls the frozen zero-spill `R^-1` quartic BM with generated GT16
lambda order, and transposes the product back.  The candidate performs two
quadratic splits, QBM-PREWEIGHT, and the merge contract.  Merge intentionally
returns twice the quartic product in `R^-1`; the factor `1/2` is reserved for
inverse normalization.  Tests therefore compare the candidate directly with
twice the control, coefficient by coefficient modulo q.

Boundary, alternating, 1,000 random full-range cases, all three QBM schedules,
and `out==in` alias cases pass exactly.  The scalar suite additionally checks
full quotient-ring schoolbook multiplication.  ASan/UBSan passes with leak
detection disabled because LeakSanitizer is unavailable under the host ptrace
environment.

Ten 200,000-iteration AB/BA process samples record:

| Boundary | Median TSC | MAD | Delta |
| --- | ---: | ---: | ---: |
| Old then new: old | 601.868 | 1.150 | -- |
| Old then new: candidate | 553.674 | 0.735 | -8.007% |
| New then old: old | 603.351 | 2.613 | -- |
| New then old: candidate | 551.606 | 0.026 | -8.576% |
| Combined old | 601.868 | -- | -- |
| Combined candidate | 553.028 | -- | -8.115% |

The linked vector-at-a-time QBM is 211 bytes and spill-free.  Four-vector
interleaving is 549 bytes and contains six stack references caused by two
spilled data values, but lowers isolated QBM median from 223.282 to 216.867
TSC ticks.  Eight-vector interleaving grows to 1,264 bytes, has 33 stack data
references, and regresses to 270.198; it is rejected.

This clears only the direct terminal 5% cycle gate.  The CPU is an Intel Core
Ultra 7 155H under the powersave governor, not the frozen Ryzen host, and no
executable vertical forward/inverse exists.  Serialization, modulo-q compare,
and quadratic baseinv/keygen remain unmeasured.  Consequently the result does
not authorize assembly or production integration.
