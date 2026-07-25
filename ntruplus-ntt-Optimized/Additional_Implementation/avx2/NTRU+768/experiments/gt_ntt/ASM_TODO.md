# AVX2 GT assembly implementation and optimization TODO

This document tracks the work required to turn the verified AVX2 intrinsic
forward-NTT baseline into a complete NTRU+768 assembly pipeline.  It separates
verified contracts from candidates and open design work.

Status markers:

- `[x]` verified by an implementation and a differential/range test.
- `[~]` selected candidate, not yet a production contract.
- `[ ]` unresolved or not implemented.

## Fixed platform and algebra contracts

- [x] Ring: `Z_3457[X] / (X^768 - X^384 + 1)`.
- [x] Coefficients and persistent SIMD state use signed 16-bit lanes.
- [x] AVX2 provides 16 signed int16 lanes and 16 architectural YMM registers.
- [x] Target benchmark CPU: AMD Ryzen 7 9700X, `znver5`.
- [x] The local Slothy checkout has no x86 model; instruction scheduling and
  register allocation must be designed and audited manually.
- [x] The portable GT reference and intrinsic prototype define the forward-NTT
  mathematical relation.
- [x] The canonical stage-3+4+5 ASM uses the KPQC-compatible packed-int16
  Barrett checkpoint with exact image `[0,q]`.
- [x] A benchmark-only three-instruction centered checkpoint is exhaustively
  verified over `[-8(q-1),8(q-1)]` and returns `[-3080,3079]`.

The implementation may use the high and low halves of a 16x16 product, but it
should not widen persistent data to eight int32 lanes unless a measured region
shows a net benefit.

## Whole-pipeline layout contract

### Internal transform layout

- [x] Eight natural streams use lanes
  `[branch0 lane0..3 | branch1 lane0..3]`.
- [x] DFT3 output rows are `row0`, `row1`, and `row2`.
- [x] `row01[Q] = [row0.Q streams8 | row1.Q streams8]`.
- [x] The singleton is packed as
  `row2_packed[q] = [row2.Q=q | row2.Q=q+16]` after stage 1.
- [x] Stage 1+2 uses four-vector stripes
  `Q={q,q+8,q+16,q+24}`.
- [x] Stage 3+4+5 consumes one independent eight-vector block.

### Candidate external NTT-domain layout

- [~] Use 192 quartic terminal blocks:
  `2 branches * 96 blocks = 12 batches * 16 blocks`.
- [~] Store each batch in structure-of-arrays form:

  ```text
  YMM0 = c0 of terminal blocks 0..15
  YMM1 = c1 of terminal blocks 0..15
  YMM2 = c2 of terminal blocks 0..15
  YMM3 = c3 of terminal blocks 0..15
  ```

- [x] The forward ASM prototype implements and tests the exact mapping.  For
  DFT3 row `k3=0..2`, NTT32 slot `Q=0..31`, branch `b=0..1`, and quartic
  coefficient `c=0..3`:

  ```text
  batch       = 4*k3 + floor(Q/8)             // 0..11
  lane        = 8*b + (Q mod 8)               // 0..15
  output word = 64*batch + 16*c + lane
  ```

  Thus one batch is exactly eight consecutive Q values from each of two
  branches; its four YMM vectors hold `c0`, `c1`, `c2`, and `c3`.
- [x] The mapping oracle relates this layout to the verified row-bitrev output:

  ```text
  j = (32*k3 + 3*Q) mod 96
  soa[64*batch + 16*c + lane] = rowbitrev[384*b + 4*j + c]
  ```

- [x] Pack lambda and `lambda*qinv` in the same 16-block order.
- [x] Pointwise multiplication consumes four YMM values directly and emits the
  same layout.
- [x] Forward NTT fuses the required transpose into its final stores.
- [x] The scheduled inverse consumes SoA directly and fuses the reverse mapping
  into its first loads/final stores.
- [x] Prove and exhaustively round-trip the complete coefficient-to-batch
  mapping for all 768 positions.
- [x] Compare total forward + basemul + inverse cycles against the production
  row-bitrev pipeline and KPQC Final baseline; the latest GT full-polymul gap is
  1.308x.

