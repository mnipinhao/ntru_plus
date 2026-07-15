#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

#include "gt_ntt_avx2.h"
#include "gt_ntt_tables.h"

#define GT_QINV 12929
#define GT_R (-147)
#define GT_ZETA_TOP (-1033)
#define GT_ZETA_TOP_QINV 13687
#define GT_OMEGA3 (-886)
#define GT_OMEGA3_QINV 13706
#define GT_BARRETT_V 19412

static inline int16_t factor_qinv(int16_t factor)
{
	return (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * GT_QINV);
}

static inline __m128i montgomery_mul_fixed128(__m128i a, __m128i b,
	__m128i bqinv)
{
	const __m128i q = _mm_set1_epi16(GT_NTT_Q);
	const __m128i hi = _mm_mulhi_epi16(a, b);
	const __m128i correction = _mm_mulhi_epi16(
		_mm_mullo_epi16(a, bqinv), q);

	return _mm_sub_epi16(hi, correction);
}

static inline __m256i montgomery_mul_fixed256(__m256i a, __m256i b,
	__m256i bqinv)
{
	const __m256i q = _mm256_set1_epi16(GT_NTT_Q);
	const __m256i hi = _mm256_mulhi_epi16(a, b);
	const __m256i correction = _mm256_mulhi_epi16(
		_mm256_mullo_epi16(a, bqinv), q);

	return _mm256_sub_epi16(hi, correction);
}

static inline __m256i montgomery_mul256(__m256i a, __m256i b)
{
	return montgomery_mul_fixed256(a, b,
		_mm256_mullo_epi16(b, _mm256_set1_epi16(GT_QINV)));
}

static inline __m256i barrett_reduce256(__m256i a)
{
	const __m256i v = _mm256_set1_epi32(GT_BARRETT_V);
	const __m256i rounding = _mm256_set1_epi32(1 << 25);
	const __m256i q = _mm256_set1_epi32(GT_NTT_Q);
	const __m128i low16 = _mm256_castsi256_si128(a);
	const __m128i high16 = _mm256_extracti128_si256(a, 1);
	__m256i low32 = _mm256_cvtepi16_epi32(low16);
	__m256i high32 = _mm256_cvtepi16_epi32(high16);
	__m256i packed;

	low32 = _mm256_srai_epi32(
		_mm256_add_epi32(_mm256_mullo_epi32(low32, v), rounding), 26);
	high32 = _mm256_srai_epi32(
		_mm256_add_epi32(_mm256_mullo_epi32(high32, v), rounding), 26);
	low32 = _mm256_sub_epi32(_mm256_cvtepi16_epi32(low16),
		_mm256_mullo_epi32(low32, q));
	high32 = _mm256_sub_epi32(_mm256_cvtepi16_epi32(high16),
		_mm256_mullo_epi32(high32, q));

	/* packs_epi32 is lane-local: qword permutation restores 0..15 order. */
	packed = _mm256_packs_epi32(low32, high32);
	return _mm256_permute4x64_epi64(packed, 0xd8);
}

static inline unsigned bitreverse_limited(unsigned x, unsigned bits)
{
	unsigned result = 0;

	for (unsigned i = 0; i < bits; i++) {
		result = (result << 1) | (x & 1U);
		x >>= 1;
	}
	return result;
}

static inline unsigned ntt32_twiddle_power(unsigned stage, unsigned lo)
{
	if (stage == 1) {
		return 0;
	}
	return bitreverse_limited(lo >> (6 - stage), stage - 1)
		<< (5 - stage);
}

static inline unsigned gt_input_index(unsigned n3, unsigned n32)
{
	return (64U * n3 + 33U * n32) % 96U;
}

static inline unsigned gt_output_index(unsigned k3, unsigned k32)
{
	return (32U * k3 + 3U * k32) % 96U;
}

/*
 * Return one Good-Thomas input slot as eight int16 streams:
 *   [branch0 lane0..3 | branch1 lane0..3].
 */
