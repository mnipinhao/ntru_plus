#include "qbm_intrinsic.h"

#include <immintrin.h>
#include <stddef.h>

#include "quadratic-constants.h"

enum { Q = 3457, QINV = 12929 };

static const uint8_t low_dup_bytes[32] __attribute__((aligned(32))) = {
    0,1,2,3,0,1,2,3, 8,9,10,11,8,9,10,11,
    0,1,2,3,0,1,2,3, 8,9,10,11,8,9,10,11,
};
static const uint8_t high_dup_bytes[32] __attribute__((aligned(32))) = {
    4,5,6,7,4,5,6,7, 12,13,14,15,12,13,14,15,
    4,5,6,7,4,5,6,7, 12,13,14,15,12,13,14,15,
};
static const uint8_t swap_pair_bytes[32] __attribute__((aligned(32))) = {
    2,3,0,1, 6,7,4,5, 10,11,8,9, 14,15,12,13,
    2,3,0,1, 6,7,4,5, 10,11,8,9, 14,15,12,13,
};
static const uint8_t interleave_bytes[32] __attribute__((aligned(32))) = {
    0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15,
    0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15,
};

static inline __m256i montmul16(__m256i x, const int16_t mont[16],
                                const int16_t qinv[16])
{
    const __m256i q = _mm256_set1_epi16(Q);
    const __m256i m = _mm256_mullo_epi16(
        x, _mm256_load_si256((const __m256i *)qinv));
    const __m256i high = _mm256_mulhi_epi16(
        x, _mm256_load_si256((const __m256i *)mont));
    const __m256i correction = _mm256_mulhi_epi16(m, q);
    return _mm256_sub_epi16(high, correction);
}

static inline __m256i montreduce32(__m256i x)
{
    const __m256i qinv = _mm256_set1_epi16(QINV);
    const __m256i lowmask = _mm256_set1_epi32(0x0000ffff);
    const __m256i qpair = _mm256_set1_epi32(Q);
    __m256i m = _mm256_mullo_epi16(x, qinv);
    m = _mm256_and_si256(m, lowmask);
    const __m256i mq = _mm256_madd_epi16(m, qpair);
    return _mm256_srai_epi32(_mm256_sub_epi32(x, mq), 16);
}

static inline __m256i pack_pairs(__m256i c0, __m256i c1)
{
    const __m256i mask = _mm256_load_si256((const __m256i *)interleave_bytes);
    return _mm256_shuffle_epi8(_mm256_packs_epi32(c0, c1), mask);
}

static inline __m256i qbm_one(__m256i a, __m256i b, size_t vector)
{
    const __m256i swap = _mm256_load_si256((const __m256i *)swap_pair_bytes);
    const __m256i weighted = montmul16(
        b, round4c_weight_mont[vector], round4c_weight_qinv[vector]);
    const __m256i c0 = _mm256_madd_epi16(a, weighted);
    const __m256i c1 = _mm256_madd_epi16(a, _mm256_shuffle_epi8(b, swap));
    return pack_pairs(montreduce32(c0), montreduce32(c1));
}

void round4c_split_intrinsic(int16_t out[ROUND4C_WORDS],
                             const int16_t in[ROUND4C_WORDS])
{
    const __m256i low_mask = _mm256_load_si256((const __m256i *)low_dup_bytes);
    const __m256i high_mask = _mm256_load_si256((const __m256i *)high_dup_bytes);
    for (size_t vector = 0; vector < 48; ++vector) {
        const __m256i x = _mm256_loadu_si256((const __m256i *)(in + 16 * vector));
        const __m256i low = _mm256_shuffle_epi8(x, low_mask);
        const __m256i high = _mm256_shuffle_epi8(x, high_mask);
        const __m256i weighted = montmul16(
            high, round4c_split_mont[vector], round4c_split_qinv[vector]);
        _mm256_storeu_si256((__m256i *)(out + 16 * vector),
                            _mm256_add_epi16(low, weighted));
    }
}

void round4c_qbm_vector_intrinsic(int16_t out[ROUND4C_WORDS],
                                  const int16_t a[ROUND4C_WORDS],
                                  const int16_t b[ROUND4C_WORDS])
{
    for (size_t vector = 0; vector < 48; ++vector) {
        const __m256i av = _mm256_loadu_si256((const __m256i *)(a + 16 * vector));
        const __m256i bv = _mm256_loadu_si256((const __m256i *)(b + 16 * vector));
        _mm256_storeu_si256((__m256i *)(out + 16 * vector), qbm_one(av, bv, vector));
    }
}

static inline void qbm_interleaved(int16_t *out, const int16_t *a,
                                   const int16_t *b, size_t width)
{
    for (size_t base = 0; base < 48; base += width) {
        __m256i av[8], bv[8], c1[8];
        const __m256i swap = _mm256_load_si256((const __m256i *)swap_pair_bytes);
        for (size_t lane = 0; lane < width; ++lane) {
            av[lane] = _mm256_loadu_si256((const __m256i *)(a + 16 * (base + lane)));
            bv[lane] = _mm256_loadu_si256((const __m256i *)(b + 16 * (base + lane)));
            c1[lane] = _mm256_madd_epi16(
                av[lane], _mm256_shuffle_epi8(bv[lane], swap));
        }
        for (size_t lane = 0; lane < width; ++lane) {
            const size_t vector = base + lane;
            const __m256i weighted = montmul16(
                bv[lane], round4c_weight_mont[vector],
                round4c_weight_qinv[vector]);
            const __m256i c0 = _mm256_madd_epi16(av[lane], weighted);
            _mm256_storeu_si256((__m256i *)(out + 16 * vector),
                pack_pairs(montreduce32(c0), montreduce32(c1[lane])));
        }
    }
}

void round4c_qbm_interleaved4_intrinsic(int16_t out[ROUND4C_WORDS],
                                        const int16_t a[ROUND4C_WORDS],
                                        const int16_t b[ROUND4C_WORDS])
{
    qbm_interleaved(out, a, b, 4);
}

void round4c_qbm_interleaved8_intrinsic(int16_t out[ROUND4C_WORDS],
                                        const int16_t a[ROUND4C_WORDS],
                                        const int16_t b[ROUND4C_WORDS])
{
    qbm_interleaved(out, a, b, 8);
}

void round4c_merge2_intrinsic(int16_t out[ROUND4C_WORDS],
                              const int16_t in[ROUND4C_WORDS])
{
    const __m256i plus_mask = _mm256_load_si256((const __m256i *)low_dup_bytes);
    const __m256i minus_mask = _mm256_load_si256((const __m256i *)high_dup_bytes);
    for (size_t vector = 0; vector < 48; ++vector) {
        const __m256i x = _mm256_loadu_si256((const __m256i *)(in + 16 * vector));
        const __m256i plus = _mm256_shuffle_epi8(x, plus_mask);
        const __m256i minus = _mm256_shuffle_epi8(x, minus_mask);
        const __m256i sum = _mm256_add_epi16(plus, minus);
        const __m256i difference = _mm256_sub_epi16(plus, minus);
        const __m256i high = montmul16(
            difference, round4c_merge_mont[vector],
            round4c_merge_qinv[vector]);
        _mm256_storeu_si256((__m256i *)(out + 16 * vector),
                            _mm256_blend_epi16(sum, high, 0xcc));
    }
}
