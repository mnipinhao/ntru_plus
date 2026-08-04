#include "gt_backend.h"

#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "gt_avx2_arith.h"
#include "gt_generated_tables.h"

enum {
    GT_OMEGA3 = -723,
    GT_INV3 = 2305,
    GT_INV2 = 1729,
    GT_PHI_CENTERED = -722,
    GT_INV_DELTA = 1634,
};

static __m256i expand8_i16(const int16_t *values)
{
    return _mm256_cvtepi16_epi32(
        _mm_loadu_si128((const __m128i *)values));
}

static __m128i reduce4_i32(__m128i values)
{
    const __m256i wide = _mm256_inserti128_si256(
        _mm256_setzero_si256(), values, 0);
    return _mm256_castsi256_si128(gt_reduce8_centered(wide));
}

static __m128i pack4_i32(__m128i values)
{
    return _mm_packs_epi32(values, values);
}

static __m256i branch_weights(int branch0, int branch1)
{
    __m256i weights = _mm256_castsi128_si256(_mm_set1_epi32(branch0));
    return _mm256_inserti128_si256(weights, _mm_set1_epi32(branch1), 1);
}

static void transpose8x8_i16(__m128i x[8])
{
    const __m128i t0 = _mm_unpacklo_epi16(x[0], x[1]);
    const __m128i t1 = _mm_unpackhi_epi16(x[0], x[1]);
    const __m128i t2 = _mm_unpacklo_epi16(x[2], x[3]);
    const __m128i t3 = _mm_unpackhi_epi16(x[2], x[3]);
    const __m128i t4 = _mm_unpacklo_epi16(x[4], x[5]);
    const __m128i t5 = _mm_unpackhi_epi16(x[4], x[5]);
    const __m128i t6 = _mm_unpacklo_epi16(x[6], x[7]);
    const __m128i t7 = _mm_unpackhi_epi16(x[6], x[7]);
    const __m128i u0 = _mm_unpacklo_epi32(t0, t2);
    const __m128i u1 = _mm_unpackhi_epi32(t0, t2);
    const __m128i u2 = _mm_unpacklo_epi32(t1, t3);
    const __m128i u3 = _mm_unpackhi_epi32(t1, t3);
    const __m128i u4 = _mm_unpacklo_epi32(t4, t6);
    const __m128i u5 = _mm_unpackhi_epi32(t4, t6);
    const __m128i u6 = _mm_unpacklo_epi32(t5, t7);
    const __m128i u7 = _mm_unpackhi_epi32(t5, t7);
    x[0] = _mm_unpacklo_epi64(u0, u4);
    x[1] = _mm_unpackhi_epi64(u0, u4);
    x[2] = _mm_unpacklo_epi64(u1, u5);
    x[3] = _mm_unpackhi_epi64(u1, u5);
    x[4] = _mm_unpacklo_epi64(u2, u6);
    x[5] = _mm_unpackhi_epi64(u2, u6);
    x[6] = _mm_unpacklo_epi64(u3, u7);
    x[7] = _mm_unpackhi_epi64(u3, u7);
}

static unsigned bitreverse4(unsigned x)
{
    x = ((x & 0x5U) << 1) | ((x >> 1) & 0x5U);
    x = ((x & 0x3U) << 2) | ((x >> 2) & 0x3U);
    return x & 15U;
}

static void inverse_cyclic16(__m256i state[16])
{
    for (unsigned length = 2; length <= 16; length <<= 1) {
        const unsigned step = 16U / length;
        for (unsigned start = 0; start < 16; start += length) {
            for (unsigned j = 0; j < length / 2; ++j) {
                const __m256i u = state[start + j];
                __m256i v = state[start + j + length / 2];
                const unsigned power = (16U - j * step) & 15U;
                if (power != 0) {
                    const __m256i factor = _mm256_set1_epi16(
                        gt_omega16_powers[power]);
                    v = gt_mulmod16(v, factor);
                }
                state[start + j] = gt_center16_twice(_mm256_add_epi16(u, v));
                state[start + j + length / 2] =
                    gt_center16_twice(_mm256_sub_epi16(u, v));
            }
        }
    }
}

