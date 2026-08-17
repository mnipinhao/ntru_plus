/* Benchmark-only split attribution for the current P-J1 BaseInv. */
#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

#include "../../gt_ntt/gt_basemul_soa.h"
#include "../generated/tile4_baseinv_p_tables.inc"

#define GT_RINV 1
#define GT_RINV_QINV 12929

#define gt_baseinv_center_l8_test_avx2 gt32_p_j1_attr_center_l8_test_avx2
#define gt_baseinv_native_centered_avx2 gt32_p_j1_attr_direct_avx2
#define gt_baseinv_native_center_on_load_avx2 gt32_p_j1_attr_center_on_load_avx2
#define gt_baseinv_native_quadratic_centered_avx2 gt32_p_j1_attr_quad_centered_avx2
#define gt_baseinv_native_quadratic_center_on_load_avx2 gt32_p_j1_attr_quad_center_on_load_avx2
#define gt_baseinv_native_quadratic_abi_avx2 gt32_p_j1_attr_quad_abi_avx2
#define gt_baseinv_native_centered_asm_avx2 gt32_p_j1_attr_direct_asm_avx2
#define gt_baseinv_native_center_on_load_asm_avx2 gt32_p_j1_attr_center_on_load_asm_avx2
#include "../../gt_ntt/gt_baseinv_native.c"

extern int gt32_p_j1_batch_inverse_asm(int16_t determinant[192]);
extern int gt32_p_j1_batch_inverse_tree_asm(int16_t determinant[192]);

/*
 * Exact prepare loop from baseinv_native_core(), ending at the determinant
 * and pre-sign adjugate boundary.  It is duplicated here deliberately so the
 * production implementation and its current research edits remain untouched.
 */
__attribute__((noinline))
void gt32_p_j1_attr_prepare(int16_t out[GT_NTT_N],
	int16_t determinant_out[GT_SOA_BATCHES * GT_SOA_LANES],
	const int16_t in[GT_NTT_N])
{
	__m256i *const determinant = (__m256i *)(void *)determinant_out;

	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const unsigned base = 64U * batch;
		const __m256i lambda = _mm256_load_si256(
			(const __m256i *)(const void *)gt_native_lambda[batch]);
		const __m256i lambda_qinv = _mm256_load_si256(
			(const __m256i *)(const void *)gt_native_lambda_qinv[batch]);
		const __m256i a0 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base));
		const __m256i a1 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base + 16));
		const __m256i a2 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base + 32));
		const __m256i a3 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base + 48));
		__m256i cross;
		__m256i t0;
		__m256i t1;
		__m256i t2;

		cross = montgomery_mul(a1, a3);
		t0 = _mm256_sub_epi16(montgomery_square(a2),
			_mm256_add_epi16(cross, cross));
		t0 = _mm256_add_epi16(montgomery_square(a0),
			montgomery_mul_fixed(t0, lambda, lambda_qinv));

		cross = montgomery_mul(a0, a2);
		t1 = _mm256_add_epi16(montgomery_square(a1),
			montgomery_mul_fixed(montgomery_square(a3),
				lambda, lambda_qinv));
		t1 = _mm256_sub_epi16(t1, _mm256_add_epi16(cross, cross));
		t2 = montgomery_mul_fixed(t1, lambda, lambda_qinv);

		determinant[batch] = _mm256_sub_epi16(
			montgomery_square(t0), montgomery_mul(t1, t2));

		_mm256_storeu_si256((__m256i *)(void *)(out + base),
			_mm256_add_epi16(montgomery_mul(a0, t0),
				montgomery_mul(a2, t2)));
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 16),
			_mm256_add_epi16(montgomery_mul(a3, t2),
				montgomery_mul(a1, t0)));
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 32),
			_mm256_add_epi16(montgomery_mul(a2, t0),
				montgomery_mul(a0, t1)));
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 48),
			_mm256_add_epi16(montgomery_mul(a1, t1),
				montgomery_mul(a3, t0)));
	}
}

__attribute__((noinline))
int gt32_p_j1_attr_batch_inverse(
	int16_t determinant[GT_SOA_BATCHES * GT_SOA_LANES])
{
	return batch_inverse((__m256i *)(void *)determinant);
}

__attribute__((noinline))
void gt32_p_j1_attr_finish(int16_t out[GT_NTT_N],
	const int16_t determinant_in[GT_SOA_BATCHES * GT_SOA_LANES])
{
	const __m256i zero = _mm256_setzero_si256();

	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const unsigned base = 64U * batch;
		const __m256i scale = _mm256_loadu_si256(
			(const __m256i *)(const void *)(determinant_in + 16U * batch));
		const __m256i scale_qinv = _mm256_mullo_epi16(
			scale, _mm256_set1_epi16(GT_QINV));
		__m256i r0 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(out + base));
		__m256i r1 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(out + base + 16));
		__m256i r2 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(out + base + 32));
		__m256i r3 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(out + base + 48));

		r0 = montgomery_mul_fixed(r0, scale, scale_qinv);
		r1 = _mm256_sub_epi16(zero,
			montgomery_mul_fixed(r1, scale, scale_qinv));
		r2 = montgomery_mul_fixed(r2, scale, scale_qinv);
		r3 = _mm256_sub_epi16(zero,
			montgomery_mul_fixed(r3, scale, scale_qinv));

		_mm256_storeu_si256((__m256i *)(void *)(out + base), r0);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 16), r1);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 32), r2);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 48), r3);
	}
}

/* Whole-BaseInv attribution endpoint using the hand-written batch kernel. */
__attribute__((noinline))
int gt32_p_j1_attr_direct_batch_asm(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	int16_t determinant[GT_SOA_BATCHES * GT_SOA_LANES]
		__attribute__((aligned(32)));

	gt32_p_j1_attr_prepare(out, determinant, in);
	if (gt32_p_j1_batch_inverse_asm(determinant) != 0) {
		memset(out, 0, GT_NTT_N * sizeof(out[0]));
		return 1;
	}
	gt32_p_j1_attr_finish(out, determinant);
	return 0;
}

__attribute__((noinline))
int gt32_p_j1_attr_direct_batch_tree_asm(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	int16_t determinant[GT_SOA_BATCHES * GT_SOA_LANES]
		__attribute__((aligned(32)));

	gt32_p_j1_attr_prepare(out, determinant, in);
	if (gt32_p_j1_batch_inverse_tree_asm(determinant) != 0) {
		memset(out, 0, GT_NTT_N * sizeof(out[0]));
		return 1;
	}
	gt32_p_j1_attr_finish(out, determinant);
	return 0;
}

/* Matched function-boundary control: current C batch, same split wrapper. */
__attribute__((noinline))
int gt32_p_j1_attr_direct_split_c(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	int16_t determinant[GT_SOA_BATCHES * GT_SOA_LANES]
		__attribute__((aligned(32)));

	gt32_p_j1_attr_prepare(out, determinant, in);
	if (gt32_p_j1_attr_batch_inverse(determinant) != 0) {
		memset(out, 0, GT_NTT_N * sizeof(out[0]));
		return 1;
	}
	gt32_p_j1_attr_finish(out, determinant);
	return 0;
}
