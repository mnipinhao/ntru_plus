#include "fused_tobytes.h"

#include "p3b5_tables.h"
#include <arm_neon.h>
#include <string.h>

static const uint8_t pack_index[16] __attribute__((aligned(16))) = {
    0, 1, 16, 2, 3, 18, 4, 5, 20, 6, 7, 22, 255, 255, 255, 255
};

static inline int16x8_t canonical_mod_q(int16x8_t value)
{
    const int16x8_t q = vdupq_n_s16(3457);
    const int16x8_t reciprocal = vdupq_n_s16(9);
    int16x8_t quotient = vqrdmulhq_s16(value, reciprocal);
    int16x8_t residual = vmlsq_s16(value, quotient, q);
    int16x8_t negative = vshrq_n_s16(residual, 15);
    return vaddq_s16(residual, vandq_s16(negative, q));
}

/* Pack eight already contiguous canonical coefficients into exactly 12 bytes. */
static inline void pack8(uint8_t *out, int16x8_t value)
{
    uint16x8_t u = vreinterpretq_u16_s16(value);
    uint16x8_t even = vuzp1q_u16(u, u);
    uint16x8_t odd = vuzp2q_u16(u, u);
    uint16x8_t low = vorrq_u16(even, vshlq_n_u16(odd, 12));
    uint16x8_t high = vshrq_n_u16(odd, 4);
    uint8x16x2_t table = {{
        vreinterpretq_u8_u16(low), vreinterpretq_u8_u16(high)
    }};
    uint8x16_t bytes = vqtbl2q_u8(table, vld1q_u8(pack_index));
    uint32_t tail = vgetq_lane_u32(vreinterpretq_u32_u8(bytes), 2);
    vst1_u8(out, vget_low_u8(bytes));
    memcpy(out + 8, &tail, sizeof tail);
}

static inline void emit_q(uint8_t *out, int output_q, int table_row,
                          int16x8_t value)
{
    int16x8_t ordered = vreinterpretq_s16_u8(vqtbl1q_u8(
        vreinterpretq_u8_s16(value), vld1q_u8(p3b5_a_fwd[table_row])));
    pack8(out + 12 * output_q, canonical_mod_q(ordered));
}

static inline void transpose8(int16x8_t r0, int16x8_t r1,
                              int16x8_t r2, int16x8_t r3,
                              int16x8_t r4, int16x8_t r5,
                              int16x8_t r6, int16x8_t r7,
                              int16x8_t t[8])
{
    int16x8_t a0 = vtrn1q_s16(r0, r1);
    int16x8_t a1 = vtrn2q_s16(r0, r1);
    int16x8_t a2 = vtrn1q_s16(r2, r3);
    int16x8_t a3 = vtrn2q_s16(r2, r3);
    int16x8_t a4 = vtrn1q_s16(r4, r5);
    int16x8_t a5 = vtrn2q_s16(r4, r5);
    int16x8_t a6 = vtrn1q_s16(r6, r7);
    int16x8_t a7 = vtrn2q_s16(r6, r7);
    int32x4_t b0 = vtrn1q_s32(vreinterpretq_s32_s16(a0),
                               vreinterpretq_s32_s16(a2));
    int32x4_t b1 = vtrn1q_s32(vreinterpretq_s32_s16(a1),
                               vreinterpretq_s32_s16(a3));
    int32x4_t b2 = vtrn2q_s32(vreinterpretq_s32_s16(a0),
                               vreinterpretq_s32_s16(a2));
    int32x4_t b3 = vtrn2q_s32(vreinterpretq_s32_s16(a1),
                               vreinterpretq_s32_s16(a3));
    int32x4_t b4 = vtrn1q_s32(vreinterpretq_s32_s16(a4),
                               vreinterpretq_s32_s16(a6));
    int32x4_t b5 = vtrn1q_s32(vreinterpretq_s32_s16(a5),
                               vreinterpretq_s32_s16(a7));
    int32x4_t b6 = vtrn2q_s32(vreinterpretq_s32_s16(a4),
                               vreinterpretq_s32_s16(a6));
    int32x4_t b7 = vtrn2q_s32(vreinterpretq_s32_s16(a5),
                               vreinterpretq_s32_s16(a7));
    t[0] = vreinterpretq_s16_s64(vtrn1q_s64(vreinterpretq_s64_s32(b0),
                                             vreinterpretq_s64_s32(b4)));
    t[1] = vreinterpretq_s16_s64(vtrn1q_s64(vreinterpretq_s64_s32(b1),
                                             vreinterpretq_s64_s32(b5)));
    t[2] = vreinterpretq_s16_s64(vtrn1q_s64(vreinterpretq_s64_s32(b2),
                                             vreinterpretq_s64_s32(b6)));
    t[3] = vreinterpretq_s16_s64(vtrn1q_s64(vreinterpretq_s64_s32(b3),
                                             vreinterpretq_s64_s32(b7)));
    t[4] = vreinterpretq_s16_s64(vtrn2q_s64(vreinterpretq_s64_s32(b0),
                                             vreinterpretq_s64_s32(b4)));
    t[5] = vreinterpretq_s16_s64(vtrn2q_s64(vreinterpretq_s64_s32(b1),
                                             vreinterpretq_s64_s32(b5)));
    t[6] = vreinterpretq_s16_s64(vtrn2q_s64(vreinterpretq_s64_s32(b2),
                                             vreinterpretq_s64_s32(b6)));
    t[7] = vreinterpretq_s16_s64(vtrn2q_s64(vreinterpretq_s64_s32(b3),
                                             vreinterpretq_s64_s32(b7)));
}

