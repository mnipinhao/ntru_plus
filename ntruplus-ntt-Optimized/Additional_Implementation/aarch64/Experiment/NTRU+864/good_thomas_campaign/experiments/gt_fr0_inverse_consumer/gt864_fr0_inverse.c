#include "gt864_fr0_inverse.h"
#include "gt864_fr0_inverse_tables.h"

#include <arm_neon.h>
#include <stddef.h>

static const int16_t mod_consts[8] __attribute__((aligned(16))) = {
    3457, 0, -12929, 0, 0, 0, 0, 0
};

static const uint8_t bit_reverse4[16] = {
    0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
};

typedef struct { int16x8_t v[3]; } vectors3;
typedef struct { int16x8_t v[8]; } vectors8;
typedef struct { int16x8_t v[9]; } vectors9;

static inline int16x8_t fqmul_public(int16x8_t x, int16x8_t c,
                                     int16x8_t mod)
{
    int32x4_t low = vmull_s16(vget_low_s16(x), vget_low_s16(c));
    int32x4_t high = vmull_high_s16(x, c);
    int16x8_t quotient = vuzp1q_s16(vreinterpretq_s16_s32(low),
                                    vreinterpretq_s16_s32(high));
    quotient = vmulq_laneq_s16(quotient, mod, 2);
    low = vmlal_lane_s16(low, vget_low_s16(quotient),
                         vget_low_s16(mod), 0);
    high = vmlal_high_lane_s16(high, quotient,
                               vget_low_s16(mod), 0);
    return vuzp2q_s16(vreinterpretq_s16_s32(low),
                      vreinterpretq_s16_s32(high));
}

/* Unscaled negative-exponent length-3 transform. */
static inline vectors3 b3_inverse(int16x8_t x0, int16x8_t x1,
                                  int16x8_t x2, int16x8_t mod)
{
    const int16x8_t rho = vdupq_n_s16(GT864_RHO_MONT);
    const int16x8_t rho2 = vdupq_n_s16(GT864_RHO2_MONT);
    vectors3 out;

    out.v[0] = vaddq_s16(vaddq_s16(x0, x1), x2);
    out.v[1] = vaddq_s16(
        x0, vaddq_s16(fqmul_public(x1, rho2, mod),
                      fqmul_public(x2, rho, mod)));
    out.v[2] = vaddq_s16(
        x0, vaddq_s16(fqmul_public(x1, rho, mod),
                      fqmul_public(x2, rho2, mod)));
    return out;
}

static inline vectors9 intt9_fr(vectors9 in,
                                const int16_t inverse_twist[9][8],
                                int16x8_t mod)
{
    const int16x8_t eta = vdupq_n_s16(GT864_ETA_MONT);
    const int16x8_t eta_inv = vdupq_n_s16(GT864_ETA_INV_MONT);
    vectors3 g0 = b3_inverse(in.v[0], in.v[3], in.v[6], mod);
    vectors3 g1 = b3_inverse(in.v[1], in.v[4], in.v[7], mod);
    vectors3 g2 = b3_inverse(in.v[8], in.v[2], in.v[5], mod);
    vectors3 a;
    vectors3 b;
    vectors3 c;
    vectors9 out;

    a.v[0] = g0.v[0]; a.v[1] = g1.v[0]; a.v[2] = g2.v[0];
    b.v[0] = g0.v[1];
    b.v[1] = fqmul_public(g1.v[1], eta_inv, mod);
    b.v[2] = fqmul_public(g2.v[1], eta, mod);
    c.v[0] = g0.v[2];
    c.v[1] = fqmul_public(g1.v[2], eta, mod);
    c.v[2] = fqmul_public(g2.v[2], eta_inv, mod);

    a = b3_inverse(a.v[0], a.v[1], a.v[2], mod);
    b = b3_inverse(b.v[0], b.v[1], b.v[2], mod);
    c = b3_inverse(c.v[0], c.v[1], c.v[2], mod);
    out.v[0] = a.v[0]; out.v[3] = a.v[1]; out.v[6] = a.v[2];
    out.v[1] = b.v[0]; out.v[4] = b.v[1]; out.v[7] = b.v[2];
    out.v[8] = c.v[0]; out.v[2] = c.v[1]; out.v[5] = c.v[2];

    for (int s = 0; s < 9; s++)
        out.v[s] = fqmul_public(out.v[s],
                                vld1q_s16(inverse_twist[s]), mod);
    return out;
}

