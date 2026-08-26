#include "gt864_montgomery.h"

#include <assert.h>
#include <stddef.h>
#include <stdint.h>

#define GT864_POINTS (GT864_N / GT864_LEAF_DEGREE)
#define GT864_QINV 12929
#define GT864_R 3310
#define GT864_RSQ 867

extern const int16_t zetas[GT864_POINTS];

static int16_t canonical(int64_t value)
{
    value %= GT864_Q;
    if (value < 0)
        value += GT864_Q;
    return (int16_t)value;
}

static int16_t centered(int64_t value)
{
    int16_t result = canonical(value);
    if (result > GT864_Q / 2)
        result = (int16_t)(result - GT864_Q);
    return result;
}

static int16_t montgomery_reduce(int32_t value)
{
    int16_t quotient = (int16_t)value * GT864_QINV;
    return (int16_t)((value - (int32_t)quotient * GT864_Q) >> 16);
}

static int16_t fqmul_public(int16_t value, int16_t public_montgomery)
{
    return montgomery_reduce((int32_t)value * public_montgomery);
}

static int16_t fqmul_canonical(int16_t a, int16_t b)
{
    return canonical((int64_t)a * b);
}

static int16_t fqpow_canonical(int16_t base, int exponent)
{
    int16_t result = 1;
    while (exponent > 0) {
        if (exponent & 1)
            result = fqmul_canonical(result, base);
        base = fqmul_canonical(base, base);
        exponent >>= 1;
    }
    return result;
}

static int16_t fqinv_canonical(int16_t value)
{
    return fqpow_canonical(value, GT864_Q - 2);
}

static int16_t montgomery_encode(int16_t value)
{
    return centered((int64_t)canonical(value) * GT864_R);
}

static void centered_copy(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    for (size_t i = 0; i < GT864_N; i++)
        out[i] = centered(in[i]);
}

static void build_grid(int16_t lambda[GT864_COLUMNS],
                       int16_t z[GT864_COLUMNS],
                       int16_t roots[GT864_ROWS][GT864_COLUMNS])
{
    const int16_t primitive_864 = 2401;
    const int16_t eta = 1520;
    int column = 0;

    for (int exponent = 0; exponent < 96; exponent++) {
        if (exponent % 6 != 1 && exponent % 6 != 5)
            continue;
        lambda[column] = fqpow_canonical(primitive_864, exponent);
        z[column] = fqpow_canonical(lambda[column], GT864_ROWS);
        column++;
    }
    assert(column == GT864_COLUMNS);

    for (int row = 0; row < GT864_ROWS; row++) {
        int16_t eta_power = fqpow_canonical(eta, row);
        for (int col = 0; col < GT864_COLUMNS; col++)
            roots[row][col] = fqmul_canonical(lambda[col], eta_power);
    }
}

static void build_legacy_to_grid(int mapping[GT864_POINTS])
{
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];

    build_grid(lambda, z, roots);
    for (int pair = 0; pair < GT864_POINTS / 2; pair++) {
        for (int sign = 0; sign < 2; sign++) {
            int legacy = 2 * pair + sign;
            int16_t root_mont = sign == 0 ? zetas[GT864_POINTS / 2 + pair]
                                          : (int16_t)-zetas[GT864_POINTS / 2 + pair];
            int16_t root = canonical(montgomery_reduce(root_mont));
            mapping[legacy] = -1;
            for (int row = 0; row < GT864_ROWS; row++) {
                for (int col = 0; col < GT864_COLUMNS; col++) {
                    if (roots[row][col] == root)
                        mapping[legacy] = row * GT864_COLUMNS + col;
                }
            }
            assert(mapping[legacy] >= 0);
        }
    }
}

void gt864_grid_to_legacy(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int mapping[GT864_POINTS];

    for (int i = 0; i < GT864_N; i++)
        input[i] = in[i];
    build_legacy_to_grid(mapping);
    for (int legacy = 0; legacy < GT864_POINTS; legacy++) {
        for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++)
            out[legacy * GT864_LEAF_DEGREE + branch] =
                input[mapping[legacy] * GT864_LEAF_DEGREE + branch];
    }
}

void gt864_legacy_to_grid(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int mapping[GT864_POINTS];

    for (int i = 0; i < GT864_N; i++)
        input[i] = in[i];
    build_legacy_to_grid(mapping);
    for (int legacy = 0; legacy < GT864_POINTS; legacy++) {
        for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++)
            out[mapping[legacy] * GT864_LEAF_DEGREE + branch] =
                input[legacy * GT864_LEAF_DEGREE + branch];
    }
}

