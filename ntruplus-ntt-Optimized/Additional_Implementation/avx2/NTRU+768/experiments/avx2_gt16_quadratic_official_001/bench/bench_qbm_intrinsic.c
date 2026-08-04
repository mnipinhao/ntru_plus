#define _GNU_SOURCE
#include "qbm_intrinsic.h"
#include "inverse_stage1_intrinsic.h"
#include "transpose_intrinsic.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { SAMPLES = 20, DEFAULT_ITERATIONS = 20000 };

typedef void (*binary_kernel)(int16_t *, const int16_t *, const int16_t *);
typedef void (*unary_kernel)(int16_t *, const int16_t *);

void gt_basemul_native_rminus1_c0lazy_asm_avx2(
    int16_t out[768], const int16_t a[768], const int16_t b[768]);
void gt_invntt_soa_avx2_fused_asm(int16_t out[768], const int16_t in[768]);

static volatile uint64_t sink;

static uint64_t start_tsc(void)
{
    _mm_lfence();
    return __rdtsc();
}

static uint64_t stop_tsc(void)
{
    unsigned aux;
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static int compare_u64(const void *left, const void *right)
{
    const uint64_t a = *(const uint64_t *)left;
    const uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static double median(uint64_t values[SAMPLES])
{
    uint64_t copy[SAMPLES];
    memcpy(copy, values, sizeof(copy));
    qsort(copy, SAMPLES, sizeof(copy[0]), compare_u64);
    return 0.5 * (copy[SAMPLES / 2 - 1] + copy[SAMPLES / 2]);
}

static void pin_cpu1(void)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    (void)sched_setaffinity(0, sizeof(set), &set);
}

static void fill_inputs(int16_t *a, int16_t *b)
{
    uint32_t state = 0x51424d34u;
    for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
        state = state * 1664525u + 1013904223u;
        a[i] = (int16_t)((int)(state % 3457) - 1728);
        state = state * 1664525u + 1013904223u;
        b[i] = (int16_t)((int)(state % 3457) - 1728);
    }
}

static double bench_binary(binary_kernel kernel, int16_t *out,
                           const int16_t *a, const int16_t *b,
                           size_t iterations)
{
    uint64_t samples[SAMPLES];
    for (size_t warm = 0; warm < 2; ++warm)
        for (size_t i = 0; i < iterations / 10 + 1; ++i)
            kernel(out, a, b);
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        const uint64_t begin = start_tsc();
        for (size_t i = 0; i < iterations; ++i)
            kernel(out, a, b);
        samples[sample] = stop_tsc() - begin;
        sink += (uint16_t)out[(17 * sample) % ROUND4C_WORDS];
    }
    return median(samples) / iterations;
}

static double bench_unary(unary_kernel kernel, int16_t *out,
                          const int16_t *in, size_t iterations)
{
    uint64_t samples[SAMPLES];
    for (size_t warm = 0; warm < 2; ++warm)
        for (size_t i = 0; i < iterations / 10 + 1; ++i)
            kernel(out, in);
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        const uint64_t begin = start_tsc();
        for (size_t i = 0; i < iterations; ++i)
            kernel(out, in);
        samples[sample] = stop_tsc() - begin;
        sink += (uint16_t)out[(19 * sample) % ROUND4C_WORDS];
    }
    return median(samples) / iterations;
}

static int16_t scratch_a[ROUND4C_WORDS] __attribute__((aligned(32)));
static int16_t scratch_b[ROUND4C_WORDS] __attribute__((aligned(32)));
static int16_t scratch_product[ROUND4C_WORDS] __attribute__((aligned(32)));
static int16_t scratch_old_a[ROUND4C_WORDS] __attribute__((aligned(32)));
static int16_t scratch_old_b[ROUND4C_WORDS] __attribute__((aligned(32)));

static __attribute__((noinline, noclone))
void terminal_vector(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_split_intrinsic(scratch_a, a);
    round4c_split_intrinsic(scratch_b, b);
    round4c_qbm_vector_intrinsic(scratch_product, scratch_a, scratch_b);
    round4c_merge2_intrinsic(out, scratch_product);
}

