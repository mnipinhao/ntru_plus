# Candidate A Batch8 Explanation

This note documents the current Candidate A batch8 path after the stale
experiments were removed and the fast batch8 TMVP kernel was restored.

## Current Status

Candidate A batch8 is a validated stage4-boundary product probe plus a KEM
bridge.  It is not yet a production-compatible KEM backend.

The important distinction is:

- The forward source currently stops before NTT32 stage5 and stores a rowpack
  stage4 layout.
- The batch8 TMVP kernel then materializes the missing stage5 even/odd pairs
  inside the pointwise product adapter.
- Therefore the current path is a stage4-source path with internal stage5
  materialization.  It is not a pure incomplete-NTT residual product that
  multiplies directly in the stage4 domain without stage5 arithmetic.

Validated results from the current reports:

- `test_gt_tmvp_candidate_a_batch8_fullpath`: pass.
- `total_mismatches`: 0.
- `tmvp_batch8_asm_mul`: 68 cntvct ticks.
- `tmvp_batch8_asm_fullpath_mul`: 155 cntvct ticks.
- Add path currently falls back to C.

## Main Files

- `Makefile`
  - Defines the Candidate A batch8 test, bench, and KEM bridge targets.
- `gt_tmvp_quartic_tmvp_experimental.h`
  - Declares the Candidate A product and add entry points.
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_gt_tmvp_candidate_a_tmvp_batch8.opt.S`
  - AArch64 Neon batch8 TMVP product core.
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_gt_tmvp_candidate_a_tmvp_batch8_wrapper.c`
  - Public C wrapper, rowpack offsets, and per-branch/per-row/per-block
    constant setup.
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_soa_row_stage2_to5_no_entry_no_end.opt.S`
  - In-place inverse NTT32 rowkernel for the after-stage1 row state.
- `docs/gt_soa_layout_experiment/kernels/ntruplus768_invntt32_rowpack_postmerge_branchfold.S`
  - Rowpack postmerge and branchfold back to polynomial order.
- `poly_gt_tmvp_candidate_a_batch8_kem.c`
  - Natural-domain KEM bridge using the Candidate A multiplication path.
- `gt_test/test_gt_tmvp_incomplete_candidate_a_stage2_postmerge_c.c`
  - Fullpath correctness and tick benchmark harness.

## Data Layout

The working rowpack layout is:

```text
index = branch * 384 + row * 128 + lane * 32 + k32

branch = 0..1
row    = 0..2
lane   = 0..3
k32    = 0..31
```

The current multiplication dataflow is:

```text
natural polynomial
  -> top split
  -> branch twist
  -> Good-Thomas 96 = 3 x 32 mapping
  -> DFT3 per k32
  -> NTT32 stages 1..4 only
  -> rowpack stage4 source
  -> Candidate A batch8 TMVP materializes stage5 and multiplies
  -> inverse rowkernel after-stage1 adapter: [ce + co, ce - co]
  -> inverse rowkernel stages 2..5
  -> postmerge branchfold
  -> natural polynomial
