# InvNTT rminus1 Window Audit

Date: 2026-06-29

Status: manifest-ready, documentation-only.  Slothy was not run.

## Target

Production decap path:

```c
poly_basemul_rminus1(&m1, &c, &f);
poly_invntt_from_rminus1(&m1, &m1);
poly_crepmod3(&m1, &m1);
```

ASM source basis:

```text
source marker commit: b44c5cd Prepare InvNTT rminus1 Slothy target
wrapper: ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/inv_my_ntt_rminus1.S
shared body: ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/invntt_opt.production.s
```

The rminus1 wrapper aliases the normal production InvNTT body and switches the
final branchfold table through `INVNTT_INPUT_RMINUS1`.  It does not use a
different row-stage algorithm.

## Contracts

Input:

- GT block-major `poly` produced by `poly_basemul_rminus1()`.
- The input carries one extra `R^-1` factor.
- In-place call is production-relevant: `poly_invntt_from_rminus1(&m1, &m1)`.

Temporary layout:

- Stage123 writes stripe-major scratch at `sp + 1568`.
- Stage45 consumes scratch as `[j, j+8, j+16, j+24]` q-vector stripes.
- Stage45 writes row buffers:
  - row0: `sp + 32`
  - row1: `sp + 544`
  - row2: `sp + 1056`
- Branchfold post consumes those row buffers through `x8`, `x9`, and `x10`.

Output:

- Normal time-domain `R^0` coefficients.
- Representative contract must remain valid for immediate `poly_crepmod3()`.
- `INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS` is part of the production contract.

Out of scope:

- Slothy run.
- New `.opt.s` candidate.
- Basemul-to-InvNTT fusion.
- Crep3 fusion.
- Q31 byte-contract path.
- Polyinv rewrite.
- Production default change.

## Marker Windows

Expanded instruction counts were measured from the Pi5-built
`bench_gt_invntt_pmu_bin` with `nm` and `objdump`, using the first set of marker
labels in the normal rminus1 wrapper.  The crep3 wrapper produces a second set
of duplicate local marker names in the binary; that second set is not used for
this manifest.

| window | instructions | memory reads | memory writes | recommendation |
| --- | ---: | ---: | ---: | --- |
| row0_stage123 | 420 | 66 | 32 | audit_only |
| row0_stage45 | 337 | 48 | 32 | candidate |
| row1_stage123 | 420 | 66 | 32 | audit_only |
| row1_stage45 | 337 | 48 | 32 | first_candidate |
| row2_stage123 | 420 | 66 | 32 | candidate |
| row2_stage45 | 337 | 48 | 32 | candidate |
| post_fused | 431 | 75 | 30 | needs_review |
| whole_function | 7103 | 1011 | 609 | reject |

## First Candidate

`INVNTT-RM1-ROW1-STAGE45` is the first candidate, but only under a
split-heuristic-only policy:

- It is isolated between stage123 scratch production and row-buffer output.
- It avoids public ABI prologue/epilogue and the final branchfold post path.
- It is representative-neutral as long as row-buffer store layout and row-end
  reductions are preserved.
- It is 337 instructions, so it is not a normal 70-150 instruction window.

If Slothy cannot parse or solve this row window, the next preparation step is to
extract smaller stage45 stripe windows or use the existing stage45 stripe macro
as the source of a narrower symbolic target.  That is a separate task.

## Rejected Or Deferred Windows

Stage123 rows are audit/extract only:

- They expand to 420 instructions each.
- They include direct physical input loads, butterfly chains, and scratch
  layout stores.
- They should not be optimized until there is a separate input-layout and
  scratch-layout contract.

`post_fused` is not first pass:

- It includes inverse DFT3.
- It mutates row-buffer and output pointers.
- It includes branchfold constants, final output reductions, and final output
  stores.
- It is representative-sensitive for `poly_crepmod3()`.

Whole function is rejected:

- It crosses public ABI scaffolding, all three rows, post path, and exposed
  stage123scratch ABI code in the symbol range.
- It is 7103 static instructions in the measured symbol range.

Basemul-to-InvNTT fusion is rejected for this pass because the current task is
window manifest/tracking only, and prior PMU data showed the measured decap
basemul-to-InvNTT boundary estimate was too small to justify a fusion mainline.

## Verification Baseline

Standalone target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
```

Expected:

```text
correctness,total_mismatches=0
poly_invntt_from_rminus1 = 4152.907 cycles/call, 5078 instr/call
```

Full KEM component target:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Expected:

```text
correctness,total_mismatches=0,valid_cases=64
decap_invntt_rminus1 = 4024.297 cycles/call, 5074 instr/call
```

Any future Slothy candidate must pass both targets before PMU data is used for
a decision.
