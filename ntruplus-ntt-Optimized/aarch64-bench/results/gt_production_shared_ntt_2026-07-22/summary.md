# GT Production vs KPQC Final Detailed Profile

Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.
Each row is p50 of 61 samples x 2000 calls; warmup=200.
Both binaries run deterministic KEM setup and correctness checks before PMU; the component mode also runs a reconstructed-ciphertext decapsulation postflight. Full KEM totals are decisive; component subtotals omit copies/call overhead and are used for hotspot attribution only.
This run collected cycles only; instruction and CPI columns are reported as n/a.

## Measurement Environment

- Git HEAD: `unavailable (rsync mirror)` (not a Git worktree)
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- Host: `Linux pinhao 6.18.33+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.18.33-1+rpt1 (2026-06-01) aarch64 GNU/Linux`

## Full KEM

| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39956/39964/39966 | 37695/37702/37707 | -5.66% | n/a | n/a |
| kem_enc | 39063/39066/39070 | 37568/37576/37583 | -3.81% | n/a | n/a |
| kem_dec | 35187/35189/35192 | 32867/32872/32876 | -6.58% | n/a | n/a |


## Generic/Public Primitive Diagnostics

These rows compare isolated public/generic kernels. They are API and algorithm diagnostics, not a list of the specialized kernels selected by the production KEM. In particular, `inverse_ntt_generic`, `basemul`, `basemul_add`, and `baseinv_generic` must not be substituted for the `*_actual` KEM-path rows below.
Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3587 | 2911 | -18.85% | n/a | n/a | n/a | n/a |
| TRANSFORM | inverse_ntt_generic | 3969 | 4071 | +2.57% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul | 2670 | 2834 | +6.14% | n/a | n/a | n/a | n/a |
| POINTWISE | basemul_add | 2633 | 2925 | +11.09% | n/a | n/a | n/a | n/a |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_2ntt_basemul_invntt | 14179 | 12923 | -8.86% | n/a | n/a | n/a | n/a |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17844 | 16283 | -8.75% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_tobytes_internal_layout | 458 | 399 | -12.88% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_frombytes_internal_layout | 327 | 302 | -7.65% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_tobytes_canonical | 458 | 616 | +34.50% | n/a | n/a | n/a | n/a |
| SERIALIZE | ntt_frombytes_canonical | 327 | 489 | +49.54% | n/a | n/a | n/a | n/a |
| SUPPORT | cbd1 | 305 | 305 | +0.00% | n/a | n/a | n/a | n/a |
| SUPPORT | triple | 196 | 192 | -2.04% | n/a | n/a | n/a | n/a |
| SUPPORT | crepmod3 | 400 | 384 | -4.00% | n/a | n/a | n/a | n/a |
| SUPPORT | poly_sub | 173 | 173 | +0.00% | n/a | n/a | n/a | n/a |
| SUPPORT | sotp_encode | 322 | 322 | +0.00% | n/a | n/a | n/a | n/a |
| SUPPORT | sotp_decode | 310 | 310 | +0.00% | n/a | n/a | n/a | n/a |

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
| path | keygen_shake256_sample | 2 | 2717 | 2724 | +0.26% | +14 | n/a | n/a |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | keygen_sample_ntt_f | 1 | 3642 | 3302 | -9.34% | -340 | n/a | n/a |
| path | keygen_sample_ntt_g | 1 | 3639 | 3305 | -9.18% | -334 | n/a | n/a |
| path | keygen_baseinv_actual | 2 | 4056 | 4044 | -0.30% | paired only | n/a | n/a |
| path | keygen_basemul_actual | 2 | 2641 | 1668 | -36.84% | paired only | n/a | n/a |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6693 | 5709 | -14.70% | -1968 | n/a | n/a |
| path | keygen_poly_tobytes_public | 1 | 458 | 566 | +23.58% | +108 | n/a | n/a |
| path | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +32.10% | +147 | n/a | n/a |
| path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 568 | +24.02% | +110 | n/a | n/a |
| path | keygen_hash_f_pk | 1 | 11873 | 11857 | -0.13% | -16 | n/a | n/a |
| **path subtotal** | | | **39962** | **37681** | **-5.71%** | **-2281** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11871 | 11861 | -0.08% | -10 | n/a | n/a |
| path | enc_hash_h_msg | 1 | 2742 | 2737 | -0.18% | -5 | n/a | n/a |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | enc_poly_ntt_r | 1 | 3458 | 2594 | -24.99% | -864 | n/a | n/a |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | enc_hash_g_polybytes | 1 | 13129 | 13111 | -0.14% | -18 | n/a | n/a |
| path | enc_poly_sotp_encode | 1 | 323 | 316 | -2.17% | -7 | n/a | n/a |
| path | enc_poly_ntt_m | 1 | 3441 | 2593 | -24.64% | -848 | n/a | n/a |
| path | enc_poly_frombytes_pk | 1 | 326 | 489 | +50.00% | +163 | n/a | n/a |
| path | enc_basemul_add_actual | 1 | 2569 | 2287 | -10.98% | -282 | n/a | n/a |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| combined | enc_basemul_add_plus_pack | 1 | 3029 | 2900 | -4.26% | -129 | n/a | n/a |
| **path subtotal** | | | **39078** | **37523** | **-3.98%** | **-1555** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 2 | 327 | 489 | +49.54% | +324 | n/a | n/a |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | n/a | n/a |
| path | dec_first_invntt_actual | 1 | 3952 | 3555 | -10.05% | -397 | n/a | n/a |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5575 | -15.43% | -1017 | n/a | n/a |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | n/a | n/a |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2593 | -24.64% | -848 | n/a | n/a |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | n/a | n/a |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | n/a | n/a |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | +34.50% | +158 | n/a | n/a |
| path | dec_verify_product_to_bytes_actual | 1 | 3427 | 3301 | -3.68% | -126 | n/a | n/a |
| path | dec_hash_g_polybytes | 1 | 13126 | 13111 | -0.11% | -15 | n/a | n/a |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | n/a | n/a |
| path | dec_hash_h_msg | 1 | 2747 | 2738 | -0.33% | -9 | n/a | n/a |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | n/a | n/a |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2594 | -24.99% | -864 | n/a | n/a |
| path | dec_poly_tobytes_r1 | 1 | 458 | 613 | +33.84% | +155 | n/a | n/a |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | n/a | n/a |
| **path subtotal** | | | **35238** | **32821** | **-6.86%** | **-2417** | | |

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
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 613 | +155 |
| KEYGEN | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +147 |
| KEYGEN | keygen_poly_tobytes_secret_hinv | 1 | 458 | 568 | +110 |
| KEYGEN | keygen_poly_tobytes_public | 1 | 458 | 566 | +108 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | a376740f09f1 | 174858 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/32 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | poly_basemul | 20 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
| gt_production_default | kem_components | 9126d9842b08 | 179762 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/32 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/48 |
|  |  |  |  | poly_frombytes | 12 | 8/8 |
|  |  |  |  | poly_tobytes | 12 | 16/16 |
|  |  |  |  | poly_ntt | 14776 | 16/16 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/0 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/48 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 16/48 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/0 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/32 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/16 |
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/12 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/32 |
|  |  |  |  | poly_baseinv | 16 | 0/0 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/0 |
|  |  |  |  | poly_basemul | 20 | 0/32 |
|  |  |  |  | poly_basemul_add | 20 | 16/48 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/48 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/48 |
| gt_production_default | kem_keygen | 270e6faa3266 | 107325 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/0 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| gt_production_default | kem_enc | 8b55a03350b7 | 107309 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/0 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| gt_production_default | kem_dec | 8f56e94df3dd | 107309 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 16/48 |
|  |  |  |  | gt_keygen_blockmajor_to_bpq | 116 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_to_cq_scaled_r | 144 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_bpq_prepare | 504 | 16/16 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_basemul_bpq_cq_to_cq_scaled_r | 1584 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_keygen_tobytes_bpq_p1 | 5264 | 16/16 |
|  |  |  |  | gt_fqinv15_asm | 448 | 0/32 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 0/0 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 16/48 |
| kpqc_final | kernel_components | ce2826dd8333 | 44913 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_components | 9028a790e4f9 | 49849 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | 4a28f1fbe892 | 36917 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_enc | 05018ac8b678 | 36901 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_dec | bfd625f0ab1e | 36901 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
