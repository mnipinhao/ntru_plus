#include "gt864_friso2.h"
#include "gt864_fr0_inverse.h"
#include "gt864_top_split.h"
#include "gt864_ntt16.h"
#include "gt864_boundary.h"
#include "gt864_fr0_basemul.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define COEFFICIENTS 864
#define P8_PADDED 896

static uint32_t random_state = 0x5U;
static int basis_roundtrip_mismatches;
static int basemul_mismatches;
static int basemul_add_mismatches;
static int alias_mismatches;
static int full_product_mismatches;
static int basis_cases;
static int basemul_cases;
static int product_cases;

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

static int16_t random_centered(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((int32_t)(random_state % Q) - Q / 2);
}

static int16_t random_small(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % 5U) - 2);
}

static void compare_modq(const int16_t a[COEFFICIENTS],
                         const int16_t b[COEFFICIENTS], int *mismatches,
                         const char *label)
{
    for (int i = 0; i < COEFFICIENTS; i++) {
        if (canonical(a[i]) != canonical(b[i])) {
            if (*mismatches < 8)
                fprintf(stderr, "%s mismatch i=%d got=%d expected=%d\n",
                        label, i, a[i], b[i]);
            (*mismatches)++;
        }
    }
}

static void forward_fr0(int16_t out[COEFFICIENTS],
                        const int16_t in[COEFFICIENTS])
{
    int16_t p8[P8_PADDED];
    gt864_top_split_ld3(p8, in);
    gt864_ntt16_p8_neon(p8);
    gt864_boundary_fr0(out, p8);
}

static void inverse_fr0(int16_t out[COEFFICIENTS],
                        const int16_t in[COEFFICIENTS])
{
    int16_t p8[P8_PADDED];
    gt864_fr0_inverse_ntt9_neon(p8, in);
    gt864_fr0_inverse_finish_neon(out, p8);
}

static void schoolbook(int16_t out[COEFFICIENTS],
                       const int16_t a[COEFFICIENTS],
                       const int16_t b[COEFFICIENTS])
{
    int64_t product[2 * COEFFICIENTS - 1] = {0};
    for (int i = 0; i < COEFFICIENTS; i++)
        for (int j = 0; j < COEFFICIENTS; j++)
            product[i + j] += (int32_t)a[i] * b[j];
    for (int degree = 2 * COEFFICIENTS - 2;
         degree >= COEFFICIENTS; degree--) {
        int64_t value = product[degree] % Q;
        product[degree - 432] += value;
        product[degree - 864] -= value;
    }
    for (int i = 0; i < COEFFICIENTS; i++)
        out[i] = centered(product[i]);
}

static void check_basis_roundtrip(const int16_t input[COEFFICIENTS],
                                  const char *label)
{
    int16_t normalized[COEFFICIENTS];
    int16_t restored[COEFFICIENTS];
    gt864_friso2_normalize(normalized, input);
    gt864_friso2_denormalize(restored, normalized);
    compare_modq(restored, input, &basis_roundtrip_mismatches, label);
    basis_cases++;
}

static void check_basemul_case(const int16_t a[COEFFICIENTS],
                               const int16_t b[COEFFICIENTS],
                               const int16_t c[COEFFICIENTS],
                               const char *label)
{
    int16_t na[COEFFICIENTS];
    int16_t nb[COEFFICIENTS];
    int16_t nc[COEFFICIENTS];
    int16_t got[COEFFICIENTS];
    int16_t got_add[COEFFICIENTS];
    int16_t ordinary[COEFFICIENTS];
    int16_t ordinary_add[COEFFICIENTS];
    int16_t expected[COEFFICIENTS];
    int16_t expected_add[COEFFICIENTS];
    int16_t alias[COEFFICIENTS];

    gt864_friso2_normalize(na, a);
    gt864_friso2_normalize(nb, b);
    gt864_friso2_normalize(nc, c);
    gt864_friso2_basemul(got, na, nb);
    gt864_friso2_basemul_add(got_add, na, nb, nc);

    gt864_fr0_basemul_neon(ordinary, a, b);
    gt864_fr0_basemul_add_neon(ordinary_add, a, b, c);
    gt864_friso2_normalize(expected, ordinary);
    gt864_friso2_normalize(expected_add, ordinary_add);
    compare_modq(got, expected, &basemul_mismatches, label);
    compare_modq(got_add, expected_add, &basemul_add_mismatches, label);

    memcpy(alias, na, sizeof(alias));
    gt864_friso2_basemul(alias, alias, nb);
    compare_modq(alias, got, &alias_mismatches, "basemul-alias-a");
    memcpy(alias, nb, sizeof(alias));
    gt864_friso2_basemul(alias, na, alias);
    compare_modq(alias, got, &alias_mismatches, "basemul-alias-b");
    memcpy(alias, nc, sizeof(alias));
    gt864_friso2_basemul_add(alias, na, nb, alias);
    compare_modq(alias, got_add, &alias_mismatches, "basemul-add-alias-c");
    basemul_cases++;
}

