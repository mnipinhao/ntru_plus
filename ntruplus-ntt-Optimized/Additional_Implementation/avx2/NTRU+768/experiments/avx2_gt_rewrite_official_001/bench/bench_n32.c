#define _GNU_SOURCE
#include <errno.h>
#include <immintrin.h>
#include <inttypes.h>
#include <math.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt_backend.h"

enum {
    DEFAULT_SAMPLES = 20,
    MAX_SAMPLES = 64,
};

typedef void (*row_kernel)(int16_t out[32][16],
                           const int16_t in[32][16]);

static volatile uint64_t checksum_sink;

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static int compare_double(const void *left, const void *right)
{
    const double a = *(const double *)left;
    const double b = *(const double *)right;
    return (a > b) - (a < b);
}

static double median(const double *values, unsigned count)
{
    double copy[MAX_SAMPLES];
    memcpy(copy, values, count * sizeof *copy);
    qsort(copy, count, sizeof *copy, compare_double);
    if (count & 1U)
        return copy[count / 2];
    return (copy[count / 2 - 1] + copy[count / 2]) / 2.0;
}

static double mad(const double *values, unsigned count, double center)
{
    double deviations[MAX_SAMPLES];
    for (unsigned i = 0; i < count; ++i)
        deviations[i] = fabs(values[i] - center);
    return median(deviations, count);
}

static double measure(row_kernel kernel, uint64_t iterations,
                      int16_t output[32][16], const int16_t input[32][16])
{
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        kernel(output, input);
    const uint64_t end = ticks();
    uint64_t checksum = 0;
    for (size_t i = 0; i < 32; ++i)
        checksum = checksum * 131U + (uint16_t)output[i][i & 15U];
    checksum_sink ^= checksum;
    return (double)(end - begin) / (double)iterations;
}

static int pin_cpu1(void)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    return sched_setaffinity(0, sizeof set, &set);
}

int main(int argc, char **argv)
{
    uint64_t iterations = UINT64_C(1000000);
    unsigned samples = DEFAULT_SAMPLES;
    const char *candidate = "paired";
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc)
            iterations = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc)
            samples = (unsigned)strtoul(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--candidate") == 0 && i + 1 < argc)
            candidate = argv[++i];
        else {
            fprintf(stderr,
                    "usage: %s [--iterations N] [--samples N] [--candidate paired|B1|B2]\n",
                    argv[0]);
            return 2;
        }
    }
    if (iterations == 0 || samples == 0 || samples > MAX_SAMPLES) {
        fprintf(stderr, "invalid benchmark dimensions\n");
        return 2;
    }
    if (pin_cpu1() != 0) {
        fprintf(stderr, "sched_setaffinity(cpu=1): %s\n", strerror(errno));
        return 2;
    }

    _Alignas(32) int16_t input[32][16];
    _Alignas(32) int16_t output[32][16];
    for (size_t i = 0; i < 32; ++i)
        for (size_t lane = 0; lane < 16; ++lane)
            input[i][lane] = (int16_t)(((int)(97 * i + 53 * lane) % 3457) - 1728);

    if (strcmp(candidate, "B1") == 0 || strcmp(candidate, "B2") == 0) {
        const row_kernel kernel = strcmp(candidate, "B1") == 0
            ? gt_avx2_ntt32_b1_rows : gt_avx2_ntt32_b2_rows;
        for (unsigned warmup = 0; warmup < 2; ++warmup)
            (void)measure(kernel, iterations, output,
                          (const int16_t (*)[16])input);
        double values[MAX_SAMPLES];
        for (unsigned sample = 0; sample < samples; ++sample)
            values[sample] = measure(kernel, iterations, output,
                                     (const int16_t (*)[16])input);
        const double center = median(values, samples);
        printf("{\n");
        printf("  \"schema_version\": 1,\n");
        printf("  \"candidate\": \"%s\",\n", candidate);
        printf("  \"cpu\": 1,\n");
        printf("  \"iterations_per_sample\": %" PRIu64 ",\n", iterations);
        printf("  \"warmups\": 2,\n");
        printf("  \"samples\": %u,\n", samples);
        printf("  \"median_cycles\": %.3f,\n", center);
        printf("  \"mad_cycles\": %.3f,\n", mad(values, samples, center));
        printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
        printf("}\n");
        return 0;
    }
    if (strcmp(candidate, "paired") != 0) {
        fprintf(stderr, "candidate must be paired, B1, or B2\n");
        return 2;
    }

    for (unsigned warmup = 0; warmup < 2; ++warmup) {
        (void)measure(gt_avx2_ntt32_b1_rows, iterations, output,
                      (const int16_t (*)[16])input);
        (void)measure(gt_avx2_ntt32_b2_rows, iterations, output,
                      (const int16_t (*)[16])input);
    }

    double b1[MAX_SAMPLES];
    double b2[MAX_SAMPLES];
    for (unsigned sample = 0; sample < samples; ++sample) {
        if ((sample & 1U) == 0) {
            b1[sample] = measure(gt_avx2_ntt32_b1_rows, iterations, output,
                                 (const int16_t (*)[16])input);
            b2[sample] = measure(gt_avx2_ntt32_b2_rows, iterations, output,
                                 (const int16_t (*)[16])input);
        } else {
            b2[sample] = measure(gt_avx2_ntt32_b2_rows, iterations, output,
                                 (const int16_t (*)[16])input);
            b1[sample] = measure(gt_avx2_ntt32_b1_rows, iterations, output,
                                 (const int16_t (*)[16])input);
        }
    }

    const double b1_median = median(b1, samples);
    const double b2_median = median(b2, samples);
    const double b1_mad = mad(b1, samples, b1_median);
    const double b2_mad = mad(b2, samples, b2_median);
    const double best = b1_median < b2_median ? b1_median : b2_median;
    const double difference = 100.0 * fabs(b1_median - b2_median) / best;
    const char *selection = difference < 1.0 ? "B1-size-tiebreak"
                            : (b1_median < b2_median ? "B1" : "B2");

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"cpu\": 1,\n");
    printf("  \"iterations_per_sample\": %" PRIu64 ",\n", iterations);
    printf("  \"warmups\": 2,\n");
    printf("  \"paired_samples\": %u,\n", samples);
    printf("  \"B1\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
           b1_median, b1_mad);
    printf("  \"B2\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
           b2_median, b2_mad);
    printf("  \"difference_percent\": %.3f,\n", difference);
    printf("  \"selection\": \"%s\",\n", selection);
    printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
    printf("}\n");
    return 0;
}
