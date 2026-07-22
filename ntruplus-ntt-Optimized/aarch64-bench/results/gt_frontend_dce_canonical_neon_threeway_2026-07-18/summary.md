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
| kem_keygen | 39945 | 38609 | 38589 | -3.395% | -0.052% |
| kem_enc | 39047 | 38290 | 38212 | -2.138% | -0.204% |
| kem_dec | 35181 | 33700 | 33569 | -4.582% | -0.389% |

## Cycle Distributions

| Operation | Variant | p10 | p50 | p90 |
|---|---|---:|---:|---:|
| kem_keygen | gt_production_default | 38578 | 38589 | 38601 |
| kem_keygen | gt_production_source_order | 38601 | 38609 | 38623 |
| kem_keygen | kpqc_final | 39943 | 39945 | 39947 |
| kem_enc | gt_production_default | 38207 | 38212 | 38215 |
| kem_enc | gt_production_source_order | 38285 | 38290 | 38297 |
| kem_enc | kpqc_final | 39044 | 39047 | 39054 |
| kem_dec | gt_production_default | 33564 | 33569 | 33576 |
| kem_dec | gt_production_source_order | 33698 | 33700 | 33705 |
| kem_dec | kpqc_final | 35180 | 35181 | 35184 |

## Binary Metadata

| Variant | Text bytes | poly_ntt bytes | poly_ntt mod32/mod64 |
|---|---:|---:|---:|
| gt_production_default | 170561 | 14776 | 16/16 |
| gt_production_source_order | 170689 | 14904 | 16/16 |
| kpqc_final | 40601 | n/a | n/a/n/a |

All runs completed the harness setup KEM correctness check before measurement.
Keypair is reported but G1R123+S2 is not expected to improve it because the GT keypair path uses the specialized triple NTT.
