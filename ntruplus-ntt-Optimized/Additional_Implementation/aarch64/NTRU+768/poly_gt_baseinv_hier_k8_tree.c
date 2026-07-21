#include <stdint.h>
#include <string.h>

#include <arm_neon.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#if NTRUPLUS_N != 768
#error "hier_k8 tree backend is specialized for NTRU+768"
#endif

#if defined(GT_BASEINV_USE_HIER_K8_TREE) && \
    defined(GT_BASEINV_SCALED_R_EXTERNAL_BACKEND)

#define GT_BASEINV_QUARTIC_LANES 4
#define GT_DEN_VECTORS 24

void baseinv_batch_finish24_n1_asm(int16_t *dst, const int16_t *den_inv);
int16x8_t gt_fqinv15_asm(int16x8_t a, int16x8_t con);
int poly_baseinv_scaled_r(poly *r, const poly *a);

static const int16_t gt_baseinv_scaled_r_consts[8]
	__attribute__((aligned(16))) = {
	3457, 19412, -12929, -147, -1393, -682, -6464, 0
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

static int batch_inverse_8(int16x8_t r[8], int16x8_t con)
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

static void recover_group3(int16x8_t *r0, int16x8_t *r1,
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

static int hier_k8_tree(int16x8_t den[GT_DEN_VECTORS], int16x8_t con)
{
	int16x8_t c01[8];
	int16x8_t group_prod[8];

	for (int group = 0; group < 8; group++)
	{
		const int start = group * 3;

		c01[group] = fqmul_neon(den[start], den[start + 1], con);
		group_prod[group] = fqmul_neon(c01[group], den[start + 2], con);
	}

	if (batch_inverse_8(group_prod, con))
		return 1;

	for (int group = 0; group < 8; group++)
	{
		const int start = group * 3;

		recover_group3(&den[start], &den[start + 1], &den[start + 2],
		               c01[group], group_prod[group], con);
	}

	return 0;
}

int poly_baseinv_scaled_r(poly *r, const poly *a)
{
	int16x8_t con = vld1q_s16(gt_baseinv_scaled_r_consts);
	int16x8_t den[GT_DEN_VECTORS] __attribute__((aligned(16)));
	const int16_t *src = a->coeffs;
	int16_t *dst = r->coeffs;
	const int16_t *lambda = &gt_rowbitrev_lambda[0][0];

	for (int i = 0; i < GT_DEN_VECTORS; i++)
	{
		int16x8_t zeta = vld1q_s16(lambda);

		baseinv_8_prepare(dst, &den[i], src, zeta, con);
		src += 8 * GT_BASEINV_QUARTIC_LANES;
		dst += 8 * GT_BASEINV_QUARTIC_LANES;
		lambda += 8;
	}

	if (hier_k8_tree(den, con))
	{
		memset(r->coeffs, 0, sizeof(r->coeffs));
		return 1;
	}

	baseinv_batch_finish24_n1_asm(r->coeffs, (const int16_t *)den);
	return 0;
}

#endif
