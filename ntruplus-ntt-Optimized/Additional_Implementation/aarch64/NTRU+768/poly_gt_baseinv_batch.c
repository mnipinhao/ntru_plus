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
#if defined(GT_BASEINV_USE_HIER_K8) || \
    defined(GT_BASEINV_HIER_K8_DIFF_HELPERS) || \
    defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
int poly_baseinv_scaled_r_hier_k8_candidate(poly *r, const poly *a);
#endif
#if defined(GT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS)
int poly_keygen_baseinv_scaled_r_x2_direct_model(poly *finv, poly *ginv,
                                                 const poly *f,
                                                 const poly *g);
int poly_keygen_compute_h_hinv_direct_model(poly *h, poly *hinv,
                                            const poly *f, const poly *g);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
#endif
#if defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
int poly_baseinv_scaled_r_hier_k8_prepare_for_bench(poly *num,
                                                    int16_t den[24 * 8],
                                                    const poly *a);
int poly_baseinv_scaled_r_hier_k8_tree_for_bench(int16_t den[24 * 8]);
void poly_baseinv_scaled_r_finish_for_bench(poly *out, const poly *num,
                                            const int16_t den_inv[24 * 8]);
void gt_baseinv_fqinv15_x2_for_bench(int16_t f[8], int16_t g[8]);
#endif
#if defined(GT_BASEINV_HIER_K8_DIFF_HELPERS)
int poly_baseinv_scaled_r_current_reference(poly *r, const poly *a);
int poly_baseinv_scaled_r_fqinv16_reference(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_fqinv16_candidate(poly *r, const poly *a);
#endif
#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
int16_t fqinv_divstep_scalar_ref(int16_t a, int scaled_r);
int16x8_t fqinv_divstep_neon_intrinsics(int16x8_t a, int16x8_t con,
                                         int16_t final_scale);
#if defined(GT_BASEINV_USE_DIVSTEP_ASM)
int16x8_t gt_fqinv_delta_divstep_asm(int16x8_t a, int16x8_t con,
                                      int16_t final_scale);
#endif
#if defined(GT_BASEINV_USE_DIVSTEP_S32FOLD_ASM)
int16x8_t gt_fqinv_delta_divstep_s32fold_asm(int16x8_t a, int16x8_t con,
                                              int16_t final_scale);
#endif
#if defined(GT_BASEINV_USE_DIVSTEP_MODQ16_ASM)
int16x8_t gt_fqinv_delta_divstep_modq16_asm(int16x8_t a, int16x8_t con,
                                             int16_t final_scale);
#endif
#if defined(GT_BASEINV_USE_DIVSTEP_LAZY16_ASM)
int16x8_t gt_fqinv_delta_divstep_lazy16_asm(int16x8_t a, int16x8_t con,
                                             int16_t final_scale);
#endif
#if defined(GT_BASEINV_USE_DIVSTEP_SWAR_ASM)
int16x8_t gt_fqinv_delta_divstep_swar_asm(int16x8_t a, int16x8_t con,
                                           int16_t final_scale);
#endif
void gt_baseinv_fqinv_current_vec_for_bench(int16_t out[8],
                                            const int16_t in[8],
                                            int scaled_r);
void gt_baseinv_fqinv16_vec_for_bench(int16_t out[8],
                                      const int16_t in[8],
                                      int scaled_r);
void gt_baseinv_fqinv_divstep_vec_for_bench(int16_t out[8],
                                            const int16_t in[8],
                                            int scaled_r);
int gt_baseinv_fqinv16_24_for_bench(int16_t r[24 * 8]);
int gt_baseinv_fqinv_divstep_24_for_bench(int16_t r[24 * 8]);
int gt_baseinv_fqinv_hier_kway_divstep_for_bench(int16_t *r, int m, int k);
int poly_baseinv_gt_batch_scaled_r_fqinv16_for_bench(poly *r,
                                                     const poly *a);
int poly_baseinv_gt_batch_scaled_r_divstep_for_bench(poly *r,
                                                     const poly *a);
int poly_baseinv_gt_batch_scaled_r_hier_kway_divstep_for_bench(poly *r,
                                                               const poly *a,
                                                               int k);
#endif
#if defined(GT_BASEINV_KWAY_BENCH_HELPERS)
int gt_baseinv_fqinv_batch_old_24_for_bench(int16_t r[24 * 8]);
int gt_baseinv_fqinv_batch_new_24_for_bench(int16_t r[24 * 8]);
int gt_baseinv_fqinv_kway_new_24_for_bench(int16_t r[24 * 8], int k);
int gt_baseinv_fqinv_batch_new_36_for_bench(int16_t r[36 * 8]);
int gt_baseinv_fqinv_kway_new_36_for_bench(int16_t r[36 * 8], int k);
int gt_baseinv_fqinv_batch_current_m_for_bench(int16_t *r, int m);
int gt_baseinv_fqinv_flat_kway_current_for_bench(int16_t *r, int m, int k);
int gt_baseinv_fqinv_hier_kway_current_for_bench(int16_t *r, int m, int k);
void gt_baseinv_fqinv_current_extra_fqmul_vec_for_bench(
	int16_t out[8], const int16_t in[8], const int16_t mul[8], int extra);
void gt_baseinv_fqmul_vec_for_bench(int16_t out[8], const int16_t a[8],
                                    const int16_t b[8]);
int poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(poly *r, const poly *a,
                                                      int k);
int poly_baseinv_gt_batch_scaled_r_flat_kway_current_for_bench(poly *r,
                                                               const poly *a,
                                                               int k);
int poly_baseinv_gt_batch_scaled_r_hier_kway_current_for_bench(poly *r,
                                                               const poly *a,
                                                               int k);
#endif

#if defined(GT_BASEINV_HIER_K8_NO_CANON) && \
    defined(GT_BASEINV_HIER_K8_OUTPUT_CANON)
#error "select only one GT_BASEINV_HIER_K8 canonicalization mode"
#endif

#if defined(GT_BASEINV_HIER_K8_NO_CANON) && \
    defined(GT_BASEINV_HIER_K8_EACH_INV_CANON)
#error "select only one GT_BASEINV_HIER_K8 canonicalization mode"
#endif

#if defined(GT_BASEINV_HIER_K8_OUTPUT_CANON) && \
    defined(GT_BASEINV_HIER_K8_EACH_INV_CANON)
#error "select only one GT_BASEINV_HIER_K8 canonicalization mode"
#endif

#if defined(GT_BASEINV_USE_HIER_K8) && !defined(__aarch64__)
#error "GT_BASEINV_USE_HIER_K8 is an AArch64/Neon-only backend"
#endif

#if defined(GT_BASEINV_USE_HIER_K8) && !defined(GT_BASEINV_USE_FQINV15_ASM)
#error "GT_BASEINV_USE_HIER_K8 requires GT_BASEINV_USE_FQINV15_ASM"
#endif

#if defined(GT_BASEINV_USE_HIER_K8_TREE) && !defined(GT_BASEINV_USE_HIER_K8)
#error "GT_BASEINV_USE_HIER_K8_TREE requires GT_BASEINV_USE_HIER_K8"
#endif

#if defined(GT_BASEINV_USE_HIER_K8) && \
    (defined(GT_BASEINV_HIER_K8_OUTPUT_CANON) || \
     defined(GT_BASEINV_HIER_K8_EACH_INV_CANON))
#error "GT_BASEINV_USE_HIER_K8 is the no-canon fqinv15_asm candidate only"
#endif

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

#if defined(GT_BASEINV_HIER_K8_DIFF_HELPERS)
static int16_t center_modq_i16(int16_t x)
{
	int32_t y = x;

	y %= NTRUPLUS_Q;
	if (y < 0)
		y += NTRUPLUS_Q;
	if (y > NTRUPLUS_Q / 2)
		y -= NTRUPLUS_Q;
	return (int16_t)y;
}

static void center_vec_array_modq(int16x8_t *v, int nvec)
{
	int16_t *p = (int16_t *)v;

	for (int i = 0; i < 8 * nvec; i++)
		p[i] = center_modq_i16(p[i]);
}

static void center_poly_modq(poly *r)
{
	for (int i = 0; i < NTRUPLUS_N; i++)
		r->coeffs[i] = center_modq_i16(r->coeffs[i]);
}
#endif

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

static inline int16x8_t fqinv_new_neon(int16x8_t a, int16x8_t con)
{
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
}

#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
static inline int16x8_t fqinv16_neon(int16x8_t a, int16x8_t con)
{
	int16x8_t t1, t2, t3;

	t1 = fqmul_neon(a, a, con);     // 10
	t2 = fqmul_neon(t1, t1, con);   // 100
	t2 = fqmul_neon(t2, t2, con);   // 1000
	t3 = fqmul_neon(t2, t2, con);   // 10000

	t1 = fqmul_neon(t1, t2, con);   // 1010

	t2 = fqmul_neon(t1, t3, con);   // 11010
	t2 = fqmul_neon(t2, t2, con);   // 110100
	t2 = fqmul_neon(t2, a, con);    // 110101

	t1 = fqmul_neon(t1, t2, con);   // 111111

	t2 = fqmul_neon(t2, t2, con);   // 1101010
	t2 = fqmul_neon(t2, t2, con);   // 11010100
	t2 = fqmul_neon(t2, t2, con);   // 110101000
	t2 = fqmul_neon(t2, t2, con);   // 1101010000
	t2 = fqmul_neon(t2, t2, con);   // 11010100000
	t2 = fqmul_neon(t2, t2, con);   // 110101000000
	t2 = fqmul_neon(t2, t1, con);   // 110101111111

	t1 = vqrdmulhq_laneq_s16(t2, con, 6);
	t2 = vmulq_laneq_s16(t2, con, 5);
	t2 = vmlsq_laneq_s16(t2, t1, con, 0);

	return t2;
}

#define GT_BASEINV_DELTA_SCALE_NORMAL (-1082)
#define GT_BASEINV_DELTA_SCALE_SCALED_R 32
#define GT_BASEINV_DELTA_REDUCE_RECIP 621199

static int32_t divstep_modq_i32(int32_t x)
{
	x %= NTRUPLUS_Q;
	if (x < 0)
		x += NTRUPLUS_Q;
	return x;
}

static int16_t divstep_center_i32(int32_t x)
{
	x = divstep_modq_i32(x);
	if (x > NTRUPLUS_Q / 2)
		x -= NTRUPLUS_Q;
	return (int16_t)x;
}

static int32_t delta_divstep_v_scalar(int16_t a, int16_t *final_f)
{
	int32_t f = NTRUPLUS_Q;
	int32_t g = divstep_modq_i32(a);
	int32_t delta2 = 1;
	int32_t vcoef = 0;
	int32_t rcoef = 1;

	for (int i = 0; i < 27; i++)
	{
		int32_t s = delta2 >= 0;
		int32_t t = g & 1;
		int32_t active = s & t;
		int32_t f0 = f;
		int32_t g0 = g;
		int32_t delta20 = delta2;
		int32_t vcoef0 = vcoef;
		int32_t rcoef0 = rcoef;

		f = active ? g0 : f0;
		g = (g0 + (t ? (s ? -f0 : f0) : 0)) >> 1;
		delta2 = (active ? -delta20 : delta20) + 2;
		vcoef = active ? 2 * rcoef0 : 2 * vcoef0;
		rcoef = rcoef0 + (t ? (s ? -vcoef0 : vcoef0) : 0);
	}

	*final_f = (int16_t)f;
	return vcoef;
}

int16_t fqinv_divstep_scalar_ref(int16_t a, int scaled_r)
{
	int32_t x = divstep_modq_i32(a);
	int16_t final_f;
	int32_t vcoef;
	int64_t scaled;

	if (x == 0)
		return 0;

	vcoef = delta_divstep_v_scalar((int16_t)x, &final_f);
	if (final_f < 0)
		vcoef = -vcoef;

	/*
	 * The delta2 divstep leaves a * V = final_f * 2^27 mod q.
	 * Apply final_f and 2^-27 once after the fixed 27 iterations.
	 */
	scaled = (int64_t)vcoef * (scaled_r ? 2375 : 1583);
	return divstep_center_i32((int32_t)(scaled % NTRUPLUS_Q));
}

static inline int32x4_t selectq_s32(uint32x4_t mask, int32x4_t a,
                                    int32x4_t b)
{
	return vreinterpretq_s32_u32(
		vbslq_u32(mask, vreinterpretq_u32_s32(a),
		          vreinterpretq_u32_s32(b)));
}

static inline int16x8_t selectq_s16(uint16x8_t mask, int16x8_t a,
                                    int16x8_t b)
{
	return vreinterpretq_s16_u16(
		vbslq_u16(mask, vreinterpretq_u16_s16(a),
		          vreinterpretq_u16_s16(b)));
}

static inline uint32x4_t mask16_low_to_u32(uint16x8_t mask)
{
	return vreinterpretq_u32_s32(
		vmovl_s16(vreinterpret_s16_u16(vget_low_u16(mask))));
}

static inline uint32x4_t mask16_high_to_u32(uint16x8_t mask)
{
	return vreinterpretq_u32_s32(
		vmovl_s16(vreinterpret_s16_u16(vget_high_u16(mask))));
}

static inline int16x8_t normalize_modq_s16(int16x8_t x)
{
	const int16x8_t zero = vdupq_n_s16(0);
	const int16x8_t q = vdupq_n_s16(NTRUPLUS_Q);

	x = selectq_s16(vcltq_s16(x, zero), vaddq_s16(x, q), x);
	x = selectq_s16(vcgeq_s16(x, q), vsubq_s16(x, q), x);
	return x;
}

static inline int16x8_t pack_s32_to_s16(int32x4_t lo, int32x4_t hi)
{
	return vcombine_s16(vmovn_s32(lo), vmovn_s32(hi));
}

static inline int16x8_t reduce_s32_modq_to_s16(int32x4_t lo, int32x4_t hi)
{
	const int32x4_t recip = vdupq_n_s32(GT_BASEINV_DELTA_REDUCE_RECIP);
	const int32x4_t q = vdupq_n_s32(NTRUPLUS_Q);
	int32x4_t qlo = vqrdmulhq_s32(lo, recip);
	int32x4_t qhi = vqrdmulhq_s32(hi, recip);

	lo = vmlsq_s32(lo, qlo, q);
	hi = vmlsq_s32(hi, qhi, q);
	return pack_s32_to_s16(lo, hi);
}

int16x8_t fqinv_divstep_neon_intrinsics(int16x8_t a, int16x8_t con,
                                        int16_t final_scale)
{
	int16x8_t amod = normalize_modq_s16(a);
	int16x8_t f = vdupq_n_s16(NTRUPLUS_Q);
	int16x8_t g = amod;
	int16x8_t delta2 = vdupq_n_s16(1);
	int32x4_t vlo = vdupq_n_s32(0);
	int32x4_t vhi = vdupq_n_s32(0);
	int32x4_t rlo = vdupq_n_s32(1);
	int32x4_t rhi = vdupq_n_s32(1);
	const int16x8_t zero16 = vdupq_n_s16(0);
	const int16x8_t one16 = vdupq_n_s16(1);
	const int16x8_t two16 = vdupq_n_s16(2);
	const int32x4_t zero32 = vdupq_n_s32(0);

	for (int i = 0; i < 27; i++)
	{
		uint16x8_t s = vcgeq_s16(delta2, zero16);
		uint16x8_t t = vceqq_s16(vandq_s16(g, one16), one16);
		uint16x8_t active = vandq_u16(s, t);
		uint32x4_t slo = mask16_low_to_u32(s);
		uint32x4_t shi = mask16_high_to_u32(s);
		uint32x4_t tlo = mask16_low_to_u32(t);
		uint32x4_t thi = mask16_high_to_u32(t);
		uint32x4_t active_lo = mask16_low_to_u32(active);
		uint32x4_t active_hi = mask16_high_to_u32(active);
		int16x8_t f0 = f;
		int16x8_t g0 = g;
		int16x8_t delta20 = delta2;
		int32x4_t vlo0 = vlo;
		int32x4_t vhi0 = vhi;
		int32x4_t rlo0 = rlo;
		int32x4_t rhi0 = rhi;
		int16x8_t f_adjust = selectq_s16(s, vnegq_s16(f0), f0);
		int16x8_t g_add = selectq_s16(t, f_adjust, zero16);
		int32x4_t r_adjust_lo =
			selectq_s32(slo, vnegq_s32(vlo0), vlo0);
		int32x4_t r_adjust_hi =
			selectq_s32(shi, vnegq_s32(vhi0), vhi0);

		f = selectq_s16(active, g0, f0);
		g = vshrq_n_s16(vaddq_s16(g0, g_add), 1);
		delta2 = vaddq_s16(selectq_s16(active, vnegq_s16(delta20),
		                                delta20),
		                    two16);
		vlo = selectq_s32(active_lo, vshlq_n_s32(rlo0, 1),
		                  vshlq_n_s32(vlo0, 1));
		vhi = selectq_s32(active_hi, vshlq_n_s32(rhi0, 1),
		                  vshlq_n_s32(vhi0, 1));
		rlo = vaddq_s32(rlo0, selectq_s32(tlo, r_adjust_lo, zero32));
		rhi = vaddq_s32(rhi0, selectq_s32(thi, r_adjust_hi, zero32));
	}

	{
		uint32x4_t fneg_lo = mask16_low_to_u32(vcltq_s16(f, zero16));
		uint32x4_t fneg_hi = mask16_high_to_u32(vcltq_s16(f, zero16));
		int16x8_t vmod;
		int16x8_t out;
		uint16x8_t zero_mask = vceqq_s16(amod, zero16);

		vlo = selectq_s32(fneg_lo, vnegq_s32(vlo), vlo);
		vhi = selectq_s32(fneg_hi, vnegq_s32(vhi), vhi);
		vmod = reduce_s32_modq_to_s16(vlo, vhi);
		out = fqmul_neon(vmod, vdupq_n_s16(final_scale), con);

		return vreinterpretq_s16_u16(
			vbslq_u16(zero_mask, vreinterpretq_u16_s16(zero16),
			          vreinterpretq_u16_s16(out)));
	}
}

static inline int16x8_t fqinv_divstep_neon(int16x8_t a, int16x8_t con,
                                           int16_t final_scale)
{
#if defined(GT_BASEINV_USE_DIVSTEP_S32FOLD_ASM)
	return gt_fqinv_delta_divstep_s32fold_asm(a, con, final_scale);
#elif defined(GT_BASEINV_USE_DIVSTEP_LAZY16_ASM)
	return gt_fqinv_delta_divstep_lazy16_asm(a, con, final_scale);
#elif defined(GT_BASEINV_USE_DIVSTEP_MODQ16_ASM)
	return gt_fqinv_delta_divstep_modq16_asm(a, con, final_scale);
#elif defined(GT_BASEINV_USE_DIVSTEP_SWAR_ASM)
	return gt_fqinv_delta_divstep_swar_asm(a, con, final_scale);
#elif defined(GT_BASEINV_USE_DIVSTEP_ASM)
	return gt_fqinv_delta_divstep_asm(a, con, final_scale);
#else
	return fqinv_divstep_neon_intrinsics(a, con, final_scale);
#endif
}

static int poly_fqinv_batch_divstep_neon(int16x8_t r[24], int16x8_t con,
                                         int16_t final_scale)
{
	int16x8_t c[24];
	int16x8_t inv;

	c[0] = r[0];
	for (int i = 1; i < 24; i++)
		c[i] = fqmul_neon(c[i - 1], r[i], con);

	if (!vminvq_u16(vreinterpretq_u16_s16(c[23])))
		return 1;

	inv = fqinv_divstep_neon(c[23], con, final_scale);

	for (int i = 23; i > 0; i--)
	{
		int16x8_t ri = r[i];
		r[i] = fqmul_neon(c[i - 1], inv, con);
		inv = fqmul_neon(inv, ri, con);
	}

	r[0] = inv;
	return 0;
}

static int poly_fqinv_batch_divstep_m_neon(int16x8_t *r, int m,
                                           int16x8_t con,
                                           int16_t final_scale)
{
	int16x8_t c[36];
	int16x8_t inv;

	if (m <= 0 || m > 36)
		return 1;

	c[0] = r[0];
	for (int i = 1; i < m; i++)
		c[i] = fqmul_neon(c[i - 1], r[i], con);

	if (!vminvq_u16(vreinterpretq_u16_s16(c[m - 1])))
		return 1;

	inv = fqinv_divstep_neon(c[m - 1], con, final_scale);

	for (int i = m - 1; i > 0; i--)
	{
		int16x8_t ri = r[i];
		r[i] = fqmul_neon(c[i - 1], inv, con);
		inv = fqmul_neon(inv, ri, con);
	}

	r[0] = inv;
	return 0;
}

static int poly_fqinv_hier_kway_divstep_neon(int16x8_t *r, int m, int k,
                                             int16x8_t con,
                                             int16_t final_scale)
{
	int16x8_t c[36];
	int16x8_t group_prod[36];
	const int s = k == 0 ? 0 : m / k;

	if (m <= 0 || m > 36 || k <= 0 || k > m || (m % k) != 0)
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;

		c[start] = r[start];
		for (int i = start + 1; i < end; i++)
			c[i] = fqmul_neon(c[i - 1], r[i], con);
		group_prod[group] = c[end - 1];
	}

	if (poly_fqinv_batch_divstep_m_neon(group_prod, k, con, final_scale))
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;
		int16x8_t w = group_prod[group];

		for (int i = end - 1; i > start; i--)
		{
			int16x8_t ri = r[i];

			r[i] = fqmul_neon(c[i - 1], w, con);
			w = fqmul_neon(w, ri, con);
		}

		r[start] = w;
	}

	return 0;
}

