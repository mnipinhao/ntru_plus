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
- [ ] Replace the prototype's widened int32 Barrett finalizer with a proven
  packed-int16 reducer if that wins on Zen 5.

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

- [~] Pack lambda and `lambda*qinv` in the same 16-block order.
- [~] Pointwise multiplication consumes four YMM values directly and emits the
  same layout.
- [~] Forward NTT fuses the required transpose into its final stores.
- [~] Inverse NTT fuses the reverse mapping into its first loads.
- [ ] Prove the complete coefficient-to-batch mapping for all 768 positions.
- [ ] Compare this SoA layout with the current GT row-bitrev block-major layout
  using total forward + basemul + inverse cycles.

There must not be a standalone 768-coefficient transpose pass between forward
NTT and pointwise multiplication, or between pointwise multiplication and the
inverse NTT.

## Arithmetic tables

- [x] Forward twist and omega32 values match the AArch64 GT reference.
- [ ] Prepack every fixed factor as `(factor, factor*qinv)`.
- [ ] Prepack GT input CRT indices; remove runtime `% 96` arithmetic.
- [ ] Generate row01 twiddles as full-lane repeats.
- [ ] Generate singleton twiddles as
  `[twiddle(Q) x8 | twiddle(Q+16) x8]`.
- [ ] Generate the candidate SoA lambda table in physical batch order.
- [ ] Add a generator/checker so table changes are reproducible rather than
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

- [ ] Keep eight data YMM registers live for one block.
- [ ] For each stage, schedule its four independent butterflies together:

  ```text
  four mullo
  four independent mulhi
  four correction mulhi
  four Montgomery subtract
  four butterfly add/sub pairs
  ```

- [ ] Use destructive high operands after both product halves have been issued.
- [ ] Target at most 8 data + 4 temporary + 1 q registers.
- [ ] Audit the generated/handwritten region with `llvm-mca -mcpu=znver5`.
- [ ] Confirm zero stack spill/reload instructions in the final object.

### Final store

- [ ] Implement the candidate 16-block SoA transpose as part of the final
  stage/store schedule.
- [ ] Account for every cross-128-bit-half instruction.
- [ ] Compare a packed-int16 final reducer with the current widened intrinsic
  reducer.
- [ ] Preserve `out == in` behavior or explicitly change the API contract.

## Pointwise multiplication

- [ ] Write the quartic base-multiplication formula for one 16-block SoA batch.
- [ ] Load `a0..a3`, `b0..b3`, and lambda without an input transpose.
- [ ] Schedule independent 16x16 Montgomery products in groups that hide the
  Zen 5 three-cycle multiply latency.
- [ ] Keep accumulated bounds within signed int16 or document every reduction.
- [ ] Preserve the SoA layout at output.
- [ ] Add `basemul_add` because it is used by encapsulation.
- [ ] Differential-test every batch against the scalar quartic reference.

## Inverse NTT

- [ ] Consume pointwise SoA output directly.
- [ ] Fuse SoA-to-internal mapping into the first inverse loads.
- [ ] Define inverse NTT32 row packing and stage schedule.
- [ ] Define inverse DFT3, untwist, normalization, and final top merge.
- [ ] Prove inverse lazy ranges and scaling-domain transitions.
- [ ] Verify `invNTT(NTT(a)) == a mod q` for boundary and random inputs.
- [ ] Verify the complete forward + basemul + inverse polynomial product.

## ABI, constant-time, and object audit

- [ ] Record System V AMD64 argument, stack-alignment, and clobber contracts.
- [ ] Emit `vzeroupper` at public boundaries if required by the caller mix.
- [ ] Keep all branches, addresses, and table indices input-independent.
- [ ] Check 32-byte alignment assumptions for every aligned load/store.
- [ ] Record stack and scratch use; wipe secret scratch if the final caller
  contract requires it.
- [ ] Disassemble the linked object, not only the source `.S` file.
- [ ] Reject any AVX-512 instruction in the AVX2 target object.

## Validation and benchmark gates

- [x] Intrinsic Montgomery and Barrett unit tests.
- [x] Frontend and stage-2 representation-boundary tests.
- [x] Full forward-NTT differential test against the portable GT reference.
- [ ] SoA mapping oracle and inverse mapping oracle.
- [ ] Pointwise differential tests.
- [ ] Inverse and full-polymul differential tests.
- [ ] Production NTRU+ test binary and KAT.
- [ ] Benchmark NTT, basemul, inverse NTT, and full polynomial multiplication.
- [ ] Record CPU model, pinned core, SMT sibling, governor, boost state,
  compiler, flags, TSC method, and perf events.

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
