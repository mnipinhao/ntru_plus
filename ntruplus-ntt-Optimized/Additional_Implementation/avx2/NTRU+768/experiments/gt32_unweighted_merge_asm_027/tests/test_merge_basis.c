#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "inverse_stage1_intrinsic.h"
#include "merge_basis_asm.h"
#include "qbm_intrinsic.h"
#include "quadratic-constants.h"

enum { Q = 3457, CENTER = 1728, WORDS = 768 };

static _Alignas(32) int16_t input_a[WORDS], input_b[WORDS], product[WORDS];
static _Alignas(32) int16_t rows_control[WORDS], rows_candidate[WORDS];
static _Alignas(32) int16_t rows_heterogeneous[WORDS], rows_repaired[WORDS];
static _Alignas(32) int16_t expected[WORDS], got[WORDS];

static __m256i montmul_vector(__m256i x, __m256i mont, __m256i qinv)
{
    const __m256i q = _mm256_set1_epi16(Q);
    __m256i m = _mm256_mullo_epi16(x, qinv);
    __m256i high = _mm256_mulhi_epi16(x, mont);
    return _mm256_sub_epi16(high, _mm256_mulhi_epi16(m, q));
}

static __m256i montmul_scalar(__m256i x, int16_t mont, int16_t qinv)
{
    return montmul_vector(x, _mm256_set1_epi16(mont),
                         _mm256_set1_epi16(qinv));
}

static __m256i center_once(__m256i x)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i center = _mm256_set1_epi16(CENTER);
    const __m256i negative_center = _mm256_set1_epi16(-CENTER);
    __m256i mask = _mm256_cmpgt_epi16(x, center);
    x = _mm256_sub_epi16(x, _mm256_and_si256(mask, q));
    mask = _mm256_cmpgt_epi16(negative_center, x);
    return _mm256_add_epi16(x, _mm256_and_si256(mask, q));
}

static __m256i standard_r2_without_half(__m256i value)
{
    static const uint8_t low_mask[32] __attribute__((aligned(32))) = {
        0,1,2,3,4,5,6,7, 0,1,2,3,4,5,6,7,
        0,1,2,3,4,5,6,7, 0,1,2,3,4,5,6,7,
    };
    static const uint8_t high_mask[32] __attribute__((aligned(32))) = {
        8,9,10,11,12,13,14,15, 8,9,10,11,12,13,14,15,
        8,9,10,11,12,13,14,15, 8,9,10,11,12,13,14,15,
    };
    __m256i plus = _mm256_shuffle_epi8(value,
        _mm256_load_si256((const __m256i *)low_mask));
    __m256i minus = _mm256_shuffle_epi8(value,
        _mm256_load_si256((const __m256i *)high_mask));
    __m256i sum = _mm256_add_epi16(plus, minus);
    __m256i difference = _mm256_sub_epi16(plus, minus);
    __m256i high = montmul_vector(difference,
        _mm256_load_si256((const __m256i *)round4c_inv_beta_vector_mont),
        _mm256_load_si256((const __m256i *)round4c_inv_beta_vector_qinv));
    return _mm256_blend_epi16(sum, high, 0xf0);
}

