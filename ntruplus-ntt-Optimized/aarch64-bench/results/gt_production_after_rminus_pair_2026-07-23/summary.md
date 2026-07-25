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
| kem_keygen | 39939/39954/39958 | 37676/37680/37685 | -5.69% | 80799 | 86067 |
| kem_enc | 39068/39071/39073 | 37596/37606/37610 | -3.75% | 103978 | 106175 |
| kem_dec | 35193/35199/35200 | 32863/32864/32866 | -6.63% | 72675 | 76465 |


## Generic/Public Primitive Diagnostics

These rows compare isolated public/generic kernels. They are API and algorithm diagnostics, not a list of the specialized kernels selected by the production KEM. In particular, `inverse_ntt_generic`, `basemul`, `basemul_add`, and `baseinv_generic` must not be substituted for the `*_actual` KEM-path rows below.
Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3611 | 2862 | -20.74% | 3265 | 3708 | 1.106 | 0.772 |
| TRANSFORM | inverse_ntt_generic | 3971 | 4079 | +2.72% | 3472 | 5093 | 1.144 | 0.801 |
| POINTWISE | basemul | 2670 | 2839 | +6.33% | 2493 | 2495 | 1.071 | 1.138 |
| POINTWISE | basemul_add | 2629 | 2923 | +11.18% | 2616 | 2810 | 1.005 | 1.040 |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | 4298 | 4432 | 0.944 | 1.125 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14204 | 12940 | -8.90% | 12477 | 14986 | 1.138 | 0.863 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17836 | 16419 | -7.94% | 15857 | 19001 | 1.125 | 0.864 |
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
| path | keygen_shake256_sample | 2 | 2714 | 2720 | +0.22% | +12 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 3300 | -9.39% | -342 | 3461 | 5572 |
| path | keygen_sample_ntt_g | 1 | 3637 | 3306 | -9.10% | -331 | 3456 | 5569 |
| path | keygen_baseinv_actual | 2 | 4056 | 4043 | -0.32% | paired only | 4300 | 4312 |
| path | keygen_basemul_actual | 2 | 2641 | 1661 | -37.11% | paired only | 2491 | 2319 |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 5705 | -14.76% | -1976 | 6787 | 6629 |
| path | keygen_poly_tobytes_public | 1 | 458 | 566 | +23.58% | +108 | 784 | 1202 |
| path | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +32.10% | +147 | 784 | 1321 |
| path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 570 | +24.45% | +112 | 784 | 1203 |
| path | keygen_hash_f_pk | 1 | 11869 | 11876 | +0.06% | +7 | 39329 | 39329 |
| **path subtotal** | | | **39950** | **37677** | **-5.69%** | **-2273** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11868 | 11876 | +0.07% | +8 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2741 | 2735 | -0.22% | -6 | 8889 | 8889 |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | enc_poly_ntt_r | 1 | 3458 | 2596 | -24.93% | -862 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | enc_hash_g_polybytes | 1 | 13129 | 13124 | -0.04% | -5 | 43518 | 43518 |
| path | enc_poly_sotp_encode | 1 | 323 | 316 | -2.17% | -7 | 524 | 524 |
| path | enc_poly_ntt_m | 1 | 3441 | 2593 | -24.64% | -848 | 3263 | 3706 |
| path | enc_poly_frombytes_pk | 1 | 326 | 489 | +50.00% | +163 | 566 | 1105 |
| path | enc_basemul_add_actual | 1 | 2569 | 2286 | -11.02% | -283 | 2612 | 2216 |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | enc_basemul_add_plus_pack | 1 | 3027 | 2900 | -4.20% | -127 | 3392 | 3581 |
| **path subtotal** | | | **39074** | **37550** | **-3.90%** | **-1524** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 2 | 327 | 489 | +49.54% | +324 | 568 | 1105 |
| path | dec_first_basemul_actual | 1 | 2641 | 1911 | -27.64% | -730 | 2489 | 1903 |
| path | dec_first_invntt_actual | 1 | 3952 | 3557 | -9.99% | -395 | 3470 | 4821 |
| combined | dec_first_basemul_plus_invntt | 1 | 6594 | 5470 | -17.05% | -1124 | 5955 | 6720 |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | 400 | 400 |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2597 | -24.53% | -844 | 3263 | 3706 |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | 225 | 225 |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2487 | 2489 |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3413 | -0.35% | -12 | 3831 | 4310 |
| path | dec_hash_g_polybytes | 1 | 13129 | 13133 | +0.03% | +4 | 43518 | 43518 |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | 543 | 543 |
| path | dec_hash_h_msg | 1 | 2740 | 2739 | -0.04% | -1 | 8889 | 8889 |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2596 | -24.93% | -862 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 615 | +34.28% | +157 | 781 | 1366 |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | 532 | 532 |
| **path subtotal** | | | **35232** | **32857** | **-6.74%** | **-2375** | | |


## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 2 | 327 | 489 | +324 |
| ENCAP | enc_poly_frombytes_pk | 1 | 326 | 489 | +163 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 616 | +158 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 616 | +158 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 615 | +157 |
| KEYGEN | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +147 |
| KEYGEN | keygen_poly_tobytes_secret_hinv | 1 | 458 | 570 | +112 |
| KEYGEN | keygen_poly_tobytes_public | 1 | 458 | 566 | +108 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | 747eb7036b31 | 162618 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/32 |
|  |  |  |  | poly_basemul | 704 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
| gt_production_default | kem_components | 500fc3910f89 | 167466 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
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
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/44 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/16 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/16 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/16 |
| gt_production_default | kem_keygen | b8e449eca233 | 95286 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/32 |
|  |  |  |  | poly_basemul | 704 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| gt_production_default | kem_enc | e2e194961ae4 | 95270 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/32 |
|  |  |  |  | poly_basemul | 704 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| gt_production_default | kem_dec | 7323c9ecf562 | 95270 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 2880 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 464 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 0/32 |
|  |  |  |  | poly_basemul | 704 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
| kpqc_final | kernel_components | 26a05bfc6480 | 45177 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | c401b732864b | 50113 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_keygen | f6eeab5261eb | 37342 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 4cf917ec1758 | 37342 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | 8b9aa2fca811 | 37342 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
