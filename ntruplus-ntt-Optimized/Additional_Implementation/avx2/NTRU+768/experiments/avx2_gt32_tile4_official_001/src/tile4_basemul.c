#include <immintrin.h>
#include <stdint.h>

#include "tile4.h"
#include "../generated/tile4_basemul_constants.h"

#define GT_QINV 12929

static int16_t signed_high16(int32_t value)
{
	return (int16_t)(value >> 16);
}

static int16_t montgomery_scalar(int16_t a, int16_t b)
{
	const int16_t low = (int16_t)(uint16_t)((uint32_t)(uint16_t)a
		* (uint32_t)(uint16_t)b * GT_QINV);
	return (int16_t)(signed_high16((int32_t)a * b)
		- signed_high16((int32_t)low * GT32_TILE4_Q));
}

static int16_t center_rminus1_scalar(int32_t value)
{
	const int32_t quotient = (value * 10 + 16384) >> 15;
	return (int16_t)(value - quotient * GT32_TILE4_Q);
}

static void quartic_scalar(int16_t out[4], const int16_t a[4],
	const int16_t b[4], int16_t lambda)
{
	int32_t wrapped;
	int32_t value;

	wrapped = montgomery_scalar(a[1], b[3])
		+ montgomery_scalar(a[2], b[2])
		+ montgomery_scalar(a[3], b[1]);
	value = montgomery_scalar((int16_t)wrapped, lambda)
		+ montgomery_scalar(a[0], b[0]);
	out[0] = center_rminus1_scalar(value);

	wrapped = montgomery_scalar(a[2], b[3])
		+ montgomery_scalar(a[3], b[2]);
	value = montgomery_scalar((int16_t)wrapped, lambda)
		+ montgomery_scalar(a[0], b[1])
		+ montgomery_scalar(a[1], b[0]);
	out[1] = center_rminus1_scalar(value);

	wrapped = montgomery_scalar(a[3], b[3]);
	value = montgomery_scalar((int16_t)wrapped, lambda)
		+ montgomery_scalar(a[0], b[2])
		+ montgomery_scalar(a[1], b[1])
		+ montgomery_scalar(a[2], b[0]);
	out[2] = center_rminus1_scalar(value);

	value = montgomery_scalar(a[0], b[3])
		+ montgomery_scalar(a[1], b[2])
		+ montgomery_scalar(a[2], b[1])
		+ montgomery_scalar(a[3], b[0]);
	out[3] = center_rminus1_scalar(value);
}

void gt32_tile4_basemul_b0(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS])
{
	for (unsigned tile = 0; tile < GT32_TILE4_TILES; tile++) {
		for (unsigned vector = 0; vector < 8; vector++) {
			for (unsigned lane = 0; lane < 4; lane++) {
				int16_t av[4];
				int16_t bv[4];
				int16_t result[4];
				const unsigned base = 128U * tile + 16U * vector + 4U * lane;
				for (unsigned c = 0; c < 4; c++) {
					av[c] = a[base + c];
					bv[c] = b[base + c];
				}
				quartic_scalar(result, av, bv,
					gt32_tile4_lambda_mont[tile][vector][4U * lane]);
				for (unsigned c = 0; c < 4; c++)
					out[base + c] = result[c];
			}
		}
	}
}

static const uint8_t broadcast_mask[4][32] __attribute__((aligned(32))) = {
	{0,1,0,1,0,1,0,1,8,9,8,9,8,9,8,9, 0,1,0,1,0,1,0,1,8,9,8,9,8,9,8,9},
	{2,3,2,3,2,3,2,3,10,11,10,11,10,11,10,11, 2,3,2,3,2,3,2,3,10,11,10,11,10,11,10,11},
	{4,5,4,5,4,5,4,5,12,13,12,13,12,13,12,13, 4,5,4,5,4,5,4,5,12,13,12,13,12,13,12,13},
	{6,7,6,7,6,7,6,7,14,15,14,15,14,15,14,15, 6,7,6,7,6,7,6,7,14,15,14,15,14,15,14,15},
};

static const uint8_t wide_d_shuffle[4][32] __attribute__((aligned(32))) = {
	{0,1,6,7,4,5,2,3, 8,9,14,15,12,13,10,11,
	 0,1,6,7,4,5,2,3, 8,9,14,15,12,13,10,11},
	{2,3,0,1,6,7,4,5, 10,11,8,9,14,15,12,13,
	 2,3,0,1,6,7,4,5, 10,11,8,9,14,15,12,13},
	{4,5,2,3,0,1,6,7, 12,13,10,11,8,9,14,15,
	 4,5,2,3,0,1,6,7, 12,13,10,11,8,9,14,15},
	{6,7,4,5,2,3,0,1, 14,15,12,13,10,11,8,9,
	 6,7,4,5,2,3,0,1, 14,15,12,13,10,11,8,9},
};

