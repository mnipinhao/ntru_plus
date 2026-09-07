# R0 source/object/reference inventory

Baseline: `d598969f830090de33ca9cc2462e102b668e437e`.

This is a conservative inventory, not authorization to delete uncalled symbols.
Object undefined references, local textual references and linked root membership are distinct.
The ABI fixture deliberately retains more symbols than the three KEM roots.

## Path map (32 files; no functions renamed)

| Before | After |
|---|---|
| `NO_CE/fips202.c` | `fips202.c` |
| `NO_CE/fips202.h` | `fips202.h` |
| `asm/base.S` | `base.S` |
| `asm/cbd.S` | `cbd.S` |
| `asm/internal/decap_add.S` | `decap_add.S` |
| `asm/internal/decap_base.S` | `decap_base.S` |
| `asm/internal/decap_forward.S` | `decap_forward.S` |
| `asm/internal/decap_ntt.S` | `decap_ntt.S` |
| `asm/internal/decap_pack.S` | `decap_pack.S` |
| `asm/internal/decap_packed64.S` | `decap_packed64.S` |
| `asm/internal/decap_verify.S` | `decap_verify.S` |
| `asm/internal/encap_muladd.S` | `encap_muladd.S` |
| `asm/internal/fqinv.S` | `fqinv.S` |
| `asm/internal/keygen_baseinv_finish.S` | `keygen_baseinv_finish.S` |
| `asm/internal/keygen_baseinv_prepare.S` | `keygen_baseinv_prepare.S` |
| `asm/internal/keygen_baseinv_tree.S` | `keygen_baseinv_tree.S` |
| `asm/internal/keygen_pack.S` | `keygen_pack.S` |
| `asm/internal/unpack.S` | `unpack.S` |
| `asm/invntt.S` | `invntt.S` |
| `asm/kem_api.S` | `kem_api.S` |
| `asm/ntt.S` | `ntt.S` |
| `asm/pack.S` | `pack.S` |
| `asm/support.S` | `support.S` |
| `internal/basemul_lambda.c` | `basemul_lambda.c` |
| `internal/decap_verify.c` | `decap_verify.c` |
| `internal/decap_verify.h` | `decap_verify.h` |
| `internal/keygen.c` | `keygen.c` |
| `internal/keygen.h` | `keygen.h` |
| `internal/keygen_lambda.c` | `keygen_lambda.c` |
| `internal/layout.h` | `layout.h` |
| `internal/ntt.h` | `ntt_internal.h` |
| `internal/secure_clear.h` | `secure_clear.h` |

## Ordered 28-unit source closure

Definitions include weak aliases; names beginning `_` are retained platform aliases.
Undefined names are per-object dependencies, not unresolved final-link failures.

### 00: `kem.c` → `kem.c`

- Exported definitions: `crypto_kem_dec_internal` (T), `crypto_kem_enc_internal` (T), `crypto_kem_keypair_internal` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `explicit_bzero`, `gt_decap_checked_ct_f_basemul_scale64`, `gt_decap_poly_basemul`, `gt_decap_poly_frombytes`, `gt_decap_poly_invntt_scale`, `gt_decap_poly_ntt`, `gt_decap_poly_sub`, `gt_decap_poly_tobytes`, `gt_internal_poly_ntt_encap_small`, `gt_internal_poly_tobytes_from_loose`, `gt_keygen_baseinv_cq_to_cq_scaled_r`, `gt_keygen_basemul_cq_cq_to_cq_scaled_r`, `gt_keygen_poly_ntt_to_cq`, `gt_keygen_tobytes_cq`, `hash_f`, `hash_g`, `hash_h`, `memset`, `poly_basemul_add`, `poly_cbd1`, `poly_crepmod3`, `poly_frombytes`, `poly_sotp_decode`, `poly_sotp_encode`, `poly_tobytes`, `poly_triple`, `randombytes`, `shake256`

### 01: `symmetric.c` → `symmetric.c`

- Exported definitions: `hash_f` (T), `hash_g` (T), `hash_h` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `explicit_bzero`, `memcpy`, `shake256`

