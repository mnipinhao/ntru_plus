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

A subsequent ML-KEM-style global-scheduling probe keeps the N5 arithmetic and
frontend unchanged, but peels the identity length-16 column, hoists both
twiddle bases, interleaves the three independent Montgomery chains, and lets
the two DFT3 blocks consume renamed butterfly sums without the former three
register copies per column.  Two- and four-output frontend interleaving both
regressed and were rejected.  The surviving tail candidate passes all seven
forward candidates, alias, lazy-QBM, complete-inverse, sanitizer, and linked
object audits.  Two stable million-call AB/BA runs average 474.615 TSC for the
original full assembler and 469.944 for the scheduled candidate, a 4.671-tick
(0.984%) saving; frozen GT32 averages 460.680.  Because the improvement remains
just below the 1% selection threshold and the GT16 deficit is still 2.01%, the
new symbol remains a benchmark-only research candidate rather than replacing
the selected implementation.  The comparison uses one shared static scratch;
separate scratch page offsets produced a repeatable 4 KiB-alias-sensitive
outlier and are not used for the reported result.

The alternative lane-`i16` layout was then tested at its first crossover gate
without changing the selected producer.  One YMM represents one fixed
branch/degree plane across all 16 transform positions; AVX2 lane permutations,
masks, and vector twiddle tables implement the four NTT16 layers.  A three-row
version interleaves three independent transforms.  It passes 273 cross-layout
mod-q cases and exact one-row/three-row differential.  A directional 2,000-call
short run over 48 logical transforms records 249.361 TSC for the existing
cross-register CT16, 796.040 for single-row lane-`i16`, and 693.803 for the
three-row schedule.  Three-row interleaving helps by 12.84%, but the result is
still 2.78x the existing layout.  Seven static vector stack references in the
compiler-generated x3 batch cannot account for the 444-tick deficit; even its
shuffle/arithmetic floor loses the existing 16-plane SIMD batching.  Per the
experiment-A stop rule, register-resident 3x16+DFT3, layout conversion, and a
new frontend table are not implemented.  These numbers are screening data,
not a formal 100,000-iteration benchmark.

The next isolated probe applies Official's operation-class scheduling and SSA
renaming to exactly one selected-N5 length-2/4/8 tile.  It passes 389
bit-exact cases, removes nine dynamic instructions (129 to 120), and measures
32.529 versus 32.709 TSC in a directional 2,000-call run: a real but small
0.55% tile gain, so it remains isolated pending a user-requested formal run.

Removing the terminal checkpoint (N4) is not mathematically forbidden.  The
generated consumer trace now proves that its +/-16257 input still leaves QBM's
largest `vpmaddwd` accumulator at 528,580,098 and the 32-bit reducer/`packssdw`
safe.  The obstacle is the unchanged inverse ABI: QBM can then emit
[-9793,9793], the merge reaches [-19586,19586], and the next int16 butterfly
reaches [-39172,39172].  A benchmark-only wide-QBM therefore absorbs an exact
centering repair and passes 256 representative/inverse cases, proving the
rewrite is possible.  The direct repair costs 160.770 TSC in a short run,
however, versus approximately 40.974 TSC indicated by the historical N4 and
N5 runs (not a same-run comparison).  It currently moves and enlarges the
reduction cost rather than eliminating it.

Three Official-style consumer experiments then test the N4 boundary directly.
A hand-scheduled four-vector QBM keeps four independent `c1` accumulators live
and reduces paired `c0/c1` values together.  In a directional 2,000-call run it
improves plain wide QBM by 2.41% and centered wide QBM by 9.54%.  A separate
inverse assembly keeps length-4/8 in each eight-vector tile resident and uses
one store/reload boundary for length-16; the boundary is unavoidable under the
current ABI because one `k3` row contains sixteen complete YMM values.

The most aggressive kernel performs QBM, quadratic merge, and inverse
length-2 without a QBM store.  It is exact, but loses the four-way QBM ILP and
regresses the full consumer by 2.78%.  The best combination instead retains a
centered benchmark boundary between the four-way QBM assembly and inverse
assembly.  It measures 1438.895 versus 1492.364 TSC through the complete
inverse tail, a directional 3.58% improvement.  This hybrid is retained for a
future formal benchmark; the direct register-fusion schedule is rejected.

A same-binary directional comparison also aligns all three backends at their
native multiplication-plus-scaled-inverse boundary.  Over 2,000 calls,
Official measures 733.570 TSC, frozen GT32 measures 1195.545 TSC, and the
GT16 hybrid measures 1435.543 TSC.  Thus the hybrid remains 20.08% behind
frozen GT32 and 95.69% behind Official on this consumer boundary.  These are
short-run routing numbers, not formal promotion measurements.

The complete GT16 inverse is now also executable as benchmark-only assembly.
`round4c_inverse_full_asm` covers quadratic merge and inverse length-2, the
register-resident length-4/8 plus length-16 boundary, inverse DFT3/postweight,
special R2/top-CRT merge, and coefficient-order stores.  Its stage-1 and
finish subentries allow independent differential testing.  All entries are
bit-exact for 1,006 canonical cases, 256 wide-consumer cases, and the in-place
alias case; ASan/UBSan also pass.  Parallel low/high merge and three-way
Montgomery scheduling reduce the first assembly draft substantially, but the
short-run result remains placement-sensitive and never establishes a win over
the existing C-stage1/asm-NTT16/C-tail hybrid.  The full assembly is therefore
retained as a correctness and scheduling control, not selected for integration.

The next consumer variant keeps QBM in its native `R^-1` domain and removes
the separate full-array QBM canonicalization pass.  The two int32 Montgomery
reducers remain necessary to narrow `vpmaddwd`; they are not scale-restoration
passes.  Instead, the lazy representatives remain int16-safe through the
quadratic merge, are repaired once there, and require only one correction
after inverse length-2.  The existing generated final CRT constants already
absorb the outstanding Montgomery scale.  This path is exact for all 256 wide
consumer cases.  In a directional 2,000-call run it measures 1383.521 TSC with
the hybrid tail and 1374.480 TSC with the complete assembly, versus 1434.724
for the previous centered hybrid.  The best local saving is therefore about
4.2%; the remaining gaps are 14.85% to frozen GT32 and 87.95% to Official on
the native multiplication-plus-inverse boundary.  A formal benchmark has not
been requested or run.

The selected stage-1 now hoists both shuffle masks and the center10 vector,
uses a fixed 24-entry counted loop instead of a sentinel branch, and calls an
internal no-`vzeroupper` stage-1 entry from the full path.  A subsequent short
run measures the lazy full-assembly consumer at 1373.002 TSC, with directional
gaps of 14.40% to frozen GT32 and 87.43% to Official.  A two-column DFT3
software pipeline was also implemented and verified without spills, but
regressed to 1385.515 TSC; it was therefore reverted.
