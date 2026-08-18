#include "official_invntt_ct.h"

#include <immintrin.h>
#include <stdint.h>
#include <string.h>

extern void official_f32x3_rminus1_invntt_ct_asm(
	int16_t out[768], const int16_t in[768]);

/* Decoded from the frozen Official Basemul/Inverse terminal records. */
static const uint8_t record_branch[6] = {0, 0, 0, 1, 1, 1};
static const uint8_t record_row[6] = {0, 1, 2, 1, 2, 0};
static const uint8_t record_j[6][16] = {
	{0,8,20,28,10,18,30,6,21,29,9,17,31,7,19,27},
	{7,15,27,3,17,25,5,13,28,4,16,24,6,14,26,2},
	{14,22,2,10,24,0,12,20,3,11,23,31,13,21,1,9},
	{25,1,13,21,3,11,23,31,14,22,2,10,24,0,12,20},
	{0,8,20,28,10,18,30,6,21,29,9,17,31,7,19,27},
	{7,15,27,3,17,25,5,13,28,4,16,24,6,14,26,2},
};

static unsigned f32x3_word(unsigned branch, unsigned row,
	unsigned j, unsigned coefficient)
{
	const unsigned vector = 16U * row + j / 2U;
	const unsigned lane = 8U * branch + 4U * (j & 1U) + coefficient;
	return 16U * vector + lane;
}

void official_ntt_to_f32x3(int16_t out[768], const int16_t in[768])
{
	for (unsigned record = 0; record < 6; ++record) {
		for (unsigned partner = 0; partner < 2; ++partner) {
			const unsigned group = 2U * record + partner;
			const __m256i c0 = _mm256_load_si256((const __m256i *)(const void *)
				(in + 64U * group));
			const __m256i c1 = _mm256_load_si256((const __m256i *)(const void *)
				(in + 64U * group + 16U));
			const __m256i c2 = _mm256_load_si256((const __m256i *)(const void *)
				(in + 64U * group + 32U));
			const __m256i c3 = _mm256_load_si256((const __m256i *)(const void *)
				(in + 64U * group + 48U));
			const __m256i a0 = _mm256_unpacklo_epi16(c0, c1);
			const __m256i a1 = _mm256_unpackhi_epi16(c0, c1);
			const __m256i a2 = _mm256_unpacklo_epi16(c2, c3);
			const __m256i a3 = _mm256_unpackhi_epi16(c2, c3);
			const __m256i quartics[4] = {
				_mm256_unpacklo_epi32(a0, a2),
				_mm256_unpackhi_epi32(a0, a2),
				_mm256_unpacklo_epi32(a1, a3),
				_mm256_unpackhi_epi32(a1, a3),
			};
			static const uint8_t source_lane[4][4] = {
				{0, 1, 8, 9}, {2, 3, 10, 11},
				{4, 5, 12, 13}, {6, 7, 14, 15},
			};
			for (unsigned vector = 0; vector < 4; ++vector) {
				uint64_t words[4] __attribute__((aligned(32)));
				_mm256_store_si256((__m256i *)(void *)words, quartics[vector]);
				for (unsigned qword = 0; qword < 4; ++qword) {
					const unsigned lane = source_lane[vector][qword];
					const unsigned j = (record_j[record][lane] +
						16U * partner) & 31U;
					const unsigned destination = f32x3_word(
						record_branch[record], record_row[record], j, 0);
					memcpy(out + destination, words + qword, sizeof(uint64_t));
				}
			}
		}
	}
}

void official_invntt_ct_adapter_y2(int16_t out[768], const int16_t in[768])
{
	int16_t state[768] __attribute__((aligned(32)));
	official_ntt_to_f32x3(state, in);
	official_f32x3_rminus1_invntt_ct_asm(out, state);
}
