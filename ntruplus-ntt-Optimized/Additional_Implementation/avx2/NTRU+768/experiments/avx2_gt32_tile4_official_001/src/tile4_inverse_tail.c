#include <stdint.h>
#include <immintrin.h>

#include "tile4.h"
#include "../generated/tile4_inverse_tail_constants.h"

#define TAIL_Q 3457
#define TAIL_R 3310
#define TAIL_W 2734
#define TAIL_W2 722
#define TAIL_TOP_INV 1823
#define TAIL_NORM_INV 3421

static int16_t centered64(int64_t value)
{
	value %= TAIL_Q;
	if (value < 0)
		value += TAIL_Q;
	if (value > TAIL_Q / 2)
		value -= TAIL_Q;
	return (int16_t)value;
}

static int16_t mul_mod(int16_t a, int16_t b)
{
	return centered64((int64_t)a * b);
}

static int16_t pow_mod(int16_t base, unsigned exponent)
{
	int16_t result = 1;
	while (exponent != 0U) {
		if ((exponent & 1U) != 0U)
			result = mul_mod(result, base);
		base = mul_mod(base, base);
		exponent >>= 1;
	}
	return result;
}

static unsigned tail_input_index(unsigned n3, unsigned q)
{
	return (64U * n3 + 33U * q) % 96U;
}

static int16_t load_tile(const int16_t *in, unsigned k3, unsigned branch,
	unsigned q, unsigned coefficient)
{
	return in[128U * (2U * k3 + branch) + 16U * (q / 4U)
		+ 4U * (q % 4U) + coefficient];
}

static void inverse_tail(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS], int rminus1)
{
	const int16_t final_scale = rminus1 != 0
		? mul_mod(TAIL_NORM_INV, TAIL_R) : TAIL_NORM_INV;
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
			int16_t branch_value[2][3];
			for (unsigned branch = 0; branch < 2; branch++) {
				const int16_t r0 = load_tile(in, 0, branch, q, coefficient);
				const int16_t r1 = load_tile(in, 1, branch, q, coefficient);
				const int16_t r2 = load_tile(in, 2, branch, q, coefficient);
				const int16_t x[3] = {
					centered64((int32_t)r0 + r1 + r2),
					centered64((int32_t)r0 + mul_mod(r1, TAIL_W2)
						+ mul_mod(r2, TAIL_W)),
					centered64((int32_t)r0 + mul_mod(r1, TAIL_W)
						+ mul_mod(r2, TAIL_W2)),
				};
				const int16_t scale = branch == 0U ? 2 : 22;
				for (unsigned n3 = 0; n3 < 3; n3++) {
					const unsigned n = tail_input_index(n3, q);
					branch_value[branch][n3] = mul_mod(x[n3],
						pow_mod(scale, n));
				}
			}
			for (unsigned n3 = 0; n3 < 3; n3++) {
				const unsigned n = tail_input_index(n3, q);
				const int16_t high = mul_mod(centered64(
					(int32_t)branch_value[1][n3]
					- branch_value[0][n3]), TAIL_TOP_INV);
				const int16_t low = centered64(
					(int32_t)branch_value[0][n3] + 722 * (int32_t)high);
				out[4U * n + coefficient] = mul_mod(low, final_scale);
				out[384U + 4U * n + coefficient] = mul_mod(high, final_scale);
			}
		}
	}
}

void gt32_tile4_inverse_tail_ref_e0(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	inverse_tail(out, in, 0);
}

void gt32_tile4_inverse_tail_ref_rminus1(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	inverse_tail(out, in, 1);
}

static __m256i mont_fixed256(__m256i value, __m256i factor,
	__m256i factor_qinv)
{
	const __m256i q = _mm256_set1_epi16(TAIL_Q);
	return _mm256_sub_epi16(_mm256_mulhi_epi16(value, factor),
		_mm256_mulhi_epi16(_mm256_mullo_epi16(value, factor_qinv), q));
}

static __m256i center256(__m256i value)
{
	const __m256i q = _mm256_set1_epi16(TAIL_Q);
	const __m256i quotient = _mm256_mulhrs_epi16(value,
		_mm256_set1_epi16(10));
	return _mm256_sub_epi16(value, _mm256_mullo_epi16(quotient, q));
}