There must not be a standalone 768-coefficient transpose pass between forward
NTT and pointwise multiplication, or between pointwise multiplication and the
inverse NTT.

## Arithmetic tables

- [x] Forward twist and omega32 values match the AArch64 GT reference.
- [x] Prepack every forward fixed factor as `(factor*qinv, factor)`, including
  the 16 slot-pair x 3-row frontend table.
- [x] Prepack GT input CRT byte offsets as `16 x 6 uint16`; the ASM hot loop has
  no runtime `% 96` arithmetic.
- [x] Encode row01 stage-3+4+5 twiddles as full-lane repeats.
- [x] Encode singleton stage-3+4+5 twiddles as
  `[twiddle(Q) x8 | twiddle(Q+16) x8]`.
- [x] Generate the candidate SoA lambda table in physical batch order.
- [x] Add a generator/checker so table changes are reproducible rather than
  hand-edited.

## Forward NTT assembly regions

### Frontend slot-pair

- [x] Implement top split and twist for one `(Q,Q+1)` pair.
- [x] Process the two slots in the two 128-bit halves of each YMM and interleave
  all three independent `n3` Montgomery chains.
- [x] Keep three low and three high YMM live through top split, then reuse their
  registers for packed branch streams and twist corrections.
- [x] Schedule the DFT3 Montgomery chain while computing `r0`, `x0-x2`, and
  `x0-x1`.
- [x] Store/transpose DFT3 results immediately; do not carry outputs across
  frontend iterations.
- [x] Audit the actual GCC 16 object: intrinsic frontend has no stack spill but
  spends work on runtime mapping/twist construction; the 518-byte linked ASM
  frontend has zero stack traffic/calls and removes that construction.

### NTT32 stage 1+2

- [x] Process one four-vector row01 stripe at a time.
- [x] Interleave independent Montgomery chains at each dependency level to hide
  latency without exceeding the register budget.
- [x] Keep the Montgomery `R` multiplication in the canonical symbol: it is
  congruent to identity but also reduces the lazy high operand.
- [x] Evaluate a signed identity reducer at those exact `R` sites.  Exhaustive
  bounds give `[-2179,2178]` for the stage1 input interval and
  `[-2359,2359]` for the stage2 interval, preserving the existing
  `4(q-1)`/`5(q-1)` lazy contracts.
- [x] Store stage-2 results in the consumer's block order.
- [x] Replace the GCC 16 stage1+2 symbol's five constant spill/reloads with
  YMM9..YMM15 constants.  The 423-byte linked ASM symbol has zero stack
  traffic/calls and is byte-exact at the scratch boundary.
- [x] Fuse frontend and stage1+2 behind a 970-byte linked entry with one aligned
  1536-byte semantic scratch, no internal calls, and one terminal
  `vzeroupper`.
- [x] Pipeline the next pair's CRT-indexed loads into the current DFT3 tail.
  Current outputs stay in YMM6..YMM10 while dead YMM0..YMM5 receive the next
  three low/high inputs; table-indexed mapping and the semantic scratch remain
  unchanged.
- [x] Measure u2 and u4 schedules.  Canonical producer means are
  412.58/411.67 cycles versus 425.93; with the identity reducer they are
  404.05/404.30 versus 418.13.  u2 is 2183 linked bytes while u4 is 3847.
- [~] Select u2 for the existing SoA pipeline.  Full polynomial multiplication
  is 3141.62 cycles versus 3146.69 for u4 and 3219.54 canonical GT.
- [x] Evaluate a stripe-first zero-handoff producer.  It generates pair
  A=`(q,q+16)` and pair B=`(q+8,q+24)`, keeps A's three stage-1 values live,
  and writes stage2 directly.  Its GCC 16/GNU-as linked symbol is 1194 bytes
  (`0x4aa`); it is
  exact and stack-free, but the final forward/reverse 1M-iteration check is
  497.41/497.49 versus 425.40/425.71 cycles, 16.86%--16.93% slower.
