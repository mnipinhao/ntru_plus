#include "gt864_forward_compose.h"
#include "gt864_forward_barrett_tables.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#define Q 3457

static const uint8_t reverse4[16] = {
    0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15
};

static int16_t narrow_checked(int32_t value)
{
    assert(value >= INT16_MIN && value <= INT16_MAX);
    return (int16_t)value;
}
/* Scalar mirror of Neon mul/sqrdmulh/mls on signed halfwords. */
static int16_t fqmul_barrett(int16_t a, gt864_barrett_pair constant)
{
    int32_t quotient = ((int32_t)2 * a * constant.bprime + (1 << 15)) >> 16;
    int32_t value = (int32_t)a * constant.b - quotient * Q;
    return narrow_checked(value);
}

static size_t p8_index(int top, int component, int t, int s)
{
    if (s < 8)
        return (size_t)(((top * 3 + component) * 16 + t) * 8 + s);
    return (size_t)(768 + 8 * t + 3 * top + component);
}

static size_t output_index(int top, int row, int column, int component)
{
    int group = top * 18 + row * 2 + column / 8;
    return (size_t)(24 * group + 8 * component + column % 8);
}

static void b3(int16_t out[3], int16_t a, int16_t b, int16_t c)
{
    int16_t rb = fqmul_barrett(b, gt864_barrett_rho);
    int16_t r2c = fqmul_barrett(c, gt864_barrett_rho2);
    int16_t r2b = fqmul_barrett(b, gt864_barrett_rho2);
    int16_t rc = fqmul_barrett(c, gt864_barrett_rho);

    out[0] = narrow_checked((int32_t)a + b + c);
    out[1] = narrow_checked((int32_t)a + rb + r2c);
    out[2] = narrow_checked((int32_t)a + r2b + rc);
}

static void ntt9(int16_t out[9], const int16_t input[9],
                 int top, int block, int lane)
{
    int16_t f[9];
    int16_t a[3], b[3], c[3], g0[3], g1[3], g2[3];

    /* Including s=0 is deliberate: it bounds the NTT16 lazy left path. */
    for (int s = 0; s < 9; s++)
        f[s] = fqmul_barrett(
            input[s], gt864_forward9_twist[top][block][s][lane]);

    b3(a, f[0], f[3], f[6]);
    b3(b, f[1], f[4], f[7]);
    b3(c, f[8], f[2], f[5]);

    /* Only the direct-sum inputs need another boundary before level two. */
    b[0] = fqmul_barrett(b[0], gt864_barrett_one);
    c[0] = fqmul_barrett(c[0], gt864_barrett_one);
    b3(g0, a[0], b[0], c[0]);
    b3(g1, a[1], fqmul_barrett(b[1], gt864_barrett_eta),
       fqmul_barrett(c[1], gt864_barrett_eta_inv));
    b3(g2, a[2], fqmul_barrett(b[2], gt864_barrett_eta_inv),
       fqmul_barrett(c[2], gt864_barrett_eta));

    out[0] = g0[0]; out[1] = g1[0]; out[2] = g2[1];
    out[3] = g0[1]; out[4] = g1[1]; out[5] = g2[2];
    out[6] = g0[2]; out[7] = g1[2]; out[8] = g2[0];
}

void gt864_forward_compose_barrett(int16_t out[864], const int16_t p8[896])
{
    for (int top = 0; top < 2; top++) {
        for (int component = 0; component < 3; component++) {
            int16_t state[9][16];

            for (int s = 0; s < 9; s++) {
                for (int t = 0; t < 16; t++)
                    state[s][reverse4[t]] = fqmul_barrett(
                        p8[p8_index(top, component, t, s)],
                        gt864_forward16_twist[top][t]);
                for (int stage = 0, length = 2; stage < 4;
                     stage++, length <<= 1) {
                    int half = length / 2;
                    for (int start = 0; start < 16; start += length)
                        for (int j = 0; j < half; j++) {
                            int left = start + j;
                            int right = left + half;
                            int16_t u = state[s][left];
                            int16_t v = fqmul_barrett(
                                state[s][right],
                                gt864_forward16_stage[stage][j]);
                            state[s][left] = narrow_checked((int32_t)u + v);
                            state[s][right] = narrow_checked((int32_t)u - v);
                        }
                }
            }

            for (int column = 0; column < 16; column++) {
                int16_t input9[9], output9[9];
                for (int s = 0; s < 9; s++)
                    input9[s] = state[s][column];
                ntt9(output9, input9, top, column / 8, column % 8);
                for (int row = 0; row < 9; row++)
                    out[output_index(top, row, column, component)] = output9[row];
            }
        }
    }
}