### 02: `NO_CE/fips202.c` → `fips202.c`

- Exported definitions: `shake256` (T), `shake256_absorb` (T), `shake256_ctx_clone` (T), `shake256_ctx_release` (T), `shake256_inc_absorb` (T), `shake256_inc_ctx_clone` (T), `shake256_inc_ctx_release` (T), `shake256_inc_finalize` (T), `shake256_inc_init` (T), `shake256_inc_squeeze` (T), `shake256_squeezeblocks` (T)
- Named data symbols: `KeccakF_RoundConstants`
- Undefined references: `explicit_bzero`, `memcpy`

### 03: `internal/keygen.c` → `keygen.c`

- Exported definitions: `gt_keygen_baseinv_cq_to_cq_scaled_r` (T), `gt_keygen_basemul_cq_cq_to_cq_scaled_r` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `explicit_bzero`, `gt_keygen_baseinv_cq_finish`, `gt_keygen_baseinv_cq_prepare`, `gt_keygen_baseinv_hier_k8`, `gt_keygen_bpq_lambda8`, `memset`

### 04: `internal/keygen_lambda.c` → `keygen_lambda.c`

- Exported definitions: `gt_keygen_bpq_lambda8` (R)
- Named data symbols: `gt_keygen_bpq_lambda8`
- Undefined references: (none)

### 05: `internal/basemul_lambda.c` → `basemul_lambda.c`

- Exported definitions: `gt_rowbitrev_lambda` (R)
- Named data symbols: `gt_rowbitrev_lambda`
- Undefined references: (none)

### 06: `internal/decap_verify.c` → `decap_verify.c`

- Exported definitions: `gt_decap_verify_predecoded_qsoa_to_bytes` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `gt_decap_verify_pointwise`, `qsoa_tobytes`

### 07: `asm/ntt.S` → `ntt.S`

- Exported definitions: `_gt_internal_block_major_poly_ntt_loose` (T), `_gt_internal_poly_ntt_encap_small` (T), `_gt_internal_poly_ntt_loose` (T), `_gt_keygen_poly_ntt_to_cq` (T), `gt_internal_block_major_poly_ntt_loose` (T), `gt_internal_poly_ntt_encap_small` (T), `gt_internal_poly_ntt_loose` (T), `gt_internal_poly_ntt_loose_end` (T), `gt_keygen_poly_ntt_to_cq` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 08: `asm/invntt.S` → `invntt.S`

- Exported definitions: `_gt_block_major_poly_invntt` (T), `_poly_invntt` (W), `gt_block_major_poly_invntt` (T), `poly_invntt` (W)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 09: `asm/base.S` → `base.S`

- Exported definitions: `_poly_basemul` (T), `poly_basemul` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `gt_rowbitrev_lambda`

### 10: `asm/pack.S` → `pack.S`

- Exported definitions: `_gt_internal_poly_tobytes_from_loose` (T), `_poly_tobytes` (T), `gt_internal_poly_tobytes_from_loose` (T), `poly_tobytes` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 11: `asm/cbd.S` → `cbd.S`

- Exported definitions: `_poly_cbd1` (T), `_poly_sotp_decode` (T), `_poly_sotp_encode` (T), `poly_cbd1` (T), `poly_sotp_decode` (T), `poly_sotp_encode` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 12: `asm/support.S` → `support.S`

- Exported definitions: `_poly_crepmod3` (T), `_poly_sub` (T), `_poly_triple` (T), `_qsoa_frombytes` (T), `_qsoa_tobytes` (T), `poly_crepmod3` (T), `poly_sub` (T), `poly_triple` (T), `qsoa_frombytes` (T), `qsoa_tobytes` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 13: `asm/kem_api.S` → `kem_api.S`

- Exported definitions: `crypto_kem_dec` (T), `crypto_kem_enc` (T), `crypto_kem_keypair` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `crypto_kem_dec_internal`, `crypto_kem_enc_internal`, `crypto_kem_keypair_internal`

### 14: `asm/internal/unpack.S` → `unpack.S`

