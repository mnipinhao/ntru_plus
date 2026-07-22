# GT Production vs KPQC Final Detailed Profile

Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.
Each row is p50 of 31 samples x 1000 calls; warmup=100.
Both binaries run deterministic KEM setup and correctness checks before PMU; the component mode also runs a reconstructed-ciphertext decapsulation postflight. Full KEM totals are decisive; component subtotals omit copies/call overhead and are used for hotspot attribution only.
Cycles and retired instructions are collected in separate counter builds/runs. Derived CPI is therefore diagnostic rather than a same-group atomic PMU sample.

## Measurement Environment

- Git HEAD: `unavailable (rsync mirror)` (not a Git worktree)
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- Host: `Linux pinhao 6.18.33+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.18.33-1+rpt1 (2026-06-01) aarch64 GNU/Linux`

## Full KEM

| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39949/39951/39952 | 38278/38281/38292 | -4.18% | n/a | n/a |
| kem_enc | 39074/39078/39084 | 37708/37714/37721 | -3.49% | n/a | n/a |
| kem_dec | 35159/35163/35166 | 33447/33453/33459 | -4.86% | n/a | n/a |

## Optional Candidate Variants

These variants were linked and measured in the same profile run but remain separate from the production default.

| Operation | Candidate | Candidate cycles | Delta vs GT production | Delta vs KPQC | Candidate instr |
|---|---|---:|---:|---:|---:|
| kem_keygen | gt_production_paper_hier_k8 | 38279 | -2 (-0.01%) | -1672 (-4.19%) | n/a |
| kem_enc | gt_production_paper_hier_k8 | 37697 | -17 (-0.05%) | -1381 (-3.53%) | n/a |
| kem_dec | gt_production_paper_hier_k8 | 33458 | +5 (+0.01%) | -1705 (-4.85%) | n/a |

## Primitive Kernels

These rows compare isolated public kernels. Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3528 | 2730 | -22.62% | n/a | n/a | n/a | n/a |
| TRANSFORM | inverse_ntt_generic | 3964 | 4062 | +2.47% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul | 2645 | 2823 | +6.73% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul_add | 2619 | 2902 | +10.81% | n/a | n/a | n/a | n/a |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_2ntt_basemul_invntt | 14016 | 12908 | -7.91% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17646 | 16369 | -7.24% | n/a | n/a | n/a | n/a |
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

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2721 | 2722 | +0.04% | +2 | n/a | n/a |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | keygen_sample_ntt_f | 1 | 3642 | 2709 | -25.62% | -933 | n/a | n/a |
| path | keygen_sample_ntt_g | 1 | 3639 | 2716 | -25.36% | -923 | n/a | n/a |
| path | keygen_baseinv_actual | 2 | 4056 | 4515 | +11.32% | paired only | n/a | n/a |
| path | keygen_basemul_actual | 2 | 2641 | 2022 | -23.44% | paired only | n/a | n/a |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6694 | 6534 | -2.39% | -320 | n/a | n/a |
| path | keygen_poly_tobytes_key | 3 | 458 | 606 | +32.31% | +444 | n/a | n/a |
| path | keygen_hash_f_pk | 1 | 11855 | 11883 | +0.24% | +28 | n/a | n/a |
| **path subtotal** | | | **39952** | **38250** | **-4.26%** | **-1702** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11857 | 11884 | +0.23% | +27 | n/a | n/a |
| path | enc_hash_h_msg | 1 | 2736 | 2738 | +0.07% | +2 | n/a | n/a |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | enc_poly_ntt_r | 1 | 3458 | 2589 | -25.13% | -869 | n/a | n/a |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | enc_hash_g_polybytes | 1 | 13103 | 13142 | +0.30% | +39 | n/a | n/a |
| path | enc_poly_sotp_encode | 1 | 316 | 316 | +0.00% | +0 | n/a | n/a |
| path | enc_poly_ntt_m | 1 | 3441 | 2588 | -24.79% | -853 | n/a | n/a |
| path | enc_poly_frombytes_pk | 1 | 326 | 488 | +49.69% | +162 | n/a | n/a |
| path | enc_basemul_add_actual | 1 | 2569 | 2404 | -6.42% | -165 | n/a | n/a |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| combined | enc_basemul_add_plus_pack | 1 | 3033 | 3022 | -0.36% | -11 | n/a | n/a |
| **path subtotal** | | | **39025** | **37684** | **-3.44%** | **-1341** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 3 | 327 | 489 | +49.54% | +486 | n/a | n/a |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | n/a | n/a |
| path | dec_first_invntt_actual | 1 | 3952 | 3556 | -10.02% | -396 | n/a | n/a |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5577 | -15.40% | -1015 | n/a | n/a |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | n/a | n/a |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2588 | -24.79% | -853 | n/a | n/a |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | n/a | n/a |
| path | dec_verify_basemul | 1 | 2641 | 2813 | +6.51% | +172 | n/a | n/a |
| path | dec_poly_tobytes_verify | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| combined | dec_verify_basemul_plus_pack | 1 | 3098 | 3427 | +10.62% | +329 | n/a | n/a |
| path | dec_hash_g_polybytes | 1 | 13102 | 13131 | +0.22% | +29 | n/a | n/a |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | n/a | n/a |
| path | dec_hash_h_msg | 1 | 2736 | 2743 | +0.26% | +7 | n/a | n/a |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2589 | -25.13% | -869 | n/a | n/a |
| path | dec_poly_tobytes_r1 | 1 | 458 | 615 | +34.28% | +157 | n/a | n/a |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | n/a | n/a |
| **path subtotal** | | | **35202** | **33456** | **-4.96%** | **-1746** | | |

## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 3 | 327 | 489 | +486 |
| KEYGEN | keygen_poly_tobytes_key | 3 | 458 | 606 | +444 |
| DECAP | dec_verify_basemul | 1 | 2641 | 2813 | +172 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 488 | +162 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 616 | +158 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_verify | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 615 | +157 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | 659f0eea32dc | 180418 | poly_tobytes_gt_canonical | 5440 | 16/16 |
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
| gt_production_default | kem_components | a664d14e2fe8 | 184834 | poly_tobytes_gt_canonical | 5440 | 16/48 |
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
| gt_production_default | kem_keygen | d5789b16be1c | 177177 | poly_tobytes_gt_canonical | 5440 | 16/48 |
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
| gt_production_default | kem_enc | 406e07059963 | 177161 | poly_tobytes_gt_canonical | 5440 | 16/48 |
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
| gt_production_default | kem_dec | 94057ce33a2b | 177161 | poly_tobytes_gt_canonical | 5440 | 16/48 |
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
| gt_production_paper_hier_k8 | kernel_components | 1a9144bb88ee | 181226 | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 4/4 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 16/16 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/32 |
| gt_production_paper_hier_k8 | kem_components | fea18cfc9408 | 185642 | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 4/36 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 16/48 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
| gt_production_paper_hier_k8 | kem_keygen | e42077cd79b4 | 177969 | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 4/36 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 16/48 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
| gt_production_paper_hier_k8 | kem_enc | 7e491f5d12db | 177969 | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 4/36 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 16/48 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
| gt_production_paper_hier_k8 | kem_dec | 7f9120a55ee1 | 177969 | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 4/36 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 16/48 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
| kpqc_final | kernel_components | 10b48960a969 | 44505 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | 85d06208fe50 | 48953 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | bd2eefc35eb5 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | cf039e2ea4f4 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | 2c24c06704c1 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
