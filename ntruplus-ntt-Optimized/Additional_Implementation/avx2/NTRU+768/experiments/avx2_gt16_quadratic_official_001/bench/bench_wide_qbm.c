#define _GNU_SOURCE
#include "qbm_intrinsic.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { SAMPLES = 9, DEFAULT_ITERATIONS = 2000 };
typedef void (*kernel)(int16_t *, const int16_t *, const int16_t *);
static volatile uint64_t sink;

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
    int16_t a[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t b[ROUND4C_WORDS] __attribute__((aligned(32)));
    int16_t out[ROUND4C_WORDS] __attribute__((aligned(32)));
    uint64_t plain[SAMPLES], centered[SAMPLES];
    uint32_t state = 0x57494445u;
    for (size_t i = 0; i < ROUND4C_WORDS; ++i) {
        state = state * 1664525u + 1013904223u;
        a[i] = (int16_t)((int)(state % 32515) - 16257);
        state = state * 1664525u + 1013904223u;
        b[i] = (int16_t)((int)(state % 32515) - 16257);
    }
    for (size_t warm = 0; warm < 2; ++warm) {
        for (size_t i = 0; i < 32; ++i) {
            round4c_qbm_vector_intrinsic(out, a, b);
            round4c_qbm_wide_centered_intrinsic(out, a, b);
        }
    }
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        if (sample & 1) {
            centered[sample] = run(round4c_qbm_wide_centered_intrinsic,
                                   out, a, b, iterations);
            plain[sample] = run(round4c_qbm_vector_intrinsic,
                                out, a, b, iterations);
        } else {
            plain[sample] = run(round4c_qbm_vector_intrinsic,
                                out, a, b, iterations);
            centered[sample] = run(round4c_qbm_wide_centered_intrinsic,
                                   out, a, b, iterations);
        }
    }
    qsort(plain, SAMPLES, sizeof(plain[0]), compare);
    qsort(centered, SAMPLES, sizeof(centered[0]), compare);
    const double p = (double)plain[SAMPLES / 2] / iterations;
    const double c = (double)centered[SAMPLES / 2] / iterations;
    printf("{\n  \"iterations\": %zu,\n", iterations);
    printf("  \"plain_wide_qbm_tsc\": %.4f,\n", p);
    printf("  \"centered_wide_qbm_tsc\": %.4f,\n", c);
    printf("  \"consumer_repair_cost_tsc\": %.4f,\n", c - p);
    printf("  \"sink\": %llu\n}\n", (unsigned long long)sink);
    return 0;
}
