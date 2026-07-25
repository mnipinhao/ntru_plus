#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "gt_baseinv_native.h"
#include "gt_basemul_soa.h"

#define GT_QINV 12929
#define GT_RINV (-682)
#define GT_RINV_QINV 29782
#define GT_CENTER10 10

static inline __m256i montgomery_mul(__m256i a, __m256i b)
{
	const __m256i q = _mm256_set1_epi16(GT_NTT_Q);
	const __m256i qinv = _mm256_set1_epi16(GT_QINV);
	const __m256i low = _mm256_mullo_epi16(a, b);
	const __m256i high = _mm256_mulhi_epi16(a, b);
	const __m256i correction = _mm256_mulhi_epi16(
		_mm256_mullo_epi16(low, qinv), q);

	return _mm256_sub_epi16(high, correction);
}

static inline __m256i montgomery_mul_fixed(__m256i a, __m256i factor,
	__m256i factor_qinv)
{
	const __m256i q = _mm256_set1_epi16(GT_NTT_Q);
	const __m256i high = _mm256_mulhi_epi16(a, factor);
	const __m256i correction = _mm256_mulhi_epi16(
		_mm256_mullo_epi16(a, factor_qinv), q);

	return _mm256_sub_epi16(high, correction);
}

static inline __m256i montgomery_square(__m256i a)
{
	return montgomery_mul(a, a);
}

/*
 * Exact for every signed 16-bit input in the declared GTN-L8 interval:
 *
 *   t = round(a * 10 / 2^15)
 *   centered = a - t*q
 *
 * Exhaustive tests pin congruence and the resulting [-3080,3079] bound.
 */
static inline __m256i center_l8(__m256i a)
{
	const __m256i ten = _mm256_set1_epi16(GT_CENTER10);
	const __m256i q = _mm256_set1_epi16(GT_NTT_Q);
	const __m256i quotient = _mm256_mulhrs_epi16(a, ten);

	return _mm256_sub_epi16(a, _mm256_mullo_epi16(quotient, q));
}

void gt_baseinv_center_l8_test_avx2(int16_t out[16],
	const int16_t in[16])
{
	const __m256i a = _mm256_loadu_si256(
		(const __m256i *)(const void *)in);

	_mm256_storeu_si256((__m256i *)(void *)out, center_l8(a));
}

static inline __m256i field_inverse(__m256i r)
{
	const __m256i qinv = _mm256_set1_epi16(GT_QINV);
	const __m256i rinv = _mm256_set1_epi16(GT_RINV);
	const __m256i rinv_qinv = _mm256_set1_epi16(GT_RINV_QINV);
	__m256i r_qinv;
	__m256i t1_qinv;
	__m256i t2_qinv;
	__m256i t1;
	__m256i t2;
	__m256i t3;

	r_qinv = _mm256_mullo_epi16(r, qinv);
	t1 = montgomery_square(r);                 /* 10 */

	t1_qinv = _mm256_mullo_epi16(t1, qinv);
	t2 = montgomery_square(t1);                /* 100 */
	t2 = montgomery_square(t2);                /* 1000 */
	t3 = montgomery_square(t2);                /* 10000 */
	t1 = montgomery_mul_fixed(t2, t1, t1_qinv); /* 1010 */

	t1_qinv = _mm256_mullo_epi16(t1, qinv);
	t2 = montgomery_mul_fixed(t3, t1, t1_qinv); /* 11010 */
	t2 = montgomery_square(t2);                /* 110100 */
	t2 = montgomery_mul_fixed(t2, r, r_qinv);  /* 110101 */
	t1 = montgomery_mul_fixed(t2, t1, t1_qinv); /* 111111 */

	t2 = montgomery_square(t2);                /* 1101010 */
	t2 = montgomery_square(t2);                /* 11010100 */
	t2 = montgomery_square(t2);                /* 110101000 */
	t2 = montgomery_square(t2);                /* 1101010000 */
	t2 = montgomery_square(t2);                /* 11010100000 */
	t2 = montgomery_square(t2);                /* 110101000000 */

	t2_qinv = _mm256_mullo_epi16(t2, qinv);
	t2 = montgomery_mul_fixed(t1, t2, t2_qinv); /* q-2 */

	return montgomery_mul_fixed(t2, rinv, rinv_qinv);
}

/*
 * Replace the 12 determinants by their lane-wise inverses using one field
 * inversion.  The only data-dependent control transfer is the same
 * algorithm-visible invertibility failure boundary used by production
 * poly_baseinv().
 */
static int batch_inverse(__m256i determinant[12])
{
	const __m256i qinv = _mm256_set1_epi16(GT_QINV);
	const __m256i zero = _mm256_setzero_si256();
	__m256i prefix[12];
	__m256i operand_qinv[12];
	__m256i inverse;

	prefix[0] = determinant[0];
	for (size_t i = 1; i < 12; i++) {
		const __m256i operand = determinant[i];

		operand_qinv[i] = _mm256_mullo_epi16(operand, qinv);
		prefix[i] = montgomery_mul_fixed(prefix[i - 1], operand,
			operand_qinv[i]);
	}

	{
		const __m256i mask = _mm256_cmpeq_epi16(prefix[11], zero);

		if (!_mm256_testz_si256(mask, mask)) {
			return 1;
		}
	}

	inverse = field_inverse(prefix[11]);
	for (size_t i = 11; i > 0; i--) {
		const __m256i inverse_qinv =
			_mm256_mullo_epi16(inverse, qinv);
		const __m256i operand = determinant[i];

		determinant[i] = montgomery_mul_fixed(prefix[i - 1],
			inverse, inverse_qinv);
		inverse = montgomery_mul_fixed(inverse, operand,
			operand_qinv[i]);
	}
	determinant[0] = inverse;
	return 0;
}

