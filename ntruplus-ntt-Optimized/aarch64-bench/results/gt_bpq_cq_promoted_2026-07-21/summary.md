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
| kem_keygen | 39946/39948/39951 | 36372/36373/36375 | -8.95% | n/a | n/a |
| kem_enc | 39007/39011/39015 | 37566/37574/37578 | -3.68% | n/a | n/a |
| kem_dec | 35180/35181/35185 | 32891/32904/32913 | -6.47% | n/a | n/a |

## Optional Candidate Variants

These variants were linked and measured in the same profile run but remain separate from the production default.

| Operation | Candidate | Candidate cycles | Delta vs GT production | Delta vs KPQC | Candidate instr |
|---|---|---:|---:|---:|---:|
| kem_keygen | gt_production_pre_bpq_cq | 38264 | +1891 (+5.20%) | -1684 (-4.22%) | n/a |
| kem_enc | gt_production_pre_bpq_cq | 37556 | -18 (-0.05%) | -1455 (-3.73%) | n/a |
| kem_dec | gt_production_pre_bpq_cq | 32876 | -28 (-0.09%) | -2305 (-6.55%) | n/a |

## Primitive Kernels

These rows compare isolated public kernels. Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3611 | 2873 | -20.44% | n/a | n/a | n/a | n/a |
| TRANSFORM | inverse_ntt_generic | 3978 | 4075 | +2.44% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul | 2671 | 2839 | +6.29% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul_add | 2634 | 2940 | +11.62% | n/a | n/a | n/a | n/a |
| POINTWISE | baseinv_generic | 4056 | 4986 | +22.93% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_2ntt_basemul_invntt | 14208 | 13027 | -8.31% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17806 | 16408 | -7.85% | n/a | n/a | n/a | n/a |
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
GT keygen stores the two specialized sample NTTs directly in BPQ layout, converts the operand being inverted to CQ during baseinv prepare, performs hierarchical K=8 batch inversion with `gt_fqinv15_asm`, and keeps the result in scaled-R CQ layout for the mixed BPQ x CQ basemul. Its baseinv and basemul rows must therefore be interpreted together, not as independent generic-API drop-in kernels.
The isolated `inverse_ntt_generic` primitive calls the public generic `poly_invntt`. The production decapsulation row `dec_first_invntt_actual` instead calls the paired `poly_invntt_from_rminus1` backend when the GT production flag is active.
The decapsulation verify path is compared as one logical `dec_verify_product_to_bytes_actual` row: GT calls the promoted F2 fused canonical backend, while KPQC performs canonical `hinv` unpack, normal basemul, and canonical pack. Both sides therefore start from serialized `hinv` bytes and end at serialized product bytes. The separate generic basemul and pack rows are diagnostics and are not included in the path subtotal.

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2719 | 2721 | +0.07% | +4 | n/a | n/a |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | keygen_sample_ntt_f | 1 | 3642 | 2645 | -27.38% | -997 | n/a | n/a |
| path | keygen_sample_ntt_g | 1 | 3637 | 2653 | -27.06% | -984 | n/a | n/a |
| path | keygen_baseinv_actual | 2 | 4056 | 4039 | -0.42% | paired only | n/a | n/a |
| path | keygen_basemul_actual | 2 | 2641 | 1663 | -37.03% | paired only | n/a | n/a |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 5705 | -14.76% | -1976 | n/a | n/a |
| path | keygen_poly_tobytes_public | 1 | 458 | 566 | +23.58% | +108 | n/a | n/a |
| path | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +32.10% | +147 | n/a | n/a |
| path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | +23.58% | +108 | n/a | n/a |
| path | keygen_hash_f_pk | 1 | 11858 | 11857 | -0.01% | -1 | n/a | n/a |
| **path subtotal** | | | **39949** | **36344** | **-9.02%** | **-3605** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11860 | 11857 | -0.03% | -3 | n/a | n/a |
| path | enc_hash_h_msg | 1 | 2739 | 2736 | -0.11% | -3 | n/a | n/a |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | enc_poly_ntt_r | 1 | 3458 | 2596 | -24.93% | -862 | n/a | n/a |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | enc_hash_g_polybytes | 1 | 13112 | 13110 | -0.02% | -2 | n/a | n/a |
| path | enc_poly_sotp_encode | 1 | 323 | 316 | -2.17% | -7 | n/a | n/a |
| path | enc_poly_ntt_m | 1 | 3441 | 2588 | -24.79% | -853 | n/a | n/a |
| path | enc_poly_frombytes_pk | 1 | 326 | 488 | +49.69% | +162 | n/a | n/a |
| path | enc_basemul_add_actual | 1 | 2569 | 2286 | -11.02% | -283 | n/a | n/a |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| combined | enc_basemul_add_plus_pack | 1 | 3027 | 2900 | -4.20% | -127 | n/a | n/a |
| **path subtotal** | | | **39047** | **37512** | **-3.93%** | **-1535** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 2 | 327 | 489 | +49.54% | +324 | n/a | n/a |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | n/a | n/a |
| path | dec_first_invntt_actual | 1 | 3952 | 3558 | -9.97% | -394 | n/a | n/a |
| combined | dec_first_basemul_plus_invntt | 1 | 6594 | 5577 | -15.42% | -1017 | n/a | n/a |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | n/a | n/a |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2588 | -24.79% | -853 | n/a | n/a |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | n/a | n/a |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | n/a | n/a |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3301 | -3.62% | -124 | n/a | n/a |
| path | dec_hash_g_polybytes | 1 | 13112 | 13112 | +0.00% | +0 | n/a | n/a |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | n/a | n/a |
| path | dec_hash_h_msg | 1 | 2736 | 2736 | +0.00% | +0 | n/a | n/a |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2596 | -24.93% | -862 | n/a | n/a |
| path | dec_poly_tobytes_r1 | 1 | 458 | 615 | +34.28% | +157 | n/a | n/a |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | n/a | n/a |
| **path subtotal** | | | **35211** | **32822** | **-6.78%** | **-2389** | | |

## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 2 | 327 | 489 | +324 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 488 | +162 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 616 | +158 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 615 | +157 |
| KEYGEN | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +147 |
| KEYGEN | keygen_poly_tobytes_public | 1 | 458 | 566 | +108 |
| KEYGEN | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | +108 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | 81f2b87b97b0 | 211330 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
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
| gt_production_default | kem_components | 9f880e121337 | 216210 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/32 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
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
| gt_production_default | kem_keygen | 2aea811bd842 | 208057 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
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
| gt_production_default | kem_enc | e7f959c7b076 | 208041 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
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
| gt_production_default | kem_dec | 5267cab11bc0 | 208041 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
|  |  |  |  | poly_basemul_decap_verify_canonical_f2_pair_pipeline | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
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
| gt_production_pre_bpq_cq | kernel_components | ffd4f09e18d7 | 192906 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
| gt_production_pre_bpq_cq | kem_components | ad512e389371 | 197770 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/32 |
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
| gt_production_pre_bpq_cq | kem_keygen | d30fc74d5a08 | 189617 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
| gt_production_pre_bpq_cq | kem_enc | ae03f5d9702d | 189617 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
| gt_production_pre_bpq_cq | kem_dec | d69c100975bb | 189617 | gt_decap_verify_canonical_f2_pair_pipeline_candidate | 92 | 0/0 |
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
| kpqc_final | kernel_components | e6eb9654a60e | 44505 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | 2a2fbb5be1ac | 49441 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_keygen | 9477e724c63f | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | b5d31d5999ee | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | bbfb1d25a5c6 | 41457 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
