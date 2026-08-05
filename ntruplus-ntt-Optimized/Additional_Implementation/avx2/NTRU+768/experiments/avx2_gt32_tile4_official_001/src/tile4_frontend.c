#include <immintrin.h>
#include <stdint.h>

#include "tile4.h"
#include "../generated/tile4_frontend_constants.h"

#define GT_QINV 12929
#define GT_ZETA_TOP (-1033)
#define GT_OMEGA3 (-886)

static int16_t signed_high16(int32_t value)
{
	return (int16_t)(value >> 16);
}

static int16_t factor_qinv_scalar(int16_t factor)
{
	return (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * GT_QINV);
}

static int16_t montgomery_scalar(int16_t value, int16_t factor)
{
	const int16_t low = (int16_t)(uint16_t)((uint32_t)(uint16_t)value
		* (uint32_t)(uint16_t)factor_qinv_scalar(factor));
	return (int16_t)(signed_high16((int32_t)value * factor)
		- signed_high16((int32_t)low * GT32_TILE4_Q));
}

static unsigned input_index(unsigned n3, unsigned n32)
{
	return (64U * n3 + 33U * n32) % 96U;
}

static int16_t frontend_component(const int16_t in[GT32_TILE4_POLY_WORDS],
	unsigned branch, unsigned n3, unsigned q, unsigned coefficient)
{
	const unsigned n = input_index(n3, q);
	const int16_t low = in[4U * n + coefficient];
	const int16_t high = in[384U + 4U * n + coefficient];
	const int16_t split = montgomery_scalar(high, GT_ZETA_TOP);
	const int16_t value = branch == 0U
		? (int16_t)(low + split)
		: (int16_t)(low + high - split);
	return montgomery_scalar(value, gt32_tile4_twist[branch][n]);
}

void gt32_tile4_frontend_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (unsigned q = 0; q < 32; q++) {
		for (unsigned branch = 0; branch < 2; branch++) {
			for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
				const int16_t x0 = frontend_component(in, branch, 0, q, coefficient);
				const int16_t x1 = frontend_component(in, branch, 1, q, coefficient);
				const int16_t x2 = frontend_component(in, branch, 2, q, coefficient);
				const int16_t t = montgomery_scalar((int16_t)(x1 - x2), GT_OMEGA3);
				const int16_t row[3] = {
					(int16_t)(x0 + x1 + x2),
					(int16_t)(x0 - x2 + t),
					(int16_t)(x0 - x1 - t),
				};
				for (unsigned k3 = 0; k3 < 3; k3++) {
					const unsigned tile = 2U * k3 + branch;
					const unsigned word = 128U * tile + 16U * (q / 4U)
						+ 4U * (q % 4U) + coefficient;
					out[word] = row[k3];
				}
			}
		}
	}
}

static __m128i montgomery_fixed128(__m128i value, __m128i factor,
	__m128i factor_qinv)
{
	const __m128i q = _mm_set1_epi16(GT32_TILE4_Q);
	return _mm_sub_epi16(_mm_mulhi_epi16(value, factor),
		_mm_mulhi_epi16(_mm_mullo_epi16(value, factor_qinv), q));
}

