# Forward NTT Production Window Manifest

Date: 2026-06-30

Scope: production-contract Forward NTT window selection for
`poly_ntt` / `gt_block_major_poly_ntt`.  This manifest only considers the
production block-major row-bitrev path:

```text
asm/gt/poly_ntt_gt_production.s
asm/slothy/production/my_32ntt.opt.s
```

Rowspec, oldstore, ldrtrn, rowpack, tuple, BPQ, and TMVP candidate paths are
out of scope.

## Production Contract

Input is a natural-order `poly`.  Output is GT block-major row-bitrev layout.
The output is consumed directly by GT base inverse, GT basemul variants,
`poly_tobytes`, and decap `poly_sub`/verify paths.  A Slothy candidate must not
change this physical layout.

## Window Summary

| window | source | instructions | policy | recommendation |
| --- | --- | ---: | --- | --- |
| `FWD-NTT-PHASE123-ITER0` | `asm/slothy/production/my_ntt_phase123.n1.opt.s` | 160 | split-heuristic-only | audit later |
| `FWD-NTT-NTT32-STAGE12-STRIPES0-3` | `asm/slothy/production/my_32ntt.opt.s` | 103 | normal | attempted, parser-blocked by internal labels |
| `FWD-NTT-NTT32-STAGE12-STRIPES4-7` | `asm/slothy/production/my_32ntt.opt.s` | 103 | normal | later only if label-clean input is materialized |
| `FWD-NTT-NTT32-STAGE345-BLOCK0` | `asm/slothy/production/my_32ntt.opt.s` | 167 | split-heuristic-only | later only with safer integration plan |
| `FWD-NTT-NTT32-STAGE345-BLOCK1` | `asm/slothy/production/my_32ntt.opt.s` | 160 | split-heuristic-only | attempted, generated candidate crashed KEM profiler |
| `FWD-NTT-NTT32-BLOCK0-FINAL-REDUCE-STORE` | `asm/slothy/window_inputs/forward_ntt_ntt32_final_store_marked.s` | 81 | normal | attempted, solver infeasible |

## Materialized Final-Store Input

Production `asm/slothy/production/my_32ntt.opt.s` already has stage12 and stage345 block
labels, but it does not have exact final-reduction/store subwindow labels.  The
benchmark-only helper below creates a production-derived marked input copy:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/materialize_forward_ntt_production_windows.py
```

Generated input:

```text
ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/forward_ntt_ntt32_final_store_marked.s
```

Validation command:

```sh
python3 ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/asm/slothy/window_inputs/materialize_forward_ntt_production_windows.py --write
```

Validation result:

```text
block0 parent_instruction_count=167 child_instruction_count=81 equivalence_check=pass
block1 parent_instruction_count=160 child_instruction_count=98 equivalence_check=pass
block2 parent_instruction_count=162 child_instruction_count=98 equivalence_check=pass
block3 parent_instruction_count=162 child_instruction_count=99 equivalence_check=pass
```

The check normalizes labels, comments, blank lines, and local marker names, then
compares instruction text against the corresponding production slice.

## First Campaign Selection

Initial production-contract campaign windows:

1. `FWD-NTT-NTT32-BLOCK0-FINAL-REDUCE-STORE`
2. `FWD-NTT-NTT32-STAGE12-STRIPES0-3`
3. `FWD-NTT-NTT32-STAGE345-BLOCK1`

Rationale: final reduction/store is layout-sensitive, stage12 has a normal-size
grouped window, and stage345 is the meaningful NTT32 arithmetic block.  Phase123
was not selected for the first campaign because each production iteration is
already a 160-instruction split-heuristic window and the immediate risk is
lower than NTT32 final-store/stage345.

## Resulting Readiness

The first campaign did not produce a viable candidate:

- block0 final-reduction/store parsed but was solver-infeasible at 256/512
  stalls.
- stage12 stripes0-3 was parser-blocked by internal marker labels when using
  the production source directly.
- stage345 block1 split-heuristic solved and selfchecked, but the benchmark-only
  KEM component build crashed before correctness output.

Decision: do not continue small local Forward NTT Slothy windows as a direct
optimization route.  The target now needs a structural/window-contract strategy:
label-clean materialized inputs, explicit live-out contracts, and safer
candidate integration before another campaign.