static void invert_vandermonde(
    int16_t inverse[GT864_COLUMNS][GT864_COLUMNS],
    const int16_t z[GT864_COLUMNS])
{
    int16_t matrix[GT864_COLUMNS][2 * GT864_COLUMNS];

    for (int row = 0; row < GT864_COLUMNS; row++) {
        int16_t power = 1;
        for (int col = 0; col < GT864_COLUMNS; col++) {
            matrix[row][col] = power;
            power = fqmul_canonical(power, z[row]);
            matrix[row][GT864_COLUMNS + col] = (int16_t)(row == col);
        }
    }

    for (int col = 0; col < GT864_COLUMNS; col++) {
        int pivot = col;
        while (pivot < GT864_COLUMNS && matrix[pivot][col] == 0)
            pivot++;
        assert(pivot < GT864_COLUMNS);
        if (pivot != col) {
            for (int j = 0; j < 2 * GT864_COLUMNS; j++) {
                int16_t temporary = matrix[col][j];
                matrix[col][j] = matrix[pivot][j];
                matrix[pivot][j] = temporary;
            }
        }

        int16_t pivot_inverse = fqinv_canonical(matrix[col][col]);
        for (int j = 0; j < 2 * GT864_COLUMNS; j++)
            matrix[col][j] = fqmul_canonical(matrix[col][j], pivot_inverse);

        for (int row = 0; row < GT864_COLUMNS; row++) {
            if (row == col)
                continue;
            int16_t factor = matrix[row][col];
            for (int j = 0; j < 2 * GT864_COLUMNS; j++)
                matrix[row][j] = canonical(
                    matrix[row][j] - (int64_t)factor * matrix[col][j]);
        }
    }

    for (int row = 0; row < GT864_COLUMNS; row++)
        for (int col = 0; col < GT864_COLUMNS; col++)
            inverse[row][col] = matrix[row][GT864_COLUMNS + col];
}

void gt864_mont_forward(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    centered_copy(input, in);
    build_grid(lambda, z, roots);
    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int16_t value = 0;
                int16_t z_mont = montgomery_encode(z[col]);
                for (int degree = GT864_COLUMNS - 1; degree >= 0; degree--)
                    value = centered(fqmul_public(value, z_mont) +
                                     input[GT864_LEAF_DEGREE *
                                           (residue + GT864_ROWS * degree) + branch]);
                stage32[branch][residue][col] = value;
            }
        }
    }

    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            int16_t root_mont = montgomery_encode(roots[row][col]);
            for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
                int16_t value = 0;
                for (int residue = GT864_ROWS - 1; residue >= 0; residue--)
                    value = centered(fqmul_public(value, root_mont) +
                                     stage32[branch][residue][col]);
                out[(row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE + branch] = value;
            }
        }
    }
}

void gt864_mont_inverse(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    const int16_t eta = 1520;
    const int16_t inverse_9 = fqinv_canonical(GT864_ROWS);
    int16_t input[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];
    int16_t inverse_v[GT864_COLUMNS][GT864_COLUMNS];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    centered_copy(input, in);
    build_grid(lambda, z, roots);
    invert_vandermonde(inverse_v, z);

    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int16_t sum = 0;
                for (int row = 0; row < GT864_ROWS; row++) {
                    int exponent = (GT864_ROWS -
                                    (row * residue) % GT864_ROWS) % GT864_ROWS;
                    int16_t factor_mont = montgomery_encode(
                        fqpow_canonical(eta, exponent));
                    sum = centered(sum + fqmul_public(
                        input[(row * GT864_COLUMNS + col) *
                              GT864_LEAF_DEGREE + branch], factor_mont));
                }
                int16_t scale = fqmul_canonical(
                    inverse_9,
                    fqpow_canonical(fqinv_canonical(lambda[col]), residue));
                stage32[branch][residue][col] =
                    centered(fqmul_public(sum, montgomery_encode(scale)));
            }
        }
    }

    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int degree = 0; degree < GT864_COLUMNS; degree++) {
                int16_t sum = 0;
                for (int col = 0; col < GT864_COLUMNS; col++)
                    sum = centered(sum + fqmul_public(
                        stage32[branch][residue][col],
                        montgomery_encode(inverse_v[degree][col])));
                out[GT864_LEAF_DEGREE *
                    (residue + GT864_ROWS * degree) + branch] = sum;
            }
        }
    }
}

void gt864_mont_basemul(int16_t out[GT864_N], const int16_t a[GT864_N],
                        const int16_t b[GT864_N])
{
    int16_t left[GT864_N];
    int16_t right[GT864_N];
    int16_t result[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];

    centered_copy(left, a);
    centered_copy(right, b);
    build_grid(lambda, z, roots);

    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            int offset = (row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE;
            int16_t root_mont = montgomery_encode(roots[row][col]);
            int16_t a0 = left[offset + 0];
            int16_t a1 = left[offset + 1];
            int16_t a2 = left[offset + 2];
            int16_t b0 = right[offset + 0];
            int16_t b1 = right[offset + 1];
            int16_t b2 = right[offset + 2];
            int16_t r0 = montgomery_reduce((int32_t)a2 * b1 + (int32_t)a1 * b2);
            int16_t r1 = montgomery_reduce((int32_t)a2 * b2);

            r0 = montgomery_reduce((int32_t)r0 * root_mont + (int32_t)a0 * b0);
            r1 = montgomery_reduce((int32_t)r1 * root_mont +
                                   (int32_t)a0 * b1 + (int32_t)a1 * b0);
            int16_t r2 = montgomery_reduce((int32_t)a2 * b0 +
                                           (int32_t)a1 * b1 +
                                           (int32_t)a0 * b2);
            result[offset + 0] = montgomery_reduce((int32_t)r0 * GT864_RSQ);
            result[offset + 1] = montgomery_reduce((int32_t)r1 * GT864_RSQ);
            result[offset + 2] = montgomery_reduce((int32_t)r2 * GT864_RSQ);
        }
    }
    for (int i = 0; i < GT864_N; i++)
        out[i] = result[i];
}

void gt864_mont_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                    const int16_t b[GT864_N])
{
    int16_t forward_a[GT864_N];
    int16_t forward_b[GT864_N];
    int16_t product[GT864_N];

    gt864_mont_forward(forward_a, a);
    gt864_mont_forward(forward_b, b);
    gt864_mont_basemul(product, forward_a, forward_b);
    gt864_mont_inverse(out, product);
}
