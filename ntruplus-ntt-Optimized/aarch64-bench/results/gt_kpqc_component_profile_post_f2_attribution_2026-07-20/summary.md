# GT Production vs KPQC Final Detailed Profile

Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.
Each row is p50 of 31 samples x 2000 calls; warmup=100.
Both binaries run deterministic KEM setup and correctness checks before PMU; the component mode also runs a reconstructed-ciphertext decapsulation postflight. Full KEM totals are decisive; component subtotals omit copies/call overhead and are used for hotspot attribution only.
Cycles and retired instructions are collected in separate counter builds/runs. Derived CPI is therefore diagnostic rather than a same-group atomic PMU sample.

## Measurement Environment

- Git HEAD: `unavailable (rsync mirror)` (not a Git worktree)
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- Host: `Linux pinhao 6.18.33+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.18.33-1+rpt1 (2026-06-01) aarch64 GNU/Linux`

## Full KEM

| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39941/39943/39945 | 38262/38266/38270 | -4.20% | 80801 | 82520 |
| kem_enc | 39072/39074/39077 | 37670/37677/37680 | -3.58% | 103980 | 106191 |
| kem_dec | 35157/35159/35162 | 32887/32899/32907 | -6.43% | 72677 | 76429 |


## Primitive Kernels

These rows compare isolated public kernels. Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3611 | 2873 | -20.44% | 3265 | 3708 | 1.106 | 0.775 |
| TRANSFORM | inverse_ntt_generic | 3977 | 4076 | +2.49% | 3472 | 5093 | 1.145 | 0.800 |
| POINTWISE | basemul | 2679 | 2843 | +6.12% | 2493 | 2495 | 1.075 | 1.139 |
| POINTWISE | basemul_add | 2630 | 2922 | +11.10% | 2616 | 2810 | 1.005 | 1.040 |
| POINTWISE | baseinv_generic | 4056 | 4986 | +22.93% | 4298 | 4432 | 0.944 | 1.125 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14225 | 12941 | -9.03% | 12477 | 14986 | 1.140 | 0.864 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17818 | 16351 | -8.23% | 15857 | 19001 | 1.124 | 0.861 |
| SERIALIZE | ntt_tobytes_internal_layout | 459 | 399 | -13.07% | 784 | 784 | 0.585 | 0.509 |
| SERIALIZE | ntt_frombytes_internal_layout | 328 | 302 | -7.93% | 568 | 568 | 0.577 | 0.532 |
| SERIALIZE | ntt_tobytes_canonical | 459 | 616 | +34.20% | 784 | 1369 | 0.585 | 0.450 |
| SERIALIZE | ntt_frombytes_canonical | 328 | 489 | +49.09% | 568 | 1105 | 0.577 | 0.443 |
| SUPPORT | cbd1 | 305 | 305 | +0.00% | 500 | 500 | 0.610 | 0.610 |
| SUPPORT | triple | 196 | 192 | -2.04% | 199 | 197 | 0.985 | 0.975 |
| SUPPORT | crepmod3 | 400 | 384 | -4.00% | 398 | 398 | 1.005 | 0.965 |
| SUPPORT | poly_sub | 173 | 173 | +0.00% | 225 | 225 | 0.769 | 0.769 |
| SUPPORT | sotp_encode | 322 | 322 | +0.00% | 521 | 521 | 0.618 | 0.618 |
| SUPPORT | sotp_decode | 310 | 310 | +0.00% | 542 | 542 | 0.572 | 0.572 |

## Actual KEM-Path Components

