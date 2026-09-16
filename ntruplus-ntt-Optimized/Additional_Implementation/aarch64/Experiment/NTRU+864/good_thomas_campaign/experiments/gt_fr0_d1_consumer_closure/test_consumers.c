#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_d1.h"
#include "gt864_fr0_inverse_asm.h"
#include "poly.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457
#define POLYBYTES 1296
#define GUARD 16

void gt864_forward_poly_ntt_all_one_mul_b3(int16_t out[N],
                                            const int16_t in[N]);

static uint32_t random_state = 0xd1c10864U;
static int c1_cases;
static int c2_cases;
static int coefficient_mismatches;
static int byte_mismatches;
static int alias_mismatches;
static int sentinel_mismatches;

static int16_t centered(int64_t value)
{
    value %= Q;
    if (value < 0) value += Q;
    if (value > Q / 2) value -= Q;
    return (int16_t)value;
}

static uint32_t random_u32(void)
{
    random_state = random_state * 1664525U + 1013904223U;
    return random_state;
}

static int16_t random_full(void)
{
    return (int16_t)((int32_t)(random_u32() % 6913U) - 3456);
}

static int16_t random_small(void)
{
    return (int16_t)((int32_t)(random_u32() % 3U) - 1);
}

static void schoolbook(int16_t out[N], const int16_t a[N], const int16_t b[N])
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
    for (int i = 0; i < N; i++) out[i] = centered(product[i]);
}

static void inverse_fr0(int16_t out[N], const int16_t in[N])
{
    int16_t p8[896] = {0};
    gt864_fr0_inverse_ntt9_asm(p8, in);
    gt864_fr0_inverse_finish_asm(out, p8);
}

static void compare_coefficients(const int16_t got[N],
                                 const int16_t expected[N], const char *label,
                                 int *counter)
{
    for (int i = 0; i < N; i++)
        if (centered(got[i]) != centered(expected[i])) {
            if (*counter < 8)
                fprintf(stderr, "%s coefficient i=%d got=%d expected=%d\n",
                        label, i, got[i], expected[i]);
            (*counter)++;
        }
}

static void guarded_inverse(int16_t out[N], const int16_t in[N])
{
    struct {
        uint8_t prefix[GUARD];
        int16_t value[N];
        uint8_t suffix[GUARD];
    } guarded;
    memset(&guarded, 0xa5, sizeof(guarded));
    inverse_fr0(guarded.value, in);
    for (int i = 0; i < GUARD; i++)
        if (guarded.prefix[i] != 0xa5 || guarded.suffix[i] != 0xa5)
            sentinel_mismatches++;
    memcpy(out, guarded.value, sizeof(guarded.value));
}

static void check_c1(const int16_t a[N], const int16_t b[N], const char *label)
{
    int16_t fa[N], fb[N], old_product[N], d1_product[N];
    int16_t alias[N], old_out[N], d1_out[N], expected[N];

    gt864_forward_poly_ntt_all_one_mul_b3(fa, a);
    gt864_forward_poly_ntt_all_one_mul_b3(fb, b);
    gt864_fr0_basemul_neon(old_product, fa, fb);
    gt864_fr0_basemul_d1_neon(d1_product, fa, fb);
    guarded_inverse(old_out, old_product);
    guarded_inverse(d1_out, d1_product);
    schoolbook(expected, a, b);
    compare_coefficients(old_out, expected, label, &coefficient_mismatches);
    compare_coefficients(d1_out, expected, label, &coefficient_mismatches);
    compare_coefficients(d1_out, old_out, label, &coefficient_mismatches);

    memcpy(alias, fa, sizeof(alias));
    gt864_fr0_basemul_d1_neon(alias, alias, fb);
    compare_coefficients(alias, d1_product, "c1-alias-a", &alias_mismatches);
    memcpy(alias, fb, sizeof(alias));
    gt864_fr0_basemul_d1_neon(alias, fa, alias);
    compare_coefficients(alias, d1_product, "c1-alias-b", &alias_mismatches);
    c1_cases++;
}

