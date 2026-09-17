#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define Q 3457
#define QINV 12929

static int32_t mr32_ref(int32_t s)
{
    const int16_t t = (int16_t)((uint16_t)s * (uint16_t)QINV);
    const int64_t n = (int64_t)s - (int64_t)t * Q;
    if ((n & 0xffff) != 0)
        abort();
    return (int32_t)(n / 65536);
}

static __m256i mr32_avx2(__m256i s)
{
    const __m256i qinv = _mm256_set1_epi16(QINV);
    const __m256i q_even = _mm256_setr_epi16(Q, 0, Q, 0, Q, 0, Q, 0,
                                             Q, 0, Q, 0, Q, 0, Q, 0);
    __m256i t = _mm256_mullo_epi16(s, qinv);
    t = _mm256_madd_epi16(t, q_even);
    s = _mm256_sub_epi32(s, t);
    return _mm256_srai_epi32(s, 16);
}

static uint32_t next_u32(uint32_t *state)
{
    uint32_t x = *state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    *state = x;
    return x;
}

int main(void)
{
    uint32_t state = 0x00d3864u;
    int checked = 0;
    for (int round = 0; round < 25000; ++round) {
        int16_t a[16] __attribute__((aligned(32)));
        int16_t b[16] __attribute__((aligned(32)));
        int32_t got[8] __attribute__((aligned(32)));
        int32_t expect[8];
        for (int i = 0; i < 16; ++i) {
            a[i] = (int16_t)(next_u32(&state) % Q);
            b[i] = (int16_t)next_u32(&state);
        }
        if (round == 0) {
            for (int i = 0; i < 16; i += 2) {
                a[i] = 0;
                a[i + 1] = Q - 1;
                b[i] = INT16_MIN;
                b[i + 1] = INT16_MAX;
            }
        }
        const __m256i av = _mm256_load_si256((const __m256i *)a);
        const __m256i bv = _mm256_load_si256((const __m256i *)b);
        const __m256i sums = _mm256_madd_epi16(av, bv);
        const __m256i reduced = mr32_avx2(sums);
        _mm256_store_si256((__m256i *)got, reduced);
        for (int i = 0; i < 8; ++i) {
            const int32_t s = (int32_t)a[2 * i] * b[2 * i] +
                              (int32_t)a[2 * i + 1] * b[2 * i + 1];
            expect[i] = mr32_ref(s);
            if (got[i] != expect[i] || got[i] < INT16_MIN || got[i] > INT16_MAX)
                return 1;
            if (((int64_t)got[i] * 65536 - s) % Q != 0)
                return 2;
            ++checked;
        }

        const __m256i lo = reduced;
        const __m256i hi = mr32_avx2(_mm256_add_epi32(sums, _mm256_set1_epi32(12345)));
        const __m256i packed0 = _mm256_packs_epi32(lo, hi);
        const __m256i packed = _mm256_permute4x64_epi64(packed0, 0xd8);
        int16_t packed_words[16] __attribute__((aligned(32)));
        int32_t hi_words[8] __attribute__((aligned(32)));
        _mm256_store_si256((__m256i *)packed_words, packed);
        _mm256_store_si256((__m256i *)hi_words, hi);
        for (int i = 0; i < 8; ++i) {
            if (packed_words[i] != got[i] || packed_words[8 + i] != hi_words[i])
                return 3;
        }
    }
    printf("d3 mr32 avx2: %d lanes checked\n", checked);
    return 0;
}