- Exported definitions: `_poly_frombytes` (T), `poly_frombytes` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 15: `asm/internal/keygen_baseinv_prepare.S` → `keygen_baseinv_prepare.S`

- Exported definitions: `gt_keygen_baseinv_cq_prepare` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `gt_keygen_bpq_lambda8`

### 16: `asm/internal/keygen_baseinv_tree.S` → `keygen_baseinv_tree.S`

- Exported definitions: `gt_keygen_baseinv_hier_k8` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `gt_fqinv15_asm`

### 17: `asm/internal/keygen_baseinv_finish.S` → `keygen_baseinv_finish.S`

- Exported definitions: `gt_keygen_baseinv_cq_finish` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 18: `asm/internal/keygen_pack.S` → `keygen_pack.S`

- Exported definitions: `_gt_keygen_tobytes_cq` (T), `gt_keygen_tobytes_cq` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 19: `asm/internal/fqinv.S` → `fqinv.S`

- Exported definitions: `gt_fqinv15_asm` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 20: `asm/internal/encap_muladd.S` → `encap_muladd.S`

- Exported definitions: `_poly_basemul_add` (T), `poly_basemul_add` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: `gt_rowbitrev_lambda`

### 21: `asm/internal/decap_verify.S` → `decap_verify.S`

- Exported definitions: `_gt_decap_verify_pointwise` (T), `gt_decap_verify_pointwise` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 22: `asm/internal/decap_packed64.S` → `decap_packed64.S`

- Exported definitions: `gt_decap_checked_ct_f_basemul_scale64` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 23: `asm/internal/decap_add.S` → `decap_add.S`

- Exported definitions: `_gt_decap_poly_sub` (T), `_gt_decap_poly_triple` (T), `gt_decap_poly_sub` (T), `gt_decap_poly_triple` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 24: `asm/internal/decap_base.S` → `decap_base.S`

- Exported definitions: `_gt_decap_poly_baseinv_1` (T), `_gt_decap_poly_basemul` (T), `_gt_decap_poly_basemul_add` (T), `_gt_decap_poly_basemul_scale` (T), `gt_decap_poly_baseinv_1` (T), `gt_decap_poly_basemul` (T), `gt_decap_poly_basemul_add` (T), `gt_decap_poly_basemul_scale` (T)
- Named data symbols: `zetas_mul`
- Undefined references: (none)

### 25: `asm/internal/decap_ntt.S` → `decap_ntt.S`

- Exported definitions: `_gt_decap_poly_invntt_scale` (T), `_gt_decap_reference_poly_ntt` (T), `gt_decap_poly_invntt_scale` (T), `gt_decap_reference_poly_ntt` (T)
- Named data symbols: `zetas`, `zetas_inv`
- Undefined references: (none)

### 26: `asm/internal/decap_pack.S` → `decap_pack.S`

- Exported definitions: `_gt_decap_poly_frombytes` (T), `_gt_decap_poly_tobytes` (T), `gt_decap_poly_frombytes` (T), `gt_decap_poly_tobytes` (T)
- Named data symbols: (none; inline .text tables are indexed below)
- Undefined references: (none)

### 27: `asm/internal/decap_forward.S` → `decap_forward.S`

- Exported definitions: `_gt_decap_gt_poly_ntt` (T), `_gt_decap_poly_ntt` (T), `gt_decap_gt_poly_ntt` (T), `gt_decap_poly_ntt` (T), `gt_decap_poly_ntt_end` (T)
- Named data symbols: `joint_frontend_twist_table`, `joint_stage12_packed_table`, `joint_stage345_decap_row_tables`, `u01_block_first_gt_ntt32_batch8_twiddle_vecs`, `u01_block_first_twist_table`, `u01_block_first_zetas`
- Undefined references: (none)

## Explicit local assembly label/reference index

Includes code labels and inline data labels: do not assume symbol type `t` means code.
Line numbers refer to the baseline source; all assembly bytes are unchanged.
Macro-expanded/generated assembler labels are additionally captured by the object symbol/relocation audit.

