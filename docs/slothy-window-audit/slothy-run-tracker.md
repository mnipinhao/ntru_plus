# Slothy Run Tracker

This tracker records audit-only, planned, optimized, rejected, and promoted
Slothy attempts.  Rows with `Slothy command = not run` are not optimizer runs;
they are still recorded so later generated artifacts can be traced back to the
contract and baseline that justified the attempt.

Status values:

```text
audit-only
manifest-ready
planned
preflight-blocked
materialized
parse-pass
optimized
assemble-pass
correctness-pass
kem-pass
pmu-win
rejected
promoted
```

## Runs

| run id | date | target | region | source marker commit | manifest commit | generated candidate commit | status | Slothy command | parser status | assemble status | standalone correctness | full KEM correctness | local cycles/instr | full API cycles/instr | decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INVNTT-RM1-AUDIT-20260629 | 2026-06-29 | InvNTT rminus1 | marker-only production block-major audit | `b44c5cd` | n/a | n/a | audit-only | not run | not run | pass via `bench_gt_invntt_pmu` build | `correctness,total_mismatches=0` | `correctness,total_mismatches=0,valid_cases=64` | `poly_invntt_from_rminus1`: 4152.907 cycles / 5078 instr | `decap_invntt_rminus1`: 4024.297 cycles / 5074 instr | keep as baseline | Marker labels and contract only; no Slothy, no generated candidate. |
| INVNTT-RM1-MANIFEST-20260629 | 2026-06-29 | InvNTT rminus1 | all marker-bounded windows | `b44c5cd` | `0edf12e` | n/a | manifest-ready | not run | not run | pass via `bench_gt_invntt_pmu` build | `correctness,total_mismatches=0` | `correctness,total_mismatches=0,valid_cases=64` | `poly_invntt_from_rminus1`: 4153.602 cycles / 5078 instr | `decap_invntt_rminus1`: 4024.475 cycles / 5074 instr | manifest complete | Row-level manifest and tracker; no production behavior change. |
| INVNTT-RM1-ROW1-STAGE45-STRIPES2-3-PLAN-001 | 2026-06-30 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3` | `b44c5cd` | `0edf12e` | n/a | planned | not run | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | planned run order 1 | First normal stripe-level candidate; 84 instructions, non-edge stripe pair, complete reduction/store groups. |
| INVNTT-RM1-ROW1-STAGE45-STRIPES2-3-RUN-001 | 2026-06-30 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3` | `b44c5cd` | `a19152f` | n/a | preflight-blocked | not run; preflight failed before Slothy | not run; source labels missing | not run | not run | not run | not measured | not measured | blocked before parser | Preflight found only the full row labels `slothy_start_invntt_block_row1_stage45` / `slothy_end_invntt_block_row1_stage45`. The concrete stripes2-3 start/end labels did not exist, and the 337-instruction row-level window was not run as a substitute. |
| INVNTT-RM1-ROW1-STAGE45-STRIPES2-3-RUN-002 | 2026-06-30 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45-STRIPES2-3` | `b44c5cd` | `9166b2d` | n/a | planned | not run; use materialized source labels | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | planned next Slothy run | Materialized benchmark-only source: `asm/slothy/window_inputs/invntt_rminus1_row1_stage45_stripes_marked.s`; start/end labels `slothy_start_invntt_rm1_row1_stage45_stripes2_3` / `slothy_end_invntt_rm1_row1_stage45_stripes2_3`; count/equivalence check passed. |
| INVNTT-RM1-ROW1-STAGE45-STRIPES4-5-PLAN-001 | 2026-06-30 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45-STRIPES4-5` | `b44c5cd` | `0edf12e` | n/a | planned | not run | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | planned run order 2 | Second normal stripe-level candidate; same 84-instruction shape as stripes2-3. |
| INVNTT-RM1-ROW1-STAGE45-PLAN-001 | 2026-06-29 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45` | `b44c5cd` | `0edf12e` | n/a | planned | not run | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | planned run order 3, split-heuristic stress only | 337-instruction row-stage45 window; too large for a normal window and should not be run before stripe-level candidates. |
| INVNTT-RM1-ROW1-STAGE45-STRIPES0-1-PLAN-001 | 2026-06-30 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45-STRIPES0-1` | `b44c5cd` | `0edf12e` | n/a | planned | not run | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | later stripe candidate | 84 instructions and clean store boundary, but j=0 has edge-case constants. |
| INVNTT-RM1-ROW1-STAGE45-STRIPES6-7-PLAN-001 | 2026-06-30 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45-STRIPES6-7` | `b44c5cd` | `0edf12e` | n/a | planned | not run | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | later stripe candidate | 84 instructions and clean store boundary, but closest to row tail. |

## Required Post-Run Gates

Any future Slothy-generated InvNTT rminus1 candidate must pass these before it
can be promoted:

```sh
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_invntt_pmu SUDO= CORE=3
make -C ntruplus-ntt-Optimized/aarch64-bench -B bench_gt_kem_component_profile_pmu SUDO= CORE=3
```

Required correctness:

```text
correctness,total_mismatches=0
correctness,total_mismatches=0,valid_cases=64
```

Do not evaluate PMU deltas if either correctness line is missing or nonzero.
