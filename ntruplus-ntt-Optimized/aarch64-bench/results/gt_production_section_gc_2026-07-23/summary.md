# GT Production vs KPQC Final Detailed Profile

Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.
Each row is p50 of 31 samples x 2000 calls; warmup=100.
Variants use their current Makefile section-GC policy.
All binaries run deterministic KEM setup and correctness checks before PMU; the component mode also runs a reconstructed-ciphertext decapsulation postflight. Full KEM totals are decisive; component subtotals omit copies/call overhead and are used for hotspot attribution only.
Cycles and retired instructions are collected in separate counter builds/runs. Derived CPI is therefore diagnostic rather than a same-group atomic PMU sample.

## Measurement Environment

- Git HEAD: `unavailable (rsync mirror)` (not a Git worktree)
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- Host: `Linux pinhao 6.18.33+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.18.33-1+rpt1 (2026-06-01) aarch64 GNU/Linux`

## Full KEM

| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39991/39995/40001 | 37716/37721/37727 | -5.69% | 80799 | 86069 |
| kem_enc | 39070/39075/39079 | 37599/37604/37610 | -3.76% | 103978 | 106173 |
| kem_dec | 35192/35193/35200 | 32847/32848/32851 | -6.66% | 72675 | 76465 |


## Generic/Public Primitive Diagnostics

These rows compare isolated public/generic kernels. They are API and algorithm diagnostics, not a list of the specialized kernels selected by the production KEM. In particular, `inverse_ntt_generic`, `basemul`, `basemul_add`, and `baseinv_generic` must not be substituted for the `*_actual` KEM-path rows below.
Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3606 | 2861 | -20.66% | 3265 | 3708 | 1.104 | 0.772 |
| TRANSFORM | inverse_ntt_generic | 3969 | 4087 | +2.97% | 3472 | 5093 | 1.143 | 0.802 |
| POINTWISE | basemul | 2669 | 2856 | +7.01% | 2493 | 2495 | 1.071 | 1.145 |
| POINTWISE | basemul_add | 2636 | 2938 | +11.46% | 2616 | 2810 | 1.008 | 1.046 |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | 4298 | 4427 | 0.944 | 1.126 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14196 | 13000 | -8.42% | 12477 | 14986 | 1.138 | 0.867 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17815 | 16141 | -9.40% | 15857 | 19001 | 1.123 | 0.849 |
| SERIALIZE | ntt_tobytes_internal_layout | 459 | 399 | -13.07% | 784 | 782 | 0.585 | 0.510 |
| SERIALIZE | ntt_frombytes_internal_layout | 328 | 310 | -5.49% | 568 | 566 | 0.577 | 0.548 |
| SERIALIZE | ntt_tobytes_canonical | 459 | 613 | +33.55% | 784 | 1367 | 0.585 | 0.448 |
| SERIALIZE | ntt_frombytes_canonical | 328 | 487 | +48.48% | 568 | 1103 | 0.577 | 0.442 |
| SUPPORT | cbd1 | 305 | 302 | -0.98% | 500 | 501 | 0.610 | 0.603 |
| SUPPORT | triple | 196 | 192 | -2.04% | 199 | 197 | 0.985 | 0.975 |
| SUPPORT | crepmod3 | 400 | 384 | -4.00% | 398 | 398 | 1.005 | 0.965 |
| SUPPORT | poly_sub | 173 | 172 | -0.58% | 225 | 222 | 0.769 | 0.775 |
| SUPPORT | sotp_encode | 322 | 315 | -2.17% | 521 | 521 | 0.618 | 0.605 |
| SUPPORT | sotp_decode | 310 | 310 | +0.00% | 542 | 540 | 0.572 | 0.574 |

## Actual Production KEM-Path Components

These rows follow the same production macros as the full-KEM binaries. The GT configuration in this report selects the production Good-Thomas forward NTT, the keygen-only BPQ/CQ backend with hierarchical K=8/fqinv15 inversion, direct-Q31 encapsulation, the rminus1 basemul/InvNTT decapsulation pair, and the canonical pointwise verify backend. Default-off experiments such as the compact serialization candidate are not included until promoted.
`path` rows are non-overlapping call-graph components. `combined` rows are boundary diagnostics and are excluded from weighted subtotals.
These rows use fixed, deterministic buffers reconstructed from a valid KEM key/ciphertext and satisfy each GT representation/range contract.
GT keygen explicitly forms 3F+1/3G, calls the shared production poly_ntt, then converts the generic GT block-major result to BPQ. It converts the operand being inverted to CQ during baseinv prepare, performs hierarchical K=8 batch inversion with `gt_fqinv15_asm`, and keeps the result in scaled-R CQ layout for the mixed BPQ x CQ basemul. Its baseinv and basemul rows must therefore be interpreted together, not as independent generic-API drop-in kernels.
The isolated `inverse_ntt_generic` primitive calls the public generic `poly_invntt`. The production decapsulation row `dec_first_invntt_actual` instead calls the paired `poly_invntt_from_rminus1` backend when the GT production flag is active.
The decapsulation verify path is compared as one logical `dec_verify_product_to_bytes_actual` row: GT calls the production fused canonical backend, while KPQC performs canonical `hinv` unpack, normal basemul, and canonical pack. Both sides therefore start from serialized `hinv` bytes and end at serialized product bytes. The separate generic basemul and pack rows are diagnostics and are not included in the path subtotal.

