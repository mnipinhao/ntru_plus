#include "gt864_fr0_inverse.h"
#include "gt864_fr0_inverse_tables.h"
#include "../gt_2x9x16_ld3_top_split/gt864_top_split.h"
#include "../gt_boundary_cost_campaign/gt864_boundary.h"
#include "../gt_ntt16_producer_range/gt864_ntt16.h"
#include "../gt_fr0_basemul_arithmetic/gt864_fr0_basemul.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define THETA 9

void invntt(int16_t out[864], const int16_t in[864]);

static uint32_t random_state = 0x5dU;
static int inverse9_mismatches;
static int official_inverse_mismatches;
static int roundtrip_mismatches;
static int product_mismatches;
static int padding_mismatches;
static int inverse_cases;
static int product_cases;
static int maximum_output_abs;

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

static size_t p8_index(int top, int component, int column, int s)
{
    if (s < 8)
        return (size_t)(((top * 3 + component) * 16 + column) * 8 + s);
    return (size_t)(GT864_INVERSE_P8_MAIN + 8 * column +
                    3 * top + component);
}

static void forward_fr0(int16_t out[864], const int16_t in[864])
{
    int16_t p8[GT864_INVERSE_P8_PADDED];
    gt864_top_split_ld3(p8, in);
    gt864_ntt16_p8_neon(p8);
    gt864_boundary_fr0(out, p8);
}

static void check_inverse9_direct(const int16_t fr0[864],
                                  const int16_t p8[896], const char *label)
{
    int16_t eta = powmod(THETA, 96);
    for (int top = 0; top < 2; top++) {
        int residue = top == 0 ? 1 : 5;
        for (int component = 0; component < 3; component++) {
            for (int column = 0; column < 16; column++) {
                int16_t lambda = powmod(THETA, residue + 6 * column);
                for (int s = 0; s < 9; s++) {
                    int64_t sum = 0;
                    for (int row = 0; row < 9; row++)
                        sum += (int32_t)fr0[fr_index(
                            top, row, column, component)] *
                            powmod(eta, -(row * s) % 9);
                    sum = (int32_t)canonical(sum) * powmod(9, -1);
                    sum = (int32_t)canonical(sum) * powmod(lambda, -s);
                    if (canonical(p8[p8_index(top, component, column, s)]) !=
                        canonical(sum)) {
                        if (inverse9_mismatches < 8)
                            fprintf(stderr,
                                "%s inverse9 mismatch h=%d b=%d c=%d s=%d "
                                "got=%d expected=%d\n", label, top, component,
                                column, s,
                                p8[p8_index(top, component, column, s)],
                                centered(sum));
                        inverse9_mismatches++;
                    }
                }
            }
        }
    }
}

static void check_fr0_case(const int16_t fr0[864], const char *label)
{
    int16_t legacy[864];
    int16_t p8[896];
    int16_t got[864];
    int16_t official[864];

    gt864_fr0_inverse_ntt9_neon(p8, fr0);
    check_inverse9_direct(fr0, p8, label);
    gt864_fr0_inverse_finish_neon(got, p8);

    for (int physical = 0; physical < 288; physical++) {
        int legacy_leaf = gt864_inverse_physical_to_legacy[physical];
        int group = physical / 8;
        int lane = physical % 8;
        for (int component = 0; component < 3; component++)
            legacy[3 * legacy_leaf + component] =
                fr0[24 * group + 8 * component + lane];
    }
    invntt(official, legacy);

    for (int i = 0; i < 864; i++) {
        int magnitude = got[i] < 0 ? -got[i] : got[i];
        if (magnitude > maximum_output_abs)
            maximum_output_abs = magnitude;
        if (canonical(got[i]) != canonical(official[i])) {
            if (official_inverse_mismatches < 8)
                fprintf(stderr, "%s official mismatch i=%d got=%d ref=%d\n",
                        label, i, got[i], official[i]);
            official_inverse_mismatches++;
        }
    }

    /* Padding lanes are outside the 864-value contract and must not affect it. */
    {
        int16_t altered[896];
        int16_t second[864];
        memcpy(altered, p8, sizeof(altered));
        for (int column = 0; column < 16; column++) {
            altered[GT864_INVERSE_P8_MAIN + 8 * column + 6] =
                (int16_t)(1234 + column);
            altered[GT864_INVERSE_P8_MAIN + 8 * column + 7] =
                (int16_t)(-1234 - column);
        }
        gt864_fr0_inverse_finish_neon(second, altered);
        for (int i = 0; i < 864; i++)
            if (second[i] != got[i])
                padding_mismatches++;
    }
    inverse_cases++;
}

