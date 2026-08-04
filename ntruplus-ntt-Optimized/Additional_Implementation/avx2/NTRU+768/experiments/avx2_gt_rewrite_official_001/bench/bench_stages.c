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

enum { MAX_SAMPLES = 64, STAGE_COUNT = 8 };

typedef struct {
    poly coefficient;
    poly frequency;
    poly inverse_input;
    poly output;
    _Alignas(32) int16_t rows[3][32][16];
    _Alignas(32) int16_t after32[3][32][16];
    uint8_t encoded[NTRUPLUS_POLYBYTES];
} stage_context;

typedef void (*stage_fn)(stage_context *);

typedef struct {
    const char *name;
    stage_fn run;
    double samples[MAX_SAMPLES];
    double median;
    double mad;
} stage;

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

static void run_forward_frontend(stage_context *ctx)
{
    gt_profile_forward_frontend(ctx->rows, &ctx->coefficient);
}

static void run_forward_b1(stage_context *ctx)
{
    gt_profile_forward_b1(&ctx->output,
                          (const int16_t (*)[32][16])ctx->rows);
}

static void run_basemul(stage_context *ctx)
{
    gt_poly_basemul(&ctx->output, &ctx->frequency, &ctx->frequency);
}

static void run_baseinv(stage_context *ctx)
{
    (void)gt_poly_baseinv(&ctx->output, &ctx->inverse_input);
}

static void run_inverse_b1(stage_context *ctx)
{
    gt_profile_inverse_b1(ctx->after32, &ctx->frequency);
}

static void run_inverse_tail(stage_context *ctx)
{
    gt_profile_inverse_tail(&ctx->output,
                            (const int16_t (*)[32][16])ctx->after32);
}

static void run_tobytes(stage_context *ctx)
{
    gt_poly_tobytes(ctx->encoded, &ctx->frequency);
}

static void run_frombytes(stage_context *ctx)
{
    (void)gt_poly_frombytes(&ctx->output, ctx->encoded);
}

static double measure(stage *candidate, uint64_t iterations,
                      stage_context *ctx)
{
    const uint64_t begin = ticks();
    for (uint64_t i = 0; i < iterations; ++i)
        candidate->run(ctx);
    const uint64_t end = ticks();
    const uint16_t *words = (const uint16_t *)ctx;
    uint64_t checksum = 0;
    for (size_t i = 0; i < sizeof *ctx / sizeof *words; i += 97)
        checksum = checksum * UINT64_C(1315423911) + words[i];
    checksum_sink ^= checksum;
    return (double)(end - begin) / (double)iterations;
}

static void initialize(stage_context *ctx)
{
    memset(ctx, 0, sizeof *ctx);
    for (size_t i = 0; i < NTRUPLUS_N; ++i)
        ctx->coefficient.coeffs[i] = (int16_t)((int)(i % 8U) - 3);
    ctx->frequency = ctx->coefficient;
    gt_poly_ntt(&ctx->frequency);
    gt_profile_forward_frontend(ctx->rows, &ctx->coefficient);
    gt_profile_inverse_b1(ctx->after32, &ctx->frequency);
    for (size_t batch = 0; batch < 12; ++batch)
        for (size_t lane = 0; lane < 16; ++lane)
            ctx->inverse_input.coeffs[64 * batch + lane] = 1;
    gt_poly_tobytes(ctx->encoded, &ctx->frequency);
}

int main(int argc, char **argv)
{
    uint64_t iterations = UINT64_C(1000000);
    unsigned samples = 20;
    const char *selected = "all";
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--iterations") == 0 && i + 1 < argc)
            iterations = strtoull(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--samples") == 0 && i + 1 < argc)
            samples = (unsigned)strtoul(argv[++i], NULL, 10);
        else if (strcmp(argv[i], "--candidate") == 0 && i + 1 < argc)
            selected = argv[++i];
        else {
            fprintf(stderr, "usage: %s [--iterations N] [--samples N] "
                    "[--candidate all|NAME]\n", argv[0]);
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

    stage stages[STAGE_COUNT] = {
        {"forward_frontend", run_forward_frontend, {0}, 0, 0},
        {"forward_b1", run_forward_b1, {0}, 0, 0},
        {"basemul_bm_a", run_basemul, {0}, 0, 0},
        {"baseinv", run_baseinv, {0}, 0, 0},
        {"inverse_b1", run_inverse_b1, {0}, 0, 0},
        {"inverse_tail", run_inverse_tail, {0}, 0, 0},
        {"tobytes", run_tobytes, {0}, 0, 0},
        {"frombytes", run_frombytes, {0}, 0, 0},
    };
    stage_context ctx;
    initialize(&ctx);

    size_t first = 0;
    size_t last = STAGE_COUNT;
    if (strcmp(selected, "all") != 0) {
        for (first = 0; first < STAGE_COUNT; ++first)
            if (strcmp(selected, stages[first].name) == 0)
                break;
        if (first == STAGE_COUNT) {
            fprintf(stderr, "unknown stage: %s\n", selected);
            return 2;
        }
        last = first + 1;
    }

    for (size_t i = first; i < last; ++i)
        for (unsigned warmup = 0; warmup < 2; ++warmup)
            (void)measure(&stages[i], iterations, &ctx);

    for (unsigned sample = 0; sample < samples; ++sample) {
        if ((sample & 1U) == 0) {
            for (size_t i = first; i < last; ++i)
                stages[i].samples[sample] = measure(&stages[i], iterations,
                                                    &ctx);
        } else {
            for (size_t i = last; i-- > first;)
                stages[i].samples[sample] = measure(&stages[i], iterations,
                                                    &ctx);
        }
    }

    for (size_t i = first; i < last; ++i) {
        stages[i].median = median(stages[i].samples, samples);
        stages[i].mad = mad(stages[i].samples, samples, stages[i].median);
    }

    printf("{\n");
    printf("  \"schema_version\": 1,\n");
    printf("  \"candidate\": \"%s\",\n", selected);
    printf("  \"cpu\": 1,\n");
    printf("  \"iterations_per_sample\": %" PRIu64 ",\n", iterations);
    printf("  \"warmups\": 2,\n");
    printf("  \"samples\": %u,\n", samples);
    printf("  \"stages\": {\n");
    for (size_t i = first; i < last; ++i) {
        printf("    \"%s\": {\"median_cycles\": %.3f, "
               "\"mad_cycles\": %.3f}%s\n", stages[i].name,
               stages[i].median, stages[i].mad,
               i + 1 == last ? "" : ",");
    }
    printf("  },\n");
    printf("  \"canonical_standalone_pass_cycles\": 0,\n");
    printf("  \"canonical_note\": \"reductions are embedded in forward_b1\",\n");
    printf("  \"checksum\": \"%016" PRIx64 "\"\n", checksum_sink);
    printf("}\n");
    return 0;
}
