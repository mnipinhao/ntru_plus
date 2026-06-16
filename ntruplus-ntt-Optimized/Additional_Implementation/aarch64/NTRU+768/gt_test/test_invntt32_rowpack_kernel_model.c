#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if !defined(__aarch64__)
#error "test_invntt32_rowpack_kernel_model requires AArch64 Neon"
#endif

#include <arm_neon.h>

#include "params.h"

#define RANDOM_TESTS 256

#ifdef TEST_ROWPACK_INVNTT32_ASM
void ntruplus768_invntt32_rowpack_soa_row(int16_t *row_plane,
                                          const int16_t *consts);
extern const int16_t ntruplus768_invntt32_rowpack_soa_row_consts[];
#endif

static const int16_t stage2_twiddles[8] __attribute__((aligned(16))) = {
	1, 708, 1, 708, 1, 708, 1, 708,
};

static const int16_t stage2_pre[8] __attribute__((aligned(16))) = {
	9, 6711, 9, 6711, 9, 6711, 9, 6711,
};

static const int16_t stage3_twiddles[8] __attribute__((aligned(16))) = {
	1, 1521, 708, -1716, 1, 1521, 708, -1716,
};

static const int16_t stage3_pre[8] __attribute__((aligned(16))) = {
	9, 14417, 6711, -16266, 9, 14417, 6711, -16266,
};

static const int16_t stage45_twiddles[3][8] __attribute__((aligned(16))) = {
	{ 1, -39, 1521, -550, 708, 44, -1716, 1241 },
	{ 1, -436, -39, -281, 1521, 588, -550, 1267 },
	{ 708, -1015, 44, 1558, -1716, 1464, 1241, 1673 },
};

static const int16_t stage45_pre[3][8] __attribute__((aligned(16))) = {
	{ 9, -370, 14417, -5213, 6711, 417, -16266, 11763 },
	{ 9, -4133, -370, -2664, 14417, 5573, -5213, 12010 },
	{ 6711, -9621, 417, 14768, -16266, 13877, 11763, 15858 },
};

static const uint16_t odd_lane_mask_data[8] __attribute__((aligned(16))) = {
	0, 0xffff, 0, 0xffff, 0, 0xffff, 0, 0xffff,
};

static const uint16_t high2_lane_mask_data[8] __attribute__((aligned(16))) = {
	0, 0, 0xffff, 0xffff, 0, 0, 0xffff, 0xffff,
};

static const uint16_t high4_lane_mask_data[8] __attribute__((aligned(16))) = {
	0, 0, 0, 0, 0xffff, 0xffff, 0xffff, 0xffff,
};

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525u + 1013904223u;
	return *state;
}

static int abs_i(int x)
{
	return x < 0 ? -x : x;
}

static int64_t arshift(int64_t x, unsigned shift)
{
	if (x >= 0)
	{
		return x >> shift;
	}

	return -(((-x) + ((INT64_C(1) << shift) - 1)) >> shift);
}

static int16_t wrap16(int32_t x)
{
	return (int16_t)(uint16_t)x;
}

static int16_t sat16(int64_t x)
{
	if (x > 32767)
	{
		return 32767;
	}

	if (x < -32768)
	{
		return -32768;
	}

	return (int16_t)x;
}

static int16_t sqrdmulh_s16(int16_t a, int16_t b)
{
	const int64_t doubled = INT64_C(2) * a * b;
	const int64_t rounded = arshift(doubled + (INT64_C(1) << 15), 16);

	return sat16(rounded);
}

static int16_t sqdmulh_s16(int16_t a, int16_t b)
{
	return sat16(arshift(INT64_C(2) * a * b, 16));
}

static int16_t srshr_s16(int16_t a, unsigned shift)
{
	return (int16_t)arshift((int64_t)a + (INT64_C(1) << (shift - 1)), shift);
}