static __m128i load_twisted_streams(
	const int16_t in[GT32_TILE4_POLY_WORDS], unsigned n)
{
	const __m128i low = _mm_loadl_epi64(
		(const __m128i *)(const void *)(in + 4U * n));
	const __m128i high = _mm_loadl_epi64(
		(const __m128i *)(const void *)(in + 384U + 4U * n));
	const __m128i split = montgomery_fixed128(high,
		_mm_set1_epi16(GT_ZETA_TOP),
		_mm_set1_epi16(factor_qinv_scalar(GT_ZETA_TOP)));
	const __m128i branches = _mm_unpacklo_epi64(
		_mm_add_epi16(low, split),
		_mm_sub_epi16(_mm_add_epi16(low, high), split));
	const __m128i twist = _mm_setr_epi16(
		gt32_tile4_twist[0][n], gt32_tile4_twist[0][n],
		gt32_tile4_twist[0][n], gt32_tile4_twist[0][n],
		gt32_tile4_twist[1][n], gt32_tile4_twist[1][n],
		gt32_tile4_twist[1][n], gt32_tile4_twist[1][n]);
	const __m128i twist_qinv = _mm_setr_epi16(
		factor_qinv_scalar(gt32_tile4_twist[0][n]),
		factor_qinv_scalar(gt32_tile4_twist[0][n]),
		factor_qinv_scalar(gt32_tile4_twist[0][n]),
		factor_qinv_scalar(gt32_tile4_twist[0][n]),
		factor_qinv_scalar(gt32_tile4_twist[1][n]),
		factor_qinv_scalar(gt32_tile4_twist[1][n]),
		factor_qinv_scalar(gt32_tile4_twist[1][n]),
		factor_qinv_scalar(gt32_tile4_twist[1][n]));
	return montgomery_fixed128(branches, twist, twist_qinv);
}

static __m256i join_q_pair(__m128i even, __m128i odd)
{
	return _mm256_inserti128_si256(_mm256_castsi128_si256(even), odd, 1);
}

static __m256i montgomery_fixed256(__m256i value, int16_t factor)
{
	const __m256i q = _mm256_set1_epi16(GT32_TILE4_Q);
	return _mm256_sub_epi16(
		_mm256_mulhi_epi16(value, _mm256_set1_epi16(factor)),
		_mm256_mulhi_epi16(
			_mm256_mullo_epi16(value,
				_mm256_set1_epi16(factor_qinv_scalar(factor))), q));
}

static void store_row_pair(int16_t out[GT32_TILE4_POLY_WORDS],
	__m256i row, unsigned k3, unsigned q)
{
	const __m128i even = _mm256_castsi256_si128(row);
	const __m128i odd = _mm256_extracti128_si256(row, 1);
	const unsigned vector_word = 16U * (q / 4U) + 4U * (q % 4U);
	_mm_storeu_si128((__m128i *)(void *)(out + 128U * (2U * k3)
		+ vector_word), _mm_unpacklo_epi64(even, odd));
	_mm_storeu_si128((__m128i *)(void *)(out + 128U * (2U * k3 + 1U)
		+ vector_word), _mm_unpackhi_epi64(even, odd));
}

void gt32_tile4_frontend_intrinsic(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (unsigned q = 0; q < 32; q += 2) {
		const __m256i x0 = join_q_pair(
			load_twisted_streams(in, input_index(0, q)),
			load_twisted_streams(in, input_index(0, q + 1)));
		const __m256i x1 = join_q_pair(
			load_twisted_streams(in, input_index(1, q)),
			load_twisted_streams(in, input_index(1, q + 1)));
		const __m256i x2 = join_q_pair(
			load_twisted_streams(in, input_index(2, q)),
			load_twisted_streams(in, input_index(2, q + 1)));
		const __m256i t = montgomery_fixed256(_mm256_sub_epi16(x1, x2),
			GT_OMEGA3);
		const __m256i row0 = _mm256_add_epi16(_mm256_add_epi16(x0, x1), x2);
		const __m256i row1 = _mm256_add_epi16(_mm256_sub_epi16(x0, x2), t);
		const __m256i row2 = _mm256_sub_epi16(_mm256_sub_epi16(x0, x1), t);

		store_row_pair(out, row0, 0, q);
		store_row_pair(out, row1, 1, q);
		store_row_pair(out, row2, 2, q);
	}
}

void gt32_tile4_forward_full_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	gt32_tile4_frontend_ref(scratch, in);
	gt32_tile4_forward_all_ref(out, scratch);
}

void gt32_tile4_forward_full_candidate(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	gt32_tile4_frontend_asm(scratch, in);
	gt32_tile4_forward_all_asm(out, scratch);
}
