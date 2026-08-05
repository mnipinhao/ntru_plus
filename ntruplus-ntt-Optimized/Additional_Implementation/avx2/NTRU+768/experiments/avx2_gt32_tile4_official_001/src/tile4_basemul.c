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
