#include "qbm_intrinsic.h"
#include "inverse_stage1_intrinsic.h"
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

static int powmod(int value, unsigned exponent)
{
    int result = 1;
    while (exponent != 0) {
        if (exponent & 1)
            result = modq((int64_t)result * value);
        value = modq((int64_t)value * value);
        exponent >>= 1;
    }
    return result;
}

static int standard_constant(int16_t mont)
{
    return modq((int64_t)mont * 2775); /* 2775 = R^-1 mod q. */
}

static int centered(int value)
{
    value = modq(value);
    return value > CENTER ? value - Q : value;
}

static void scalar_full_inverse(int16_t out[ROUND4C_WORDS],
                                const int16_t after_ntt16[ROUND4C_WORDS])
{
    int residues[4][4][48];
    const int inv3 = powmod(3, Q - 2);
    const int inverse_omega3 = 722;
    for (size_t branch = 0; branch < 4; ++branch) {
        for (size_t degree = 0; degree < 4; ++degree) {
            for (size_t i3 = 0; i3 < 3; ++i3) {
                for (size_t i16 = 0; i16 < 16; ++i16) {
                    const size_t natural = (16 * i3 + 33 * i16) % 48;
                    int64_t value = 0;
                    for (size_t k3 = 0; k3 < 3; ++k3) {
                        const size_t lane = 4 * branch + degree;
                        value += (int64_t)after_ntt16[
                            16 * (16 * k3 + i16) + lane]
                            * powmod(inverse_omega3, (unsigned)(i3 * k3));
                    }
                    residues[branch][degree][natural] = modq(
                        value * inv3 * powmod(round4c_branch_f[branch],
                                               (unsigned)natural));
                }
            }
        }
    }

    const int inv2 = powmod(2, Q - 2);
    const int inv_delta = powmod(2735 - 723, Q - 2);
    const int inverse_scale = modq((int64_t)R_MOD_Q * inv2);
    for (size_t degree = 0; degree < 4; ++degree) {
        for (size_t n = 0; n < 48; ++n) {
            int top[2][2];
            for (size_t top_index = 0; top_index < 2; ++top_index) {
                const size_t plus = 2 * top_index;
                const size_t minus = plus + 1;
                const int inv2beta = powmod(
                    2 * round4c_branch_beta[plus], Q - 2);
                top[top_index][0] = modq(
                    (residues[plus][degree][n] +
                     residues[minus][degree][n]) * (int64_t)inv2);
                top[top_index][1] = modq(
                    (residues[plus][degree][n] -
                     residues[minus][degree][n]) * (int64_t)inv2beta);
            }
            for (size_t half = 0; half < 2; ++half) {
                const int high = modq(
                    (top[0][half] - top[1][half]) * (int64_t)inv_delta);
                const int low = modq(top[0][half] - (int64_t)2735 * high);
                const size_t n96 = n + 48 * half;
                out[4 * n96 + degree] = (int16_t)centered(
                    modq((int64_t)low * inverse_scale));
                out[4 * (n96 + 96) + degree] = (int16_t)centered(
                    modq((int64_t)high * inverse_scale));
            }
        }
    }
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
    int16_t inverse_i0[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_i1[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_stage1_asm[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_ntt0[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_ntt1[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_full[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_full_i1[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_full_asm[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_full_all_asm[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_finish_rows[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t inverse_full_want[ROUND4C_WORDS] __attribute__((aligned(32)));

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
    round4c_inverse_stage1_i0(inverse_i0, product0);
    round4c_inverse_stage1_i1(inverse_i1, product0);
    if (memcmp(inverse_i0, inverse_i1, sizeof(inverse_i0)) != 0) {
        fprintf(stderr, "inverse I0/I1 stage-1 differential failed\n");
        return 1;
    }
    round4c_inverse_stage1_asm(inverse_stage1_asm, product0);
    if (memcmp(inverse_i0, inverse_stage1_asm, sizeof(inverse_i0)) != 0) {
        fprintf(stderr, "inverse stage-1 asm differential failed\n");
        return 1;
    }
    for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
        if (inverse_i1[i] < -CENTER || inverse_i1[i] > CENTER) {
            fprintf(stderr, "inverse stage-1 range failed i=%zu value=%d\n",
                    i, inverse_i1[i]);
            return 1;
        }
    }
    round4c_inverse_ntt16_i0(inverse_ntt0, product0);
    round4c_inverse_ntt16_i1(inverse_ntt1, product0);
    if (memcmp(inverse_ntt0, inverse_ntt1, sizeof(inverse_ntt0)) != 0) {
        fprintf(stderr, "inverse I0/I1 full NTT16 differential failed\n");
        return 1;
    }
    const int inv16 = powmod(16, Q - 2);
    for (size_t k3 = 0; k3 < 3; ++k3) {
        for (size_t output_index = 0; output_index < 16; ++output_index) {
            for (size_t lane = 0; lane < 16; ++lane) {
                int64_t want = 0;
                for (size_t frequency = 0; frequency < 16; ++frequency) {
                    want += (int64_t)merged[16 * (16 * k3 + frequency) + lane]
                        * powmod(3418, (unsigned)(output_index * frequency));
                }
                want = modq(want * inv16);
                const int got = modq(inverse_ntt1[
                    16 * (16 * k3 + output_index) + lane]);
                if (got != want) {
                    fprintf(stderr,
                        "inverse NTT16 mismatch k3=%zu n=%zu lane=%zu got=%d want=%d\n",
                        k3, output_index, lane, got, (int)want);
                    return 1;
                }
            }
        }
    }
    round4c_inverse_full_i0(inverse_full, product0);
    round4c_inverse_full_i1(inverse_full_i1, product0);
    if (memcmp(inverse_full, inverse_full_i1, sizeof(inverse_full)) != 0) {
        fprintf(stderr, "full inverse I0/I1 differential failed\n");
        return 1;
    }
    round4c_inverse_full_i0_ntt16_asm(inverse_full_asm, product0);
    if (memcmp(inverse_full, inverse_full_asm, sizeof(inverse_full)) != 0) {
        fprintf(stderr, "full inverse NTT16 asm differential failed\n");
        return 1;
    }
    memcpy(inverse_finish_rows, inverse_i0, sizeof(inverse_finish_rows));
    round4c_inverse_finish_asm(inverse_full_all_asm, inverse_finish_rows);
    if (memcmp(inverse_full, inverse_full_all_asm,
               sizeof(inverse_full)) != 0) {
        for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
            if (inverse_full[i] != inverse_full_all_asm[i]) {
                fprintf(stderr,
                        "inverse finish asm mismatch i=%zu got=%d want=%d\n",
                        i, inverse_full_all_asm[i], inverse_full[i]);
                break;
            }
        }
        return 1;
    }
    round4c_inverse_full_asm(inverse_full_all_asm, product0);
    if (memcmp(inverse_full, inverse_full_all_asm,
               sizeof(inverse_full)) != 0) {
        fprintf(stderr, "full inverse asm differential failed\n");
        return 1;
    }
    round4c_inverse_full_i0_finish_asm(inverse_full_all_asm, product0);
    if (memcmp(inverse_full, inverse_full_all_asm,
               sizeof(inverse_full)) != 0) {
        fprintf(stderr, "full inverse asm-tail differential failed\n");
        return 1;
    }
    scalar_full_inverse(inverse_full_want, inverse_ntt0);
    if (memcmp(inverse_full, inverse_full_want, sizeof(inverse_full)) != 0) {
        for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
            if (inverse_full[i] != inverse_full_want[i]) {
                fprintf(stderr,
                        "full inverse mismatch i=%zu got=%d want=%d\n",
                        i, inverse_full[i], inverse_full_want[i]);
                break;
            }
        }
        return 1;
    }
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
    memcpy(product4, product0, sizeof(product4));
    round4c_inverse_stage1_i1(product4, product4);
    if (memcmp(product4, inverse_i1, sizeof(product4)) != 0)
        return 1;
    memcpy(product4, product0, sizeof(product4));
    round4c_inverse_ntt16_i1(product4, product4);
    if (memcmp(product4, inverse_ntt1, sizeof(product4)) != 0)
        return 1;
    memcpy(product4, product0, sizeof(product4));
    round4c_inverse_full_i0(product4, product4);
    if (memcmp(product4, inverse_full, sizeof(product4)) != 0)
        return 1;
    memcpy(product4, product0, sizeof(product4));
    round4c_inverse_full_asm(product4, product4);
    if (memcmp(product4, inverse_full, sizeof(product4)) != 0)
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
    /* N4 removes the terminal forward checkpoint.  Prove that QBM itself can
     * absorb the resulting +/-16257 representatives: reduce an equivalent
     * canonical input pair and require an identical centered product, then
     * carry both through the unchanged inverse. */
    int16_t wide_product[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t canonical_product[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t wide_inverse[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t canonical_inverse[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t fused_stage1[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t canonical_stage1[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t qbm4_product[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t plain_wide_product[ROUND4C_WORDS] __attribute__((aligned(32)));
    for (size_t test = 0; test < 256; ++test) {
        int16_t canonical_a[ROUND4C_WORDS] __attribute__((aligned(32)));
        int16_t canonical_b[ROUND4C_WORDS] __attribute__((aligned(32)));
        for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
            a[i] = (int16_t)((int)(random32() % 32515) - 16257);
            b[i] = (int16_t)((int)(random32() % 32515) - 16257);
            canonical_a[i] = (int16_t)centered(a[i]);
            canonical_b[i] = (int16_t)centered(b[i]);
        }
        round4c_qbm_wide_centered_intrinsic(wide_product, a, b);
        round4c_qbm_wide_centered_intrinsic(canonical_product,
                                             canonical_a, canonical_b);
        round4c_qbm_vector_intrinsic(plain_wide_product, a, b);
        round4c_qbm_wide4_asm(qbm4_product, a, b);
        if (memcmp(plain_wide_product, qbm4_product,
                   sizeof(plain_wide_product)) != 0) {
            fprintf(stderr, "four-way QBM asm mismatch test=%zu\n", test);
            return 1;
        }
        round4c_qbm_wide4_centered_asm(qbm4_product, a, b);
        if (memcmp(wide_product, qbm4_product, sizeof(wide_product)) != 0) {
            fprintf(stderr, "four-way centered QBM asm mismatch test=%zu\n", test);
            return 1;
        }
        if (memcmp(wide_product, canonical_product,
                   sizeof(wide_product)) != 0) {
            fprintf(stderr, "wide-QBM representative mismatch test=%zu\n", test);
            return 1;
        }
        for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
            if (wide_product[i] < -CENTER || wide_product[i] > CENTER) {
                fprintf(stderr, "wide-QBM range mismatch test=%zu i=%zu value=%d\n",
                        test, i, wide_product[i]);
                return 1;
            }
        }
        round4c_inverse_full_i0(wide_inverse, wide_product);
        round4c_inverse_full_i0(canonical_inverse, canonical_product);
        if (memcmp(wide_inverse, canonical_inverse,
                   sizeof(wide_inverse)) != 0) {
            fprintf(stderr, "wide-QBM inverse mismatch test=%zu\n", test);
            return 1;
        }
        round4c_inverse_stage1_wide_asm(fused_stage1, plain_wide_product);
        round4c_inverse_stage1_i0(canonical_stage1, canonical_product);
        if (memcmp(fused_stage1, canonical_stage1,
                   sizeof(fused_stage1)) != 0) {
            fprintf(stderr, "wide R^-1 stage1 asm mismatch test=%zu\n", test);
            return 1;
        }
        round4c_inverse_full_wide_asm(wide_inverse, plain_wide_product);
        if (memcmp(wide_inverse, canonical_inverse,
                   sizeof(wide_inverse)) != 0) {
            fprintf(stderr, "wide R^-1 full inverse asm mismatch test=%zu\n",
                    test);
            return 1;
        }
        round4c_inverse_full_wide_hybrid(wide_inverse, plain_wide_product);
        if (memcmp(wide_inverse, canonical_inverse,
                   sizeof(wide_inverse)) != 0) {
            fprintf(stderr, "wide R^-1 inverse hybrid mismatch test=%zu\n",
                    test);
            return 1;
        }
        round4c_qbm_inverse_full_fused(wide_inverse, a, b);
        if (memcmp(wide_inverse, canonical_inverse,
                   sizeof(wide_inverse)) != 0) {
            fprintf(stderr, "fused QBM/full inverse mismatch test=%zu\n", test);
            return 1;
        }
        round4c_qbm_inverse_stage1_fused_asm(fused_stage1, a, b);
        round4c_inverse_stage1_i0(canonical_stage1, canonical_product);
        if (memcmp(fused_stage1, canonical_stage1,
                   sizeof(fused_stage1)) != 0) {
            for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
                if (fused_stage1[i] != canonical_stage1[i]) {
                    fprintf(stderr,
                            "fused QBM/stage1 mismatch test=%zu i=%zu got=%d want=%d\n",
                            test, i, fused_stage1[i], canonical_stage1[i]);
                    break;
                }
            }
            return 1;
        }
        if (test == 0) {
            memcpy(wide_inverse, a, sizeof(wide_inverse));
            round4c_qbm_inverse_stage1_fused(wide_inverse, wide_inverse, b);
            if (memcmp(wide_inverse, fused_stage1, sizeof(wide_inverse)) != 0)
                return 1;
            memcpy(wide_inverse, b, sizeof(wide_inverse));
            round4c_qbm_inverse_stage1_fused(wide_inverse, a, wide_inverse);
            if (memcmp(wide_inverse, fused_stage1, sizeof(wide_inverse)) != 0)
                return 1;
        }
        memcpy(wide_inverse, fused_stage1, sizeof(wide_inverse));
        memcpy(canonical_inverse, fused_stage1, sizeof(canonical_inverse));
        round4c_inverse_ntt16_layers_asm(wide_inverse);
        round4c_inverse_ntt16_layers_reference(canonical_inverse);
        if (memcmp(wide_inverse, canonical_inverse,
                   sizeof(wide_inverse)) != 0) {
            for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
                if (wide_inverse[i] != canonical_inverse[i]) {
                    fprintf(stderr,
                            "inverse NTT16 asm mismatch test=%zu i=%zu got=%d want=%d\n",
                            test, i, wide_inverse[i], canonical_inverse[i]);
                    break;
                }
            }
            return 1;
        }
    }
    puts("intrinsic split/QBM/merge/full-inverse/alias/wide-QBM differential: pass");
    return 0;
}