static void check_full_product(const int16_t a[COEFFICIENTS],
                               const int16_t b[COEFFICIENTS],
                               const char *label)
{
    int16_t fa[COEFFICIENTS];
    int16_t fb[COEFFICIENTS];
    int16_t na[COEFFICIENTS];
    int16_t nb[COEFFICIENTS];
    int16_t np[COEFFICIENTS];
    int16_t fp[COEFFICIENTS];
    int16_t got[COEFFICIENTS];
    int16_t expected[COEFFICIENTS];

    forward_fr0(fa, a);
    forward_fr0(fb, b);
    gt864_friso2_normalize(na, fa);
    gt864_friso2_normalize(nb, fb);
    gt864_friso2_basemul(np, na, nb);
    gt864_friso2_denormalize(fp, np);
    inverse_fr0(got, fp);
    schoolbook(expected, a, b);
    compare_modq(got, expected, &full_product_mismatches, label);
    product_cases++;
}

int main(void)
{
    int16_t a[COEFFICIENTS];
    int16_t b[COEFFICIENTS];
    int16_t c[COEFFICIENTS];
    static const int16_t boundaries[] = {-1728, -1, 0, 1, 1728};
    static const int positions[] = {0,1,2,23,24,431,432,433,861,862,863};

    for (size_t k = 0; k < sizeof(boundaries) / sizeof(boundaries[0]); k++) {
        for (int i = 0; i < COEFFICIENTS; i++)
            a[i] = boundaries[k];
        check_basis_roundtrip(a, "basis-boundary");
    }
    for (size_t k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(a, 0, sizeof(a));
        a[positions[k]] = (int16_t)(k & 1 ? -1728 : 1728);
        check_basis_roundtrip(a, "basis-impulse");
    }
    for (int trial = 0; trial < 32; trial++) {
        for (int i = 0; i < COEFFICIENTS; i++)
            a[i] = random_centered();
        check_basis_roundtrip(a, "basis-random");
    }

    for (int trial = 0; trial < 32; trial++) {
        for (int i = 0; i < COEFFICIENTS; i++) {
            a[i] = random_centered();
            b[i] = random_centered();
            c[i] = random_centered();
        }
        check_basemul_case(a, b, c, "basemul-random");
    }

    for (size_t k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(a, 0, sizeof(a));
        memset(b, 0, sizeof(b));
        a[positions[k]] = 1;
        b[positions[(k + 3) %
                    (sizeof(positions) / sizeof(positions[0]))]] = -1;
        check_full_product(a, b, "product-impulse");
    }
    for (int trial = 0; trial < 8; trial++) {
        for (int i = 0; i < COEFFICIENTS; i++) {
            a[i] = random_small();
            b[i] = random_small();
        }
        check_full_product(a, b, "product-random-small");
    }

    printf("gt864_friso2_c_reference_gate=%s\n",
           basis_roundtrip_mismatches + basemul_mismatches +
           basemul_add_mismatches + alias_mismatches +
           full_product_mismatches == 0
               ? "pass" : "fail");
    printf("basis_cases=%d\n", basis_cases);
    printf("basis_roundtrip_modq_mismatches=%d\n",
           basis_roundtrip_mismatches);
    printf("basemul_cases=%d\n", basemul_cases);
    printf("basemul_modq_mismatches=%d\n", basemul_mismatches);
    printf("basemul_add_modq_mismatches=%d\n", basemul_add_mismatches);
    printf("alias_modq_mismatches=%d\n", alias_mismatches);
    printf("full_product_cases=%d\n", product_cases);
    printf("full_product_modq_mismatches=%d\n", full_product_mismatches);
    printf("coefficient_memory_expansion=0\n");
    printf("reference_conversion_passes=2\n");
    printf("production_linked=0\n");
    return basis_roundtrip_mismatches + basemul_mismatches +
           basemul_add_mismatches + alias_mismatches +
           full_product_mismatches != 0;
}
