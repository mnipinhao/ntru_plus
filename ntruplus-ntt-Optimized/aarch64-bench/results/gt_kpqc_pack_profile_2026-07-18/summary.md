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
| kem_keygen | 39950/39953/39954 | 38616/38621/38633 | -3.33% | 80801 | 82902 |
| kem_enc | 39010/39014/39018 | 37794/37798/37802 | -3.12% | 103980 | 106239 |
| kem_dec | 35191/35199/35204 | 33585/33587/33590 | -4.58% | 72677 | 77267 |

## Optional Candidate Variants

These variants were linked and measured in the same profile run but remain separate from the production default.

| Operation | Candidate | Candidate cycles | Delta vs GT production | Delta vs KPQC | Candidate instr |
|---|---|---:|---:|---:|---:|
| kem_keygen | gt_production_serialization_keygen_p1_u1 | 38613 | -8 (-0.02%) | -1340 (-3.35%) | 82758 |
| kem_enc | gt_production_serialization_keygen_p1_u1 | 37700 | -98 (-0.26%) | -1314 (-3.37%) | 106191 |
| kem_dec | gt_production_serialization_keygen_p1_u1 | 33488 | -99 (-0.29%) | -1711 (-4.86%) | 77123 |

## Primitive Kernels

These rows compare isolated public kernels. Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3607 | 2868 | -20.49% | 3265 | 3708 | 1.105 | 0.773 |
| TRANSFORM | inverse_ntt_generic | 3974 | 4083 | +2.74% | 3472 | 5093 | 1.145 | 0.802 |
| POINTWISE | basemul | 2672 | 2842 | +6.36% | 2493 | 2495 | 1.072 | 1.139 |
| POINTWISE | basemul_add | 2634 | 2923 | +10.97% | 2616 | 2810 | 1.007 | 1.040 |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | 4298 | 4432 | 0.944 | 1.125 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14163 | 12964 | -8.47% | 12477 | 14986 | 1.135 | 0.865 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17771 | 16380 | -7.83% | 15857 | 19001 | 1.121 | 0.862 |
| SERIALIZE | ntt_tobytes_internal_layout | 459 | 399 | -13.07% | 784 | 784 | 0.585 | 0.509 |
| SERIALIZE | ntt_frombytes_internal_layout | 328 | 302 | -7.93% | 568 | 568 | 0.577 | 0.532 |
| SERIALIZE | ntt_tobytes_canonical | 459 | 616 | +34.20% | 784 | 1369 | 0.585 | 0.450 |
| SERIALIZE | ntt_frombytes_canonical | 328 | 528 | +60.98% | 568 | 1153 | 0.577 | 0.458 |
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

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2721 | 2720 | -0.04% | -2 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 2703 | -25.78% | -939 | 3461 | 4194 |
| path | keygen_sample_ntt_g | 1 | 3637 | 2723 | -25.13% | -914 | 3456 | 4191 |
| path | keygen_baseinv_actual | 2 | 4056 | 4682 | +15.43% | paired only | 4300 | 4305 |
| path | keygen_basemul_actual | 2 | 2641 | 2020 | -23.51% | paired only | 2491 | 1917 |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 6701 | +0.12% | +16 | 6787 | 6218 |
| path | keygen_poly_tobytes_key | 3 | 458 | 616 | +34.50% | +474 | 784 | 1369 |
| path | keygen_hash_f_pk | 1 | 11882 | 11877 | -0.04% | -5 | 39329 | 39329 |
| **path subtotal** | | | **39977** | **38601** | **-3.44%** | **-1376** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11882 | 11877 | -0.04% | -5 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2743 | 2737 | -0.22% | -6 | 8889 | 8889 |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | enc_poly_ntt_r | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | enc_hash_g_polybytes | 1 | 13145 | 13124 | -0.16% | -21 | 43518 | 43518 |
| path | enc_poly_sotp_encode | 1 | 316 | 316 | +0.00% | +0 | 524 | 524 |
| path | enc_poly_ntt_m | 1 | 3441 | 2594 | -24.61% | -847 | 3263 | 3706 |
| path | enc_poly_frombytes_pk | 1 | 326 | 528 | +61.96% | +202 | 566 | 1151 |
| path | enc_basemul_add_actual | 1 | 2569 | 2404 | -6.42% | -165 | 2612 | 2230 |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | enc_basemul_add_plus_pack | 1 | 3033 | 3022 | -0.36% | -11 | 3392 | 3595 |
| **path subtotal** | | | **39099** | **37709** | **-3.56%** | **-1390** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 3 | 327 | 528 | +61.47% | +603 | 568 | 1153 |
| path | dec_first_basemul_actual | 1 | 2641 | 2022 | -23.44% | -619 | 2489 | 1917 |
| path | dec_first_invntt_actual | 1 | 3952 | 3557 | -9.99% | -395 | 3470 | 4821 |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5577 | -15.40% | -1015 | 5955 | 6734 |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | 400 | 400 |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2594 | -24.61% | -847 | 3263 | 3706 |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | 225 | 225 |
| path | dec_verify_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2487 | 2489 |
| path | dec_poly_tobytes_verify | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | dec_verify_basemul_plus_pack | 1 | 3098 | 3427 | +10.62% | +329 | 3267 | 3854 |
| path | dec_hash_g_polybytes | 1 | 13137 | 13134 | -0.02% | -3 | 43518 | 43518 |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | 543 | 543 |
| path | dec_hash_h_msg | 1 | 2743 | 2737 | -0.22% | -6 | 8889 | 8889 |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 613 | +33.84% | +155 | 781 | 1366 |
| path | dec_verify_polybytes | 1 | 149 | 150 | +0.67% | +1 | 532 | 532 |
| **path subtotal** | | | **35243** | **33582** | **-4.71%** | **-1661** | | |

## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 3 | 327 | 528 | +603 |
| KEYGEN | keygen_poly_tobytes_key | 3 | 458 | 616 | +474 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 528 | +202 |
| DECAP | dec_verify_basemul | 1 | 2641 | 2813 | +172 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 616 | +158 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_verify | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 613 | +155 |
| KEYGEN | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 6701 | +16 |
| DECAP | dec_verify_polybytes | 1 | 149 | 150 | +1 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | e73631f95c36 | 174898 | poly_tobytes_gt_canonical | 5428 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical | 4572 | 4/36 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/32 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/48 |
|  |  |  |  | poly_baseinv | 16 | 4/4 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
| gt_production_default | kem_components | 760243190023 | 179346 | poly_tobytes_gt_canonical | 5428 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical | 4572 | 4/36 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/32 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/48 |
|  |  |  |  | poly_baseinv | 16 | 4/4 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
| gt_production_default | kem_keygen | 509e58b7d9ec | 171657 | poly_tobytes_gt_canonical | 5428 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical | 4572 | 4/4 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/0 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/16 |
|  |  |  |  | poly_baseinv | 16 | 4/36 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/32 |
| gt_production_default | kem_enc | e6fc8fabb50f | 171641 | poly_tobytes_gt_canonical | 5428 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical | 4572 | 4/4 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/0 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/16 |
|  |  |  |  | poly_baseinv | 16 | 4/36 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/32 |
| gt_production_default | kem_dec | c96be8b7a1c3 | 171641 | poly_tobytes_gt_canonical | 5428 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical | 4572 | 4/4 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/0 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/16 |
|  |  |  |  | poly_baseinv | 16 | 4/36 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/32 |
| gt_production_serialization_keygen_p1_u1 | kernel_components | 16a912e4b296 | 179994 | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/0 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/16 |
|  |  |  |  | poly_baseinv | 16 | 4/36 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
| gt_production_serialization_keygen_p1_u1 | kem_components | d706d05f6da0 | 184442 | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/48 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/0 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/16 |
|  |  |  |  | poly_baseinv | 16 | 4/36 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
| gt_production_serialization_keygen_p1_u1 | kem_keygen | a9ea58ff0ecd | 176753 | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/32 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/48 |
|  |  |  |  | poly_baseinv | 16 | 4/4 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
| gt_production_serialization_keygen_p1_u1 | kem_enc | 94a50d7158ea | 176753 | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/32 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/48 |
|  |  |  |  | poly_baseinv | 16 | 4/4 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
| gt_production_serialization_keygen_p1_u1 | kem_dec | fc675460b518 | 176753 | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | poly_ntt_mul3 | 48 | 16/16 |
|  |  |  |  | poly_ntt_mul3_add1 | 52 | 16/48 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 0/32 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 16/48 |
|  |  |  |  | poly_baseinv | 16 | 4/4 |
|  |  |  |  | poly_baseinv_scaled_r | 4 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 20 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
| kpqc_final | kernel_components | 959bdd13fb45 | 44393 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | 2e6e9ec1f0cc | 48905 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | 184fe06a66ea | 41409 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 9ead21fa98ee | 41409 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | a0d057ff8979 | 41409 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
