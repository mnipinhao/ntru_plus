#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_tables.h"

#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457
#define NEG_QINV (-12929)
#define R (-147)
#define RSQ 867
#define BOUND 25569

static uint32_t random_state = 0xb453U;
static int cases;
static int exact_basemul_mismatches;
static int exact_add_mismatches;
static int canonical_mismatches;
static int alias_mismatches;

static int16_t centered(int64_t value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    if (value > Q / 2)
        value -= Q;
    return (int16_t)value;
}

static int16_t montgomery_reduce(int64_t wide)
{
    int32_t value;
    int16_t quotient;

    if (wide < INT32_MIN || wide > INT32_MAX) {
        fprintf(stderr, "scalar accumulator overflow: %lld\n",
                (long long)wide);
        return 0;
    }
    value = (int32_t)wide;
    quotient = (int16_t)value * NEG_QINV;
    return (int16_t)((value + (int32_t)quotient * Q) >> 16);
}

static void scalar_cubic(int16_t out[3], const int16_t a[3],
                         const int16_t b[3], int16_t zeta,
                         const int16_t *addend)
{
    int16_t r0 = montgomery_reduce((int64_t)a[2] * b[1] +
                                   (int64_t)a[1] * b[2]);
    int16_t r1 = montgomery_reduce((int64_t)a[2] * b[2]);
    int16_t r2;

    r0 = montgomery_reduce((int64_t)r0 * zeta + (int64_t)a[0] * b[0]);
    r1 = montgomery_reduce((int64_t)r1 * zeta +
                           (int64_t)a[0] * b[1] +
                           (int64_t)a[1] * b[0]);
    r2 = montgomery_reduce((int64_t)a[2] * b[0] +
                           (int64_t)a[1] * b[1] +
                           (int64_t)a[0] * b[2]);
    if (addend == NULL) {
        out[0] = montgomery_reduce((int64_t)r0 * RSQ);
        out[1] = montgomery_reduce((int64_t)r1 * RSQ);
        out[2] = montgomery_reduce((int64_t)r2 * RSQ);
    } else {
        out[0] = montgomery_reduce((int64_t)addend[0] * R +
                                   (int64_t)r0 * RSQ);
        out[1] = montgomery_reduce((int64_t)addend[1] * R +
                                   (int64_t)r1 * RSQ);
        out[2] = montgomery_reduce((int64_t)addend[2] * R +
                                   (int64_t)r2 * RSQ);
    }
}

static size_t physical_index(int leaf, int component)
{
    return (size_t)(24 * (leaf / 8) + 8 * component + leaf % 8);
}

static void fr0_to_legacy(int16_t legacy[864], const int16_t fr0[864])
{
    for (int physical = 0; physical < 288; physical++) {
        int legacy_leaf = gt864_fr0_physical_to_legacy[physical];
        for (int component = 0; component < 3; component++)
            legacy[3 * legacy_leaf + component] =
                fr0[physical_index(physical, component)];
    }
}

static void legacy_to_fr0(int16_t fr0[864], const int16_t legacy[864])
{
    for (int physical = 0; physical < 288; physical++) {
        int legacy_leaf = gt864_fr0_physical_to_legacy[physical];
        for (int component = 0; component < 3; component++)
            fr0[physical_index(physical, component)] =
                legacy[3 * legacy_leaf + component];
    }
}

static void scalar_legacy_product(int16_t out[864], const int16_t a[864],
                                  const int16_t b[864], const int16_t *c)
{
    for (int leaf = 0; leaf < 288; leaf++)
        scalar_cubic(out + 3 * leaf, a + 3 * leaf, b + 3 * leaf,
                     gt864_legacy_zetas_mul[leaf],
                     c == NULL ? NULL : c + 3 * leaf);
}

static void check_canonical_leaf(const int16_t got[864], const int16_t a[864],
                                 const int16_t b[864], const int16_t *c,
                                 const char *label)
{
    const int rinv = 2775; /* R^-1 mod 3457. */

    for (int leaf = 0; leaf < 288; leaf++) {
        int group = leaf / 8;
        int lane = leaf % 8;
        int16_t zeta = centered((int32_t)gt864_fr0_zetas_mul[group][lane] *
                                rinv);
        int16_t av[3];
        int16_t bv[3];
        int16_t cv[3] = {0, 0, 0};
        int16_t expected[3];

        for (int component = 0; component < 3; component++) {
            av[component] = a[physical_index(leaf, component)];
            bv[component] = b[physical_index(leaf, component)];
            if (c != NULL)
                cv[component] = c[physical_index(leaf, component)];
        }
        expected[0] = centered((int64_t)av[0] * bv[0] +
                               (int64_t)zeta *
                               ((int64_t)av[1] * bv[2] +
                                (int64_t)av[2] * bv[1]) + cv[0]);
        expected[1] = centered((int64_t)av[0] * bv[1] +
                               (int64_t)av[1] * bv[0] +
                               (int64_t)zeta * av[2] * bv[2] + cv[1]);
        expected[2] = centered((int64_t)av[0] * bv[2] +
                               (int64_t)av[1] * bv[1] +
                               (int64_t)av[2] * bv[0] + cv[2]);
        for (int component = 0; component < 3; component++) {
            int16_t actual = centered(got[physical_index(leaf, component)]);
            if (actual != expected[component]) {
                if (canonical_mismatches < 8)
                    fprintf(stderr,
                            "%s canonical mismatch leaf=%d component=%d got=%d expected=%d\n",
                            label, leaf, component, actual,
                            expected[component]);
                canonical_mismatches++;
            }
        }
    }
}

