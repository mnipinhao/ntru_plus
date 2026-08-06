#ifndef NTRUPLUS_GT32_TILE4_H
#define NTRUPLUS_GT32_TILE4_H

#include <stdint.h>

#define GT32_TILE4_Q 3457
#define GT32_TILE4_WORDS 128
#define GT32_TILE4_TILES 6
#define GT32_TILE4_POLY_WORDS (GT32_TILE4_WORDS * GT32_TILE4_TILES)
#define GT32_TILE4_SERIALIZED_BYTES 1152

/* Correctness-first P1 unpackers; inputs and outputs must be disjoint. */
int gt32_tile4_frombytes_aos_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_tile4_frombytes_bm_soa_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_tile4_frombytes_aos_official_bridge(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_tile4_frombytes_bm_soa_official_bridge(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_tile4_frombytes_aos_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
/* P1-V control: direct AoS decoder followed by an in-place SoA transpose. */
int gt32_tile4_frombytes_bm_soa_aos_control_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);

/* Native quartic multiplication: TILE4 e=0 x e=0 -> TILE4 e=-1. */
void gt32_tile4_basemul_b0(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_b1(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* A1 gate: direct AoS vpmaddwd accumulation, e=0 x e=0 -> e=-1. */
void gt32_tile4_basemul_wide_a1_intrinsic(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_k1_intrinsic(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_k2_intrinsic(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_k2_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Register-transpose assembly candidate.  Distinct buffers are required. */
void gt32_tile4_basemul_b2_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* B3 late-finalizer ablation.  Distinct buffers are required. */
void gt32_tile4_basemul_b3_late_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* B4b partial-qinv-hoist, multi-accumulator schoolbook ablation. */
void gt32_tile4_basemul_b4b_partial_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* General NTT ABI: TILE4 e=0 x e=0 -> TILE4 e=0, distinct buffers. */
void gt32_tile4_basemul_general_b2_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Decap-only bridge: TILE4 e=0 x e=0 -> private coefficient planes e=-1. */
void gt32_tile4_basemul_scale_soa_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only raw e=-1 SoA producer; only validated private consumers. */
void gt32_tile4_basemul_raw_soa_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Decap-only lazy candidate: TILE4 e=0 x e=0 -> raw TILE4 e=-1. */
void gt32_tile4_basemul_raw_aos_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/*
 * Decap-only proof-safe lazy AoS for N5 output: c0..c2 raw, only the SoA
 * c3 plane is centered.  Inputs outside the generated N5 range contract are
 * unsupported; this leaf performs no runtime range or alias validation.
 */
void gt32_tile4_basemul_c3center_aos_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_c3center_late_aos_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* P1 mixed island: private BM SoA e=0 x TILE4 AoS e=0 -> lazy AoS e=-1. */
void gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_aos[GT32_TILE4_POLY_WORDS]);

/* Benchmark-only basemul attribution leaves; never used by production KEM. */
void gt32_tile4_attr_empty_asm(int16_t *out, const int16_t *a,
	const int16_t *b);
void gt32_tile4_attr_transpose_one_asm(int16_t *out, const int16_t *in);
void gt32_tile4_attr_transpose_two_asm(int16_t *out_a, int16_t *out_b,
	const int16_t *in_a, const int16_t *in_b);
void gt32_tile4_attr_transpose_three_asm(int16_t *out_a, int16_t *out_b,
	int16_t *out_c, const int16_t *in_a, const int16_t *in_b,
	const int16_t *in_c);
void gt32_tile4_attr_basemul_raw_soa_asm(int16_t *out,
	const int16_t *a_soa, const int16_t *b_soa);
void gt32_tile4_attr_basemul_c3_soa_asm(int16_t *out,
	const int16_t *a_soa, const int16_t *b_soa);
void gt32_tile4_attr_center_c3_soa_asm(int16_t *out, const int16_t *in);
void gt32_tile4_attr_basemul_i1_stage01_fused_asm(int16_t *out,
	const int16_t *a_aos, const int16_t *b_aos);
void gt32_tile4_attr_inverse_i1_cross3_asm(int16_t *out,
	const int16_t *post_stage1);

void gt32_tile4_frontend_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_intrinsic(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Low-level frontend requires disjoint input/output regions. */
void gt32_tile4_frontend_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Raw top split requires every input coefficient to be in [-3,4]. */
void gt32_tile4_frontend_raw_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_fixed_raw_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_wide_raw_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

/*
 * One tile is one (k3, branch) and four quartic coefficients:
 *   vector = Q / 4, lane = 4 * (Q % 4) + coefficient.
 * Input Q is natural order; forward output Q is bit-reversed frequency order.
 */
void gt32_tile4_forward_tile_ref(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_inverse_tile_ref(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_forward_all_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* D2a oracle: private coefficient planes e=-1 -> same private layout e=-1. */
void gt32_tile4_inverse_soa_private_ref(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_soa_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_soa_private_parallel_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_tail_ref_e0(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_tail_ref_rminus1(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_tail_intrinsic_rminus1(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* AoS e=-1 -> coefficient order e=0; input and output must be disjoint. */
void gt32_tile4_inverse_tail_asm_rminus1(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_tail_t1_relaxed_asm(int16_t *out, const int16_t *in);
void gt32_tile4_inverse_tail_t2_one_mont_asm(int16_t *out, const int16_t *in);
void gt32_tile4_inverse_tail_t3_reduced_center_asm(int16_t *out, const int16_t *in);
void gt32_tile4_inverse_tail_t3_relaxed_control_asm(int16_t *out,
	const int16_t *in);
void gt32_tile4_inverse_tail_t4_matrix3_asm(int16_t *out, const int16_t *in);
/* Decapsulation-only: bounded mod-q representative for immediate crepmod3. */
void gt32_tile4_inverse_tail_champion_private_asm(int16_t *out,
	const int16_t *in);
void gt32_tile4_inverse_tail_t5_private_asm(int16_t *out, const int16_t *in);
void gt32_tile4_inverse_tail_t6_dual_private_asm(int16_t *out,
	const int16_t *in);
void gt32_tile4_inverse_tail_t7_triple_private_asm(int16_t *out,
	const int16_t *in);
void gt32_tile4_inverse_tail_t8_renamed_private_asm(int16_t *out,
	const int16_t *in);
/* Decapsulation-only fused inverse tail and crepmod3; output is ternary. */
void gt32_tile4_inverse_tail_t10_crepmod3_asm(int16_t *out,
	const int16_t *in);
void gt32_tile4_inverse_tail_t9_isolated_private_asm(int16_t *out,
	const int16_t *in);

void gt32_tile4_forward_tile_asm(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_inverse_tile_asm(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_forward_all_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_all_serial_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_all_parallel_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_all_pair_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_pair_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_pair_selective_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

/* Full coefficient-order input -> TILE4 bit-reversed frequency output. */
void gt32_tile4_forward_full_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_candidate(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Small-input-only combined candidate; supports out == in. */
void gt32_tile4_forward_full_fixed_pair_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_fixed_pair_wide_load_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_wide_raw_pair_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_wide_raw_pair_align32_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_wide_raw_pair_align64_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

#endif
