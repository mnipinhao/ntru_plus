#include <immintrin.h>
#include <stdint.h>

#include "gt_invntt_soa.h"

#define GT_QINV 12929
#define GT_PACKED_BARRETT_V 19412
#define GT_OMEGA3 (-886)
#define GT_ZMINUSZ5INV (-1665)
#define GT_NINV (-811)
#define GT_2NINV (-1622)

#include "gt_invntt_soa_tables.inc"

/* Byte-shuffle masks are duplicated into both 128-bit halves. */
static const uint8_t duplicate_low_len2[16] __attribute__((aligned(16))) = {
	0, 1, 0, 1, 4, 5, 4, 5, 8, 9, 8, 9, 12, 13, 12, 13
};
static const uint8_t duplicate_high_len2[16] __attribute__((aligned(16))) = {
	2, 3, 2, 3, 6, 7, 6, 7, 10, 11, 10, 11, 14, 15, 14, 15
};
static const uint8_t duplicate_low_len4[16] __attribute__((aligned(16))) = {
	0, 1, 2, 3, 0, 1, 2, 3, 8, 9, 10, 11, 8, 9, 10, 11
};
static const uint8_t duplicate_high_len4[16] __attribute__((aligned(16))) = {
	4, 5, 6, 7, 4, 5, 6, 7, 12, 13, 14, 15, 12, 13, 14, 15
};
static const uint8_t duplicate_low_len8[16] __attribute__((aligned(16))) = {
	0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7
};
static const uint8_t duplicate_high_len8[16] __attribute__((aligned(16))) = {
	8, 9, 10, 11, 12, 13, 14, 15, 8, 9, 10, 11, 12, 13, 14, 15
};

static inline int16_t factor_qinv(int16_t factor)
{
	return (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * GT_QINV);
}

static inline __m128i montgomery_mul_fixed128(__m128i a, __m128i factor,
	__m128i factor_qinv_vector)
{
	const __m128i q = _mm_set1_epi16(GT_NTT_Q);
	const __m128i high = _mm_mulhi_epi16(a, factor);
	const __m128i correction = _mm_mulhi_epi16(
		_mm_mullo_epi16(a, factor_qinv_vector), q);

	return _mm_sub_epi16(high, correction);
}

static inline __m256i montgomery_mul_fixed256(__m256i a, __m256i factor,
	__m256i factor_qinv_vector)
{
	const __m256i q = _mm256_set1_epi16(GT_NTT_Q);
	const __m256i high = _mm256_mulhi_epi16(a, factor);
	const __m256i correction = _mm256_mulhi_epi16(
		_mm256_mullo_epi16(a, factor_qinv_vector), q);

	return _mm256_sub_epi16(high, correction);
}

static inline __m256i packed_barrett_reduce256(__m256i a)
{
	__m256i quotient = _mm256_mulhi_epi16(a,
		_mm256_set1_epi16(GT_PACKED_BARRETT_V));

	quotient = _mm256_srai_epi16(quotient, 10);
	return _mm256_sub_epi16(a,
		_mm256_mullo_epi16(quotient, _mm256_set1_epi16(GT_NTT_Q)));
}

static inline __m256i broadcast_shuffle(const uint8_t mask[16])
{
	return _mm256_broadcastsi128_si256(
		_mm_load_si128((const __m128i *)(const void *)mask));
}

static inline __m256i intt_len2(__m256i value)
{
	const __m256i low = _mm256_shuffle_epi8(value,
		broadcast_shuffle(duplicate_low_len2));
	const __m256i high = _mm256_shuffle_epi8(value,
		broadcast_shuffle(duplicate_high_len2));
	const __m256i sum = _mm256_add_epi16(low, high);
	const __m256i difference = _mm256_sub_epi16(low, high);

	return _mm256_blend_epi16(sum, difference, 0xaa);
}

static inline __m256i intt_len4(__m256i value)
{
	const __m256i low = _mm256_shuffle_epi8(value,
		broadcast_shuffle(duplicate_low_len4));
	const __m256i high = _mm256_shuffle_epi8(value,
		broadcast_shuffle(duplicate_high_len4));
	const __m256i product = montgomery_mul_fixed256(high,
		_mm256_load_si256((const __m256i *)(const void *)gt_intt_twiddle[0]),
		_mm256_load_si256((const __m256i *)(const void *)
			gt_intt_twiddle_qinv[0]));
	const __m256i sum = _mm256_add_epi16(low, product);
	const __m256i difference = _mm256_sub_epi16(low, product);

	return _mm256_blend_epi16(sum, difference, 0xcc);
}

