#include "gt864_reference.h"

#include <stddef.h>
#include <stdint.h>

#define GT864_POINTS (GT864_N / GT864_LEAF_DEGREE)

static int16_t canonical(int64_t value)
{
    value %= GT864_Q;
    if (value < 0)
        value += GT864_Q;
    return (int16_t)value;
}

static int16_t fqmul(int16_t a, int16_t b)
{
    return canonical((int64_t)a * b);
}

static int16_t fqpow(int16_t base, int exponent)
{
    int16_t result = 1;

    while (exponent > 0) {
        if (exponent & 1)
            result = fqmul(result, base);
        base = fqmul(base, base);
        exponent >>= 1;
    }
    return result;
}

static int16_t fqinv(int16_t value)
{
    return fqpow(value, GT864_Q - 2);
}

static void canonical_copy(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    for (size_t i = 0; i < GT864_N; i++)
        out[i] = canonical(in[i]);
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
        lambda[column] = fqpow(primitive_864, exponent);
        z[column] = fqpow(lambda[column], GT864_ROWS);
        column++;
    }

    for (int row = 0; row < GT864_ROWS; row++) {
        int16_t eta_power = fqpow(eta, row);
        for (int col = 0; col < GT864_COLUMNS; col++)
            roots[row][col] = fqmul(lambda[col], eta_power);
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
            power = fqmul(power, z[row]);
            matrix[row][GT864_COLUMNS + col] = (int16_t)(row == col);
        }
    }

    for (int col = 0; col < GT864_COLUMNS; col++) {
        int pivot = col;
        while (pivot < GT864_COLUMNS && matrix[pivot][col] == 0)
            pivot++;
        if (pivot != col) {
            for (int j = 0; j < 2 * GT864_COLUMNS; j++) {
                int16_t temporary = matrix[col][j];
                matrix[col][j] = matrix[pivot][j];
                matrix[pivot][j] = temporary;
            }
        }

        int16_t pivot_inverse = fqinv(matrix[col][col]);
        for (int j = 0; j < 2 * GT864_COLUMNS; j++)
            matrix[col][j] = fqmul(matrix[col][j], pivot_inverse);

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

void gt864_forward_direct(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];

    canonical_copy(input, in);
    build_grid(lambda, z, roots);

    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
                int16_t value = 0;
                for (int degree = GT864_POINTS - 1; degree >= 0; degree--)
                    value = canonical((int64_t)value * roots[row][col] +
                                      input[GT864_LEAF_DEGREE * degree + branch]);
                out[(row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE + branch] = value;
            }
        }
    }
}

void gt864_forward(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    int16_t input[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    canonical_copy(input, in);
    build_grid(lambda, z, roots);

    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int16_t value = 0;
                for (int degree = GT864_COLUMNS - 1; degree >= 0; degree--)
                    value = canonical((int64_t)value * z[col] +
                                      input[GT864_LEAF_DEGREE *
                                            (residue + GT864_ROWS * degree) + branch]);
                stage32[branch][residue][col] = value;
            }
        }
    }

    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
                int16_t value = 0;
                for (int residue = GT864_ROWS - 1; residue >= 0; residue--)
                    value = canonical((int64_t)value * roots[row][col] +
                                      stage32[branch][residue][col]);
                out[(row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE + branch] = value;
            }
        }
    }
}

