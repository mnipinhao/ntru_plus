#include "gt864_radix3.h"

#include <stddef.h>
#include <stdint.h>

#define NTRUPLUS_R             -147 /* R = 2^16 mod q */
#define NTRUPLUS_QINV         12929 /* q^-1 mod 2^16 */

/* Public radix-3 constants, all centered Montgomery representatives. */
#define GT864_ETA_MONT          1265 /* eta * R; eta has order 9 */
#define GT864_ETA_INV_MONT      -248 /* eta^-1 * R */
#define GT864_RHO_MONT          1033 /* eta^3 * R; order 3 */
#define GT864_RHO2_MONT         -886 /* eta^6 * R */

/*
 * Same compile-time column tables as the frozen Montgomery reference.
 * lambda[c] selects one ninth root above z[c], while z[c] is a root of
 * z^32-z^16+1.  Every entry is value * R mod q in centered form.
 */
static const int16_t gt864_lambda_mont[GT864_COLUMNS] = {
      -333,    365,    917,   -403,   -179,   1089,   1230,     -9,
      -553,  -1657,    -24,   -472,   1343,   1061,   1046,  -1323,
      1677,  -1589,    -71,   -244,    372,    402,   1654,   -889,
      1072,   1493,    -66,  -1298,   -628,    325,   1148,    683,
};

static const int16_t gt864_z_mont[GT864_COLUMNS] = {
      -888,  -1028,    963,  -1548,   -729,    978,    -62,   1392,
      -470,  -1603,   -775,    115,   1039,  -1024,  -1045,   -291,
       888,   1028,   -963,   1548,    729,   -978,     62,  -1392,
       470,   1603,    775,   -115,  -1039,   1024,   1045,    291,
};

static int16_t canonical(int32_t value)
{
    value %= GT864_Q;
    if (value < 0)
        value += GT864_Q;
    return (int16_t)value;
}

static int16_t centered(int32_t value)
{
    int16_t result = canonical(value);
    if (result > GT864_Q / 2)
        result = (int16_t)(result - GT864_Q);
    return result;
}

static int16_t montgomery_reduce(int32_t value)
{
    int16_t quotient = (int16_t)value * NTRUPLUS_QINV;
    return (int16_t)((value - (int32_t)quotient * GT864_Q) >> 16);
}

/* R^0 value times a public cR constant -> centered R^0 result. */
static int16_t fqmul_public(int16_t value, int16_t constant_mont)
{
    return centered(montgomery_reduce((int32_t)value * constant_mont));
}

/* Montgomery cR times dR -> centered cdR, used to walk lambda powers. */
static int16_t fqmul_mont(int16_t left_mont, int16_t right_mont)
{
    return centered(montgomery_reduce((int32_t)left_mont * right_mont));
}

/*
 * Positive-exponent B3:
 *
 *   out[k] = in[0] + in[1] rho^k + in[2] rho^(2k),  k=0,1,2.
 *
 * rho and rho^2 are fixed butterfly constants and are not part of the
 * inter-level constant-count comparison.
 */
static void b3_forward(int16_t out[3], int16_t in0, int16_t in1, int16_t in2)
{
    out[0] = centered((int32_t)in0 + in1 + in2);
    out[1] = centered((int32_t)in0 +
                      fqmul_public(in1, GT864_RHO_MONT) +
                      fqmul_public(in2, GT864_RHO2_MONT));
    out[2] = centered((int32_t)in0 +
                      fqmul_public(in1, GT864_RHO2_MONT) +
                      fqmul_public(in2, GT864_RHO_MONT));
}

/*
 * Paper-style nine-point orientation for the positive-exponent convention.
 * Input f already includes the column twist lambda^s.  The third first-layer
 * butterfly is cyclically oriented as (f8,f2,f5), so the four inter-level
 * multiplications use only eta and eta^-1:
 *
 *   (F0,F3,F6) = B3(a0, b0,          c0)
 *   (F1,F4,F7) = B3(a1, eta*b1,      eta^-1*c1)
 *   (F8,F2,F5) = B3(a2, eta^-1*b2,  eta*c2)
 *
 * Multiplication count remains four; distinct inter-level constants fall from
 * {eta, eta^2, eta^4} to {eta, eta^-1}.
 */
static void ntt9_oriented(int16_t out[GT864_ROWS],
                          const int16_t f[GT864_ROWS])
{
    int16_t a[3];
    int16_t b[3];
    int16_t c[3];
    int16_t group[3];

    b3_forward(a, f[0], f[3], f[6]);
    b3_forward(b, f[1], f[4], f[7]);
    b3_forward(c, f[8], f[2], f[5]);

    b3_forward(group, a[0], b[0], c[0]);
    out[0] = group[0];
    out[3] = group[1];
    out[6] = group[2];

    b3_forward(group, a[1], fqmul_public(b[1], GT864_ETA_MONT),
               fqmul_public(c[1], GT864_ETA_INV_MONT));
    out[1] = group[0];
    out[4] = group[1];
    out[7] = group[2];

    b3_forward(group, a[2], fqmul_public(b[2], GT864_ETA_INV_MONT),
               fqmul_public(c[2], GT864_ETA_MONT));
    out[8] = group[0];
    out[2] = group[1];
    out[5] = group[2];
}

void gt864_radix3_forward(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    for (size_t i = 0; i < GT864_N; i++)
        input[i] = centered(in[i]);

    /* Identical 32-column Horner stage to the frozen GT reference. */
    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int16_t value = 0;
                for (int degree = GT864_COLUMNS - 1; degree >= 0; degree--)
                    value = centered(fqmul_public(value, gt864_z_mont[col]) +
                                     input[GT864_LEAF_DEGREE *
                                           (residue + GT864_ROWS * degree) +
                                           branch]);
                stage32[branch][residue][col] = value;
            }
        }
    }

    /*
     * For each column, y=lambda*eta^row implies
     *
     *   F[row] = sum_s (T[s] lambda^s) eta^(row*s).
     *
     * The explicit lambda twist turns the remaining work into one NTT9.
     * A future Neon kernel may fuse these fixed factors into adjacent stages;
     * this C reference keeps the representation transition visible.
     */
    for (int col = 0; col < GT864_COLUMNS; col++) {
        for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
            int16_t f[GT864_ROWS];
            int16_t transformed[GT864_ROWS];
            int16_t lambda_power_mont = NTRUPLUS_R;

            for (int residue = 0; residue < GT864_ROWS; residue++) {
                f[residue] = fqmul_public(
                    stage32[branch][residue][col], lambda_power_mont);
                lambda_power_mont = fqmul_mont(
                    lambda_power_mont, gt864_lambda_mont[col]);
            }
            ntt9_oriented(transformed, f);
            for (int row = 0; row < GT864_ROWS; row++)
                out[(row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE +
                    branch] = transformed[row];
        }
    }
}

void gt864_radix3_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                      const int16_t b[GT864_N])
{
    int16_t forward_a[GT864_N];
    int16_t forward_b[GT864_N];
    int16_t product[GT864_N];

    gt864_radix3_forward(forward_a, a);
    gt864_radix3_forward(forward_b, b);
    gt864_mont_basemul(product, forward_a, forward_b);
    gt864_mont_inverse(out, product);
}
