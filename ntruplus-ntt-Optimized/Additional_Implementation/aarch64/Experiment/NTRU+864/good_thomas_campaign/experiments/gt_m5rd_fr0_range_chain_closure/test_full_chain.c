#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt864_fr0_basemul.h"
#include "gt864_fr0_inverse_asm.h"

#define N 864
#define Q 3457

void gt864_forward_poly_ntt_all_one_mul_b3(int16_t out[N],
                                            const int16_t in[N]);

static uint32_t random_state = 0x670864U;
static int product_cases;
static int add_cases;
static int mismatches;

static int16_t centered(int64_t value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    if (value > Q / 2)
        value -= Q;
    return (int16_t)value;
}

static void schoolbook(int16_t out[N], const int16_t a[N],
                       const int16_t b[N])
{
    int64_t product[2 * N - 1] = {0};
    for (int i = 0; i < N; i++)
        for (int j = 0; j < N; j++)
            product[i + j] += (int32_t)a[i] * b[j];
    for (int degree = 2 * N - 2; degree >= N; degree--) {
        int64_t value = product[degree] % Q;
        product[degree - 432] += value;
        product[degree - 864] -= value;
    }
    for (int i = 0; i < N; i++)
        out[i] = centered(product[i]);
}

static void inverse_fr0(int16_t out[N], const int16_t in[N])
{
    int16_t p8[896] = {0};
    gt864_fr0_inverse_ntt9_asm(p8, in);
    gt864_fr0_inverse_finish_asm(out, p8);
}

static void compare(const int16_t got[N], const int16_t expected[N],
                    const char *label)
{
    for (int i = 0; i < N; i++) {
        if (centered(got[i]) != centered(expected[i])) {
            if (mismatches < 8)
                fprintf(stderr,
                        "%s mismatch i=%d got=%d expected=%d\n",
                        label, i, got[i], expected[i]);
            mismatches++;
        }
    }
}

static void check_product(const int16_t a[N], const int16_t b[N],
                          const char *label)
{
    int16_t fa[N], fb[N], fp[N], got[N], expected[N];
    gt864_forward_poly_ntt_all_one_mul_b3(fa, a);
    gt864_forward_poly_ntt_all_one_mul_b3(fb, b);
    gt864_fr0_basemul_neon(fp, fa, fb);
    inverse_fr0(got, fp);
    schoolbook(expected, a, b);
    compare(got, expected, label);
    product_cases++;
}

static void check_product_add(const int16_t a[N], const int16_t b[N],
                              const int16_t c[N], const char *label)
{
    int16_t fa[N], fb[N], fc[N], fp[N], got[N], expected[N];
    int16_t product[N];
    gt864_forward_poly_ntt_all_one_mul_b3(fa, a);
    gt864_forward_poly_ntt_all_one_mul_b3(fb, b);
    gt864_forward_poly_ntt_all_one_mul_b3(fc, c);
    gt864_fr0_basemul_add_neon(fp, fa, fb, fc);
    inverse_fr0(got, fp);
    schoolbook(product, a, b);
    for (int i = 0; i < N; i++)
        expected[i] = centered((int32_t)product[i] + c[i]);
    compare(got, expected, label);
    add_cases++;
}

static int16_t random_full(void)
{
    random_state = random_state * 1664525U + 1013904223U;
    return (int16_t)((int32_t)(random_state % 6913U) - 3456);
}

int main(void)
{
    int16_t a[N], b[N], c[N];
    static const int positions[] = {0, 1, 2, 431, 432, 433, 861, 862, 863};

    for (int i = 0; i < N; i++) {
        a[i] = (int16_t)(i & 1 ? -3456 : 3456);
        b[i] = (int16_t)(i % 3 == 0 ? 3456 : -3456);
        c[i] = (int16_t)(i % 5 == 0 ? -3456 : 3456);
    }
    check_product(a, b, "alternating-boundary-product");
    check_product_add(a, b, c, "alternating-boundary-add");

    for (unsigned k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(a, 0, sizeof(a));
        memset(b, 0, sizeof(b));
        a[positions[k]] = (int16_t)(k & 1 ? -3456 : 3456);
        b[positions[(k + 4) % (sizeof(positions) / sizeof(positions[0]))]] =
            (int16_t)(k & 1 ? 3456 : -3456);
        check_product(a, b, "boundary-impulse-product");
    }

    for (int trial = 0; trial < 8; trial++) {
        for (int i = 0; i < N; i++) {
            a[i] = random_full();
            b[i] = random_full();
            c[i] = random_full();
        }
        check_product(a, b, "random-full-product");
        if (trial < 4)
            check_product_add(a, b, c, "random-full-add");
    }

    printf("g0_full_chain_gate=%s\n", mismatches == 0 ? "pass" : "fail");
    printf("product_cases=%d\n", product_cases);
    printf("basemul_add_cases=%d\n", add_cases);
    printf("coefficient_mismatches=%d\n", mismatches);
    printf("production_linked=0\n");
    return mismatches != 0;
}
