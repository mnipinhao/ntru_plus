#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "qbm_atomic.h"
#include "quadratic-constants.h"

enum { WORDS = 768, SAMPLES = 40, ITERATIONS = 2000 };

static _Alignas(32) int16_t input_a[WORDS];
static _Alignas(32) int16_t input_b[WORDS];
static _Alignas(32) int16_t output[WORDS];

static int pin_first_available_cpu(void)
{
    cpu_set_t available, selected;
    if (sched_getaffinity(0, sizeof available, &available) != 0)
        return -1;
    for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        if (!CPU_ISSET(cpu, &available))
            continue;
        CPU_ZERO(&selected);
        CPU_SET(cpu, &selected);
        return sched_setaffinity(0, sizeof selected, &selected) == 0 ? cpu : -1;
    }
    return -1;
}

static uint64_t ticks(void)
{
    unsigned aux;
    _mm_lfence();
    uint64_t value = __rdtscp(&aux);
    _mm_lfence();
    return value;
}

static double measure(qbm_asm_fn function)
{
    uint64_t start = ticks();
    for (size_t i = 0; i < ITERATIONS; ++i)
        function(output, input_a, input_b,
                 round4c_weight_mont, round4c_weight_qinv);
    return (double)(ticks() - start) / ITERATIONS;
}

static int compare_double(const void *left, const void *right)
{
    double a = *(const double *)left;
    double b = *(const double *)right;
    return (a > b) - (a < b);
}

static double median(const double values[SAMPLES])
{
    double copy[SAMPLES];
    for (size_t i = 0; i < SAMPLES; ++i)
        copy[i] = values[i];
    qsort(copy, SAMPLES, sizeof copy[0], compare_double);
    return (copy[SAMPLES / 2 - 1] + copy[SAMPLES / 2]) * 0.5;
}

int main(void)
{
    double control[SAMPLES], atomic[SAMPLES], delta[SAMPLES], deviation[SAMPLES];
    int cpu = pin_first_available_cpu();
    int wins = 0;
    uint64_t random = UINT64_C(0x243f6a8885a308d3);
    for (size_t i = 0; i < WORDS; ++i) {
        random ^= random << 13;
        random ^= random >> 7;
        random ^= random << 17;
        input_a[i] = (int16_t)((int)(random % 6913) - 3456);
        random ^= random << 13;
        random ^= random >> 7;
        random ^= random << 17;
        input_b[i] = (int16_t)((int)(random % 6913) - 3456);
    }
    for (size_t warm = 0; warm < 200; ++warm) {
        qbm_selected_control_asm(output, input_a, input_b,
                                 round4c_weight_mont, round4c_weight_qinv);
        qbm_atomic_expanded_asm(output, input_a, input_b,
                                round4c_weight_mont, round4c_weight_qinv);
    }
    for (size_t sample = 0; sample < SAMPLES; ++sample) {
        if ((sample & 1) == 0) {
            control[sample] = measure(qbm_selected_control_asm);
            atomic[sample] = measure(qbm_atomic_expanded_asm);
        } else {
            atomic[sample] = measure(qbm_atomic_expanded_asm);
            control[sample] = measure(qbm_selected_control_asm);
        }
        delta[sample] = atomic[sample] - control[sample];
        wins += delta[sample] < 0.0;
    }
    double delta_median = median(delta);
    for (size_t i = 0; i < SAMPLES; ++i) {
        double value = delta[i] - delta_median;
        deviation[i] = value < 0 ? -value : value;
    }
    printf("{\n");
    printf("  \"cpu\": %d,\n", cpu);
    printf("  \"iterations\": %d,\n", ITERATIONS);
    printf("  \"samples\": %d,\n", SAMPLES);
    printf("  \"control_address\": \"%p\",\n", (void *)qbm_selected_control_asm);
    printf("  \"atomic_address\": \"%p\",\n", (void *)qbm_atomic_expanded_asm);
    printf("  \"control_median_tsc\": %.6f,\n", median(control));
    printf("  \"atomic_median_tsc\": %.6f,\n", median(atomic));
    printf("  \"atomic_minus_control_median_tsc\": %.6f,\n", delta_median);
    printf("  \"delta_mad_tsc\": %.6f,\n", median(deviation));
    printf("  \"atomic_wins\": %d\n", wins);
    printf("}\n");
    return 0;
}