| Source | Label | Definition line | Same-file textual reference lines |
|---|---|---:|---|
| `kem.c` | `cleanup` | 363 | 333 |
| `asm/ntt.S` | `gt_internal_poly_ntt_loose` | 23 | 16, 21, 6797 |
| `asm/ntt.S` | `_gt_internal_poly_ntt_loose` | 24 | 17 |
| `asm/ntt.S` | `gt_internal_block_major_poly_ntt_loose` | 25 | 18 |
| `asm/ntt.S` | `_gt_internal_block_major_poly_ntt_loose` | 26 | 19 |
| `asm/ntt.S` | `gt_keygen_poly_ntt_to_cq` | 35 | 30, 33, 6798 |
| `asm/ntt.S` | `_gt_keygen_poly_ntt_to_cq` | 36 | 31 |
| `asm/ntt.S` | `.Lgt_shared_core_entry` | 38 | 28, 7033 |
| `asm/ntt.S` | `.Lntt_endpoint_suffix` | 1378 | 8250 |
| `asm/ntt.S` | `.Lgt_shared_core_generic_suffix` | 1382 |  |
| `asm/ntt.S` | `.Lgt_shared_core_cq_suffix` | 4042 | 1381 |
| `asm/ntt.S` | `.Lgt_shared_core_epilogue` | 6785 | 4041 |
| `asm/ntt.S` | `.Lgt_shared_core_end` | 6795 | 6797, 6798 |
| `asm/ntt.S` | `gt_internal_poly_ntt_loose_end` | 6801 | 6800 |
| `asm/ntt.S` | `u01_block_first_zetas` | 6807 | 53 |
| `asm/ntt.S` | `u01_block_first_twist_table` | 6811 | 55 |
| `asm/ntt.S` | `u01_block_first_gt_ntt32_batch8_twiddle_vecs` | 7006 | 56 |
| `asm/ntt.S` | `gt_internal_poly_ntt_encap_small` | 7030 | 7025, 7028 |
| `asm/ntt.S` | `_gt_internal_poly_ntt_encap_small` | 7031 | 7026 |
| `asm/ntt.S` | `.Lencap_small_front` | 7034 | 66 |
| `asm/invntt.S` | `poly_invntt` | 638 | 630, 633 |
| `asm/invntt.S` | `_poly_invntt` | 639 | 631, 634 |
| `asm/invntt.S` | `gt_block_major_poly_invntt` | 640 | 635 |
| `asm/invntt.S` | `_gt_block_major_poly_invntt` | 641 | 636 |
| `asm/invntt.S` | `L_invntt_post_tail` | 687 | 685 |
| `asm/invntt.S` | `.Linvntt32_stage45_scratch_row_helper` | 708 | 660, 672, 684 |
| `asm/invntt.S` | `inv_consts` | 713 | 646, 688 |
| `asm/invntt.S` | `invntt32_stage123_consts` | 718 | 108 |
| `asm/invntt.S` | `invntt32_stage45_consts` | 723 | 165 |
| `asm/invntt.S` | `inv_branchfold_vecs` | 752 | 694 |
| `asm/base.S` | `GT_RMINUS1_PAIR_SYMBOL` | 19 | 15, 17 |
| `asm/base.S` | `GT_RMINUS1_PAIR_DARWIN_SYMBOL` | 20 | 16, 18 |
| `asm/base.S` | `.Lrminus1_pair_production_loop` | 31 | 189 |
| `asm/base.S` | `.Lrminus1_pair_slothy_start` | 32 |  |
| `asm/base.S` | `.Lrminus1_pair_slothy_end` | 187 |  |
| `asm/base.S` | `.Lrminus1_pair_consts` | 197 | 26 |
| `asm/pack.S` | `gt_internal_poly_tobytes_from_loose` | 19 | 14, 17 |
| `asm/pack.S` | `_gt_internal_poly_tobytes_from_loose` | 20 | 15 |
| `asm/pack.S` | `poly_tobytes` | 23 | 3, 9, 12, 479 |
| `asm/pack.S` | `_poly_tobytes` | 24 | 10 |
| `asm/pack.S` | `.Lwave8_dual_pack_entry` | 26 | 22 |
| `asm/pack.S` | `.Lcanonical_pack_compact_core` | 356 | 60, 86, 112, 138, 164, 190, 216, 242, 268, 294, 320, 346 |
| `asm/pack.S` | `.Lwave8_pack_already_reduced` | 384 | 358 |
| `asm/pack.S` | `.Lcanonical_pack_compact_q` | 472 | 33 |
| `asm/cbd.S` | `poly_cbd1` | 3 | 1 |
| `asm/cbd.S` | `_poly_cbd1` | 4 | 2 |
| `asm/cbd.S` | `_loop_cbd` | 15 | 124 |
| `asm/cbd.S` | `poly_sotp_encode` | 134 | 132 |
| `asm/cbd.S` | `_poly_sotp_encode` | 135 | 133 |
| `asm/cbd.S` | `_loop_sotp_encode` | 147 | 261 |
| `asm/cbd.S` | `poly_sotp_decode` | 273 | 271 |
| `asm/cbd.S` | `_poly_sotp_decode` | 274 | 272 |
| `asm/cbd.S` | `_loop_sotp_decode` | 290 | 409 |
| `asm/support.S` | `poly_sub` | 10 | 8 |
| `asm/support.S` | `_poly_sub` | 11 | 9 |
| `asm/support.S` | `_support_loop_sub` | 15 | 48 |
| `asm/support.S` | `poly_triple` | 53 | 51 |
| `asm/support.S` | `_poly_triple` | 54 | 52 |
| `asm/support.S` | `_support_loop_triple` | 59 | 89 |
| `asm/support.S` | `poly_crepmod3` | 94 | 92 |
| `asm/support.S` | `_poly_crepmod3` | 95 | 93 |
| `asm/support.S` | `_support_loop_crepmod3` | 101 | 124 |
| `asm/support.S` | `qsoa_frombytes` | 129 | 127 |
| `asm/support.S` | `_qsoa_frombytes` | 130 | 128 |
| `asm/support.S` | `_support_loop_frombytes` | 145 | 206 |
| `asm/support.S` | `qsoa_tobytes` | 222 | 220 |
| `asm/support.S` | `_qsoa_tobytes` | 223 | 221 |
| `asm/support.S` | `_support_loop_tobytes` | 229 | 301 |
| `asm/support.S` | `support_const_mask_0fff` | 305 | 136 |
| `asm/support.S` | `support_const_q` | 310 | 224 |
| `asm/internal/unpack.S` | `poly_frombytes` | 6 | 4 |
| `asm/internal/unpack.S` | `_poly_frombytes` | 7 | 5 |
| `asm/internal/unpack.S` | `.Lcanonical_unpack_candidate_mask` | 1237 | 13 |
| `asm/internal/keygen_baseinv_prepare.S` | `Lgt_keygen_baseinv_cq_prepare_loop` | 55 | 256 |
| `asm/internal/keygen_baseinv_prepare.S` | `Lgt_keygen_baseinv_prepare_constants` | 307 | 48 |
| `asm/internal/keygen_baseinv_tree.S` | `Lbpq_tree_failure` | 187 | 160 |
| `asm/internal/keygen_baseinv_tree.S` | `Lbpq_tree_return` | 190 | 185 |
| `asm/internal/keygen_baseinv_tree.S` | `Lbpq_tree_scaled_r_consts` | 204 | 140, 163 |
| `asm/internal/keygen_baseinv_finish.S` | `Lbpq_finish_cq_loop` | 66 | 78 |
| `asm/internal/keygen_baseinv_finish.S` | `Lbpq_finish_scaled_r_consts` | 86 | 63 |
| `asm/internal/keygen_pack.S` | `gt_keygen_tobytes_cq` | 11 | 9 |
| `asm/internal/keygen_pack.S` | `_gt_keygen_tobytes_cq` | 12 | 10 |
| `asm/internal/keygen_pack.S` | `.Lgt_keygen_shared_pack64_core` | 524 | 62, 103, 144, 185, 226, 267, 308, 349, 390, 431, 472, 513 |
| `asm/internal/keygen_pack.S` | `.Lbpq_cq_pack_indexes` | 588 | 19 |
| `asm/internal/keygen_pack.S` | `.Lbpq_cq_pack_q` | 614 | 20 |
| `asm/internal/encap_muladd.S` | `poly_basemul_add` | 48 | 2, 4, 46 |
| `asm/internal/encap_muladd.S` | `_poly_basemul_add` | 49 | 47 |
| `asm/internal/encap_muladd.S` | `Lpoly_basemul_add_loop` | 61 | 243 |
| `asm/internal/encap_muladd.S` | `Lpoly_basemul_add_consts` | 253 | 57 |
| `asm/internal/decap_verify.S` | `gt_decap_verify_pointwise` | 7 | 5 |
| `asm/internal/decap_verify.S` | `_gt_decap_verify_pointwise` | 8 | 6 |
| `asm/internal/decap_verify.S` | `.Lfused_gather_mul_group` | 578 | 49, 72, 95, 118, 141, 164, 187, 210, 233, 256, 279, 302, 325, 348, 371, 394, 417, 440, 463, 486, 509, 532, 555, 569 |
| `asm/internal/decap_verify.S` | `.Lfused_gather_zetas_mul` | 683 | 16 |
| `asm/internal/decap_packed64.S` | `.Lgt_decap_checked_ct_f_basemul_scale64_loop64` | 198 | 445 |
| `asm/internal/decap_packed64.S` | `.Lgt_decap_zetas_mul` | 465 | 190 |
| `asm/internal/decap_packed64.S` | `.Lgt_decap_mask_0fff` | 493 | 192 |
| `asm/internal/decap_add.S` | `gt_decap_poly_sub` | 9 | 7 |
| `asm/internal/decap_add.S` | `_gt_decap_poly_sub` | 10 | 8 |
| `asm/internal/decap_add.S` | `_loop_sub` | 20 | 49 |
| `asm/internal/decap_add.S` | `gt_decap_poly_triple` | 67 | 65 |
| `asm/internal/decap_add.S` | `_gt_decap_poly_triple` | 68 | 66 |
| `asm/internal/decap_add.S` | `_loop_triple` | 79 | 106 |
| `asm/internal/decap_base.S` | `gt_decap_poly_basemul` | 23 | 2, 21 |
| `asm/internal/decap_base.S` | `_gt_decap_poly_basemul` | 24 | 22 |
| `asm/internal/decap_base.S` | `_looptop` | 45 | 153 |
| `asm/internal/decap_base.S` | `gt_decap_poly_basemul_scale` | 192 | 170, 190 |
| `asm/internal/decap_base.S` | `_gt_decap_poly_basemul_scale` | 193 | 191 |
| `asm/internal/decap_base.S` | `_looptop_scale` | 212 | 313 |
| `asm/internal/decap_base.S` | `gt_decap_poly_basemul_add` | 354 | 330, 352 |
| `asm/internal/decap_base.S` | `_gt_decap_poly_basemul_add` | 355 | 353 |
| `asm/internal/decap_base.S` | `_looptop_add` | 375 | 499 |
| `asm/internal/decap_base.S` | `gt_decap_poly_baseinv_1` | 537 | 517, 535 |
| `asm/internal/decap_base.S` | `_gt_decap_poly_baseinv_1` | 538 | 536 |
| `asm/internal/decap_base.S` | `_looptop_baseinv_1` | 556 | 810 |
| `asm/internal/decap_base.S` | `zetas_mul` | 832 | 36, 205, 368, 550 |
| `asm/internal/decap_base.S` | `.Ldecap_basemul_q31_consts` | 860 | 40 |
| `asm/internal/decap_ntt.S` | `gt_decap_reference_poly_ntt` | 20 | 2, 18 |
| `asm/internal/decap_ntt.S` | `_gt_decap_reference_poly_ntt` | 21 | 19 |
| `asm/internal/decap_ntt.S` | `_looptop_012` | 39 | 247 |
| `asm/internal/decap_ntt.S` | `_looptop_3456` | 254 | 440 |
| `asm/internal/decap_ntt.S` | `gt_decap_poly_invntt_scale` | 475 | 455, 473 |
| `asm/internal/decap_ntt.S` | `_gt_decap_poly_invntt_scale` | 476 | 474 |
| `asm/internal/decap_ntt.S` | `_looptop_6543` | 492 | 663 |
| `asm/internal/decap_ntt.S` | `_looptop_210` | 671 | 959 |
| `asm/internal/decap_ntt.S` | `zetas` | 979 | 33, 494 |
| `asm/internal/decap_ntt.S` | `zetas_inv` | 1039 | 488 |
| `asm/internal/decap_pack.S` | `gt_decap_poly_frombytes` | 15 | 2, 13 |
| `asm/internal/decap_pack.S` | `_gt_decap_poly_frombytes` | 16 | 14 |
| `asm/internal/decap_pack.S` | `_loop_frombytes` | 32 | 89 |
| `asm/internal/decap_pack.S` | `gt_decap_poly_tobytes` | 122 | 109, 120 |
| `asm/internal/decap_pack.S` | `_gt_decap_poly_tobytes` | 123 | 121 |
| `asm/internal/decap_pack.S` | `_loop_tobytes` | 138 | 215 |
| `asm/internal/decap_pack.S` | `const_mask_0fff` | 230 | 26 |
| `asm/internal/decap_pack.S` | `const_q` | 235 | 133 |
| `asm/internal/decap_forward.S` | `gt_decap_poly_ntt` | 16 | 9, 14, 5253 |
| `asm/internal/decap_forward.S` | `_gt_decap_poly_ntt` | 17 | 10 |
| `asm/internal/decap_forward.S` | `gt_decap_gt_poly_ntt` | 18 | 11 |
| `asm/internal/decap_forward.S` | `_gt_decap_gt_poly_ntt` | 19 | 12 |
| `asm/internal/decap_forward.S` | `gt_decap_stage12_row0_slothy_start` | 1368 |  |
| `asm/internal/decap_forward.S` | `wave25_row0_slothy_start` | 1374 |  |
| `asm/internal/decap_forward.S` | `wave25_row0_slothy_end` | 2659 |  |
| `asm/internal/decap_forward.S` | `wave25_row1_slothy_start` | 2665 |  |
| `asm/internal/decap_forward.S` | `wave25_row1_slothy_end` | 3950 |  |
| `asm/internal/decap_forward.S` | `wave25_row2_slothy_start` | 3956 |  |
| `asm/internal/decap_forward.S` | `wave25_row2_slothy_end` | 5241 |  |
| `asm/internal/decap_forward.S` | `gt_decap_stage345_decap_row2_slothy_end` | 5242 |  |
| `asm/internal/decap_forward.S` | `gt_decap_poly_ntt_end` | 5256 | 5255 |
| `asm/internal/decap_forward.S` | `u01_block_first_zetas` | 5269 | 33 |
| `asm/internal/decap_forward.S` | `u01_block_first_twist_table` | 5276 |  |
| `asm/internal/decap_forward.S` | `u01_block_first_gt_ntt32_batch8_twiddle_vecs` | 5474 | 36 |
| `asm/internal/decap_forward.S` | `joint_frontend_twist_table` | 5495 | 35 |
| `asm/internal/decap_forward.S` | `joint_stage12_packed_table` | 5696 | 1365 |
| `asm/internal/decap_forward.S` | `joint_stage345_decap_row_tables` | 5706 | 1366 |