void gt_avx2_intt32_b_rows(int16_t out[32][16],
                           const int16_t in[32][16])
{
    __m256i plus[16];
    __m256i minus[16];
    const __m256i inv16 = _mm256_set1_epi16(gt_inv16);
    const __m256i inv2 = _mm256_set1_epi16(GT_INV2);

    for (size_t k = 0; k < 16; ++k) {
        const size_t physical = bitreverse4((unsigned)k);
        plus[physical] = _mm256_loadu_si256((const __m256i *)in[2 * k]);
        minus[physical] = _mm256_loadu_si256((const __m256i *)in[2 * k + 1]);
    }
    inverse_cyclic16(plus);
    inverse_cyclic16(minus);
    for (size_t j = 0; j < 16; ++j) {
        plus[j] = gt_mulmod16(plus[j], inv16);
        const __m256i untwist = _mm256_set1_epi16(gt_b_split_untwist[j]);
        minus[j] = gt_mulmod16(gt_mulmod16(minus[j], inv16), untwist);
        const __m256i low = gt_mulmod16(
            gt_center16_twice(_mm256_add_epi16(plus[j], minus[j])), inv2);
        const __m256i high = gt_mulmod16(
            gt_center16_twice(_mm256_sub_epi16(plus[j], minus[j])), inv2);
        _mm256_storeu_si256((__m256i *)out[j], low);
        _mm256_storeu_si256((__m256i *)out[j + 16], high);
    }
}

static void load_gt_block(int16_t input[32][16], const poly *frequency,
                          size_t k3, size_t block32)
{
    __m128i first[8];
    __m128i second[8];
    for (size_t column = 0; column < 8; ++column) {
        const size_t branch = column / 4;
        const size_t degree = column % 4;
        const size_t batch = ((branch * 3 + k3) * 2 + block32);
        const __m256i values = _mm256_loadu_si256(
            (const __m256i *)&frequency->coeffs[
                64 * batch + 16 * degree]);
        first[column] = _mm256_castsi256_si128(values);
        second[column] = _mm256_extracti128_si256(values, 1);
    }
    transpose8x8_i16(first);
    transpose8x8_i16(second);
    const size_t row = 16 * block32;
    for (size_t i = 0; i < 8; ++i) {
        _mm_storeu_si128((__m128i *)input[row + i], first[i]);
        _mm_storeu_si128((__m128i *)input[row + 8 + i], second[i]);
    }
}

void gt_poly_invntt_avx2_b(poly *r)
{
    const poly frequency = *r;
    _Alignas(32) int16_t input[32][16];
    _Alignas(32) int16_t after32[3][32][16];

    memset(input, 0, sizeof input);
    memset(after32, 0, sizeof after32);
    for (size_t k3 = 0; k3 < 3; ++k3) {
        load_gt_block(input, &frequency, k3, 0);
        load_gt_block(input, &frequency, k3, 1);
        gt_avx2_intt32_b_rows(after32[k3],
                              (const int16_t (*)[16])input);
    }

    const __m256i omega3 = _mm256_set1_epi32(GT_OMEGA3);
    const __m256i inv3 = _mm256_set1_epi32(GT_INV3);
    const __m128i inv_delta = _mm_set1_epi32(GT_INV_DELTA);
    const __m128i phi0 = _mm_set1_epi32(GT_PHI_CENTERED);
    for (size_t n32 = 0; n32 < 32; ++n32) {
        const __m256i x0 = expand8_i16(after32[0][n32]);
        const __m256i x1 = expand8_i16(after32[1][n32]);
        const __m256i x2 = expand8_i16(after32[2][n32]);
        const __m256i t = gt_reduce8_centered(_mm256_mullo_epi32(
            _mm256_sub_epi32(x1, x2), omega3));
        __m256i values[3];
        values[0] = gt_reduce8_centered(_mm256_mullo_epi32(
            gt_reduce8_centered(
                _mm256_add_epi32(x0, _mm256_add_epi32(x1, x2))), inv3));
        values[1] = gt_reduce8_centered(_mm256_mullo_epi32(
            gt_reduce8_centered(
                _mm256_sub_epi32(_mm256_sub_epi32(x0, x1), t)), inv3));
        values[2] = gt_reduce8_centered(_mm256_mullo_epi32(
            gt_reduce8_centered(
                _mm256_add_epi32(_mm256_sub_epi32(x0, x2), t)), inv3));

        for (size_t n3 = 0; n3 < 3; ++n3) {
            const size_t n = gt_input_crt[32 * n3 + n32];
            const __m256i weights = branch_weights(
                gt_postweight[0][n], gt_postweight[1][n]);
            const __m256i weighted = gt_reduce8_centered(
                _mm256_mullo_epi32(values[n3], weights));
            const __m128i u = _mm256_castsi256_si128(weighted);
            const __m128i v = _mm256_extracti128_si256(weighted, 1);
            const __m128i high = reduce4_i32(_mm_mullo_epi32(
                _mm_sub_epi32(u, v), inv_delta));
            const __m128i low = reduce4_i32(_mm_sub_epi32(
                u, _mm_mullo_epi32(high, phi0)));
            _mm_storel_epi64((__m128i *)&r->coeffs[4 * n],
                             pack4_i32(low));
            _mm_storel_epi64((__m128i *)&r->coeffs[
                NTRUPLUS_N / 2 + 4 * n], pack4_i32(high));
        }
    }
}

void gt_poly_invntt_scale(poly *r)
{
    gt_poly_invntt_avx2_b(r);
}
