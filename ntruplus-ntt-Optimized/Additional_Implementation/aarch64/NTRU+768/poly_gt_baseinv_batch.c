#include <stdint.h>
#include <string.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#if defined(__aarch64__)
#include <arm_neon.h>
#endif

#if NTRUPLUS_N != 768
#error "GT batch baseinv is specialized for NTRU+768"
#endif

#define GT_BASEINV_BRANCHES 2
#define GT_BASEINV_BRANCH_N (NTRUPLUS_N / GT_BASEINV_BRANCHES)
#define GT_BASEINV_BLOCKS_PER_BRANCH 96
#define GT_BASEINV_ROWS 3
#define GT_BASEINV_ROW_N 32
#define GT_BASEINV_QUARTIC_LANES 4

int poly_baseinv_gt_batch(poly *r, const poly *a);
int poly_baseinv_gt_batch_scaled_r(poly *r, const poly *a);
int poly_baseinv_gt_tuple_batch(poly *r, const poly *a);
int poly_baseinv_scaled_r(poly *r, const poly *a);

#if defined(__aarch64__)
void baseinv_batch_finish24_n1_asm(int16_t *dst, const int16_t *den_inv);
#if defined(GT_BASEINV_USE_FQINV15_ASM)
int16x8_t gt_fqinv15_asm(int16x8_t a, int16x8_t con);
#endif

static const int16_t gt_baseinv_consts[8] __attribute__((aligned(16))) = {
	3457, 19412, -12929, -147, -1393, -1571, -14891, 0
};

static const int16_t gt_baseinv_scaled_r_consts[8]
	__attribute__((aligned(16))) = {
	3457, 19412, -12929, -147, -1393, -682, -6464, 0
};

static const int16_t gt_tuple_baseinv_lambda[GT_BASEINV_BRANCHES]
                                             [GT_BASEINV_BLOCKS_PER_BRANCH / 8]
                                             [8] __attribute__((aligned(16))) = {
	{
		{   1655,  -1655,    183,   -183,  -1674,   1674,   -559,    559 },
		{   -397,    397,   1059,  -1059,   -223,    223,  -1138,   1138 },
		{    242,   -242,   1514,  -1514,    432,   -432,  -1640,   1640 },
		{    437,   -437,  -1723,   1723,   -277,    277,   -933,    933 },
		{   -443,    443,   -943,    943,    352,   -352,   -312,    312 },
		{    100,   -100,  -1660,   1660,  -1250,   1250,      8,     -8 },
		{   1341,  -1341,   1247,  -1247,  -1206,   1206,    -31,     31 },
		{  -1364,   1364,   1209,  -1209,   -235,    235,    444,   -444 },
		{  -1212,   1212,    760,   -760,   1322,  -1322,    871,   -871 },
		{    297,   -297,    601,   -601,   1473,  -1473,   1130,  -1130 },
		{  -1583,   1583,    696,   -696,    774,   -774,   1671,  -1671 },
		{    927,   -927,    514,   -514,    512,   -512,    489,   -489 }
	},
	{
		{    779,   -779,   1588,  -1588,  -1095,   1095,    892,   -892 },
		{   1221,  -1221,   -218,    218,    294,   -294,   -732,    732 },
		{     22,    -22,   1709,  -1709,   -275,    275,   1108,  -1108 },
		{    354,   -354,  -1728,   1728,   -968,    968,    858,   -858 },
		{    274,   -274,   -400,    400,     32,    -32,   1543,  -1543 },
		{  -1248,   1248,  -1408,   1408,  -1685,   1685,    315,   -315 },
		{   1379,  -1379,  -1458,   1458,  -1681,   1681,    940,   -940 },
		{   -124,    124,   1367,  -1367,   1550,  -1550,  -1531,   1531 },
		{  -1053,   1053,  -1188,   1188,   1063,  -1063,   1022,  -1022 },
		{     27,    -27,   1626,  -1626,   1391,  -1391,    417,   -417 },
		{  -1401,   1401,   -251,    251,  -1501,   1501,   1409,  -1409 },
		{   -230,    230,    361,   -361,   -582,    582,    673,   -673 }
	}
};

