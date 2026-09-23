#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* A stage-6 YMM mixes four half-scaled lanes with twelve plain lanes. */
__attribute__((noinline))
void officialopt_mixed_qhalf_butterfly(__m256i a, __m256i t,
                                      __m256i mask, __m256i *plus,
                                      __m256i *minus)
{
    const __m256i bias = _mm256_set1_epi16((short)0x8000);
    const __m256i one = _mm256_set1_epi16(1);
    const __m256i correction = _mm256_set1_epi16(1728);
    const __m256i zero = _mm256_setzero_si256();
    __m256i parity = _mm256_and_si256(_mm256_xor_si256(a, t), one);
    __m256i addend = _mm256_and_si256(_mm256_sub_epi16(zero, parity), correction);
    __m256i biased_a = _mm256_xor_si256(a, bias);
    __m256i p_half = _mm256_add_epi16(
        _mm256_xor_si256(_mm256_avg_epu16(biased_a,
                                          _mm256_xor_si256(t, bias)), bias),
        addend);
    __m256i m_half = _mm256_add_epi16(
        _mm256_xor_si256(_mm256_avg_epu16(
            biased_a, _mm256_xor_si256(_mm256_sub_epi16(zero, t), bias)),
            bias), addend);
    __m256i p_plain = _mm256_add_epi16(a, t);
    __m256i m_plain = _mm256_sub_epi16(a, t);
    *plus = _mm256_blendv_epi8(p_plain, p_half, mask);
    *minus = _mm256_blendv_epi8(m_plain, m_half, mask);
}

static uint32_t state = 0x20260923u;
static int random_word(void)
{
    state = state * 1664525u + 1013904223u;
    return (int)(state % 15001u) - 7500;
}

static int modq(int x)
{
    int r = x % 3457;
    return r < 0 ? r + 3457 : r;
}

int main(void)
{
    _Alignas(32) int16_t av[16], tv[16], mask[16], hi[16], lo[16];
    const int edge[] = {-7644, -1, 0, 1, 7644};
    for (int trial = 0; trial < 100000 + 25; ++trial) {
        for (int lane = 0; lane < 16; ++lane) {
            av[lane] = trial < 25 ? (int16_t)edge[trial / 5] :
                                      (int16_t)random_word();
            tv[lane] = trial < 25 ? (int16_t)edge[trial % 5] :
                                      (int16_t)random_word();
            mask[lane] = (int16_t)((((lane + trial) * 5) % 16) < 4 ? -1 : 0);
        }
        __m256i p, m;
        officialopt_mixed_qhalf_butterfly(
            _mm256_load_si256((const __m256i *)av),
            _mm256_load_si256((const __m256i *)tv),
            _mm256_load_si256((const __m256i *)mask), &p, &m);
        _mm256_store_si256((__m256i *)hi, p);
        _mm256_store_si256((__m256i *)lo, m);
        for (int lane = 0; lane < 16; ++lane) {
            int a = av[lane], t = tv[lane];
            if (mask[lane]) {
                if (modq(2 * (int)hi[lane]) != modq(a + t) ||
                    modq(2 * (int)lo[lane]) != modq(a - t))
                    return 1;
            } else if (hi[lane] != a + t || lo[lane] != a - t) {
                return 1;
            }
        }
    }
    puts("mixed AVX2 butterfly: 100025 vectors passed");
    return 0;
}
