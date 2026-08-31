#include "gt864_boundary.h"
#include "gt864_boundary_tables.h"

#include <arm_neon.h>
#include <stddef.h>
#include <stdint.h>

#define Q 3457
#define THETA 9

#if defined(__clang__) || defined(__GNUC__)
#define ALWAYS_INLINE static inline __attribute__((always_inline))
#define NOINLINE __attribute__((noinline))
#else
#define ALWAYS_INLINE static inline
#define NOINLINE
#endif

static const int16_t mod_consts[8] __attribute__((aligned(16))) = {
    3457, 0, -12929, 0, 0, 0, 0, 0
};

typedef struct {
    int16x8_t v[8];
} vectors8;

typedef struct {
    int16x8_t v[3];
} vectors3;

typedef struct {
    int16x8_t v[9];
} vectors9;

ALWAYS_INLINE size_t main_index(int top, int component, int column)
{
    return (size_t)(((top * 3 + component) * 16 + column) * 8);
}

ALWAYS_INLINE size_t tail_index(int top, int component, int column)
{
    return (size_t)(GT864_BOUNDARY_MAIN_COEFFICIENTS + column * 8 +
                    top * 3 + component);
}

ALWAYS_INLINE size_t fr_scratch_index(int top, int component, int block,
                                      int row)
{
    return (size_t)(((((top * 3 + component) * 2 + block) * 9 + row) * 8));
}

ALWAYS_INLINE size_t fr_output_index(int top, int row, int column,
                                     int component)
{
    int group = top * 18 + row * 2 + column / 8;
    return (size_t)(24 * group + 8 * component + column % 8);
}

ALWAYS_INLINE size_t fc_output_index(int top, int row, int column,
                                     int component)
{
    int group;
    int lane;

    if (row < 8) {
        group = top * 18 + column;
        lane = row;
    } else {
        group = top * 18 + 16 + column / 8;
        lane = column % 8;
    }
    return (size_t)(24 * group + 8 * component + lane);
}

/*
 * Exact 8x8 transpose of signed 16-bit lanes.  Input vector i is one column
 * R_{c+i}=[U_0,...,U_7]; output vector s is
 * S_s=[U_s(c+0),...,U_s(c+7)].  No arithmetic, scale, or bound changes.
 */
ALWAYS_INLINE vectors8 transpose8x8_s16(vectors8 in)
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

/* R^0 vector x times public Montgomery vector yR -> bounded R^0 vector. */
ALWAYS_INLINE int16x8_t fqmul_public(int16x8_t x, int16x8_t y,
                                     int16x8_t con)
{
    int32x4_t low = vmull_s16(vget_low_s16(x), vget_low_s16(y));
    int32x4_t high = vmull_high_s16(x, y);
    int16x8_t quotient;

    quotient = vuzp1q_s16(vreinterpretq_s16_s32(low),
                          vreinterpretq_s16_s32(high));
    quotient = vmulq_laneq_s16(quotient, con, 2);
    low = vmlal_lane_s16(low, vget_low_s16(quotient),
                         vget_low_s16(con), 0);
    high = vmlal_high_lane_s16(high, quotient, vget_low_s16(con), 0);
    return vuzp2q_s16(vreinterpretq_s16_s32(low),
                      vreinterpretq_s16_s32(high));
}

/* Positive-exponent order-three butterfly, lane-wise. */
ALWAYS_INLINE vectors3 b3_forward(int16x8_t x0, int16x8_t x1,
                                  int16x8_t x2, int16x8_t con)
{
    const int16x8_t rho = vdupq_n_s16(GT864_RHO_MONT);
    const int16x8_t rho2 = vdupq_n_s16(GT864_RHO2_MONT);
    vectors3 out;

    out.v[0] = vaddq_s16(vaddq_s16(x0, x1), x2);
    out.v[1] = vaddq_s16(
        x0, vaddq_s16(fqmul_public(x1, rho, con),
                      fqmul_public(x2, rho2, con)));
    out.v[2] = vaddq_s16(
        x0, vaddq_s16(fqmul_public(x1, rho2, con),
                      fqmul_public(x2, rho, con)));
    return out;
}