static void check_roundtrip_case(const int16_t input[864], const char *label)
{
    int16_t fr0[864];
    int16_t p8[896];
    int16_t got[864];

    forward_fr0(fr0, input);
    /* This is an algebra roundtrip, normalized into M5C's inverse-input bound.
     * The real pipeline reaches the same boundary through BaseMul/BaseMulAdd. */
    for (int i = 0; i < 864; i++)
        fr0[i] = centered(fr0[i]);
    gt864_fr0_inverse_ntt9_neon(p8, fr0);
    gt864_fr0_inverse_finish_neon(got, p8);
    for (int i = 0; i < 864; i++) {
        if (canonical(got[i]) != canonical(input[i])) {
            if (roundtrip_mismatches < 8)
                fprintf(stderr, "%s roundtrip mismatch i=%d got=%d in=%d\n",
                        label, i, got[i], input[i]);
            roundtrip_mismatches++;
        }
    }
}

static void schoolbook(int16_t out[864], const int16_t a[864],
                       const int16_t b[864])
{
    int64_t product[1727] = {0};
    for (int i = 0; i < 864; i++)
        for (int j = 0; j < 864; j++)
            product[i + j] += (int32_t)a[i] * b[j];
    for (int degree = 1726; degree >= 864; degree--) {
        int64_t value = product[degree] % Q;
        product[degree - 432] += value;
        product[degree - 864] -= value;
    }
    for (int i = 0; i < 864; i++)
        out[i] = centered(product[i]);
}

static void check_product_case(const int16_t a[864], const int16_t b[864],
                               const char *label)
{
    int16_t fa[864];
    int16_t fb[864];
    int16_t fp[864];
    int16_t p8[896];
    int16_t got[864];
    int16_t expected[864];

    forward_fr0(fa, a);
    forward_fr0(fb, b);
    gt864_fr0_basemul_neon(fp, fa, fb);
    gt864_fr0_inverse_ntt9_neon(p8, fp);
    gt864_fr0_inverse_finish_neon(got, p8);
    schoolbook(expected, a, b);
    for (int i = 0; i < 864; i++) {
        if (canonical(got[i]) != canonical(expected[i])) {
            if (product_mismatches < 8)
                fprintf(stderr, "%s product mismatch i=%d got=%d ref=%d\n",
                        label, i, got[i], expected[i]);
            product_mismatches++;
        }
    }
    product_cases++;
}

static int16_t random_small(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % 5U) - 2);
}

int main(void)
{
    int16_t fr0[864];
    int16_t input[864];
    int16_t a[864];
    int16_t b[864];
    static const int16_t boundaries[] = {-2168, 2168, -1, 0, 1};
    static const int positions[] = {0,1,2,3,26,27,431,432,433,861,862,863};

    for (size_t k = 0; k < sizeof(boundaries) / sizeof(boundaries[0]); k++) {
        for (int i = 0; i < 864; i++)
            fr0[i] = boundaries[k];
        check_fr0_case(fr0, "fr0-boundary");
    }
    for (size_t k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(fr0, 0, sizeof(fr0));
        fr0[positions[k]] = (int16_t)(k & 1 ? -2168 : 2168);
        check_fr0_case(fr0, "fr0-impulse");
    }
    for (int trial = 0; trial < 32; trial++) {
        for (int i = 0; i < 864; i++)
            fr0[i] = (int16_t)((int32_t)((random_state =
                random_state * 1664525u + 1013904223u) % 4337U) - 2168);
        check_fr0_case(fr0, "fr0-random");
    }

    for (size_t k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(input, 0, sizeof(input));
        input[positions[k]] = (int16_t)(k & 1 ? -1 : 1);
        check_roundtrip_case(input, "roundtrip-impulse");
    }
    for (int trial = 0; trial < 16; trial++) {
        for (int i = 0; i < 864; i++)
            input[i] = random_small();
        check_roundtrip_case(input, "roundtrip-random-small");
    }

    for (int trial = 0; trial < 8; trial++) {
        for (int i = 0; i < 864; i++) {
            a[i] = random_small();
            b[i] = random_small();
        }
        check_product_case(a, b, "product");
    }

    printf("gt864_fr0_inverse_consumer_gate=%s\n",
           inverse9_mismatches + official_inverse_mismatches +
           roundtrip_mismatches + product_mismatches + padding_mismatches == 0
               ? "pass" : "fail");
    printf("inverse_cases=%d\n", inverse_cases);
    printf("inverse9_direct_mismatches=%d\n", inverse9_mismatches);
    printf("official_inverse_modq_mismatches=%d\n",
           official_inverse_mismatches);
    printf("roundtrip_modq_mismatches=%d\n", roundtrip_mismatches);
    printf("full_product_mismatches=%d\n", product_mismatches);
    printf("product_cases=%d\n", product_cases);
    printf("padding_dependency_mismatches=%d\n", padding_mismatches);
    printf("maximum_observed_output_abs=%d\n", maximum_output_abs);
    printf("algorithmic_load_passes=2\n");
    printf("algorithmic_store_passes=2\n");
    printf("production_linked=0\n");
    return inverse9_mismatches + official_inverse_mismatches +
           roundtrip_mismatches + product_mismatches + padding_mismatches != 0;
}
