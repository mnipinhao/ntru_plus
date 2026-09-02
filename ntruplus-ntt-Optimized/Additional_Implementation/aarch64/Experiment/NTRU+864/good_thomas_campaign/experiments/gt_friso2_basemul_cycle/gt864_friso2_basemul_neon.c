#include "gt864_friso2_basemul_neon.h"

#include <arm_neon.h>

#define Q 3457
#define NEG_QINV (-12929)
#define R (-147)
#define RSQ 867
#define GROUPS_PER_TOP 18
#define HALFWORDS_PER_GROUP 24

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

static inline wide8 scale_wide(wide8 value, int32x4_t factor)
{
    value.low = vmulq_s32(value.low, factor);
    value.high = vmulq_s32(value.high, factor);
    return value;
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

static inline void cubic_staged(int16x8_t out[3], const int16x8_t a[3],
                                const int16x8_t b[3], int16x8_t z0_r1)
{
    wide8 cross0 = multiply(a[2], b[1]);
    wide8 square2 = multiply(a[2], b[2]);
    wide8 acc;

    cross0 = multiply_add(cross0, a[1], b[2]);
    int16x8_t reduced0 = montgomery_reduce(cross0);
    int16x8_t reduced1 = montgomery_reduce(square2);

    acc = multiply(reduced0, z0_r1);
    acc = multiply_add(acc, a[0], b[0]);
    out[0] = montgomery_reduce(acc);

    acc = multiply(reduced1, z0_r1);
    acc = multiply_add(acc, a[0], b[1]);
    acc = multiply_add(acc, a[1], b[0]);
    out[1] = montgomery_reduce(acc);

    acc = multiply(a[2], b[0]);
    acc = multiply_add(acc, a[1], b[1]);
    acc = multiply_add(acc, a[0], b[2]);
    out[2] = montgomery_reduce(acc);
}

static inline void cubic_direct(int16x8_t out[3], const int16x8_t a[3],
                                const int16x8_t b[3], int32x4_t z0)
{
    wide8 cross0 = multiply(a[2], b[1]);
    wide8 acc;

    cross0 = multiply_add(cross0, a[1], b[2]);
    acc = scale_wide(cross0, z0);
    acc = multiply_add(acc, a[0], b[0]);
    out[0] = montgomery_reduce(acc);

    acc = scale_wide(multiply(a[2], b[2]), z0);
    acc = multiply_add(acc, a[0], b[1]);
    acc = multiply_add(acc, a[1], b[0]);
    out[1] = montgomery_reduce(acc);

    acc = multiply(a[2], b[0]);
    acc = multiply_add(acc, a[1], b[1]);
    acc = multiply_add(acc, a[0], b[2]);
    out[2] = montgomery_reduce(acc);
}

static inline int16x8_t finish(int16x8_t value)
{
    return montgomery_reduce(multiply(value, vdupq_n_s16(RSQ)));
}

static inline int16x8_t finish_add(int16x8_t value, int16x8_t addend)
{
    wide8 acc = multiply(value, vdupq_n_s16(RSQ));
    acc = multiply_add(acc, addend, vdupq_n_s16(R));
    return montgomery_reduce(acc);
}

#define LOAD_TILE(prefix, pointer, offset)                                    \
    int16x8_t prefix[3] = {vld1q_s16((pointer) + (offset)),                   \
                             vld1q_s16((pointer) + (offset) + 8),             \
                             vld1q_s16((pointer) + (offset) + 16)}

#define STORE_PRODUCT(pointer, offset, product)                              \
    do {                                                                      \
        vst1q_s16((pointer) + (offset), finish((product)[0]));                \
        vst1q_s16((pointer) + (offset) + 8, finish((product)[1]));            \
        vst1q_s16((pointer) + (offset) + 16, finish((product)[2]));           \
    } while (0)

#define STORE_PRODUCT_ADD(pointer, offset, product, addend)                  \
    do {                                                                      \
        vst1q_s16((pointer) + (offset),                                       \
                  finish_add((product)[0], (addend)[0]));                     \
        vst1q_s16((pointer) + (offset) + 8,                                   \
                  finish_add((product)[1], (addend)[1]));                     \
        vst1q_s16((pointer) + (offset) + 16,                                  \
                  finish_add((product)[2], (addend)[2]));                     \
    } while (0)

__attribute__((noinline))
void gt864_friso2_basemul_staged(int16_t out[864], const int16_t a[864],
                                 const int16_t b[864])
{
    static const int16_t z0_r1_by_top[2] = {-1323, -441};
    for (int top = 0; top < 2; ++top) {
        int16x8_t z0_r1 = vdupq_n_s16(z0_r1_by_top[top]);
        for (int tile = 0; tile < GROUPS_PER_TOP; ++tile) {
            int offset = HALFWORDS_PER_GROUP * (GROUPS_PER_TOP * top + tile);
            LOAD_TILE(av, a, offset);
            LOAD_TILE(bv, b, offset);
            int16x8_t product[3];
            cubic_staged(product, av, bv, z0_r1);
            STORE_PRODUCT(out, offset, product);
        }
    }
}

__attribute__((noinline))
void gt864_friso2_basemul_direct(int16_t out[864], const int16_t a[864],
                                 const int16_t b[864])
{
    static const int32_t z0_by_top[2] = {9, 3};
    for (int top = 0; top < 2; ++top) {
        int32x4_t z0 = vdupq_n_s32(z0_by_top[top]);
        for (int tile = 0; tile < GROUPS_PER_TOP; ++tile) {
            int offset = HALFWORDS_PER_GROUP * (GROUPS_PER_TOP * top + tile);
            LOAD_TILE(av, a, offset);
            LOAD_TILE(bv, b, offset);
            int16x8_t product[3];
            cubic_direct(product, av, bv, z0);
            STORE_PRODUCT(out, offset, product);
        }
    }
}

__attribute__((noinline))
void gt864_friso2_basemul_add_staged(int16_t out[864], const int16_t a[864],
                                     const int16_t b[864],
                                     const int16_t c[864])
{
    static const int16_t z0_r1_by_top[2] = {-1323, -441};
    for (int top = 0; top < 2; ++top) {
        int16x8_t z0_r1 = vdupq_n_s16(z0_r1_by_top[top]);
        for (int tile = 0; tile < GROUPS_PER_TOP; ++tile) {
            int offset = HALFWORDS_PER_GROUP * (GROUPS_PER_TOP * top + tile);
            LOAD_TILE(av, a, offset);
            LOAD_TILE(bv, b, offset);
            LOAD_TILE(cv, c, offset);
            int16x8_t product[3];
            cubic_staged(product, av, bv, z0_r1);
            STORE_PRODUCT_ADD(out, offset, product, cv);
        }
    }
}

__attribute__((noinline))
void gt864_friso2_basemul_add_direct(int16_t out[864], const int16_t a[864],
                                     const int16_t b[864],
                                     const int16_t c[864])
{
    static const int32_t z0_by_top[2] = {9, 3};
    for (int top = 0; top < 2; ++top) {
        int32x4_t z0 = vdupq_n_s32(z0_by_top[top]);
        for (int tile = 0; tile < GROUPS_PER_TOP; ++tile) {
            int offset = HALFWORDS_PER_GROUP * (GROUPS_PER_TOP * top + tile);
            LOAD_TILE(av, a, offset);
            LOAD_TILE(bv, b, offset);
            LOAD_TILE(cv, c, offset);
            int16x8_t product[3];
            cubic_direct(product, av, bv, z0);
            STORE_PRODUCT_ADD(out, offset, product, cv);
        }
    }
}