- [x] Evaluate a 768-byte half-handoff producer.  It temporarily stores only
  pair A's three YMM values in their eventual stage2 slots and reloads them
  after pair B.  Its GCC 16/GNU-as linked symbol is 1252 bytes (`0x4e4`); it is exact and
  stack-free, but 499.46/499.48 cycles is 17.33%--17.41% slower than
  canonical.
- [x] Close the copy-elimination candidate at the current packing.  The hot
  1536-byte L1 handoff is cheaper than the extra cross-half packing and live
  range pressure.  Do not reopen it without a materially different mapping or
  a producer/consumer fusion that also removes those costs.

### NTT32 stage 3+4+5

- [x] Keep eight data YMM registers live for one block.
- [x] For each stage, schedule its four independent butterflies together:

  ```text
  four mullo
  four independent mulhi
  four correction mulhi
  four Montgomery subtract
  four butterfly add/sub pairs
  ```

- [x] Use destructive high operands after both product halves have been issued.
- [x] The canonical serial path uses 8 data + 4 temporary YMM registers; q and
  Barrett constants are read-only memory operands.  Remapped/resident candidates
  intentionally use different physical ownership.
- [x] Audit the original serial handwritten extraction with
  `llvm-mca -mcpu=znver5`.  Its historical one-pass estimate is 358
  instructions, 180 cycles, and block throughput 70.  This does not describe
  the later multi-symbol file and is only a scheduling diagnostic, not a
  call-level cycle prediction.
- [x] Confirm zero stack spill/reload instructions in the linked ASM symbol;
  `gt_ntt_avx2_stage345_soa_asm` is 2037 bytes (`0x7f5`).
- [x] Evaluate pairwise-interleaved Barrett/transpose scheduling; it is exact
  but performance-neutral.
- [x] Implement a no-copy physical register mapping.  It removes four
  `vmovdqa` per stage, 72 moves over six blocks, and reduces the linked symbol
  to 1913 bytes (`0x779`).
- [x] Evaluate keeping q and the packed Barrett reciprocal resident for a full
  block.  The GCC 16/GNU-as linked candidate is 1797 bytes (`0x705`) and
  replaces 28 memory-source constant
  operands with two loads per block, but is neutral to slower on Zen 5.

### Final store

- [x] Implement the candidate 16-block SoA transpose as part of the final
  stage/store schedule.
- [x] Account for every cross-128-bit-half instruction: each eight-vector block
  uses eight `vperm2i128` instructions after a lane-local 8x8 transpose.
- [x] Compare a packed-int16 final reducer with the widened intrinsic reducer.
  The packed form is modulo-equivalent and returns `[0,q]`, while the intrinsic
  path returns centered representatives.
- [x] Add the three-instruction centered final reducer.  Centered queued
  Stage345 is 307.18 cycles versus 323.46 canonical queued and is 1854 linked
  bytes.
- [x] Preserve and differential-test `out == in` behavior in the hybrid public
  wrapper.
- [x] Select `queued-store` within the five `[0,q]` schedule variants and reuse
  its store ordering in the centered SoA winner.  It uses the no-copy
  arithmetic, issues all eight `vperm2i128` outputs before the eight stores,
  and is 1913 bytes (`0x779`).  Forward- and reversed-order ten-repeat,
  1M-iteration checks improve isolated stage3+4+5 by 1.13%--1.50% and full
  forward by 0.21%--0.34%; full polynomial multiplication is nominally about
  0.10% slower but within perf variation, hence neutral.
- [x] Keep the canonical symbol and production path unchanged.  A sub-1% local
  win is schedule evidence, not enough to promote a full pipeline whose
  polynomial-multiplication result does not improve reliably.
- [x] Compose direct+queued explicitly.  It improves direct full forward by
  0.40%--0.45% but remains about 12% slower than canonical; its full-polymul
  result flips from 0.35% faster to 0.04% slower with operation order.
- [x] Implement transpose-native output without deleting the required
  lane-local 8x8 transpose.  Directly store branch0 `c0..c3` from
  YMM8..YMM11 and branch1 `c0..c3` from YMM12..YMM15, eliminating all 48
  cross-half `vperm2i128` instructions over six blocks.
- [x] Verify the 12-batch native mapping byte-exactly against centered SoA.
  Native Stage345 is 289.18 cycles and 1744 linked bytes.
