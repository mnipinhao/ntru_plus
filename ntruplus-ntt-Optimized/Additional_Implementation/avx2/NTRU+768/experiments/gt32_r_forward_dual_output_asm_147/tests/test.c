#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "candidate.h"
#include "internal.h"

static uint64_t state = UINT64_C(0x147d00d123456789);
static uint32_t rnd(void) {
    state ^= state << 13; state ^= state >> 7; state ^= state << 17;
    return (uint32_t)state;
}

static int one(const int16_t in[768], int trial) {
    _Alignas(64) int16_t frontend[768], m0[768], m1[768];
    _Alignas(64) uint8_t w0[1152], w1[1152];
    ntruplus768_ntt_frontend_avx2(frontend, in);
    ntruplus768_ntt_m_avx2(m0, frontend);
    ntruplus768_pack_m_lazy10788_avx2(w0, m0);
    gt147_ntt_m_wire_avx2(m1, frontend, w1);
    if (memcmp(m0, m1, sizeof m0)) {
        printf("M mismatch trial=%d\n", trial); return 1;
    }
    if (memcmp(w0, w1, sizeof w0)) {
        for (int i = 0; i < 1152; ++i) if (w0[i] != w1[i]) {
            printf("WIRE mismatch trial=%d byte=%d got=%u want=%u\n",
                   trial, i, w1[i], w0[i]); break;
        }
        if (trial == 0) {
            printf("control nonzero:");
            for (int i = 0; i < 1152; ++i) if (w0[i]) printf(" %d:%u", i, w0[i]);
            printf("\ncandidate nonzero:");
            for (int i = 0; i < 1152; ++i) if (w1[i]) printf(" %d:%u", i, w1[i]);
            printf("\n");
        }
        return 1;
    }
    return 0;
}

int main(void) {
    _Alignas(64) int16_t in[768];
    for (int p = 0; p < 768; ++p) {
        memset(in, 0, sizeof in); in[p] = 1;
        if (one(in, p)) return 1;
    }
    for (int t = 0; t < 1000; ++t) {
        for (int i = 0; i < 768; ++i) in[i] = (int16_t)((int)(rnd() % 5) - 2);
        if (one(in, 768 + t)) return 1;
    }
    puts("PASS impulses=768 random_cbd_range=1000 M_exact WIRE12_exact");
    return 0;
}