static inline __m256i intt_len8(__m256i value)
{
	const __m256i low = _mm256_shuffle_epi8(value,
		broadcast_shuffle(duplicate_low_len8));
	const __m256i high = _mm256_shuffle_epi8(value,
		broadcast_shuffle(duplicate_high_len8));
	const __m256i product = montgomery_mul_fixed256(high,
		_mm256_load_si256((const __m256i *)(const void *)gt_intt_twiddle[1]),
		_mm256_load_si256((const __m256i *)(const void *)
			gt_intt_twiddle_qinv[1]));
	const __m256i sum = _mm256_add_epi16(low, product);
	const __m256i difference = _mm256_sub_epi16(low, product);

	return _mm256_blend_epi16(sum, difference, 0xf0);
}

static inline void intt_cross_group(__m256i *low, __m256i *high,
	unsigned table)
{
	const __m256i product = montgomery_mul_fixed256(*high,
		_mm256_load_si256((const __m256i *)(const void *)
			gt_intt_twiddle[table]),
		_mm256_load_si256((const __m256i *)(const void *)
			gt_intt_twiddle_qinv[table]));
	const __m256i original_low = *low;

	*low = _mm256_add_epi16(original_low, product);
	*high = _mm256_sub_epi16(original_low, product);
}

static void intt32_one_stream(int16_t scratch[GT_NTT_N],
	const int16_t in[GT_NTT_N], unsigned k3, unsigned coefficient)
{
	__m256i group[4];

	for (unsigned i = 0; i < 4; i++) {
		const unsigned offset = 64U * (4U * k3 + i) + 16U * coefficient;

		group[i] = _mm256_loadu_si256(
			(const __m256i *)(const void *)(in + offset));
		group[i] = intt_len2(group[i]);
		group[i] = intt_len4(group[i]);
		group[i] = intt_len8(group[i]);
	}

	/* len=16 pairs Q[0..7] with Q[8..15] inside each 16-slot half. */
	intt_cross_group(&group[0], &group[1], 2);
	intt_cross_group(&group[2], &group[3], 2);
	/* len=32 pairs the two 16-slot halves; j=0..7 and j=8..15 differ. */
	intt_cross_group(&group[0], &group[2], 3);
	intt_cross_group(&group[1], &group[3], 4);

	for (unsigned i = 0; i < 4; i++) {
		const unsigned offset = 64U * (4U * k3 + i) + 16U * coefficient;

		_mm256_store_si256((__m256i *)(void *)(scratch + offset),
			packed_barrett_reduce256(group[i]));
	}
}

void gt_invntt_soa_ntt32_intrinsic(int16_t rows[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
			intt32_one_stream(rows, in, k3, coefficient);
		}
	}
}

static inline __m256i final_merge_vector(__m256i value,
	unsigned n3, unsigned group)
{
	const __m256i untwisted = montgomery_mul_fixed256(value,
		_mm256_load_si256((const __m256i *)(const void *)
			gt_inv_untwist[4U * n3 + group]),
		_mm256_load_si256((const __m256i *)(const void *)
			gt_inv_untwist_qinv[4U * n3 + group]));
	const __m128i branch0 = _mm256_castsi256_si128(untwisted);
	const __m128i branch1 = _mm256_extracti128_si256(untwisted, 1);
	const __m128i sum = _mm_add_epi16(branch0, branch1);
	const __m128i difference = _mm_sub_epi16(branch0, branch1);
	const __m128i correction = montgomery_mul_fixed128(difference,
		_mm_set1_epi16(GT_ZMINUSZ5INV),
		_mm_set1_epi16(factor_qinv(GT_ZMINUSZ5INV)));
	const __m128i low_output = montgomery_mul_fixed128(
		_mm_sub_epi16(sum, correction), _mm_set1_epi16(GT_NINV),
		_mm_set1_epi16(factor_qinv(GT_NINV)));
	const __m128i high_output = montgomery_mul_fixed128(correction,
		_mm_set1_epi16(GT_2NINV),
		_mm_set1_epi16(factor_qinv(GT_2NINV)));

	return _mm256_inserti128_si256(_mm256_castsi128_si256(low_output),
		high_output, 1);
}

static inline void store_block_pair(int16_t out[GT_NTT_N], __m256i pair,
	const uint8_t blocks[8], unsigned first)
{
	const __m128i low = _mm256_castsi256_si128(pair);
	const __m128i high = _mm256_extracti128_si256(pair, 1);
	const unsigned block0 = blocks[first];
	const unsigned block1 = blocks[first + 1];

	_mm_storel_epi64((__m128i *)(void *)(out + 4U * block0), low);
	_mm_storel_epi64((__m128i *)(void *)(out + 4U * block1),
		_mm_srli_si128(low, 8));
	_mm_storel_epi64((__m128i *)(void *)(out + 384U + 4U * block0), high);
	_mm_storel_epi64((__m128i *)(void *)(out + 384U + 4U * block1),
		_mm_srli_si128(high, 8));
}

