# GT Production vs KPQC Final Detailed Profile

Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.
Each row is p50 of 31 samples x 2000 calls; warmup=100.
All variants use uniform section GC.
All binaries run deterministic KEM setup and correctness checks before PMU; the component mode also runs a reconstructed-ciphertext decapsulation postflight. Full KEM totals are decisive; component subtotals omit copies/call overhead and are used for hotspot attribution only.
Cycles and retired instructions are collected in separate counter builds/runs. Derived CPI is therefore diagnostic rather than a same-group atomic PMU sample.

## Measurement Environment

- Git HEAD: `unavailable (rsync mirror)` (not a Git worktree)
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- Host: `Linux pinhao 6.18.33+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.18.33-1+rpt1 (2026-06-01) aarch64 GNU/Linux`

## Full KEM

| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39929/39937/39944 | 37745/37753/37758 | -5.47% | 80801 | 86069 |
| kem_enc | 39063/39067/39073 | 37586/37590/37595 | -3.78% | 103976 | 106173 |
| kem_dec | 35178/35182/35187 | 32848/32850/32852 | -6.63% | 72677 | 76429 |

## Optional Candidate Variants

These variants were linked and measured in the same profile run but remain separate from the production default.

| Operation | Candidate | Candidate cycles | Delta vs GT production | Delta vs KPQC | Candidate instr |
|---|---|---:|---:|---:|---:|
| kem_keygen | gt_keygen_all_cq_shared_core_direct_cq | 36767 | -986 (-2.61%) | -3170 (-7.94%) | 81573 |
| kem_enc | gt_keygen_all_cq_shared_core_direct_cq | 37604 | +14 (+0.04%) | -1463 (-3.74%) | 106185 |
| kem_dec | gt_keygen_all_cq_shared_core_direct_cq | 32955 | +105 (+0.32%) | -2227 (-6.33%) | 76441 |

## Generic/Public Primitive Diagnostics