static int16_t scalar_fqmul(int16_t a, int16_t mul, int16_t pre)
{
	const int16_t qhat = sqrdmulh_s16(a, pre);
	int16_t prod = wrap16((int32_t)a * mul);

	prod = wrap16((int32_t)prod - (int32_t)qhat * NTRUPLUS_Q);
	return prod;
}

static int16_t scalar_barrett(int16_t a)
{
	int16_t t = sqdmulh_s16(a, 19412);

	t = srshr_s16(t, 11);
	return wrap16((int32_t)a - (int32_t)t * NTRUPLUS_Q);
}

static void scalar_butterfly(int16_t a[32], int lo, int hi,
                             int16_t mul, int16_t pre)
{
	const int16_t old_lo = a[lo];
	const int16_t prod = scalar_fqmul(a[hi], mul, pre);

	a[lo] = wrap16((int32_t)a[lo] + prod);
	a[hi] = wrap16((int32_t)old_lo - prod);
}

static void scalar_invntt32_row_end(int16_t out[32], const int16_t in[32])
{
	static const int16_t stage123_mul[5] = { 1, 708, 1521, 708, -1716 };
	static const int16_t stage123_pre[5] = { 9, 6711, 14417, 6711, -16266 };
	static const int16_t stage45_mul[8][3] = {
		{ 1, 1, 708 },
		{ -39, -436, -1015 },
		{ 1521, -39, 44 },
		{ -550, -281, 1558 },
		{ 708, 1521, -1716 },
		{ 44, 588, 1464 },
		{ -1716, -550, 1241 },
		{ 1241, 1267, 1673 },
	};
	static const int16_t stage45_pre_scalar[8][3] = {
		{ 9, 9, 6711 },
		{ -370, -4133, -9621 },
		{ 14417, -370, 417 },
		{ -5213, -2664, 14768 },
		{ 6711, 14417, -16266 },
		{ 417, 5573, 13877 },
		{ -16266, -5213, 11763 },
		{ 11763, 12010, 15858 },
	};

	memcpy(out, in, 32 * sizeof(out[0]));

	for (int i = 0; i < 32; i++)
	{
		out[i] = scalar_barrett(out[i]);
	}

	for (int base = 0; base < 32; base += 8)
	{
		scalar_butterfly(out, base + 0, base + 1,
		                 stage123_mul[0], stage123_pre[0]);
		scalar_butterfly(out, base + 2, base + 3,
		                 stage123_mul[0], stage123_pre[0]);
		scalar_butterfly(out, base + 4, base + 5,
		                 stage123_mul[0], stage123_pre[0]);
		scalar_butterfly(out, base + 6, base + 7,
		                 stage123_mul[0], stage123_pre[0]);

		scalar_butterfly(out, base + 0, base + 2,
		                 stage123_mul[0], stage123_pre[0]);
		scalar_butterfly(out, base + 1, base + 3,
		                 stage123_mul[1], stage123_pre[1]);
		scalar_butterfly(out, base + 4, base + 6,
		                 stage123_mul[0], stage123_pre[0]);
		scalar_butterfly(out, base + 5, base + 7,
		                 stage123_mul[1], stage123_pre[1]);

		scalar_butterfly(out, base + 0, base + 4,
		                 stage123_mul[0], stage123_pre[0]);
		scalar_butterfly(out, base + 1, base + 5,
		                 stage123_mul[2], stage123_pre[2]);
		scalar_butterfly(out, base + 2, base + 6,
		                 stage123_mul[3], stage123_pre[3]);
		scalar_butterfly(out, base + 3, base + 7,
		                 stage123_mul[4], stage123_pre[4]);
	}

	for (int j = 0; j < 8; j++)
	{
		scalar_butterfly(out, j, j + 8,
		                 stage45_mul[j][0], stage45_pre_scalar[j][0]);
		scalar_butterfly(out, j + 16, j + 24,
		                 stage45_mul[j][0], stage45_pre_scalar[j][0]);
		scalar_butterfly(out, j, j + 16,
		                 stage45_mul[j][1], stage45_pre_scalar[j][1]);
		scalar_butterfly(out, j + 8, j + 24,
		                 stage45_mul[j][2], stage45_pre_scalar[j][2]);
	}

	for (int i = 0; i < 32; i++)
	{
		out[i] = scalar_barrett(out[i]);
	}
}

