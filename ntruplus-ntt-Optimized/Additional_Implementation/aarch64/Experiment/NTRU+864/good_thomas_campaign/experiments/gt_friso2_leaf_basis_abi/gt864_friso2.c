#include "gt864_friso2.h"

#include <stddef.h>

#define Q 3457
#define THETA 9

static int16_t canonical(int64_t value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    return (int16_t)value;
}

static int16_t centered(int64_t value)
{
    int16_t out = canonical(value);
    return out > Q / 2 ? (int16_t)(out - Q) : out;
}

static int16_t powmod(int16_t base, int exponent)
{
    int16_t result = 1;
    if (exponent < 0) {
        base = powmod(base, Q - 2);
        exponent = -exponent;
    }
    while (exponent != 0) {
        if (exponent & 1)
            result = canonical((int32_t)result * base);
        base = canonical((int32_t)base * base);
        exponent >>= 1;
    }
    return result;
}

static size_t fr_index(int top, int row, int column, int component)
{
    int group = top * 18 + row * 2 + column / 8;
    return (size_t)(24 * group + 8 * component + column % 8);
}

/*
 * z(alpha,row,column) = theta^(1+6c+96r), z0=9,  tau=theta^(2c+32r)
 * z(beta, row,column) = theta^(5+6c+96r), z0=3,  tau=27*theta^(2c+32r)
 * In both cases tau^3*z0=z.  The choices 9 and 3 are ordinary R0 values.
 */
static int16_t leaf_tau(int top, int row, int column)
{
    int16_t common = powmod(THETA, 2 * column + 32 * row);
    return top == 0 ? common : canonical(27 * common);
}

static void change_basis(int16_t out[GT864_FRISO2_COEFFICIENTS],
                         const int16_t in[GT864_FRISO2_COEFFICIENTS],
                         int inverse)
{
    for (int top = 0; top < 2; top++) {
        for (int row = 0; row < 9; row++) {
            for (int column = 0; column < 16; column++) {
                int16_t tau = leaf_tau(top, row, column);
                if (inverse)
                    tau = powmod(tau, -1);
                int16_t tau2 = canonical((int32_t)tau * tau);
                out[fr_index(top, row, column, 0)] =
                    centered(in[fr_index(top, row, column, 0)]);
                out[fr_index(top, row, column, 1)] = centered(
                    (int64_t)in[fr_index(top, row, column, 1)] * tau);
                out[fr_index(top, row, column, 2)] = centered(
                    (int64_t)in[fr_index(top, row, column, 2)] * tau2);
            }
        }
    }
}

void gt864_friso2_normalize(int16_t out[GT864_FRISO2_COEFFICIENTS],
                            const int16_t in[GT864_FRISO2_COEFFICIENTS])
{
    change_basis(out, in, 0);
}

void gt864_friso2_denormalize(int16_t out[GT864_FRISO2_COEFFICIENTS],
                              const int16_t in[GT864_FRISO2_COEFFICIENTS])
{
    change_basis(out, in, 1);
}

static void cubic_product(int16_t out[3], const int16_t a[3],
                          const int16_t b[3], int z0)
{
    out[0] = centered((int64_t)a[0] * b[0] +
                      (int64_t)z0 * (a[1] * (int32_t)b[2] +
                                     a[2] * (int32_t)b[1]));
    out[1] = centered((int64_t)a[0] * b[1] +
                      (int64_t)a[1] * b[0] +
                      (int64_t)z0 * a[2] * b[2]);
    out[2] = centered((int64_t)a[0] * b[2] +
                      (int64_t)a[1] * b[1] +
                      (int64_t)a[2] * b[0]);
}

static void basemul_common(int16_t out[GT864_FRISO2_COEFFICIENTS],
                           const int16_t a[GT864_FRISO2_COEFFICIENTS],
                           const int16_t b[GT864_FRISO2_COEFFICIENTS],
                           const int16_t *addend)
{
    for (int top = 0; top < 2; top++) {
        int z0 = top == 0 ? 9 : 3;
        for (int row = 0; row < 9; row++) {
            for (int column = 0; column < 16; column++) {
                int16_t av[3];
                int16_t bv[3];
                int16_t product[3];
                for (int component = 0; component < 3; component++) {
                    size_t index = fr_index(top, row, column, component);
                    av[component] = a[index];
                    bv[component] = b[index];
                }
                cubic_product(product, av, bv, z0);
                for (int component = 0; component < 3; component++) {
                    size_t index = fr_index(top, row, column, component);
                    out[index] = centered((int32_t)product[component] +
                                          (addend == NULL ? 0 : addend[index]));
                }
            }
        }
    }
}

void gt864_friso2_basemul(int16_t out[GT864_FRISO2_COEFFICIENTS],
                          const int16_t a[GT864_FRISO2_COEFFICIENTS],
                          const int16_t b[GT864_FRISO2_COEFFICIENTS])
{
    basemul_common(out, a, b, NULL);
}

void gt864_friso2_basemul_add(int16_t out[GT864_FRISO2_COEFFICIENTS],
                              const int16_t a[GT864_FRISO2_COEFFICIENTS],
                              const int16_t b[GT864_FRISO2_COEFFICIENTS],
                              const int16_t c[GT864_FRISO2_COEFFICIENTS])
{
    basemul_common(out, a, b, c);
}
