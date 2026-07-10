#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void invntt_stage123_stage45_stripe0_baseline(int16_t *out, const poly *in,
                                               int16_t *scratch);
void invntt_stage123_stage45_stripe0_fused(int16_t *out, const poly *in,
                                            int16_t *scratch);
void invntt_stage45_post_stripe0_baseline(int16_t *out, const int16_t *row0,
                                           const int16_t *row1,
                                           const int16_t *stage123_scratch);
void invntt_stage45_post_stripe0_handoff(int16_t *out, const int16_t *row0,
                                          const int16_t *row1,
                                          const int16_t *stage123_scratch);

static uint32_t state = 0x45a1235au;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void fill_small(poly *a)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        a->coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
}

static int compare_bytes(const char *name, const void *want, const void *got,
                         size_t bytes)
{
    const uint8_t *a = want;
    const uint8_t *b = got;
    int mismatches = 0;
    for (size_t i = 0; i < bytes; i++) {
        if (a[i] != b[i]) {
            if (mismatches < 8)
                printf("%s mismatch[%zu]: want=%u got=%u\n", name, i,
                       (unsigned)a[i], (unsigned)b[i]);
            mismatches++;
        }
    }
    return mismatches;
}

int main(void)
{
    poly a, b, antt, bntt, product;
    _Alignas(16) int16_t scratch0[256], scratch1[256];
    _Alignas(16) int16_t row0[8], row1[8], stage123[32];
    _Alignas(16) int16_t out0[NTRUPLUS_N], out1[NTRUPLUS_N];
    int mismatches = 0;

    for (int t = 0; t < 516; t++) {
        fill_small(&a);
        fill_small(&b);
        poly_ntt(&antt, &a);
        poly_ntt(&bntt, &b);
        poly_basemul_rminus1(&product, &antt, &bntt);
        memset(scratch0, 0x5a, sizeof scratch0);
        memset(scratch1, 0xa5, sizeof scratch1);
        memset(out0, 0x3c, sizeof out0);
        memset(out1, 0x3c, sizeof out1);
        invntt_stage123_stage45_stripe0_baseline(out0, &product, scratch0);
        invntt_stage123_stage45_stripe0_fused(out1, &product, scratch1);
        mismatches += compare_bytes("stage123_stage45", out0, out1,
                                    sizeof out0);

        for (int i = 0; i < 8; i++) {
            row0[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
            row1[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
        }
        for (int i = 0; i < 32; i++)
            stage123[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
        memset(out0, 0x69, sizeof out0);
        memset(out1, 0x69, sizeof out1);
        invntt_stage45_post_stripe0_baseline(out0, row0, row1, stage123);
        invntt_stage45_post_stripe0_handoff(out1, row0, row1, stage123);
        mismatches += compare_bytes("stage45_post", out0, out1, sizeof out0);
    }

    printf("invntt_boundary_mismatches=%d\n", mismatches);
    return mismatches == 0 ? 0 : 1;
}