These rows compare isolated public/generic kernels. They are API and algorithm diagnostics, not a list of the specialized kernels selected by the production KEM. In particular, `inverse_ntt_generic`, `basemul`, `basemul_add`, and `baseinv_generic` must not be substituted for the `*_actual` KEM-path rows below.
Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3620 | 2860 | -20.99% | 3265 | 3708 | 1.109 | 0.771 |
| TRANSFORM | inverse_ntt_generic | 3965 | 4079 | +2.88% | 3472 | 5093 | 1.142 | 0.801 |
| POINTWISE | basemul | 2669 | 2851 | +6.82% | 2493 | 2495 | 1.071 | 1.143 |
| POINTWISE | basemul_add | 2637 | 2951 | +11.91% | 2616 | 2810 | 1.008 | 1.050 |
| POINTWISE | baseinv_generic | 4056 | 4983 | +22.86% | 4298 | 4427 | 0.944 | 1.126 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14098 | 12888 | -8.58% | 12477 | 14986 | 1.130 | 0.860 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17790 | 16170 | -9.11% | 15857 | 19001 | 1.122 | 0.851 |
| SERIALIZE | ntt_tobytes_internal_layout | 458 | 399 | -12.88% | 782 | 782 | 0.586 | 0.510 |
| SERIALIZE | ntt_frombytes_internal_layout | 327 | 310 | -5.20% | 566 | 566 | 0.578 | 0.548 |
| SERIALIZE | ntt_tobytes_canonical | 458 | 612 | +33.62% | 782 | 1367 | 0.586 | 0.448 |
| SERIALIZE | ntt_frombytes_canonical | 326 | 487 | +49.39% | 566 | 1103 | 0.576 | 0.442 |
| SUPPORT | cbd1 | 302 | 302 | +0.00% | 501 | 501 | 0.603 | 0.603 |
| SUPPORT | triple | 196 | 192 | -2.04% | 197 | 197 | 0.995 | 0.975 |
| SUPPORT | crepmod3 | 398 | 384 | -3.52% | 398 | 398 | 1.000 | 0.965 |
| SUPPORT | poly_sub | 172 | 172 | +0.00% | 222 | 222 | 0.775 | 0.775 |
| SUPPORT | sotp_encode | 315 | 315 | +0.00% | 521 | 521 | 0.605 | 0.605 |
| SUPPORT | sotp_decode | 310 | 310 | +0.00% | 540 | 540 | 0.574 | 0.574 |

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
| path | keygen_shake256_sample | 2 | 2719 | 2719 | +0.00% | +0 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 302 | 302 | +0.00% | +0 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 3299 | -9.42% | -343 | 3459 | 5570 |
| path | keygen_sample_ntt_g | 1 | 3639 | 3304 | -9.21% | -335 | 3454 | 5567 |
| path | keygen_baseinv_actual | 2 | 4056 | 4039 | -0.42% | paired only | 4298 | 4310 |
| path | keygen_basemul_actual | 2 | 2641 | 1670 | -36.77% | paired only | 2488 | 2318 |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6694 | 5710 | -14.70% | -1968 | 6783 | 6625 |
| path | keygen_poly_tobytes_public | 1 | 458 | 566 | +23.58% | +108 | 782 | 1200 |
| path | keygen_poly_tobytes_secret_f | 1 | 458 | 619 | +35.15% | +161 | 782 | 1319 |
| path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | +23.58% | +108 | 782 | 1200 |
| path | keygen_hash_f_pk | 1 | 11858 | 11860 | +0.02% | +2 | 39329 | 39329 |
| **path subtotal** | | | **39949** | **37674** | **-5.69%** | **-2275** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11858 | 11856 | -0.02% | -2 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2737 | 2737 | +0.00% | +0 | 8887 | 8887 |
| path | enc_poly_cbd1_r | 1 | 302 | 302 | +0.00% | +0 | 501 | 501 |
| path | enc_poly_ntt_r | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 612 | +33.62% | +154 | 782 | 1367 |
| path | enc_hash_g_polybytes | 1 | 13095 | 13090 | -0.04% | -5 | 43516 | 43516 |
| path | enc_poly_sotp_encode | 1 | 315 | 315 | +0.00% | +0 | 521 | 521 |
| path | enc_poly_ntt_m | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | enc_poly_frombytes_pk | 1 | 327 | 487 | +48.93% | +160 | 566 | 1103 |
| path | enc_basemul_add_actual | 1 | 2569 | 2285 | -11.05% | -284 | 2610 | 2214 |
| path | enc_poly_tobytes_ct | 1 | 458 | 612 | +33.62% | +154 | 782 | 1367 |
| combined | enc_basemul_add_plus_pack | 1 | 3028 | 2899 | -4.26% | -129 | 3389 | 3578 |
| **path subtotal** | | | **39035** | **37484** | **-3.97%** | **-1551** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 2 | 327 | 487 | +48.93% | +320 | 566 | 1103 |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | 2488 | 1914 |
| path | dec_first_invntt_actual | 1 | 3952 | 3556 | -10.02% | -396 | 3468 | 4819 |
| combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5575 | -15.43% | -1017 | 5953 | 6730 |
| path | dec_poly_crepmod3 | 1 | 398 | 384 | -3.52% | -14 | 398 | 398 |
| path | dec_poly_ntt_m1 | 1 | 3458 | 2595 | -24.96% | -863 | 3261 | 3704 |
| path | dec_poly_sub | 1 | 172 | 172 | +0.00% | +0 | 222 | 222 |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2488 | 2490 |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 612 | +33.62% | +154 | 782 | 1367 |
| path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3282 | -4.18% | -143 | 3830 | 4256 |
| path | dec_hash_g_polybytes | 1 | 13096 | 13091 | -0.04% | -5 | 43516 | 43516 |
| path | dec_poly_sotp_decode | 1 | 310 | 310 | +0.00% | +0 | 540 | 540 |
| path | dec_hash_h_msg | 1 | 2738 | 2738 | +0.00% | +0 | 8887 | 8887 |
| path | dec_poly_cbd1_r1 | 1 | 302 | 302 | +0.00% | +0 | 501 | 501 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 612 | +33.62% | +154 | 782 | 1367 |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | 533 | 533 |
| **path subtotal** | | | **35212** | **32780** | **-6.91%** | **-2432** | | |

## Optional Candidate Component Deltas

These tables use the same fixtures and measured boundaries as the two baseline component tables. Candidate rows are actual candidate-macro paths, not generic substitutes.

### Generic/Public Primitive Diagnostics: `gt_keygen_all_cq_shared_core_direct_cq`

