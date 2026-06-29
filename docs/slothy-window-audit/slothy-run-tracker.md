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

| run id | date | target | region | source commit | status | Slothy command | parser status | assemble status | standalone correctness | full KEM correctness | local cycles/instr | full API cycles/instr | decision | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| INVNTT-RM1-AUDIT-20260629 | 2026-06-29 | InvNTT rminus1 | marker-only production block-major audit | `b44c5cd` | audit-only | not run | not run | pass via `bench_gt_invntt_pmu` build | `correctness,total_mismatches=0` | `correctness,total_mismatches=0,valid_cases=64` | `poly_invntt_from_rminus1`: 4152.907 cycles / 5078 instr | `decap_invntt_rminus1`: 4024.297 cycles / 5074 instr | keep as baseline | Marker labels and contract only; no Slothy, no generated candidate. |
| INVNTT-RM1-MANIFEST-20260629 | 2026-06-29 | InvNTT rminus1 | all marker-bounded windows | `b44c5cd` | manifest-ready | not run | not run | pass via `bench_gt_invntt_pmu` build | `correctness,total_mismatches=0` | `correctness,total_mismatches=0,valid_cases=64` | `poly_invntt_from_rminus1`: 4153.602 cycles / 5078 instr | `decap_invntt_rminus1`: 4024.475 cycles / 5074 instr | manifest complete | Added window manifest and run tracker; no production behavior change. |
| INVNTT-RM1-ROW1-STAGE45-PLAN-001 | 2026-06-29 | InvNTT rminus1 | `INVNTT-RM1-ROW1-STAGE45` | `b44c5cd` | planned | not run | not run | not run | not run | baseline comparator: 4152.907 cycles / 5078 instr | baseline comparator: 4024.297 cycles / 5074 instr | planned first candidate | 337-instruction row-stage45 window; only acceptable as split-heuristic-only. If too large, split into smaller stripe windows before optimizing. |

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