static __m256i center_canonical256(__m256i value)
{
	const __m256i q = _mm256_set1_epi16(TAIL_Q);
	const __m256i half_q = _mm256_set1_epi16(TAIL_Q / 2);
	const __m256i minus_half_q = _mm256_set1_epi16(-(TAIL_Q / 2));
	value = center256(value);
	value = _mm256_sub_epi16(value, _mm256_and_si256(q,
		_mm256_cmpgt_epi16(value, half_q)));
	return _mm256_add_epi16(value, _mm256_and_si256(q,
		_mm256_cmpgt_epi16(minus_half_q, value)));
}

static void inverse_dft3(__m256i r0, __m256i r1, __m256i r2,
	__m256i *x0, __m256i *x1, __m256i *x2)
{
	const __m256i w = _mm256_set1_epi16(-886);
	const __m256i w_qinv = _mm256_set1_epi16(13706);
	const __m256i w2 = _mm256_set1_epi16(1033);
	const __m256i w2_qinv = _mm256_set1_epi16(-13687);
	r0 = center256(r0);
	r1 = center256(r1);
	r2 = center256(r2);
	*x0 = _mm256_add_epi16(_mm256_add_epi16(r0, r1), r2);
	*x1 = _mm256_add_epi16(r0, _mm256_add_epi16(
		mont_fixed256(r1, w2, w2_qinv),
		mont_fixed256(r2, w, w_qinv)));
	*x2 = _mm256_add_epi16(r0, _mm256_add_epi16(
		mont_fixed256(r1, w, w_qinv),
		mont_fixed256(r2, w2, w2_qinv)));
}

static void inverse_blend3(__m256i x, __m256i y, __m256i z,
	__m256i *r0, __m256i *r1, __m256i *r2)
{
	*r0 = _mm256_blend_epi32(_mm256_blend_epi32(x, y, 0x0c), z, 0x30);
	*r1 = _mm256_blend_epi32(_mm256_blend_epi32(z, x, 0x0c), y, 0x30);
	*r2 = _mm256_blend_epi32(_mm256_blend_epi32(y, z, 0x0c), x, 0x30);
}

static __m256i matrix_product(__m256i y0, __m256i y1,
	const int16_t factor[4][16], const int16_t qinv[4][16], unsigned row)
{
	const __m256i a = _mm256_load_si256(
		(const __m256i *)(const void *)factor[2U * row]);
	const __m256i aq = _mm256_load_si256(
		(const __m256i *)(const void *)qinv[2U * row]);
	const __m256i b = _mm256_load_si256(
		(const __m256i *)(const void *)factor[2U * row + 1U]);
	const __m256i bq = _mm256_load_si256(
		(const __m256i *)(const void *)qinv[2U * row + 1U]);
	return center_canonical256(_mm256_add_epi16(mont_fixed256(y0, a, aq),
		mont_fixed256(y1, b, bq)));
}

void gt32_tile4_inverse_tail_intrinsic_rminus1(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (unsigned group = 0; group < 8; group++) {
		__m256i b0[3], b1[3], p0[3], p1[3];
		for (unsigned k3 = 0; k3 < 3; k3++) {
			b0[k3] = _mm256_loadu_si256((const __m256i *)(const void *)(
				in + 128U * (2U * k3) + 16U * group));
			b1[k3] = _mm256_loadu_si256((const __m256i *)(const void *)(
				in + 128U * (2U * k3 + 1U) + 16U * group));
		}
		inverse_dft3(b0[0], b0[1], b0[2], &b0[0], &b0[1], &b0[2]);
		inverse_dft3(b1[0], b1[1], b1[2], &b1[0], &b1[1], &b1[2]);
		inverse_blend3(b0[0], b0[1], b0[2], &p0[0], &p0[1], &p0[2]);
		inverse_blend3(b1[0], b1[1], b1[2], &p1[0], &p1[1], &p1[2]);
		for (unsigned segment = 0; segment < 3; segment++) {
			const unsigned permuted = (segment + 3U - group % 3U) % 3U;
			const __m256i low = matrix_product(p0[permuted], p1[permuted],
				gt32_tile4_tail_matrix[group][segment],
				gt32_tile4_tail_matrix_qinv[group][segment], 0);
			const __m256i high = matrix_product(p0[permuted], p1[permuted],
				gt32_tile4_tail_matrix[group][segment],
				gt32_tile4_tail_matrix_qinv[group][segment], 1);
			_mm256_storeu_si256((__m256i *)(void *)(out + 128U * segment
				+ 16U * group), low);
			_mm256_storeu_si256((__m256i *)(void *)(out + 384U
				+ 128U * segment + 16U * group), high);
		}
	}
}
