/*
 * Exhaustive C twin of tools/prove_freeze_2op.py (shared copy of the NTRU+864
 * avx2_official_opt_001 test, parameterised only through params.h / consts.c):
 * runs all 65536 int16 inputs through the real AVX2 instructions of the
 * Official freeze (864 pack.s:401-437, 768/1152 pack.s:19-70:
 * vpmulhrsw _16xv, vpmullw _16xq, vpsubw; vpsraw 15, vpand _16xq, vpaddw) and
 * of the 2-op replacement (vpaddw _16xq, vpminuw), with the constants taken
 * from the linked pinned consts.c.  Asserts Barrett output in (-q, q), the two
 * results equal bit for bit, and both equal x mod q.
 */
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "consts.h"

int main(void) {
    const __m256i v = _mm256_load_si256((const __m256i *)_16xv);
    const __m256i q = _mm256_load_si256((const __m256i *)_16xq);
    int lo = 32767, hi = -32768;
    unsigned long bad = 0, n = 0;
    for (int base = -32768; base < 32768; base += 16) {
        int16_t in[16] __attribute__((aligned(32)));
        int16_t b[16] __attribute__((aligned(32)));
        int16_t o3[16] __attribute__((aligned(32)));
        int16_t o2[16] __attribute__((aligned(32)));
        for (int i = 0; i < 16; i++) in[i] = (int16_t)(base + i);
        __m256i x = _mm256_load_si256((const __m256i *)in);
        __m256i t = _mm256_mulhrs_epi16(x, v);
        t = _mm256_mullo_epi16(t, q);
        x = _mm256_sub_epi16(x, t);
        _mm256_store_si256((__m256i *)b, x);
        __m256i s = _mm256_srai_epi16(x, 15);
        s = _mm256_and_si256(s, q);
        _mm256_store_si256((__m256i *)o3, _mm256_add_epi16(x, s));
        _mm256_store_si256((__m256i *)o2, _mm256_min_epu16(x, _mm256_add_epi16(x, q)));
        for (int i = 0; i < 16; i++, n++) {
            int r = (base + i) % NTRUPLUS_Q;
            if (r < 0) r += NTRUPLUS_Q;
            if (b[i] < lo) lo = b[i];
            if (b[i] > hi) hi = b[i];
            bad += o3[i] != o2[i] || o2[i] != r;
        }
    }
    printf("freeze 2-op: %lu inputs, Barrett output in [%d, %d], q=%d, mismatches=%lu\n", n, lo, hi,
           NTRUPLUS_Q, bad);
    if (n != 65536 || bad || lo <= -NTRUPLUS_Q || hi >= NTRUPLUS_Q) {
        fputs("FAIL\n", stderr);
        return 1;
    }
    puts("freeze 2-op exhaustive: pass");
    return 0;
}