static int poly_fqinv_batch_fqinv16_neon(int16x8_t r[24], int16x8_t con)
{
	int16x8_t c[24];
	int16x8_t inv;

	c[0] = r[0];
	for (int i = 1; i < 24; i++)
		c[i] = fqmul_neon(c[i - 1], r[i], con);

	if (!vminvq_u16(vreinterpretq_u16_s16(c[23])))
		return 1;

	inv = fqinv16_neon(c[23], con);

	for (int i = 23; i > 0; i--)
	{
		int16x8_t ri = r[i];
		r[i] = fqmul_neon(c[i - 1], inv, con);
		inv = fqmul_neon(inv, ri, con);
	}

	r[0] = inv;
	return 0;
}

#if defined(GT_BASEINV_HIER_K8_DIFF_HELPERS)
static int poly_fqinv_batch_fqinv16_m_neon(int16x8_t *r, int m,
                                           int16x8_t con)
{
	int16x8_t c[36];
	int16x8_t inv;

	if (m <= 0 || m > 36)
		return 1;

	c[0] = r[0];
	for (int i = 1; i < m; i++)
		c[i] = fqmul_neon(c[i - 1], r[i], con);

	if (!vminvq_u16(vreinterpretq_u16_s16(c[m - 1])))
		return 1;

	inv = fqinv16_neon(c[m - 1], con);

	for (int i = m - 1; i > 0; i--)
	{
		int16x8_t ri = r[i];
		r[i] = fqmul_neon(c[i - 1], inv, con);
		inv = fqmul_neon(inv, ri, con);
	}

	r[0] = inv;
	return 0;
}