static inline int16x8_t fqmul_vec(int16x8_t x, int16x8_t tw,
                                  int16x8_t pre)
{
	const int16x8_t qhat = vqrdmulhq_s16(x, pre);
	int16x8_t prod = vmulq_s16(x, tw);

	return vmlsq_n_s16(prod, qhat, NTRUPLUS_Q);
}

static inline int16x8_t barrett_vec(int16x8_t x)
{
	int16x8_t t = vqdmulhq_n_s16(x, 19412);

	t = vrshrq_n_s16(t, 11);
	return vmlsq_n_s16(x, t, NTRUPLUS_Q);
}

static inline int16x8_t butterfly_distance1(int16x8_t x)
{
	const uint16x8_t odd_mask = vld1q_u16(odd_lane_mask_data);
	const int16x8_t swap = vrev32q_s16(x);
	const int16x8_t sum = vaddq_s16(x, swap);
	const int16x8_t high = vsubq_s16(swap, x);

	return vbslq_s16(odd_mask, high, sum);
}

static inline int16x8_t swap_distance2(int16x8_t x)
{
	return vreinterpretq_s16_s32(
		vrev64q_s32(vreinterpretq_s32_s16(x)));
}

static inline int16x8_t butterfly_distance2(int16x8_t x)
{
	const uint16x8_t high_mask = vld1q_u16(high2_lane_mask_data);
	const int16x8_t swap = swap_distance2(x);
	const int16x8_t tw = vld1q_s16(stage2_twiddles);
	const int16x8_t pre = vld1q_s16(stage2_pre);
	const int16x8_t hi_src = vbslq_s16(high_mask, x, swap);
	const int16x8_t lo_src = vbslq_s16(high_mask, swap, x);
	const int16x8_t prod = fqmul_vec(hi_src, tw, pre);
	const int16x8_t lo = vaddq_s16(lo_src, prod);
	const int16x8_t hi = vsubq_s16(lo_src, prod);

	return vbslq_s16(high_mask, hi, lo);
}

static inline int16x8_t butterfly_distance4(int16x8_t x)
{
	const uint16x8_t high_mask = vld1q_u16(high4_lane_mask_data);
	const int16x8_t swap = vextq_s16(x, x, 4);
	const int16x8_t tw = vld1q_s16(stage3_twiddles);
	const int16x8_t pre = vld1q_s16(stage3_pre);
	const int16x8_t hi_src = vbslq_s16(high_mask, x, swap);
	const int16x8_t lo_src = vbslq_s16(high_mask, swap, x);
	const int16x8_t prod = fqmul_vec(hi_src, tw, pre);
	const int16x8_t lo = vaddq_s16(lo_src, prod);
	const int16x8_t hi = vsubq_s16(lo_src, prod);

	return vbslq_s16(high_mask, hi, lo);
}

static inline void butterfly_vec_pair(int16x8_t *lo, int16x8_t *hi,
                                      int table_col)
{
	const int16x8_t tw = vld1q_s16(stage45_twiddles[table_col]);
	const int16x8_t pre = vld1q_s16(stage45_pre[table_col]);
	const int16x8_t old_lo = *lo;
	const int16x8_t prod = fqmul_vec(*hi, tw, pre);

	*lo = vaddq_s16(*lo, prod);
	*hi = vsubq_s16(old_lo, prod);
}

