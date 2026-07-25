#include <stdint.h>
#include <string.h>

#include <arm_neon.h>

#include "keygen.h"

#if NTRUPLUS_N != 768
#error "The direct-CQ keygen backend is specialized for NTRU+768"
#endif

#define GT_KEYGEN_CQ_GROUPS 24

extern const int16_t gt_keygen_bpq_lambda8[GT_KEYGEN_CQ_GROUPS][8];

int gt_keygen_baseinv_hier_k8(int16_t *den);
void gt_keygen_baseinv_cq_finish(int16_t *out_cq,
                                 const int16_t *numerator,
                                 const int16_t *den);

static const int16_t gt_keygen_cq_consts[8]
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

static inline int16x8_t fqmul_neon(int16x8_t a, int16x8_t b,
                                   int16x8_t con)
{
    int32x4_t lo = vmull_s16(vget_low_s16(a), vget_low_s16(b));
    int32x4_t hi = vmull_high_s16(a, b);

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

static inline int16x8_t reduce_mul4(int16x8_t a0, int16x8_t b0,
                                    int16x8_t a1, int16x8_t b1,
                                    int16x8_t a2, int16x8_t b2,
                                    int16x8_t a3, int16x8_t b3,
                                    int16x8_t con)
{
    int32x4_t lo = vmull_s16(vget_low_s16(a0), vget_low_s16(b0));
    int32x4_t hi = vmull_high_s16(a0, b0);

    lo = vmlal_s16(lo, vget_low_s16(a1), vget_low_s16(b1));
    hi = vmlal_high_s16(hi, a1, b1);
    lo = vmlal_s16(lo, vget_low_s16(a2), vget_low_s16(b2));
    hi = vmlal_high_s16(hi, a2, b2);
    lo = vmlal_s16(lo, vget_low_s16(a3), vget_low_s16(b3));
    hi = vmlal_high_s16(hi, a3, b3);
    return montgomery_reduce_vec(lo, hi, con);
}

static void baseinv_cq_prepare_group(int16_t *numerator, int16x8_t *den,
                                     const int16_t *src, int16x8_t zeta,
                                     int16x8_t con)
{
    int16x8_t a0 = vld1q_s16(src + 0);
    int16x8_t a1 = vld1q_s16(src + 8);
    int16x8_t a2 = vld1q_s16(src + 16);
    int16x8_t a3 = vld1q_s16(src + 24);
    int16x8_t neg2a2 = vshlq_n_s16(vnegq_s16(a2), 1);
    int16x8_t neg2a3 = vshlq_n_s16(vnegq_s16(a3), 1);
    int16x8_t t0, t1, t2;
    int16x8_t n0, n1, n2, n3;

    t0 = reduce_mul2(a2, a2, a1, neg2a3, con);
    t1 = fqmul_neon(a3, a3, con);
    t0 = reduce_mul2(t0, zeta, a0, a0, con);
    t1 = reduce_mul3(t1, zeta, a1, a1, a0, neg2a2, con);
    t2 = fqmul_neon(t1, zeta, con);

    *den = reduce_mul2(t0, t0, vnegq_s16(t1), t2, con);
    n0 = reduce_mul2(a0, t0, a2, t2, con);
    n1 = reduce_mul2(a3, t2, a1, t0, con);
    n2 = reduce_mul2(a2, t0, a0, t1, con);
    n3 = reduce_mul2(a1, t1, a3, t0, con);

    vst1q_s16(numerator + 0, n0);
    vst1q_s16(numerator + 8, n1);
    vst1q_s16(numerator + 16, n2);
    vst1q_s16(numerator + 24, n3);
}

int gt_keygen_baseinv_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *in_cq)
{
    int16_t den[GT_KEYGEN_CQ_GROUPS * 8] __attribute__((aligned(16)));
    int16_t numerator[GT_KEYGEN_CQ_GROUPS * 32]
        __attribute__((aligned(16)));
    int16x8_t con = vld1q_s16(gt_keygen_cq_consts);
    int group;

    for (group = 0; group < GT_KEYGEN_CQ_GROUPS; group++) {
        int16x8_t zeta = vld1q_s16(gt_keygen_bpq_lambda8[group]);

        baseinv_cq_prepare_group(numerator + 32 * group,
                                 (int16x8_t *)(den + 8 * group),
                                 in_cq->storage.coeffs + 32 * group,
                                 zeta, con);
    }

    if (gt_keygen_baseinv_hier_k8(den)) {
        memset(out_cq, 0, sizeof(*out_cq));
        return 1;
    }
    gt_keygen_baseinv_cq_finish(out_cq->storage.coeffs, numerator, den);
    return 0;
}

void gt_keygen_basemul_cq_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *a_cq,
    const gt_cq_poly *b_scaled_r_cq)
{
    int16x8_t con = vld1q_s16(gt_keygen_cq_consts);
    int group;

    for (group = 0; group < GT_KEYGEN_CQ_GROUPS; group++) {
        const int16_t *ap = a_cq->storage.coeffs + 32 * group;
        const int16_t *bp = b_scaled_r_cq->storage.coeffs + 32 * group;
        int16_t *rp = out_cq->storage.coeffs + 32 * group;
        int16x8_t zeta = vld1q_s16(gt_keygen_bpq_lambda8[group]);
        int16x8_t a0 = vld1q_s16(ap + 0);
        int16x8_t a1 = vld1q_s16(ap + 8);
        int16x8_t a2 = vld1q_s16(ap + 16);
        int16x8_t a3 = vld1q_s16(ap + 24);
        int16x8_t b0 = vld1q_s16(bp + 0);
        int16x8_t b1 = vld1q_s16(bp + 8);
        int16x8_t b2 = vld1q_s16(bp + 16);
        int16x8_t b3 = vld1q_s16(bp + 24);
        int16x8_t r0, r1, r2, r3;
        int16x8_t t;

        t = reduce_mul3(a1, b3, a2, b2, a3, b1, con);
        r0 = reduce_mul2(t, zeta, a0, b0, con);

        t = reduce_mul2(a2, b3, a3, b2, con);
        r1 = reduce_mul3(t, zeta, a0, b1, a1, b0, con);

        t = fqmul_neon(a3, b3, con);
        r2 = reduce_mul4(t, zeta, a0, b2, a1, b1, a2, b0, con);

        r3 = reduce_mul4(a0, b3, a1, b2, a2, b1, a3, b0, con);

        vst1q_s16(rp + 0, r0);
        vst1q_s16(rp + 8, r1);
        vst1q_s16(rp + 16, r2);
        vst1q_s16(rp + 24, r3);
    }
}
