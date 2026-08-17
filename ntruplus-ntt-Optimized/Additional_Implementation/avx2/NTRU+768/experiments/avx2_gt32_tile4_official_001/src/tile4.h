#ifndef NTRUPLUS_GT32_TILE4_H
#define NTRUPLUS_GT32_TILE4_H

#include <stdint.h>

#define GT32_TILE4_Q 3457
#define GT32_TILE4_WORDS 128
#define GT32_TILE4_TILES 6
#define GT32_TILE4_POLY_WORDS (GT32_TILE4_WORDS * GT32_TILE4_TILES)
#define GT32_TILE4_SERIALIZED_BYTES 1152

/* Keygen-only typed representations.  These wrappers intentionally prevent
 * an e=1 BaseInv result from entering a generic e=0 consumer by accident. */
typedef struct __attribute__((aligned(32))) {
	int16_t words[GT32_TILE4_POLY_WORDS];
} gt32_f0_aos_e0_t;

typedef struct __attribute__((aligned(32))) {
	int16_t words[GT32_TILE4_POLY_WORDS];
} gt32_baseinv_j1_aos_e1_t;

/* K3-A correctness implementation; fixed-control scalar reference, not a
 * production or performance-selected BaseInv kernel. */
int gt32_tile4_baseinv_j1_aos_ref(gt32_baseinv_j1_aos_e1_t *out,
	const gt32_f0_aos_e0_t *in);
int gt32_tile4_baseinv_j1_aos_avx2(gt32_baseinv_j1_aos_e1_t *out,
	const gt32_f0_aos_e0_t *in);

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
int gt32_q24_decode_aos_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_q24_decode_soa_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_q24_decode3_soa_asm(
	int16_t c[GT32_TILE4_POLY_WORDS],
	int16_t f[GT32_TILE4_POLY_WORDS],
	int16_t hinv[GT32_TILE4_POLY_WORDS], const uint8_t ct[1152],
	const uint8_t sk[2304]);
void gt32_q24_encode_aos_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_q24_encode_soa_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Private BM SoA, e=0, |word| <= 10788 -> Official canonical bytes. */
void gt32_q24_encode_soa_lazy10788_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only: same contract with pair/pack constants register-resident. */
void gt32_q24_encode_soa_lazy10788_rr_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Progressive-P coefficient-plane SoA, e=0, |word| <= 10788. */
void gt32_q24_encode_p_soa_lazy10788_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

/* Encap B3-general + m: private SoA, e=0, |word| <= 12699. */
void gt32_q24_encode_soa_encap_hr_h1_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_q24_encode_soa_encap_hr_h2_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Compare lazy10788 private-SoA directly with canonical bytes; return 0/1. */
int gt32_q24_encode_soa_lazy10788_verify_asm(
	const uint8_t expected[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Private BM SoA e=0 comparison modulo q.  The first operand is bounded by
 * 1911, the second by 10788, hence their signed difference is <= 12699. */
int gt32_tile4_soa_equal_modq_12699_asm(
	const int16_t recovered[GT32_TILE4_POLY_WORDS],
	const int16_t derived[GT32_TILE4_POLY_WORDS]);

/* Benchmark-only Decode(c,f) -> first scale-B3 streaming frontier. */
int gt32_q24_decode2_b3_scale_stream_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t c[GT32_TILE4_SERIALIZED_BYTES],
	const uint8_t f[GT32_TILE4_SERIALIZED_BYTES]);
int gt32_tile4_frombytes_aos_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
/* Correct Official index[192] semantic route directly to private BM SoA. */
int gt32_tile4_frombytes_bm_soa_semantic_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES]);
/* Decapsulation-private c/f/hinv decoder with one rejection accumulator. */
int gt32_tile4_frombytes3_bm_soa_semantic_asm(
	int16_t c[GT32_TILE4_POLY_WORDS],
	int16_t f[GT32_TILE4_POLY_WORDS],
	int16_t hinv[GT32_TILE4_POLY_WORDS],
	const uint8_t ct[GT32_TILE4_SERIALIZED_BYTES],
	const uint8_t sk[2 * GT32_TILE4_SERIALIZED_BYTES]);
