#include "inverse_stage1_intrinsic.h"

#include <immintrin.h>
#include <stddef.h>
#include <string.h>

#include "qbm_intrinsic.h"
#include "quadratic-constants.h"

enum { Q = 3457, CENTER = 1728 };

static const uint8_t plus_dup_bytes[32] __attribute__((aligned(32))) = {
    0,1,2,3,0,1,2,3, 8,9,10,11,8,9,10,11,
    0,1,2,3,0,1,2,3, 8,9,10,11,8,9,10,11,
};
static const uint8_t minus_dup_bytes[32] __attribute__((aligned(32))) = {
    4,5,6,7,4,5,6,7, 12,13,14,15,12,13,14,15,
    4,5,6,7,4,5,6,7, 12,13,14,15,12,13,14,15,
};
static const uint8_t low64_dup_bytes[32] __attribute__((aligned(32))) = {
    0,1,2,3,4,5,6,7, 0,1,2,3,4,5,6,7,
    0,1,2,3,4,5,6,7, 0,1,2,3,4,5,6,7,
};
static const uint8_t high64_dup_bytes[32] __attribute__((aligned(32))) = {
    8,9,10,11,12,13,14,15, 8,9,10,11,12,13,14,15,
    8,9,10,11,12,13,14,15, 8,9,10,11,12,13,14,15,
};

static int16_t merged_scratch[768] __attribute__((aligned(32)));
static int16_t quadratic_alias_scratch[768] __attribute__((aligned(32)));
static int16_t full_inverse_rows[768] __attribute__((aligned(32)));
static const uint8_t bitreverse3[8] = {0, 4, 2, 6, 1, 5, 3, 7};

static inline __m256i montmul_vector(__m256i x, __m256i mont, __m256i qinv)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i m = _mm256_mullo_epi16(x, qinv);
    const __m256i high = _mm256_mulhi_epi16(x, mont);
    return _mm256_sub_epi16(high, _mm256_mulhi_epi16(m, q));
}

static inline __m256i montmul16(__m256i x, const int16_t mont[16],
                                const int16_t qinv[16])
{
    return montmul_vector(
        x, _mm256_load_si256((const __m256i *)mont),
        _mm256_load_si256((const __m256i *)qinv));
}

static inline __m256i montmul_scalar(__m256i x, int16_t mont, int16_t qinv)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i m = _mm256_mullo_epi16(x, _mm256_set1_epi16(qinv));
    const __m256i high = _mm256_mulhi_epi16(x, _mm256_set1_epi16(mont));
    return _mm256_sub_epi16(high, _mm256_mulhi_epi16(m, q));
}

static inline __m256i merge2_one(__m256i x, size_t vector)
{
    const __m256i plus_mask = _mm256_load_si256((const __m256i *)plus_dup_bytes);
    const __m256i minus_mask = _mm256_load_si256((const __m256i *)minus_dup_bytes);
    const __m256i plus = _mm256_shuffle_epi8(x, plus_mask);
    const __m256i minus = _mm256_shuffle_epi8(x, minus_mask);
    const __m256i sum = _mm256_add_epi16(plus, minus);
    const __m256i difference = _mm256_sub_epi16(plus, minus);
    const __m256i high = montmul16(
        difference, round4c_merge_mont[vector], round4c_merge_qinv[vector]);
    return _mm256_blend_epi16(sum, high, 0xcc);
}

static inline __m256i center_twice(__m256i x)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i center = _mm256_set1_epi16(CENTER);
    const __m256i negative_center = _mm256_set1_epi16(-CENTER);
    for (size_t iteration = 0; iteration < 2; ++iteration) {
        __m256i mask = _mm256_cmpgt_epi16(x, center);
        x = _mm256_sub_epi16(x, _mm256_and_si256(mask, q));
        mask = _mm256_cmpgt_epi16(negative_center, x);
        x = _mm256_add_epi16(x, _mm256_and_si256(mask, q));
    }
    return x;
}

static inline __m256i center_once(__m256i x)
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i center = _mm256_set1_epi16(CENTER);
    const __m256i negative_center = _mm256_set1_epi16(-CENTER);
    __m256i mask = _mm256_cmpgt_epi16(x, center);
    x = _mm256_sub_epi16(x, _mm256_and_si256(mask, q));
    mask = _mm256_cmpgt_epi16(negative_center, x);
    return _mm256_add_epi16(x, _mm256_and_si256(mask, q));
}

