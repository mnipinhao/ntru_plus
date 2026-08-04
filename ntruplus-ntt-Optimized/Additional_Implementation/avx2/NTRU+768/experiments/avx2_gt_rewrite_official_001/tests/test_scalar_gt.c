#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_backend.h"
#include "gt_generated_tables.h"
#include "gt_schoolbook.h"

enum { RANDOM_CASES = 16 };

static uint64_t rng_state = UINT64_C(0xbb67ae8584caa73b);

static uint32_t prng32(void)
{
    uint64_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    rng_state = x;
    return (uint32_t)(x >> 16);
}

static void fill_case(poly *a, unsigned id)
{
    memset(a, 0, sizeof *a);
    switch (id) {
    case 0:
        break;
    case 1:
        a->coeffs[0] = 1;
        break;
    case 2:
        a->coeffs[384] = 1;
        break;
    case 3:
        a->coeffs[767] = -1;
        break;
    case 4:
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            a->coeffs[i] = (int16_t)((i & 1U) ? 4 : -3);
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
            a->coeffs[i] = (int16_t)((int)(prng32() & 7U) - 3);
        break;
    }
}

static int bytes_equal(const poly *official, const poly *gt)
{
    uint8_t official_bytes[NTRUPLUS_POLYBYTES];
    uint8_t gt_bytes[NTRUPLUS_POLYBYTES];
    poly_tobytes(official_bytes, official);
    gt_poly_tobytes(gt_bytes, gt);
    return memcmp(official_bytes, gt_bytes, sizeof official_bytes) == 0;
}

static int check_forward_case(const poly *input, unsigned id)
{
    poly official = *input;
    poly b1 = *input;
    poly b2 = *input;
    poly c = *input;
    poly avx2_b1 = *input;
    poly avx2_b2 = *input;
    poly staged_b1;
    _Alignas(32) int16_t rows[3][32][16];
    gt_range_trace trace;

    poly_ntt(&official);
    gt_ref_ntt_variant(&b1, GT_N32_B1, &trace);
    if (trace.top_min < -2891 || trace.top_max > 2896) {
        fprintf(stderr, "top range failed case=%u min=%d max=%d\n",
                id, trace.top_min, trace.top_max);
        return 0;
    }
    gt_ref_ntt_variant(&b2, GT_N32_B2, NULL);
    gt_ref_ntt_variant(&c, GT_N32_C, NULL);
    gt_poly_ntt_avx2_b1(&avx2_b1);
    gt_poly_ntt_avx2_b2(&avx2_b2);
    gt_profile_forward_frontend(rows, input);
    gt_profile_forward_b1(&staged_b1,
                          (const int16_t (*)[32][16])rows);
    if (memcmp(&b1, &b2, sizeof b1) != 0 || memcmp(&b2, &c, sizeof b2) != 0) {
        fprintf(stderr, "N32 stage differential failed case=%u\n", id);
        return 0;
    }
    if (memcmp(&b2, &avx2_b1, sizeof b2) != 0
            || memcmp(&avx2_b1, &staged_b1, sizeof avx2_b1) != 0
            || memcmp(&b2, &avx2_b2, sizeof b2) != 0) {
        fprintf(stderr, "AVX2/staged B1/B2 differential failed case=%u\n", id);
        return 0;
    }
    if (!bytes_equal(&official, &b2)) {
        fprintf(stderr, "Official forward mapping failed case=%u\n", id);
        return 0;
    }
    {
        poly scalar_inverse = b2;
        poly avx2_inverse = b2;
        poly staged_inverse;
        _Alignas(32) int16_t after32[3][32][16];
        gt_ref_poly_invntt_scale(&scalar_inverse);
        gt_poly_invntt_avx2_b(&avx2_inverse);
        gt_profile_inverse_b1(after32, &b2);
        gt_profile_inverse_tail(&staged_inverse,
                                (const int16_t (*)[32][16])after32);
        if (memcmp(&scalar_inverse, &avx2_inverse, sizeof scalar_inverse) != 0
                || memcmp(&avx2_inverse, &staged_inverse,
                          sizeof avx2_inverse) != 0) {
            fprintf(stderr, "AVX2/staged inverse differential failed case=%u\n",
                    id);
            return 0;
        }
    }
    gt_poly_invntt_scale(&b2);
    if (!gt_equal_mod_q(b2.coeffs, input->coeffs)) {
        fprintf(stderr, "GT round-trip failed case=%u\n", id);
        return 0;
    }
    return 1;
}

static int check_product_case(const poly *a, const poly *b, unsigned id)
{
    poly official_a = *a;
    poly official_b = *b;
    poly official_product;
    poly gt_a = *a;
    poly gt_b = *b;
    poly gt_product;
    int16_t oracle[NTRUPLUS_N];

    poly_ntt(&official_a);
    poly_ntt(&official_b);
    poly_basemul(&official_product, &official_a, &official_b);
    gt_poly_ntt(&gt_a);
    gt_poly_ntt(&gt_b);
    gt_poly_basemul(&gt_product, &gt_a, &gt_b);
    if (!bytes_equal(&official_product, &gt_product)) {
        fprintf(stderr, "basemul mapping failed case=%u\n", id);
        return 0;
    }

    gt_poly_invntt_scale(&gt_product);
    gt_schoolbook_mul(oracle, a->coeffs, b->coeffs);
    if (!gt_equal_mod_q(gt_product.coeffs, oracle)) {
        fprintf(stderr, "schoolbook product failed case=%u\n", id);
        return 0;
    }
    return 1;
}