/* Benchmark-only: c/f -> AoS for R1-U, hinv -> persistent private SoA. */
int gt32_tile4_frombytes2_aos_1soa_semantic_asm(
	int16_t c_aos[GT32_TILE4_POLY_WORDS],
	int16_t f_aos[GT32_TILE4_POLY_WORDS],
	int16_t hinv_soa[GT32_TILE4_POLY_WORDS],
	const uint8_t ct[GT32_TILE4_SERIALIZED_BYTES],
	const uint8_t sk[2 * GT32_TILE4_SERIALIZED_BYTES]);
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
void gt32_tile4_basemul_wide_r1u_intrinsic(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_wide_r1s_intrinsic(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_aos_dot_r1u_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Serious-qualified typed alias: Forward AoS x Forward AoS -> inverse e=-1. */
void gt32_tile4_basemul_scale_ff_aos_r1u_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_forward_aos[GT32_TILE4_POLY_WORDS],
	const int16_t b_forward_aos[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only B=33 half-native leaf order; e=0 x e=0 -> e=-1. */
void gt32_n32_basemul_half_r1u_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t b_half_native[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only post-twist NTT32 S1-S3 physical scheduling probe. */
void gt32_n32_wave_s1s3_control_asm(int16_t out[256],
	const int16_t in[256]);
void gt32_n32_wave_s1s3_c2_asm(int16_t out[256],
	const int16_t in[256]);
void gt32_n32_branch1_qmem_asm(int16_t out[128], const int16_t in[128]);
void gt32_n32_branch1_qreg_asm(int16_t out[128], const int16_t in[128]);
void gt32_n32_conj_wave_control_asm(int16_t out[256],
	const int16_t in_coefficients[GT32_TILE4_POLY_WORDS]);
void gt32_n32_conj_wave_branch_at_time_asm(int16_t out[256],
	const int16_t in_coefficients[GT32_TILE4_POLY_WORDS]);
void gt32_n32_suffix_route6_control_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_n32_suffix_route5_half_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/*
 * Complete NTT32-first Forward, small coefficient input [-3,4], e=0.
 * The raw symbol is semantic/range attribution only: its representative is
 * not covered by the R1-U/native-inverse proof.  The centered symbol applies
 * one final center10 to all packets; the conjugated symbol below instead
 * centers only residual row 0 and is the production-shaped composable entry.
 * All three symbols support out == in.
 */
void gt32_n32_forward_half_raw_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t in_coefficients[GT32_TILE4_POLY_WORDS]);
void gt32_n32_forward_half_centered_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t in_coefficients[GT32_TILE4_POLY_WORDS]);
/* Proved row-conjugated Forward with the required row-0-only checkpoint. */
void gt32_n32_forward_half_conjugated_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t in_coefficients[GT32_TILE4_POLY_WORDS]);
void gt32_n32_forward_half_conjugated_branch_at_time_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t in_coefficients[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only post-S3 suffix scheduling probes. */
void gt32_n32_suffix_serial_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t post_s3[GT32_TILE4_POLY_WORDS]);
void gt32_n32_suffix_3way_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t post_s3[GT32_TILE4_POLY_WORDS]);
void gt32_n32_suffix_dft_dual_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t post_s3[GT32_TILE4_POLY_WORDS]);
void gt32_n32_suffix_mlkstyle_asm(
	int16_t out_half_native[GT32_TILE4_POLY_WORDS],
	const int16_t post_s3[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_aos_dot_r1s_asm(
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
/* Correct-decoder SS gate: private SoA e=0 x SoA e=0 -> lazy AoS e=-1. */
void gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_soa[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only: private SoA e=0 x SoA e=0 -> private SoA e=-1. */
void gt32_tile4_bm_soa_dot_redc16_asm(
	int16_t out_soa[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_soa[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only Gate C: private SoA e=0 x TILE4 AoS e=0 -> AoS e=0. */
void gt32_tile4_basemul_general_soa_aos_to_aos_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_aos[GT32_TILE4_POLY_WORDS]);
/* SoA-domain decap gate: private SoA e=0 x SoA e=0 -> AoS e=0. */
void gt32_tile4_basemul_general_soa_soa_to_aos_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_soa[GT32_TILE4_POLY_WORDS]);
/* Encodeq island: private SoA e=0 x SoA e=0 -> private SoA e=0. */
void gt32_tile4_basemul_general_soa_soa_to_soa_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_soa[GT32_TILE4_POLY_WORDS]);
/* Bounded Encap probe: general SoA BM and add a SoA message at final store. */
void gt32_tile4_basemul_general_soa_soa_add_m_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa[GT32_TILE4_POLY_WORDS],
	const int16_t b_soa[GT32_TILE4_POLY_WORDS],
	const int16_t m_soa[GT32_TILE4_POLY_WORDS]);
/* Correct-semantic bridge into the unchanged Official poly_tobytes input. */
void gt32_tile4_soa_to_official_words_asm(
	int16_t out_official_words[GT32_TILE4_POLY_WORDS],
	const int16_t in_soa[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_soa_to_official_words_grouped_asm(
	int16_t out_official_words[GT32_TILE4_POLY_WORDS],
	const int16_t in_soa[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_soa_tobytes_direct_asm(
	uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	const int16_t in_soa[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only: private SoA e=1 x TILE4 AoS e=0 -> AoS e=0. */
void gt32_tile4_basemul_e1_soa_aos_to_aos_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a_soa_e1[GT32_TILE4_POLY_WORDS],
	const int16_t b_aos_e0[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only typed edge: F0 AoS x J1 AoS -> exact Official P0 words. */
void gt32_tile4_keygen_fj1_p0_s0_asm(
	int16_t out_p0[GT32_TILE4_POLY_WORDS],
	const int16_t f0_aos[GT32_TILE4_POLY_WORDS],
	const int16_t j1_aos[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_keygen_fj1_p0_s1_asm(
	int16_t out_p0[GT32_TILE4_POLY_WORDS],
	const int16_t f0_aos[GT32_TILE4_POLY_WORDS],
	const int16_t j1_aos[GT32_TILE4_POLY_WORDS]);

/* Benchmark-only basemul attribution leaves; never used by production KEM. */
void gt32_tile4_attr_empty_asm(int16_t *out, const int16_t *a,
	const int16_t *b);
void gt32_tile4_attr_transpose_one_asm(int16_t *out, const int16_t *in);
void gt32_tile4_attr_transpose_one_shufps_asm(int16_t *out,
	const int16_t *in);
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
void gt32_tile4_attr_forward_all_bm_soa_asm(int16_t *out_soa,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_soa_shufps_asm(int16_t *out_soa,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_soa_s5x4_asm(int16_t *out_soa,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_soa_s45w1_asm(int16_t *out_soa,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_soa_s45w2_asm(int16_t *out_soa,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_soa_qpair02_asm(int16_t *out_soa,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_l1_asm(int16_t *out_l1,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_forward_all_bm_l2_asm(int16_t *out_l2,
	const int16_t *frontend_tile4_scratch);
void gt32_tile4_attr_basemul_c3_l1_aos_asm(int16_t *out_aos,
	const int16_t *a_l1, const int16_t *b_aos);
void gt32_tile4_attr_basemul_c3_l1_l1_asm(int16_t *out_aos,
	const int16_t *a_l1, const int16_t *b_l1);
void gt32_tile4_attr_basemul_c3_l2_aos_asm(int16_t *out_aos,
	const int16_t *a_l2, const int16_t *b_aos);
void gt32_tile4_attr_basemul_c3_l2_l2_asm(int16_t *out_aos,
	const int16_t *a_l2, const int16_t *b_l2);
void gt32_tile4_attr_basemul_c3_soa_l2_asm(int16_t *out_aos,
	const int16_t *a_soa, const int16_t *b_l2);
void gt32_tile4_attr_basemul_c3_l2_soa_asm(int16_t *out_aos,
	const int16_t *a_l2, const int16_t *b_soa);
void gt32_tile4_attr_basemul_c3_qpair02_to_aos_asm(int16_t *out_aos,
	const int16_t *a_qpair02_soa, const int16_t *b_qpair02_soa);
void gt32_tile4_attr_basemul_c3_p_to_aos_asm(int16_t *out_aos,
	const int16_t *a_p_soa, const int16_t *b_p_soa);
void gt32_tile4_attr_forward_b_stream_bm_soa_asm(int16_t *out_soa,
	const int16_t *a_soa, const int16_t *b_frontend_tile4,
	int16_t inactive_half_scratch[64]);

void gt32_tile4_frontend_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_wide_e1_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in_e1[GT32_TILE4_POLY_WORDS]);
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
void gt32_tile4_forward_all_pair_id_center_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_pair_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_radix4_identity_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_pair_selective_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

/*
 * N32-first typed inverse experiment.
 *
 * Input: group-major half-native R1-U AoS, e=-1, with physical k3/row order
 * [0,1,2] in qwords 0/1 and [0,2,1] in qwords 2/3.
 * Output: component-major reflected inverse rows, e=-1, for the later
 * untwist/top-reconstruction stage.  The complete and IDFT helpers require
 * disjoint input/output buffers; the L8-L32 suffix supports in-place use.
 */
void gt32_n32_idft_l2_l4_half_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_n32_inv_l8_l32_half_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_n32_inverse_half_r1u_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Benchmark-only current-I1 IDFT3 adapter to the N32 branch-major endpoint. */
void gt32_current_idft3_branch_row_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t current_i1[GT32_TILE4_POLY_WORDS]);

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
void gt32_tile4_forward_full_wide_raw_pair_id_center_align64_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

#endif