## Linked KEM roots: surviving project symbols

Built with the three public KEM entrypoints rooted by the six-path fixture and `--gc-sections`.
Presence may reflect sharing an indivisible assembly section, not direct call reachability.

```text
0000000000000f20 000000000000018c t crypto_kem_enc_derand
00000000000010c0 00000000000001d0 T crypto_kem_keypair_internal
00000000000012a0 0000000000000060 T crypto_kem_enc_internal
0000000000001300 00000000000001d8 T crypto_kem_dec_internal
00000000000014e0 0000000000000048 T hash_f
0000000000001540 0000000000000058 T hash_g
00000000000015a0 0000000000000060 T hash_h
0000000000002480 0000000000000410 T shake256
00000000000028a0 0000000000000090 T gt_keygen_baseinv_cq_to_cq_scaled_r
0000000000002940 0000000000000174 T gt_keygen_basemul_cq_cq_to_cq_scaled_r
0000000000002ac0 T _gt_internal_block_major_poly_ntt_loose
0000000000002ac0 T _gt_internal_poly_ntt_loose
0000000000002ac0 T gt_internal_block_major_poly_ntt_loose
0000000000002ac0 0000000000005af0 T gt_internal_poly_ntt_loose
0000000000002ac8 T _gt_keygen_poly_ntt_to_cq
0000000000002ac8 0000000000005ae8 T gt_keygen_poly_ntt_to_cq
00000000000085b0 T gt_internal_poly_ntt_loose_end
0000000000009260 T _gt_internal_poly_ntt_encap_small
0000000000009260 T gt_internal_poly_ntt_encap_small
000000000000a510 T _gt_internal_poly_tobytes_from_loose
000000000000a510 T gt_internal_poly_tobytes_from_loose
000000000000a518 T _poly_tobytes
000000000000a518 00000000000006d8 T poly_tobytes
000000000000abf0 T _poly_cbd1
000000000000abf0 T poly_cbd1
000000000000ad48 T _poly_sotp_encode
000000000000ad48 T poly_sotp_encode
000000000000aeac T _poly_sotp_decode
000000000000aeac T poly_sotp_decode
000000000000b040 T _poly_sub
000000000000b040 T poly_sub
000000000000b0b0 T _poly_triple
000000000000b0b0 T poly_triple
000000000000b118 T _poly_crepmod3
000000000000b118 T poly_crepmod3
000000000000b3d0 000000000000003c T crypto_kem_keypair
000000000000b40c 000000000000003c T crypto_kem_enc
000000000000b448 000000000000003c T crypto_kem_dec
000000000000b490 T _poly_frombytes
000000000000b490 T poly_frombytes
000000000000c780 00000000000003dc T gt_keygen_baseinv_cq_prepare
000000000000cb70 00000000000008f8 T gt_keygen_baseinv_hier_k8
000000000000d480 000000000000009c T gt_keygen_baseinv_cq_finish
000000000000d530 T _gt_keygen_tobytes_cq
000000000000d530 T gt_keygen_tobytes_cq
000000000000df60 T gt_fqinv15_asm
000000000000e150 T _poly_basemul_add
000000000000e150 T poly_basemul_add
000000000000e460 000000000000042c T gt_decap_checked_ct_f_basemul_scale64
000000000000ea30 T _gt_decap_poly_sub
000000000000ea30 T gt_decap_poly_sub
000000000000eaa0 T _gt_decap_poly_basemul
000000000000eaa0 T gt_decap_poly_basemul
000000000000ec28 T _gt_decap_poly_invntt_scale
000000000000ec28 T gt_decap_poly_invntt_scale
000000000000f180 T _gt_decap_poly_frombytes
000000000000f180 T gt_decap_poly_frombytes
000000000000f288 T _gt_decap_poly_tobytes
000000000000f288 T gt_decap_poly_tobytes
000000000000f3f0 T _gt_decap_gt_poly_ntt
000000000000f3f0 T _gt_decap_poly_ntt
000000000000f3f0 T gt_decap_gt_poly_ntt
000000000000f3f0 0000000000003218 T gt_decap_poly_ntt
0000000000010854 t gt_decap_stage12_row0_slothy_start
00000000000125e4 t gt_decap_stage345_decap_row2_slothy_end
0000000000012608 T gt_decap_poly_ntt_end
00000000000127d0 0000000000000180 R gt_keygen_bpq_lambda8
0000000000012950 0000000000000180 R gt_rowbitrev_lambda
```

## Relocation reference graph

Cross-object call/jump/data edges are retained in `reference-graph.json`.
Owner names are objdump symbol anchors, not a proof of exact intra-section ownership.
Local PC-relative tables can have no relocation: use the label index above as well.