static const uint8_t wide_pack_shuffle[32] __attribute__((aligned(32))) = {
	0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,
	0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,
};

static inline __m256i montgomery_vector(__m256i a, __m256i b)
{
	const __m256i q = _mm256_set1_epi16(GT32_TILE4_Q);
	const __m256i qinv = _mm256_set1_epi16(GT_QINV);
	const __m256i low = _mm256_mullo_epi16(a, b);
	const __m256i correction = _mm256_mulhi_epi16(
		_mm256_mullo_epi16(low, qinv), q);
	return _mm256_sub_epi16(_mm256_mulhi_epi16(a, b), correction);
}

static inline __m256i center_rminus1_vector(__m256i value)
{
	const __m256i quotient = _mm256_mulhrs_epi16(value,
		_mm256_set1_epi16(10));
	return _mm256_sub_epi16(value,
		_mm256_mullo_epi16(quotient, _mm256_set1_epi16(GT32_TILE4_Q)));
}

static inline __m256i montgomery32_vector(__m256i value)
{
	const __m256i qinv = _mm256_set1_epi32(GT_QINV);
	const __m256i q = _mm256_set1_epi32(GT32_TILE4_Q);
	const __m256i low_mask = _mm256_set1_epi32(0xffff);
	__m256i correction = _mm256_mullo_epi32(value, qinv);
	correction = _mm256_and_si256(correction, low_mask);
	correction = _mm256_mullo_epi32(correction, q);
	return _mm256_srai_epi32(_mm256_sub_epi32(value, correction), 16);
}

void gt32_tile4_basemul_wide_a1_intrinsic(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS])
{
	for (unsigned tile = 0; tile < GT32_TILE4_TILES; tile++) {
		for (unsigned vector = 0; vector < 8U; vector++) {
			const unsigned word = 128U * tile + 16U * vector;
			const __m256i av = _mm256_loadu_si256(
				(const __m256i *)(const void *)(a + word));
			const __m256i bv = _mm256_loadu_si256(
				(const __m256i *)(const void *)(b + word));
			const __m256i lambda = _mm256_load_si256(
				(const __m256i *)(const void *)
				gt32_tile4_lambda_mont[tile][vector]);
			const __m256i lambda_b = montgomery_vector(bv, lambda);
			const __m256i mixed = _mm256_blend_epi16(bv, lambda_b, 0xee);
			const __m256i d0 = _mm256_shuffle_epi8(mixed,
				_mm256_load_si256((const __m256i *)(const void *)
				wide_d_shuffle[0]));
			const __m256i d1 = _mm256_shuffle_epi8(
				_mm256_blend_epi16(bv, mixed, 0xcc),
				_mm256_load_si256((const __m256i *)(const void *)
				wide_d_shuffle[1]));
			const __m256i d2 = _mm256_shuffle_epi8(
				_mm256_blend_epi16(bv, mixed, 0x88),
				_mm256_load_si256((const __m256i *)(const void *)
				wide_d_shuffle[2]));
			const __m256i d3 = _mm256_shuffle_epi8(bv,
				_mm256_load_si256((const __m256i *)(const void *)
				wide_d_shuffle[3]));
			const __m256i p0 = _mm256_madd_epi16(av, d0);
			const __m256i p1 = _mm256_madd_epi16(av, d1);
			const __m256i p2 = _mm256_madd_epi16(av, d2);
			const __m256i p3 = _mm256_madd_epi16(av, d3);
			const __m256i c01 = montgomery32_vector(
				_mm256_hadd_epi32(p0, p1));
			const __m256i c23 = montgomery32_vector(
				_mm256_hadd_epi32(p2, p3));
			const __m256i packed = _mm256_shuffle_epi8(
				_mm256_packs_epi32(c01, c23),
				_mm256_load_si256((const __m256i *)(const void *)
				wide_pack_shuffle));
			_mm256_storeu_si256((__m256i *)(void *)(out + word), packed);
		}
	}
}

static inline void transpose4x16(__m256i value[4])
{
	const __m256i t0 = _mm256_unpacklo_epi16(value[0], value[1]);
	const __m256i t1 = _mm256_unpackhi_epi16(value[0], value[1]);
	const __m256i t2 = _mm256_unpacklo_epi16(value[2], value[3]);
	const __m256i t3 = _mm256_unpackhi_epi16(value[2], value[3]);
	const __m256i u0 = _mm256_unpacklo_epi32(t0, t2);
	const __m256i u1 = _mm256_unpackhi_epi32(t0, t2);
	const __m256i u2 = _mm256_unpacklo_epi32(t1, t3);
	const __m256i u3 = _mm256_unpackhi_epi32(t1, t3);
	value[0] = _mm256_unpacklo_epi64(u0, u2);
	value[1] = _mm256_unpackhi_epi64(u0, u2);
	value[2] = _mm256_unpacklo_epi64(u1, u3);
	value[3] = _mm256_unpackhi_epi64(u1, u3);
}