#define SET_LANE(K, W, J8) \
    vsetq_lane_s16(vgetq_lane_s16((J8), (K)), (W), (K))

static __attribute__((noinline)) void route9_pack(
    uint8_t out[1296], const int16_t *in, int output_q_base)
{
    int16x8_t j0 = vld1q_s16(in + 8 * 24);
    int16x8_t j1 = vld1q_s16(in + 7 * 24);
    int16x8_t j2 = vld1q_s16(in + 6 * 24);
    int16x8_t j3 = vld1q_s16(in + 5 * 24);
    int16x8_t j4 = vld1q_s16(in + 4 * 24);
    int16x8_t j5 = vld1q_s16(in + 3 * 24);
    int16x8_t j6 = vld1q_s16(in + 2 * 24);
    int16x8_t j7 = vld1q_s16(in + 1 * 24);
    int16x8_t j8 = vld1q_s16(in);
    int16x8_t t[8];
    int16x8_t w;

    transpose8(j0, vextq_s16(j1, j1, 7), vextq_s16(j2, j2, 6),
               vextq_s16(j3, j3, 5), vextq_s16(j4, j4, 4),
               vextq_s16(j5, j5, 3), vextq_s16(j6, j6, 2),
               vextq_s16(j7, j7, 1), t);

    w = SET_LANE(0, t[0], j8);
    emit_q(out, output_q_base + 6 * 0, 0, w);
    w = vbslq_s16(vld1q_u16(p3b5_prefix[0]), t[0], t[1]);
    emit_q(out, output_q_base + 6 * 3, 1, SET_LANE(1, w, j8));
    w = vbslq_s16(vld1q_u16(p3b5_prefix[1]), t[1], t[2]);
    emit_q(out, output_q_base + 6 * 6, 2, SET_LANE(2, w, j8));
    w = vbslq_s16(vld1q_u16(p3b5_prefix[2]), t[2], t[3]);
    emit_q(out, output_q_base + 6 * 1, 3, SET_LANE(3, w, j8));
    w = vbslq_s16(vld1q_u16(p3b5_prefix[3]), t[3], t[4]);
    emit_q(out, output_q_base + 6 * 4, 4, SET_LANE(4, w, j8));
    w = vbslq_s16(vld1q_u16(p3b5_prefix[4]), t[4], t[5]);
    emit_q(out, output_q_base + 6 * 7, 5, SET_LANE(5, w, j8));
    w = vbslq_s16(vld1q_u16(p3b5_prefix[5]), t[5], t[6]);
    emit_q(out, output_q_base + 6 * 2, 6, SET_LANE(6, w, j8));
    emit_q(out, output_q_base + 6 * 5, 7, SET_LANE(7, t[6], j8));
    emit_q(out, output_q_base + 6 * 8, 8, t[7]);
}

#undef SET_LANE

void gt864_fr0_fused_tobytes(uint8_t out[1296], const int16_t fr0[864])
{
    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            for (int part = 0; part < 2; part++) {
                const int16_t *in = fr0 + 432 * top + 216 * part
                                    + 8 * component;
                int output_q_base = 54 * top + 3 * part + component;
                route9_pack(out, in, output_q_base);
            }
        }
    }
}
