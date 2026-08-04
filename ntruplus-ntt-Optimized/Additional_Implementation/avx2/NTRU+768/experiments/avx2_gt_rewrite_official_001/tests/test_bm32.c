#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt_backend.h"
#include "gt_schoolbook.h"

static uint64_t rng_state = UINT64_C(0x3c6ef372fe94f82b);

static uint32_t prng32(void)
{
    uint64_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    rng_state = x;
    return (uint32_t)(x >> 16);
}

static int check_reducer(void)
{
    static const int32_t edges[] = {
        -INT32_MAX, -1720922256, -3458, -3457, -3456, -1729,
        -1728, -1, 0, 1, 1728, 1729, 3456, 3457, 3458,
        1720922256, INT32_MAX,
    };
    int32_t input[8];
    int16_t output[8];

    for (size_t base = 0; base < sizeof edges / sizeof edges[0]; base += 8) {
        for (size_t lane = 0; lane < 8; ++lane)
            input[lane] = edges[(base + lane) % (sizeof edges / sizeof edges[0])];
        gt_avx2_reduce32_test(output, input);
        for (size_t lane = 0; lane < 8; ++lane)
            if (output[lane] != gt_centered_q(input[lane])) {
                fprintf(stderr, "reducer edge failed x=%d got=%d want=%d\n",
                        input[lane], output[lane], gt_centered_q(input[lane]));
                return 0;
            }
    }

    for (unsigned round = 0; round < 125000; ++round) {
        for (size_t lane = 0; lane < 8; ++lane) {
            const uint32_t magnitude = prng32() & UINT32_C(0x7fffffff);
            input[lane] = (prng32() & 1U)
                ? (int32_t)magnitude : -(int32_t)magnitude;
        }
        gt_avx2_reduce32_test(output, input);
        for (size_t lane = 0; lane < 8; ++lane)
            if (output[lane] != gt_centered_q(input[lane])) {
                fprintf(stderr, "reducer random failed x=%d got=%d want=%d\n",
                        input[lane], output[lane], gt_centered_q(input[lane]));
                return 0;
            }
    }
    return 1;
}

static void fill_bound_pattern(poly *a, poly *b, int bound, unsigned pattern)
{
    const int maximum = bound - 1;
    for (size_t i = 0; i < NTRUPLUS_N; ++i) {
        switch (pattern) {
        case 0:
            a->coeffs[i] = (int16_t)maximum;
            b->coeffs[i] = (int16_t)maximum;
            break;
        case 1:
            a->coeffs[i] = (int16_t)((i & 1U) ? maximum : -maximum);
            b->coeffs[i] = (int16_t)((i & 2U) ? -maximum : maximum);
            break;
        case 2:
            a->coeffs[i] = (int16_t)((i % 4U == 3U) ? maximum : -maximum);
            b->coeffs[i] = (int16_t)((i % 4U == 0U) ? -maximum : maximum);
            break;
        default:
            a->coeffs[i] = (int16_t)((int)(prng32() % (unsigned)(2 * bound - 1))
                                     - maximum);
            b->coeffs[i] = (int16_t)((int)(prng32() % (unsigned)(2 * bound - 1))
                                     - maximum);
            break;
        }
    }
}

static int check_bound(int multiple)
{
    const int bound = multiple * NTRUPLUS_Q;
    for (unsigned pattern = 0; pattern < 3 + 200; ++pattern) {
        poly a;
        poly b;
        poly reference;
        poly avx2;
        poly bm_b;
        fill_bound_pattern(&a, &b, bound, pattern);
        gt_ref_poly_basemul(&reference, &a, &b);
        gt_poly_basemul(&avx2, &a, &b);
        if (memcmp(&reference, &avx2, sizeof reference) != 0) {
            fprintf(stderr, "BM-A mismatch bound=%dq pattern=%u\n",
                    multiple, pattern);
            return 0;
        }
        if (multiple == 3) {
            gt_poly_basemul_bm_b(&bm_b, &a, &b);
            if (memcmp(&reference, &bm_b, sizeof reference) != 0) {
                fprintf(stderr, "BM-B mismatch bound=3q pattern=%u\n", pattern);
                return 0;
            }
        }
        for (size_t i = 0; i < NTRUPLUS_N; ++i)
            if (avx2.coeffs[i] < -1728 || avx2.coeffs[i] > 1728) {
                fprintf(stderr, "BM-A output range bound=%dq pattern=%u i=%zu value=%d\n",
                        multiple, pattern, i, avx2.coeffs[i]);
                return 0;
            }
        /* Official supports a==b with a distinct output, but not r==a/r==b. */
        gt_ref_poly_basemul(&reference, &a, &a);
        gt_poly_basemul(&avx2, &a, &a);
        if (memcmp(&avx2, &reference, sizeof avx2) != 0)
            return 0;
    }
    return 1;
}

int main(void)
{
    int failures = !check_reducer();
    for (int multiple = 3; multiple <= 6; ++multiple)
        failures += !check_bound(multiple);
    printf("bm32-reducer-vectors=1000000 BM-A-bounds=3q,4q,5q,6q BM-B-bound=3q failures=%d\n",
           failures);
    return failures == 0 ? 0 : 1;
}
