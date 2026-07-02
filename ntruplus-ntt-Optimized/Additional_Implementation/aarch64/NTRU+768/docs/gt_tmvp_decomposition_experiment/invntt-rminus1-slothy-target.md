# InvNTT rminus1 Slothy Target Preparation

Date: 2026-06-29

Status: Slothy-ready target audit only.  No Slothy run, no fusion prototype,
no Q31 change, and no production default change in this pass.

## Scope

This target is the production decap inverse NTT used after
`poly_basemul_rminus1()`:

```c
poly_basemul_rminus1(&m1, &c, &f);
poly_invntt_from_rminus1(&m1, &m1);
poly_crepmod3(&m1, &m1);
```

It is not the crep3-fused path, not the stage123scratch split path, and not a
basemul-to-InvNTT fusion target.

## Entrypoints

| layer | entrypoint | file | note |
| --- | --- | --- | --- |
| C decap call | `poly_invntt_from_rminus1(poly *r, const poly *a)` | `kem.c` | active under `GT_PRODUCTION_USE_RMINUS1_DECAP` |
| public ASM alias | `poly_invntt_from_rminus1`, `_poly_invntt_from_rminus1` | `asm/gt/poly_invntt_rminus1.S` | wrapper macro-renames `poly_invntt` |
| block-major body | `gt_block_major_poly_invntt_from_rminus1` | `asm/gt/poly_invntt_rminus1.S` -> `asm/slothy/production/invntt_opt.production.s` | decap rminus1 path uses this body |
| shared production source | `gt_block_major_poly_invntt` body | `asm/slothy/production/invntt_opt.production.s` | same instruction body as normal InvNTT; rminus1 only changes branchfold constants |

The wrapper defines:

```asm
.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
```

## Input / Output Contract

Input `a`:

- `poly` in GT block-major layout produced by `poly_basemul_rminus1()`.
- The block-major body reads branch halves at `x1 + 0` and `x1 + 768`.
- Row input order is compile-time fixed by the three physical row maps in
  `DIRECT_STAGE123_STRIPE_SCRATCH_ROW{0,1,2}`.
- In-place use is required and currently used: `poly_invntt_from_rminus1(&m1, &m1)`.
  The kernel reads input into stage123 scratch / row buffers before final output
  stores, so this aliasing contract must be preserved.

Temporary layout:

- Stage123 writes a stripe-major scratch at `sp + 1568`.
- Stage45 consumes scratch as `[j, j+8, j+16, j+24]` contiguous q-vectors.
- Stage45 stores natural-order row buffers at:
  - row0: `sp + 32`
  - row1: `sp + 544`
  - row2: `sp + 1056`
- Branchfold post consumes those three row buffers through `x8/x9/x10`.

Output `r`:

- Normal time-domain `poly` coefficients in the representative contract required
  by `poly_crepmod3()`.
- Final branchfold reductions are active through
  `INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS`; this is part of the decap correctness
  contract and must not be removed by a scheduling pass.

## Montgomery / rminus1 Factor Contract

`poly_basemul_rminus1()` intentionally leaves one extra `R^-1` factor for this
InvNTT entry.  `asm/gt/poly_invntt_rminus1.S` uses the same row kernels and post
pipeline as normal InvNTT, but defines `INVNTT_INPUT_RMINUS1`, which switches
the final branchfold table to:

```text
asm/slothy/production/invntt_branchfold_vecs_rminus1.inc
```

The paired result is a normal `R^0` output suitable for `poly_crepmod3()`.
Therefore:

- `poly_invntt_from_rminus1()` is paired with `poly_basemul_rminus1()`.
- Normal `poly_invntt()` must not be substituted for the rminus1 product.
- Q31 encap byte-contract output must not be reused here; decap needs
  arithmetic-correct representatives, not only equivalent `poly_tobytes()`
  bytes.

## Slothy Region Markers

Marker labels were added to the production block-major body in
`asm/slothy/production/invntt_opt.production.s`.  They are labels/comments only and do not
change instruction selection, layout, or production defaults.

