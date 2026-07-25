#include <immintrin.h>
#include <stdint.h>

#include "gt_basemul_soa.h"

#define GT_QINV 12929
#define GT_RSQ 867
#define GT_RSQ_QINV 2787

#include "gt_basemul_soa_tables.inc"

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

static inline __m256i montgomery_mul_load(const int16_t *a,
	const int16_t *b)
{
	return montgomery_mul(
		_mm256_loadu_si256((const __m256i *)(const void *)a),
		_mm256_loadu_si256((const __m256i *)(const void *)b));
}

static void gt_basemul_layout_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N],
	const int16_t lambda_table[GT_SOA_BATCHES][GT_SOA_LANES],
	const int16_t lambda_qinv_table[GT_SOA_BATCHES][GT_SOA_LANES])
{
	const __m256i rsq = _mm256_set1_epi16(GT_RSQ);
	const __m256i rsq_qinv = _mm256_set1_epi16(GT_RSQ_QINV);

	for (unsigned batch = 0; batch < GT_SOA_BATCHES; batch++) {
		const unsigned base = 64U * batch;
		const int16_t *const ap = a + base;
		const int16_t *const bp = b + base;
		const __m256i lambda = _mm256_load_si256(
			(const __m256i *)(const void *)lambda_table[batch]);
		const __m256i lambda_qinv = _mm256_load_si256(
			(const __m256i *)(const void *)lambda_qinv_table[batch]);
		__m256i accumulator;

		/* c0 = a0*b0 + lambda*(a1*b3 + a2*b2 + a3*b1). */
		accumulator = montgomery_mul_load(ap + 16, bp + 48);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 32, bp + 32));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 48, bp + 16));
		accumulator = montgomery_mul_fixed(accumulator,
			lambda, lambda_qinv);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap, bp));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base), accumulator);

		/* c1 = a0*b1 + a1*b0 + lambda*(a2*b3 + a3*b2). */
		accumulator = montgomery_mul_load(ap + 32, bp + 48);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 48, bp + 32));
		accumulator = montgomery_mul_fixed(accumulator,
			lambda, lambda_qinv);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap, bp + 16));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 16, bp));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 16), accumulator);

		/* c2 = a0*b2 + a1*b1 + a2*b0 + lambda*a3*b3. */
		accumulator = montgomery_mul_load(ap + 48, bp + 48);
		accumulator = montgomery_mul_fixed(accumulator,
			lambda, lambda_qinv);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap, bp + 32));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 16, bp + 16));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 32, bp));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 32), accumulator);

		/* c3 = a0*b3 + a1*b2 + a2*b1 + a3*b0. */
		accumulator = montgomery_mul_load(ap, bp + 48);
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 16, bp + 32));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 32, bp + 16));
		accumulator = _mm256_add_epi16(accumulator,
			montgomery_mul_load(ap + 48, bp));
		accumulator = montgomery_mul_fixed(accumulator, rsq, rsq_qinv);
		_mm256_storeu_si256((__m256i *)(void *)(out + base + 48), accumulator);
	}
}

void gt_basemul_soa_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N])
{
	gt_basemul_layout_avx2(out, a, b,
		gt_soa_lambda, gt_soa_lambda_qinv);
}

void gt_basemul_native_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N])
{
	gt_basemul_layout_avx2(out, a, b,
		gt_native_lambda, gt_native_lambda_qinv);
}