static inline int16x8_t montgomery_reduce_vec(int32x4_t lo, int32x4_t hi,
                                              int16x8_t con)
{
	int16x8_t t;

	t = vuzp1q_s16(vreinterpretq_s16_s32(lo),
	               vreinterpretq_s16_s32(hi));
	t = vmulq_laneq_s16(t, con, 2);
	lo = vmlal_lane_s16(lo, vget_low_s16(t), vget_low_s16(con), 0);
	hi = vmlal_high_lane_s16(hi, t, vget_low_s16(con), 0);

	return vuzp2q_s16(vreinterpretq_s16_s32(lo),
	                  vreinterpretq_s16_s32(hi));
}

static inline int16x8_t fqmul_neon(int16x8_t x, int16x8_t y, int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(x), vget_low_s16(y));
	int32x4_t hi = vmull_high_s16(x, y);

	return montgomery_reduce_vec(lo, hi, con);
}

static inline int16x8_t reduce_mul2(int16x8_t a0, int16x8_t b0,
                                    int16x8_t a1, int16x8_t b1,
                                    int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(a0), vget_low_s16(b0));
	int32x4_t hi = vmull_high_s16(a0, b0);

	lo = vmlal_s16(lo, vget_low_s16(a1), vget_low_s16(b1));
	hi = vmlal_high_s16(hi, a1, b1);

	return montgomery_reduce_vec(lo, hi, con);
}

static inline int16x8_t reduce_mul3(int16x8_t a0, int16x8_t b0,
                                    int16x8_t a1, int16x8_t b1,
                                    int16x8_t a2, int16x8_t b2,
                                    int16x8_t con)
{
	int32x4_t lo = vmull_s16(vget_low_s16(a0), vget_low_s16(b0));
	int32x4_t hi = vmull_high_s16(a0, b0);

	lo = vmlal_s16(lo, vget_low_s16(a1), vget_low_s16(b1));
	hi = vmlal_high_s16(hi, a1, b1);
	lo = vmlal_s16(lo, vget_low_s16(a2), vget_low_s16(b2));
	hi = vmlal_high_s16(hi, a2, b2);

	return montgomery_reduce_vec(lo, hi, con);
}

static inline int16x8_t fqinv_neon(int16x8_t a, int16x8_t con)
{
#if defined(GT_BASEINV_USE_FQINV15_ASM)
	return gt_fqinv15_asm(a, con);
#else
	int16x8_t t, t16, t128, t145, t691, u;

	t = fqmul_neon(a, a, con);       // 2
	t = fqmul_neon(t, t, con);       // 4
	t = fqmul_neon(t, t, con);       // 8
	t16 = fqmul_neon(t, t, con);     // 16

	t = fqmul_neon(t16, t16, con);   // 32
	t = fqmul_neon(t, t, con);       // 64
	t128 = fqmul_neon(t, t, con);    // 128

	t = fqmul_neon(t128, t16, con);  // 144
	t145 = fqmul_neon(t, a, con);    // 145
	t = fqmul_neon(t145, t128, con); // 273
	t = fqmul_neon(t, t, con);       // 546
	t691 = fqmul_neon(t, t145, con); // 691

	t = fqmul_neon(t691, t691, con); // 1382
	t = fqmul_neon(t, t, con);       // 2764
	t = fqmul_neon(t, t691, con);    // 3455

	u = vqrdmulhq_laneq_s16(t, con, 6);
	t = vmulq_laneq_s16(t, con, 5);
	t = vmlsq_laneq_s16(t, u, con, 0);

	return t;
#endif
}

static int poly_fqinv_batch_neon(int16x8_t r[24], int16x8_t con)
{
	int16x8_t c[24];
	int16x8_t inv;

	c[0] = r[0];
	for (int i = 1; i < 24; i++)
		c[i] = fqmul_neon(c[i - 1], r[i], con);

	if (!vminvq_u16(vreinterpretq_u16_s16(c[23])))
		return 1;

	inv = fqinv_neon(c[23], con);

	for (int i = 23; i > 0; i--)
	{
		int16x8_t ri = r[i];
		r[i] = fqmul_neon(c[i - 1], inv, con);
		inv = fqmul_neon(inv, ri, con);
	}

	r[0] = inv;
	return 0;
}