static inline vectors8 transpose8x8_s16(vectors8 in)
{
    int16x8x2_t t0 = vtrnq_s16(in.v[0], in.v[1]);
    int16x8x2_t t1 = vtrnq_s16(in.v[2], in.v[3]);
    int16x8x2_t t2 = vtrnq_s16(in.v[4], in.v[5]);
    int16x8x2_t t3 = vtrnq_s16(in.v[6], in.v[7]);
    int32x4x2_t u0 = vtrnq_s32(vreinterpretq_s32_s16(t0.val[0]),
                               vreinterpretq_s32_s16(t1.val[0]));
    int32x4x2_t u1 = vtrnq_s32(vreinterpretq_s32_s16(t0.val[1]),
                               vreinterpretq_s32_s16(t1.val[1]));
    int32x4x2_t u2 = vtrnq_s32(vreinterpretq_s32_s16(t2.val[0]),
                               vreinterpretq_s32_s16(t3.val[0]));
    int32x4x2_t u3 = vtrnq_s32(vreinterpretq_s32_s16(t2.val[1]),
                               vreinterpretq_s32_s16(t3.val[1]));
    vectors8 out;

    out.v[0] = vcombine_s16(vget_low_s16(vreinterpretq_s16_s32(u0.val[0])),
                            vget_low_s16(vreinterpretq_s16_s32(u2.val[0])));
    out.v[1] = vcombine_s16(vget_low_s16(vreinterpretq_s16_s32(u1.val[0])),
                            vget_low_s16(vreinterpretq_s16_s32(u3.val[0])));
    out.v[2] = vcombine_s16(vget_low_s16(vreinterpretq_s16_s32(u0.val[1])),
                            vget_low_s16(vreinterpretq_s16_s32(u2.val[1])));
    out.v[3] = vcombine_s16(vget_low_s16(vreinterpretq_s16_s32(u1.val[1])),
                            vget_low_s16(vreinterpretq_s16_s32(u3.val[1])));
    out.v[4] = vcombine_s16(vget_high_s16(vreinterpretq_s16_s32(u0.val[0])),
                            vget_high_s16(vreinterpretq_s16_s32(u2.val[0])));
    out.v[5] = vcombine_s16(vget_high_s16(vreinterpretq_s16_s32(u1.val[0])),
                            vget_high_s16(vreinterpretq_s16_s32(u3.val[0])));
    out.v[6] = vcombine_s16(vget_high_s16(vreinterpretq_s16_s32(u0.val[1])),
                            vget_high_s16(vreinterpretq_s16_s32(u2.val[1])));
    out.v[7] = vcombine_s16(vget_high_s16(vreinterpretq_s16_s32(u1.val[1])),
                            vget_high_s16(vreinterpretq_s16_s32(u3.val[1])));
    return out;
}

static inline size_t fr_index(int top, int row, int column, int component)
{
    int group = top * 18 + row * 2 + column / 8;
    return (size_t)(24 * group + 8 * component + column % 8);
}

static inline size_t p8_main_index(int top, int component, int column)
{
    return (size_t)(((top * 3 + component) * 16 + column) * 8);
}

void gt864_fr0_inverse_ntt9_neon(int16_t out[GT864_INVERSE_P8_PADDED],
                                 const int16_t in[GT864_FR0_COEFFICIENTS])
{
    int16x8_t mod = vld1q_s16(mod_consts);

    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int bank = top * 3 + component;
            for (int block = 0; block < 2; block++) {
                int first_column = 8 * block;
                vectors9 rows;
                vectors8 first8;
                vectors8 columns;

                for (int row = 0; row < 9; row++)
                    rows.v[row] = vld1q_s16(
                        in + fr_index(top, row, first_column, component));
                rows = intt9_fr(rows,
                    gt864_inverse9_twist_mont[top][block], mod);
                for (int s = 0; s < 8; s++)
                    first8.v[s] = rows.v[s];
                columns = transpose8x8_s16(first8);
                for (int lane = 0; lane < 8; lane++)
                    vst1q_s16(out + p8_main_index(
                        top, component, first_column + lane), columns.v[lane]);

#define STORE_TAIL(lane) \
                vst1q_lane_s16(out + GT864_INVERSE_P8_MAIN + \
                    8 * (first_column + (lane)) + bank, rows.v[8], (lane))
                STORE_TAIL(0); STORE_TAIL(1); STORE_TAIL(2); STORE_TAIL(3);
                STORE_TAIL(4); STORE_TAIL(5); STORE_TAIL(6); STORE_TAIL(7);
#undef STORE_TAIL
            }
        }
    }
}

