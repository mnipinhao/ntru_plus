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
- [x] The stage-3+4+5 ASM prototype uses a packed-int16 Barrett checkpoint.
  Its full input interval and output range are exhaustively checked; the
  centered widened reducer remains in the intrinsic comparison path.

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
  1.33x.

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
- [x] Keep the Montgomery `R` multiplication: it is congruent to identity but
  also reduces the lazy high operand.
- [x] Store stage-2 results in the consumer's block order.
- [x] Replace the GCC 16 stage1+2 symbol's five constant spill/reloads with
  YMM9..YMM15 constants.  The 423-byte linked ASM symbol has zero stack
  traffic/calls and is byte-exact at the scratch boundary.
- [x] Fuse frontend and stage1+2 behind a 970-byte linked entry with one aligned
  1536-byte semantic scratch, no internal calls, and one terminal
  `vzeroupper`.
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
- [x] Preserve and differential-test `out == in` behavior in the hybrid public
  wrapper.
- [~] `queued-store` is the selected default-off schedule candidate.  It uses
  the no-copy arithmetic, issues all eight `vperm2i128` outputs before the
  eight stores, and is 1913 bytes (`0x779`).  Forward- and reversed-order
  ten-repeat, 1M-iteration checks improve isolated stage3+4+5 by 1.13%--1.50% and full
  forward by 0.21%--0.34%; full polynomial multiplication is nominally about
  0.10% slower but within perf variation, hence neutral.
- [x] Keep the canonical symbol and production path unchanged.  A sub-1% local
  win is schedule evidence, not enough to promote a full pipeline whose
  polynomial-multiplication result does not improve reliably.
- [x] Compose direct+queued explicitly.  It improves direct full forward by
  0.40%--0.45% but remains about 12% slower than canonical; its full-polymul
  result flips from 0.35% faster to 0.04% slower with operation order.

## Pointwise multiplication

- [x] Write and differential-test the quartic base-multiplication formula for
  one 16-block SoA batch.
- [x] Load `a0..a3`, `b0..b3`, and lambda without an input transpose.
- [ ] Schedule independent 16x16 Montgomery products in groups that hide the
  Zen 5 three-cycle multiply latency.
- [x] Keep accumulated bounds within signed int16 and document every reduction.
- [x] Preserve the SoA layout at output.
- [ ] Replace the semantics intrinsic with a zero-spill scheduled ASM kernel.
  GCC 16 currently emits a 773-byte symbol, a 72-byte frame, and YMM spill/
  reload traffic; this is measured baseline evidence, not a final schedule.
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
  `[-5(q-1),5(q-1)]`, including modulo-q oracle, `[0,q]` output range, and
  exact equality across all five ASM schedules.
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

Preliminary Ryzen 7 9700X results with boost enabled and CPU 2 pinned show a
983-tick median for the hybrid ASM SoA forward transform versus 1476 for the
intrinsic GT transform (33.4% lower).  This is not a release claim because the
SMT sibling was not isolated and the remaining frontend/stage-1+2 is intrinsic.
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

Both proposed follow-ups have now been measured.  Zero/half frontend handoff
regresses the producer by 16.86%--16.93%/17.33%--17.41%, so the semantic
scratch is retained.  The queued Stage345/SoA store lowers its isolated region
by 1.13%--1.50% and full forward by 0.21%--0.34%, but full-polymul has no
reliable improvement.
The next high-value targets are a structural stage2-to-stage345 boundary change
or the still-dominant inverse/postprocess path.  Do not reopen runtime twist
construction, compiler-spill work, or the same scratch-copy elimination.

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