static void rows_to_coefficients(int16_t out[WORDS], const int16_t rows[WORDS])
{
    for (size_t i3 = 0; i3 < 3; ++i3) {
        for (size_t i16 = 0; i16 < 16; ++i16) {
            size_t vector = 16 * i3 + i16;
            size_t natural = (16 * i3 + 33 * i16) % 48;
            __m256i value = _mm256_load_si256(
                (const __m256i *)(rows + 16 * vector));
            __m256i paired = standard_r2_without_half(value);
            __m256i top0 = _mm256_permute2x128_si256(paired, paired, 0x00);
            __m256i top1 = _mm256_permute2x128_si256(paired, paired, 0x11);
            __m256i difference = _mm256_sub_epi16(top0, top1);
            __m256i scaled_top0 = montmul_scalar(top0,
                round4c_final_merge_mont[0], round4c_final_merge_qinv[0]);
            __m256i high = montmul_scalar(difference,
                round4c_final_merge_mont[1], round4c_final_merge_qinv[1]);
            __m256i low_term = montmul_scalar(difference,
                round4c_final_merge_mont[2], round4c_final_merge_qinv[2]);
            __m128i low = _mm256_castsi256_si128(center_once(
                _mm256_sub_epi16(scaled_top0, low_term)));
            __m128i high128 = _mm256_castsi256_si128(center_once(high));
            _mm_storel_epi64((__m128i *)(out + 4 * natural), low);
            _mm_storel_epi64((__m128i *)(out + 4 * (natural + 48)),
                             _mm_srli_si128(low, 8));
            _mm_storel_epi64((__m128i *)(out + 4 * (natural + 96)), high128);
            _mm_storel_epi64((__m128i *)(out + 4 * (natural + 144)),
                             _mm_srli_si128(high128, 8));
        }
    }
}

static void repair_heterogeneous(int16_t out[WORDS], const int16_t in[WORDS])
{
    for (size_t i16 = 0; i16 < 16; ++i16) {
        for (size_t lane = 0; lane < 16; ++lane) {
            int high = (lane & 2) != 0;
            out[16 * (0 * 16 + i16) + lane] =
                in[16 * ((high ? 2 : 0) * 16 + i16) + lane];
            out[16 * (1 * 16 + i16) + lane] =
                in[16 * ((high ? 0 : 1) * 16 + i16) + lane];
            out[16 * (2 * 16 + i16) + lane] =
                in[16 * ((high ? 1 : 2) * 16 + i16) + lane];
        }
    }
}

static int congruent_quiet(const int16_t *a, const int16_t *b)
{
    for (size_t i = 0; i < WORDS; ++i)
        if (((int)a[i] - b[i]) % Q != 0)
            return 0;
    return 1;
}

static uint64_t random_state = UINT64_C(0x243f6a8885a308d3);
static uint32_t random32(void)
{
    random_state ^= random_state << 13;
    random_state ^= random_state >> 7;
    random_state ^= random_state << 17;
    return (uint32_t)random_state;
}

static int one_trial(size_t trial)
{
    for (size_t i = 0; i < WORDS; ++i) {
        input_a[i] = (int16_t)((int)(random32() % 6913) - 3456);
        input_b[i] = (int16_t)((int)(random32() % 6913) - 3456);
    }
    round4c_qbm_vector_intrinsic(product, input_a, input_b);
    round4c_inverse_full_i1(expected, product);
    qbm_inverse_control_rows_asm(rows_control, product);
    qbm_inverse_repaired_rows_asm(rows_candidate, product);
    qbm_inverse_heterogeneous_rows_asm(rows_heterogeneous, product);
    repair_heterogeneous(rows_repaired, rows_heterogeneous);
    rows_to_coefficients(got, rows_control);
    if (memcmp(got, expected, sizeof got) != 0) {
        fprintf(stderr, "control coefficient mismatch trial=%zu\n", trial);
        return 0;
    }
    /* The emitted candidate is deliberately retained as an executable
     * counterexample to the 026 scale propagation.  A test failure here
     * means the claimed 45-Montgomery + 48-blend graph unexpectedly became
     * correct and the exact-conjugation proof must be revisited. */
    if (congruent_quiet(rows_control, rows_candidate) ||
        congruent_quiet(rows_control, rows_repaired)) {
        fprintf(stderr, "claimed schedule unexpectedly matched trial=%zu\n", trial);
        return 0;
    }
    return 1;
}

int main(void)
{
    for (size_t trial = 0; trial < 1000; ++trial)
        if (!one_trial(trial))
            return 1;
    puts("027: control passes and claimed 026 schedule is rejected in 1000 trials");
    return 0;
}