- [~] Select u4 + identity + native-centered for forward-only native layout:
  698.55 cycles versus 756.84 canonical GT and 650.13 production.
- [x] Add true single-entry U2/U4 native forwards.  Each symbol inlines the
  producer and Stage345, uses two disjoint 1536-byte stack regions, has no
  internal call/push/pop, restores the exact entry stack pointer, and has one
  terminal `vzeroupper`.
- [x] Harden the single-entry test boundary with 32-byte guard bands, byte-exact
  native-to-SoA comparison, random/boundary inputs, inverse round-trip, and
  `out == in` coverage.  The linked U2/U4 symbols are 4019/5747 bytes.
- [x] Measure the single-entry candidates using a shared output arena and both
  operation orders.  At 5M calls, U2 saves 1.220 cycles (0.175%) while U4 loses
  1.264 cycles (0.181%); keep U2 as the scheduling platform and U4 as
  default-off regression evidence.
- [x] Pipeline the next Stage345 block's eight stage2 loads into the current
  native-store tail.  Reuse dead YMM0--YMM7 for the next block while current
  outputs in YMM8--YMM15 are stored; use a prologue/body/epilogue schedule and
  do not increase the eight-vector arithmetic live set.
- [~] Implement native-layout basemul and inverse first-load mapping.  The
  generated native lambda table and `gt_basemul_native_avx2` now consume all
  12 native batches directly, including centered-by-lazy operands in either
  orientation.  The inverse first-load mapping is still missing.  Do not
  insert the test-only 768-word native-to-SoA conversion into a timed or
  production path.
- [x] Pair adjacent singleton-row Q values through Stage1/2.  The row2q2
  candidate saves 75.001 instructions and 1.761% cycles in its stable paired
  run, while restoring the established `[Q|Q+16]` consumer layout with four
  `vperm2i128` instructions.
- [x] Reject the contiguous Stage345 twiddle stream.  It saves ten retired
  instructions but regresses cycles by 9.643% on Zen 5; do not combine it with
  row2q2.
- [x] Add the asymmetric lazy-native forward.  Omitting the six blocks' final
  center reducers saves exactly 144 instructions and 10.418% isolated cycles.
- [x] Reject calling separate centered and lazy forward symbols in one pair;
  duplicating the roughly 7-KB code image loses about 5--7% at the boundary.
- [x] Select the shared runtime-center symbol as the next default-off native
  pipeline.  The `2*forward + native basemul` paired mean improves 4.326% in
  cycles and 4.422% in reference cycles, with exactly 144 fewer instructions.
- [ ] Implement the native inverse first-load mapping and measure the complete
  `2*forward + native basemul + inverse` path before any production promotion.

## Pointwise multiplication

- [x] Write and differential-test the quartic base-multiplication formula for
  one 16-block SoA batch.
- [x] Load `a0..a3`, `b0..b3`, and lambda without an input transpose.
- [~] Schedule independent 16x16 Montgomery products in groups that hide the
  Zen 5 three-cycle multiply latency.  The first ASM keeps all eight inputs and
  four `a_i*qinv` values resident, so the out-of-order core can overlap adjacent
  chains, but an explicit x3/x4 source schedule remains a follow-up candidate.
- [x] Keep accumulated bounds within signed int16 and document every reduction.
- [x] Preserve the SoA layout at output.
- [x] Add a zero-spill scheduled ASM kernel for both SoA and native tables.
  It hoists four `a_i*qinv` values per batch, keeps `a0..a3`, their premultiplies,
  and `b0..b3` resident, and uses lambda/R2 memory operands.  The native linked
  body is 655 bytes with no stack/call; isolated reference cycles improve
  10.326% and the runtime-forward pair boundary improves 3.532%.
- [x] Test an `R^-1` basemul output contract that removes four `R^2` finalizers
  per batch and absorbs the common scale in matching inverse constants.  The
  safe version replaces all four chains by three-instruction center10
  checkpoints and saves 48 instructions.  The selected `c0-lazy` version
  leaves the proven `2*(q-1)` c0 accumulator untouched, checkpoints c1..c3,
  and saves 84 instructions; balanced TSC medians improve 0.78% for full SoA
  polymul and 1.65% for the selected native forward-pair boundary.