static void baseinv_8_prepare(int16_t *dst, int16x8_t *den,
                              const int16_t *src, int16x8_t zeta,
                              int16x8_t con)
{
	int16x8x4_t a = vld4q_s16(src);
	int16x8x4_t n;
	int16x8_t neg2a2 = vshlq_n_s16(vnegq_s16(a.val[2]), 1);
	int16x8_t neg2a3 = vshlq_n_s16(vnegq_s16(a.val[3]), 1);
	int16x8_t negt1;
	int16x8_t t0, t1, t2;

	t0 = reduce_mul2(a.val[2], a.val[2], a.val[1], neg2a3, con);
	t1 = fqmul_neon(a.val[3], a.val[3], con);

	t0 = reduce_mul2(t0, zeta, a.val[0], a.val[0], con);
	t1 = reduce_mul3(t1, zeta, a.val[1], a.val[1],
	                 a.val[0], neg2a2, con);
	t2 = fqmul_neon(t1, zeta, con);

	negt1 = vnegq_s16(t1);
	*den = reduce_mul2(t0, t0, negt1, t2, con);

	n.val[0] = reduce_mul2(a.val[0], t0, a.val[2], t2, con);
	n.val[1] = reduce_mul2(a.val[3], t2, a.val[1], t0, con);
	n.val[2] = reduce_mul2(a.val[2], t0, a.val[0], t1, con);
	n.val[3] = reduce_mul2(a.val[1], t1, a.val[3], t0, con);

	vst4q_s16(dst, n);
}

static void baseinv_8_finish(int16_t *dst, int16x8_t den_inv, int16x8_t con)
{
	int16x8x4_t n = vld4q_s16(dst);
	int16x8_t neg_den_inv = vnegq_s16(den_inv);

	n.val[0] = fqmul_neon(n.val[0], den_inv, con);
	n.val[1] = fqmul_neon(n.val[1], neg_den_inv, con);
	n.val[2] = fqmul_neon(n.val[2], den_inv, con);
	n.val[3] = fqmul_neon(n.val[3], neg_den_inv, con);

	vst4q_s16(dst, n);
}

static int poly_baseinv_batch_block_major_neon(poly *r, const poly *a,
                                               const int16_t consts[8])
{
	int16x8_t con = vld1q_s16(consts);
	int16x8_t den[24] __attribute__((aligned(16)));
	const int16_t *src = a->coeffs;
	int16_t *dst = r->coeffs;
	const int16_t *lambda = &gt_rowbitrev_lambda[0][0];

	for (int i = 0; i < 24; i++)
	{
		int16x8_t zeta = vld1q_s16(lambda);

		baseinv_8_prepare(dst, &den[i], src, zeta, con);
		src += 8 * GT_BASEINV_QUARTIC_LANES;
		dst += 8 * GT_BASEINV_QUARTIC_LANES;
		lambda += 8;
	}

	if (poly_fqinv_batch_neon(den, con))
	{
		memset(r->coeffs, 0, sizeof(r->coeffs));
		return 1;
	}

#ifdef GT_BASEINV_BATCH_USE_ASM_FINISH
	(void)con;
	baseinv_batch_finish24_n1_asm(r->coeffs, (const int16_t *)den);
#else
	dst = r->coeffs;
	for (int i = 0; i < 24; i++)
	{
		baseinv_8_finish(dst, den[i], con);
		dst += 8 * GT_BASEINV_QUARTIC_LANES;
	}
#endif

	return 0;
}

