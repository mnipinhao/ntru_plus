#include "qbm_intrinsic.h"
#include "transpose_intrinsic.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "quadratic-constants.h"

enum { Q = 3457, CENTER = 1728, R_MOD_Q = 3310 };

void gt_basemul_native_rminus1_c0lazy_asm_avx2(
    int16_t out[768], const int16_t a[768], const int16_t b[768]);

static uint32_t state = 0x47543143u;

static uint32_t random32(void)
{
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

static int modq(int64_t value)
{
    int result = (int)(value % Q);
    return result < 0 ? result + Q : result;
}

static int standard_constant(int16_t mont)
{
    return modq((int64_t)mont * 2775); /* 2775 = R^-1 mod q. */
}

static int check_case(const int16_t quartic_a[ROUND4C_WORDS],
                      const int16_t quartic_b[ROUND4C_WORDS])
{
    int16_t qa[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t qb[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t product0[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t product4[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t product8[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t merged[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t old_a[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t old_b[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t old_product[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t old_vertical[ROUND4C_WORDS] __attribute__((aligned(32)));

    round4c_split_intrinsic(qa, quartic_a);
    round4c_split_intrinsic(qb, quartic_b);
    round4c_qbm_vector_intrinsic(product0, qa, qb);
    round4c_qbm_interleaved4_intrinsic(product4, qa, qb);
    round4c_qbm_interleaved8_intrinsic(product8, qa, qb);
    if (memcmp(product0, product4, sizeof(product0)) != 0 ||
        memcmp(product0, product8, sizeof(product0)) != 0) {
        fprintf(stderr, "QBM scheduling differential failed\n");
        return 1;
    }
    round4c_merge2_intrinsic(merged, product0);
    round4c_vertical_to_soa(old_a, quartic_a);
    round4c_vertical_to_soa(old_b, quartic_b);
    gt_basemul_native_rminus1_c0lazy_asm_avx2(old_product, old_a, old_b);
    round4c_soa_to_vertical(old_vertical, old_product);

    for (size_t vector = 0; vector < 48; ++vector) {
        for (size_t branch = 0; branch < 4; ++branch) {
            const size_t qbase = 16 * vector + 4 * branch;
            const int s = standard_constant(round4c_split_mont[vector][4 * branch]);
            const int alpha = modq((int64_t)s * s);
            int64_t conv[7] = {0};
            for (size_t i = 0; i < 4; ++i)
                for (size_t j = 0; j < 4; ++j)
                    conv[i + j] += (int64_t)quartic_a[qbase + i] * quartic_b[qbase + j];
            for (int degree = 6; degree >= 4; --degree)
                conv[degree - 4] += alpha * conv[degree];
            for (size_t degree = 0; degree < 4; ++degree) {
                const int got = modq((int64_t)merged[qbase + degree] * R_MOD_Q);
                const int want = modq(2 * conv[degree]);
                if (got != want) {
                    fprintf(stderr,
                        "merged QBM mismatch vector=%zu branch=%zu degree=%zu got=%d want=%d\n",
                        vector, branch, degree, got, want);
                    return 1;
                }
                if (modq(merged[qbase + degree]) !=
                    modq(2 * old_vertical[qbase + degree])) {
                    fprintf(stderr,
                        "old/new terminal mismatch vector=%zu branch=%zu degree=%zu\n",
                        vector, branch, degree);
                    return 1;
                }
            }
        }
    }

    /* Each entry supports the alias cases needed by a fused scratch boundary. */
    memcpy(product4, quartic_a, sizeof(product4));
    round4c_split_intrinsic(product4, product4);
    if (memcmp(product4, qa, sizeof(product4)) != 0)
        return 1;
    memcpy(product4, qa, sizeof(product4));
    round4c_qbm_vector_intrinsic(product4, product4, qb);
    if (memcmp(product4, product0, sizeof(product4)) != 0)
        return 1;
    memcpy(product4, qb, sizeof(product4));
    round4c_qbm_vector_intrinsic(product4, qa, product4);
    if (memcmp(product4, product0, sizeof(product4)) != 0)
        return 1;
    memcpy(product4, product0, sizeof(product4));
    round4c_merge2_intrinsic(product4, product4);
    if (memcmp(product4, merged, sizeof(product4)) != 0)
        return 1;
    return 0;
}

int main(void)
{
    int16_t a[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t b[ROUND4C_WORDS] __attribute__((aligned(32)));
    const int16_t patterns[][2] = {
        {0, 0}, {1, -1}, {CENTER, CENTER}, {-CENTER, -CENTER},
        {CENTER, -CENTER}, {-CENTER, CENTER},
    };
    for (size_t pattern = 0; pattern < sizeof(patterns) / sizeof(patterns[0]); ++pattern) {
        for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
            a[i] = patterns[pattern][i & 1];
            b[i] = patterns[pattern][(i + 1) & 1];
        }
        if (check_case(a, b) != 0)
            return 1;
    }
    for (size_t test = 0; test < 1000; ++test) {
        for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
            a[i] = (int16_t)((int)(random32() % Q) - CENTER);
            b[i] = (int16_t)((int)(random32() % Q) - CENTER);
        }
        if (check_case(a, b) != 0)
            return 1;
    }
    puts("intrinsic split/QBM schedules/merge/alias differential: pass");
    return 0;
}
