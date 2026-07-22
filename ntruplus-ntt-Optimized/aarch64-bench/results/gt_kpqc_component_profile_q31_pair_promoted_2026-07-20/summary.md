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
| kem_keygen | 39943/39953/39956 | 38288/38290/38294 | -4.16% | n/a | n/a |
| kem_enc | 39072/39076/39082 | 37552/37561/37568 | -3.88% | n/a | n/a |
| kem_dec | 35151/35153/35156 | 32875/32884/32893 | -6.45% | n/a | n/a |


## Primitive Kernels

These rows compare isolated public kernels. Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3610 | 2885 | -20.08% | n/a | n/a | n/a | n/a |
| TRANSFORM | inverse_ntt_generic | 3980 | 4079 | +2.49% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul | 2673 | 2840 | +6.25% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul_add | 2629 | 2932 | +11.53% | n/a | n/a | n/a | n/a |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_2ntt_basemul_invntt | 14196 | 12922 | -8.97% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17808 | 16362 | -8.12% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_tobytes_internal_layout | 459 | 399 | -13.07% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_frombytes_internal_layout | 328 | 302 | -7.93% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_tobytes_canonical | 459 | 616 | +34.20% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_frombytes_canonical | 328 | 489 | +49.09% | n/a | n/a | n/a | n/a |
| SUPPORT | cbd1 | 305 | 305 | +0.00% | n/a | n/a | n/a | n/a |
| SUPPORT | triple | 196 | 192 | -2.04% | n/a | n/a | n/a | n/a |
| SUPPORT | crepmod3 | 400 | 384 | -4.00% | n/a | n/a | n/a | n/a |
| SUPPORT | poly_sub | 173 | 173 | +0.00% | n/a | n/a | n/a | n/a |
| SUPPORT | sotp_encode | 322 | 322 | +0.00% | n/a | n/a | n/a | n/a |
| SUPPORT | sotp_decode | 310 | 310 | +0.00% | n/a | n/a | n/a | n/a |

## Actual KEM-Path Components

`path` rows are non-overlapping call-graph components. `combined` rows are boundary diagnostics and are excluded from weighted subtotals.
These rows use fixed, deterministic buffers reconstructed from a valid KEM key/ciphertext and satisfy each GT representation/range contract.
GT keygen uses the scaled-factor chain `poly_baseinv_scaled_r` -> hierarchical K=8 batch inversion -> `gt_fqinv15_asm` -> Neon finish, followed by `poly_basemul_scaled_r_input`. Its baseinv and basemul rows must therefore be interpreted together, not as independent normal-factor drop-in kernels.
The decapsulation verify path is compared as one logical `dec_verify_product_to_bytes_actual` row: GT calls the promoted F2 fused canonical backend, while KPQC calls its normal basemul followed by pack. The separate generic basemul and pack rows are diagnostics and are not included in the path subtotal.

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2723 | 2715 | -0.29% | -16 | n/a | n/a |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | keygen_sample_ntt_f | 1 | 3642 | 2704 | -25.76% | -938 | n/a | n/a |
| path | keygen_sample_ntt_g | 1 | 3638 | 2715 | -25.37% | -923 | n/a | n/a |
| path | keygen_baseinv_actual | 2 | 4056 | 4514 | +11.29% | paired only | n/a | n/a |
| path | keygen_basemul_actual | 2 | 2641 | 2022 | -23.44% | paired only | n/a | n/a |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6694 | 6532 | -2.42% | -324 | n/a | n/a |
| path | keygen_poly_tobytes_key | 3 | 458 | 606 | +32.31% | +444 | n/a | n/a |
| path | keygen_hash_f_pk | 1 | 11882 | 11870 | -0.10% | -12 | n/a | n/a |
| **path subtotal** | | | **39982** | **38215** | **-4.42%** | **-1767** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11885 | 11872 | -0.11% | -13 | n/a | n/a |
| path | enc_hash_h_msg | 1 | 2743 | 2744 | +0.04% | +1 | n/a | n/a |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | enc_poly_ntt_r | 1 | 3458 | 2589 | -25.13% | -869 | n/a | n/a |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | enc_hash_g_polybytes | 1 | 13139 | 13128 | -0.08% | -11 | n/a | n/a |
| path | enc_poly_sotp_encode | 1 | 316 | 316 | +0.00% | +0 | n/a | n/a |
| path | enc_poly_ntt_m | 1 | 3441 | 2594 | -24.61% | -847 | n/a | n/a |
| path | enc_poly_frombytes_pk | 1 | 326 | 488 | +49.69% | +162 | n/a | n/a |
| path | enc_basemul_add_actual | 1 | 2569 | 2286 | -11.02% | -283 | n/a | n/a |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| combined | enc_basemul_add_plus_pack | 1 | 3033 | 2900 | -4.39% | -133 | n/a | n/a |
| **path subtotal** | | | **39096** | **37552** | **-3.95%** | **-1544** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 3 | 327 | 489 | +49.54% | +486 | n/a | n/a |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | n/a | n/a |
| path | dec_first_invntt_actual | 1 | 3952 | 3557 | -9.99% | -395 | n/a | n/a |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5577 | -15.40% | -1015 | n/a | n/a |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | n/a | n/a |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2594 | -24.61% | -847 | n/a | n/a |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | n/a | n/a |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | n/a | n/a |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | dec_verify_product_to_bytes_actual | 1 | 3098 | 3301 | +6.55% | +203 | n/a | n/a |
| path | dec_hash_g_polybytes | 1 | 13139 | 13130 | -0.07% | -9 | n/a | n/a |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | n/a | n/a |
| path | dec_hash_h_msg | 1 | 2743 | 2742 | -0.04% | -1 | n/a | n/a |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2589 | -25.13% | -869 | n/a | n/a |
| path | dec_poly_tobytes_r1 | 1 | 458 | 615 | +34.28% | +157 | n/a | n/a |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | n/a | n/a |
| **path subtotal** | | | **35245** | **33333** | **-5.42%** | **-1912** | | |

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
| gt_production_default | kernel_components | c8a3167eae28 | 192890 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| gt_production_default | kem_components | 641776f026bd | 197330 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/32 |
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
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| gt_production_default | kem_keygen | 7776297f95a0 | 189617 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| gt_production_default | kem_enc | dbe482b8e3c3 | 189601 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| gt_production_default | kem_dec | 0065f22e6d22 | 189601 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| kpqc_final | kernel_components | dfd44d160242 | 44505 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | 1107259603e9 | 48985 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | 30a59a66ffe7 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 8e2226653970 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | f241b1656ae1 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