static int poly_fqinv_hier_kway_fqinv16_neon(int16x8_t *r, int m, int k,
                                             int16x8_t con)
{
	int16x8_t c[36];
	int16x8_t group_prod[36];
	const int s = k == 0 ? 0 : m / k;

	if (m <= 0 || m > 36 || k <= 0 || k > m || (m % k) != 0)
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;

		c[start] = r[start];
		for (int i = start + 1; i < end; i++)
			c[i] = fqmul_neon(c[i - 1], r[i], con);
		group_prod[group] = c[end - 1];
	}

	if (poly_fqinv_batch_fqinv16_m_neon(group_prod, k, con))
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;
		int16x8_t w = group_prod[group];

		for (int i = end - 1; i > start; i--)
		{
			int16x8_t ri = r[i];

			r[i] = fqmul_neon(c[i - 1], w, con);
			w = fqmul_neon(w, ri, con);
		}

		r[start] = w;
	}

	return 0;
}
#endif
#endif

static inline int16x8_t fqinv_neon(int16x8_t a, int16x8_t con)
{
#if defined(GT_BASEINV_USE_FQINV15_ASM)
	return gt_fqinv15_asm(a, con);
#else
	return fqinv_new_neon(a, con);
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

#if defined(GT_BASEINV_USE_HIER_K8) || \
    defined(GT_BASEINV_HIER_K8_DIFF_HELPERS) || \
    defined(GT_BASEINV_KWAY_BENCH_HELPERS) || \
    defined(GT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS) || \
    defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
static int poly_fqinv_batch_current_m_neon(int16x8_t *r, int m, int16x8_t con)
{
	int16x8_t c[36];
	int16x8_t inv;

	if (m <= 0 || m > 36)
		return 1;

	c[0] = r[0];
	for (int i = 1; i < m; i++)
		c[i] = fqmul_neon(c[i - 1], r[i], con);

	if (!vminvq_u16(vreinterpretq_u16_s16(c[m - 1])))
		return 1;

	inv = fqinv_neon(c[m - 1], con);

	for (int i = m - 1; i > 0; i--)
	{
		int16x8_t ri = r[i];
		r[i] = fqmul_neon(c[i - 1], inv, con);
		inv = fqmul_neon(inv, ri, con);
	}

	r[0] = inv;
	return 0;
}
#endif

#if defined(GT_BASEINV_KWAY_BENCH_HELPERS)
static int poly_fqinv_flat_kway_current_neon(int16x8_t *r, int m, int k,
                                             int16x8_t con)
{
	int16x8_t c[36];
	int16x8_t inv[36];
	const int s = k == 0 ? 0 : m / k;

	if (m <= 0 || m > 36 || k <= 0 || k > m || (m % k) != 0)
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;

		c[start] = r[start];
		for (int i = start + 1; i < end; i++)
			c[i] = fqmul_neon(c[i - 1], r[i], con);

		if (!vminvq_u16(vreinterpretq_u16_s16(c[end - 1])))
			return 1;

		inv[group] = fqinv_neon(c[end - 1], con);
	}

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;
		int16x8_t w = inv[group];

		for (int i = end - 1; i > start; i--)
		{
			int16x8_t ri = r[i];

			r[i] = fqmul_neon(c[i - 1], w, con);
			w = fqmul_neon(w, ri, con);
		}

		r[start] = w;
	}

	return 0;
}
#endif

