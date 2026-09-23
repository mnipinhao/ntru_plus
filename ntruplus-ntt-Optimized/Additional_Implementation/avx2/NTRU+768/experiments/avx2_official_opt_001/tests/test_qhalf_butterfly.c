#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

/* Local AVX2 arithmetic probe; no KEM function or public ABI is changed. */
__attribute__((noinline))
void officialopt_qhalf_butterfly(__m256i a, __m256i t,
                                 __m256i *plus, __m256i *minus)
{
    const __m256i bias = _mm256_set1_epi16((short)0x8000);
    const __m256i one = _mm256_set1_epi16(1);
    const __m256i correction = _mm256_set1_epi16(1728);
    const __m256i zero = _mm256_setzero_si256();
    __m256i parity = _mm256_and_si256(_mm256_xor_si256(a, t), one);
    __m256i addend = _mm256_and_si256(_mm256_sub_epi16(zero, parity), correction);
    __m256i biased_a = _mm256_xor_si256(a, bias);
    __m256i biased_t = _mm256_xor_si256(t, bias);
    __m256i biased_neg_t = _mm256_xor_si256(_mm256_sub_epi16(zero, t), bias);
    __m256i p = _mm256_avg_epu16(biased_a, biased_t);
    __m256i m = _mm256_avg_epu16(biased_a, biased_neg_t);
    *plus = _mm256_add_epi16(_mm256_xor_si256(p, bias), addend);
    *minus = _mm256_add_epi16(_mm256_xor_si256(m, bias), addend);
}

/* Signed floor average = (a & b) + arithmetic_shift_right(a ^ b, 1). */
__attribute__((noinline))
void officialopt_qhalf_butterfly_floor(__m256i a, __m256i t,
                                       __m256i *plus, __m256i *minus)
{
    const __m256i zero = _mm256_setzero_si256();
    const __m256i one = _mm256_set1_epi16(1);
    const __m256i correction = _mm256_set1_epi16(1729);
    __m256i neg_t = _mm256_sub_epi16(zero, t);
    __m256i xor_plus = _mm256_xor_si256(a, t);
    __m256i xor_minus = _mm256_xor_si256(a, neg_t);
    __m256i parity = _mm256_and_si256(xor_plus, one);
    __m256i addend = _mm256_and_si256(_mm256_sub_epi16(zero, parity), correction);
    __m256i p = _mm256_add_epi16(_mm256_and_si256(a, t),
                                  _mm256_srai_epi16(xor_plus, 1));
    __m256i m = _mm256_add_epi16(_mm256_and_si256(a, neg_t),
                                  _mm256_srai_epi16(xor_minus, 1));
    *plus = _mm256_add_epi16(p, addend);
    *minus = _mm256_add_epi16(m, addend);
}

static uint32_t state = 0x20260923u;
static int next_value(void)
{
    state = state * 1664525u + 1013904223u;
    return (int)(state % 29001u) - 14500;
}

static int modq(int x)
{
    int r = x % 3457;
    return r < 0 ? r + 3457 : r;
}

static void check(const int16_t a[16], const int16_t t[16])
{
    _Alignas(32) int16_t hi[16], lo[16];
    __m256i va = _mm256_load_si256((const __m256i *)a);
    __m256i vt = _mm256_load_si256((const __m256i *)t);
    __m256i p, m;
    officialopt_qhalf_butterfly(va, vt, &p, &m);
    _mm256_store_si256((__m256i *)hi, p);
    _mm256_store_si256((__m256i *)lo, m);
    for (int i = 0; i < 16; ++i) {
        if (modq(2 * (int)hi[i]) != modq((int)a[i] + t[i]) ||
            modq(2 * (int)lo[i]) != modq((int)a[i] - t[i])) {
            fprintf(stderr, "mismatch lane=%d a=%d t=%d hi=%d lo=%d\n",
                    i, a[i], t[i], hi[i], lo[i]);
            exit(1);
        }
    }
    officialopt_qhalf_butterfly_floor(va, vt, &p, &m);
    _mm256_store_si256((__m256i *)hi, p);
    _mm256_store_si256((__m256i *)lo, m);
    for (int i = 0; i < 16; ++i) {
        if (modq(2 * (int)hi[i]) != modq((int)a[i] + t[i]) ||
            modq(2 * (int)lo[i]) != modq((int)a[i] - t[i])) {
            fprintf(stderr, "floor mismatch lane=%d a=%d t=%d hi=%d lo=%d\n",
                    i, a[i], t[i], hi[i], lo[i]);
            exit(1);
        }
    }
}

int main(void)
{
    _Alignas(32) int16_t a[16], t[16];
    const int edge[] = {-16284, -14556, -7644, -1, 0, 1, 7644, 14556, 16284};
    for (size_t i = 0; i < sizeof edge / sizeof edge[0]; ++i)
        for (size_t j = 0; j < sizeof edge / sizeof edge[0]; ++j) {
            for (int lane = 0; lane < 16; ++lane) {
                a[lane] = (int16_t)edge[i];
                t[lane] = (int16_t)edge[j];
            }
            check(a, t);
        }
    for (int trial = 0; trial < 100000; ++trial) {
        for (int lane = 0; lane < 16; ++lane) {
            a[lane] = (int16_t)next_value();
            t[lane] = (int16_t)next_value();
        }
        check(a, t);
    }
    puts("AVX2 modular-half butterfly: 100081 vectors passed");
    return 0;
}