| Group | Kind | Component | Count | KPQC cycles | GT production cycles | Candidate cycles | Candidate vs GT | Candidate vs KPQC | KPQC instr | GT instr | Candidate instr |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | primitive | forward_ntt | 1 | 3620 | 2860 | 2872 | +12 (+0.42%) | -748 (-20.66%) | 3265 | 3708 | 3714 |
| TRANSFORM | primitive | inverse_ntt_generic | 1 | 3965 | 4079 | 4071 | -8 (-0.20%) | +106 (+2.67%) | 3472 | 5093 | 5093 |
| POINTWISE | primitive | basemul | 1 | 2669 | 2851 | 2858 | +7 (+0.25%) | +189 (+7.08%) | 2493 | 2495 | 2495 |
| POINTWISE | primitive | basemul_add | 1 | 2637 | 2951 | 2929 | -22 (-0.75%) | +292 (+11.07%) | 2616 | 2810 | 2810 |
| POINTWISE | primitive | baseinv_generic | 1 | 4056 | 4983 | 4983 | +0 (+0.00%) | +927 (+22.86%) | 4298 | 4427 | 4427 |
| PIPELINE | primitive | polymul_2ntt_basemul_invntt | 1 | 14098 | 12888 | 12908 | +20 (+0.16%) | -1190 (-8.44%) | 12477 | 14986 | 14998 |
| PIPELINE | primitive | polymul_add_3ntt_basemuladd_invntt | 1 | 17790 | 16170 | 16154 | -16 (-0.10%) | -1636 (-9.20%) | 15857 | 19001 | 19019 |
| SERIALIZE | diagnostic | ntt_tobytes_internal_layout | 1 | 458 | 399 | 399 | +0 (+0.00%) | -59 (-12.88%) | 782 | 782 | 782 |
| SERIALIZE | diagnostic | ntt_frombytes_internal_layout | 1 | 327 | 310 | 310 | +0 (+0.00%) | -17 (-5.20%) | 566 | 566 | 566 |
| SERIALIZE | primitive | ntt_tobytes_canonical | 1 | 458 | 612 | 612 | +0 (+0.00%) | +154 (+33.62%) | 782 | 1367 | 1367 |
| SERIALIZE | primitive | ntt_frombytes_canonical | 1 | 326 | 487 | 487 | +0 (+0.00%) | +161 (+49.39%) | 566 | 1103 | 1103 |
| SUPPORT | primitive | cbd1 | 1 | 302 | 302 | 302 | +0 (+0.00%) | +0 (+0.00%) | 501 | 501 | 501 |
| SUPPORT | primitive | triple | 1 | 196 | 192 | 192 | +0 (+0.00%) | -4 (-2.04%) | 197 | 197 | 197 |
| SUPPORT | primitive | crepmod3 | 1 | 398 | 384 | 384 | +0 (+0.00%) | -14 (-3.52%) | 398 | 398 | 398 |
| SUPPORT | primitive | poly_sub | 1 | 172 | 172 | 172 | +0 (+0.00%) | +0 (+0.00%) | 222 | 222 | 222 |
| SUPPORT | primitive | sotp_encode | 1 | 315 | 315 | 315 | +0 (+0.00%) | +0 (+0.00%) | 521 | 521 | 521 |
| SUPPORT | primitive | sotp_decode | 1 | 310 | 310 | 310 | +0 (+0.00%) | +0 (+0.00%) | 540 | 540 | 540 |

### Actual KEM-Path Components: `gt_keygen_all_cq_shared_core_direct_cq`

