#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define THETA 9
#define TOPS 2
#define COLUMNS 16
#define ROWS 9
#define COMPONENTS 3
#define COEFFICIENTS (TOPS * COLUMNS * ROWS * COMPONENTS)

typedef int16_t leaf[ROWS][COMPONENTS];
typedef leaf domain[TOPS][COLUMNS];

static int modq(int64_t value)
{
    value %= Q;
    if (value < 0) value += Q;
    return (int)value;
}

static int power(int base, int exponent)
{
    int result = 1;
    if (exponent < 0) {
        base = power(base, Q - 2);
        exponent = -exponent;
    }
    while (exponent) {
        if (exponent & 1) result = modq((int64_t)result * base);
        base = modq((int64_t)base * base);
        exponent >>= 1;
    }
    return result;
}

static int lambda_at(int top, int column)
{
    const int residue[2] = {1, 5};
    return power(THETA, residue[top] + 6 * column);
}

static int eta(void) { return power(THETA, 96); }

static void forward_leaf(leaf out, const leaf in, int lambda, int rotation)
{
    int root9 = eta();
    for (int physical = 0; physical < ROWS; physical++) {
        int logical = (physical + rotation) % ROWS;
        int root = modq((int64_t)lambda * power(root9, logical));
        for (int c = 0; c < COMPONENTS; c++) {
            int64_t sum = 0;
            for (int s = 0; s < ROWS; s++)
                sum += (int64_t)in[s][c] * power(root, s);
            out[physical][c] = (int16_t)modq(sum);
        }
    }
}

static void cubic_product(int16_t out[3], const int16_t a[3],
                          const int16_t b[3], int zeta)
{
    int64_t raw[5] = {0};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            raw[i + j] += (int64_t)a[i] * b[j];
    out[0] = (int16_t)modq(raw[0] + zeta * raw[3]);
    out[1] = (int16_t)modq(raw[1] + zeta * raw[4]);
    out[2] = (int16_t)modq(raw[2]);
}

static void basemul_leaf(leaf out, const leaf a, const leaf b,
                         int lambda, int rotation)
{
    int root9 = eta();
    for (int physical = 0; physical < ROWS; physical++) {
        int logical = (physical + rotation) % ROWS;
        int zeta = modq((int64_t)lambda * power(root9, logical));
        cubic_product(out[physical], a[physical], b[physical], zeta);
    }
}

static void inverse_leaf(leaf out, const leaf in, int lambda, int rotation)
{
    int root9 = eta();
    int inv9 = power(9, -1);
    for (int s = 0; s < ROWS; s++) {
        for (int c = 0; c < COMPONENTS; c++) {
            int64_t sum = 0;
            for (int physical = 0; physical < ROWS; physical++) {
                int logical = (physical + rotation) % ROWS;
                sum += (int64_t)in[physical][c] * power(root9, -logical * s);
            }
            out[s][c] = (int16_t)modq(sum * inv9 * power(lambda, -s));
        }
    }
}

static void multiply(domain out, const domain a, const domain b, int rotation)
{
    for (int top = 0; top < TOPS; top++) {
        for (int column = 0; column < COLUMNS; column++) {
            leaf fa, fb, product;
            int lambda = lambda_at(top, column);
            forward_leaf(fa, a[top][column], lambda, rotation);
            forward_leaf(fb, b[top][column], lambda, rotation);
            basemul_leaf(product, fa, fb, lambda, rotation);
            inverse_leaf(out[top][column], product, lambda, rotation);
        }
    }
}

static uint32_t random_state = 1;
static int sample(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int)(random_state % Q);
}

int main(void)
{
    static domain a, b, baseline, candidate;
    int comparisons = 0;
    for (int trial = 0; trial < 96; trial++) {
        int16_t *ap = &a[0][0][0][0];
        int16_t *bp = &b[0][0][0][0];
        for (int i = 0; i < COEFFICIENTS; i++) {
            if (trial == 0) { ap[i] = 0; bp[i] = 0; }
            else if (trial == 1) { ap[i] = Q - 1; bp[i] = Q - 1; }
            else if (trial == 2) { ap[i] = (i & 1) ? 1 : Q - 1; bp[i] = (i % 3) ? Q - 1 : 1; }
            else { ap[i] = (int16_t)sample(); bp[i] = (int16_t)sample(); }
        }
        multiply(baseline, a, b, 0);
        for (int rotation = 0; rotation < ROWS; rotation++) {
            multiply(candidate, a, b, rotation);
            assert(memcmp(baseline, candidate, sizeof(baseline)) == 0);
            comparisons += COEFFICIENTS;
        }
    }
    printf("delayed_twist_c_reference=pass\n");
    printf("coefficient_shape=%d\n", COEFFICIENTS);
    printf("trials=96\nrotations_per_trial=9\n");
    printf("coefficient_comparisons=%d\n", comparisons);
    printf("validated_pending_state=row_rotation_only\n");
    return 0;
}
