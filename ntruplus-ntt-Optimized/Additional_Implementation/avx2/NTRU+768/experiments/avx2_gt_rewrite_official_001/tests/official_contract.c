#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "poly.h"
#include "gt_schoolbook.h"

enum { RANDOM_CASES = 64 };

typedef struct {
    int min;
    int max;
    uint64_t digest;
} profile;

typedef struct {
    int r_equals_a;
    int r_equals_b;
    int a_equals_b;
    int all_equal;
} alias_profile;

static uint64_t rng_state = UINT64_C(0x6a09e667f3bcc909);

static uint32_t prng32(void)
{
    uint64_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    rng_state = x;
    return (uint32_t)(x >> 16);
}

static uint64_t fnv1a(const void *data, size_t len, uint64_t h)
{
    const uint8_t *p = data;
    for (size_t i = 0; i < len; ++i) {
        h ^= p[i];
        h *= UINT64_C(1099511628211);
    }
    return h;
}

static void profile_init(profile *p)
{
    p->min = INT_MAX;
    p->max = INT_MIN;
    p->digest = UINT64_C(1469598103934665603);
}

static void profile_add(profile *p, const poly *a)
{
    for (size_t i = 0; i < NTRUPLUS_N; ++i) {
        if (a->coeffs[i] < p->min)
            p->min = a->coeffs[i];
        if (a->coeffs[i] > p->max)
            p->max = a->coeffs[i];
    }
    p->digest = fnv1a(a, sizeof *a, p->digest);
}

static int exact_poly(const poly *a, const poly *b)
{
    return memcmp(a, b, sizeof *a) == 0;
}

static void fill_case(poly *a, unsigned id)
{
    memset(a, 0, sizeof *a);
    switch (id) {
    case 0: /* zero */
        break;
    case 1: /* multiplicative identity */
        a->coeffs[0] = 1;
        break;
    case 2: /* impulse at top split */
        a->coeffs[384] = 1;
        break;
    case 3: /* impulse at final coefficient */
        a->coeffs[767] = -1;
        break;
    case 4:
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            a->coeffs[i] = (int16_t)((i & 1) ? 4 : -3);
        break;
    case 5:
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            a->coeffs[i] = 4;
        break;
    case 6:
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            a->coeffs[i] = -3;
        break;
    default:
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            a->coeffs[i] = (int16_t)((int)(prng32() & 7) - 3);
        break;
    }
}

static void alias_profile_init(alias_profile *p)
{
    p->r_equals_a = 1;
    p->r_equals_b = 1;
    p->a_equals_b = 1;
    p->all_equal = 1;
}

static void call_basemul(poly *r, const poly *a, const poly *b, int scale)
{
    if (scale)
        poly_basemul_scale(r, a, b);
    else
        poly_basemul(r, a, b);
}

static void check_basemul_alias(alias_profile *result, const poly *a,
                                const poly *b, int scale)
{
    poly expected;
    poly square_expected;
    poly x;
    poly y;

    call_basemul(&expected, a, b, scale);

    x = *a;
    y = *b;
    call_basemul(&x, &x, &y, scale);
    result->r_equals_a &= exact_poly(&x, &expected);

    x = *a;
    y = *b;
    call_basemul(&y, &x, &y, scale);
    result->r_equals_b &= exact_poly(&y, &expected);

    x = *a;
    y = *a;
    call_basemul(&square_expected, &x, &y, scale);
    call_basemul(&expected, a, a, scale);
    result->a_equals_b &= exact_poly(&expected, &square_expected);

    x = *a;
    call_basemul(&x, &x, &x, scale);
    result->all_equal &= exact_poly(&x, &square_expected);
}

static int check_serialization_contract(void)
{
    uint8_t bytes[NTRUPLUS_POLYBYTES];
    poly a;
    poly b;

    for (unsigned raw = 0; raw < 4096; ++raw) {
        for (size_t i = 0; i < NTRUPLUS_N / 2; ++i) {
            bytes[3 * i + 0] = (uint8_t)raw;
            bytes[3 * i + 1] = (uint8_t)((raw >> 8) | (raw << 4));
            bytes[3 * i + 2] = (uint8_t)(raw >> 4);
        }
        memset(&b, 0xa5, sizeof b);
        const int rc = poly_frombytes(&b, bytes);
        if (rc != (raw >= NTRUPLUS_Q))
            return 0;
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            if (b.coeffs[i] != (int16_t)raw)
                return 0;
    }

    for (size_t i = 0; i < NTRUPLUS_N; ++i)
        a.coeffs[i] = (int16_t)((int)(i % NTRUPLUS_Q) - 1728);
    poly_tobytes(bytes, &a);
    if (poly_frombytes(&b, bytes) != 0)
        return 0;
    for (size_t i = 0; i < NTRUPLUS_N; ++i) {
        int expected = a.coeffs[i];
        if (expected < 0)
            expected += NTRUPLUS_Q;
        if (b.coeffs[i] != expected)
            return 0;
    }
    return 1;
}