- [ ] Add `basemul_add` because it is used by encapsulation.
- [x] Differential-test every batch against the scalar quartic reference and
  test forward-NTT-to-basemul composition.

## Inverse NTT

- [x] Consume pointwise SoA output directly without a row-bitrev buffer or
  standalone 768-word transpose.
- [x] Fuse the first inverse mapping into four Q-group loads for each `(k3,c)`.
- [x] Define the inverse NTT32 schedule:

  ```text
  four YMM = Q[0..7], Q[8..15], Q[16..23], Q[24..31]
  len2/4/8 = vpshufb inside each 128-bit branch half
  len16    = group0/1 and group2/3
  len32    = group0/2 and group1/3
  ```

- [x] Keep all five inverse NTT32 stages lazy.  Bounds grow from `q` to `6q`,
  then one packed-int16 Barrett checkpoint returns every row to `[0,q]`.
- [x] Define inverse DFT3, untwist, 96-folded normalization, and branch merge.
- [x] Replace scalar word scatter with four-coefficient 4x8 transpose and
  public CRT block table; final output uses 192 low/high 64-bit block stores.
- [x] Prove inverse lazy ranges and scaling-domain transitions in
  `range-proof.md`.
- [x] Verify `invNTT(NTT(a)) == a mod q` for boundary and random inputs.
- [x] Verify the complete forward + basemul + inverse polynomial product
  against schoolbook multiplication, including a full-range boundary case.
- [x] Hand-schedule one `(k3,c)` four-group lazy inverse NTT32 region.
  `gt_invntt_soa_ntt32_asm` is a 955-byte linked symbol with no stack access
  or calls.  It uses all 16 YMM registers and matches the intrinsic scratch
  boundary exactly for boundary and 100 random inputs.
- [x] Hand-schedule one Q-group inverse DFT3 plus packed checkpoint region.
  `gt_invntt_soa_dft3_asm` is a 230-byte linked symbol with no stack access or
  calls.  Its 16 in-place iterations interleave three independent Barrett
  chains, use YMM0..YMM14, and match the intrinsic scratch exactly for the
  boundary and 100 random inputs.
- [x] Hand-schedule one `(n3,Qgroup)` untwist/merge/4x8 final-store region.
  `gt_invntt_soa_postprocess_asm` is a 781-byte linked symbol with no stack
  access or calls.  Its 12 iterations use generated public factor/block tables
  and match the intrinsic 768-word output exactly for direct boundary and 100
  random valid scratch inputs.
- [x] Keep inverse NTT32 ASM within the 16-register budget: 4 data, 8
  shuffle/Montgomery temporaries, 2 reusable mask/twiddle registers, q, and
  Barrett reciprocal.
- [x] Keep postprocess ASM within the 16-register budget: four final data plus
  unpack temporaries; do not retain multiple Q-groups across scratch boundaries.
- [~] Remove the two GCC constant spills and define whether the 1536-byte row
  scratch is caller-provided or stack-owned in the production ABI.  The
  three-region wrapper has no constant spills and owns exactly 1536 stack
  bytes, but the production scratch ABI remains undecided.
- [x] Fuse the three inverse regions behind one benchmark-only ASM entry.
  `gt_invntt_soa_avx2_fused_asm` is 1968 linked bytes, owns one aligned
  1536-byte stack scratch, contains no push/pop/call, and emits one terminal
  `vzeroupper`.  It reuses the standalone region macros and passes exact,
  in-place, round-trip, and full-polymul tests.
- [x] Measure region fusion in both operation orders.  Isolated inverse improves
  only 0.07%--0.16%; full-polymul deltas range from -0.05% to +0.48%, so pure
  call-boundary fusion is performance-neutral and should not receive more work.

## ABI, constant-time, and object audit

- [x] Record the prototype System V AMD64 contract: `out` is in `rdi`, scratch
  is in `rsi`; only caller-saved GPRs and YMM0..YMM15 are clobbered.  Standalone
  regions plus direct/half entries do not touch the stack; the canonical fused
  producer deliberately owns its 1536-byte semantic frame.