static void rowpack_invntt32_neon(int16_t out[32], const int16_t in[32])
{
	int16x8_t x0 = vld1q_s16(&in[0]);
	int16x8_t x1 = vld1q_s16(&in[8]);
	int16x8_t x2 = vld1q_s16(&in[16]);
	int16x8_t x3 = vld1q_s16(&in[24]);

	x0 = barrett_vec(x0);
	x1 = barrett_vec(x1);
	x2 = barrett_vec(x2);
	x3 = barrett_vec(x3);

	x0 = butterfly_distance1(x0);
	x1 = butterfly_distance1(x1);
	x2 = butterfly_distance1(x2);
	x3 = butterfly_distance1(x3);

	x0 = butterfly_distance2(x0);
	x1 = butterfly_distance2(x1);
	x2 = butterfly_distance2(x2);
	x3 = butterfly_distance2(x3);

	x0 = butterfly_distance4(x0);
	x1 = butterfly_distance4(x1);
	x2 = butterfly_distance4(x2);
	x3 = butterfly_distance4(x3);

	butterfly_vec_pair(&x0, &x1, 0);
	butterfly_vec_pair(&x2, &x3, 0);
	butterfly_vec_pair(&x0, &x2, 1);
	butterfly_vec_pair(&x1, &x3, 2);

	x0 = barrett_vec(x0);
	x1 = barrett_vec(x1);
	x2 = barrett_vec(x2);
	x3 = barrett_vec(x3);

	vst1q_s16(&out[0], x0);
	vst1q_s16(&out[8], x1);
	vst1q_s16(&out[16], x2);
	vst1q_s16(&out[24], x3);
}

#ifdef TEST_ROWPACK_INVNTT32_ASM
static void rowpack_invntt32_asm(int16_t out[32], const int16_t in[32])
{
	memcpy(out, in, 32 * sizeof(out[0]));
	ntruplus768_invntt32_rowpack_soa_row(
		out, ntruplus768_invntt32_rowpack_soa_row_consts);
}
#endif

static void fill_input(int16_t in[32], unsigned pattern, uint32_t seed)
{
	for (int i = 0; i < 32; i++)
	{
		switch (pattern)
		{
		case 0:
			in[i] = 0;
			break;
		case 1:
			in[i] = 1;
			break;
		case 2:
			in[i] = (i & 1) ? -1 : 1;
			break;
		default:
			in[i] =
				(int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) -
				          NTRUPLUS_Q);
			break;
		}
	}
}

static int compare_rows(const char *label, const int16_t got[32],
                        const int16_t want[32])
{
	for (int i = 0; i < 32; i++)
	{
		if (got[i] != want[i])
		{
			fprintf(stderr,
			        "%s mismatch at %d: got %d want %d abs_in=%d\n",
			        label,
			        i,
			        got[i],
			        want[i],
			        abs_i(want[i]));
			return 0;
		}
	}

	return 1;
}

int main(void)
{
	int16_t in[32];
	int16_t got[32];
	int16_t want[32];

	for (unsigned pattern = 0; pattern < 4; pattern++)
	{
		fill_input(in, pattern, 0x12345678u + pattern);
		scalar_invntt32_row_end(want, in);
		rowpack_invntt32_neon(got, in);

		if (!compare_rows("rowpack intt32 pattern", got, want))
		{
			return 1;
		}

#ifdef TEST_ROWPACK_INVNTT32_ASM
		rowpack_invntt32_asm(got, in);

		if (!compare_rows("rowpack intt32 asm pattern", got, want))
		{
			return 1;
		}
#endif
	}

	for (int t = 0; t < RANDOM_TESTS; t++)
	{
		fill_input(in, 3, 0x9e3779b9u + (uint32_t)t);
		scalar_invntt32_row_end(want, in);
		rowpack_invntt32_neon(got, in);

		if (!compare_rows("rowpack intt32 random", got, want))
		{
			return 1;
		}

#ifdef TEST_ROWPACK_INVNTT32_ASM
		rowpack_invntt32_asm(got, in);

		if (!compare_rows("rowpack intt32 asm random", got, want))
		{
			return 1;
		}
#endif
	}

	printf("rowpack SoA invntt32 Neon row model: ok\n");
	return 0;
}
