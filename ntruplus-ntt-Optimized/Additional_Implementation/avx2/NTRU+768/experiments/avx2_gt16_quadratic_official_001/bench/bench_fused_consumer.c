#define _GNU_SOURCE
#include "inverse_stage1_intrinsic.h"
#include "qbm_intrinsic.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { WORDS = 768, SAMPLES = 9, DEFAULT_ITERATIONS = 2000 };
typedef void (*kernel)(int16_t *, const int16_t *, const int16_t *);
static int16_t product[WORDS] __attribute__((aligned(32)));
static int16_t native_a[WORDS] __attribute__((aligned(32)));
static int16_t native_b[WORDS] __attribute__((aligned(32)));
static int16_t quadratic_bench[WORDS] __attribute__((aligned(32)));
static volatile uint64_t sink;

void poly_basemul_scale(int16_t *out, const int16_t *a, const int16_t *b);
void poly_invntt_scale(int16_t *values);
void gt_basemul_native_rminus1_c0lazy_asm_avx2(
    int16_t *out, const int16_t *a, const int16_t *b);
void gt_invntt_soa_avx2_fused_asm(int16_t *out, const int16_t *in);

static void baseline_stage1(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_qbm_wide_centered_intrinsic(product, a, b);
    round4c_inverse_stage1_i0(out, product);
}

static void fused_stage1(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_qbm_inverse_stage1_fused_asm(out, a, b);
}

static void stage1_c_only(int16_t *out, const int16_t *a, const int16_t *b)
{
    (void)a;
    (void)b;
    round4c_inverse_stage1_i0(out, quadratic_bench);
}

static void stage1_asm_only(int16_t *out, const int16_t *a, const int16_t *b)
{
    (void)a;
    (void)b;
    round4c_inverse_stage1_asm(out, quadratic_bench);
}

static void inverse_hybrid_only(int16_t *out, const int16_t *a,
                                const int16_t *b)
{
    (void)a;
    (void)b;
    round4c_inverse_full_i0_ntt16_asm(out, quadratic_bench);
}

static void inverse_all_asm_only(int16_t *out, const int16_t *a,
                                 const int16_t *b)
{
    (void)a;
    (void)b;
    round4c_inverse_full_asm(out, quadratic_bench);
}

static void inverse_asm_tail_only(int16_t *out, const int16_t *a,
                                  const int16_t *b)
{
    (void)a;
    (void)b;
    round4c_inverse_full_i0_finish_asm(out, quadratic_bench);
}

static void baseline_ntt16(int16_t *out, const int16_t *a, const int16_t *b)
{
    baseline_stage1(out, a, b);
    round4c_inverse_ntt16_layers_reference(out);
}

static void fused_ntt16(int16_t *out, const int16_t *a, const int16_t *b)
{
    fused_stage1(out, a, b);
    round4c_inverse_ntt16_layers_asm(out);
}

static void baseline_full(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_qbm_wide_centered_intrinsic(product, a, b);
    round4c_inverse_full_i0(out, product);
}

static void fused_full(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_qbm_inverse_full_fused(out, a, b);
}

static void hybrid_full(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_qbm_wide4_centered_asm(product, a, b);
    round4c_inverse_full_i0_ntt16_asm(out, product);
}

static void all_asm_full(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_qbm_wide4_centered_asm(product, a, b);
    round4c_inverse_full_asm(out, product);
}

static void rminus1_lazy_hybrid_full(int16_t *out, const int16_t *a,
                                     const int16_t *b)
{
    round4c_qbm_wide4_asm(product, a, b);
    round4c_inverse_full_wide_hybrid(out, product);
}

static void rminus1_lazy_all_asm_full(int16_t *out, const int16_t *a,
                                      const int16_t *b)
{
    round4c_qbm_wide4_asm(product, a, b);
    round4c_inverse_full_wide_asm(out, product);
}

static void official_full(int16_t *out, const int16_t *a, const int16_t *b)
{
    (void)a;
    (void)b;
    poly_basemul_scale(out, native_a, native_b);
    poly_invntt_scale(out);
}

static void frozen_full(int16_t *out, const int16_t *a, const int16_t *b)
{
    (void)a;
    (void)b;
    gt_basemul_native_rminus1_c0lazy_asm_avx2(product, native_a, native_b);
    gt_invntt_soa_avx2_fused_asm(out, product);
}

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static int compare(const void *a, const void *b)
{
    const uint64_t x = *(const uint64_t *)a;
    const uint64_t y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static uint64_t run(kernel fn, int16_t *out, const int16_t *a,
                    const int16_t *b, size_t iterations)
{
    const uint64_t begin = ticks();
    for (size_t i = 0; i < iterations; ++i)
        fn(out, a, b);
    const uint64_t elapsed = ticks() - begin;
    sink += (uint16_t)out[37];
    return elapsed;
}

static void paired(const char *label, kernel baseline, kernel candidate,
                   int16_t *out, const int16_t *a, const int16_t *b,
                   size_t iterations)
{
    uint64_t old[SAMPLES], new[SAMPLES];
    for (size_t warm = 0; warm < 2; ++warm)
        for (size_t i = 0; i < 32; ++i) {
            baseline(out, a, b);
            candidate(out, a, b);
        }
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        if (sample & 1) {
            new[sample] = run(candidate, out, a, b, iterations);
            old[sample] = run(baseline, out, a, b, iterations);
        } else {
            old[sample] = run(baseline, out, a, b, iterations);
            new[sample] = run(candidate, out, a, b, iterations);
        }
    }
    qsort(old, SAMPLES, sizeof(old[0]), compare);
    qsort(new, SAMPLES, sizeof(new[0]), compare);
    const double a0 = (double)old[SAMPLES / 2] / iterations;
    const double a1 = (double)new[SAMPLES / 2] / iterations;
    printf("  \"%s_baseline_tsc\": %.4f,\n", label, a0);
    printf("  \"%s_fused_asm_tsc\": %.4f,\n", label, a1);
    printf("  \"%s_delta_percent\": %.4f,\n", label,
           100.0 * (a1 - a0) / a0);
}