/* Paper-oriented 9-point NTT; each register is one row across 8 columns. */
ALWAYS_INLINE vectors9 ntt9_fr(vectors9 f,
                               const int16_t twist_table[9][8],
                               int16x8_t con)
{
    vectors3 a;
    vectors3 b;
    vectors3 c;
    vectors3 group;
    vectors9 out;
    const int16x8_t eta = vdupq_n_s16(GT864_ETA_MONT);
    const int16x8_t eta_inv = vdupq_n_s16(GT864_ETA_INV_MONT);

    for (int s = 1; s < 9; s++) {
        int16x8_t twist = vld1q_s16(twist_table[s]);
        f.v[s] = fqmul_public(f.v[s], twist, con);
    }

    a = b3_forward(f.v[0], f.v[3], f.v[6], con);
    b = b3_forward(f.v[1], f.v[4], f.v[7], con);
    c = b3_forward(f.v[8], f.v[2], f.v[5], con);

    group = b3_forward(a.v[0], b.v[0], c.v[0], con);
    out.v[0] = group.v[0];
    out.v[3] = group.v[1];
    out.v[6] = group.v[2];

    group = b3_forward(a.v[1], fqmul_public(b.v[1], eta, con),
                       fqmul_public(c.v[1], eta_inv, con), con);
    out.v[1] = group.v[0];
    out.v[4] = group.v[1];
    out.v[7] = group.v[2];

    group = b3_forward(a.v[2], fqmul_public(b.v[2], eta_inv, con),
                       fqmul_public(c.v[2], eta, con), con);
    out.v[8] = group.v[0];
    out.v[2] = group.v[1];
    out.v[5] = group.v[2];
    return out;
}

/*
 * Within-register FC-0 transform.  Only lanes 0..2 are live during each
 * radix-3 level.  This deliberately exposes the routing cost instead of
 * hiding it in scalar C: lane insert/extract operations gather the first
 * layer and transpose the 3x3 intermediate; the final outputs are packed to
 * rows 0..7 plus a scalar row-8 tail.
 */
ALWAYS_INLINE int16x8_t gather3(int16x8_t a, int lane0, int lane1, int lane2)
{
    int16x8_t out = vdupq_n_s16(0);

    switch (lane0) {
    case 0: out = vsetq_lane_s16(vgetq_lane_s16(a, 0), out, 0); break;
    case 1: out = vsetq_lane_s16(vgetq_lane_s16(a, 1), out, 0); break;
    case 2: out = vsetq_lane_s16(vgetq_lane_s16(a, 2), out, 0); break;
    case 3: out = vsetq_lane_s16(vgetq_lane_s16(a, 3), out, 0); break;
    case 4: out = vsetq_lane_s16(vgetq_lane_s16(a, 4), out, 0); break;
    case 5: out = vsetq_lane_s16(vgetq_lane_s16(a, 5), out, 0); break;
    case 6: out = vsetq_lane_s16(vgetq_lane_s16(a, 6), out, 0); break;
    default: out = vsetq_lane_s16(vgetq_lane_s16(a, 7), out, 0); break;
    }
    switch (lane1) {
    case 0: out = vsetq_lane_s16(vgetq_lane_s16(a, 0), out, 1); break;
    case 1: out = vsetq_lane_s16(vgetq_lane_s16(a, 1), out, 1); break;
    case 2: out = vsetq_lane_s16(vgetq_lane_s16(a, 2), out, 1); break;
    case 3: out = vsetq_lane_s16(vgetq_lane_s16(a, 3), out, 1); break;
    case 4: out = vsetq_lane_s16(vgetq_lane_s16(a, 4), out, 1); break;
    case 5: out = vsetq_lane_s16(vgetq_lane_s16(a, 5), out, 1); break;
    case 6: out = vsetq_lane_s16(vgetq_lane_s16(a, 6), out, 1); break;
    default: out = vsetq_lane_s16(vgetq_lane_s16(a, 7), out, 1); break;
    }
    switch (lane2) {
    case 0: out = vsetq_lane_s16(vgetq_lane_s16(a, 0), out, 2); break;
    case 1: out = vsetq_lane_s16(vgetq_lane_s16(a, 1), out, 2); break;
    case 2: out = vsetq_lane_s16(vgetq_lane_s16(a, 2), out, 2); break;
    case 3: out = vsetq_lane_s16(vgetq_lane_s16(a, 3), out, 2); break;
    case 4: out = vsetq_lane_s16(vgetq_lane_s16(a, 4), out, 2); break;
    case 5: out = vsetq_lane_s16(vgetq_lane_s16(a, 5), out, 2); break;
    case 6: out = vsetq_lane_s16(vgetq_lane_s16(a, 6), out, 2); break;
    default: out = vsetq_lane_s16(vgetq_lane_s16(a, 7), out, 2); break;
    }
    return out;
}

