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

The paired inverse is now executable through coefficient-order stores.  It is
a lazy Cooley-Tukey schedule: only length 8 corrects, identity twiddle
Montgomery multiplies are omitted, and `/16` plus `/3` are folded into the
`F^n` postweight.  I0 (standalone merge) beats fused-first-load I1 by 0.782%
through the complete inverse.  I0 measures 1126.226 TSC ticks versus 911.862
for the same-binary frozen GT32 fused inverse, a 23.51% regression.  The
inverse deficit is now 214.364 ticks versus the terminal boundary's 48.840-tick
gain.

The vertical forward is now executable in four benchmark-only forms:
DFT3-first and NTT16-first, each with a materialized and fused boundary.  It
uses a natural-input, bit-reversed Cooley-Tukey NTT16.  The small `[-3,4]`
contract permits special R2, standard R2, and `F^-n` preweight to become four
ordinary lane-wise products followed by one identity Montgomery reduction;
the generator proves the signed-int16 raw bound.  Length 2 and 8 correct once,
length 4 and 16 remain lazy, and identity twiddles are omitted.

All four candidates pass 77 scalar component-oracle cases, in-place aliasing,
and materialized/fused representative differentials.  In two 20-sample runs
of one million calls per sample, the mean of the AB/BA medians is 466.072 TSC
for frozen GT32 and 719.857 for the intrinsic F1 fused producer.  F0
materialized, F0 fused, and F1 materialized measure 789.876, 795.646, and
750.758 respectively.

A benchmark-only GNU assembler CT16 now replaces the intrinsic core in the F1
producer.  Each eight-vector half-tile stays in registers through length 2, 4,
and 8; only then is it materialized for the cross-half length-16 layer.  The
kernel has fixed public loops, generated execution-order constants, and no
stack access or vector spill.  Direct CT16 drops from 286.151 to 239.911 TSC
(16.16%); the complete hybrid producer drops from 719.857 to 674.753 (6.27%).
Reversing benchmark order preserves the result.

Million-call direct buckets measure 283.176 TSC for the fused-linear frontend,
239.911 for the assembler CT16 arithmetic pass, 109.244 for the centered F0
DFT3 boundary, and 102.457 for standalone quadratic split.  These buckets overlap
when fused and therefore are not summed as a reconstructed producer, but they
show that the deficit is distributed across the mandatory frontend and CT16;
it is not explained by a single spill or materialization pass.

The assembler-assisted forward still regresses by 208.681 ticks instead of
saving the required
82.762.  Under the pre-existing local chain accounting, two forwards plus the
known terminal/inverse deficit miss parity by 582.886 ticks.  This is a direct
gate failure, not a production or promotion result: the host still uses the
powersave governor, but same-binary AB/BA evidence is decisive enough to stop
before assembly, serialization, baseinv, or KEM integration.
