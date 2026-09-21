/* AVX2 conformance test, NOT a formal proof of the full NTT binary.
 * Pass signed Montgomery constants as command-line arguments.
 */
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static int wrap16(int64_t x) {
    unsigned u = (unsigned)((uint64_t)x & 65535u);
    return u < 32768u ? (int)u : (int)u - 65536;
}
static int floor16(int64_t x) {
    return x >= 0 ? (int)(x / 65536) : -(int)((-x + 65535) / 65536);
}
int main(int argc, char **argv) {
    int16_t in[16], got[16];
    uint64_t checks = 0;
    const __m256i q = _mm256_set1_epi16(3457);
    if (argc < 2) return 2;
    for (int arg = 1; arg < argc; ++arg) {
        char *end;
        long parsed = strtol(argv[arg], &end, 10);
        if (*end || parsed < -32768 || parsed > 32767) return 2;
        int w = (int)parsed;
        int wi = wrap16((int64_t)w*12929);
        for (int base = -32768; base < 32768; base += 16) {
            for (int i = 0; i < 16; ++i) in[i] = (int16_t)(base+i);
            __m256i x = _mm256_loadu_si256((const __m256i *)in);
            __m256i low = _mm256_mullo_epi16(x, _mm256_set1_epi16((short)wi));
            __m256i hi = _mm256_mulhi_epi16(x, _mm256_set1_epi16((short)w));
            __m256i out = _mm256_sub_epi16(hi, _mm256_mulhi_epi16(low, q));
            _mm256_storeu_si256((__m256i *)got, out);
            for (int i = 0; i < 16; ++i) {
                int v = base+i;
                int expected = floor16((int64_t)v*w) - floor16((int64_t)wrap16((int64_t)v*wi)*3457);
                if (expected < -32768 || expected > 32767 || got[i] != expected ||
                    ((int64_t)got[i]*65536-(int64_t)v*w)%3457) return 1;
                ++checks;
            }
        }
    }
    for (int base = -32768; base < 32768; base += 16) {
        for (int i = 0; i < 16; ++i) in[i] = (int16_t)(base+i);
        __m256i x = _mm256_loadu_si256((const __m256i *)in);
        __m256i t = _mm256_mulhrs_epi16(x, _mm256_set1_epi16(9));
        __m256i y = _mm256_sub_epi16(x, _mm256_mullo_epi16(t, q));
        __m256i z = _mm256_add_epi16(y, _mm256_and_si256(_mm256_srai_epi16(y, 15), q));
        _mm256_storeu_si256((__m256i *)got, z);
        for (int i = 0; i < 16; ++i) {
            int expected = ((base+i)%3457 + 3457)%3457;
            if (got[i] != expected) return 1;
        }
    }
    /* Deliberately cover the rounded-high multiply extreme separately. */
    __m256i edge = _mm256_set1_epi16(-32768);
    _mm256_storeu_si256((__m256i *)got, _mm256_mulhrs_epi16(edge, edge));
    if (got[0] != -32768) return 1;
    printf("{\"montgomery_cases\":%llu,\"serializer_cases\":65536,"
           "\"pmulhrsw_extreme\":%d,\"status\":\"pass\"}\n",
           (unsigned long long)checks, got[0]);
    return 0;
}