static inline __m128i load_twisted_streams(
	const int16_t in[GT_NTT_N], unsigned n)
{
	const __m128i low = _mm_loadl_epi64(
		(const __m128i *)(const void *)(in + 4U * n));
	const __m128i high = _mm_loadl_epi64(
		(const __m128i *)(const void *)(in + 384U + 4U * n));
	const __m128i split = montgomery_mul_fixed128(high,
		_mm_set1_epi16(GT_ZETA_TOP),
		_mm_set1_epi16(GT_ZETA_TOP_QINV));
	const __m128i branch0 = _mm_add_epi16(low, split);
	const __m128i branch1 = _mm_sub_epi16(
		_mm_add_epi16(low, high), split);
	const __m128i streams = _mm_unpacklo_epi64(branch0, branch1);
	const __m128i twist = _mm_setr_epi16(
		gt_twist[0][n], gt_twist[0][n],
		gt_twist[0][n], gt_twist[0][n],
		gt_twist[1][n], gt_twist[1][n],
		gt_twist[1][n], gt_twist[1][n]);
	const __m128i twist_qinv = _mm_setr_epi16(
		factor_qinv(gt_twist[0][n]), factor_qinv(gt_twist[0][n]),
		factor_qinv(gt_twist[0][n]), factor_qinv(gt_twist[0][n]),
		factor_qinv(gt_twist[1][n]), factor_qinv(gt_twist[1][n]),
		factor_qinv(gt_twist[1][n]), factor_qinv(gt_twist[1][n]));

	return montgomery_mul_fixed128(streams, twist, twist_qinv);
}

static inline __m256i join_slots(__m128i even, __m128i odd)
{
	return _mm256_inserti128_si256(_mm256_castsi128_si256(even), odd, 1);
}

void gt_ntt_avx2_frontend(gt_frontend_scratch *scratch,
	const int16_t in[GT_NTT_N])
{
	const __m256i omega3 = _mm256_set1_epi16(GT_OMEGA3);
	const __m256i omega3_qinv = _mm256_set1_epi16(GT_OMEGA3_QINV);

	for (unsigned q = 0; q < 32; q += 2) {
		const __m256i x0 = join_slots(
			load_twisted_streams(in, gt_input_index(0, q)),
			load_twisted_streams(in, gt_input_index(0, q + 1)));
		const __m256i x1 = join_slots(
			load_twisted_streams(in, gt_input_index(1, q)),
			load_twisted_streams(in, gt_input_index(1, q + 1)));
		const __m256i x2 = join_slots(
			load_twisted_streams(in, gt_input_index(2, q)),
			load_twisted_streams(in, gt_input_index(2, q + 1)));
		__m256i d;
		__m256i t;
		__m256i r0;
		__m256i r1;
		__m256i r2;

		d = _mm256_sub_epi16(x1, x2);
		t = montgomery_mul_fixed256(d, omega3, omega3_qinv);
		r0 = _mm256_add_epi16(_mm256_add_epi16(x0, x1), x2);
		r1 = _mm256_add_epi16(_mm256_sub_epi16(x0, x2), t);
		r2 = _mm256_sub_epi16(_mm256_sub_epi16(x0, x1), t);

		/* [row0.Q | row1.Q], one YMM per Q. */
		_mm256_store_si256((__m256i *)(void *)scratch->row01[q],
			_mm256_permute2x128_si256(r0, r1, 0x20));
		_mm256_store_si256((__m256i *)(void *)scratch->row01[q + 1],
			_mm256_permute2x128_si256(r0, r1, 0x31));
		_mm_store_si128((__m128i *)(void *)scratch->row2[q],
			_mm256_castsi256_si128(r2));
		_mm_store_si128((__m128i *)(void *)scratch->row2[q + 1],
			_mm256_extracti128_si256(r2, 1));
	}
}

static inline __m256i pack_row2_stage1(__m128i low, __m128i high)
{
	const __m128i reduced_high = montgomery_mul_fixed128(high,
		_mm_set1_epi16(GT_R), _mm_set1_epi16(factor_qinv(GT_R)));

	return join_slots(_mm_add_epi16(low, reduced_high),
		_mm_sub_epi16(low, reduced_high));
}

