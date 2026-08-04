#ifndef GT_AVX2_ARITH_H
#define GT_AVX2_ARITH_H

#include <immintrin.h>

#include "params.h"

enum {
    GT_RECIP_Q32 = 1242397,
    GT_CENTER = 1728,
};

/* Valid for every signed x with |x| < 2^31. */
static inline __m256i gt_reduce8_centered(__m256i x)
{
    const __m256i reciprocal = _mm256_set1_epi32(GT_RECIP_Q32);
    const __m256i q = _mm256_set1_epi32(NTRUPLUS_Q);
    const __m256i qm1 = _mm256_set1_epi32(NTRUPLUS_Q - 1);
    const __m256i center = _mm256_set1_epi32(GT_CENTER);
    const __m256i sign = _mm256_srai_epi32(x, 31);
    const __m256i absolute = _mm256_sub_epi32(_mm256_xor_si256(x, sign), sign);

    __m256i even = _mm256_mul_epu32(absolute, reciprocal);
    __m256i odd_input = _mm256_srli_si256(absolute, 4);
    __m256i odd = _mm256_mul_epu32(odd_input, reciprocal);
    even = _mm256_srli_epi64(even, 32);
    odd = _mm256_slli_epi64(_mm256_srli_epi64(odd, 32), 32);
    const __m256i quotient = _mm256_or_si256(even, odd);

    __m256i remainder = _mm256_sub_epi32(
        absolute, _mm256_mullo_epi32(quotient, q));
    __m256i correction = _mm256_cmpgt_epi32(remainder, qm1);
    remainder = _mm256_sub_epi32(remainder,
                                 _mm256_and_si256(correction, q));
    correction = _mm256_cmpgt_epi32(remainder, center);
    remainder = _mm256_sub_epi32(remainder,
                                 _mm256_and_si256(correction, q));
    return _mm256_sub_epi32(_mm256_xor_si256(remainder, sign), sign);
}

static inline __m256i gt_pack16_sequential(__m256i low, __m256i high)
{
    __m256i packed = _mm256_packs_epi32(low, high);
    return _mm256_permute4x64_epi64(packed, 0xd8);
}

static inline __m256i gt_mulmod16(__m256i a, __m256i b)
{
    const __m128i a_low = _mm256_castsi256_si128(a);
    const __m128i b_low = _mm256_castsi256_si128(b);
    const __m128i a_high = _mm256_extracti128_si256(a, 1);
    const __m128i b_high = _mm256_extracti128_si256(b, 1);
    __m256i low = _mm256_mullo_epi32(_mm256_cvtepi16_epi32(a_low),
                                     _mm256_cvtepi16_epi32(b_low));
    __m256i high = _mm256_mullo_epi32(_mm256_cvtepi16_epi32(a_high),
                                      _mm256_cvtepi16_epi32(b_high));
    return gt_pack16_sequential(gt_reduce8_centered(low),
                                gt_reduce8_centered(high));
}

static inline __m256i gt_center16_twice(__m256i x)
{
    const __m256i q = _mm256_set1_epi16(NTRUPLUS_Q);
    const __m256i center = _mm256_set1_epi16(GT_CENTER);
    const __m256i neg_center = _mm256_set1_epi16(-GT_CENTER);
    for (unsigned i = 0; i < 2; ++i) {
        __m256i mask = _mm256_cmpgt_epi16(x, center);
        x = _mm256_sub_epi16(x, _mm256_and_si256(mask, q));
        mask = _mm256_cmpgt_epi16(neg_center, x);
        x = _mm256_add_epi16(x, _mm256_and_si256(mask, q));
    }
    return x;
}

#endif
