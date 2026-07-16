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
- [~] Forward NTT fuses the required transpose into its final stores.
- [~] Inverse NTT fuses the reverse mapping into its first loads.
- [x] Prove and exhaustively round-trip the complete coefficient-to-batch
  mapping for all 768 positions.
- [ ] Compare this SoA layout with the current GT row-bitrev block-major layout
  using total forward + basemul + inverse cycles.

There must not be a standalone 768-coefficient transpose pass between forward
NTT and pointwise multiplication, or between pointwise multiplication and the
inverse NTT.

## Arithmetic tables

- [x] Forward twist and omega32 values match the AArch64 GT reference.
- [~] Prepack every fixed factor as `(factor, factor*qinv)`: complete for the
  ASM stage-3+4+5 tables, pending for the intrinsic frontend/stage-1+2 path.
- [ ] Prepack GT input CRT indices; remove runtime `% 96` arithmetic.
- [x] Encode row01 stage-3+4+5 twiddles as full-lane repeats.
- [x] Encode singleton stage-3+4+5 twiddles as
  `[twiddle(Q) x8 | twiddle(Q+16) x8]`.
- [x] Generate the candidate SoA lambda table in physical batch order.
- [x] Add a generator/checker so table changes are reproducible rather than
  hand-edited.

## Forward NTT assembly regions

### Frontend slot-pair

- [ ] Implement top split and twist for one `(Q,Q+1)` pair.
- [ ] Interleave the two XMM Montgomery chains to hide multiply latency.
- [ ] Form one `x_n3` YMM before proceeding to the next `n3`; do not keep six
  independent slot values live.
- [ ] Schedule the DFT3 Montgomery chain while computing `r0`, `x0-x2`, and
  `x0-x1`.
- [ ] Store/transpose DFT3 results immediately; do not carry outputs across
  frontend iterations.
- [ ] Eliminate the vector spills currently emitted for the intrinsic frontend.

### NTT32 stage 1+2

- [ ] Process one four-vector row01 stripe at a time.
- [ ] Interleave row01 and singleton Montgomery work where it reduces multiply
  latency without exceeding the register budget.
- [ ] Keep the Montgomery `R` multiplication: it is congruent to identity but
  also reduces the lazy high operand.
- [ ] Store stage-2 results in the consumer's block order.

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
- [x] Use 8 data + 4 temporary YMM registers; q and Barrett constants are
  read-only memory operands rather than additional live registers.
- [x] Audit the handwritten region with `llvm-mca -mcpu=znver5`.  A one-pass
  whole-file static estimate reports 358 instructions, 180 cycles, and block
  throughput 70; loops and the test-only reducer entry mean this is a scheduling
  diagnostic, not a call-level cycle prediction.
- [x] Confirm zero stack spill/reload instructions in the linked ASM symbol;
  `gt_ntt_avx2_stage345_soa_asm` is 2037 bytes (`0x7f5`).

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

- [ ] Consume pointwise SoA output directly.
- [ ] Fuse SoA-to-internal mapping into the first inverse loads.
- [ ] Define inverse NTT32 row packing and stage schedule.
- [ ] Define inverse DFT3, untwist, normalization, and final top merge.
- [ ] Prove inverse lazy ranges and scaling-domain transitions.
- [ ] Verify `invNTT(NTT(a)) == a mod q` for boundary and random inputs.
- [ ] Verify the complete forward + basemul + inverse polynomial product.

## ABI, constant-time, and object audit

- [x] Record the prototype System V AMD64 contract: `out` is in `rdi`, scratch
  is in `rsi`; only caller-saved GPRs and YMM0..YMM15 are clobbered; the ASM
  region does not touch the stack.
- [x] Emit `vzeroupper` before returning from the public ASM boundary.
- [x] Keep all branches, addresses, and table indices input-independent.
- [x] Check alignment assumptions: the stage-2 scratch is 32-byte aligned and
  uses `vmovdqa`; output has no alignment precondition and uses `vmovdqu`.
- [~] Record stack and scratch use: the C hybrid wrapper currently owns 3072
  bytes of aligned scratch, while the ASM region allocates zero bytes.  Decide
  whether the production caller must wipe secret scratch.
- [ ] Define the production scratch-lifetime policy and wipe secret scratch if
  the final caller contract requires it.
- [x] Disassemble and audit the linked object, not only the source `.s` file.
- [x] Reject any AVX-512 instruction in the AVX2 target object.

## Validation and benchmark gates

- [x] Intrinsic Montgomery and Barrett unit tests.
- [x] Frontend and stage-2 representation-boundary tests.
- [x] Full forward-NTT differential test against the portable GT reference.
- [x] SoA mapping oracle and inverse mapping oracle.
- [x] Pointwise differential tests.
- [ ] Inverse and full-polymul differential tests.
- [x] Production NTRU+ test binary.
- [ ] Production KAT.
- [~] Benchmark NTT, basemul, inverse NTT, and full polynomial multiplication.
  The production path has all four measurements; the GT SoA path has forward
  NTT and intrinsic basemul, but no inverse/full-polymul measurement yet.
- [x] Record CPU model, pinned core, SMT sibling, governor, boost state,
  compiler, flags, TSC method, and perf events.

Preliminary Ryzen 7 9700X results with boost enabled and CPU 2 pinned show a
983-tick median for the hybrid ASM SoA forward transform versus 1476 for the
intrinsic GT transform (33.4% lower).  This is not a release claim because the
SMT sibling was not isolated and the remaining frontend/stage-1+2 is intrinsic.
The matching SoA intrinsic basemul records 318 TSC ticks and 478.83 hardware
cycles/call versus production's 318 ticks and 480.43 cycles/call.  Its current
spill traffic still has to be removed before treating this as a scheduled
pointwise result.

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