static __attribute__((noinline, noclone))
void terminal_interleaved4(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_split_intrinsic(scratch_a, a);
    round4c_split_intrinsic(scratch_b, b);
    round4c_qbm_interleaved4_intrinsic(scratch_product, scratch_a, scratch_b);
    round4c_merge2_intrinsic(out, scratch_product);
}

static __attribute__((noinline, noclone))
void terminal_interleaved8(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_split_intrinsic(scratch_a, a);
    round4c_split_intrinsic(scratch_b, b);
    round4c_qbm_interleaved8_intrinsic(scratch_product, scratch_a, scratch_b);
    round4c_merge2_intrinsic(out, scratch_product);
}

static __attribute__((noinline, noclone))
void terminal_old_quartic(int16_t *out, const int16_t *a, const int16_t *b)
{
    round4c_vertical_to_soa(scratch_old_a, a);
    round4c_vertical_to_soa(scratch_old_b, b);
    gt_basemul_native_rminus1_c0lazy_asm_avx2(
        scratch_product, scratch_old_a, scratch_old_b);
    round4c_soa_to_vertical(out, scratch_product);
}

int main(int argc, char **argv)
{
    size_t iterations = DEFAULT_ITERATIONS;
    int reverse = 0;
    int inverse_only = 0;
    for (int arg = 1; arg < argc; ++arg) {
        if (strcmp(argv[arg], "--iterations") == 0 && arg + 1 < argc)
            iterations = strtoull(argv[++arg], NULL, 10);
        else if (strcmp(argv[arg], "--reverse") == 0)
            reverse = 1;
        else if (strcmp(argv[arg], "--inverse-only") == 0)
            inverse_only = 1;
        else {
            fprintf(stderr,
                    "usage: %s [--iterations N] [--reverse] [--inverse-only]\n",
                    argv[0]);
            return 2;
        }
    }
    pin_cpu1();
    int16_t a[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t b[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t qa[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t qb[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t out[ROUND4C_WORDS] __attribute__((aligned(32)));
    fill_inputs(a, b);
    round4c_split_intrinsic(qa, a);
    round4c_split_intrinsic(qb, b);
    round4c_qbm_vector_intrinsic(scratch_product, qa, qb);

    if (inverse_only) {
        double stage_i0;
        double stage_i1;
        double ntt16_i0;
        double ntt16_i1;
        double full_i0;
        double frozen_inverse;
        if (reverse) {
            stage_i1 = bench_unary(round4c_inverse_stage1_i1, out,
                                   scratch_product, iterations);
            stage_i0 = bench_unary(round4c_inverse_stage1_i0, out,
                                   scratch_product, iterations);
            ntt16_i1 = bench_unary(round4c_inverse_ntt16_i1, out,
                                   scratch_product, iterations);
            ntt16_i0 = bench_unary(round4c_inverse_ntt16_i0, out,
                                   scratch_product, iterations);
            full_i0 = bench_unary(round4c_inverse_full_i0, out,
                                  scratch_product, iterations);
            frozen_inverse = bench_unary(gt_invntt_soa_avx2_fused_asm, out,
                                         scratch_product, iterations);
        } else {
            stage_i0 = bench_unary(round4c_inverse_stage1_i0, out,
                                   scratch_product, iterations);
            stage_i1 = bench_unary(round4c_inverse_stage1_i1, out,
                                   scratch_product, iterations);
            ntt16_i0 = bench_unary(round4c_inverse_ntt16_i0, out,
                                   scratch_product, iterations);
            ntt16_i1 = bench_unary(round4c_inverse_ntt16_i1, out,
                                   scratch_product, iterations);
            frozen_inverse = bench_unary(gt_invntt_soa_avx2_fused_asm, out,
                                         scratch_product, iterations);
            full_i0 = bench_unary(round4c_inverse_full_i0, out,
                                  scratch_product, iterations);
        }
        printf("{\n");
        printf("  \"iterations\": %zu,\n", iterations);
        printf("  \"boundary_order\": \"%s\",\n",
               reverse ? "i1-i0" : "i0-i1");
        printf("  \"inverse_i0_merge_then_stage1_tsc\": %.3f,\n", stage_i0);
        printf("  \"inverse_i1_fused_merge_stage1_tsc\": %.3f,\n", stage_i1);
        printf("  \"inverse_ntt16_i0_tsc\": %.3f,\n", ntt16_i0);
        printf("  \"inverse_ntt16_i1_tsc\": %.3f,\n", ntt16_i1);
        printf("  \"inverse_full_i0_tsc\": %.3f,\n", full_i0);
        printf("  \"frozen_gt32_inverse_tsc\": %.3f,\n", frozen_inverse);
        printf("  \"sink\": %llu\n", (unsigned long long)sink);
        printf("}\n");
        return 0;
    }

    printf("{\n");
    printf("  \"iterations\": %zu,\n", iterations);
    printf("  \"boundary_order\": \"%s\",\n", reverse ? "new-old" : "old-new");
    printf("  \"split_tsc\": %.3f,\n",
           bench_unary(round4c_split_intrinsic, out, a, iterations));
    printf("  \"qbm_vector_tsc\": %.3f,\n",
           bench_binary(round4c_qbm_vector_intrinsic, out, qa, qb, iterations));
    printf("  \"qbm_interleaved4_tsc\": %.3f,\n",
           bench_binary(round4c_qbm_interleaved4_intrinsic, out, qa, qb, iterations));
    printf("  \"qbm_interleaved8_tsc\": %.3f,\n",
           bench_binary(round4c_qbm_interleaved8_intrinsic, out, qa, qb, iterations));
    printf("  \"merge2_tsc\": %.3f,\n",
           bench_unary(round4c_merge2_intrinsic, out, scratch_product, iterations));
    double inverse_i0;
    double inverse_i1;
    if (reverse) {
        inverse_i1 = bench_unary(round4c_inverse_stage1_i1, out,
                                 scratch_product, iterations);
        inverse_i0 = bench_unary(round4c_inverse_stage1_i0, out,
                                 scratch_product, iterations);
    } else {
        inverse_i0 = bench_unary(round4c_inverse_stage1_i0, out,
                                 scratch_product, iterations);
        inverse_i1 = bench_unary(round4c_inverse_stage1_i1, out,
                                 scratch_product, iterations);
    }
    printf("  \"inverse_i0_merge_then_stage1_tsc\": %.3f,\n", inverse_i0);
    printf("  \"inverse_i1_fused_merge_stage1_tsc\": %.3f,\n", inverse_i1);
    double inverse_ntt16_i0;
    double inverse_ntt16_i1;
    if (reverse) {
        inverse_ntt16_i1 = bench_unary(round4c_inverse_ntt16_i1, out,
                                       scratch_product, iterations);
        inverse_ntt16_i0 = bench_unary(round4c_inverse_ntt16_i0, out,
                                       scratch_product, iterations);
    } else {
        inverse_ntt16_i0 = bench_unary(round4c_inverse_ntt16_i0, out,
                                       scratch_product, iterations);
        inverse_ntt16_i1 = bench_unary(round4c_inverse_ntt16_i1, out,
                                       scratch_product, iterations);
    }
    printf("  \"inverse_ntt16_i0_tsc\": %.3f,\n", inverse_ntt16_i0);
    printf("  \"inverse_ntt16_i1_tsc\": %.3f,\n", inverse_ntt16_i1);
    printf("  \"inverse_full_i0_tsc\": %.3f,\n",
           bench_unary(round4c_inverse_full_i0, out,
                       scratch_product, iterations));
    double old_terminal;
    double new4_terminal;
    if (reverse) {
        new4_terminal = bench_binary(terminal_interleaved4, out, a, b, iterations);
        old_terminal = bench_binary(terminal_old_quartic, out, a, b, iterations);
    } else {
        old_terminal = bench_binary(terminal_old_quartic, out, a, b, iterations);
        new4_terminal = bench_binary(terminal_interleaved4, out, a, b, iterations);
    }
    printf("  \"old_transpose_quartic_transpose_tsc\": %.3f,\n", old_terminal);
    printf("  \"terminal_vector_tsc\": %.3f,\n",
           bench_binary(terminal_vector, out, a, b, iterations));
    printf("  \"terminal_interleaved4_tsc\": %.3f,\n", new4_terminal);
    printf("  \"terminal_interleaved8_tsc\": %.3f,\n",
           bench_binary(terminal_interleaved8, out, a, b, iterations));
    printf("  \"sink\": %llu\n", (unsigned long long)sink);
    printf("}\n");
    return 0;
}
