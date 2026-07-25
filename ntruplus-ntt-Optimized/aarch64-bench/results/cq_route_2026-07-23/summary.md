# GT Production vs KPQC Final Detailed Profile

Raspberry Pi 5 Cortex-A76, portable NO_CE hash path, core pinned.
Each row is p50 of 31 samples x 2000 calls; warmup=100.
All binaries run deterministic KEM setup and correctness checks before PMU; the component mode also runs a reconstructed-ciphertext decapsulation postflight. Full KEM totals are decisive; component subtotals omit copies/call overhead and are used for hotspot attribution only.
Cycles and retired instructions are collected in separate counter builds/runs. Derived CPI is therefore diagnostic rather than a same-group atomic PMU sample.

## Measurement Environment

- Git HEAD: `unavailable (rsync mirror)` (not a Git worktree)
- Compiler: `cc (Debian 14.2.0-19) 14.2.0`
- Host: `Linux pinhao 6.18.33+rpt-rpi-2712 #1 SMP PREEMPT Debian 1:6.18.33-1+rpt1 (2026-06-01) aarch64 GNU/Linux`

## Full KEM

| Operation | KPQC cycles p10/p50/p90 | GT cycles p10/p50/p90 | GT p50 delta | KPQC instr | GT instr |
|---|---:|---:|---:|---:|---:|
| kem_keygen | 39956/39959/39965 | 37700/37704/37710 | -5.64% | 80799 | 86067 |
| kem_enc | 39032/39036/39041 | 37589/37606/37613 | -3.66% | 103978 | 106175 |
| kem_dec | 35158/35160/35167 | 32847/32852/32860 | -6.56% | 72675 | 76429 |

## Optional Candidate Variants

These variants were linked and measured in the same profile run but remain separate from the production default.

| Operation | Candidate | Candidate cycles | Delta vs GT production | Delta vs KPQC | Candidate instr |
|---|---|---:|---:|---:|---:|
| kem_keygen | gt_keygen_all_cq_shared_core_direct_cq | 36764 | -940 (-2.49%) | -3195 (-8.00%) | 81573 |
| kem_enc | gt_keygen_all_cq_shared_core_direct_cq | 37564 | -42 (-0.11%) | -1472 (-3.77%) | 106185 |
| kem_dec | gt_keygen_all_cq_shared_core_direct_cq | 32930 | +78 (+0.24%) | -2230 (-6.34%) | 76441 |

## Generic/Public Primitive Diagnostics

These rows compare isolated public/generic kernels. They are API and algorithm diagnostics, not a list of the specialized kernels selected by the production KEM. In particular, `inverse_ntt_generic`, `basemul`, `basemul_add`, and `baseinv_generic` must not be substituted for the `*_actual` KEM-path rows below.
Internal NTT-domain layouts differ, so equality means equivalent scheme semantics, not byte-identical intermediate arrays.
The primitive transform/pipeline rows rotate over `NITERATIONS` input/output polynomials; they intentionally expose the larger working-set behavior.
`*_internal_layout` serialization rows are diagnostics. For GT they omit the canonical wire permutation; their delta to `*_canonical` isolates boundary cost.

