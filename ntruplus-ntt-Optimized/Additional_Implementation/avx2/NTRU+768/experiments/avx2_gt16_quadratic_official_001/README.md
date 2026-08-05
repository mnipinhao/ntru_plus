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

A benchmark-only GNU assembler CT16 first replaced the intrinsic core in the
F1 producer.  The final complete F1 assembler now also owns the fused-linear
frontend, preweight, identity Montgomery reduction, DFT3, quadratic split, and
terminal-layout stores; it has no calls back into C.  Each generated group of
eight frontend vectors remains in registers through length 2, 4, and 8.  The
length-16 butterflies then feed DFT3 and split directly, without a complete
consumer-side store/reload boundary.

All assembler constants are generator-owned and emitted in execution order.
The complete symbol is a 2432-byte leaf with fixed public loops and addresses,
no stack access, no vector spill, no AVX-512 instruction, and an explicit
`vzeroupper`.  Guard-buffer, in-place alias, scalar component congruence,
bit-exact C/hybrid/full-assembler differential, and ASan/UBSan all pass.

In the final two 20-sample runs of one million calls, the mean of the forward
and reverse medians is 465.481 TSC for frozen GT32, 722.700 for intrinsic F1,
671.479 for hybrid F1, and 513.404 for complete-assembler F1.  Complete assembly
therefore saves 209.296 ticks (28.96%) versus the intrinsic producer and 158.075
ticks (23.54%) versus the hybrid.  Benchmark order preserves the result.

The full assembler result shows that the former 208.681-tick hybrid deficit was
substantially implementation overhead.  A follow-up transfer audit compared
the schedule with ML-KEM AVX2.  Montgomery correction fusion and four-way
`center_once` scheduling regress on this host, but ML-KEM's lazy-representation
principle transfers directly: length 2/4/8 now remain lazy, followed by one
parallel three-instruction `center10` checkpoint.  DFT3 outputs receive the
same fixed checkpoint before quadratic split.

The selected N5 range trace proves a terminal bound of 4143.  Under that widened
consumer contract, QBM `vpmaddwd` is bounded by 34,328,898, its exact reducer
image is `[-2252,2252]`, and narrowing is safe.  Differential tests compare N5
QBM against canonicalized inputs and carry both results through the complete
inverse; all 77 cases pass.  The faster but consumer-incompatible N4 candidate
measured 433.079 TSC preliminarily and was rejected at a 16257 terminal bound.

Final million-call AB/BA medians average 474.053 TSC for N5 versus 463.551 for
frozen GT32.  N5 saves 39.351 ticks (7.66%) against the previous 513.404-cycle
full assembler and leaves a 10.501-tick (2.27%) deficit.  Frozen GT32 already
contains four-way Montgomery ILP, global register renaming, parallel center10,
load/store overlap, and a lazy terminal.  Its only applicable missing ML-KEM
boundary trick—an internal entry without `vzeroupper`—regressed by 0.110 tick
in million-call AB/BA and was removed, leaving the frozen oracle unchanged.

GT16 still exceeds the existing 383.31 forward parity ceiling by 90.743 ticks;
the legacy local `2F+B+I` accounting remains 181.486 ticks behind before
serialization and baseinv.  The prototype therefore stays default-off and is
not integrated into the KEM.
