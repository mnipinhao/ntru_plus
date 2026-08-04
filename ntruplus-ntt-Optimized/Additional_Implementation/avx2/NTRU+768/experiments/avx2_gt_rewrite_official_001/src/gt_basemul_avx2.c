#include "gt_backend.h"

#include <immintrin.h>
#include <stddef.h>

#include "gt_avx2_arith.h"
#include "gt_generated_tables.h"

static inline __m128i load4(const int16_t *p)
{
    return _mm_loadl_epi64((const __m128i *)p);
}

static inline __m128i reduce4(__m128i x)
{
    const __m256i wide = _mm256_inserti128_si256(_mm256_setzero_si256(), x, 0);
    const __m128i reduced = _mm256_castsi256_si128(gt_reduce8_centered(wide));
    return _mm_packs_epi32(reduced, reduced);
}

static inline __m128i mulmod4(__m128i a, __m128i b)
{
    const __m128i product = _mm_mullo_epi32(_mm_cvtepi16_epi32(a),
                                            _mm_cvtepi16_epi32(b));
    return reduce4(product);
}

static inline __m128i mulwide4(__m128i a, __m128i b)
{
    return _mm_mullo_epi32(_mm_cvtepi16_epi32(a),
                           _mm_cvtepi16_epi32(b));
}

static inline __m128i cross4(__m128i ai, __m128i aj,
                             __m128i bi, __m128i bj,
                             __m128i di, __m128i dj)
{
    const __m128i product = mulwide4(_mm_add_epi16(ai, aj),
                                     _mm_add_epi16(bi, bj));
    return reduce4(_mm_sub_epi32(product, _mm_add_epi32(di, dj)));
}

static inline __m128i madd_reduce4(__m128i a0, __m128i b0,
                                   __m128i a1, __m128i b1)
{
    return reduce4(_mm_madd_epi16(_mm_unpacklo_epi16(a0, a1),
                                  _mm_unpacklo_epi16(b0, b1)));
}

static inline __m128i madd4_4(__m128i a0, __m128i b0,
                              __m128i a1, __m128i b1,
                              __m128i a2, __m128i b2,
                              __m128i a3, __m128i b3)
{
    return _mm_add_epi32(
        _mm_madd_epi16(_mm_unpacklo_epi16(a0, a1),
                       _mm_unpacklo_epi16(b0, b1)),
        _mm_madd_epi16(_mm_unpacklo_epi16(a2, a3),
                       _mm_unpacklo_epi16(b2, b3)));
}

static __attribute__((noinline, noclone))
void basemul4(int16_t *r, const int16_t *a, const int16_t *b,
              const int16_t *alpha)
{
    const __m128i av = load4(alpha);
    const __m128i aa1 = mulmod4(av, load4(a + 16));
    const __m128i aa2 = mulmod4(av, load4(a + 32));
    const __m128i aa3 = mulmod4(av, load4(a + 48));
    __m128i c = madd4_4(load4(a), load4(b), aa1, load4(b + 48),
                        aa2, load4(b + 32), aa3, load4(b + 16));
    _mm_storel_epi64((__m128i *)(r + 0), reduce4(c));
    c = madd4_4(load4(a), load4(b + 16), load4(a + 16), load4(b),
                aa2, load4(b + 48), aa3, load4(b + 32));
    _mm_storel_epi64((__m128i *)(r + 16), reduce4(c));
    c = madd4_4(load4(a), load4(b + 32), load4(a + 16), load4(b + 16),
                load4(a + 32), load4(b), aa3, load4(b + 48));
    _mm_storel_epi64((__m128i *)(r + 32), reduce4(c));
    c = madd4_4(load4(a), load4(b + 48), load4(a + 16), load4(b + 32),
                load4(a + 32), load4(b + 16), load4(a + 48), load4(b));
    _mm_storel_epi64((__m128i *)(r + 48), reduce4(c));
}

void gt_poly_basemul(poly *r, const poly *a, const poly *b)
{
    for (size_t batch = 0; batch < 12; ++batch) {
        const size_t base = 64 * batch;
        for (size_t quarter = 0; quarter < 4; ++quarter) {
            const size_t lane = 4 * quarter;
            basemul4(&r->coeffs[base + lane], &a->coeffs[base + lane],
                     &b->coeffs[base + lane],
                     &gt_alpha[16 * batch + lane]);
        }
    }
}

static __attribute__((noinline, noclone))
void basemul4_bm_b(int16_t *r, const int16_t *a, const int16_t *b,
                   const int16_t *alpha)
{
    const __m128i one = _mm_set1_epi16(1);
    const __m128i av = load4(alpha);
    const __m128i a0 = load4(a);
    const __m128i a1 = load4(a + 16);
    const __m128i a2 = load4(a + 32);
    const __m128i a3 = load4(a + 48);
    const __m128i b0 = load4(b);
    const __m128i b1 = load4(b + 16);
    const __m128i b2 = load4(b + 32);
    const __m128i b3 = load4(b + 48);
    const __m128i d0w = mulwide4(a0, b0);
    const __m128i d1w = mulwide4(a1, b1);
    const __m128i d2w = mulwide4(a2, b2);
    const __m128i d3w = mulwide4(a3, b3);
    const __m128i d0 = reduce4(d0w);
    const __m128i d1 = reduce4(d1w);
    const __m128i d2 = reduce4(d2w);
    const __m128i d3 = reduce4(d3w);
    const __m128i e01 = cross4(a0, a1, b0, b1, d0w, d1w);
    const __m128i e02 = cross4(a0, a2, b0, b2, d0w, d2w);
    const __m128i e03 = cross4(a0, a3, b0, b3, d0w, d3w);
    const __m128i e12 = cross4(a1, a2, b1, b2, d1w, d2w);
    const __m128i e13 = cross4(a1, a3, b1, b3, d1w, d3w);
    const __m128i e23 = cross4(a2, a3, b2, b3, d2w, d3w);

    _mm_storel_epi64((__m128i *)(r + 0),
        madd_reduce4(d0, one, av, _mm_add_epi16(e13, d2)));
    _mm_storel_epi64((__m128i *)(r + 16),
        madd_reduce4(e01, one, av, e23));
    _mm_storel_epi64((__m128i *)(r + 32),
        madd_reduce4(_mm_add_epi16(e02, d1), one, av, d3));
    _mm_storel_epi64((__m128i *)(r + 48),
        madd_reduce4(e03, one, e12, one));
}

void gt_poly_basemul_bm_b(poly *r, const poly *a, const poly *b)
{
    for (size_t batch = 0; batch < 12; ++batch) {
        const size_t base = 64 * batch;
        for (size_t quarter = 0; quarter < 4; ++quarter) {
            const size_t lane = 4 * quarter;
            basemul4_bm_b(&r->coeffs[base + lane], &a->coeffs[base + lane],
                          &b->coeffs[base + lane],
                          &gt_alpha[16 * batch + lane]);
        }
    }
}

void gt_poly_basemul_scale(poly *r, const poly *a, const poly *b)
{
    /* Normal-form GT inverse contains its own normalization. */
    gt_poly_basemul(r, a, b);
}

void gt_avx2_reduce32_test(int16_t out[8], const int32_t in[8])
{
    const __m256i x = _mm256_loadu_si256((const __m256i *)in);
    const __m256i y = gt_reduce8_centered(x);
    const __m128i low = _mm256_castsi256_si128(y);
    const __m128i high = _mm256_extracti128_si256(y, 1);
    const __m128i packed = _mm_packs_epi32(low, high);
    _mm_storeu_si128((__m128i *)out, packed);
}
