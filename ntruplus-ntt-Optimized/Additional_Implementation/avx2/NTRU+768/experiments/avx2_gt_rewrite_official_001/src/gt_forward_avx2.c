#include "gt_backend.h"

#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "gt_avx2_arith.h"
#include "gt_generated_tables.h"

enum {
    GT_PHI_CENTERED = -722,
    GT_PHI_INV_CENTERED = 723,
    GT_OMEGA3 = -723,
};

static __m128i pack8_i32(__m256i x)
{
    return _mm_packs_epi32(_mm256_castsi256_si128(x),
                           _mm256_extracti128_si256(x, 1));
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

static unsigned twiddle_power(unsigned stage, unsigned lo)
{
    if (stage == 1)
        return 0;
    unsigned x = lo >> (5U - stage);
    unsigned reversed = 0;
    for (unsigned i = 0; i < stage - 1; ++i) {
        reversed = (reversed << 1) | (x & 1U);
        x >>= 1;
    }
    return reversed << (4U - stage);
}

static void cyclic16(__m256i state[16])
{
    for (unsigned stage = 1; stage <= 4; ++stage) {
        const unsigned distance = 1U << (4U - stage);
        for (unsigned lo = 0; lo < 16; ++lo) {
            if (lo & distance)
                continue;
            const unsigned hi = lo + distance;
            const unsigned power = twiddle_power(stage, lo);
            const __m256i u = state[lo];
            __m256i t = state[hi];
            if (power != 0) {
                const __m256i factor = _mm256_set1_epi16(
                    gt_omega16_powers[power]);
                t = gt_mulmod16(t, factor);
            }
            state[lo] = gt_center16_twice(_mm256_add_epi16(u, t));
            state[hi] = gt_center16_twice(_mm256_sub_epi16(u, t));
        }
    }
}

static void ntt32_b_rows(int16_t out[32][16], const int16_t in[32][16],
                         int identity_reduce)
{
    __m256i plus[16];
    __m256i minus[16];
    for (size_t j = 0; j < 16; ++j) {
        const __m256i low = _mm256_loadu_si256((const __m256i *)in[j]);
        const __m256i high = _mm256_loadu_si256((const __m256i *)in[j + 16]);
        plus[j] = _mm256_add_epi16(low, high);
        if (identity_reduce)
            plus[j] = gt_center16_twice(plus[j]);
        const __m256i difference = _mm256_sub_epi16(low, high);
        const __m256i twist = _mm256_set1_epi16(gt_b_split_twist[j]);
        minus[j] = gt_mulmod16(difference, twist);
    }

    cyclic16(plus);
    cyclic16(minus);
    for (size_t k = 0; k < 16; ++k) {
        const size_t physical = bitreverse4((unsigned)k);
        _mm256_storeu_si256((__m256i *)out[2 * k], plus[physical]);
        _mm256_storeu_si256((__m256i *)out[2 * k + 1], minus[physical]);
    }
}

void gt_avx2_ntt32_b1_rows(int16_t out[32][16],
                           const int16_t in[32][16])
{
    ntt32_b_rows(out, in, 0);
}

void gt_avx2_ntt32_b2_rows(int16_t out[32][16],
                           const int16_t in[32][16])
{
    ntt32_b_rows(out, in, 1);
}

static void store_gt_block(poly *r, size_t k3, size_t block32,
                           const int16_t output[32][16])
{
    __m128i first[8];
    __m128i second[8];
    const size_t row = 16 * block32;
    for (size_t i = 0; i < 8; ++i) {
        first[i] = _mm_loadu_si128((const __m128i *)output[row + i]);
        second[i] = _mm_loadu_si128((const __m128i *)output[row + 8 + i]);
    }
    transpose8x8_i16(first);
    transpose8x8_i16(second);
    for (size_t column = 0; column < 8; ++column) {
        __m256i values = _mm256_castsi128_si256(first[column]);
        values = _mm256_inserti128_si256(values, second[column], 1);
        const size_t branch = column / 4;
        const size_t degree = column % 4;
        const size_t batch = ((branch * 3 + k3) * 2 + block32);
        _mm256_storeu_si256((__m256i *)&r->coeffs[
            64 * batch + 16 * degree], values);
    }
}

static void forward_b(poly *r, int identity_reduce)
{
    const poly input = *r;
    _Alignas(32) int16_t rows[3][32][16];
    _Alignas(32) int16_t output[32][16];
    memset(rows, 0, sizeof rows);

    /* Fused 8-lane F0/F1 producer: raw -722/+723 top butterfly, branch
     * preweight, DFT3, and lane-transposed rows for the AVX2 B kernel. */
    const __m256i phi0 = _mm256_set1_epi32(GT_PHI_CENTERED);
    const __m256i phi1 = _mm256_set1_epi32(GT_PHI_INV_CENTERED);
    const __m256i omega3 = _mm256_set1_epi32(GT_OMEGA3);
    for (size_t n32 = 0; n32 < 32; ++n32) {
        __m256i x[3];
        for (size_t n3 = 0; n3 < 3; ++n3) {
            const size_t n = gt_input_crt[32 * n3 + n32];
            const size_t index = 4 * n;
            const __m256i low = _mm256_cvtepi16_epi32(
                _mm_loadl_epi64((const __m128i *)&input.coeffs[index]));
            const __m256i high = _mm256_cvtepi16_epi32(
                _mm_loadl_epi64((const __m128i *)&input.coeffs[
                    index + NTRUPLUS_N / 2]));
            const __m256i top0 = _mm256_add_epi32(
                low, _mm256_mullo_epi32(high, phi0));
            const __m256i top1 = _mm256_add_epi32(
                low, _mm256_mullo_epi32(high, phi1));
            __m256i top = _mm256_castsi128_si256(
                _mm256_castsi256_si128(top0));
            top = _mm256_inserti128_si256(
                top, _mm256_castsi256_si128(top1), 1);
            const __m256i weights = branch_weights(
                gt_preweight[0][n], gt_preweight[1][n]);
            x[n3] = gt_reduce8_centered(
                _mm256_mullo_epi32(top, weights));
        }
        const __m256i difference = _mm256_sub_epi32(x[1], x[2]);
        const __m256i t = gt_reduce8_centered(
            _mm256_mullo_epi32(difference, omega3));
        const __m256i y0 = gt_reduce8_centered(
            _mm256_add_epi32(x[0], _mm256_add_epi32(x[1], x[2])));
        const __m256i y1 = gt_reduce8_centered(
            _mm256_add_epi32(_mm256_sub_epi32(x[0], x[2]), t));
        const __m256i y2 = gt_reduce8_centered(
            _mm256_sub_epi32(_mm256_sub_epi32(x[0], x[1]), t));
        _mm_storeu_si128((__m128i *)rows[0][n32], pack8_i32(y0));
        _mm_storeu_si128((__m128i *)rows[1][n32], pack8_i32(y1));
        _mm_storeu_si128((__m128i *)rows[2][n32], pack8_i32(y2));
    }

    for (size_t k3 = 0; k3 < 3; ++k3) {
        ntt32_b_rows(output, (const int16_t (*)[16])rows[k3], identity_reduce);
        store_gt_block(r, k3, 0, (const int16_t (*)[16])output);
        store_gt_block(r, k3, 1, (const int16_t (*)[16])output);
    }
}

void gt_poly_ntt_avx2_b1(poly *r)
{
    forward_b(r, 0);
}

void gt_poly_ntt_avx2_b2(poly *r)
{
    forward_b(r, 1);
}
