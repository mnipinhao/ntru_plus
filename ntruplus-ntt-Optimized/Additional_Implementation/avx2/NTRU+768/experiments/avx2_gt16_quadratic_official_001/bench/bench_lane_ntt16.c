#define _GNU_SOURCE
#include "forward_intrinsic.h"
#include "lane_ntt16_intrinsic.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { Q = 3457, SAMPLES = 9, DEFAULT_ITERATIONS = 2000 };

typedef void (*kernel)(int16_t *, const int16_t *);

static volatile uint64_t sink;

static void cross_register(int16_t *out, const int16_t *in)
{
    (void)in;
    round4c_forward_ntt16_asm(out);
}

static void lane_x1_inplace(int16_t *out, const int16_t *in)
{
    (void)in;
    round4c_lane_ntt16_batch_x1(out, out);
}

static void lane_x3_inplace(int16_t *out, const int16_t *in)
{
    (void)in;
    round4c_lane_ntt16_batch_x3(out, out);
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

static double measure(kernel fn, int16_t *out, const int16_t *in,
                      size_t iterations)
{
    uint64_t samples[SAMPLES];
    for (size_t warm = 0; warm < 2; ++warm)
        for (size_t i = 0; i < 32; ++i)
            fn(out, in);
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        const uint64_t begin = ticks();
        for (size_t i = 0; i < iterations; ++i)
            fn(out, in);
        samples[sample] = ticks() - begin;
        sink += (uint16_t)out[37 * sample];
    }
    qsort(samples, SAMPLES, sizeof(samples[0]), compare);
    return (double)samples[SAMPLES / 2] / iterations;
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
    int16_t input[768] __attribute__((aligned(32)));
    int16_t output[768] __attribute__((aligned(32)));
    uint32_t state = 0x4c41594fu;
    for (size_t i = 0; i < 768; ++i) {
        state = state * 1664525u + 1013904223u;
        input[i] = (int16_t)((int)(state % Q) - 1728);
    }
    memcpy(output, input, sizeof(output));
    const double cross = measure(cross_register, output, input, iterations);
    memcpy(output, input, sizeof(output));
    const double x1 = measure(lane_x1_inplace, output, input, iterations);
    memcpy(output, input, sizeof(output));
    const double x3 = measure(lane_x3_inplace, output, input, iterations);
    printf("{\n  \"iterations\": %zu,\n", iterations);
    printf("  \"logical_transforms\": 48,\n");
    printf("  \"cross_register_tsc\": %.4f,\n", cross);
    printf("  \"lane_i16_x1_tsc\": %.4f,\n", x1);
    printf("  \"lane_i16_x3_tsc\": %.4f,\n", x3);
    printf("  \"lane_i16_x1_per_transform\": %.4f,\n", x1 / 48.0);
    printf("  \"lane_i16_x3_per_transform\": %.4f,\n", x3 / 48.0);
    printf("  \"sink\": %llu\n}\n", (unsigned long long)sink);
    return 0;
}
