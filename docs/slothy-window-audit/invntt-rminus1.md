# InvNTT rminus1 Window Audit

Date: 2026-06-29
Refined: 2026-06-30

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
| row1_stage45 | 337 | 48 | 32 | candidate, split-heuristic-only |
| row2_stage123 | 420 | 66 | 32 | audit_only |
| row2_stage45 | 337 | 48 | 32 | candidate |
| post_fused | 431 | 75 | 30 | needs_review |
| whole_function | 7103 | 1011 | 609 | reject |

## ROW1-STAGE45 Subwindows

`INVNTT-RM1-ROW1-STAGE45` is a 337-instruction row-level window.  It is too
large for a normal first Slothy pass, so the refined manifest adds stripe-pair
subwindows derived from the canonical `INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH`
macro.  Each stripe macro is 42 instructions, so two complete stripes form an
84-instruction window.  This keeps every butterfly, reduction chain, and
row-buffer store group intact.

The current production row macro is already cross-stripe scheduled.  Therefore
these subwindows are extraction targets for a future symbolic/perstripe source,
not labels that already exist in `invntt_opt.production.s`.

2026-06-30 preflight for `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3` confirmed that
only the full row labels exist in the production source:
`slothy_start_invntt_block_row1_stage45` and
`slothy_end_invntt_block_row1_stage45`.  There are no concrete
`STRIPES2-3` start/end labels in the source or marker flow, so RUN-001 was
stopped before Slothy.  The 337-instruction row-level window was not used as a
substitute.  A later run must first materialize exact stripes2-3 extraction
labels/source; otherwise this window remains a semantic candidate only.

2026-06-30 materialization created a benchmark-only Slothy input source at
`ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s`.
It does not modify production assembly and is not included by production
wrappers.  The required concrete labels are:
`slothy_start_invntt_rm1_row1_stage45_stripes2_3` and
`slothy_end_invntt_rm1_row1_stage45_stripes2_3`.
The check script reports parent count 337, child count 84, and equivalence
against the canonical production per-stripe macro expansion.  A contiguous
parent-slice comparison is not applicable because the production parent row is
already cross-stripe scheduled.

| subwindow | stripes | instructions | memory reads | memory writes | recommendation |
| --- | ---: | ---: | ---: | ---: | --- |
| `INVNTT-RM1-ROW1-STAGE45-STRIPES0-1` | 0-1 | 84 | 12 | 8 | candidate |
| `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3` | 2-3 | 84 | 12 | 8 | materialized / planned |
| `INVNTT-RM1-ROW1-STAGE45-STRIPES4-5` | 4-5 | 84 | 12 | 8 | candidate |
| `INVNTT-RM1-ROW1-STAGE45-STRIPES6-7` | 6-7 | 84 | 12 | 8 | candidate |

2026-06-30 campaign `INVNTT-RM1-ROW1-STAGE45-STRIPES-CAMPAIGN-001` ran all
four stripe-pair windows on the remote Slothy host.  All four parsed and solved
in normal mode without split heuristic.  `STRIPES2-3` was kept as the
benchmark-only current best because it was the first active target and tied the
other windows in the Slothy model result: 88 cycles and 67 stalls.

Pi5 benchmark-only row1 materialized result:

| variant | cycles/call | instr/call | result |
| --- | ---: | ---: | --- |
| materialized canonical ROW1-STAGE45 row1 | 624.673 | 357 | pass |
| materialized + Slothy `STRIPES2-3` | 616.679 | 357 | pass, -1.28% |

Production `poly_invntt_from_rminus1` remained unchanged and measured 4144.795
cycles/call in the same `bench_gt_invntt_pmu` run.  KEM component profiling
reported `decap_invntt_rminus1 = 4024.731` cycles/call with
`correctness,total_mismatches=0,valid_cases=64`.

2026-06-30 scaling campaign `INVNTT-RM1-STAGE45-SCALING-CAMPAIGN-002`
retested the row1 materialized path and built an all-four Slothy stripe-pair
candidate.  Correctness still passed, but the performance result did not scale:

| variant | cycles/call | instr/call | result |
| --- | ---: | ---: | --- |
| materialized canonical ROW1-STAGE45 row1 | 543.266 | 357 | pass |
| materialized + Slothy `STRIPES2-3` | 612.778 | 357 | pass, slower |
| materialized + all-four Slothy stripes | 625.327 | 357 | pass, slower |

The production-scheduled 337-instruction row1 Stage45 split-heuristic stress
attempt reached Slothy parsing with 337 instructions, then failed on
`adr x3, invntt32_stage45_consts`.  No fullrow candidate was produced.

Current conclusion: stop the canonical row1 Stage45 stripe route.  Do not clone
this route to row0/row2 unless a new production-row contract or parser/model
fix changes the evaluation target.

## Planned Run Order

1. `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3`

   Completed as RUN-002.  Later scaling retest regressed, so it is no longer an
   active best and is not promoted to production.

2. `INVNTT-RM1-ROW1-STAGE45-STRIPES4-5`

   Solved during the scaling campaign.  Do not extend the canonical stripe
   route further because all-four row1 PMU regressed.

3. `INVNTT-RM1-ROW1-STAGE45`

   Row-level stress test only.  One split-heuristic attempt failed in the parser
   on `adr x3, invntt32_stage45_consts`; parser/model support is needed before
   this route can continue.

`INVNTT-RM1-ROW1-STAGE45` remains useful as a row-level audit/stress window:

- It is isolated between stage123 scratch production and row-buffer output.
- It avoids public ABI prologue/epilogue and the final branchfold post path.
- It is representative-neutral as long as row-buffer store layout and row-end
  reductions are preserved.
- It is 337 instructions, so it is not a normal 70-150 instruction window.

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
