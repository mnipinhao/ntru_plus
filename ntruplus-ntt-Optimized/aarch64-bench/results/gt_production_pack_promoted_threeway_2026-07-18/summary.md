# GT Production Three-Way Full-KEM Benchmark

Pi 5 Cortex-A76, core pinned, portable NO_CE hash path.
Each cell is the median of 61 samples with 2000 calls per sample.

Variants:

- new: canonical GT production with frontend DCE + fixed-register Slothy schedule
- original: canonical GT production with the pre-Slothy source-order frontend
- kpqc: unmodified KPQC final

## Cycles

| Operation | KPQC final | GT source-order | GT new | New vs KPQC | New vs source-order |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39962 | 38755 | 38634 | -3.323% | -0.312% |
| kem_enc | 39023 | 39519 | 37667 | -3.475% | -4.686% |
| kem_dec | 35182 | 33747 | 33481 | -4.835% | -0.788% |

## Cycle Distributions

| Operation | Variant | p10 | p50 | p90 |
|---|---|---:|---:|---:|
| kem_keygen | gt_production_default | 38631 | 38634 | 38639 |
| kem_keygen | gt_production_source_order | 38750 | 38755 | 38763 |
| kem_keygen | kpqc_final | 39960 | 39962 | 39965 |
| kem_enc | gt_production_default | 37660 | 37667 | 37673 |
| kem_enc | gt_production_source_order | 39514 | 39519 | 39527 |
| kem_enc | kpqc_final | 39017 | 39023 | 39036 |
| kem_dec | gt_production_default | 33476 | 33481 | 33491 |
| kem_dec | gt_production_source_order | 33742 | 33747 | 33752 |
| kem_dec | kpqc_final | 35179 | 35182 | 35185 |

## Binary Metadata

| Variant | Text bytes | poly_ntt bytes | poly_ntt mod32/mod64 |
|---|---:|---:|---:|
| gt_production_default | 176737 | 14776 | 16/48 |
| gt_production_source_order | 176865 | 14904 | 16/48 |
| kpqc_final | 41537 | n/a | n/a/n/a |

All runs completed the harness setup KEM correctness check before measurement.
Keypair is reported but G1R123+S2 is not expected to improve it because the GT keypair path uses the specialized triple NTT.