| Group | Kernel | KPQC cycles | GT cycles | GT delta | KPQC instr | GT instr | KPQC CPI | GT CPI |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | forward_ntt | 3607 | 2866 | -20.54% | 3265 | 3708 | 1.105 | 0.773 |
| TRANSFORM | inverse_ntt_generic | 3974 | 4085 | +2.79% | 3472 | 5093 | 1.145 | 0.802 |
| POINTWISE | basemul | 2674 | 2838 | +6.13% | 2493 | 2495 | 1.073 | 1.137 |
| POINTWISE | basemul_add | 2630 | 2939 | +11.75% | 2616 | 2810 | 1.005 | 1.046 |
| POINTWISE | baseinv_generic | 4056 | 4985 | +22.90% | 4298 | 4432 | 0.944 | 1.125 |
| PIPELINE | polymul_2ntt_basemul_invntt | 14191 | 13111 | -7.61% | 12477 | 14986 | 1.137 | 0.875 |
| PIPELINE | polymul_add_3ntt_basemuladd_invntt | 17822 | 16413 | -7.91% | 15857 | 19001 | 1.124 | 0.864 |
| SERIALIZE | ntt_tobytes_internal_layout | 459 | 399 | -13.07% | 784 | 784 | 0.585 | 0.509 |
| SERIALIZE | ntt_frombytes_internal_layout | 328 | 310 | -5.49% | 568 | 568 | 0.577 | 0.546 |
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
| path | keygen_shake256_sample | 2 | 2722 | 2719 | -0.11% | -6 | 8857 | 8857 |
| path | keygen_poly_cbd1_secret | 2 | 303 | 303 | +0.00% | +0 | 501 | 501 |
| path | keygen_sample_ntt_f | 1 | 3642 | 3301 | -9.36% | -341 | 3461 | 5572 |
| path | keygen_sample_ntt_g | 1 | 3637 | 3306 | -9.10% | -331 | 3456 | 5569 |
| path | keygen_baseinv_actual | 2 | 4056 | 4044 | -0.30% | paired only | 4300 | 4312 |
| path | keygen_basemul_actual | 2 | 2641 | 1662 | -37.07% | paired only | 2491 | 2319 |
| combined | keygen_baseinv_plus_basemul_contract | 2 | 6694 | 5705 | -14.77% | -1978 | 6787 | 6629 |
| path | keygen_poly_tobytes_public | 1 | 458 | 566 | +23.58% | +108 | 784 | 1202 |
| path | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | +32.10% | +147 | 784 | 1321 |
| path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 568 | +24.02% | +110 | 784 | 1203 |
| path | keygen_hash_f_pk | 1 | 11886 | 11857 | -0.24% | -29 | 39329 | 39329 |
| **path subtotal** | | | **39983** | **37659** | **-5.81%** | **-2324** | | |

### Encap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | enc_hash_f_pk | 1 | 11886 | 11857 | -0.24% | -29 | 39329 | 39329 |
| path | enc_hash_h_msg | 1 | 2739 | 2738 | -0.04% | -1 | 8889 | 8889 |
| path | enc_poly_cbd1_r | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | enc_poly_ntt_r | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | enc_poly_tobytes_r | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | enc_hash_g_polybytes | 1 | 13143 | 13109 | -0.26% | -34 | 43518 | 43518 |
| path | enc_poly_sotp_encode | 1 | 323 | 316 | -2.17% | -7 | 524 | 524 |
| path | enc_poly_ntt_m | 1 | 3441 | 2588 | -24.79% | -853 | 3263 | 3706 |
| path | enc_poly_frombytes_pk | 1 | 326 | 489 | +50.00% | +163 | 566 | 1105 |
| path | enc_basemul_add_actual | 1 | 2569 | 2287 | -10.98% | -282 | 2612 | 2216 |
| path | enc_poly_tobytes_ct | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| combined | enc_basemul_add_plus_pack | 1 | 3027 | 2900 | -4.20% | -127 | 3392 | 3581 |
| **path subtotal** | | | **39104** | **37513** | **-4.07%** | **-1591** | | |

### Decap

| Kind | Component | Count | KPQC cycles | GT cycles | GT delta | Weighted cycle delta | KPQC instr | GT instr |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| path | dec_poly_frombytes | 2 | 327 | 489 | +49.54% | +324 | 568 | 1105 |
| path | dec_first_basemul_actual | 1 | 2641 | 2020 | -23.51% | -621 | 2489 | 1917 |
| path | dec_first_invntt_actual | 1 | 3952 | 3555 | -10.05% | -397 | 3470 | 4821 |
| combined | dec_first_basemul_plus_invntt | 1 | 6594 | 5575 | -15.45% | -1019 | 5955 | 6734 |
| path | dec_poly_crepmod3 | 1 | 400 | 384 | -4.00% | -16 | 400 | 400 |
| path | dec_poly_ntt_m1 | 1 | 3441 | 2588 | -24.79% | -853 | 3263 | 3706 |
| path | dec_poly_sub | 1 | 173 | 173 | +0.00% | +0 | 225 | 225 |
| diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | +6.51% | +172 | 2487 | 2489 |
| diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | +34.50% | +158 | 784 | 1369 |
| path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3282 | -4.18% | -143 | 3831 | 4260 |
| path | dec_hash_g_polybytes | 1 | 13142 | 13110 | -0.24% | -32 | 43518 | 43518 |
| path | dec_poly_sotp_decode | 1 | 308 | 308 | +0.00% | +0 | 543 | 543 |
| path | dec_hash_h_msg | 1 | 2738 | 2736 | -0.07% | -2 | 8889 | 8889 |
| path | dec_poly_cbd1_r1 | 1 | 303 | 303 | +0.00% | +0 | 503 | 503 |
| path | dec_poly_ntt_r1 | 1 | 3458 | 2594 | -24.99% | -864 | 3261 | 3704 |
| path | dec_poly_tobytes_r1 | 1 | 458 | 613 | +33.84% | +155 | 781 | 1366 |
| path | dec_verify_polybytes | 1 | 150 | 150 | +0.00% | +0 | 532 | 532 |
| **path subtotal** | | | **35243** | **32794** | **-6.95%** | **-2449** | | |