static inline void intt16(int16x8_t value[16], int16x8_t mod)
{
    for (int stage = 0, length = 2; stage < 4; stage++, length <<= 1) {
        int half = length >> 1;
        for (int start = 0; start < 16; start += length) {
            for (int j = 0; j < half; j++) {
                int left = start + j;
                int right = left + half;
                int16x8_t u = value[left];
                int16x8_t v = fqmul_public(
                    value[right], vdupq_n_s16(
                        gt864_inverse16_stage_twiddle_mont[stage][j]), mod);
                value[left] = vaddq_s16(u, v);
                value[right] = vsubq_s16(u, v);
            }
        }
    }
}

static inline void store4_component(int16_t *out, int t, int s0,
                                    int component, int16x4_t low,
                                    int16x4_t high)
{
#define STORE4(lane) \
    vst1_lane_s16(out + 3 * (s0 + (lane) + 9 * t) + component, low, (lane)); \
    vst1_lane_s16(out + 3 * (s0 + (lane) + 9 * (t + 16)) + component, \
                  high, (lane))
    STORE4(0); STORE4(1); STORE4(2); STORE4(3);
#undef STORE4
}

static inline void top_recombine8(int16x8_t packed, int16x8_t mod,
                                  int16x4_t *low, int16x4_t *high)
{
    int16x8_t a = vcombine_s16(vget_low_s16(packed), vget_low_s16(packed));
    int16x8_t b = vcombine_s16(vget_high_s16(packed), vget_high_s16(packed));
    int16x8_t h = fqmul_public(vsubq_s16(b, a),
                               vdupq_n_s16(GT864_DELTA_INV_MONT), mod);
    int16x8_t l = vsubq_s16(a, fqmul_public(
        h, vdupq_n_s16(GT864_ALPHA_MONT), mod));
    *low = vget_low_s16(l);
    *high = vget_low_s16(h);
}

void gt864_fr0_inverse_finish_neon(int16_t out[GT864_FR0_COEFFICIENTS],
                                   const int16_t in[GT864_INVERSE_P8_PADDED])
{
    int16x8_t mod = vld1q_s16(mod_consts);

    /* Pack alpha and beta into the two vector halves: no top-branch scratch. */
    for (int component = 0; component < 3; component++) {
        for (int half_s = 0; half_s < 2; half_s++) {
            int16x8_t value[16];
            for (int column = 0; column < 16; column++) {
                int16x4_t a4 = vld1_s16(in + p8_main_index(
                    0, component, column) + 4 * half_s);
                int16x4_t b4 = vld1_s16(in + p8_main_index(
                    1, component, column) + 4 * half_s);
                value[bit_reverse4[column]] = vcombine_s16(a4, b4);
            }
            intt16(value, mod);
            for (int t = 0; t < 16; t++) {
                int16x4_t low;
                int16x4_t high;
                value[t] = fqmul_public(value[t],
                    vld1q_s16(gt864_inverse16_main_scale_mont[t]), mod);
                top_recombine8(value[t], mod, &low, &high);
                store4_component(out, t, 4 * half_s, component, low, high);
            }
        }
    }

    /* s=8 is already packed as alpha[3], beta[3], padding[2]. */
    {
        int16x8_t value[16];
        for (int column = 0; column < 16; column++)
            value[bit_reverse4[column]] = vld1q_s16(
                in + GT864_INVERSE_P8_MAIN + 8 * column);
        intt16(value, mod);
        for (int t = 0; t < 16; t++) {
            int16x8_t a;
            int16x8_t b;
            int16x8_t high;
            int16x8_t low;
            value[t] = fqmul_public(value[t],
                vld1q_s16(gt864_inverse16_tail_scale_mont[t]), mod);
            a = value[t];
            b = vextq_s16(value[t], value[t], 3);
            high = fqmul_public(vsubq_s16(b, a),
                vdupq_n_s16(GT864_DELTA_INV_MONT), mod);
            low = vsubq_s16(a, fqmul_public(high,
                vdupq_n_s16(GT864_ALPHA_MONT), mod));
#define STORE_TAIL_COMPONENT(lane) \
            vst1q_lane_s16(out + 3 * (8 + 9 * t) + (lane), low, (lane)); \
            vst1q_lane_s16(out + 3 * (8 + 9 * (t + 16)) + (lane), \
                           high, (lane))
            STORE_TAIL_COMPONENT(0);
            STORE_TAIL_COMPONENT(1);
            STORE_TAIL_COMPONENT(2);
#undef STORE_TAIL_COMPONENT
        }
    }
}