/* K1 gate: outer Karatsuba, linear products remain schoolbook (15 Monts). */
void gt32_tile4_basemul_k1_intrinsic(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS])
{
	for (unsigned block = 0; block < 12U; block++) {
		__m256i av[4];
		__m256i bv[4];
		for (unsigned i = 0; i < 4U; i++) {
			const unsigned word = 64U * block + 16U * i;
			av[i] = _mm256_loadu_si256(
				(const __m256i *)(const void *)(a + word));
			bv[i] = _mm256_loadu_si256(
				(const __m256i *)(const void *)(b + word));
		}
		transpose4x16(av);
		transpose4x16(bv);
		const __m256i lambda = _mm256_load_si256(
			(const __m256i *)(const void *)
			gt32_tile4_lambda_transpose_mont[block]);

		const __m256i p0 = montgomery_vector(av[0], bv[0]);
		const __m256i p1 = _mm256_add_epi16(
			montgomery_vector(av[0], bv[1]),
			montgomery_vector(av[1], bv[0]));
		const __m256i p2 = montgomery_vector(av[1], bv[1]);
		const __m256i q0 = montgomery_vector(av[2], bv[2]);
		const __m256i q1 = _mm256_add_epi16(
			montgomery_vector(av[2], bv[3]),
			montgomery_vector(av[3], bv[2]));
		const __m256i q2 = montgomery_vector(av[3], bv[3]);

		const __m256i a02 = _mm256_add_epi16(av[0], av[2]);
		const __m256i a13 = _mm256_add_epi16(av[1], av[3]);
		const __m256i b02 = _mm256_add_epi16(bv[0], bv[2]);
		const __m256i b13 = _mm256_add_epi16(bv[1], bv[3]);
		const __m256i r0 = _mm256_sub_epi16(
			_mm256_sub_epi16(montgomery_vector(a02, b02), p0), q0);
		const __m256i r1 = _mm256_sub_epi16(
			_mm256_sub_epi16(_mm256_add_epi16(
				montgomery_vector(a02, b13),
				montgomery_vector(a13, b02)), p1), q1);
		const __m256i r2 = _mm256_sub_epi16(
			_mm256_sub_epi16(montgomery_vector(a13, b13), p2), q2);

		__m256i cv[4];
		cv[0] = _mm256_add_epi16(p0, montgomery_vector(
			_mm256_add_epi16(q0, r2), lambda));
		cv[1] = _mm256_add_epi16(p1, montgomery_vector(q1, lambda));
		cv[2] = _mm256_add_epi16(_mm256_add_epi16(p2, r0),
			montgomery_vector(q2, lambda));
		cv[3] = r1;
		for (unsigned i = 0; i < 4U; i++)
			cv[i] = center_rminus1_vector(cv[i]);
		transpose4x16(cv);
		for (unsigned i = 0; i < 4U; i++) {
			const unsigned word = 64U * block + 16U * i;
			_mm256_storeu_si256((__m256i *)(void *)(out + word), cv[i]);
		}
	}
}

static inline void linear_karatsuba(__m256i out[3], __m256i a0, __m256i a1,
	__m256i b0, __m256i b1)
{
	out[0] = montgomery_vector(a0, b0);
	out[2] = montgomery_vector(a1, b1);
	out[1] = montgomery_vector(_mm256_add_epi16(a0, a1),
		_mm256_add_epi16(b0, b1));
	out[1] = _mm256_sub_epi16(_mm256_sub_epi16(out[1], out[0]), out[2]);
}