static int poly_baseinv_batch_tuple_neon(poly *r, const poly *a)
{
	int16x8_t con = vld1q_s16(gt_baseinv_consts);
	int16x8_t den[24] __attribute__((aligned(16)));
	int den_index = 0;

	for (int branch = 0; branch < GT_BASEINV_BRANCHES; branch++)
	{
		for (int block = 0; block < GT_BASEINV_BLOCKS_PER_BRANCH; block += 8)
		{
			const int lambda_index = block >> 3;
			const int pos =
				branch * GT_BASEINV_BRANCH_N +
				GT_BASEINV_QUARTIC_LANES * block;

			baseinv_8_prepare(r->coeffs + pos, &den[den_index],
			                  a->coeffs + pos,
			                  vld1q_s16(gt_tuple_baseinv_lambda[branch]
			                                                     [lambda_index]),
			                  con);
			den_index++;
		}
	}

	if (poly_fqinv_batch_neon(den, con))
	{
		memset(r->coeffs, 0, sizeof(r->coeffs));
		return 1;
	}

#ifdef GT_BASEINV_BATCH_USE_ASM_FINISH
	(void)con;
	baseinv_batch_finish24_n1_asm(r->coeffs, (const int16_t *)den);
#else
	den_index = 0;
	for (int branch = 0; branch < GT_BASEINV_BRANCHES; branch++)
	{
		for (int block = 0; block < GT_BASEINV_BLOCKS_PER_BRANCH; block += 8)
		{
			const int pos =
				branch * GT_BASEINV_BRANCH_N +
				GT_BASEINV_QUARTIC_LANES * block;

			baseinv_8_finish(r->coeffs + pos, den[den_index], con);
			den_index++;
		}
	}
#endif

	return 0;
}
#endif

int poly_baseinv_gt_batch(poly *r, const poly *a)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_neon(r, a, gt_baseinv_consts);
#else
	for (int branch = 0; branch < GT_BASEINV_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BASEINV_BRANCH_N;

		for (int physical_j = 0; physical_j < GT_BASEINV_BLOCKS_PER_BRANCH;
		     physical_j++)
		{
			const int pos =
				branch_start + GT_BASEINV_QUARTIC_LANES * physical_j;

			if (baseinv(r->coeffs + pos, a->coeffs + pos,
			            gt_rowbitrev_lambda[branch][physical_j]))
			{
				memset(r->coeffs, 0, sizeof(r->coeffs));
				return 1;
			}
		}
	}

	return 0;
#endif
}

int poly_baseinv_gt_batch_scaled_r(poly *r, const poly *a)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_neon(r, a,
	                                          gt_baseinv_scaled_r_consts);
#else
	if (poly_baseinv_gt_batch(r, a))
		return 1;

	for (int i = 0; i < NTRUPLUS_N; i++)
	{
		int32_t v = (int32_t)r->coeffs[i] * -147;

		v %= NTRUPLUS_Q;
		if (v > NTRUPLUS_Q / 2)
			v -= NTRUPLUS_Q;
		if (v < -NTRUPLUS_Q / 2)
			v += NTRUPLUS_Q;
		r->coeffs[i] = (int16_t)v;
	}

	return 0;
#endif
}

int poly_baseinv_gt_tuple_batch(poly *r, const poly *a)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_tuple_neon(r, a);
#else
	for (int branch = 0; branch < GT_BASEINV_BRANCHES; branch++)
	{
		const int branch_start = branch * GT_BASEINV_BRANCH_N;

		for (int row = 0; row < GT_BASEINV_ROWS; row++)
		{
			for (int k32 = 0; k32 < GT_BASEINV_ROW_N; k32++)
			{
				const int block = row * GT_BASEINV_ROW_N + k32;
				const int physical_j =
					(GT_BASEINV_ROW_N * row + GT_BASEINV_ROWS * k32) %
					GT_BASEINV_BLOCKS_PER_BRANCH;
				const int pos =
					branch_start + GT_BASEINV_QUARTIC_LANES * block;

				if (baseinv(r->coeffs + pos, a->coeffs + pos,
				            gt_rowbitrev_lambda[branch][physical_j]))
				{
					memset(r->coeffs, 0, sizeof(r->coeffs));
					return 1;
				}
			}
		}
	}

	return 0;
#endif
}

#ifndef GT_BASEINV_BATCH_NO_ABI_WRAPPER
int poly_baseinv(poly *r, const poly *a)
{
	return poly_baseinv_gt_batch(r, a);
}
#endif

int poly_baseinv_scaled_r(poly *r, const poly *a)
{
	return poly_baseinv_gt_batch_scaled_r(r, a);
}