| marker pair | row | scope | first-pass use |
| --- | --- | --- | --- |
| `slothy_start_invntt_block_row0_stage123` / `slothy_end_invntt_block_row0_stage123` | row0 | direct input -> stage123 stripe scratch | audit/extract only; large macro expansion |
| `slothy_start_invntt_block_row0_stage45` / `slothy_end_invntt_block_row0_stage45` | row0 | stage45 scratch consumer + row-end reduction | primary scheduling candidate |
| `slothy_start_invntt_block_row1_stage123` / `slothy_end_invntt_block_row1_stage123` | row1 | direct input -> stage123 stripe scratch | audit/extract only |
| `slothy_start_invntt_block_row1_stage45` / `slothy_end_invntt_block_row1_stage45` | row1 | stage45 scratch consumer + row-end reduction | primary scheduling candidate |
| `slothy_start_invntt_block_row2_stage123` / `slothy_end_invntt_block_row2_stage123` | row2 | direct input -> stage123 stripe scratch | audit/extract only |
| `slothy_start_invntt_block_row2_stage45` / `slothy_end_invntt_block_row2_stage45` | row2 | stage45 scratch consumer + row-end reduction | primary scheduling candidate |
| `slothy_start_invntt_post_fused` / `slothy_end_invntt_post_fused` | post | inverse DFT3 + branchfold final store | existing marker; not a fusion task |

The stage45 row body is already Slothy-scheduled in the current production
source.  A future rerun should operate on an expanded source, use the row marker
labels as extraction boundaries, and keep prologue/epilogue and branchfold post
outside the first pass.

## Correctness Targets

Standalone InvNTT rminus1 correctness is already covered by:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
```

Expected correctness line:

```text
correctness,total_mismatches=0
```

That target checks:

- `poly_invntt_from_rminus1_stage45scratch` against full
  `poly_invntt_from_rminus1` modulo `q`.
- `poly_invntt_from_rminus1_crepmod3` against
  `poly_invntt_from_rminus1` followed by `poly_crepmod3`.
- crep3 stage123 scratch conversion against the normal stage123 scratch.
- crep3 stage45scratch output against the separate InvNTT + crepmod3 reference.

Full decap / KEM differential is covered by:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Expected correctness line:

```text
correctness,total_mismatches=0,valid_cases=64
```

This target exercises the current production KEM wrappers and includes the
decap sequence:

```text
poly_basemul_rminus1 -> poly_invntt_from_rminus1 -> poly_crepmod3
```

## Stable PMU Baseline

Use the dedicated InvNTT target for local kernel PMU:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
```

Default settings:

```text
GT_INVNTT_PMU_NTESTS=31
GT_INVNTT_PMU_NITERATIONS=10000
GT_INVNTT_PMU_NWARMUP=100
CORE=3
```

The latest recorded dedicated baseline in
`invntt-rowbuffer-post-pmu.md` was:

```text
poly_invntt_from_rminus1 = 4123.278 cycles/call, 5113 instr/call, IPC=1.2400
```

The latest full KEM component profile recorded:

```text
decap_invntt_rminus1 = 4024.985 cycles/call = 12.1% decap
```

Marker-only verification run on Pi5 after this target-prep change:

```text
command: make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
correctness,total_mismatches=0
poly_invntt_from_rminus1 = 4152.907 cycles/call, 5078 instr/call, IPC=1.2228

command: make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
correctness,total_mismatches=0,valid_cases=64
decap_invntt_rminus1 = 4024.297 cycles/call, 5074 instr/call, IPC=1.2608
```

After any Slothy-generated candidate, rerun both the standalone InvNTT PMU and
the full KEM component profile.  Do not benchmark without a zero-mismatch
correctness line.

## Next Slothy Handoff Checklist

Before running Slothy in a separate task:

1. Expand or extract the marker-bounded row regions so the Slothy input contains
   real AArch64 instructions, not only macro invocations.
2. Keep the first pass local to stage45 row regions unless a separate contract
   is written for stage123.
3. Preserve these live-ins for stage45:
   `x14` scratch base, `x2` row buffer base, `q0` q/Barrett constants.
4. Preserve row-buffer output layout and final branchfold representative
   contract.
5. Assemble the generated candidate.
6. Run `bench_gt_invntt_pmu` and require `correctness,total_mismatches=0`.
7. Run `bench_gt_kem_component_profile_pmu` and require
   `correctness,total_mismatches=0,valid_cases=64`.
8. Only then compare cycles/instructions/IPC against the stable PMU baseline.

Do not combine this with basemul-to-InvNTT fusion, crep3 fusion, Q31, or
hash/backend changes.
