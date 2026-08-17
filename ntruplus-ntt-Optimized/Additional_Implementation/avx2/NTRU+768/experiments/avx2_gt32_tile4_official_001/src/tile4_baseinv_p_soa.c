/* Benchmark-only P-lane instantiation of the mature GTN SoA BaseInv. */
#include <stdint.h>

#include "../../gt_ntt/gt_basemul_soa.h"

/* Keep the quadratic-only metadata available to discarded helper symbols. */
#define gt_native_lambda gt_old_native_lambda
#define gt_native_lambda_qinv gt_old_native_lambda_qinv
#include "../../gt_ntt/gt_basemul_soa_tables.inc"
#undef gt_native_lambda
#undef gt_native_lambda_qinv

#include "../generated/tile4_baseinv_p_tables.inc"

/* Give this bounded experiment private symbol names. */
#define gt_baseinv_center_l8_test_avx2 gt32_p_baseinv_center_l8_test_avx2
#define gt_baseinv_native_centered_avx2 gt32_p_baseinv_direct_avx2
#define gt_baseinv_native_center_on_load_avx2 gt32_p_baseinv_center_on_load_avx2
#define gt_baseinv_native_quadratic_centered_avx2 gt32_p_baseinv_quad_centered_avx2
#define gt_baseinv_native_quadratic_center_on_load_avx2 gt32_p_baseinv_quad_center_on_load_avx2
#define gt_baseinv_native_quadratic_abi_avx2 gt32_p_baseinv_quad_abi_avx2
#define gt_baseinv_native_centered_asm_avx2 gt32_p_baseinv_direct_asm_avx2
#define gt_baseinv_native_center_on_load_asm_avx2 gt32_p_baseinv_center_on_load_asm_avx2
#include "../../gt_ntt/gt_baseinv_native.c"

/*
 * P1 boundary probe: split the mature BaseInv after batch inversion so its
 * pre-sign adjugate can be consumed without materializing the final inverse.
 * The determinant array contains the twelve already-inverted lane vectors.
 */
int gt32_p_baseinv_prepare_inverse_asm_avx2(int16_t out[GT_NTT_N],
	int16_t determinant_out[GT_SOA_BATCHES * GT_SOA_LANES],
	const int16_t in[GT_NTT_N])
{
	__m256i *const determinant = (__m256i *)(void *)determinant_out;

	gt_baseinv_native_prepare_centered_asm(out, determinant, in);
	if (batch_inverse(determinant) != 0) {
		memset(out, 0, GT_NTT_N * sizeof(out[0]));
		memset(determinant_out, 0,
			GT_SOA_BATCHES * GT_SOA_LANES *
				sizeof(determinant_out[0]));
		return 1;
	}
	return 0;
}

void gt32_p_baseinv_apply_inverse_avx2(int16_t out[GT_NTT_N],
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

/*
 * Matched executable probe for BaseInv terminal -> native BaseMul entry.
 * It reproduces the four final inverse vectors in registers and immediately
 * consumes them as the second BaseMul operand.  The pre-adjugate and the
 * inverted determinant remain reusable compact producer outputs; the full
 * final inverse polynomial never exists.
 */
void gt32_p_baseinv_apply_inverse_bm_avx2(int16_t out[GT_NTT_N],
	const int16_t other[GT_NTT_N], const int16_t presign[GT_NTT_N],
	const int16_t determinant_in[GT_SOA_BATCHES * GT_SOA_LANES])
{
	const __m256i zero = _mm256_setzero_si256();
	const __m256i rsq = _mm256_set1_epi16(867);
	const __m256i rsq_qinv = _mm256_set1_epi16(2787);

	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const unsigned base = 64U * batch;
		const __m256i scale = _mm256_loadu_si256(
			(const __m256i *)(const void *)(determinant_in + 16U * batch));
		const __m256i scale_qinv = _mm256_mullo_epi16(
			scale, _mm256_set1_epi16(GT_QINV));
		const __m256i lambda = _mm256_load_si256(
			(const __m256i *)(const void *)gt_native_lambda[batch]);
		const __m256i lambda_qinv = _mm256_load_si256(
			(const __m256i *)(const void *)gt_native_lambda_qinv[batch]);
		const __m256i a0 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(other + base));
		const __m256i a1 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(other + base + 16));
		const __m256i a2 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(other + base + 32));
		const __m256i a3 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(other + base + 48));
		const __m256i b0 = montgomery_mul_fixed(
			_mm256_loadu_si256((const __m256i *)(const void *)(presign + base)),
			scale, scale_qinv);
		const __m256i b1 = _mm256_sub_epi16(zero,
			montgomery_mul_fixed(_mm256_loadu_si256(
				(const __m256i *)(const void *)(presign + base + 16)),
				scale, scale_qinv));
		const __m256i b2 = montgomery_mul_fixed(
			_mm256_loadu_si256((const __m256i *)(const void *)(presign + base + 32)),
			scale, scale_qinv);
		const __m256i b3 = _mm256_sub_epi16(zero,
			montgomery_mul_fixed(_mm256_loadu_si256(
				(const __m256i *)(const void *)(presign + base + 48)),
				scale, scale_qinv));
		__m256i accumulator;

		accumulator = _mm256_add_epi16(montgomery_mul(a1, b3),
			montgomery_mul(a2, b2));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a3, b1));
		accumulator = montgomery_mul_fixed(accumulator,
			lambda, lambda_qinv);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a0, b0));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base), accumulator);

		accumulator = _mm256_add_epi16(montgomery_mul(a2, b3),
			montgomery_mul(a3, b2));
		accumulator = montgomery_mul_fixed(accumulator,
			lambda, lambda_qinv);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a0, b1));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a1, b0));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 16), accumulator);

		accumulator = montgomery_mul_fixed(montgomery_mul(a3, b3),
			lambda, lambda_qinv);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a0, b2));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a1, b1));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a2, b0));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 32), accumulator);

		accumulator = _mm256_add_epi16(montgomery_mul(a0, b3),
			montgomery_mul(a1, b2));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a2, b1));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul(a3, b0));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 48), accumulator);
	}
}