#if defined(GT_BASEINV_USE_HIER_K8) || \
    defined(GT_BASEINV_HIER_K8_DIFF_HELPERS) || \
    defined(GT_BASEINV_KWAY_BENCH_HELPERS) || \
    defined(GT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS) || \
    defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
static int poly_fqinv_hier_kway_current_neon(int16x8_t *r, int m, int k,
                                             int16x8_t con)
{
	int16x8_t c[36];
	int16x8_t group_prod[36];
	const int s = k == 0 ? 0 : m / k;

	if (m <= 0 || m > 36 || k <= 0 || k > m || (m % k) != 0)
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;

		c[start] = r[start];
		for (int i = start + 1; i < end; i++)
			c[i] = fqmul_neon(c[i - 1], r[i], con);
		group_prod[group] = c[end - 1];
	}

	if (poly_fqinv_batch_current_m_neon(group_prod, k, con))
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;
		int16x8_t w = group_prod[group];

		for (int i = end - 1; i > start; i--)
		{
			int16x8_t ri = r[i];

			r[i] = fqmul_neon(c[i - 1], w, con);
			w = fqmul_neon(w, ri, con);
		}

		r[start] = w;
	}

	return 0;
}
#endif

#if defined(GT_BASEINV_KWAY_BENCH_HELPERS)
static int poly_fqinv_kway_new_neon(int16x8_t *r, int m, int k,
                                    int16x8_t con)
{
	int16x8_t c[36];
	int16x8_t inv[36];
	const int s = k == 0 ? 0 : m / k;

	if (m <= 0 || m > 36 || k <= 0 || k > m || (m % k) != 0)
		return 1;

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;

		c[start] = r[start];
		for (int i = start + 1; i < end; i++)
			c[i] = fqmul_neon(c[i - 1], r[i], con);

		if (!vminvq_u16(vreinterpretq_u16_s16(c[end - 1])))
			return 1;

		inv[group] = fqinv_new_neon(c[end - 1], con);
	}

	for (int group = 0; group < k; group++)
	{
		const int start = group * s;
		const int end = start + s;
		int16x8_t w = inv[group];

		for (int i = end - 1; i > start; i--)
		{
			int16x8_t ri = r[i];

			r[i] = fqmul_neon(c[i - 1], w, con);
			w = fqmul_neon(w, ri, con);
		}

		r[start] = w;
	}

	return 0;
}