static inline void stage1_from_quartic(int16_t out[768], const int16_t in[768])
{
    for (size_t k3 = 0; k3 < 3; ++k3) {
        const size_t base = 16 * 16 * k3;
        for (size_t position = 0; position < 8; ++position) {
            const size_t k16 = bitreverse3[position];
            const __m256i low = _mm256_loadu_si256(
                (const __m256i *)(in + base + 16 * k16));
            const __m256i high = _mm256_loadu_si256(
                (const __m256i *)(in + base + 16 * (k16 + 8)));
            /* CT stage-1 consumes bit-reversed frequency pairs (k,k+8)
             * and writes adjacent size-2 blocks for the remaining stages. */
            _mm256_storeu_si256((__m256i *)(out + base + 16 * (2 * position)),
                center_twice(_mm256_add_epi16(low, high)));
            _mm256_storeu_si256((__m256i *)(out + base + 16 * (2 * position + 1)),
                center_twice(_mm256_sub_epi16(low, high)));
        }
    }
}

void round4c_inverse_stage1_i0(int16_t out[768], const int16_t quadratic[768])
{
    round4c_merge2_intrinsic(merged_scratch, quadratic);
    stage1_from_quartic(out, merged_scratch);
}

void round4c_inverse_stage1_i1(int16_t out[768], const int16_t quadratic[768])
{
    if (out == quadratic) {
        memcpy(quadratic_alias_scratch, quadratic, sizeof(quadratic_alias_scratch));
        quadratic = quadratic_alias_scratch;
    }
    for (size_t k3 = 0; k3 < 3; ++k3) {
        const size_t batch = 16 * k3;
        const size_t base = 16 * batch;
        for (size_t position = 0; position < 8; ++position) {
            const size_t k16 = bitreverse3[position];
            const size_t low_vector = batch + k16;
            const size_t high_vector = low_vector + 8;
            const __m256i low = merge2_one(_mm256_loadu_si256(
                (const __m256i *)(quadratic + 16 * low_vector)), low_vector);
            const __m256i high = merge2_one(_mm256_loadu_si256(
                (const __m256i *)(quadratic + 16 * high_vector)), high_vector);
            _mm256_storeu_si256((__m256i *)(out + base + 16 * (2 * position)),
                center_twice(_mm256_add_epi16(low, high)));
            _mm256_storeu_si256((__m256i *)(out + base + 16 * (2 * position + 1)),
                center_twice(_mm256_sub_epi16(low, high)));
        }
    }
}

static void inverse_ntt16_tail(int16_t values[768])
{
    size_t twiddle_offset = 0;
    for (size_t length = 4; length <= 16; length *= 2) {
        const size_t half = length / 2;
        for (size_t k3 = 0; k3 < 3; ++k3) {
            const size_t batch = 16 * k3;
            for (size_t start = 0; start < 16; start += length) {
                for (size_t index = 0; index < half; ++index) {
                    const size_t low_vector = batch + start + index;
                    const size_t high_vector = low_vector + half;
                    const __m256i low = _mm256_loadu_si256(
                        (const __m256i *)(values + 16 * low_vector));
                    __m256i high = _mm256_loadu_si256(
                        (const __m256i *)(values + 16 * high_vector));
                    high = montmul_scalar(
                        high,
                        round4c_inv16_twiddle_mont[twiddle_offset + index],
                        round4c_inv16_twiddle_qinv[twiddle_offset + index]);
                    _mm256_storeu_si256((__m256i *)(values + 16 * low_vector),
                        center_once(_mm256_add_epi16(low, high)));
                    _mm256_storeu_si256((__m256i *)(values + 16 * high_vector),
                        center_once(_mm256_sub_epi16(low, high)));
                }
            }
        }
        twiddle_offset += half;
    }
    for (size_t vector = 0; vector < 48; ++vector) {
        const __m256i x = _mm256_loadu_si256(
            (const __m256i *)(values + 16 * vector));
        _mm256_storeu_si256((__m256i *)(values + 16 * vector),
            center_once(montmul_scalar(x, round4c_inv16_norm_mont,
                                       round4c_inv16_norm_qinv)));
    }
}

void round4c_inverse_ntt16_i0(int16_t out[768], const int16_t quadratic[768])
{
    round4c_inverse_stage1_i0(out, quadratic);
    inverse_ntt16_tail(out);
}

void round4c_inverse_ntt16_i1(int16_t out[768], const int16_t quadratic[768])
{
    round4c_inverse_stage1_i1(out, quadratic);
    inverse_ntt16_tail(out);
}