- [x] Emit `vzeroupper` before returning from the public ASM boundary.
- [x] Keep all branches, addresses, and table indices input-independent.
- [x] Check alignment assumptions: the stage-2 scratch is 32-byte aligned and
  uses `vmovdqa`; output has no alignment precondition and uses `vmovdqu`.
- [~] Record stack and scratch use: canonical public forward peak use is 3072
  bytes (caller stage2 plus fused producer frontend), while direct/half public
  wrappers peak at 1536 bytes.  Decide whether the production caller must wipe
  secret scratch.
- [x] Record candidate alias boundaries: low-level direct/half producers require
  disjoint input and 1536-byte stage2 output; low-level Stage345 entries require
  a 32-byte-aligned, non-overlapping 1536-byte scratch region and output.  The
  public forward wrappers use private stage2 storage and remain `out==in` safe.
- [ ] Define the production scratch-lifetime policy and wipe secret scratch if
  the final caller contract requires it.
- [x] Disassemble and audit the linked object, not only the source `.s` file.
- [x] Reject any AVX-512 instruction in the AVX2 target object.

## Validation and benchmark gates

- [x] Intrinsic Montgomery and Barrett unit tests.
- [x] Frontend and stage-2 representation-boundary tests.
- [x] Independent Stage345 boundary tests at alternating and random values in
  `[-5(q-1),5(q-1)]`: the five canonical-representation ASM schedules are
  exact-equal in `[0,q]`; the two centered schedules and native store are
  modulo-q equivalent, stay in `[-3080,3079]`, and match their declared
  layout oracle.
- [x] Full forward-NTT differential test against the portable GT reference.
- [x] SoA mapping oracle and inverse mapping oracle.
- [x] Pointwise differential tests.
- [x] Inverse and full-polymul differential tests.
- [x] Production NTRU+ test binary.
- [ ] Production KAT.
- [x] Benchmark NTT, basemul, inverse NTT, and full polynomial multiplication
  for both production and GT SoA prototype paths.
- [x] Record CPU model, pinned core, SMT sibling, governor, boost state,
  compiler, flags, and perf events.  New conclusions use hardware `cycles`
  only; the TSC sampler is retained as an opt-in historical diagnostic.

At the earlier intrinsic-frontend checkpoint, preliminary Ryzen 7 9700X
results with boost enabled and CPU 2 pinned showed a
983-tick median for the hybrid ASM SoA forward transform versus 1476 for the
intrinsic GT transform (33.4% lower).  That historical result was not a release
claim because the SMT sibling was not isolated and frontend/stage1+2 was still
intrinsic at that checkpoint.
The matching SoA intrinsic basemul records 318 TSC ticks and 478.83 hardware
cycles/call versus production's 318 ticks and 480.43 cycles/call.  Its current
spill traffic still has to be removed before treating this as a scheduled
pointwise result.

The final direct-consumer inverse intrinsic records 1013 TSC ticks, 1494.44
hardware cycles/call, and 4621.31 instructions/call versus production inverse's
432, 651.01, and 2600.29.  Full GT SoA polynomial multiplication records 3323
TSC ticks versus production's 1652.  The initial correctness-first inverse was
4051 TSC; lazy checkpoints reduced it to 1465, and the 4x8 block store reduced
it to 1013.  This validates the schedule boundaries but does not pass the
production performance gate.

GCC 16 emits a 2681-byte inverse symbol with a 1480-byte explicit stack
adjustment plus a 120-byte red-zone window.  The semantic row scratch is 1536
bytes; two vector constants are also spilled.  The linked AVX2 binary contains
no ZMM/opmask instructions.

The first hand-scheduled inverse region lowers isolated inverse NTT32 median
from 537 to 422 TSC ticks (21.4%) and hardware cycles from 801.49 to 633.95
(20.9%).  It retires 4.3% more instructions, but IPC rises from 2.45 to 3.24;
the win is scheduling rather than instruction-count reduction.  The hybrid
full inverse falls from 998 to 886 TSC ticks, and full GT polynomial
multiplication falls from 3301 to 3179.  The latter remains 1.93x production.

