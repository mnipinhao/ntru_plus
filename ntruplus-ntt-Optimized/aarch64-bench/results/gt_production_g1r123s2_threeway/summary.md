# GT Production Three-Way Full-KEM Benchmark

Pi 5 Cortex-A76, core pinned, portable NO_CE hash path.
Each cell is the median of 61 samples with 2000 calls per sample.

Variants:

- new: promoted G1R123+S2 GT production
- legacy: original GT production forward NTT
- kpqc: unmodified KPQC final

## Cycles

| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39957 | 37980 | 37945 | -5.035% | -0.092% |
| kem_enc | 39023 | 37679 | 37633 | -3.562% | -0.122% |
| kem_dec | 35159 | 33078 | 32963 | -6.246% | -0.348% |

## Instructions

| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 80801 | 81147 | 81147 | +0.428% | +0.000% |
| kem_enc | 103980 | 105650 | 105124 | +1.100% | -0.498% |
| kem_dec | 72677 | 75192 | 74666 | +2.737% | -0.700% |

## Cycle Distributions

| Operation | Variant | p10 | p50 | p90 |
|---|---|---:|---:|---:|
| kem_keygen | gt_production_default | 37942 | 37945 | 37951 |
| kem_keygen | gt_production_legacy_ntt | 37976 | 37980 | 37987 |
| kem_keygen | kpqc_final | 39955 | 39957 | 39960 |
| kem_enc | gt_production_default | 37626 | 37633 | 37638 |
| kem_enc | gt_production_legacy_ntt | 37675 | 37679 | 37689 |
| kem_enc | kpqc_final | 39019 | 39023 | 39028 |
| kem_dec | gt_production_default | 32958 | 32963 | 32970 |
| kem_dec | gt_production_legacy_ntt | 33074 | 33078 | 33089 |
| kem_dec | kpqc_final | 35154 | 35159 | 35165 |

## Binary Metadata

| Variant | Text bytes | poly_ntt bytes | poly_ntt mod32/mod64 |
|---|---:|---:|---:|
| gt_production_default | 162225 | 14904 | 16/16 |
| gt_production_legacy_ntt | 152449 | n/a | n/a/n/a |
| kpqc_final | 40617 | n/a | n/a/n/a |

All runs completed the harness setup KEM correctness check before measurement.
Keypair is reported but G1R123+S2 is not expected to improve it because the GT keypair path uses the specialized triple NTT.