`path` rows are non-overlapping call-graph components. `combined` rows are boundary diagnostics and are excluded from weighted subtotals.
These rows use fixed, deterministic buffers reconstructed from a valid KEM key/ciphertext and satisfy each GT representation/range contract.
GT keygen uses the scaled-factor chain `poly_baseinv_scaled_r` -> hierarchical K=8 batch inversion -> `gt_fqinv15_asm` -> Neon finish, followed by `poly_basemul_scaled_r_input`. Its baseinv and basemul rows must therefore be interpreted together, not as independent normal-factor drop-in kernels.
The decapsulation verify path is compared as one logical `dec_verify_product_to_bytes_actual` row: GT calls the promoted F2 fused canonical backend, while KPQC calls its normal basemul followed by pack. The separate generic basemul and pack rows are diagnostics and are not included in the path subtotal.

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2724 | 2719 | -0.18% | -10 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 2721 | -25.29% | -921 | 3461 | 4194 |
| path | keygen_sample_ntt_g | 1 | 3638 | 2723 | -25.15% | -915 | 3456 | 4191 |
| path | keygen_baseinv_actual | 2 | 4056 | 4514 | +11.29% | paired only | 4300 | 4186 |
| path | keygen_basemul_actual | 2 | 2641 | 2022 | -23.44% | paired only | 2491 | 1917 |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 6531 | -2.42% | -324 | 6787 | 6099 |
| path | keygen_poly_tobytes_key | 3 | 458 | 606 | +32.31% | +444 | 784 | 1321 |
| path | keygen_hash_f_pk | 1 | 11878 | 11856 | -0.19% | -22 | 39329 | 39329 |
| **path subtotal** | | | **39980** | **38234** | **-4.37%** | **-1746** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11879 | 11855 | -0.20% | -24 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2737 | 2738 | +0.04% | +1 | 8889 | 8889 |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | enc_poly_ntt_r | 1 | 3458 | 2596 | -24.93% | -862 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | enc_hash_g_polybytes | 1 | 13128 | 13110 | -0.14% | -18 | 43518 | 43518 |
| path | enc_poly_sotp_encode | 1 | 316 | 316 | +0.00% | +0 | 524 | 524 |
| path | enc_poly_ntt_m | 1 | 3441 | 2588 | -24.79% | -853 | 3263 | 3706 |
| path | enc_poly_frombytes_pk | 1 | 326 | 488 | +49.69% | +162 | 566 | 1103 |
| path | enc_basemul_add_actual | 1 | 2569 | 2404 | -6.42% | -165 | 2612 | 2230 |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | enc_basemul_add_plus_pack | 1 | 3033 | 3022 | -0.36% | -11 | 3392 | 3595 |
| **path subtotal** | | | **39073** | **37630** | **-3.69%** | **-1443** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 3 | 327 | 489 | +49.54% | +486 | 568 | 1105 |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | 2489 | 1917 |
| path | dec_first_invntt_actual | 1 | 3952 | 3556 | -10.02% | -396 | 3470 | 4821 |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5577 | -15.40% | -1015 | 5955 | 6734 |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | 400 | 400 |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2594 | -24.61% | -847 | 3263 | 3706 |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | 225 | 225 |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2487 | 2489 |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | dec_verify_product_to_bytes_actual | 1 | 3098 | 3301 | +6.55% | +203 | 3267 | 4259 |
| path | dec_hash_g_polybytes | 1 | 13131 | 13110 | -0.16% | -21 | 43518 | 43518 |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | 543 | 543 |
| path | dec_hash_h_msg | 1 | 2735 | 2738 | +0.11% | +3 | 8889 | 8889 |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2596 | -24.93% | -862 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 615 | +34.28% | +157 | 781 | 1366 |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | 532 | 532 |
| **path subtotal** | | | **35229** | **33315** | **-5.43%** | **-1914** | | |

## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 3 | 327 | 489 | +486 |
| KEYGEN | keygen_poly_tobytes_key | 3 | 458 | 606 | +444 |
| DECAP | dec_verify_product_to_bytes_actual | 1 | 3098 | 3301 | +203 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 488 | +162 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 616 | +158 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 615 | +157 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | 68b0bccd24c5 | 192506 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul | 20 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/32 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 16/16 |
| gt_production_default | kem_components | 7cf953bedb6e | 196946 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/32 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/44 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/0 |
|  |  |  |  | poly_basemul | 20 | 0/0 |
|  |  |  |  | poly_basemul_add | 20 | 16/16 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/16 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/16 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/0 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 16/48 |
| gt_production_default | kem_keygen | 87490a978a6e | 189233 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul | 20 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/32 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 16/16 |
| gt_production_default | kem_enc | 74d4398b5b9e | 189217 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul | 20 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/32 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 16/16 |
| gt_production_default | kem_dec | 355cf5510b41 | 189217 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul | 20 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/32 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 16/16 |
| kpqc_final | kernel_components | d12588b282cc | 44505 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | cbda1448824a | 48985 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | 3a5d11fdb0d3 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 21b84a3e902f | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | 6535705379dc | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