The second hand-scheduled inverse region lowers isolated inverse DFT3 plus
checkpoint from 131.62 to 125.09 hardware cycles/call (4.96%).  In the same
five-repeat `perf stat -e cycles` run, full inverse falls from 1315.90 to
1306.74 cycles (0.70%), and full GT polynomial multiplication falls from
4671.29 to 4640.95 cycles (0.65%).  The two-region path remains 1.92x the
production polynomial multiplication result of 2414.32 cycles, so the next
inverse target is untwist/merge/4x8 final store.

The third hand-scheduled inverse region lowers isolated postprocess from
580.83 to 521.51 hardware cycles/call (10.21%).  In the same five-repeat
`perf stat -e cycles` run, full inverse falls from 1307.52 to 1254.70 cycles
(4.04%), and full GT polynomial multiplication falls from 4645.01 to 4584.06
cycles (1.31%).  Production polynomial multiplication is 2426.09 cycles, so
the three-region path remains 1.89x production.  Region fusion was therefore
evaluated next without changing the representation.

The fused inverse does not materially change that result.  Across one
five-repeat comparison and two ten-repeat order checks, inverse improves by
0.07%--0.16%, while the full-polymul delta ranges from 0.05% slower to 0.48%
faster.  The exact fused ABI is useful, but further call-overhead tuning is not
a priority.

The active production AVX2 arithmetic files are byte-identical to KPQC Final.
On the same five-repeat hardware-cycle run, KPQC Final/production versus GT is:
667.04 versus 1454.02 for forward NTT, 480.64 versus 479.75 for basemul, 651.61
versus 1252.94 for inverse, and 2420.73 versus 4585.62 for full polynomial
multiplication.  This moves the next priority to the GT forward
frontend/stage-1+2 schedule.

That forward milestone is now complete.  In the ten-repeat reversed-order
`perf stat -e cycles` confirmation, frontend falls from 993.73 to 334.82
cycles (66.3%), stage1+2 from 161.56 to 133.40 (17.4%), full GT forward from
1452.44 to 774.76 (46.7%), and full GT polynomial multiplication from 4584.88
to 3233.41 (29.5%).  KPQC Final/production in the same run is 669.00 forward
and 2422.08 polynomial multiplication, leaving 1.16x and 1.33x gaps.

The reducer and DFT3-tail scheduling milestone selects two default-off
paths.  Existing SoA uses u2 + identity + centered + queued-store:
717.996 forward cycles and 3141.619 full-polymul cycles, versus 756.840 and
3219.544 canonical GT.  The earlier two-entry native forward uses u4 +
identity + native-centered at 698.548 cycles.  The new single-entry paired
comparison selects U2: 696.194 cycles at 5M calls, 1.220 cycles below its
two-entry control; U4 fusion is a measured regression.  Native still has no
matching basemul/inverse contract.  Production remains faster at 650.128
forward and 2401.898 polynomial-multiplication cycles in the earlier 1M run.

Cycle sampling attributes 45.03% of the fused U2 symbol to frontend, 15.30%
to stage1+2, and 39.68% to Stage345.  Stage345 current-store/next-load
pipelining is now complete: the 5M-call, ten-repeat, two-order confirmation
lowers U2 single-entry forward from 696.868 to 695.258 cycles (-0.231%).  It
retires seven more instructions per call but raises IPC from 3.797 to 3.812,
and shrinks the linked symbol from 4019 to 3274 bytes.  The next forward target
is the frontend CRT-indexed load/address schedule.  Do not reopen runtime twist
construction, compiler-spill work, call-overhead tuning, the same scratch-copy
elimination, or further Stage345 store-tail rearrangements without new evidence.

NTRU+768 has no scheme-level matrix-vector multiplication.  That benchmark is
not applicable; `basemul_add` and full KEM component measurements are the
relevant higher-level workloads.

## Promotion rule

Do not replace production `asm/ntt.s` until the candidate:

1. preserves the approved representation contract;
2. passes forward, pointwise, inverse, full-polymul, and KAT correctness;
3. has no unexplained spill or secret-dependent access;
4. beats or matches the production full polynomial-multiplication path on the
   recorded Zen 5 benchmark environment.

