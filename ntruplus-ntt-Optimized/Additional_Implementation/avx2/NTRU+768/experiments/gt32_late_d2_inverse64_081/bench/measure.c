#define _GNU_SOURCE
#include "gate.h"
#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { TIMINGS = 32, INNER = 256 };
static int16_t a[GATE_WORDS] __attribute__((aligned(32)));
static int16_t b[GATE_WORDS] __attribute__((aligned(32)));
static int16_t t[GATE_WORDS] __attribute__((aligned(32)));
static int16_t u[GATE_WORDS] __attribute__((aligned(32)));
static int16_t h[GATE_WORDS] __attribute__((aligned(32)));
static int16_t out[GATE_WORDS] __attribute__((aligned(32)));
static volatile uint64_t sink;

static uint64_t cycles(void)
{
    unsigned aux;
    _mm_lfence();
    uint64_t x = __rdtscp(&aux);
    _mm_lfence();
    return x;
}

enum mode {
    CONTROL_FULL, CANDIDATE_FULL, CONTROL_BM, CANDIDATE_QBM,
    CONTROL_INVERSE, CANDIDATE_INVERSE, CONTROL_CROSS, CONTROL_NORM,
    CANDIDATE_NATURALIZE, CANDIDATE_INV64, CANDIDATE_CONVERT
};

static void call_variant(enum mode mode)
{
    if (mode == CANDIDATE_FULL) {
        d2_inverse64_qbm_asm(t, a, b);
        d2_inverse64_naturalize_asm(u, t);
        d2_inverse64_inv_asm(h, u);
        hwa_to_tile4_asm(out, h);
    } else if (mode == CONTROL_FULL) {
        late_soa_basemul_i2_fused_asm(t, a, b);
        control_inverse_cross3_asm(out, t);
        inverse32_normalize_asm(out, out);
    } else if (mode == CONTROL_BM) {
        late_soa_basemul_i2_fused_asm(t, a, b);
    } else if (mode == CANDIDATE_QBM) {
        d2_inverse64_qbm_asm(t, a, b);
    } else if (mode == CONTROL_INVERSE) {
        control_inverse_cross3_asm(out, t);
        inverse32_normalize_asm(out, out);
    } else if (mode == CANDIDATE_INVERSE) {
        d2_inverse64_naturalize_asm(u, t);
        d2_inverse64_inv_asm(h, u);
        hwa_to_tile4_asm(out, h);
    } else if (mode == CONTROL_CROSS) {
        control_inverse_cross3_asm(out, t);
    } else if (mode == CONTROL_NORM) {
        inverse32_normalize_asm(out, out);
    } else if (mode == CANDIDATE_NATURALIZE) {
        d2_inverse64_naturalize_asm(u, t);
    } else if (mode == CANDIDATE_INV64) {
        d2_inverse64_inv_asm(h, u);
    } else {
        hwa_to_tile4_asm(out, h);
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) return 2;
    enum mode mode;
    if (!strcmp(argv[1], "control")) mode = CONTROL_FULL;
    else if (!strcmp(argv[1], "candidate")) mode = CANDIDATE_FULL;
    else if (!strcmp(argv[1], "control-bm")) mode = CONTROL_BM;
    else if (!strcmp(argv[1], "candidate-qbm")) mode = CANDIDATE_QBM;
    else if (!strcmp(argv[1], "control-inverse")) mode = CONTROL_INVERSE;
    else if (!strcmp(argv[1], "candidate-inverse")) mode = CANDIDATE_INVERSE;
    else if (!strcmp(argv[1], "control-cross")) mode = CONTROL_CROSS;
    else if (!strcmp(argv[1], "control-norm")) mode = CONTROL_NORM;
    else if (!strcmp(argv[1], "candidate-naturalize")) mode = CANDIDATE_NATURALIZE;
    else if (!strcmp(argv[1], "candidate-inv64")) mode = CANDIDATE_INV64;
    else if (!strcmp(argv[1], "candidate-convert")) mode = CANDIDATE_CONVERT;
    else return 2;
    uint64_t s = UINT64_C(0x081123456789abcd);
    for (unsigned i = 0; i < GATE_WORDS; ++i) {
        s ^= s << 7; s ^= s >> 9;
        a[i] = (int16_t)((int)(s % 3457U) - 1728);
        s ^= s << 7; s ^= s >> 9;
        b[i] = (int16_t)((int)(s % 3457U) - 1728);
    }
    if (mode == CONTROL_INVERSE || mode == CONTROL_CROSS || mode == CONTROL_NORM)
        late_soa_basemul_i2_fused_asm(t, a, b);
    if (mode == CONTROL_NORM) control_inverse_cross3_asm(out, t);
    if (mode == CANDIDATE_INVERSE || mode == CANDIDATE_NATURALIZE ||
        mode == CANDIDATE_INV64 || mode == CANDIDATE_CONVERT)
        d2_inverse64_qbm_asm(t, a, b);
    if (mode == CANDIDATE_INV64 || mode == CANDIDATE_CONVERT)
        d2_inverse64_naturalize_asm(u, t);
    if (mode == CANDIDATE_CONVERT) d2_inverse64_inv_asm(h, u);
    for (unsigned i = 0; i < 4096; ++i) call_variant(mode);
    for (unsigned k = 0; k < TIMINGS; ++k) {
        uint64_t begin = cycles();
        for (unsigned i = 0; i < INNER; ++i) {
            call_variant(mode);
            sink += (uint16_t)out[(i + k) & 127U];
        }
        uint64_t end = cycles();
        printf("%llu\n", (unsigned long long)((end - begin) / INNER));
    }
    return sink == UINT64_MAX;
}
