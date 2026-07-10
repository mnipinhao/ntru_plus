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
| kem_keygen | 39966 | 37982 | 37966 | -5.004% | -0.042% |
| kem_enc | 39013 | 37755 | 37590 | -3.648% | -0.437% |
| kem_dec | 35180 | 32629 | 32482 | -7.669% | -0.451% |

## Instructions

| Operation | KPQC final | GT legacy | GT new | New vs KPQC | New vs legacy |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 80801 | 81147 | 81147 | +0.428% | +0.000% |
| kem_enc | 103980 | 105650 | 105124 | +1.100% | -0.498% |
| kem_dec | 72677 | 74932 | 74406 | +2.379% | -0.702% |

## Cycle Distributions

| Operation | Variant | p10 | p50 | p90 |
|---|---|---:|---:|---:|
| kem_keygen | gt_production_default | 37960 | 37966 | 37973 |
| kem_keygen | gt_production_legacy_ntt | 37978 | 37982 | 37989 |
| kem_keygen | kpqc_final | 39963 | 39966 | 39970 |
| kem_enc | gt_production_default | 37584 | 37590 | 37599 |
| kem_enc | gt_production_legacy_ntt | 37749 | 37755 | 37762 |
| kem_enc | kpqc_final | 39010 | 39013 | 39018 |
| kem_dec | gt_production_default | 32476 | 32482 | 32490 |
| kem_dec | gt_production_legacy_ntt | 32626 | 32629 | 32639 |
| kem_dec | kpqc_final | 35179 | 35180 | 35182 |

## Binary Metadata

| Variant | Text bytes | poly_ntt bytes | poly_ntt mod32/mod64 |
|---|---:|---:|---:|
| gt_production_default | 160081 | 14904 | 16/16 |
| gt_production_legacy_ntt | 150305 | n/a | n/a/n/a |
| kpqc_final | 40617 | n/a | n/a/n/a |

All runs completed the harness setup KEM correctness check before measurement.
Keypair is reported but G1R123+S2 is not expected to improve it because the GT keypair path uses the specialized triple NTT.