void gt_ntt_avx2_stage12(gt_stage2_scratch *out,
	const gt_frontend_scratch *in)
{
	const __m256i omega8 = _mm256_set1_epi16(gt_omega32[8]);
	const __m256i omega8_qinv = _mm256_set1_epi16(
		factor_qinv(gt_omega32[8]));
	const __m256i montgomery_identity = _mm256_set1_epi16(GT_R);
	const __m256i montgomery_identity_qinv = _mm256_set1_epi16(
		factor_qinv(GT_R));
	const __m256i row2_stage2_twiddle = _mm256_setr_epi16(
		GT_R, GT_R, GT_R, GT_R, GT_R, GT_R, GT_R, GT_R,
		gt_omega32[8], gt_omega32[8], gt_omega32[8], gt_omega32[8],
		gt_omega32[8], gt_omega32[8], gt_omega32[8], gt_omega32[8]);
	const __m256i row2_stage2_twiddle_qinv = _mm256_setr_epi16(
		factor_qinv(GT_R), factor_qinv(GT_R), factor_qinv(GT_R),
		factor_qinv(GT_R), factor_qinv(GT_R), factor_qinv(GT_R),
		factor_qinv(GT_R), factor_qinv(GT_R),
		factor_qinv(gt_omega32[8]), factor_qinv(gt_omega32[8]),
		factor_qinv(gt_omega32[8]), factor_qinv(gt_omega32[8]),
		factor_qinv(gt_omega32[8]), factor_qinv(gt_omega32[8]),
		factor_qinv(gt_omega32[8]), factor_qinv(gt_omega32[8]));

	for (unsigned q = 0; q < 8; q++) {
		const __m256i a0 = _mm256_load_si256(
			(const __m256i *)(const void *)in->row01[q]);
		const __m256i a1 = _mm256_load_si256(
			(const __m256i *)(const void *)in->row01[q + 8]);
		const __m256i a2 = _mm256_load_si256(
			(const __m256i *)(const void *)in->row01[q + 16]);
		const __m256i a3 = _mm256_load_si256(
			(const __m256i *)(const void *)in->row01[q + 24]);
		const __m256i a2_reduced = montgomery_mul_fixed256(a2,
			montgomery_identity, montgomery_identity_qinv);
		const __m256i a3_reduced = montgomery_mul_fixed256(a3,
			montgomery_identity, montgomery_identity_qinv);
		const __m256i s0 = _mm256_add_epi16(a0, a2_reduced);
		const __m256i d0 = _mm256_sub_epi16(a0, a2_reduced);
		const __m256i s1 = _mm256_add_epi16(a1, a3_reduced);
		const __m256i d1 = _mm256_sub_epi16(a1, a3_reduced);
		const __m256i s1_reduced = montgomery_mul_fixed256(s1,
			montgomery_identity, montgomery_identity_qinv);
		const __m256i t1 = montgomery_mul_fixed256(
			d1, omega8, omega8_qinv);
		const __m128i r20 = _mm_load_si128(
			(const __m128i *)(const void *)in->row2[q]);
		const __m128i r21 = _mm_load_si128(
			(const __m128i *)(const void *)in->row2[q + 8]);
		const __m128i r22 = _mm_load_si128(
			(const __m128i *)(const void *)in->row2[q + 16]);
		const __m128i r23 = _mm_load_si128(
			(const __m128i *)(const void *)in->row2[q + 24]);
		const __m256i p0 = pack_row2_stage1(r20, r22);
		const __m256i p1 = pack_row2_stage1(r21, r23);
		const __m256i pt = montgomery_mul_fixed256(p1,
			row2_stage2_twiddle, row2_stage2_twiddle_qinv);

		_mm256_store_si256((__m256i *)(void *)out->row01[q],
			_mm256_add_epi16(s0, s1_reduced));
		_mm256_store_si256((__m256i *)(void *)out->row01[q + 8],
			_mm256_sub_epi16(s0, s1_reduced));
		_mm256_store_si256((__m256i *)(void *)out->row01[q + 16],
			_mm256_add_epi16(d0, t1));
		_mm256_store_si256((__m256i *)(void *)out->row01[q + 24],
			_mm256_sub_epi16(d0, t1));
		_mm256_store_si256((__m256i *)(void *)out->row2_packed[q],
			_mm256_add_epi16(p0, pt));
		_mm256_store_si256((__m256i *)(void *)out->row2_packed[q + 8],
			_mm256_sub_epi16(p0, pt));
	}
}

static inline void butterfly256(__m256i *low, __m256i *high,
	__m256i twiddle)
{
	const __m256i u = *low;
	const __m256i t = montgomery_mul256(*high, twiddle);

	*low = _mm256_add_epi16(u, t);
	*high = _mm256_sub_epi16(u, t);
}

static inline __m256i row01_twiddle(unsigned stage, unsigned lo)
{
	return _mm256_set1_epi16(
		gt_omega32[ntt32_twiddle_power(stage, lo)]);
}

static inline __m256i row2_twiddle(unsigned stage, unsigned packed_lo)
{
	const int16_t low = gt_omega32[
		ntt32_twiddle_power(stage, packed_lo)];
	const int16_t high = gt_omega32[
		ntt32_twiddle_power(stage, packed_lo + 16)];

	return _mm256_setr_epi16(
		low, low, low, low, low, low, low, low,
		high, high, high, high, high, high, high, high);
}