static void load_vec_array(int16x8_t *dst, const int16_t *src, int m)
{
	for (int i = 0; i < m; i++)
		dst[i] = vld1q_s16(src + 8 * i);
}

static void store_vec_array(int16_t *dst, const int16x8_t *src, int m)
{
	for (int i = 0; i < m; i++)
		vst1q_s16(dst + 8 * i, src[i]);
}

int gt_baseinv_fqinv_batch_old_24_for_bench(int16_t r[24 * 8])
{
	int16x8_t rv[24];
	int ret;

	load_vec_array(rv, r, 24);
	ret = poly_fqinv_batch_neon(rv, vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, 24);
	return ret;
}

int gt_baseinv_fqinv_batch_new_24_for_bench(int16_t r[24 * 8])
{
	int16x8_t rv[24];
	int ret;

	load_vec_array(rv, r, 24);
	ret = poly_fqinv_kway_new_neon(rv, 24, 1,
	                               vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, 24);
	return ret;
}

int gt_baseinv_fqinv_kway_new_24_for_bench(int16_t r[24 * 8], int k)
{
	int16x8_t rv[24];
	int ret;

	load_vec_array(rv, r, 24);
	ret = poly_fqinv_kway_new_neon(rv, 24, k,
	                               vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, 24);
	return ret;
}

int gt_baseinv_fqinv_batch_new_36_for_bench(int16_t r[36 * 8])
{
	int16x8_t rv[36];
	int ret;

	load_vec_array(rv, r, 36);
	ret = poly_fqinv_kway_new_neon(rv, 36, 1,
	                               vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, 36);
	return ret;
}

int gt_baseinv_fqinv_kway_new_36_for_bench(int16_t r[36 * 8], int k)
{
	int16x8_t rv[36];
	int ret;

	load_vec_array(rv, r, 36);
	ret = poly_fqinv_kway_new_neon(rv, 36, k,
	                               vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, 36);
	return ret;
}

int gt_baseinv_fqinv_batch_current_m_for_bench(int16_t *r, int m)
{
	int16x8_t rv[36];
	int ret;

	load_vec_array(rv, r, m);
	ret = poly_fqinv_batch_current_m_neon(rv, m, vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, m);
	return ret;
}

int gt_baseinv_fqinv_flat_kway_current_for_bench(int16_t *r, int m, int k)
{
	int16x8_t rv[36];
	int ret;

	load_vec_array(rv, r, m);
	ret = poly_fqinv_flat_kway_current_neon(rv, m, k,
	                                       vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, m);
	return ret;
}

int gt_baseinv_fqinv_hier_kway_current_for_bench(int16_t *r, int m, int k)
{
	int16x8_t rv[36];
	int ret;

	load_vec_array(rv, r, m);
	ret = poly_fqinv_hier_kway_current_neon(rv, m, k,
	                                       vld1q_s16(gt_baseinv_consts));
	store_vec_array(r, rv, m);
	return ret;
}

void gt_baseinv_fqinv_current_extra_fqmul_vec_for_bench(
	int16_t out[8], const int16_t in[8], const int16_t mul[8], int extra)
{
	int16x8_t con = vld1q_s16(gt_baseinv_consts);
	int16x8_t v = fqinv_neon(vld1q_s16(in), con);
	int16x8_t m = vld1q_s16(mul);

	for (int i = 0; i < extra; i++)
		v = fqmul_neon(v, m, con);

	vst1q_s16(out, v);
}

void gt_baseinv_fqmul_vec_for_bench(int16_t out[8], const int16_t a[8],
                                    const int16_t b[8])
{
	vst1q_s16(out, fqmul_neon(vld1q_s16(a), vld1q_s16(b),
	                          vld1q_s16(gt_baseinv_consts)));
}
#endif

#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
void gt_baseinv_fqinv_current_vec_for_bench(int16_t out[8],
                                            const int16_t in[8],
                                            int scaled_r)
{
	const int16_t *consts = scaled_r ? gt_baseinv_scaled_r_consts :
	                                   gt_baseinv_consts;

	vst1q_s16(out, fqinv_neon(vld1q_s16(in), vld1q_s16(consts)));
}

void gt_baseinv_fqinv16_vec_for_bench(int16_t out[8],
                                      const int16_t in[8],
                                      int scaled_r)
{
	const int16_t *consts = scaled_r ? gt_baseinv_scaled_r_consts :
	                                   gt_baseinv_consts;

	vst1q_s16(out, fqinv16_neon(vld1q_s16(in), vld1q_s16(consts)));
}

void gt_baseinv_fqinv_divstep_vec_for_bench(int16_t out[8],
                                            const int16_t in[8],
                                            int scaled_r)
{
	const int16_t *consts = scaled_r ? gt_baseinv_scaled_r_consts :
	                                   gt_baseinv_consts;
	const int16_t final_scale = scaled_r ?
		GT_BASEINV_DELTA_SCALE_SCALED_R :
		GT_BASEINV_DELTA_SCALE_NORMAL;

	vst1q_s16(out, fqinv_divstep_neon(vld1q_s16(in),
	                                  vld1q_s16(consts),
	                                  final_scale));
}