static void inverse_dft3_postweight(int16_t rows[768])
{
    for (size_t i16 = 0; i16 < 16; ++i16) {
        const __m256i y0 = _mm256_load_si256(
            (const __m256i *)(rows + 16 * i16));
        const __m256i y1 = _mm256_load_si256(
            (const __m256i *)(rows + 16 * (16 + i16)));
        const __m256i y2 = _mm256_load_si256(
            (const __m256i *)(rows + 16 * (32 + i16)));
        const __m256i product = montmul_scalar(
            _mm256_sub_epi16(y2, y1), round4c_inv3_omega_mont,
            round4c_inv3_omega_qinv);
        __m256i output[3];
        output[0] = _mm256_add_epi16(_mm256_add_epi16(y0, y1), y2);
        output[1] = _mm256_add_epi16(_mm256_sub_epi16(y0, y1), product);
        output[2] = _mm256_sub_epi16(_mm256_sub_epi16(y0, y2), product);
        for (size_t i3 = 0; i3 < 3; ++i3) {
            const size_t vector = 16 * i3 + i16;
            output[i3] = montmul16(
                output[i3], round4c_inv48_postweight_mont[vector],
                round4c_inv48_postweight_qinv[vector]);
            _mm256_store_si256((__m256i *)(rows + 16 * vector),
                               center_once(output[i3]));
        }
    }
}

static inline __m256i standard_r2_without_half(__m256i value)
{
    const __m256i low_mask = _mm256_load_si256(
        (const __m256i *)low64_dup_bytes);
    const __m256i high_mask = _mm256_load_si256(
        (const __m256i *)high64_dup_bytes);
    const __m256i plus = _mm256_shuffle_epi8(value, low_mask);
    const __m256i minus = _mm256_shuffle_epi8(value, high_mask);
    const __m256i sum = _mm256_add_epi16(plus, minus);
    const __m256i difference = _mm256_sub_epi16(plus, minus);
    const __m256i inverse_beta = _mm256_set_m128i(
        _mm_set1_epi16(round4c_inv_beta_mont[1]),
        _mm_set1_epi16(round4c_inv_beta_mont[0]));
    const __m256i inverse_beta_qinv = _mm256_set_m128i(
        _mm_set1_epi16(round4c_inv_beta_qinv[1]),
        _mm_set1_epi16(round4c_inv_beta_qinv[0]));
    const __m256i high = montmul_vector(difference, inverse_beta,
                                       inverse_beta_qinv);
    return _mm256_blend_epi16(sum, high, 0xf0);
}

static void inverse_branch_merge_store(int16_t out[768],
                                       const int16_t rows[768])
{
    for (size_t i3 = 0; i3 < 3; ++i3) {
        for (size_t i16 = 0; i16 < 16; ++i16) {
            const size_t vector = 16 * i3 + i16;
            const size_t natural = (16 * i3 + 33 * i16) % 48;
            const __m256i paired = standard_r2_without_half(
                _mm256_load_si256((const __m256i *)(rows + 16 * vector)));
            const __m256i top0 = _mm256_permute2x128_si256(paired, paired, 0x00);
            const __m256i top1 = _mm256_permute2x128_si256(paired, paired, 0x11);
            const __m256i difference = _mm256_sub_epi16(top0, top1);
            const __m256i scaled_top0 = montmul_scalar(
                top0, round4c_final_merge_mont[0],
                round4c_final_merge_qinv[0]);
            const __m256i high = montmul_scalar(
                difference, round4c_final_merge_mont[1],
                round4c_final_merge_qinv[1]);
            const __m256i low_term = montmul_scalar(
                difference, round4c_final_merge_mont[2],
                round4c_final_merge_qinv[2]);
            const __m128i low = _mm256_castsi256_si128(center_once(
                _mm256_sub_epi16(scaled_top0, low_term)));
            const __m128i high128 = _mm256_castsi256_si128(center_once(high));
            _mm_storel_epi64((__m128i *)(out + 4 * natural), low);
            _mm_storel_epi64((__m128i *)(out + 4 * (natural + 48)),
                             _mm_srli_si128(low, 8));
            _mm_storel_epi64((__m128i *)(out + 4 * (natural + 96)), high128);
            _mm_storel_epi64((__m128i *)(out + 4 * (natural + 144)),
                             _mm_srli_si128(high128, 8));
        }
    }
}

void round4c_inverse_full_i0(int16_t out[768], const int16_t quadratic[768])
{
    round4c_inverse_ntt16_i0(full_inverse_rows, quadratic);
    inverse_dft3_postweight(full_inverse_rows);
    inverse_branch_merge_store(out, full_inverse_rows);
}
