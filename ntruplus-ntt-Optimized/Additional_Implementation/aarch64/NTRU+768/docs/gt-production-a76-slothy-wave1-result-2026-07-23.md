# Cortex-A76 Slothy Wave 1 Result

Date: 2026-07-23

This records the completed Gate 0 and Wave 1 rerun from
`gt-production-clean-release-a76-slothy-rerun-plan-2026-07-23.md`. Generated
symbolic sources, schedules, logs, and object files were removed after this
summary because no result passed the modeled performance gate.

## Environment

- Production source revision:
  `87b5f8ada2c6d087233fac8385b6f8a50f5f1e62`
- Remote Slothy revision:
  `4aac4afdd05c5f107c4748a6d4e4df663907d87f`
- Target: `slothy.targets.aarch64.cortex_a76`
- A76 target SHA-256:
  `20f48fdecc973c3339cf7b22bf888913dff1a0e3932581a93ef473092865219f`
- A76 model tests: 9 passed
- Primary candidates: `allow_spills=false`

## Result

| Window | Instructions | A76 expected cycles | Source -> candidate last issue |
|---|---:|---:|---:|
| InvNTT Stage123 single block | 83 | 20 | 20 -> 20 |
| InvNTT Stage123 two blocks | 166 | 41 | 41 -> 41 |
| InvNTT Stage45 two stripes | 78 | 19 | 19 -> 19 |
| InvNTT Stage45 four stripes | 162 | 40 | 40 -> 40 |
| InvNTT Stage45 full row | 330 | 82 | 82 -> 82 |
| Decap verify group | 100 | 25 | 24 -> 24 |
| Baseinv finish one/two iterations | 34 / 68 | 8 / 17 | 8 / 16 unchanged |
| Baseinv tree independent windows | 34-130 | 8-32 | unchanged |

Fixed and rename variants reached the same A76 objective for every applicable
window. Stage123's two-block window modeled at 41 cycles, versus 40 for two
independent single-block windows. The decap verify group already reached the
four-instruction issue-rate bound.

## Gates And Decision

- 26 formal Slothy outputs solved.
- All formal outputs cross-assembled.
- All five baseline/candidate contracts matched.
- No spills were introduced.
- No candidate reduced the A76 modeled schedule span.
- No candidate was integrated into production.
- Differential, ABI, KAT, and Pi 5 PMU candidate tests were not run because no
  schedule advanced past the modeled performance gate.

Overall status: `investigate`, with no promotion. Wave 2 serialization and
forward-NTT windows remain separate future work.