static int check_baseinv(const poly *input, unsigned id)
{
    poly official = *input;
    poly gt = *input;
    poly gt_alias;
    poly official_inverse;
    poly gt_inverse;

    poly_ntt(&official);
    gt_poly_ntt(&gt);
    const int official_rc = poly_baseinv(&official_inverse, &official);
    const int gt_rc = gt_poly_baseinv(&gt_inverse, &gt);
    if (official_rc != gt_rc) {
        fprintf(stderr, "baseinv return mismatch case=%u official=%d gt=%d\n",
                id, official_rc, gt_rc);
        return 0;
    }
    if (!bytes_equal(&official_inverse, &gt_inverse)) {
        fprintf(stderr, "baseinv value mismatch case=%u\n", id);
        return 0;
    }
    gt_alias = gt;
    if (gt_poly_baseinv(&gt_alias, &gt_alias) != gt_rc
            || !gt_ntt_equal_canonical(&gt_alias, &gt_inverse)) {
        fprintf(stderr, "GT baseinv alias mismatch case=%u\n", id);
        return 0;
    }
    return 1;
}

static int check_baseinv_failure_patterns(void)
{
    poly input;
    poly reference;
    poly candidate;
    poly product;

    for (unsigned pattern = 0; pattern < 8; ++pattern) {
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            input.coeffs[i] = (int16_t)((int)(prng32() % NTRUPLUS_Q) - 1728);
        if (pattern != 0) {
            const size_t batch = (17U * pattern) % 12U;
            const size_t lane = (29U * pattern) % 16U;
            for (size_t degree = 0; degree < 4; ++degree)
                input.coeffs[64 * batch + 16 * degree + lane] = 0;
        }

        const int reference_rc = gt_ref_poly_baseinv(&reference, &input);
        const int candidate_rc = gt_poly_baseinv(&candidate, &input);
        if (reference_rc != candidate_rc
                || !gt_ntt_equal_canonical(&reference, &candidate)) {
            fprintf(stderr, "baseinv targeted differential failed pattern=%u\n",
                    pattern);
            return 0;
        }
        if (candidate_rc != 0) {
            poly zero;
            memset(&zero, 0, sizeof zero);
            if (!gt_ntt_equal_canonical(&candidate, &zero)) {
                fprintf(stderr, "baseinv failure did not zero output pattern=%u\n",
                        pattern);
                return 0;
            }
        } else {
            gt_poly_basemul(&product, &input, &candidate);
            for (size_t batch = 0; batch < 12; ++batch)
                for (size_t lane = 0; lane < 16; ++lane)
                    for (size_t degree = 0; degree < 4; ++degree) {
                        const int16_t expected = degree == 0 ? 1 : 0;
                        if (product.coeffs[64 * batch + 16 * degree + lane]
                                != expected) {
                            fprintf(stderr,
                                    "baseinv identity failed pattern=%u batch=%zu lane=%zu degree=%zu\n",
                                    pattern, batch, lane, degree);
                            return 0;
                        }
                    }
        }
    }
    return 1;
}

static int check_serialization(void)
{
    uint8_t raw[NTRUPLUS_POLYBYTES];
    uint8_t encoded[NTRUPLUS_POLYBYTES];
    poly official;
    poly gt;

    for (unsigned value = 0; value < 4096; ++value) {
        for (size_t i = 0; i < NTRUPLUS_N / 2; ++i) {
            raw[3 * i] = (uint8_t)value;
            raw[3 * i + 1] = (uint8_t)((value >> 8) | (value << 4));
            raw[3 * i + 2] = (uint8_t)(value >> 4);
        }
        const int official_rc = poly_frombytes(&official, raw);
        const int gt_rc = gt_poly_frombytes(&gt, raw);
        if (official_rc != gt_rc) {
            fprintf(stderr, "decode return mismatch raw=%u\n", value);
            return 0;
        }
        if (gt_rc == 0) {
            gt_poly_tobytes(encoded, &gt);
            if (memcmp(encoded, raw, sizeof raw) != 0) {
                fprintf(stderr, "GT serialization round-trip raw=%u\n", value);
                return 0;
            }
        } else {
            for (size_t official_component = 0;
                    official_component < 192; ++official_component) {
                const size_t component = gt_official_to_gt[official_component];
                const size_t branch = component / 96;
                const size_t rem = component % 96;
                const size_t k3 = rem / 32;
                const size_t k32 = rem % 32;
                const size_t batch = ((branch * 3 + k3) * 2 + k32 / 16);
                const size_t lane = k32 % 16;
                for (size_t degree = 0; degree < 4; ++degree) {
                    const size_t word = 64 * batch + 16 * degree + lane;
                    if (gt.coeffs[word]
                            != official.coeffs[4 * official_component + degree]) {
                        fprintf(stderr, "malformed decode output mismatch raw=%u\n",
                                value);
                        return 0;
                    }
                }
            }
        }
    }
    return 1;
}

int main(void)
{
    int failures = 0;

    for (unsigned tc = 0; tc < 7 + RANDOM_CASES; ++tc) {
        poly a;
        poly b;
        fill_case(&a, tc);
        fill_case(&b, tc + 3);
        failures += !check_forward_case(&a, tc);
        failures += !check_product_case(&a, &b, tc);
        if (tc == 0 || tc == 1 || tc >= 7)
            failures += !check_baseinv(&a, tc);
    }
    failures += !check_baseinv_failure_patterns();
    failures += !check_serialization();

    printf("scalar-gt-cases=%d failures=%d\n", 7 + RANDOM_CASES, failures);
    return failures == 0 ? 0 : 1;
}