static int baseinv_finish(int16_t out[GT_NTT_N],
	__m256i determinant[GT_SOA_BATCHES])
{
	if (batch_inverse(determinant) != 0) {
		memset(out, 0, GT_NTT_N * sizeof(out[0]));
		return 1;
	}

	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const unsigned base = 64U * batch;
		const __m256i scale = determinant[batch];
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
		r1 = _mm256_sub_epi16(_mm256_setzero_si256(),
			montgomery_mul_fixed(r1, scale, scale_qinv));
		r2 = montgomery_mul_fixed(r2, scale, scale_qinv);
		r3 = _mm256_sub_epi16(_mm256_setzero_si256(),
			montgomery_mul_fixed(r3, scale, scale_qinv));

		_mm256_storeu_si256((__m256i *)(void *)(out + base), r0);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 16), r1);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 32), r2);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 48), r3);
	}

	return 0;
}

static inline __attribute__((always_inline)) int baseinv_native_core(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N],
	const int center_input)
{
	__m256i determinant[GT_SOA_BATCHES] __attribute__((aligned(32)));

	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const unsigned base = 64U * batch;
		const __m256i lambda = _mm256_load_si256(
			(const __m256i *)(const void *)gt_native_lambda[batch]);
		const __m256i lambda_qinv = _mm256_load_si256(
			(const __m256i *)(const void *)
				gt_native_lambda_qinv[batch]);
		__m256i a0 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base));
		__m256i a1 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base + 16));
		__m256i a2 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base + 32));
		__m256i a3 = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + base + 48));
		__m256i t0;
		__m256i t1;
		__m256i t2;
		__m256i cross;
		__m256i r0;
		__m256i r1;
		__m256i r2;
		__m256i r3;

		if (center_input != 0) {
			a0 = center_l8(a0);
			a1 = center_l8(a1);
			a2 = center_l8(a2);
			a3 = center_l8(a3);
		}

		/*
		 * t0 = a0^2 + lambda*(a2^2 - 2*a1*a3)
		 * t1 = a1^2 + lambda*a3^2 - 2*a0*a2
		 * determinant = t0^2 - lambda*t1^2
		 *
		 * All products are Montgomery-reduced before additions.  The
		 * center-on-load checkpoint therefore restores exactly the same
		 * multiply bounds as the centered control.
		 */
		cross = montgomery_mul(a1, a3);
		t0 = _mm256_sub_epi16(montgomery_square(a2),
			_mm256_add_epi16(cross, cross));
		t0 = _mm256_add_epi16(montgomery_square(a0),
			montgomery_mul_fixed(t0, lambda, lambda_qinv));

		cross = montgomery_mul(a0, a2);
		t1 = _mm256_add_epi16(montgomery_square(a1),
			montgomery_mul_fixed(montgomery_square(a3),
				lambda, lambda_qinv));
		t1 = _mm256_sub_epi16(t1,
			_mm256_add_epi16(cross, cross));
		t2 = montgomery_mul_fixed(t1, lambda, lambda_qinv);

		determinant[batch] = _mm256_sub_epi16(
			montgomery_square(t0), montgomery_mul(t1, t2));

		/* Store the production-compatible pre-sign adjugate. */
		r0 = _mm256_add_epi16(montgomery_mul(a0, t0),
			montgomery_mul(a2, t2));
		r1 = _mm256_add_epi16(montgomery_mul(a3, t2),
			montgomery_mul(a1, t0));
		r2 = _mm256_add_epi16(montgomery_mul(a2, t0),
			montgomery_mul(a0, t1));
		r3 = _mm256_add_epi16(montgomery_mul(a1, t1),
			montgomery_mul(a3, t0));

		_mm256_storeu_si256((__m256i *)(void *)(out + base), r0);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 16), r1);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 32), r2);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 48), r3);
	}

	return baseinv_finish(out, determinant);
}

int gt_baseinv_native_centered_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	return baseinv_native_core(out, in, 0);
}

int gt_baseinv_native_center_on_load_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	return baseinv_native_core(out, in, 1);
}

#if defined(GT_HAVE_AVX2_ASM)
void gt_baseinv_native_prepare_centered_asm(
	int16_t out[GT_NTT_N],
	__m256i determinant[GT_SOA_BATCHES],
	const int16_t in[GT_NTT_N]);

void gt_baseinv_native_prepare_center_on_load_asm(
	int16_t out[GT_NTT_N],
	__m256i determinant[GT_SOA_BATCHES],
	const int16_t in[GT_NTT_N]);

int gt_baseinv_native_centered_asm_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	__m256i determinant[GT_SOA_BATCHES] __attribute__((aligned(32)));

	gt_baseinv_native_prepare_centered_asm(out, determinant, in);
	return baseinv_finish(out, determinant);
}

int gt_baseinv_native_center_on_load_asm_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	__m256i determinant[GT_SOA_BATCHES] __attribute__((aligned(32)));

	gt_baseinv_native_prepare_center_on_load_asm(out, determinant, in);
	return baseinv_finish(out, determinant);
}
#endif