static inline void store_final_group(int16_t out[GT_NTT_N],
	__m256i c0, __m256i c1, __m256i c2, __m256i c3,
	unsigned n3, unsigned group)
{
	const __m256i c01_low = _mm256_unpacklo_epi16(c0, c1);
	const __m256i c01_high = _mm256_unpackhi_epi16(c0, c1);
	const __m256i c23_low = _mm256_unpacklo_epi16(c2, c3);
	const __m256i c23_high = _mm256_unpackhi_epi16(c2, c3);
	const uint8_t *const blocks = gt_inv_output_block[4U * n3 + group];

	/* Each YMM now holds two complete quartics in each 128-bit half. */
	store_block_pair(out, _mm256_unpacklo_epi32(c01_low, c23_low),
		blocks, 0);
	store_block_pair(out, _mm256_unpackhi_epi32(c01_low, c23_low),
		blocks, 2);
	store_block_pair(out, _mm256_unpacklo_epi32(c01_high, c23_high),
		blocks, 4);
	store_block_pair(out, _mm256_unpackhi_epi32(c01_high, c23_high),
		blocks, 6);
}

void gt_invntt_soa_dft3_intrinsic(int16_t rows[GT_NTT_N])
{
	const __m256i omega3 = _mm256_set1_epi16(GT_OMEGA3);
	const __m256i omega3_qinv = _mm256_set1_epi16(factor_qinv(GT_OMEGA3));

	/* Inverse DFT3 in place: k3 rows become natural-order n3 rows. */
	for (unsigned group = 0; group < 4; group++) {
		for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
			const unsigned offset0 = 64U * group + 16U * coefficient;
			const unsigned offset1 = 64U * (4U + group) + 16U * coefficient;
			const unsigned offset2 = 64U * (8U + group) + 16U * coefficient;
			const __m256i y0 = _mm256_load_si256(
				(const __m256i *)(const void *)(rows + offset0));
			const __m256i y1 = _mm256_load_si256(
				(const __m256i *)(const void *)(rows + offset1));
			const __m256i y2 = _mm256_load_si256(
				(const __m256i *)(const void *)(rows + offset2));
			const __m256i difference = _mm256_sub_epi16(y2, y1);
			const __m256i product = montgomery_mul_fixed256(difference,
				omega3, omega3_qinv);
			const __m256i x0 = packed_barrett_reduce256(_mm256_add_epi16(
				_mm256_add_epi16(y0, y1), y2));
			const __m256i x1 = packed_barrett_reduce256(_mm256_add_epi16(
				_mm256_sub_epi16(y0, y1), product));
			const __m256i x2 = packed_barrett_reduce256(_mm256_sub_epi16(
				_mm256_sub_epi16(y0, y2), product));

			_mm256_store_si256((__m256i *)(void *)(rows + offset0), x0);
			_mm256_store_si256((__m256i *)(void *)(rows + offset1), x1);
			_mm256_store_si256((__m256i *)(void *)(rows + offset2), x2);
		}
	}
}

static void invntt_postprocess_from_rows(int16_t out[GT_NTT_N],
	const int16_t rows[GT_NTT_N])
{
	for (unsigned n3 = 0; n3 < 3; n3++) {
		for (unsigned group = 0; group < 4; group++) {
			const unsigned base = 64U * (4U * n3 + group);
			const __m256i c0 = final_merge_vector(_mm256_load_si256(
				(const __m256i *)(const void *)(rows + base)), n3, group);
			const __m256i c1 = final_merge_vector(_mm256_load_si256(
				(const __m256i *)(const void *)(rows + base + 16)), n3, group);
			const __m256i c2 = final_merge_vector(_mm256_load_si256(
				(const __m256i *)(const void *)(rows + base + 32)), n3, group);
			const __m256i c3 = final_merge_vector(_mm256_load_si256(
				(const __m256i *)(const void *)(rows + base + 48)), n3, group);

			store_final_group(out, c0, c1, c2, c3, n3, group);
		}
	}
}

static void invntt_finish_from_rows(int16_t out[GT_NTT_N],
	int16_t rows[GT_NTT_N])
{
	gt_invntt_soa_dft3_intrinsic(rows);
	invntt_postprocess_from_rows(out, rows);
}

void gt_invntt_soa_avx2(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	/* All SoA input is consumed before final stores, so out==in is safe. */
	gt_invntt_soa_ntt32_intrinsic(rows, in);
	invntt_finish_from_rows(out, rows);
}

#if defined(GT_HAVE_AVX2_ASM)
void gt_invntt_soa_avx2_hybrid(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	/* The ASM region consumes all SoA input before final output stores. */
	gt_invntt_soa_ntt32_asm(rows, in);
	invntt_finish_from_rows(out, rows);
}

void gt_invntt_soa_avx2_dft3_hybrid(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	int16_t rows[GT_NTT_N] __attribute__((aligned(32)));

	gt_invntt_soa_ntt32_asm(rows, in);
	gt_invntt_soa_dft3_asm(rows);
	invntt_postprocess_from_rows(out, rows);
}
#endif