static void serialize(uint8_t out[POLYBYTES], const int16_t in[N])
{
    poly value;
    memcpy(value.coeffs, in, sizeof(value.coeffs));
    poly_tobytes(out, &value);
}

static void check_c2(const int16_t a[N], const int16_t b[N],
                     const int16_t c[N], const char *label)
{
    int16_t fa[N], fb[N], fc[N], old_product[N], d1_product[N], alias[N];
    uint8_t old_bytes[POLYBYTES], d1_bytes[POLYBYTES];

    gt864_forward_poly_ntt_all_one_mul_b3(fa, a);
    gt864_forward_poly_ntt_all_one_mul_b3(fb, b);
    gt864_forward_poly_ntt_all_one_mul_b3(fc, c);
    gt864_fr0_basemul_add_neon(old_product, fa, fb, fc);
    gt864_fr0_basemul_add_d1_neon(d1_product, fa, fb, fc);
    serialize(old_bytes, old_product);
    serialize(d1_bytes, d1_product);
    for (int i = 0; i < POLYBYTES; i++)
        if (old_bytes[i] != d1_bytes[i]) {
            if (byte_mismatches < 8)
                fprintf(stderr, "%s byte i=%d old=%u d1=%u\n", label, i,
                        (unsigned)old_bytes[i], (unsigned)d1_bytes[i]);
            byte_mismatches++;
        }
    memcpy(alias, fc, sizeof(alias));
    gt864_fr0_basemul_add_d1_neon(alias, fa, fb, alias);
    compare_coefficients(alias, d1_product, "c2-alias-c", &alias_mismatches);
    c2_cases++;
}

int main(void)
{
    int16_t a[N], b[N], c[N];
    static const int positions[] = {0, 1, 2, 431, 432, 433, 861, 862, 863};

    for (int i = 0; i < N; i++) {
        a[i] = (int16_t)(i & 1 ? -3456 : 3456);
        b[i] = (int16_t)(i % 3 ? -3456 : 3456);
        c[i] = (int16_t)(i % 5 ? 3456 : -3456);
    }
    check_c1(a, b, "boundary");
    check_c2(a, b, c, "boundary");

    for (unsigned k = 0; k < sizeof(positions) / sizeof(positions[0]); k++) {
        memset(a, 0, sizeof(a)); memset(b, 0, sizeof(b)); memset(c, 0, sizeof(c));
        a[positions[k]] = (int16_t)(k & 1 ? -3456 : 3456);
        b[positions[(k + 4) % 9]] = (int16_t)(k & 1 ? 3456 : -3456);
        c[positions[(k + 7) % 9]] = 1;
        check_c1(a, b, "impulse");
        check_c2(a, b, c, "impulse");
    }
    for (int trial = 0; trial < 24; trial++) {
        for (int i = 0; i < N; i++) {
            a[i] = random_full();
            b[i] = trial < 12 ? random_full() : random_small();
            c[i] = trial < 12 ? random_full() : random_small();
        }
        check_c1(a, b, trial < 12 ? "random-full" : "encap-shaped");
        check_c2(a, b, c, trial < 12 ? "random-full" : "encap-shaped");
    }

    printf("d1_c1_polymul=%s cases=%d coefficient_mismatches=%d alias=%d sentinel=%d\n",
           coefficient_mismatches + alias_mismatches + sentinel_mismatches == 0 ? "pass" : "fail",
           c1_cases, coefficient_mismatches, alias_mismatches, sentinel_mismatches);
    printf("d1_c2_serializer=%s cases=%d byte_mismatches=%d\n",
           byte_mismatches == 0 ? "pass" : "fail", c2_cases, byte_mismatches);
    printf("production_linked=0\n");
    return coefficient_mismatches + byte_mismatches + alias_mismatches + sentinel_mismatches != 0;
}