int gt_baseinv_fqinv16_24_for_bench(int16_t r[24 * 8])
{
	int16x8_t rv[24];
	int ret;

	for (int i = 0; i < 24; i++)
		rv[i] = vld1q_s16(r + 8 * i);

	ret = poly_fqinv_batch_fqinv16_neon(rv, vld1q_s16(gt_baseinv_consts));

	for (int i = 0; i < 24; i++)
		vst1q_s16(r + 8 * i, rv[i]);

	return ret;
}

int gt_baseinv_fqinv_divstep_24_for_bench(int16_t r[24 * 8])
{
	int16x8_t rv[24];
	int ret;

	for (int i = 0; i < 24; i++)
		rv[i] = vld1q_s16(r + 8 * i);

	ret = poly_fqinv_batch_divstep_neon(
		rv, vld1q_s16(gt_baseinv_consts), GT_BASEINV_DELTA_SCALE_NORMAL);

	for (int i = 0; i < 24; i++)
		vst1q_s16(r + 8 * i, rv[i]);

	return ret;
}

int gt_baseinv_fqinv_hier_kway_divstep_for_bench(int16_t *r, int m, int k)
{
	int16x8_t rv[36];
	int ret;

	for (int i = 0; i < m; i++)
		rv[i] = vld1q_s16(r + 8 * i);
	ret = poly_fqinv_hier_kway_divstep_neon(
		rv, m, k, vld1q_s16(gt_baseinv_consts),
		GT_BASEINV_DELTA_SCALE_NORMAL);
	for (int i = 0; i < m; i++)
		vst1q_s16(r + 8 * i, rv[i]);
	return ret;
}
#endif

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

#if defined(GT_BASEINV_KWAY_BENCH_HELPERS)
static int poly_baseinv_batch_block_major_kway_new_neon(poly *r, const poly *a,
                                                        const int16_t consts[8],
                                                        int k)
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

	if (poly_fqinv_kway_new_neon(den, 24, k, con))
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

static int poly_baseinv_batch_block_major_flat_kway_current_neon(
	poly *r, const poly *a, const int16_t consts[8], int k)
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

	if (poly_fqinv_flat_kway_current_neon(den, 24, k, con))
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

static int poly_baseinv_batch_block_major_hier_kway_current_neon(
	poly *r, const poly *a, const int16_t consts[8], int k)
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

	if (poly_fqinv_hier_kway_current_neon(den, 24, k, con))
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

#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
static int poly_baseinv_batch_block_major_hier_kway_divstep_neon(
	poly *r, const poly *a, const int16_t consts[8], int k,
	int16_t final_scale)
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

	if (poly_fqinv_hier_kway_divstep_neon(den, 24, k, con, final_scale))
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
#endif

#endif

#if defined(GT_BASEINV_USE_HIER_K8) || \
    defined(GT_BASEINV_HIER_K8_DIFF_HELPERS) || \
    defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
#if defined(GT_BASEINV_USE_HIER_K8_TREE)
static int batch_inverse_8_tree_neon(int16x8_t r[8], int16x8_t con)
{
	int16x8_t c0, c1, c2, c3, c4, c5, c6;
	int16x8_t inv;
	int16x8_t ri;

	c0 = r[0];
	c1 = fqmul_neon(c0, r[1], con);
	c2 = fqmul_neon(c1, r[2], con);
	c3 = fqmul_neon(c2, r[3], con);
	c4 = fqmul_neon(c3, r[4], con);
	c5 = fqmul_neon(c4, r[5], con);
	c6 = fqmul_neon(c5, r[6], con);

	ri = fqmul_neon(c6, r[7], con);
	if (!vminvq_u16(vreinterpretq_u16_s16(ri)))
		return 1;

	inv = gt_fqinv15_asm(ri, con);

	ri = r[7];
	r[7] = fqmul_neon(c6, inv, con);
	inv = fqmul_neon(inv, ri, con);

	ri = r[6];
	r[6] = fqmul_neon(c5, inv, con);
	inv = fqmul_neon(inv, ri, con);

	ri = r[5];
	r[5] = fqmul_neon(c4, inv, con);
	inv = fqmul_neon(inv, ri, con);

	ri = r[4];
	r[4] = fqmul_neon(c3, inv, con);
	inv = fqmul_neon(inv, ri, con);

	ri = r[3];
	r[3] = fqmul_neon(c2, inv, con);
	inv = fqmul_neon(inv, ri, con);

	ri = r[2];
	r[2] = fqmul_neon(c1, inv, con);
	inv = fqmul_neon(inv, ri, con);

	ri = r[1];
	r[1] = fqmul_neon(c0, inv, con);
	inv = fqmul_neon(inv, ri, con);

	r[0] = inv;
	return 0;
}

static void recover_group3_tree_neon(int16x8_t *r0, int16x8_t *r1,
                                     int16x8_t *r2, int16x8_t c01,
                                     int16x8_t group_inv, int16x8_t con)
{
	int16x8_t old1 = *r1;
	int16x8_t old2 = *r2;
	int16x8_t w = group_inv;

	*r2 = fqmul_neon(c01, w, con);
	w = fqmul_neon(w, old2, con);
	*r1 = fqmul_neon(*r0, w, con);
	w = fqmul_neon(w, old1, con);
	*r0 = w;
}

static int poly_fqinv_hier_k8_tree_neon(int16x8_t den[24], int16x8_t con)
{
	int16x8_t c01[8];
	int16x8_t group_prod[8];

	for (int group = 0; group < 8; group++)
	{
		const int start = group * 3;

		c01[group] = fqmul_neon(den[start], den[start + 1], con);
		group_prod[group] = fqmul_neon(c01[group], den[start + 2], con);
	}

	if (batch_inverse_8_tree_neon(group_prod, con))
		return 1;

	for (int group = 0; group < 8; group++)
	{
		const int start = group * 3;

		recover_group3_tree_neon(&den[start], &den[start + 1],
		                         &den[start + 2], c01[group],
		                         group_prod[group], con);
	}

	return 0;
}
#endif

static int poly_baseinv_batch_block_major_hier_k8_neon(
	poly *r, const poly *a, const int16_t consts[8], int use_fqinv16)
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

	if (use_fqinv16)
	{
#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
		if (poly_fqinv_hier_kway_fqinv16_neon(den, 24, 8, con))
		{
			memset(r->coeffs, 0, sizeof(r->coeffs));
			return 1;
		}
#else
		(void)use_fqinv16;
		memset(r->coeffs, 0, sizeof(r->coeffs));
		return 1;
#endif
	}
#if defined(GT_BASEINV_USE_HIER_K8_TREE)
	else if (poly_fqinv_hier_k8_tree_neon(den, con))
#else
	else if (poly_fqinv_hier_kway_current_neon(den, 24, 8, con))
#endif
	{
		memset(r->coeffs, 0, sizeof(r->coeffs));
		return 1;
	}

#if defined(GT_BASEINV_HIER_K8_EACH_INV_CANON)
	center_vec_array_modq(den, 24);
#endif

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

