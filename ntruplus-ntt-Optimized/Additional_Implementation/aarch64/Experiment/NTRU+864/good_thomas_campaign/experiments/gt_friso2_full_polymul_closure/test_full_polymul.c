#include "gt864_friso2_inverse.h"
#include "../gt_friso2_basemul_cycle/gt864_friso2_basemul_neon.h"
#include "../gt_friso2_leaf_basis_abi/gt864_friso2.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define Q 3457

extern void gt864_forward_poly_ntt_friso2(int16_t *, const int16_t *);

static uint32_t random_state = 0x864cf4U;
static int inverse_mismatches;
static int product_mismatches;
static int inverse_cases;
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
    int16_t value_mod_q = canonical(value);
    return value_mod_q > Q / 2 ? (int16_t)(value_mod_q - Q) : value_mod_q;
}

static int16_t random_small(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((random_state % 5u) - 2);
}

static int16_t random_centered(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return (int16_t)((int32_t)(random_state % Q) - Q / 2);
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

static void check_direct_inverse(const int16_t friso2[864], const char *label)
{
    int16_t fr0[864];
    int16_t direct_p8[GT864_INVERSE_P8_PADDED];
    int16_t oracle_p8[GT864_INVERSE_P8_PADDED];
    int16_t direct[864];
    int16_t oracle[864];

    gt864_friso2_denormalize(fr0, friso2);
    gt864_fr0_inverse_ntt9_neon(oracle_p8, fr0);
    gt864_fr0_inverse_finish_neon(oracle, oracle_p8);
    gt864_friso2_inverse_ntt9_neon(direct_p8, friso2);
    gt864_fr0_inverse_finish_neon(direct, direct_p8);
    for (int i = 0; i < 864; i++) {
        if (canonical(direct[i]) != canonical(oracle[i])) {
            if (inverse_mismatches < 8)
                fprintf(stderr,
                        "%s inverse mismatch i=%d got=%d oracle=%d\n",
                        label, i, direct[i], oracle[i]);
            inverse_mismatches++;
        }
    }
    inverse_cases++;
}

static void check_product(const int16_t a[864], const int16_t b[864],
                          const char *label)
{
    int16_t fa[864];
    int16_t fb[864];
    int16_t fp[864];
    int16_t p8[GT864_INVERSE_P8_PADDED];
    int16_t got[864];
    int16_t expected[864];

    gt864_forward_poly_ntt_friso2(fa, a);
    gt864_forward_poly_ntt_friso2(fb, b);
    gt864_friso2_basemul_direct(fp, fa, fb);
    gt864_friso2_inverse_ntt9_neon(p8, fp);
    gt864_fr0_inverse_finish_neon(got, p8);
    schoolbook(expected, a, b);
    for (int i = 0; i < 864; i++) {
        if (canonical(got[i]) != canonical(expected[i])) {
            if (product_mismatches < 8)
                fprintf(stderr,
                        "%s product mismatch i=%d got=%d expected=%d\n",
                        label, i, got[i], expected[i]);
            product_mismatches++;
        }
    }
    product_cases++;
}

int main(void)
{
    int16_t friso2[864];
    int16_t a[864];
    int16_t b[864];
    static const int positions[] = {0, 1, 2, 3, 431, 432, 433, 861, 862, 863};

    memset(friso2, 0, sizeof(friso2));
    check_direct_inverse(friso2, "inverse-zero");
    for (size_t k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(friso2, 0, sizeof(friso2));
        friso2[positions[k]] = (int16_t)(k & 1 ? -1728 : 1728);
        check_direct_inverse(friso2, "inverse-impulse");
    }
    for (int trial = 0; trial < 32; trial++) {
        for (int i = 0; i < 864; i++)
            friso2[i] = random_centered();
        check_direct_inverse(friso2, "inverse-random");
    }

    memset(a, 0, sizeof(a));
    memset(b, 0, sizeof(b));
    check_product(a, b, "product-zero");
    for (size_t ka = 0; ka < sizeof(positions) / sizeof(positions[0]); ka++) {
        for (size_t kb = 0; kb < sizeof(positions) / sizeof(positions[0]); kb++) {
            memset(a, 0, sizeof(a));
            memset(b, 0, sizeof(b));
            a[positions[ka]] = (int16_t)(ka & 1 ? -1 : 1);
            b[positions[kb]] = (int16_t)(kb & 1 ? 1 : -1);
            check_product(a, b, "product-impulse-pair");
        }
    }
    for (int trial = 0; trial < 16; trial++) {
        for (int i = 0; i < 864; i++) {
            a[i] = random_small();
            b[i] = random_small();
        }
        check_product(a, b, "product-random-small");
    }

    printf("gt864_friso2_full_polymul_closure=%s\n",
           inverse_mismatches + product_mismatches == 0 ? "pass" : "fail");
    printf("direct_inverse_cases=%d\n", inverse_cases);
    printf("direct_inverse_modq_mismatches=%d\n", inverse_mismatches);
    printf("full_product_cases=%d\n", product_cases);
    printf("full_product_modq_mismatches=%d\n", product_mismatches);
    printf("forward_calls_per_product=2\n");
    printf("basemul_calls_per_product=1\n");
    printf("inverse_calls_per_product=1\n");
    printf("friso2_fr0_conversion_buffer_passes=0\n");
    printf("production_linked=0\n");
    return inverse_mismatches + product_mismatches != 0;
}