static inline void row01_block345(int16_t block[8][16], unsigned base)
{
	__m256i v0 = _mm256_load_si256((const __m256i *)(const void *)block[0]);
	__m256i v1 = _mm256_load_si256((const __m256i *)(const void *)block[1]);
	__m256i v2 = _mm256_load_si256((const __m256i *)(const void *)block[2]);
	__m256i v3 = _mm256_load_si256((const __m256i *)(const void *)block[3]);
	__m256i v4 = _mm256_load_si256((const __m256i *)(const void *)block[4]);
	__m256i v5 = _mm256_load_si256((const __m256i *)(const void *)block[5]);
	__m256i v6 = _mm256_load_si256((const __m256i *)(const void *)block[6]);
	__m256i v7 = _mm256_load_si256((const __m256i *)(const void *)block[7]);

	butterfly256(&v0, &v4, row01_twiddle(3, base + 0));
	butterfly256(&v1, &v5, row01_twiddle(3, base + 1));
	butterfly256(&v2, &v6, row01_twiddle(3, base + 2));
	butterfly256(&v3, &v7, row01_twiddle(3, base + 3));
	butterfly256(&v0, &v2, row01_twiddle(4, base + 0));
	butterfly256(&v1, &v3, row01_twiddle(4, base + 1));
	butterfly256(&v4, &v6, row01_twiddle(4, base + 4));
	butterfly256(&v5, &v7, row01_twiddle(4, base + 5));
	butterfly256(&v0, &v1, row01_twiddle(5, base + 0));
	butterfly256(&v2, &v3, row01_twiddle(5, base + 2));
	butterfly256(&v4, &v5, row01_twiddle(5, base + 4));
	butterfly256(&v6, &v7, row01_twiddle(5, base + 6));

	_mm256_store_si256((__m256i *)(void *)block[0], v0);
	_mm256_store_si256((__m256i *)(void *)block[1], v1);
	_mm256_store_si256((__m256i *)(void *)block[2], v2);
	_mm256_store_si256((__m256i *)(void *)block[3], v3);
	_mm256_store_si256((__m256i *)(void *)block[4], v4);
	_mm256_store_si256((__m256i *)(void *)block[5], v5);
	_mm256_store_si256((__m256i *)(void *)block[6], v6);
	_mm256_store_si256((__m256i *)(void *)block[7], v7);
}

static inline void row2_block345(int16_t block[8][16], unsigned base)
{
	__m256i v0 = _mm256_load_si256((const __m256i *)(const void *)block[0]);
	__m256i v1 = _mm256_load_si256((const __m256i *)(const void *)block[1]);
	__m256i v2 = _mm256_load_si256((const __m256i *)(const void *)block[2]);
	__m256i v3 = _mm256_load_si256((const __m256i *)(const void *)block[3]);
	__m256i v4 = _mm256_load_si256((const __m256i *)(const void *)block[4]);
	__m256i v5 = _mm256_load_si256((const __m256i *)(const void *)block[5]);
	__m256i v6 = _mm256_load_si256((const __m256i *)(const void *)block[6]);
	__m256i v7 = _mm256_load_si256((const __m256i *)(const void *)block[7]);

	butterfly256(&v0, &v4, row2_twiddle(3, base + 0));
	butterfly256(&v1, &v5, row2_twiddle(3, base + 1));
	butterfly256(&v2, &v6, row2_twiddle(3, base + 2));
	butterfly256(&v3, &v7, row2_twiddle(3, base + 3));
	butterfly256(&v0, &v2, row2_twiddle(4, base + 0));
	butterfly256(&v1, &v3, row2_twiddle(4, base + 1));
	butterfly256(&v4, &v6, row2_twiddle(4, base + 4));
	butterfly256(&v5, &v7, row2_twiddle(4, base + 5));
	butterfly256(&v0, &v1, row2_twiddle(5, base + 0));
	butterfly256(&v2, &v3, row2_twiddle(5, base + 2));
	butterfly256(&v4, &v5, row2_twiddle(5, base + 4));
	butterfly256(&v6, &v7, row2_twiddle(5, base + 6));

	_mm256_store_si256((__m256i *)(void *)block[0], v0);
	_mm256_store_si256((__m256i *)(void *)block[1], v1);
	_mm256_store_si256((__m256i *)(void *)block[2], v2);
	_mm256_store_si256((__m256i *)(void *)block[3], v3);
	_mm256_store_si256((__m256i *)(void *)block[4], v4);
	_mm256_store_si256((__m256i *)(void *)block[5], v5);
	_mm256_store_si256((__m256i *)(void *)block[6], v6);
	_mm256_store_si256((__m256i *)(void *)block[7], v7);
}