/* K2 gate: two-level Karatsuba, 9 variable plus 3 lambda Mont chains. */
void gt32_tile4_basemul_k2_intrinsic(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS])
{
	for (unsigned block = 0; block < 12U; block++) {
		__m256i av[4];
		__m256i bv[4];
		for (unsigned i = 0; i < 4U; i++) {
			const unsigned word = 64U * block + 16U * i;
			av[i] = _mm256_loadu_si256(
				(const __m256i *)(const void *)(a + word));
			bv[i] = _mm256_loadu_si256(
				(const __m256i *)(const void *)(b + word));
		}
		transpose4x16(av);
		transpose4x16(bv);

		__m256i p[3];
		__m256i q[3];
		__m256i s[3];
		linear_karatsuba(p, av[0], av[1], bv[0], bv[1]);
		linear_karatsuba(q, av[2], av[3], bv[2], bv[3]);
		linear_karatsuba(s,
			_mm256_add_epi16(av[0], av[2]),
			_mm256_add_epi16(av[1], av[3]),
			_mm256_add_epi16(bv[0], bv[2]),
			_mm256_add_epi16(bv[1], bv[3]));
		__m256i r[3];
		for (unsigned i = 0; i < 3U; i++)
			r[i] = _mm256_sub_epi16(_mm256_sub_epi16(s[i], p[i]), q[i]);

		const __m256i lambda = _mm256_load_si256(
			(const __m256i *)(const void *)
			gt32_tile4_lambda_transpose_mont[block]);
		__m256i cv[4];
		cv[0] = _mm256_add_epi16(p[0], montgomery_vector(
			_mm256_add_epi16(q[0], r[2]), lambda));
		cv[1] = _mm256_add_epi16(p[1], montgomery_vector(q[1], lambda));
		cv[2] = _mm256_add_epi16(_mm256_add_epi16(p[2], r[0]),
			montgomery_vector(q[2], lambda));
		cv[3] = r[1];
		for (unsigned i = 0; i < 4U; i++)
			cv[i] = center_rminus1_vector(cv[i]);
		transpose4x16(cv);
		for (unsigned i = 0; i < 4U; i++) {
			const unsigned word = 64U * block + 16U * i;
			_mm256_storeu_si256((__m256i *)(void *)(out + word), cv[i]);
		}
	}
}

static inline __m256i product_coefficient(const __m256i a[4],
	const __m256i b[4], __m256i lambda, unsigned coefficient)
{
	__m256i value;
	__m256i wrapped;
	switch (coefficient) {
	case 0:
		wrapped = _mm256_add_epi16(montgomery_vector(a[1], b[3]),
			montgomery_vector(a[2], b[2]));
		wrapped = _mm256_add_epi16(wrapped,
			montgomery_vector(a[3], b[1]));
		value = _mm256_add_epi16(montgomery_vector(wrapped, lambda),
			montgomery_vector(a[0], b[0]));
		break;
	case 1:
		wrapped = _mm256_add_epi16(montgomery_vector(a[2], b[3]),
			montgomery_vector(a[3], b[2]));
		value = _mm256_add_epi16(montgomery_vector(wrapped, lambda),
			montgomery_vector(a[0], b[1]));
		value = _mm256_add_epi16(value, montgomery_vector(a[1], b[0]));
		break;
	case 2:
		wrapped = montgomery_vector(a[3], b[3]);
		value = _mm256_add_epi16(montgomery_vector(wrapped, lambda),
			montgomery_vector(a[0], b[2]));
		value = _mm256_add_epi16(value, montgomery_vector(a[1], b[1]));
		value = _mm256_add_epi16(value, montgomery_vector(a[2], b[0]));
		break;
	default:
		value = _mm256_add_epi16(montgomery_vector(a[0], b[3]),
			montgomery_vector(a[1], b[2]));
		value = _mm256_add_epi16(value, montgomery_vector(a[2], b[1]));
		value = _mm256_add_epi16(value, montgomery_vector(a[3], b[0]));
		break;
	}
	return center_rminus1_vector(value);
}

void gt32_tile4_basemul_b1(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS])
{
	for (unsigned tile = 0; tile < GT32_TILE4_TILES; tile++) {
		for (unsigned vector = 0; vector < 8; vector++) {
			const unsigned word = 128U * tile + 16U * vector;
			const __m256i input_a = _mm256_loadu_si256(
				(const __m256i *)(const void *)(a + word));
			const __m256i input_b = _mm256_loadu_si256(
				(const __m256i *)(const void *)(b + word));
			const __m256i lambda = _mm256_load_si256(
				(const __m256i *)(const void *)gt32_tile4_lambda_mont[tile][vector]);
			__m256i av[4];
			__m256i bv[4];
			for (unsigned c = 0; c < 4; c++) {
				const __m256i mask = _mm256_load_si256(
					(const __m256i *)(const void *)broadcast_mask[c]);
				av[c] = _mm256_shuffle_epi8(input_a, mask);
				bv[c] = _mm256_shuffle_epi8(input_b, mask);
			}
			__m256i packed = product_coefficient(av, bv, lambda, 0);
			packed = _mm256_blend_epi16(packed,
				product_coefficient(av, bv, lambda, 1), 0x22);
			packed = _mm256_blend_epi16(packed,
				product_coefficient(av, bv, lambda, 2), 0x44);
			packed = _mm256_blend_epi16(packed,
				product_coefficient(av, bv, lambda, 3), 0x88);
			_mm256_storeu_si256((__m256i *)(void *)(out + word), packed);
		}
	}
}