| Group | Kind | Component | Count | KPQC cycles | GT production cycles | Candidate cycles | Candidate vs GT | Candidate vs KPQC | KPQC instr | GT instr | Candidate instr |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KEYGEN | path | keygen_shake256_sample | 2 | 2719 | 2719 | 2724 | +5 (+0.18%) | +5 (+0.18%) | 8857 | 8857 | 8857 |
| KEYGEN | path | keygen_poly_cbd1_secret | 2 | 302 | 302 | 302 | +0 (+0.00%) | +0 (+0.00%) | 501 | 501 | 501 |
| KEYGEN | path | keygen_sample_ntt_f | 1 | 3642 | 3299 | 2846 | -453 (-13.73%) | -796 (-21.86%) | 3459 | 5570 | 3933 |
| KEYGEN | path | keygen_sample_ntt_g | 1 | 3639 | 3304 | 2858 | -446 (-13.50%) | -781 (-21.46%) | 3454 | 5567 | 3930 |
| KEYGEN | path | keygen_baseinv_actual | 2 | 4056 | 4039 | 3946 | -93 (-2.30%) | -110 (-2.71%) | 4298 | 4310 | 4039 |
| KEYGEN | path | keygen_basemul_actual | 2 | 2641 | 1670 | 1762 | +92 (+5.51%) | -879 (-33.28%) | 2488 | 2318 | 2037 |
| KEYGEN | combined | keygen_baseinv_plus_basemul_contract | 2 | 6694 | 5710 | 5708 | -2 (-0.04%) | -986 (-14.73%) | 6783 | 6625 | 6073 |
| KEYGEN | path | keygen_poly_tobytes_public | 1 | 458 | 566 | 568 | +2 (+0.35%) | +110 (+24.02%) | 782 | 1200 | 1200 |
| KEYGEN | path | keygen_poly_tobytes_secret_f | 1 | 458 | 619 | 568 | -51 (-8.24%) | +110 (+24.02%) | 782 | 1319 | 1200 |
| KEYGEN | path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | 568 | +2 (+0.35%) | +110 (+24.02%) | 782 | 1200 | 1200 |
| KEYGEN | path | keygen_hash_f_pk | 1 | 11858 | 11860 | 11880 | +20 (+0.17%) | +22 (+0.19%) | 39329 | 39329 | 39329 |
| ENCAP | path | enc_hash_f_pk | 1 | 11858 | 11856 | 11877 | +21 (+0.18%) | +19 (+0.16%) | 39329 | 39329 | 39329 |
| ENCAP | path | enc_hash_h_msg | 1 | 2737 | 2737 | 2737 | +0 (+0.00%) | +0 (+0.00%) | 8887 | 8887 | 8887 |
| ENCAP | path | enc_poly_cbd1_r | 1 | 302 | 302 | 302 | +0 (+0.00%) | +0 (+0.00%) | 501 | 501 | 501 |
| ENCAP | path | enc_poly_ntt_r | 1 | 3458 | 2594 | 2602 | +8 (+0.31%) | -856 (-24.75%) | 3261 | 3704 | 3710 |
| ENCAP | path | enc_poly_tobytes_r | 1 | 458 | 612 | 612 | +0 (+0.00%) | +154 (+33.62%) | 782 | 1367 | 1367 |
| ENCAP | path | enc_hash_g_polybytes | 1 | 13095 | 13090 | 13120 | +30 (+0.23%) | +25 (+0.19%) | 43516 | 43516 | 43516 |
| ENCAP | path | enc_poly_sotp_encode | 1 | 315 | 315 | 315 | +0 (+0.00%) | +0 (+0.00%) | 521 | 521 | 521 |
| ENCAP | path | enc_poly_ntt_m | 1 | 3458 | 2594 | 2602 | +8 (+0.31%) | -856 (-24.75%) | 3261 | 3704 | 3710 |
| ENCAP | path | enc_poly_frombytes_pk | 1 | 327 | 487 | 487 | +0 (+0.00%) | +160 (+48.93%) | 566 | 1103 | 1103 |
| ENCAP | path | enc_basemul_add_actual | 1 | 2569 | 2285 | 2285 | +0 (+0.00%) | -284 (-11.05%) | 2610 | 2214 | 2214 |
| ENCAP | path | enc_poly_tobytes_ct | 1 | 458 | 612 | 612 | +0 (+0.00%) | +154 (+33.62%) | 782 | 1367 | 1367 |
| ENCAP | combined | enc_basemul_add_plus_pack | 1 | 3028 | 2899 | 2899 | +0 (+0.00%) | -129 (-4.26%) | 3389 | 3578 | 3578 |
| DECAP | path | dec_poly_frombytes | 2 | 327 | 487 | 487 | +0 (+0.00%) | +160 (+48.93%) | 566 | 1103 | 1103 |
| DECAP | path | dec_first_basemul_actual | 1 | 2641 | 2020 | 2019 | -1 (-0.05%) | -622 (-23.55%) | 2488 | 1914 | 1914 |
| DECAP | path | dec_first_invntt_actual | 1 | 3952 | 3556 | 3557 | +1 (+0.03%) | -395 (-9.99%) | 3468 | 4819 | 4819 |
| DECAP | combined | dec_first_basemul_plus_invntt | 1 | 6592 | 5575 | 5575 | +0 (+0.00%) | -1017 (-15.43%) | 5953 | 6730 | 6730 |
| DECAP | path | dec_poly_crepmod3 | 1 | 398 | 384 | 384 | +0 (+0.00%) | -14 (-3.52%) | 398 | 398 | 398 |
| DECAP | path | dec_poly_ntt_m1 | 1 | 3458 | 2595 | 2602 | +7 (+0.27%) | -856 (-24.75%) | 3261 | 3704 | 3710 |
| DECAP | path | dec_poly_sub | 1 | 172 | 172 | 172 | +0 (+0.00%) | +0 (+0.00%) | 222 | 222 | 222 |
| DECAP | diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | 2813 | +0 (+0.00%) | +172 (+6.51%) | 2488 | 2490 | 2490 |
| DECAP | diagnostic | dec_verify_generic_pack | 1 | 458 | 612 | 612 | +0 (+0.00%) | +154 (+33.62%) | 782 | 1367 | 1367 |
| DECAP | path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3282 | 3282 | +0 (+0.00%) | -143 (-4.18%) | 3830 | 4256 | 4256 |
| DECAP | path | dec_hash_g_polybytes | 1 | 13096 | 13091 | 13112 | +21 (+0.16%) | +16 (+0.12%) | 43516 | 43516 | 43516 |
| DECAP | path | dec_poly_sotp_decode | 1 | 310 | 310 | 310 | +0 (+0.00%) | +0 (+0.00%) | 540 | 540 | 540 |
| DECAP | path | dec_hash_h_msg | 1 | 2738 | 2738 | 2739 | +1 (+0.04%) | +1 (+0.04%) | 8887 | 8887 | 8887 |
| DECAP | path | dec_poly_cbd1_r1 | 1 | 302 | 302 | 302 | +0 (+0.00%) | +0 (+0.00%) | 501 | 501 | 501 |
| DECAP | path | dec_poly_ntt_r1 | 1 | 3458 | 2594 | 2602 | +8 (+0.31%) | -856 (-24.75%) | 3261 | 3704 | 3710 |
| DECAP | path | dec_poly_tobytes_r1 | 1 | 458 | 612 | 612 | +0 (+0.00%) | +154 (+33.62%) | 782 | 1367 | 1367 |
| DECAP | path | dec_verify_polybytes | 1 | 150 | 150 | 150 | +0 (+0.00%) | +0 (+0.00%) | 533 | 533 | 533 |