### Keygen

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | keygen_shake256_sample | 2 | 2714 | 2721 | +0.26% | +14 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 303 | 302 | -0.33% | -2 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 3301 | -9.36% | -341 | 3461 | 5570 |
| path | keygen_sample_ntt_g | 1 | 3637 | 3308 | -9.05% | -329 | 3456 | 5567 |
| path | keygen_baseinv_actual | 2 | 4056 | 4039 | -0.42% | paired only | 4300 | 4310 |
| path | keygen_basemul_actual | 2 | 2641 | 1661 | -37.11% | paired only | 2491 | 2318 |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 5698 | -14.87% | -1990 | 6787 | 6625 |
| path | keygen_poly_tobytes_public | 1 | 458 | 566 | +23.58% | +108 | 784 | 1200 |
| path | keygen_poly_tobytes_secret_f | 1 | 458 | 619 | +35.15% | +161 | 784 | 1319 |
| path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | +23.58% | +108 | 784 | 1200 |
| path | keygen_hash_f_pk | 1 | 11883 | 11882 | -0.01% | -1 | 39329 | 39329 |
| **path subtotal** | | | **39964** | **37688** | **-5.70%** | **-2276** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11878 | 11883 | +0.04% | +5 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2741 | 2738 | -0.11% | -3 | 8889 | 8887 |
| path | enc_poly_cbd1_r | 1 | 303 | 302 | -0.33% | -1 | 503 | 501 |
| path | enc_poly_ntt_r | 1 | 3458 | 2587 | -25.19% | -871 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 613 | +33.84% | +155 | 784 | 1367 |
| path | enc_hash_g_polybytes | 1 | 13133 | 13125 | -0.06% | -8 | 43518 | 43516 |
| path | enc_poly_sotp_encode | 1 | 323 | 315 | -2.48% | -8 | 524 | 521 |
| path | enc_poly_ntt_m | 1 | 3441 | 2587 | -24.82% | -854 | 3263 | 3704 |
| path | enc_poly_frombytes_pk | 1 | 326 | 487 | +49.39% | +161 | 566 | 1103 |
| path | enc_basemul_add_actual | 1 | 2569 | 2285 | -11.05% | -284 | 2612 | 2214 |
| path | enc_poly_tobytes_ct | 1 | 458 | 613 | +33.84% | +155 | 784 | 1367 |
| combined | enc_basemul_add_plus_pack | 1 | 3027 | 2902 | -4.13% | -125 | 3392 | 3578 |
| **path subtotal** | | | **39088** | **37535** | **-3.97%** | **-1553** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 2 | 327 | 489 | +49.54% | +324 | 568 | 1103 |
| path | dec_first_basemul_actual | 1 | 2641 | 1912 | -27.60% | -729 | 2489 | 1900 |
| path | dec_first_invntt_actual | 1 | 3952 | 3557 | -9.99% | -395 | 3470 | 4819 |
| combined | dec_first_basemul_plus_invntt | 1 | 6594 | 5467 | -17.09% | -1127 | 5955 | 6716 |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | 400 | 398 |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2587 | -24.82% | -854 | 3263 | 3704 |
| path | dec_poly_sub | 1 | 173 | 172 | -0.58% | -1 | 225 | 222 |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2487 | 2490 |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 613 | +33.84% | +155 | 784 | 1367 |
| path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3394 | -0.91% | -31 | 3831 | 4306 |
| path | dec_hash_g_polybytes | 1 | 13138 | 13126 | -0.09% | -12 | 43518 | 43516 |
| path | dec_poly_sotp_decode | 1 | 308 | 310 | +0.65% | +2 | 543 | 540 |
| path | dec_hash_h_msg | 1 | 2749 | 2737 | -0.44% | -12 | 8889 | 8887 |
| path | dec_poly_cbd1_r1 | 1 | 303 | 302 | -0.33% | -1 | 503 | 501 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2587 | -25.19% | -871 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 613 | +33.84% | +155 | 781 | 1367 |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | 532 | 533 |
| **path subtotal** | | | **35250** | **32809** | **-6.92%** | **-2441** | | |


## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 2 | 327 | 489 | +324 |
| KEYGEN | keygen_poly_tobytes_secret_f | 1 | 458 | 619 | +161 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 487 | +161 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 613 | +155 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 613 | +155 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 613 | +155 |
| KEYGEN | keygen_poly_tobytes_public | 1 | 458 | 566 | +108 |
| KEYGEN | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | +108 |
| DECAP | dec_poly_sotp_decode | 1 | 308 | 310 | +2 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | d3bc1bf0f488 | 133726 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/16 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/0 |
|  |  |  |  | poly_basemul | 704 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
|  |  |  |  | poly_baseinv | 12 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
| gt_production_default | kem_components | 25721de7e0df | 134486 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/16 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/0 |
|  |  |  |  | poly_basemul | 704 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
|  |  |  |  | poly_baseinv | 12 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
| gt_production_default | kem_keygen | 918c322e0556 | 81178 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/16 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/0 |
|  |  |  |  | poly_basemul | 704 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| gt_production_default | kem_enc | a2208b5e38f5 | 81162 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/16 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/0 |
|  |  |  |  | poly_basemul | 704 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| gt_production_default | kem_dec | d3067a682636 | 81162 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/16 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/0 |
|  |  |  |  | poly_basemul | 704 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| kpqc_final | kernel_components | 0f3f4d6656fe | 45177 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | 0816c7d319ae | 50113 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_keygen | 4175bc38c18c | 37342 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | da4b95f2cdf7 | 37342 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | 8ed9a885b070 | 37342 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