```

The batch8 wrapper calls the assembly kernel for:

```text
2 branches * 3 rows * 2 k32 blocks = 12 calls per product
```

Each batch covers eight even/odd pairs for four quartic lanes.

## Assembly Contract

The batch8 product core has this ABI:

```text
x0 = output rowpack batch base
x1 = a stage4 rowpack batch base
x2 = b stage4 rowpack batch base
x3 = constants
```

The kernel uses fixed-offset `ldr q*` input and constant loads, `uzp1/uzp2`
to split even/odd pairs, `mul/sqrdmulh/mls` for fixed-factor stage5
materialization and reductions, `smull/smull2/smlal/smlal2` for widened
quartic products, and fixed-offset `str q*` stores back to rowpack output.

The final output is intentionally arranged as the inverse rowkernel after
stage1 state:

```text
even slot: ce + co
odd slot:  ce - co
```

The rowkernel then starts at inverse stage2.  This is why the stage2-to5
rowkernel source says stage1 is skipped.

## Incomplete Stage4 Route

This is the route where TMVP directly consumes the stage4 output and does not
perform the missing stage5 transformation inside `basemul()`.

Pros:

- Avoids storing and later loading complete stage5 output.
- Potentially avoids a costly late NTT32 layer if the residual product can be
  made cheaper than stage5 plus ordinary pointwise multiplication.
- Gives the most freedom to design a TMVP-specific rowpack layout.
- Can fuse the product output directly into the inverse rowkernel entry state.

Cons:

- Requires a different residual multiplication contract.  The current Candidate
  A batch8 kernel does not implement this pure form.
- Needs a new correctness proof: incomplete transform plus residual product
  must equal the complete transform product.
- Needs fresh range bounds for the residual accumulations.
- Harder to expose as a cached KEM representation; callers must not mix
  incomplete-domain and complete-domain polynomials.
- `poly_baseinv()` and serialized public-key/ciphertext representation become
  harder unless the whole KEM representation contract is redesigned.

Implication:

Pure incomplete stage4 is the higher-upside route, but it is not just "write a
forward stage4 ASM."  It requires a new residual TMVP algebra and a new test
oracle.

## Current Candidate A Stage4-Source Route

This is the route implemented now.

Pros:

- Already validates against schoolbook through the full stage4-boundary to
  final-polynomial path.
- Keeps the fast batch8 product kernel: 68 cntvct ticks for the TMVP core.
- Avoids writing complete stage5 buffers in the forward transform source.
- Directly emits the inverse rowkernel after-stage1 adapter shape.
- Good as a measurement platform for deciding whether the Candidate A shape has
  enough headroom.

Cons:

- Stage5 is still paid inside the TMVP adapter, so this is not a true
  incomplete residual product.
- The forward stage4 source is still C in the KEM bridge.
- The add path still falls back to C.
- The KEM bridge is natural-domain and self-consistent, but not byte-compatible
  with the production NTT-domain KEM representation.
- Optimizing only forward stage4 ASM may improve the bridge, but it does not
  settle whether pure incomplete or complete evalpack is the better final
  direction.

Implication:

This is the best near-term route for measurement.  If the goal is a large
end-to-end KEM speedup, the next gates are forward stage4 ASM and batch8 add
ASM, followed by a representation decision.

## Complete Stage5 / Evalpack Route

This is the route where forward NTT32 finishes stage5 before the pointwise
product.  The store layout can still be changed so the later product loads are
TMVP-friendly.

Pros:

- Much closer to the existing production KEM contract.
- Easier to reason about `poly_ntt`, `poly_invntt`, `poly_baseinv`, public key
  storage, and ciphertext storage.
- Easier to compare fairly against KPQC final and `gt_production_opt`.
- Stage5 arithmetic is paid once in the forward transform rather than hidden
  inside every product adapter.
- A carefully designed final store can make the product load layout cheaper.

Cons:

- Pays the complete stage5 transform even if a residual product could have
  avoided it.
- If the final store layout is the same logical shape as ordinary rowpack, then
  `ldr` may be just as good as `ld4/st4`; structure alone does not guarantee a
  win.
- May lose Candidate A's main benefit: fusing stage5 materialization, product,
  and inverse-stage1 adapter output.
- Complete output may need extra shuffles or stores to feed a quartic TMVP
  kernel.

Implication:

Complete evalpack is lower risk for KEM integration, but likely lower upside
unless the store/load layout materially reduces the product and inverse-entry
cost.

## KEM Bridge Caveat

`poly_gt_tmvp_candidate_a_batch8_kem.c` currently makes the KEM self-consistent
by keeping polynomials in natural-domain form at the public poly API boundary:

- `poly_ntt()` is a copy.
- `poly_invntt()` is a copy.
- `poly_basemul()` performs the Candidate A full multiplication internally.
- `poly_basemul_add()` uses the same path, but the add TMVP core is still C.
- `poly_baseinv()` internally runs complete GT NTT, scalar base inversion, and
  inverse NTT.

This is useful for correctness and early KEM timing, but it is not the final
production representation.  A fair final comparison needs either:

- a production-compatible NTT-domain Candidate A backend, or
- an explicitly documented new KEM representation contract with matching KAT
  and interoperability expectations.

## Recommended Next Gates

1. Keep `gt_production_opt` as the production control.
2. Keep Candidate A batch8 as the high-upside experimental route.
3. Do not call the current route pure incomplete; call it stage4-source with
   internal stage5 materialization.
4. Implement forward stage4 ASM only as a measurement gate for the current
   Candidate A route.
5. Implement batch8 add ASM before drawing KEM-level conclusions.
6. Decide between pure incomplete residual TMVP and complete evalpack only after
   forward stage4 and add costs are measured in the same KEM-style harness.