#if defined(GT_BASEINV_HIER_K8_OUTPUT_CANON)
	center_poly_modq(r);
#endif

	return 0;
}
#endif

#if defined(__aarch64__) && defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
int poly_baseinv_scaled_r_hier_k8_prepare_for_bench(poly *num,
                                                    int16_t den_out[24 * 8],
                                                    const poly *a)
{
	int16x8_t con = vld1q_s16(gt_baseinv_scaled_r_consts);
	int16x8_t den[24] __attribute__((aligned(16)));
	const int16_t *src = a->coeffs;
	int16_t *dst = num->coeffs;
	const int16_t *lambda = &gt_rowbitrev_lambda[0][0];

	for (int i = 0; i < 24; i++)
	{
		int16x8_t zeta = vld1q_s16(lambda);

		baseinv_8_prepare(dst, &den[i], src, zeta, con);
		src += 8 * GT_BASEINV_QUARTIC_LANES;
		dst += 8 * GT_BASEINV_QUARTIC_LANES;
		lambda += 8;
	}

	for (int i = 0; i < 24; i++)
		vst1q_s16(den_out + 8 * i, den[i]);
	return 0;
}

int poly_baseinv_scaled_r_hier_k8_tree_for_bench(int16_t den_buf[24 * 8])
{
	int16x8_t con = vld1q_s16(gt_baseinv_scaled_r_consts);
	int16x8_t den[24] __attribute__((aligned(16)));
	int ret;

	for (int i = 0; i < 24; i++)
		den[i] = vld1q_s16(den_buf + 8 * i);

	ret = poly_fqinv_hier_kway_current_neon(den, 24, 8, con);

	for (int i = 0; i < 24; i++)
		vst1q_s16(den_buf + 8 * i, den[i]);
	return ret;
}

void poly_baseinv_scaled_r_finish_for_bench(poly *out, const poly *num,
                                            const int16_t den_inv[24 * 8])
{
	memcpy(out->coeffs, num->coeffs, sizeof(out->coeffs));
#ifdef GT_BASEINV_BATCH_USE_ASM_FINISH
	baseinv_batch_finish24_n1_asm(out->coeffs, den_inv);
#else
	int16x8_t con = vld1q_s16(gt_baseinv_scaled_r_consts);
	int16_t *dst = out->coeffs;

	for (int i = 0; i < 24; i++)
	{
		baseinv_8_finish(dst, vld1q_s16(den_inv + 8 * i), con);
		dst += 8 * GT_BASEINV_QUARTIC_LANES;
	}
#endif
}

void gt_baseinv_fqinv15_x2_for_bench(int16_t f[8], int16_t g[8])
{
#if defined(GT_BASEINV_USE_FQINV15_ASM)
	int16x8_t con = vld1q_s16(gt_baseinv_scaled_r_consts);
	int16x8_t fv = vld1q_s16(f);
	int16x8_t gv = vld1q_s16(g);

	fv = gt_fqinv15_asm(fv, con);
	gv = gt_fqinv15_asm(gv, con);
	vst1q_s16(f, fv);
	vst1q_s16(g, gv);
#else
	(void)f;
	(void)g;
#endif
}
#endif

#if defined(__aarch64__) && defined(GT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS)
static int poly_fqinv_hier_k8_x2_current_neon(int16x8_t fden[24],
                                              int16x8_t gden[24],
                                              int16x8_t con)
{
	int16x8_t fc[24];
	int16x8_t gc[24];
	int16x8_t group_prod[16];

	for (int group = 0; group < 8; group++)
	{
		const int start = 3 * group;
		const int end = start + 3;

		fc[start] = fden[start];
		gc[start] = gden[start];
		for (int i = start + 1; i < end; i++)
		{
			fc[i] = fqmul_neon(fc[i - 1], fden[i], con);
			gc[i] = fqmul_neon(gc[i - 1], gden[i], con);
		}

		group_prod[group] = fc[end - 1];
		group_prod[8 + group] = gc[end - 1];
	}

	if (poly_fqinv_batch_current_m_neon(group_prod, 16, con))
		return 1;

	for (int group = 0; group < 8; group++)
	{
		const int start = 3 * group;
		const int end = start + 3;
		int16x8_t fw = group_prod[group];
		int16x8_t gw = group_prod[8 + group];

		for (int i = end - 1; i > start; i--)
		{
			int16x8_t fri = fden[i];
			int16x8_t gri = gden[i];

			fden[i] = fqmul_neon(fc[i - 1], fw, con);
			gden[i] = fqmul_neon(gc[i - 1], gw, con);
			fw = fqmul_neon(fw, fri, con);
			gw = fqmul_neon(gw, gri, con);
		}

		fden[start] = fw;
		gden[start] = gw;
	}

	return 0;
}

static int poly_baseinv_batch_block_major_hier_k8_x2_neon(
	poly *finv, poly *ginv, const poly *f, const poly *g,
	const int16_t consts[8])
{
	int16x8_t con = vld1q_s16(consts);
	int16x8_t fden[24] __attribute__((aligned(16)));
	int16x8_t gden[24] __attribute__((aligned(16)));
	const int16_t *fsrc = f->coeffs;
	const int16_t *gsrc = g->coeffs;
	int16_t *fdst = finv->coeffs;
	int16_t *gdst = ginv->coeffs;
	const int16_t *lambda = &gt_rowbitrev_lambda[0][0];

	for (int i = 0; i < 24; i++)
	{
		int16x8_t zeta = vld1q_s16(lambda);

		baseinv_8_prepare(fdst, &fden[i], fsrc, zeta, con);
		baseinv_8_prepare(gdst, &gden[i], gsrc, zeta, con);
		fsrc += 8 * GT_BASEINV_QUARTIC_LANES;
		gsrc += 8 * GT_BASEINV_QUARTIC_LANES;
		fdst += 8 * GT_BASEINV_QUARTIC_LANES;
		gdst += 8 * GT_BASEINV_QUARTIC_LANES;
		lambda += 8;
	}

	if (poly_fqinv_hier_k8_x2_current_neon(fden, gden, con))
	{
		memset(finv->coeffs, 0, sizeof(finv->coeffs));
		memset(ginv->coeffs, 0, sizeof(ginv->coeffs));
		return 1;
	}

#ifdef GT_BASEINV_BATCH_USE_ASM_FINISH
	(void)con;
	baseinv_batch_finish24_n1_asm(finv->coeffs, (const int16_t *)fden);
	baseinv_batch_finish24_n1_asm(ginv->coeffs, (const int16_t *)gden);
#else
	fdst = finv->coeffs;
	gdst = ginv->coeffs;
	for (int i = 0; i < 24; i++)
	{
		baseinv_8_finish(fdst, fden[i], con);
		baseinv_8_finish(gdst, gden[i], con);
		fdst += 8 * GT_BASEINV_QUARTIC_LANES;
		gdst += 8 * GT_BASEINV_QUARTIC_LANES;
	}
#endif

	return 0;
}
#endif

