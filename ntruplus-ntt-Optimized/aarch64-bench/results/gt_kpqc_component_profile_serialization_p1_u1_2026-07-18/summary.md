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
| kem_keygen | 39941/39942/39943 | 38618/38623/38630 | -3.30% | 80801 | 82902 |
| kem_enc | 39014/39018/39023 | 37753/37759/37773 | -3.23% | 103980 | 106239 |
| kem_dec | 35179/35181/35182 | 33574/33576/33580 | -4.56% | 72677 | 77267 |

## Primitive Kernels

These rows compare isolated public kernels. Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3617 | 2871 | -20.62% | 3265 | 3708 | 1.108 | 0.774 |
| TRANSFORM | inverse_ntt_generic | 3975 | 4081 | +2.67% | 3472 | 5093 | 1.145 | 0.801 |
| POINTWISE | basemul | 2673 | 2838 | +6.17% | 2493 | 2495 | 1.072 | 1.137 |
| POINTWISE | basemul_add | 2633 | 2941 | +11.70% | 2616 | 2810 | 1.006 | 1.047 |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | 4298 | 4432 | 0.944 | 1.125 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14184 | 12947 | -8.72% | 12477 | 14986 | 1.137 | 0.864 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17770 | 16444 | -7.46% | 15857 | 19001 | 1.121 | 0.865 |
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

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2721 | 2721 | +0.00% | +0 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 2704 | -25.76% | -938 | 3461 | 4194 |
| path | keygen_sample_ntt_g | 1 | 3637 | 2730 | -24.94% | -907 | 3456 | 4191 |
| path | keygen_baseinv_actual | 2 | 4056 | 4682 | +15.43% | +1252 | 4300 | 4305 |
| path | keygen_basemul_actual | 2 | 2641 | 2020 | -23.51% | -1242 | 2491 | 1917 |
| path | keygen_poly_tobytes_key | 3 | 458 | 616 | +34.50% | +474 | 784 | 1369 |
| path | keygen_hash_f_pk | 1 | 11882 | 11896 | +0.12% | +14 | 39329 | 39329 |
| **path subtotal** | | | **39977** | **38630** | **-3.37%** | **-1347** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11881 | 11895 | +0.12% | +14 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2743 | 2763 | +0.73% | +20 | 8889 | 8889 |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | enc_poly_ntt_r | 1 | 3458 | 2587 | -25.19% | -871 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | enc_hash_g_polybytes | 1 | 13130 | 13152 | +0.17% | +22 | 43518 | 43518 |
| path | enc_poly_sotp_encode | 1 | 316 | 316 | +0.00% | +0 | 524 | 524 |
| path | enc_poly_ntt_m | 1 | 3441 | 2588 | -24.79% | -853 | 3263 | 3706 |
| path | enc_poly_frombytes_pk | 1 | 326 | 527 | +61.66% | +201 | 566 | 1151 |
| path | enc_basemul_add_actual | 1 | 2569 | 2404 | -6.42% | -165 | 2612 | 2230 |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | enc_basemul_add_plus_pack | 1 | 3033 | 3022 | -0.36% | -11 | 3392 | 3595 |
| **path subtotal** | | | **39083** | **37767** | **-3.37%** | **-1316** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 3 | 327 | 528 | +61.47% | +603 | 568 | 1153 |
| path | dec_first_basemul_actual | 1 | 2641 | 2022 | -23.44% | -619 | 2489 | 1917 |
| path | dec_first_invntt_actual | 1 | 3952 | 3555 | -10.05% | -397 | 3470 | 4821 |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5577 | -15.40% | -1015 | 5955 | 6734 |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | 400 | 400 |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2588 | -24.79% | -853 | 3263 | 3706 |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | 225 | 225 |
| path | dec_verify_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2487 | 2489 |
| path | dec_poly_tobytes_verify | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | dec_verify_basemul_plus_pack | 1 | 3098 | 3427 | +10.62% | +329 | 3267 | 3854 |
| path | dec_hash_g_polybytes | 1 | 13139 | 13143 | +0.03% | +4 | 43518 | 43518 |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | 543 | 543 |
| path | dec_hash_h_msg | 1 | 2742 | 2763 | +0.77% | +21 | 8889 | 8889 |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2587 | -25.19% | -871 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 613 | +33.84% | +155 | 781 | 1366 |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | 532 | 532 |
| **path subtotal** | | | **35245** | **33602** | **-4.66%** | **-1643** | | |

## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| KEYGEN | keygen_baseinv_actual | 2 | 4056 | 4682 | +1252 |
| DECAP | dec_poly_frombytes | 3 | 327 | 528 | +603 |
| KEYGEN | keygen_poly_tobytes_key | 3 | 458 | 616 | +474 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 527 | +201 |
| DECAP | dec_verify_basemul | 1 | 2641 | 2813 | +172 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 616 | +158 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_verify | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 613 | +155 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | f94af79c035d | 174898 | poly_tobytes_gt_canonical | 5428 | 16/48 |
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
| gt_production_default | kem_components | b14e14d4289d | 179090 | poly_tobytes_gt_canonical | 5428 | 16/48 |
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
| gt_production_default | kem_keygen | d36979283724 | 171657 | poly_tobytes_gt_canonical | 5428 | 16/16 |
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
| gt_production_default | kem_enc | 8b807ae8fef7 | 171641 | poly_tobytes_gt_canonical | 5428 | 16/16 |
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
| gt_production_default | kem_dec | 98f25b5db080 | 171641 | poly_tobytes_gt_canonical | 5428 | 16/16 |
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
| gt_production_serialization_p1_u1 | kernel_components | 1dc6ee62c18e | 184522 | poly_tobytes_gt_canonical | 5428 | 16/48 |
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
| gt_production_serialization_p1_u1 | kem_components | 06504c9955d2 | 188714 | poly_tobytes_gt_canonical | 5428 | 16/48 |
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
| gt_production_serialization_p1_u1 | kem_keygen | 39562e4edba7 | 181281 | poly_tobytes_gt_canonical | 5428 | 16/16 |
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
| gt_production_serialization_p1_u1 | kem_enc | fc3e25a3a00d | 181281 | poly_tobytes_gt_canonical | 5428 | 16/16 |
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
| gt_production_serialization_p1_u1 | kem_dec | 8c35be7bf2c5 | 181281 | poly_tobytes_gt_canonical | 5428 | 16/16 |
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
| kpqc_final | kernel_components | 49739effa20b | 44393 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | a001120536ff | 48633 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | 5d00196db236 | 41409 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 2fd7d86599c8 | 41409 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | cb78f391ce95 | 41409 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