void gt_ntt_avx2_stage345(gt_stage2_scratch *scratch)
{
	for (unsigned base = 0; base < 32; base += 8) {
		row01_block345(&scratch->row01[base], base);
	}
	for (unsigned base = 0; base < 16; base += 8) {
		row2_block345(&scratch->row2_packed[base], base);
	}
}

static inline void scatter_streams(int16_t out[GT_NTT_N], __m128i streams,
	unsigned k3, unsigned k32)
{
	int16_t lanes[8] __attribute__((aligned(16)));
	const unsigned block = gt_output_index(k3, k32);

	_mm_store_si128((__m128i *)(void *)lanes, streams);
	for (unsigned lane = 0; lane < 4; lane++) {
		out[4U * block + lane] = lanes[lane];
		out[384U + 4U * block + lane] = lanes[4 + lane];
	}
}

void gt_ntt_avx2_scatter(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch)
{
	for (unsigned q = 0; q < 32; q++) {
		const __m256i reduced = barrett_reduce256(_mm256_load_si256(
			(const __m256i *)(const void *)scratch->row01[q]));

		scatter_streams(out, _mm256_castsi256_si128(reduced), 0, q);
		scatter_streams(out, _mm256_extracti128_si256(reduced, 1), 1, q);
	}
	for (unsigned q = 0; q < 16; q++) {
		const __m256i reduced = barrett_reduce256(_mm256_load_si256(
			(const __m256i *)(const void *)scratch->row2_packed[q]));

		scatter_streams(out, _mm256_castsi256_si128(reduced), 2, q);
		scatter_streams(out, _mm256_extracti128_si256(reduced, 1), 2, q + 16);
	}
}

void gt_ntt_avx2(int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	gt_frontend_scratch frontend;
	gt_stage2_scratch stage2;

	/* The full input is consumed before scatter, so out==in is safe. */
	gt_ntt_avx2_frontend(&frontend, in);
	gt_ntt_avx2_stage12(&stage2, &frontend);
	gt_ntt_avx2_stage345(&stage2);
	gt_ntt_avx2_scatter(out, &stage2);
}

void gt_ntt_rowbitrev_to_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned q = 0; q < 32; q++) {
			const unsigned block = gt_output_index(k3, q);
			const unsigned batch = 4U * k3 + q / 8U;

			for (unsigned branch = 0; branch < 2; branch++) {
				const unsigned lane = 8U * branch + q % 8U;

				for (unsigned c = 0; c < 4; c++) {
					out[64U * batch + 16U * c + lane] =
						in[384U * branch + 4U * block + c];
				}
			}
		}
	}
}

void gt_ntt_soa_to_rowbitrev(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned q = 0; q < 32; q++) {
			const unsigned block = gt_output_index(k3, q);
			const unsigned batch = 4U * k3 + q / 8U;

			for (unsigned branch = 0; branch < 2; branch++) {
				const unsigned lane = 8U * branch + q % 8U;

				for (unsigned c = 0; c < 4; c++) {
					out[384U * branch + 4U * block + c] =
						in[64U * batch + 16U * c + lane];
				}
			}
		}
	}
}

#if defined(GT_HAVE_AVX2_ASM)
void gt_ntt_avx2_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N])
{
	gt_frontend_scratch frontend;
	gt_stage2_scratch stage2;

	gt_ntt_avx2_frontend(&frontend, in);
	gt_ntt_avx2_stage12(&stage2, &frontend);
	gt_ntt_avx2_stage345_soa_asm(out, &stage2);
}
#endif

void gt_ntt_avx2_montgomery_test(int16_t out[16],
	const int16_t a[16], const int16_t b[16])
{
	const __m256i av = _mm256_loadu_si256(
		(const __m256i *)(const void *)a);
	const __m256i bv = _mm256_loadu_si256(
		(const __m256i *)(const void *)b);

	_mm256_storeu_si256((__m256i *)(void *)out,
		montgomery_mul256(av, bv));
}

void gt_ntt_avx2_barrett_test(int16_t out[16], const int16_t a[16])
{
	const __m256i av = _mm256_loadu_si256(
		(const __m256i *)(const void *)a);

	_mm256_storeu_si256((__m256i *)(void *)out, barrett_reduce256(av));
}
