#define _GNU_SOURCE
#include "forward_intrinsic.h"
#include "qbm_intrinsic.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { SAMPLES = 20, KERNELS = 8, DEFAULT_ITERATIONS = 20000 };

typedef void (*forward_kernel)(int16_t *, const int16_t *);

void gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
    int16_t out[768], const int16_t in[768]);

static volatile uint64_t sink;
static int16_t stage_zero[768] __attribute__((aligned(32)));
static int16_t stage_zero_asm[768] __attribute__((aligned(32)));

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

static double median20(const uint64_t input[SAMPLES])
{
    uint64_t values[SAMPLES];
    memcpy(values, input, sizeof(values));
    qsort(values, SAMPLES, sizeof(values[0]), compare_u64);
    return 0.5 * (values[9] + values[10]);
}

static double mad20(const uint64_t input[SAMPLES], double median)
{
    uint64_t deviations[SAMPLES];
    for (size_t i = 0; i < SAMPLES; ++i) {
        const double delta = input[i] > median ? input[i] - median
                                               : median - input[i];
        deviations[i] = (uint64_t)(delta + 0.5);
    }
    return median20(deviations);
}

static void pin_cpu1(void)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    (void)sched_setaffinity(0, sizeof(set), &set);
}

static void dft3_centered_kernel(int16_t *out, const int16_t *in)
{
    round4c_forward_dft3_intrinsic(out, in, 1);
}

static void ntt16_zero_kernel(int16_t *out, const int16_t *in)
{
    (void)in;
    round4c_forward_ntt16_intrinsic(out);
}

static void ntt16_zero_asm_kernel(int16_t *out, const int16_t *in)
{
    (void)in;
    round4c_forward_ntt16_asm(out);
}

static void measure_kernel(forward_kernel kernel, int16_t *out,
                           const int16_t *in, size_t iterations,
                           double *result_median, double *result_mad)
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
        sink += (uint16_t)out[(31 * sample) % 768];
    }
    const double med_ticks = median20(samples);
    *result_median = med_ticks / iterations;
    *result_mad = mad20(samples, med_ticks) / iterations;
}

int main(int argc, char **argv)
{
    size_t iterations = DEFAULT_ITERATIONS;
    int reverse = 0;
    int stages_only = 0;
    for (int arg = 1; arg < argc; ++arg) {
        if (strcmp(argv[arg], "--iterations") == 0 && arg + 1 < argc)
            iterations = strtoull(argv[++arg], NULL, 10);
        else if (strcmp(argv[arg], "--reverse") == 0)
            reverse = 1;
        else if (strcmp(argv[arg], "--stages-only") == 0)
            stages_only = 1;
        else {
            fprintf(stderr,
                    "usage: %s [--iterations N] [--reverse] [--stages-only]\n",
                    argv[0]);
            return 2;
        }
    }
    static const forward_kernel kernels[KERNELS] = {
        gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
        round4c_forward_f0_materialized,
        round4c_forward_f0_fused,
        round4c_forward_f1_materialized,
        round4c_forward_f1_fused,
        round4c_forward_f1_hybrid_asm,
        round4c_forward_f1_full_asm,
        round4c_forward_f1_mlkem_sched_asm,
    };
    static const char *const names[KERNELS] = {
        "frozen_gt32", "f0_materialized", "f0_fused",
        "f1_materialized", "f1_fused",
        "f1_hybrid_asm", "f1_full_asm", "f1_mlkem_sched_asm",
    };
    int16_t input[768] __attribute__((aligned(32)));
    int16_t output[768] __attribute__((aligned(32)));
    int16_t stage_input[768] __attribute__((aligned(32)));
    uint64_t ticks[KERNELS][SAMPLES];
    uint32_t state = 0x46574434u;
    for (size_t i = 0; i < 768; ++i) {
        state = state * 1664525u + 1013904223u;
        input[i] = (int16_t)((int)(state & 7) - 3);
    }
    pin_cpu1();
    if (!stages_only) {
        for (size_t kernel = 0; kernel < KERNELS; ++kernel)
            for (size_t warm = 0; warm < 2; ++warm)
                for (size_t i = 0; i < iterations / 10 + 1; ++i)
                    kernels[kernel](output, input);
        for (size_t sample = 0; sample < SAMPLES; ++sample) {
            for (size_t position = 0; position < KERNELS; ++position) {
                const size_t kernel = reverse ? KERNELS - 1 - position : position;
                const uint64_t begin = start_tsc();
                for (size_t i = 0; i < iterations; ++i)
                    kernels[kernel](output, input);
                ticks[kernel][sample] = stop_tsc() - begin;
                sink += (uint16_t)output[(17 * sample + kernel) % 768];
            }
        }
    }
    round4c_forward_frontend_intrinsic(stage_input, input);
    double stage_median[5], stage_mad[5];
    measure_kernel(round4c_forward_frontend_intrinsic, output, input,
                   iterations, &stage_median[0], &stage_mad[0]);
    measure_kernel(dft3_centered_kernel, output, stage_input,
                   iterations, &stage_median[1], &stage_mad[1]);
    measure_kernel(ntt16_zero_kernel, stage_zero, stage_input,
                   iterations, &stage_median[2], &stage_mad[2]);
    measure_kernel(ntt16_zero_asm_kernel, stage_zero_asm, stage_input,
                   iterations, &stage_median[3], &stage_mad[3]);
    measure_kernel(round4c_split_intrinsic, output, stage_input,
                   iterations, &stage_median[4], &stage_mad[4]);
    printf("{\n  \"iterations\": %zu,\n  \"order\": \"%s\",\n",
           iterations, reverse ? "reverse" : "forward");
    if (!stages_only) {
        for (size_t kernel = 0; kernel < KERNELS; ++kernel) {
            const double med_ticks = median20(ticks[kernel]);
            const double mad_ticks = mad20(ticks[kernel], med_ticks);
            printf("  \"%s_tsc\": %.4f,\n", names[kernel], med_ticks / iterations);
            printf("  \"%s_mad\": %.4f,\n", names[kernel],
                   mad_ticks / iterations);
        }
    }
    printf("  \"stage_frontend_tsc\": %.4f,\n", stage_median[0]);
    printf("  \"stage_frontend_mad\": %.4f,\n", stage_mad[0]);
    printf("  \"stage_dft3_centered_tsc\": %.4f,\n", stage_median[1]);
    printf("  \"stage_dft3_centered_mad\": %.4f,\n", stage_mad[1]);
    printf("  \"stage_ntt16_zero_tsc\": %.4f,\n", stage_median[2]);
    printf("  \"stage_ntt16_zero_mad\": %.4f,\n", stage_mad[2]);
    printf("  \"stage_ntt16_asm_zero_tsc\": %.4f,\n", stage_median[3]);
    printf("  \"stage_ntt16_asm_zero_mad\": %.4f,\n", stage_mad[3]);
    printf("  \"stage_split_tsc\": %.4f,\n", stage_median[4]);
    printf("  \"stage_split_mad\": %.4f,\n", stage_mad[4]);
    printf("  \"sink\": %llu\n}\n", (unsigned long long)sink);
    return 0;
}
