#define _GNU_SOURCE
#include "forward_intrinsic.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { WORDS = 128, SAMPLES = 9, DEFAULT_ITERATIONS = 2000 };

typedef void (*kernel)(int16_t values[WORDS]);
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

static uint64_t run(kernel fn, int16_t values[WORDS], size_t iterations)
{
    const uint64_t begin = ticks();
    for (size_t i = 0; i < iterations; ++i)
        fn(values);
    const uint64_t elapsed = ticks() - begin;
    sink += (uint16_t)values[37];
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
    int16_t seed[WORDS] __attribute__((aligned(32)));
    int16_t baseline[WORDS] __attribute__((aligned(32)));
    int16_t scheduled[WORDS] __attribute__((aligned(32)));
    uint64_t baseline_samples[SAMPLES];
    uint64_t scheduled_samples[SAMPLES];
    uint32_t random_state = 0x43543842u;
    for (size_t i = 0; i < WORDS; ++i) {
        random_state = random_state * 1664525u + 1013904223u;
        seed[i] = (int16_t)((int)(random_state % 3457) - 1728);
    }
    memcpy(baseline, seed, sizeof(seed));
    memcpy(scheduled, seed, sizeof(seed));
    for (size_t warm = 0; warm < 2; ++warm) {
        for (size_t i = 0; i < 32; ++i) {
            round4c_forward_ct8_baseline_asm(baseline);
            round4c_forward_ct8_sched_asm(scheduled);
        }
    }
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        memcpy(baseline, seed, sizeof(seed));
        memcpy(scheduled, seed, sizeof(seed));
        if (sample & 1) {
            scheduled_samples[sample] = run(round4c_forward_ct8_sched_asm,
                                            scheduled, iterations);
            baseline_samples[sample] = run(round4c_forward_ct8_baseline_asm,
                                           baseline, iterations);
        } else {
            baseline_samples[sample] = run(round4c_forward_ct8_baseline_asm,
                                           baseline, iterations);
            scheduled_samples[sample] = run(round4c_forward_ct8_sched_asm,
                                            scheduled, iterations);
        }
        if (memcmp(baseline, scheduled, sizeof(baseline)) != 0) {
            fputs("benchmark end-state mismatch\n", stderr);
            return 1;
        }
    }
    qsort(baseline_samples, SAMPLES, sizeof(baseline_samples[0]), compare);
    qsort(scheduled_samples, SAMPLES, sizeof(scheduled_samples[0]), compare);
    const double base = (double)baseline_samples[SAMPLES / 2] / iterations;
    const double sched = (double)scheduled_samples[SAMPLES / 2] / iterations;
    printf("{\n  \"iterations\": %zu,\n", iterations);
    printf("  \"samples\": %d,\n", SAMPLES);
    printf("  \"baseline_tsc\": %.4f,\n", base);
    printf("  \"scheduled_tsc\": %.4f,\n", sched);
    printf("  \"scheduled_delta_percent\": %.4f,\n",
           100.0 * (sched - base) / base);
    printf("  \"sink\": %llu\n}\n", (unsigned long long)sink);
    return 0;
}