## Measured Optimization Budget

Positive rows are places where GT currently spends more cycles than KPQC. The weighted delta is the first-order full-KEM budget if that row were only brought to KPQC parity; it is not a guaranteed end-to-end saving.
The GT scaled baseinv and its matching keygen basemul are represented by their combined contract row; their individual factor-shifted rows are not counted as separate optimization budgets.
Hash/SHAKE rows remain visible in the component tables but are excluded here.

| Group | Component | Count | KPQC cycles | GT cycles | Weighted GT overhead |
|---|---|---:|---:|---:|---:|
| DECAP | dec_poly_frombytes | 2 | 327 | 487 | +320 |
| KEYGEN | keygen_poly_tobytes_secret_f | 1 | 458 | 619 | +161 |
| ENCAP | enc_poly_frombytes_pk | 1 | 327 | 487 | +160 |
| ENCAP | enc_poly_tobytes_r | 1 | 458 | 612 | +154 |
| ENCAP | enc_poly_tobytes_ct | 1 | 458 | 612 | +154 |
| DECAP | dec_poly_tobytes_r1 | 1 | 458 | 612 | +154 |
| KEYGEN | keygen_poly_tobytes_public | 1 | 458 | 566 | +108 |
| KEYGEN | keygen_poly_tobytes_secret_hinv | 1 | 458 | 566 | +108 |

## Binary Metadata

Metadata is recorded from each mode's cycle-counter binary.