ALWAYS_INLINE void ntt9_fc(int16x8_t input, int16_t tail, int top, int column,
                           int16x8_t con, int16x8_t *main_out,
                           int16_t *tail_out)
{
    const int16x8_t main_twist =
        vld1q_s16(&gt864_twist_mont[top][column][0]);
    const int16x8_t tail_twist =
        vdupq_n_s16(gt864_twist_mont[top][column][8]);
    const int16x8_t eta_mix_b = {
        GT864_R_MONT, GT864_ETA_MONT, GT864_ETA_INV_MONT, 0, 0, 0, 0, 0
    };
    const int16x8_t eta_mix_c = {
        GT864_R_MONT, GT864_ETA_INV_MONT, GT864_ETA_MONT, 0, 0, 0, 0, 0
    };
    int16x8_t f = fqmul_public(input, main_twist, con);
    int16x8_t tail_vector = fqmul_public(vdupq_n_s16(tail), tail_twist, con);
    int16x8_t x0 = gather3(f, 0, 1, 0);
    int16x8_t x1 = gather3(f, 3, 4, 2);
    int16x8_t x2 = gather3(f, 6, 7, 5);
    vectors3 first;
    int16x8_t u0;
    int16x8_t u1;
    int16x8_t u2;
    vectors3 second;
    int16x8_t packed = vdupq_n_s16(0);

    x0 = vsetq_lane_s16(vgetq_lane_s16(tail_vector, 0), x0, 2);
    first = b3_forward(x0, x1, x2, con);

    u0 = vdupq_n_s16(0);
    u0 = vsetq_lane_s16(vgetq_lane_s16(first.v[0], 0), u0, 0);
    u0 = vsetq_lane_s16(vgetq_lane_s16(first.v[1], 0), u0, 1);
    u0 = vsetq_lane_s16(vgetq_lane_s16(first.v[2], 0), u0, 2);
    u1 = vdupq_n_s16(0);
    u1 = vsetq_lane_s16(vgetq_lane_s16(first.v[0], 1), u1, 0);
    u1 = vsetq_lane_s16(vgetq_lane_s16(first.v[1], 1), u1, 1);
    u1 = vsetq_lane_s16(vgetq_lane_s16(first.v[2], 1), u1, 2);
    u2 = vdupq_n_s16(0);
    u2 = vsetq_lane_s16(vgetq_lane_s16(first.v[0], 2), u2, 0);
    u2 = vsetq_lane_s16(vgetq_lane_s16(first.v[1], 2), u2, 1);
    u2 = vsetq_lane_s16(vgetq_lane_s16(first.v[2], 2), u2, 2);

    u1 = fqmul_public(u1, eta_mix_b, con);
    u2 = fqmul_public(u2, eta_mix_c, con);
    second = b3_forward(u0, u1, u2, con);

    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[0], 0), packed, 0);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[0], 1), packed, 1);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[1], 2), packed, 2);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[1], 0), packed, 3);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[1], 1), packed, 4);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[2], 2), packed, 5);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[2], 0), packed, 6);
    packed = vsetq_lane_s16(vgetq_lane_s16(second.v[2], 1), packed, 7);
    *main_out = packed;
    *tail_out = vgetq_lane_s16(second.v[0], 2);
}

