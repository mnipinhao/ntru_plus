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
    VECTOR_LEAVES_PER_POLY = 48,
    QUARTIC_LANES_PER_POLY = 192,
};

typedef void (*basemul_kernel)(poly *, const poly *, const poly *);
static volatile uint64_t checksum_sink;

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    const uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static int pin_cpu1(void)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(1, &set);
    return sched_setaffinity(0, sizeof set, &set);
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
    if ((count & 1U) != 0)
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

static double measure(basemul_kernel kernel, uint64_t iterations,
                      poly *r, const poly *a, const poly *b)
{
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        kernel(r, a, b);
    const uint64_t end = ticks();
    uint64_t checksum = checksum_sink;
    for (size_t i = 0; i < NTRUPLUS_N; i += 97)
        checksum = checksum * UINT64_C(1315423911) + (uint16_t)r->coeffs[i];
    checksum_sink = checksum;
    return (double)(end - begin) / (double)iterations;
}

int main(int argc, char **argv)
{
    uint64_t iterations = 25000;
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
                    "usage: %s [--iterations N] [--samples N] [--candidate paired|BM-A|BM-B]\n",
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

    poly a;
    poly b;
    poly output;
    for (size_t i = 0; i < NTRUPLUS_N; ++i) {
        a.coeffs[i] = (int16_t)((int)((97 * i + 17) % 20741) - 10370);
        b.coeffs[i] = (int16_t)((int)((53 * i + 31) % 20741) - 10370);
    }

    if (strcmp(candidate, "BM-A") == 0 || strcmp(candidate, "BM-B") == 0) {
        const basemul_kernel kernel = strcmp(candidate, "BM-A") == 0
            ? gt_poly_basemul : gt_poly_basemul_bm_b;
        for (unsigned warmup = 0; warmup < 2; ++warmup)
            (void)measure(kernel, iterations, &output, &a, &b);
        double values[MAX_SAMPLES];
        for (unsigned sample = 0; sample < samples; ++sample)
            values[sample] = measure(kernel, iterations, &output, &a, &b);
        const double center = median(values, samples);
        printf("{\n");
        printf("  \"schema_version\": 1,\n");
        printf("  \"candidate\": \"%s\",\n", candidate);
        printf("  \"cpu\": 1,\n");
        printf("  \"input_bound\": \"3q\",\n");
        printf("  \"poly_calls_per_sample\": %" PRIu64 ",\n", iterations);
        printf("  \"vector_leaf_calls_per_sample\": %" PRIu64 ",\n",
               iterations * VECTOR_LEAVES_PER_POLY);
        printf("  \"warmups\": 2,\n");
        printf("  \"samples\": %u,\n", samples);
        printf("  \"median_cycles\": %.3f,\n", center);
        printf("  \"mad_cycles\": %.3f,\n", mad(values, samples, center));
        printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
        printf("}\n");
        return 0;
    }
    if (strcmp(candidate, "paired") != 0) {
        fprintf(stderr, "candidate must be paired, BM-A, or BM-B\n");
        return 2;
    }

    for (unsigned warmup = 0; warmup < 2; ++warmup) {
        (void)measure(gt_poly_basemul, iterations, &output, &a, &b);
        (void)measure(gt_poly_basemul_bm_b, iterations, &output, &a, &b);
    }

    double bm_a[MAX_SAMPLES];
    double bm_b[MAX_SAMPLES];
    for (unsigned sample = 0; sample < samples; ++sample) {
        if ((sample & 1U) == 0) {
            bm_a[sample] = measure(gt_poly_basemul, iterations,
                                   &output, &a, &b);
            bm_b[sample] = measure(gt_poly_basemul_bm_b, iterations,
                                   &output, &a, &b);
        } else {
            bm_b[sample] = measure(gt_poly_basemul_bm_b, iterations,
                                   &output, &a, &b);
            bm_a[sample] = measure(gt_poly_basemul, iterations,
                                   &output, &a, &b);
        }
    }

    const double a_median = median(bm_a, samples);
    const double b_median = median(bm_b, samples);
    const double difference = 100.0 * (b_median - a_median) / a_median;
    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"cpu\": 1,\n");
    printf("  \"input_bound\": \"3q\",\n");
    printf("  \"poly_calls_per_sample\": %" PRIu64 ",\n", iterations);
    printf("  \"vector_leaf_calls_per_sample\": %" PRIu64 ",\n",
           iterations * VECTOR_LEAVES_PER_POLY);
    printf("  \"quartic_lane_operations_per_sample\": %" PRIu64 ",\n",
           iterations * QUARTIC_LANES_PER_POLY);
    printf("  \"warmups\": 2,\n");
    printf("  \"paired_samples\": %u,\n", samples);
    printf("  \"BM-A\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
           a_median, mad(bm_a, samples, a_median));
    printf("  \"BM-B\": {\"median_cycles\": %.3f, \"mad_cycles\": %.3f},\n",
           b_median, mad(bm_b, samples, b_median));
    printf("  \"BM-B_delta_percent\": %.3f,\n", difference);
    printf("  \"selection\": \"%s\",\n", a_median <= b_median ? "BM-A" : "BM-B");
    printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
    printf("}\n");
    return 0;
}