int main(int argc, char **argv)
{
    size_t iterations = DEFAULT_ITERATIONS;
    if (argc == 3 && strcmp(argv[1], "--iterations") == 0)
        iterations = strtoull(argv[2], NULL, 10);
    else if (argc != 1) {
        fprintf(stderr, "usage: %s [--iterations N]\n", argv[0]);
        return 2;
    }
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    (void)sched_setaffinity(0, sizeof(set), &set);
    int16_t a[WORDS] __attribute__((aligned(32)));
    int16_t b[WORDS] __attribute__((aligned(32)));
    int16_t old[WORDS] __attribute__((aligned(32)));
    int16_t new[WORDS] __attribute__((aligned(32)));
    uint32_t state = 0x46555345u;
    for (size_t i = 0; i < WORDS; ++i) {
        state = state * 1664525u + 1013904223u;
        a[i] = (int16_t)((int)(state % 32515) - 16257);
        state = state * 1664525u + 1013904223u;
        b[i] = (int16_t)((int)(state % 32515) - 16257);
        state = state * 1664525u + 1013904223u;
        native_a[i] = (int16_t)((int)(state % 3457) - 1728);
        state = state * 1664525u + 1013904223u;
        native_b[i] = (int16_t)((int)(state % 3457) - 1728);
    }
    baseline_stage1(old, a, b);
    fused_stage1(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    baseline_ntt16(old, a, b);
    fused_ntt16(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    baseline_full(old, a, b);
    fused_full(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    hybrid_full(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    all_asm_full(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    rminus1_lazy_hybrid_full(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    rminus1_lazy_all_asm_full(new, a, b);
    if (memcmp(old, new, sizeof(old)) != 0)
        return 1;
    round4c_qbm_wide4_centered_asm(quadratic_bench, a, b);
    printf("{\n  \"iterations\": %zu,\n", iterations);
    paired("qbm4", round4c_qbm_vector_intrinsic, round4c_qbm_wide4_asm,
           new, a, b, iterations);
    paired("qbm4_centered", round4c_qbm_wide_centered_intrinsic,
           round4c_qbm_wide4_centered_asm, new, a, b, iterations);
    paired("stage1", baseline_stage1, fused_stage1, new, a, b, iterations);
    paired("stage1_c_vs_asm", stage1_c_only, stage1_asm_only,
           new, a, b, iterations);
    paired("inverse_hybrid_vs_all_asm", inverse_hybrid_only,
           inverse_all_asm_only, new, a, b, iterations);
    paired("inverse_c_tail_vs_asm_tail", inverse_hybrid_only,
           inverse_asm_tail_only, new, a, b, iterations);
    paired("through_ntt16", baseline_ntt16, fused_ntt16,
           new, a, b, iterations);
    paired("through_full_inverse", baseline_full, fused_full,
           new, a, b, iterations);
    paired("through_full_hybrid", baseline_full, hybrid_full,
           new, a, b, iterations);
    paired("hybrid_vs_all_asm", hybrid_full, all_asm_full,
           new, a, b, iterations);
    paired("centered_vs_rminus1_lazy_hybrid", hybrid_full,
           rminus1_lazy_hybrid_full, new, a, b, iterations);
    paired("centered_vs_rminus1_lazy_all_asm", hybrid_full,
           rminus1_lazy_all_asm_full, new, a, b, iterations);
    paired("rminus1_lazy_hybrid_vs_all_asm", rminus1_lazy_hybrid_full,
           rminus1_lazy_all_asm_full, new, a, b, iterations);
    paired("official_vs_all_asm", official_full, all_asm_full,
           new, a, b, iterations);
    paired("frozen_gt32_vs_all_asm", frozen_full, all_asm_full,
           new, a, b, iterations);
    paired("official_vs_rminus1_lazy", official_full,
           rminus1_lazy_all_asm_full, new, a, b, iterations);
    paired("frozen_gt32_vs_rminus1_lazy", frozen_full,
           rminus1_lazy_all_asm_full, new, a, b, iterations);
    printf("  \"sink\": %llu\n}\n", (unsigned long long)sink);
    return 0;
}