## Forward frontend priority 1/2 status (2026-07-21)

- Rejected: expanded-constant fused top split + branch twist.  It is correct
  modulo q and range-safe, but is 2.997% slower and adds about 90 instructions
  per transform in the 5M-call confirmation.
- Selected default-off: U2 high-first cross-pair top-zeta pipeline.  It is
  byte-exact, instruction-count neutral, and 0.739% faster than the previous
  pipelined winner.
- Next bounded candidate: generate a high-first, pair-specific fixed-
  displacement frontend to remove the six scalar offset-table loads per pair.

### Fixed-displacement result

- Completed and selected default-off: 690.062 cycles versus 693.025 for the
  indexed high-first control (-0.428%) in 20 interleaved 5M-call pairs.
- Retired instructions fall by 127.003 per transform (-4.789%); reference
  cycles also fall 0.490% and the output remains byte-exact.
- Tradeoff: linked code grows from 3274 to 8234 bytes and IPC falls from 3.827
  to 3.659, although measured L1I misses remain negligible.
- Next bounded candidate: fixed output-store displacements in the existing
  unrolled body, removing `r9` setup/update without duplicating more code.

## Key-generation integration priority (2026-07-23)

- Completed: lazy Forward -> direct GTN-L3 baseinv -> native basemul native
  island, with generated quartic-slot map and direct WIRE12 serialization.
- Correctness gate passed: exhaustive canonicalizer/layout tests, deterministic
  byte-exact keypairs, full KEM differential, and 100-case NIST KAT.
- Promotion rejected: keygen is 38.807% slower and full KEM is 15.216% slower.
- Root cause: scalar native pack retires 12152.293 instructions versus
  production `pack.s` at 815.292; three calls add about 34,011 instructions.
- P0 completed: generated, zero-secret-address AVX2
  `GTN16 -> WIRE12` permutation/pack matches the scalar oracle and production
  byte stream.  Dual-sign shuffles and paired-YMM groups reduce the centered
  entry to 231.480 cycles and 810.289 instructions, versus production at
  225.468 and 815.291.
- Consumer specialization completed: L3 pack is 287.201 cycles/960.291
  instructions; centered pack is used for `h`/`hinv`, L3 for `f`.
- Six-pair confirmation: keygen is 0.089% faster with 779 fewer instructions,
  but full KEM remains about 0.45% slower despite the same 779-instruction
  saving.  The island remains default-off until the post-keygen
  frontend/I-cache cost is localized.
- Forward audit closed for now: all 48 final centers are gone; remaining
  mandatory reductions prevent int16 overflow.  The only obvious identity
  specialization saves about seven instructions per Forward and is below the
  current priority threshold.
- Current KPQC/keygen audit completed: exact same-binary isolated Forward is
  558.619 GT versus 652.417 KPQC cycles (-14.377%) and saves 275.016
  instructions, but the GT body is 6,929 bytes versus KPQC's 1,833.
- Ten alternating 200,000-keygen pairs revise the small cycle result to
  +97.427 cycles (+0.293%) and +74.098 ref cycles (+0.319%), while retaining
  the exact 779.009-instruction saving.  Treat keygen cycles as parity/slight
  regression, not a promotion win.
- Frontend counters localize the integration loss: GT adds about 1,290
  x86-decoder ops, 153 op-cache misses, and 1,325 no-dispatch frontend slots
  per keygen, while L1I misses change by only 0.044.
- Next P0: a compact, looped keygen Forward retaining Q/Q+3 wide loads, fused
  split/twist, delayed 24-vector checkpoint, row2q2, GTN-L3, and native
  transpose.  Target at most 4 KB and gate it on paired complete keygen plus
  decoder/op-cache events.  Do not spend the next experiment on the
  seven-instruction identity cleanup.
- Rejected without ASM edit: reuse KPQC's four-instruction `reduce2` for the
  GTN-L3 pack.  It maps `q` and `2q` to the arithmetic-valid representative
  `q`; byte-exact WIRE12 needs zero.  The required correction raises it to at
  least seven instructions per vector versus the current six.
