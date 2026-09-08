#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_tables.h"

#include <arm_neon.h>

#define Q 3457
#define NEG_QINV (-12929)
#define R (-147)
#define RSQ 867

typedef struct {
    int32x4_t low;
    int32x4_t high;
} wide8;

static inline wide8 multiply(int16x8_t a, int16x8_t b)
{
    wide8 out = {vmull_s16(vget_low_s16(a), vget_low_s16(b)),
                 vmull_high_s16(a, b)};
    return out;
}

static inline wide8 multiply_add(wide8 acc, int16x8_t a, int16x8_t b)
{
    acc.low = vmlal_s16(acc.low, vget_low_s16(a), vget_low_s16(b));
    acc.high = vmlal_high_s16(acc.high, a, b);
    return acc;
}

/* Signed widening Montgomery reduction: accumulator R^k -> R^(k-1). */
static inline int16x8_t montgomery_reduce(wide8 value)
{
    const int16x8_t q = vdupq_n_s16(Q);
    const int16x8_t neg_qinv = vdupq_n_s16(NEG_QINV);
    int16x8_t quotient = vuzp1q_s16(
        vreinterpretq_s16_s32(value.low),
        vreinterpretq_s16_s32(value.high));

    quotient = vmulq_s16(quotient, neg_qinv);
    value.low = vmlal_s16(value.low, vget_low_s16(quotient),
                          vget_low_s16(q));
    value.high = vmlal_high_s16(value.high, quotient, q);
    return vuzp2q_s16(vreinterpretq_s16_s32(value.low),
                      vreinterpretq_s16_s32(value.high));
}

static inline void cubic_product(int16x8_t out[3], const int16x8_t a[3],
                                 const int16x8_t b[3], int16x8_t zeta)
{
    wide8 cross0 = multiply(a[2], b[1]);
    wide8 cross1 = multiply(a[2], b[2]);
    wide8 acc;
    int16x8_t reduced0;
    int16x8_t reduced1;

    cross0 = multiply_add(cross0, a[1], b[2]);
    reduced0 = montgomery_reduce(cross0);
    reduced1 = montgomery_reduce(cross1);

    acc = multiply(reduced0, zeta);
    acc = multiply_add(acc, a[0], b[0]);
    out[0] = montgomery_reduce(acc);

    acc = multiply(reduced1, zeta);
    acc = multiply_add(acc, a[0], b[1]);
    acc = multiply_add(acc, a[1], b[0]);
    out[1] = montgomery_reduce(acc);

    acc = multiply(a[2], b[0]);
    acc = multiply_add(acc, a[1], b[1]);
    acc = multiply_add(acc, a[0], b[2]);
    out[2] = montgomery_reduce(acc);
}

static inline int16x8_t finish_product(int16x8_t value)
{
    return montgomery_reduce(multiply(value, vdupq_n_s16(RSQ)));
}

static inline int16x8_t finish_product_add(int16x8_t value, int16x8_t addend)
{
    wide8 acc = multiply(value, vdupq_n_s16(RSQ));
    acc = multiply_add(acc, addend, vdupq_n_s16(R));
    return montgomery_reduce(acc);
}

void gt864_fr0_basemul_neon(int16_t out[GT864_FR0_BASEMUL_COEFFICIENTS],
                            const int16_t a[GT864_FR0_BASEMUL_COEFFICIENTS],
                            const int16_t b[GT864_FR0_BASEMUL_COEFFICIENTS])
{
    for (int group = 0; group < 36; group++) {
        int offset = 24 * group;
        int16x8_t av[3] = {vld1q_s16(a + offset),
                           vld1q_s16(a + offset + 8),
                           vld1q_s16(a + offset + 16)};
        int16x8_t bv[3] = {vld1q_s16(b + offset),
                           vld1q_s16(b + offset + 8),
                           vld1q_s16(b + offset + 16)};
        int16x8_t product[3];

        cubic_product(product, av, bv,
                      vld1q_s16(gt864_fr0_zetas_mul[group]));
        vst1q_s16(out + offset, finish_product(product[0]));
        vst1q_s16(out + offset + 8, finish_product(product[1]));
        vst1q_s16(out + offset + 16, finish_product(product[2]));
    }
}

void gt864_fr0_basemul_add_neon(
    int16_t out[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t a[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t b[GT864_FR0_BASEMUL_COEFFICIENTS],
    const int16_t c[GT864_FR0_BASEMUL_COEFFICIENTS])
{
    for (int group = 0; group < 36; group++) {
        int offset = 24 * group;
        int16x8_t av[3] = {vld1q_s16(a + offset),
                           vld1q_s16(a + offset + 8),
                           vld1q_s16(a + offset + 16)};
        int16x8_t bv[3] = {vld1q_s16(b + offset),
                           vld1q_s16(b + offset + 8),
                           vld1q_s16(b + offset + 16)};
        int16x8_t cv[3] = {vld1q_s16(c + offset),
                           vld1q_s16(c + offset + 8),
                           vld1q_s16(c + offset + 16)};
        int16x8_t product[3];

        cubic_product(product, av, bv,
                      vld1q_s16(gt864_fr0_zetas_mul[group]));
        vst1q_s16(out + offset, finish_product_add(product[0], cv[0]));
        vst1q_s16(out + offset + 8,
                  finish_product_add(product[1], cv[1]));
        vst1q_s16(out + offset + 16,
                  finish_product_add(product[2], cv[2]));
    }
}