## Optional Candidate Component Deltas

These tables use the same fixtures and measured boundaries as the two baseline component tables. Candidate rows are actual candidate-macro paths, not generic substitutes.

### Generic/Public Primitive Diagnostics: `gt_keygen_all_cq_shared_core_direct_cq`

| Group | Kind | Component | Count | KPQC cycles | GT production cycles | Candidate cycles | Candidate vs GT | Candidate vs KPQC | KPQC instr | GT instr | Candidate instr |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TRANSFORM | primitive | forward_ntt | 1 | 3607 | 2866 | 2879 | +13 (+0.45%) | -728 (-20.18%) | 3265 | 3708 | 3714 |
| TRANSFORM | primitive | inverse_ntt_generic | 1 | 3974 | 4085 | 4070 | -15 (-0.37%) | +96 (+2.42%) | 3472 | 5093 | 5093 |
| POINTWISE | primitive | basemul | 1 | 2674 | 2838 | 2858 | +20 (+0.70%) | +184 (+6.88%) | 2493 | 2495 | 2495 |
| POINTWISE | primitive | basemul_add | 1 | 2630 | 2939 | 2931 | -8 (-0.27%) | +301 (+11.44%) | 2616 | 2810 | 2810 |
| POINTWISE | primitive | baseinv_generic | 1 | 4056 | 4985 | 4983 | -2 (-0.04%) | +927 (+22.86%) | 4298 | 4432 | 4427 |
| PIPELINE | primitive | polymul_2ntt_basemul_invntt | 1 | 14191 | 13111 | 12934 | -177 (-1.35%) | -1257 (-8.86%) | 12477 | 14986 | 14998 |
| PIPELINE | primitive | polymul_add_3ntt_basemuladd_invntt | 1 | 17822 | 16413 | 16250 | -163 (-0.99%) | -1572 (-8.82%) | 15857 | 19001 | 19019 |
| SERIALIZE | diagnostic | ntt_tobytes_internal_layout | 1 | 459 | 399 | 399 | +0 (+0.00%) | -60 (-13.07%) | 784 | 784 | 782 |
| SERIALIZE | diagnostic | ntt_frombytes_internal_layout | 1 | 328 | 310 | 310 | +0 (+0.00%) | -18 (-5.49%) | 568 | 568 | 566 |
| SERIALIZE | primitive | ntt_tobytes_canonical | 1 | 459 | 616 | 612 | -4 (-0.65%) | +153 (+33.33%) | 784 | 1369 | 1367 |
| SERIALIZE | primitive | ntt_frombytes_canonical | 1 | 328 | 489 | 487 | -2 (-0.41%) | +159 (+48.48%) | 568 | 1105 | 1103 |
| SUPPORT | primitive | cbd1 | 1 | 305 | 305 | 302 | -3 (-0.98%) | -3 (-0.98%) | 500 | 500 | 501 |
| SUPPORT | primitive | triple | 1 | 196 | 192 | 192 | +0 (+0.00%) | -4 (-2.04%) | 199 | 197 | 197 |
| SUPPORT | primitive | crepmod3 | 1 | 400 | 384 | 384 | +0 (+0.00%) | -16 (-4.00%) | 398 | 398 | 398 |
| SUPPORT | primitive | poly_sub | 1 | 173 | 173 | 172 | -1 (-0.58%) | -1 (-0.58%) | 225 | 225 | 222 |
| SUPPORT | primitive | sotp_encode | 1 | 322 | 322 | 315 | -7 (-2.17%) | -7 (-2.17%) | 521 | 521 | 521 |
| SUPPORT | primitive | sotp_decode | 1 | 310 | 310 | 310 | +0 (+0.00%) | +0 (+0.00%) | 542 | 542 | 540 |