#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
static int poly_baseinv_batch_block_major_fqinv16_neon(poly *r, const poly *a,
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

	if (poly_fqinv_batch_fqinv16_neon(den, con))
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

static int poly_baseinv_batch_block_major_divstep_neon(poly *r, const poly *a,
                                                       const int16_t consts[8],
                                                       int16_t final_scale)
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

	if (poly_fqinv_batch_divstep_neon(den, con, final_scale))
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
#endif

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
#if defined(GT_BASEINV_USE_HIER_K8)
	return poly_baseinv_scaled_r_hier_k8_candidate(r, a);
#elif defined(GT_BASEINV_SCALED_R_USE_HIER_KWAY_CURRENT)
#if defined(__aarch64__) && defined(GT_BASEINV_HIER_K8_DIFF_HELPERS)
	return poly_baseinv_scaled_r_hier_k8_candidate(r, a);
#elif defined(__aarch64__) && defined(GT_BASEINV_KWAY_BENCH_HELPERS)
#ifndef GT_BASEINV_SCALED_R_HIER_K
#define GT_BASEINV_SCALED_R_HIER_K 8
#endif
	return poly_baseinv_batch_block_major_hier_kway_current_neon(
		r, a, gt_baseinv_scaled_r_consts, GT_BASEINV_SCALED_R_HIER_K);
#else
	(void)r;
	(void)a;
	return 1;
#endif
#else
	return poly_baseinv_gt_batch_scaled_r(r, a);
#endif
}

#if defined(GT_BASEINV_USE_HIER_K8) || \
    defined(GT_BASEINV_HIER_K8_DIFF_HELPERS) || \
    defined(GT_BASEINV_HIER_K8_DECOMPOSE_HELPERS)
/*
 * Production-selectable hier_k8 backend for scaled keygen baseinv.
 *
 * hier_k8 only changes the denominator batch-inversion multiplication tree:
 * it splits the 24 denominator vectors into 8 local groups, inverts the 8
 * group products with the existing fqinv15_asm backend, then propagates those
 * inverses back inside each group.  This is coefficient-wise equivalent modulo
 * q to the current flat tree, but the multiplication order is different, so it
 * is not guaranteed to preserve exact int16 representatives.  KEM pk/sk byte
 * differential is therefore the production-readiness gate.
 */
int poly_baseinv_scaled_r_hier_k8_candidate(poly *r, const poly *a)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_hier_k8_neon(
		r, a, gt_baseinv_scaled_r_consts, 0);
#else
	(void)r;
	(void)a;
	return 1;
#endif
}
#endif

#if defined(GT_BASEINV_HIER_K8_DIFF_HELPERS)
int poly_baseinv_scaled_r_current_reference(poly *r, const poly *a)
{
	return poly_baseinv_gt_batch_scaled_r(r, a);
}

int poly_baseinv_scaled_r_fqinv16_reference(poly *r, const poly *a)
{
#if defined(__aarch64__) && defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
	return poly_baseinv_batch_block_major_fqinv16_neon(
		r, a, gt_baseinv_scaled_r_consts);
#else
	(void)r;
	(void)a;
	return 1;
#endif
}

int poly_baseinv_scaled_r_hier_k8_fqinv16_candidate(poly *r, const poly *a)
{
#if defined(__aarch64__) && defined(GT_BASEINV_KWAY_BENCH_HELPERS) && \
    defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
	return poly_baseinv_batch_block_major_hier_k8_neon(
		r, a, gt_baseinv_scaled_r_consts, 1);
#else
	(void)r;
	(void)a;
	return 1;
#endif
}
#endif

#if defined(GT_KEYGEN_DIRECT_H_HINV_MODEL_HELPERS)
int poly_keygen_baseinv_scaled_r_x2_direct_model(poly *finv, poly *ginv,
                                                 const poly *f,
                                                 const poly *g)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_hier_k8_x2_neon(
		finv, ginv, f, g, gt_baseinv_scaled_r_consts);
#else
	(void)finv;
	(void)ginv;
	(void)f;
	(void)g;
	return 1;
#endif
}

int poly_keygen_compute_h_hinv_direct_model(poly *h, poly *hinv,
                                            const poly *f, const poly *g)
{
	poly finv;
	poly ginv;

	if (poly_keygen_baseinv_scaled_r_x2_direct_model(&finv, &ginv, f, g))
	{
		memset(h->coeffs, 0, sizeof(h->coeffs));
		memset(hinv->coeffs, 0, sizeof(hinv->coeffs));
		return 1;
	}

	poly_basemul_scaled_r_input(h, g, &finv);
	poly_basemul_scaled_r_input(hinv, f, &ginv);
	return 0;
}
#endif

#if defined(GT_BASEINV_KWAY_BENCH_HELPERS)
int poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(poly *r, const poly *a,
                                                      int k)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_kway_new_neon(
		r, a, gt_baseinv_scaled_r_consts, k);
#else
	(void)r;
	(void)a;
	(void)k;
	return 1;
#endif
}

int poly_baseinv_gt_batch_scaled_r_flat_kway_current_for_bench(poly *r,
                                                               const poly *a,
                                                               int k)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_flat_kway_current_neon(
		r, a, gt_baseinv_scaled_r_consts, k);
#else
	(void)r;
	(void)a;
	(void)k;
	return 1;
#endif
}

int poly_baseinv_gt_batch_scaled_r_hier_kway_current_for_bench(poly *r,
                                                               const poly *a,
                                                               int k)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_hier_kway_current_neon(
		r, a, gt_baseinv_scaled_r_consts, k);
#else
	(void)r;
	(void)a;
	(void)k;
	return 1;
#endif
}
#endif

#if defined(GT_BASEINV_DIVSTEP_BENCH_HELPERS)
int poly_baseinv_gt_batch_scaled_r_fqinv16_for_bench(poly *r, const poly *a)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_fqinv16_neon(
		r, a, gt_baseinv_scaled_r_consts);
#else
	(void)r;
	(void)a;
	return 1;
#endif
}

int poly_baseinv_gt_batch_scaled_r_divstep_for_bench(poly *r, const poly *a)
{
#if defined(__aarch64__)
	return poly_baseinv_batch_block_major_divstep_neon(
		r, a, gt_baseinv_scaled_r_consts,
		GT_BASEINV_DELTA_SCALE_SCALED_R);
#else
	(void)r;
	(void)a;
	return 1;
#endif
}

int poly_baseinv_gt_batch_scaled_r_hier_kway_divstep_for_bench(poly *r,
                                                               const poly *a,
                                                               int k)
{
#if defined(__aarch64__) && defined(GT_BASEINV_KWAY_BENCH_HELPERS)
	return poly_baseinv_batch_block_major_hier_kway_divstep_neon(
		r, a, gt_baseinv_scaled_r_consts, k,
		GT_BASEINV_DELTA_SCALE_SCALED_R);
#else
	(void)r;
	(void)a;
	(void)k;
	return 1;
#endif
}
#endif