void gt864_inverse(int16_t out[GT864_N], const int16_t in[GT864_N])
{
    const int16_t eta = 1520;
    const int16_t inverse_9 = fqinv(GT864_ROWS);
    int16_t input[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];
    int16_t inverse_v[GT864_COLUMNS][GT864_COLUMNS];
    int16_t stage32[GT864_LEAF_DEGREE][GT864_ROWS][GT864_COLUMNS];

    canonical_copy(input, in);
    build_grid(lambda, z, roots);
    invert_vandermonde(inverse_v, z);

    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int col = 0; col < GT864_COLUMNS; col++) {
                int64_t sum = 0;
                for (int row = 0; row < GT864_ROWS; row++) {
                    int exponent = (GT864_ROWS -
                                    (row * residue) % GT864_ROWS) % GT864_ROWS;
                    sum += (int64_t)fqpow(eta, exponent) *
                           input[(row * GT864_COLUMNS + col) *
                                 GT864_LEAF_DEGREE + branch];
                }
                int16_t scale = fqmul(inverse_9,
                                      fqpow(fqinv(lambda[col]), residue));
                stage32[branch][residue][col] = fqmul(canonical(sum), scale);
            }
        }
    }

    for (int branch = 0; branch < GT864_LEAF_DEGREE; branch++) {
        for (int residue = 0; residue < GT864_ROWS; residue++) {
            for (int degree = 0; degree < GT864_COLUMNS; degree++) {
                int64_t sum = 0;
                for (int col = 0; col < GT864_COLUMNS; col++)
                    sum += (int64_t)inverse_v[degree][col] *
                           stage32[branch][residue][col];
                out[GT864_LEAF_DEGREE *
                    (residue + GT864_ROWS * degree) + branch] = canonical(sum);
            }
        }
    }
}

void gt864_basemul(int16_t out[GT864_N], const int16_t a[GT864_N],
                   const int16_t b[GT864_N])
{
    int16_t left[GT864_N];
    int16_t right[GT864_N];
    int16_t result[GT864_N];
    int16_t lambda[GT864_COLUMNS];
    int16_t z[GT864_COLUMNS];
    int16_t roots[GT864_ROWS][GT864_COLUMNS];

    canonical_copy(left, a);
    canonical_copy(right, b);
    build_grid(lambda, z, roots);

    for (int row = 0; row < GT864_ROWS; row++) {
        for (int col = 0; col < GT864_COLUMNS; col++) {
            int offset = (row * GT864_COLUMNS + col) * GT864_LEAF_DEGREE;
            int16_t root = roots[row][col];
            int16_t a0 = left[offset + 0];
            int16_t a1 = left[offset + 1];
            int16_t a2 = left[offset + 2];
            int16_t b0 = right[offset + 0];
            int16_t b1 = right[offset + 1];
            int16_t b2 = right[offset + 2];

            result[offset + 0] = canonical(
                (int64_t)a0 * b0 + (int64_t)root * (a1 * b2 + a2 * b1));
            result[offset + 1] = canonical(
                (int64_t)a0 * b1 + (int64_t)a1 * b0 +
                (int64_t)root * a2 * b2);
            result[offset + 2] = canonical(
                (int64_t)a0 * b2 + (int64_t)a1 * b1 + (int64_t)a2 * b0);
        }
    }
    canonical_copy(out, result);
}

void gt864_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
               const int16_t b[GT864_N])
{
    int16_t forward_a[GT864_N];
    int16_t forward_b[GT864_N];
    int16_t product[GT864_N];

    gt864_forward(forward_a, a);
    gt864_forward(forward_b, b);
    gt864_basemul(product, forward_a, forward_b);
    gt864_inverse(out, product);
}

void gt864_schoolbook_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                          const int16_t b[GT864_N])
{
    int16_t left[GT864_N];
    int16_t right[GT864_N];
    int64_t accum[GT864_N] = {0};

    canonical_copy(left, a);
    canonical_copy(right, b);

    for (int i = 0; i < GT864_N; i++) {
        for (int j = 0; j < GT864_N; j++) {
            int degree = i + j;
            int64_t product = (int64_t)left[i] * right[j];
            if (degree < GT864_N) {
                accum[degree] += product;
            } else if (degree < 3 * GT864_N / 2) {
                accum[degree - GT864_N / 2] += product;
                accum[degree - GT864_N] -= product;
            } else {
                accum[degree - 3 * GT864_N / 2] -= product;
            }
        }
    }

    for (int i = 0; i < GT864_N; i++)
        out[i] = canonical(accum[i]);
}