### Actual KEM-Path Components: `gt_keygen_all_cq_shared_core_direct_cq`

| Group | Kind | Component | Count | KPQC cycles | GT production cycles | Candidate cycles | Candidate vs GT | Candidate vs KPQC | KPQC instr | GT instr | Candidate instr |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| KEYGEN | path | keygen_shake256_sample | 2 | 2722 | 2719 | 2721 | +2 (+0.07%) | -1 (-0.04%) | 8857 | 8857 | 8857 |
| KEYGEN | path | keygen_poly_cbd1_secret | 2 | 303 | 303 | 302 | -1 (-0.33%) | -1 (-0.33%) | 501 | 501 | 501 |
| KEYGEN | path | keygen_sample_ntt_f | 1 | 3642 | 3301 | 2849 | -452 (-13.69%) | -793 (-21.77%) | 3461 | 5572 | 3933 |
| KEYGEN | path | keygen_sample_ntt_g | 1 | 3637 | 3306 | 2867 | -439 (-13.28%) | -770 (-21.17%) | 3456 | 5569 | 3930 |
| KEYGEN | path | keygen_baseinv_actual | 2 | 4056 | 4044 | 3946 | -98 (-2.42%) | -110 (-2.71%) | 4300 | 4312 | 4039 |
| KEYGEN | path | keygen_basemul_actual | 2 | 2641 | 1662 | 1762 | +100 (+6.02%) | -879 (-33.28%) | 2491 | 2319 | 2037 |
| KEYGEN | combined | keygen_baseinv_plus_basemul_contract | 2 | 6694 | 5705 | 5708 | +3 (+0.05%) | -986 (-14.73%) | 6787 | 6629 | 6073 |
| KEYGEN | path | keygen_poly_tobytes_public | 1 | 458 | 566 | 568 | +2 (+0.35%) | +110 (+24.02%) | 784 | 1202 | 1200 |
| KEYGEN | path | keygen_poly_tobytes_secret_f | 1 | 458 | 605 | 568 | -37 (-6.12%) | +110 (+24.02%) | 784 | 1321 | 1200 |
| KEYGEN | path | keygen_poly_tobytes_secret_hinv | 1 | 458 | 568 | 568 | +0 (+0.00%) | +110 (+24.02%) | 784 | 1203 | 1200 |
| KEYGEN | path | keygen_hash_f_pk | 1 | 11886 | 11857 | 11883 | +26 (+0.22%) | -3 (-0.03%) | 39329 | 39329 | 39329 |
| ENCAP | path | enc_hash_f_pk | 1 | 11886 | 11857 | 11884 | +27 (+0.23%) | -2 (-0.02%) | 39329 | 39329 | 39329 |
| ENCAP | path | enc_hash_h_msg | 1 | 2739 | 2738 | 2737 | -1 (-0.04%) | -2 (-0.07%) | 8889 | 8889 | 8887 |
| ENCAP | path | enc_poly_cbd1_r | 1 | 303 | 303 | 302 | -1 (-0.33%) | -1 (-0.33%) | 503 | 503 | 501 |
| ENCAP | path | enc_poly_ntt_r | 1 | 3458 | 2594 | 2596 | +2 (+0.08%) | -862 (-24.93%) | 3261 | 3704 | 3710 |
| ENCAP | path | enc_poly_tobytes_r | 1 | 458 | 616 | 612 | -4 (-0.65%) | +154 (+33.62%) | 784 | 1369 | 1367 |
| ENCAP | path | enc_hash_g_polybytes | 1 | 13143 | 13109 | 13126 | +17 (+0.13%) | -17 (-0.13%) | 43518 | 43518 | 43516 |
| ENCAP | path | enc_poly_sotp_encode | 1 | 323 | 316 | 315 | -1 (-0.32%) | -8 (-2.48%) | 524 | 524 | 521 |
| ENCAP | path | enc_poly_ntt_m | 1 | 3441 | 2588 | 2596 | +8 (+0.31%) | -845 (-24.56%) | 3263 | 3706 | 3710 |
| ENCAP | path | enc_poly_frombytes_pk | 1 | 326 | 489 | 487 | -2 (-0.41%) | +161 (+49.39%) | 566 | 1105 | 1103 |
| ENCAP | path | enc_basemul_add_actual | 1 | 2569 | 2287 | 2285 | -2 (-0.09%) | -284 (-11.05%) | 2612 | 2216 | 2214 |
| ENCAP | path | enc_poly_tobytes_ct | 1 | 458 | 616 | 612 | -4 (-0.65%) | +154 (+33.62%) | 784 | 1369 | 1367 |
| ENCAP | combined | enc_basemul_add_plus_pack | 1 | 3027 | 2900 | 2899 | -1 (-0.03%) | -128 (-4.23%) | 3392 | 3581 | 3578 |
| DECAP | path | dec_poly_frombytes | 2 | 327 | 489 | 487 | -2 (-0.41%) | +160 (+48.93%) | 568 | 1105 | 1103 |
| DECAP | path | dec_first_basemul_actual | 1 | 2641 | 2020 | 2019 | -1 (-0.05%) | -622 (-23.55%) | 2489 | 1917 | 1914 |
| DECAP | path | dec_first_invntt_actual | 1 | 3952 | 3555 | 3558 | +3 (+0.08%) | -394 (-9.97%) | 3470 | 4821 | 4819 |
| DECAP | combined | dec_first_basemul_plus_invntt | 1 | 6594 | 5575 | 5575 | +0 (+0.00%) | -1019 (-15.45%) | 5955 | 6734 | 6730 |
| DECAP | path | dec_poly_crepmod3 | 1 | 400 | 384 | 384 | +0 (+0.00%) | -16 (-4.00%) | 400 | 400 | 398 |
| DECAP | path | dec_poly_ntt_m1 | 1 | 3441 | 2588 | 2596 | +8 (+0.31%) | -845 (-24.56%) | 3263 | 3706 | 3710 |
| DECAP | path | dec_poly_sub | 1 | 173 | 173 | 172 | -1 (-0.58%) | -1 (-0.58%) | 225 | 225 | 222 |
| DECAP | diagnostic | dec_verify_generic_basemul | 1 | 2641 | 2813 | 2813 | +0 (+0.00%) | +172 (+6.51%) | 2487 | 2489 | 2490 |
| DECAP | diagnostic | dec_verify_generic_pack | 1 | 458 | 616 | 612 | -4 (-0.65%) | +154 (+33.62%) | 784 | 1369 | 1367 |
| DECAP | path | dec_verify_product_to_bytes_actual | 1 | 3425 | 3282 | 3282 | +0 (+0.00%) | -143 (-4.18%) | 3831 | 4260 | 4256 |
| DECAP | path | dec_hash_g_polybytes | 1 | 13142 | 13110 | 13127 | +17 (+0.13%) | -15 (-0.11%) | 43518 | 43518 | 43516 |
| DECAP | path | dec_poly_sotp_decode | 1 | 308 | 308 | 310 | +2 (+0.65%) | +2 (+0.65%) | 543 | 543 | 540 |
| DECAP | path | dec_hash_h_msg | 1 | 2738 | 2736 | 2738 | +2 (+0.07%) | +0 (+0.00%) | 8889 | 8889 | 8887 |
| DECAP | path | dec_poly_cbd1_r1 | 1 | 303 | 303 | 302 | -1 (-0.33%) | -1 (-0.33%) | 503 | 503 | 501 |
| DECAP | path | dec_poly_ntt_r1 | 1 | 3458 | 2594 | 2596 | +2 (+0.08%) | -862 (-24.93%) | 3261 | 3704 | 3710 |
| DECAP | path | dec_poly_tobytes_r1 | 1 | 458 | 613 | 612 | -1 (-0.16%) | +154 (+33.62%) | 781 | 1366 | 1367 |
| DECAP | path | dec_verify_polybytes | 1 | 150 | 150 | 150 | +0 (+0.00%) | +0 (+0.00%) | 532 | 532 | 533 |

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
| gt_production_default | kernel_components | 194a296c8c67 | 175018 | gt_decap_verify_to_bytes | 92 | 0/32 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/0 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_tobytes_gt_canonical_p1 | 5264 | 0/0 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 16/16 |
|  |  |  |  | poly_frombytes | 12 | 8/40 |
|  |  |  |  | poly_tobytes | 12 | 16/48 |
|  |  |  |  | poly_ntt | 14776 | 16/48 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 0/32 |
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
|  |  |  |  | poly_baseinv_gt_batch | 16 | 12/44 |
|  |  |  |  | poly_baseinv_gt_batch_scaled_r | 16 | 0/0 |
|  |  |  |  | poly_baseinv | 16 | 0/32 |
|  |  |  |  | poly_baseinv_scaled_r | 2008 | 0/0 |
|  |  |  |  | baseinv_batch_finish24_n1_asm | 32 | 0/32 |
|  |  |  |  | poly_basemul | 20 | 0/0 |
|  |  |  |  | poly_basemul_add | 20 | 16/16 |
|  |  |  |  | poly_basemul_add32 | 20 | 16/16 |
|  |  |  |  | poly_basemul_scaled_r_input | 20 | 16/16 |
| gt_production_default | kem_components | df5d645181a6 | 179866 | gt_decap_verify_to_bytes | 92 | 0/0 |
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
| gt_production_default | kem_keygen | e9fe763d17df | 107590 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | poly_ntt | 14776 | 0/32 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 16/16 |
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
| gt_production_default | kem_enc | 01fd36cc2ea7 | 107574 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | poly_ntt | 14776 | 0/32 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 16/16 |
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
| gt_production_default | kem_dec | d77b246e8054 | 107574 | gt_decap_verify_to_bytes | 92 | 0/0 |
|  |  |  |  | gt_decap_verify_pointwise | 28 | 0/32 |
|  |  |  |  | poly_tobytes_gt_canonical | 5440 | 16/48 |
|  |  |  |  | poly_frombytes_gt_canonical_u1 | 4400 | 0/0 |
|  |  |  |  | poly_frombytes | 12 | 24/24 |
|  |  |  |  | poly_tobytes | 12 | 0/32 |
|  |  |  |  | poly_ntt | 14776 | 0/32 |
|  |  |  |  | gt_ntt32_batch8_to_blockmajor | 16 | 16/16 |
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
| gt_keygen_all_cq_shared_core_direct_cq | kernel_components | b54ec2b56598 | 145182 | gt_decap_verify_to_bytes | 92 | 0/0 |
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
| gt_keygen_all_cq_shared_core_direct_cq | kem_components | dafb39421419 | 146086 | gt_decap_verify_to_bytes | 92 | 0/32 |
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
| gt_keygen_all_cq_shared_core_direct_cq | kem_keygen | b90d2f64e5f8 | 92794 | gt_decap_verify_to_bytes | 92 | 0/0 |
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
| gt_keygen_all_cq_shared_core_direct_cq | kem_enc | 9a64b7d24310 | 92778 | gt_decap_verify_to_bytes | 92 | 0/0 |
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
| gt_keygen_all_cq_shared_core_direct_cq | kem_dec | 125b150454ab | 92778 | gt_decap_verify_to_bytes | 92 | 0/0 |
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
| kpqc_final | kernel_components | 4391cbabebc3 | 45001 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_components | 8c6a7eac70ec | 50001 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_keygen | c8af8de70dbc | 37166 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_enc | 1485c97aa9bd | 37166 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
| kpqc_final | kem_dec | bf1c4505f5d5 | 37166 | poly_baseinv | 952 | 0/32 |
|  |  |  |  | poly_frombytes | 12 | 0/0 |
|  |  |  |  | poly_tobytes | 12 | 8/8 |
|  |  |  |  | poly_ntt | 12 | 16/16 |
|  |  |  |  | poly_invntt | 8 | 24/56 |
|  |  |  |  | poly_basemul | 12 | 0/32 |
|  |  |  |  | poly_basemul_add | 12 | 12/12 |
|  |  |  |  | poly_baseinv_1 | 12 | 12/12 |