| Variant | Mode | Binary SHA256 | Text bytes | Symbol | Size | Address mod32/mod64 |
|---|---|---|---:|---|---:|---:|
| gt_production_default | kernel_components | 3fece0ed91a4 | 142382 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
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
|  |  |  |  | poly_baseinv | 12 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | poly_basemul_add | 20 | 0/32 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/32 |
| gt_production_default | kem_components | e39b3daa8383 | 143142 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
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
|  |  |  |  | poly_baseinv | 12 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
| gt_production_default | kem_keygen | f3dccfffe120 | 89834 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
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
| gt_production_default | kem_enc | 5bdc3bbcad05 | 89818 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
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
| gt_production_default | kem_dec | 27737d70de97 | 89818 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | poly_ntt | 14776 | 0/0 |
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
| gt_keygen_all_cq_shared_core_direct_cq | kernel_components | ea8b00de1d2a | 145182 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 0/32 |
|  |  |  |  | poly_baseinv | 12 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/16 |
|  |  |  |  | poly_basemul | 20 | 16/48 |
|  |  |  |  | poly_basemul_add | 20 | 0/0 |
|  |  |  |  | poly_basemul_add32 | 20 | 0/0 |
|  |  |  |  | gt_experiment_keygen_baseinv_cq_to_cq_scaled_r | 576 | 0/0 |
|  |  |  |  | gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r | 372 | 0/0 |
|  |  |  |  | poly_ntt | 8 | 0/0 |
|  |  |  |  | gt_experiment_poly_ntt_to_cq | 24408 | 8/8 |
| gt_keygen_all_cq_shared_core_direct_cq | kem_components | aa559884da1e | 146086 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/16 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 24/56 |
|  |  |  |  | poly_tobytes | 12 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/0 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/16 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/0 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/48 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/16 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 0/0 |
|  |  |  |  | poly_baseinv | 12 | 0/32 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 16/48 |
|  |  |  |  | poly_basemul | 20 | 16/16 |
|  |  |  |  | gt_experiment_keygen_baseinv_cq_to_cq_scaled_r | 576 | 0/32 |
|  |  |  |  | gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r | 372 | 0/32 |
|  |  |  |  | poly_ntt | 8 | 0/32 |
|  |  |  |  | gt_experiment_poly_ntt_to_cq | 24408 | 8/40 |
| gt_keygen_all_cq_shared_core_direct_cq | kem_keygen | 7467d96d812a | 92794 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 0/32 |
|  |  |  |  | gt_experiment_keygen_baseinv_cq_to_cq_scaled_r | 576 | 0/32 |
|  |  |  |  | gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r | 372 | 0/32 |
|  |  |  |  | poly_ntt | 8 | 0/32 |
|  |  |  |  | gt_experiment_poly_ntt_to_cq | 24408 | 8/40 |
| gt_keygen_all_cq_shared_core_direct_cq | kem_enc | 403b1d600cb3 | 92778 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 0/32 |
|  |  |  |  | gt_experiment_keygen_baseinv_cq_to_cq_scaled_r | 576 | 0/32 |
|  |  |  |  | gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r | 372 | 0/32 |
|  |  |  |  | poly_ntt | 8 | 0/32 |
|  |  |  |  | gt_experiment_poly_ntt_to_cq | 24408 | 8/40 |
| gt_keygen_all_cq_shared_core_direct_cq | kem_dec | ab603300da66 | 92778 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_hier_k8 | 2296 | 0/32 |
|  |  |  |  | gt_keygen_baseinv_cq_finish | 156 | 16/48 |
|  |  |  |  | gt_keygen_tobytes_cq | 5168 | 0/32 |
|  |  |  |  | gt_fqinv15_asm | 448 | 16/16 |
|  |  |  |  | poly_basemul_rminus1 | 20 | 16/48 |
|  |  |  |  | poly_basemul_add_encap_direct32_q31_tobytes_contract | 40 | 0/32 |
|  |  |  |  | gt_experiment_keygen_baseinv_cq_to_cq_scaled_r | 576 | 0/32 |
|  |  |  |  | gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r | 372 | 0/32 |
|  |  |  |  | poly_ntt | 8 | 0/32 |
|  |  |  |  | gt_experiment_poly_ntt_to_cq | 24408 | 8/40 |
| kpqc_final | kernel_components | 7c1aabd087cc | 31189 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | ef66ae3f0276 | 34450 | poly_baseinv | 952 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 0/32 |
|  |  |  |  | poly_tobytes | 12 | 8/40 |
|  |  |  |  | poly_ntt | 12 | 16/48 |
|  |  |  |  | poly_invntt | 8 | 24/24 |
|  |  |  |  | poly_basemul | 12 | 0/0 |
|  |  |  |  | poly_basemul_add | 12 | 12/44 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/44 |
| kpqc_final | kem_keygen | 88a27acb11f5 | 23178 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 893f6baf92f4 | 23162 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | 7ef8c5fed472 | 23162 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