ALWAYS_INLINE void fr_bridge_impl(int16_t *out, const int16_t *in)
{
    for (int block = 0; block < 2; block++) {
        vectors8 tail_rows;
        vectors8 tail_columns;

        for (int lane = 0; lane < 8; lane++)
            tail_rows.v[lane] = vld1q_s16(
                in + GT864_BOUNDARY_MAIN_COEFFICIENTS +
                (block * 8 + lane) * 8);
        tail_columns = transpose8x8_s16(tail_rows);

        for (int top = 0; top < 2; top++) {
            for (int component = 0; component < 3; component++) {
                vectors8 columns;
                vectors8 rows;

                for (int lane = 0; lane < 8; lane++)
                    columns.v[lane] = vld1q_s16(
                        in + main_index(top, component, block * 8 + lane));
                rows = transpose8x8_s16(columns);
                for (int s = 0; s < 8; s++)
                    vst1q_s16(out + fr_scratch_index(top, component, block, s),
                              rows.v[s]);
                vst1q_s16(out + fr_scratch_index(top, component, block, 8),
                          tail_columns.v[top * 3 + component]);
            }
        }
    }
}

/*
 * Fused M4.2 load shape: transpose one 8-column main tile in registers and
 * construct the ninth NTT9 register with eight exact 16-bit lane loads.
 * Nothing is materialized between this helper and ntt9_fr.
 */
ALWAYS_INLINE vectors9 load_fr_transform(const int16_t *in, int top,
                                          int component, int block)
{
    vectors8 columns;
    vectors8 rows;
    vectors9 out;
    int first_column = block * 8;

    for (int lane = 0; lane < 8; lane++)
        columns.v[lane] = vld1q_s16(
            in + main_index(top, component, first_column + lane));
    rows = transpose8x8_s16(columns);
    for (int s = 0; s < 8; s++)
        out.v[s] = rows.v[s];

    out.v[8] = vdupq_n_s16(0);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 0)], out.v[8], 0);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 1)], out.v[8], 1);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 2)], out.v[8], 2);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 3)], out.v[8], 3);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 4)], out.v[8], 4);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 5)], out.v[8], 5);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 6)], out.v[8], 6);
    out.v[8] = vsetq_lane_s16(
        in[tail_index(top, component, first_column + 7)], out.v[8], 7);
    return out;
}

NOINLINE void gt864_fr_bridge(int16_t out[GT864_BOUNDARY_FR_SCRATCH_COEFFICIENTS],
                              const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS])
{
    fr_bridge_impl(out, in);
}

NOINLINE void gt864_fc_tail_extract(
    int16_t out[GT864_BOUNDARY_FC_TAIL_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS])
{
    for (int block = 0; block < 2; block++) {
        vectors8 rows;
        vectors8 columns;

        for (int lane = 0; lane < 8; lane++)
            rows.v[lane] = vld1q_s16(in + GT864_BOUNDARY_MAIN_COEFFICIENTS +
                                     (block * 8 + lane) * 8);
        columns = transpose8x8_s16(rows);
        for (int bank = 0; bank < 6; bank++)
            vst1q_s16(out + (bank * 2 + block) * 8, columns.v[bank]);
    }
}

NOINLINE void gt864_boundary_fr0(
    int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS])
{
    const int16x8_t con = vld1q_s16(mod_consts);

    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            for (int block = 0; block < 2; block++) {
                vectors9 f = load_fr_transform(in, top, component, block);
                vectors9 transformed;

                transformed = ntt9_fr(
                    f, gt864_twist_fr_mont[top][block], con);
                for (int row = 0; row < 9; row++) {
                    int group = top * 18 + row * 2 + block;
                    vst1q_s16(out + 24 * group + 8 * component,
                              transformed.v[row]);
                }
            }
        }
    }
}

