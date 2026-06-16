# Gate 11 Rowpack Promotion / Forward Topology Decision

Status: `decision_report_no_benchmark_no_asm`

Decision: `C_keep_rowpack_research_path_not_production`

Do not promote lazy ASM rowpack to production, and do not start Forward
v4 assembly now.  Keep rowpack as an opt-in experimental backend and
only continue toward Forward v4 after a topology model predicts at least
`150 cycles/NTT` recoverable, preferably near `200 cycles/NTT`.

## Three-Way Baseline

| path | KPQC final | production GT | lazy ASM rowpack | rowpack vs KPQC | rowpack vs GT |
| --- | ---: | ---: | ---: | ---: | ---: |
| product_pipeline | 13473.203 | 12254.750 | 12363.188 | -1110.015 | +108.438 |
| product_add_pipeline | 16843.469 | 14996.453 | 15556.625 | -1286.844 | +560.172 |

## Component Blocker

| path | pipeline delta | accounted component delta | unaccounted glue delta | main visible blocker |
| --- | ---: | ---: | ---: | --- |
| product | +94.015 | +245.921 | -151.906 | Forward NTT x2 `+640.718`, basemul `-418.750`, InvNTT `+23.953` |
| product-add | +623.812 | +722.109 | -98.297 | Forward NTT x3 `+1040.250`, basemul_add `-337.141`, InvNTT `+19.000` |

Backend status:

- `basemul`: rowpack faster than production GT in fullchain stage accounting
- `basemul_add`: rowpack faster than production GT in fullchain stage accounting
- `invntt`: lazy ASM rowpack is production-near
- `glue`: not the blocker; rowpack unaccounted glue is cheaper in the latest accounting
- `forward_ntt`: remaining blocker; rowpack output ABI costs about 315-347 cycles/NTT

## Forward No-Go Evidence

| gate | closed path | result | reason |
| --- | --- | --- | --- |
| Gate 6 | v3 structured-store / st4 | `rejected` | correctness passes but Forward NTT regresses to about 3152 cycles; st4/lane-store style is the wrong primitive |
| Gate 8 | v3a final-only permutation | `rejected` | current v2 tail already matches the 24-permute/block lower bound under the allowed two-input Neon interleave model |
| Gate 9 | v3b stage345-only live-out rewrite | `rejected` | current stage12 scratch is k32-major and stage345 arithmetic is lane-preserving, so rowpack plane live-out still needs a 24-permute/block network |
| Gate 10 | v3c stage12 scratch-layout-only rewrite | `rejected` | partial scratch grouping is worse; fully rowpack-friendly scratch layout-only only moves the same 24-permute/block network earlier |

## Forward v4 Conditions

- scope: earlier than the stage12 scratch boundary; arithmetic topology, not only store/scratch layout
- minimum continue gate: `150 cycles/NTT`
- preferred continue gate: `200 cycles/NTT`

Forbidden next steps:

- do not write v4 ASM before a topology model
- do not rerun Slothy on rejected v3 DAGs
- do not use st4, lane stores, scalar scatter, or scalar GT-to-rowpack conversion as the fix

## Option Decision

| option | decision | reason |
| --- | --- | --- |
| `A_continue_to_forward_topology_rewrite` | `not_now` | no v4 topology model currently predicts >=150 cycles/NTT recoverable under a valid arithmetic/live-layout plan |
| `B_archive_rowpack_as_experimental_backend` | `too_strong` | rowpack clearly beats KPQC final and remains valuable as a research baseline |
| `C_keep_rowpack_research_path_not_production` | `selected` | rowpack backend is strong, but production GT remains faster and simple Forward layout fixes are closed |

One-line conclusion: Gate 10 closes the small Forward-output-layout
patch route.  Rowpack is a strong experimental backend, but promotion
requires a larger Forward v4 arithmetic topology model before any new
ASM or Slothy work.