static int compare_exact(const int16_t got[864], const int16_t expected[864],
                         const char *label, int *counter)
{
    int before = *counter;
    for (int i = 0; i < 864; i++) {
        if (got[i] != expected[i]) {
            if (*counter < 8)
                fprintf(stderr, "%s exact mismatch i=%d got=%d expected=%d\n",
                        label, i, got[i], expected[i]);
            (*counter)++;
        }
    }
    return *counter != before;
}

static void check_case(const int16_t a[864], const int16_t b[864],
                       const int16_t c[864], const char *label)
{
    int16_t got[864];
    int16_t got_add[864];
    int16_t legacy_a[864];
    int16_t legacy_b[864];
    int16_t legacy_c[864];
    int16_t legacy_product[864];
    int16_t expected[864];
    int16_t alias[864];

    fr0_to_legacy(legacy_a, a);
    fr0_to_legacy(legacy_b, b);
    fr0_to_legacy(legacy_c, c);

    gt864_fr0_basemul_neon(got, a, b);
    scalar_legacy_product(legacy_product, legacy_a, legacy_b, NULL);
    legacy_to_fr0(expected, legacy_product);
    compare_exact(got, expected, label, &exact_basemul_mismatches);
    check_canonical_leaf(got, a, b, NULL, label);

    gt864_fr0_basemul_add_neon(got_add, a, b, c);
    scalar_legacy_product(legacy_product, legacy_a, legacy_b, legacy_c);
    legacy_to_fr0(expected, legacy_product);
    compare_exact(got_add, expected, label, &exact_add_mismatches);
    check_canonical_leaf(got_add, a, b, c, label);

    memcpy(alias, a, sizeof(alias));
    gt864_fr0_basemul_neon(alias, alias, b);
    compare_exact(alias, got, "alias-a", &alias_mismatches);
    memcpy(alias, b, sizeof(alias));
    gt864_fr0_basemul_neon(alias, a, alias);
    compare_exact(alias, got, "alias-b", &alias_mismatches);
    memcpy(alias, c, sizeof(alias));
    gt864_fr0_basemul_add_neon(alias, a, b, alias);
    compare_exact(alias, got_add, "alias-c", &alias_mismatches);
    memcpy(alias, a, sizeof(alias));
    gt864_fr0_basemul_add_neon(alias, alias, b, c);
    compare_exact(alias, got_add, "alias-add-a", &alias_mismatches);
    memcpy(alias, b, sizeof(alias));
    gt864_fr0_basemul_add_neon(alias, a, alias, c);
    compare_exact(alias, got_add, "alias-add-b", &alias_mismatches);
    cases++;
}

static int16_t random_bound(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % (2U * BOUND + 1U)) - BOUND);
}

int main(void)
{
    int16_t a[864];
    int16_t b[864];
    int16_t c[864];
    static const int16_t values[] = {-BOUND, BOUND, -1728, 1728, 0, 1, -1};

    for (size_t k = 0; k < sizeof(values) / sizeof(values[0]); k++) {
        for (int i = 0; i < 864; i++) {
            a[i] = values[k];
            b[i] = values[(k + 2) % (sizeof(values) / sizeof(values[0]))];
            c[i] = values[(k + 4) % (sizeof(values) / sizeof(values[0]))];
        }
        check_case(a, b, c, "boundary");
    }
    for (int trial = 0; trial < 40; trial++) {
        for (int i = 0; i < 864; i++) {
            a[i] = random_bound();
            b[i] = random_bound();
            c[i] = random_bound();
        }
        check_case(a, b, c, "random");
    }

    printf("gt864_fr0_basemul_arithmetic_gate=%s\n",
           exact_basemul_mismatches + exact_add_mismatches +
                   canonical_mismatches + alias_mismatches == 0 ?
               "pass" : "fail");
    printf("cases=%d\n", cases);
    printf("exact_basemul_mismatches=%d\n", exact_basemul_mismatches);
    printf("exact_basemul_add_mismatches=%d\n", exact_add_mismatches);
    printf("canonical_cubic_mismatches=%d\n", canonical_mismatches);
    printf("alias_mismatches=%d\n", alias_mismatches);
    printf("production_linked=0\n");
    return exact_basemul_mismatches + exact_add_mismatches +
           canonical_mismatches + alias_mismatches != 0;
}