NOINLINE void gt864_boundary_fr_lane0(
    int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS])
{
    const int16x8_t con = vld1q_s16(mod_consts);

    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            for (int block = 0; block < 2; block++) {
                vectors9 f = load_fr_transform(in, top, component, block);
                vectors9 transformed;

                transformed = ntt9_fr(
                    f, gt864_twist_fr_lane0_mont[top][block], con);
                for (int physical_row = 0; physical_row < 9; physical_row++) {
                    int group = top * 18 + physical_row * 2 + block;
                    vst1q_s16(out + 24 * group + 8 * component,
                              transformed.v[physical_row]);
                }
            }
        }
    }
}

NOINLINE void gt864_boundary_fc0(
    int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS])
{
    const int16x8_t con = vld1q_s16(mod_consts);

    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int16_t row8[16] __attribute__((aligned(16)));

            for (int column = 0; column < 16; column++) {
                int16x8_t transformed;
                int16_t transformed_tail;
                int group = top * 18 + column;

                ntt9_fc(vld1q_s16(in + main_index(top, component, column)),
                        in[tail_index(top, component, column)], top, column,
                        con, &transformed, &transformed_tail);
                vst1q_s16(out + 24 * group + 8 * component, transformed);
                row8[column] = transformed_tail;
            }
            for (int block = 0; block < 2; block++) {
                int group = top * 18 + 16 + block;
                vst1q_s16(out + 24 * group + 8 * component,
                          vld1q_s16(row8 + block * 8));
            }
        }
    }
}

static int16_t canonical(int64_t value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    return (int16_t)value;
}

static int16_t centered(int64_t value)
{
    int16_t result = canonical(value);
    return result > Q / 2 ? (int16_t)(result - Q) : result;
}

static int16_t powmod(int16_t base, int exponent)
{
    int16_t result = 1;

    while (exponent > 0) {
        if (exponent & 1)
            result = canonical((int32_t)result * base);
        base = canonical((int32_t)base * base);
        exponent >>= 1;
    }
    return result;
}

NOINLINE void gt864_boundary_reference_fr0(
    int16_t out[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    const int16_t in[GT864_BOUNDARY_INPUT_COEFFICIENTS])
{
    const int16_t eta = powmod(THETA, 96);

    for (int top = 0; top < 2; top++) {
        int residue = top == 0 ? 1 : 5;

        for (int component = 0; component < 3; component++) {
            for (int column = 0; column < 16; column++) {
                int16_t lambda = powmod(THETA, residue + 6 * column);

                for (int row = 0; row < 9; row++) {
                    int64_t sum = 0;
                    int16_t root = canonical((int32_t)lambda *
                                             powmod(eta, row));
                    int16_t power = 1;

                    for (int s = 0; s < 9; s++) {
                        int16_t value = s < 8
                            ? in[main_index(top, component, column) + s]
                            : in[tail_index(top, component, column)];
                        sum += (int32_t)value * power;
                        power = canonical((int32_t)power * root);
                    }
                    out[fr_output_index(top, row, column, component)] =
                        centered(sum);
                }
            }
        }
    }
}

int16_t gt864_boundary_fr_get(
    const int16_t in[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    int top, int row, int column, int component)
{
    return in[fr_output_index(top, row, column, component)];
}

int16_t gt864_boundary_fc_get(
    const int16_t in[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    int top, int row, int column, int component)
{
    return in[fc_output_index(top, row, column, component)];
}

int16_t gt864_boundary_fr_lane0_get(
    const int16_t in[GT864_BOUNDARY_OUTPUT_COEFFICIENTS],
    int top, int logical_row, int column, int component)
{
    int rotation = gt864_fr_lane0_rotation[column];
    int physical_row = (logical_row - rotation + 9) % 9;
    return in[fr_output_index(top, physical_row, column, component)];
}