int main(void)
{
    profile ntt_profile;
    profile mul_profile;
    profile mul_scale_profile;
    profile inv_profile;
    profile baseinv_profile;
    int failures = 0;
    alias_profile basemul_alias;
    alias_profile basemul_scale_alias;
    int baseinv_alias = 1;
    int baseinv_failure_zero = 1;
    int schoolbook_product = 1;
    int inverse_roundtrip_mod_q = 1;
    int serialization = 1;

    profile_init(&ntt_profile);
    profile_init(&mul_profile);
    profile_init(&mul_scale_profile);
    profile_init(&inv_profile);
    profile_init(&baseinv_profile);
    alias_profile_init(&basemul_alias);
    alias_profile_init(&basemul_scale_alias);

    for (unsigned tc = 0; tc < 7 + RANDOM_CASES; ++tc) {
        poly a;
        poly b;
        poly a_ntt;
        poly b_ntt;
        poly again;
        poly product;
        poly scaled_product;
        poly inverse;
        int16_t oracle[NTRUPLUS_N];

        fill_case(&a, tc);
        fill_case(&b, tc == 0 ? 1 : tc + 1);
        a_ntt = a;
        b_ntt = b;
        poly_ntt(&a_ntt);
        poly_ntt(&b_ntt);
        again = a;
        poly_ntt(&again);
        if (!exact_poly(&again, &a_ntt))
            ++failures;
        profile_add(&ntt_profile, &a_ntt);
        profile_add(&ntt_profile, &b_ntt);

        poly_basemul(&product, &a_ntt, &b_ntt);
        again = product;
        poly_basemul(&product, &a_ntt, &b_ntt);
        if (!exact_poly(&again, &product))
            ++failures;
        profile_add(&mul_profile, &product);

        poly_basemul_scale(&scaled_product, &a_ntt, &b_ntt);
        again = scaled_product;
        poly_basemul_scale(&scaled_product, &a_ntt, &b_ntt);
        if (!exact_poly(&again, &scaled_product))
            ++failures;
        profile_add(&mul_scale_profile, &scaled_product);

        check_basemul_alias(&basemul_alias, &a_ntt, &b_ntt, 0);
        check_basemul_alias(&basemul_scale_alias, &a_ntt, &b_ntt, 1);

        inverse = scaled_product;
        poly_invntt_scale(&inverse);
        profile_add(&inv_profile, &inverse);
        gt_schoolbook_mul(oracle, a.coeffs, b.coeffs);
        schoolbook_product &= gt_equal_mod_q(inverse.coeffs, oracle);

        inverse = a_ntt;
        poly_invntt_scale(&inverse);
        inverse_roundtrip_mod_q &= gt_equal_mod_q(inverse.coeffs, a.coeffs);

        if (tc != 0) {
            poly inv_distinct;
            poly inv_alias = a_ntt;
            const int rc_distinct = poly_baseinv(&inv_distinct, &a_ntt);
            const int rc_alias = poly_baseinv(&inv_alias, &inv_alias);
            baseinv_alias &= rc_distinct == rc_alias;
            baseinv_alias &= exact_poly(&inv_distinct, &inv_alias);
            profile_add(&baseinv_profile, &inv_distinct);
        }
    }

    {
        poly zero = {{0}};
        poly out;
        memset(&out, 0xa5, sizeof out);
        const int rc = poly_baseinv(&out, &zero);
        baseinv_failure_zero &= rc == 1;
        baseinv_failure_zero &= exact_poly(&out, &zero);
    }

    serialization &= check_serialization_contract();
    failures += !baseinv_failure_zero;
    failures += !schoolbook_product;
    failures += !serialization;
    /* This is characterization: Official inverse includes a caller scale. */

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"official_revision\": \"0c249d5828b90e8dd5de2c8405323d5ee2a0ce41\",\n");
    printf("  \"seed\": \"0x6a09e667f3bcc909\",\n");
    printf("  \"cases\": %d,\n", 7 + RANDOM_CASES);
    printf("  \"forward\": {\"min\": %d, \"max\": %d, \"fnv1a64\": \"%016" PRIx64 "\"},\n",
           ntt_profile.min, ntt_profile.max, ntt_profile.digest);
    printf("  \"basemul\": {\"min\": %d, \"max\": %d, \"fnv1a64\": \"%016" PRIx64 "\", \"alias\": {\"r_equals_a\": %s, \"r_equals_b\": %s, \"a_equals_b\": %s, \"all_equal\": %s}},\n",
           mul_profile.min, mul_profile.max, mul_profile.digest,
           basemul_alias.r_equals_a ? "true" : "false",
           basemul_alias.r_equals_b ? "true" : "false",
           basemul_alias.a_equals_b ? "true" : "false",
           basemul_alias.all_equal ? "true" : "false");
    printf("  \"basemul_scale\": {\"min\": %d, \"max\": %d, \"fnv1a64\": \"%016" PRIx64 "\", \"alias\": {\"r_equals_a\": %s, \"r_equals_b\": %s, \"a_equals_b\": %s, \"all_equal\": %s}},\n",
           mul_scale_profile.min, mul_scale_profile.max,
           mul_scale_profile.digest,
           basemul_scale_alias.r_equals_a ? "true" : "false",
           basemul_scale_alias.r_equals_b ? "true" : "false",
           basemul_scale_alias.a_equals_b ? "true" : "false",
           basemul_scale_alias.all_equal ? "true" : "false");
    printf("  \"inverse\": {\"min\": %d, \"max\": %d, \"fnv1a64\": \"%016" PRIx64 "\", \"raw_ntt_roundtrip_mod_q\": %s},\n",
           inv_profile.min, inv_profile.max, inv_profile.digest,
           inverse_roundtrip_mod_q ? "true" : "false");
    printf("  \"baseinv\": {\"min\": %d, \"max\": %d, \"fnv1a64\": \"%016" PRIx64 "\", \"in_place\": %s, \"zero_failure_zeroes_output\": %s},\n",
           baseinv_profile.min, baseinv_profile.max, baseinv_profile.digest,
           baseinv_alias ? "true" : "false",
           baseinv_failure_zero ? "true" : "false");
    printf("  \"schoolbook_product_mod_q\": %s,\n",
           schoolbook_product ? "true" : "false");
    printf("  \"serialization_all_12bit_values\": %s,\n",
           serialization ? "true" : "false");
    printf("  \"failures\": %d\n", failures);
    printf("}\n");

    return failures == 0 ? 0 : 1;
}
