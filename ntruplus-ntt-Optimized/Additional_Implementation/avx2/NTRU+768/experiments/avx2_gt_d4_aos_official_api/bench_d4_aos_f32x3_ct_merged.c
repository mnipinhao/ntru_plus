#define _GNU_SOURCE
#include "d4_aos_f32x3_ref.h"

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { BENCH_CPU = 3, FIXTURES = 32, SAMPLES = 20001, WARMUP = 4096 };

static d4aos_f32x3_state inputs[FIXTURES];
static d4aos_f32x3_state output;

static uint64_t tsc_begin(void)
{
    unsigned int low;
    unsigned int high;

    __asm__ volatile("lfence\n\trdtsc" : "=a"(low), "=d"(high) :: "memory");
    return ((uint64_t)high << 32) | low;
}

static uint64_t tsc_end(void)
{
    unsigned int low;
    unsigned int high;
    unsigned int auxiliary;

    __asm__ volatile("rdtscp\n\tlfence"
        : "=a"(low), "=d"(high), "=c"(auxiliary) :: "memory");
    return ((uint64_t)high << 32) | low;
}

static int compare_u64(const void *left_pointer, const void *right_pointer)
{
    const uint64_t left = *(const uint64_t *)left_pointer;
    const uint64_t right = *(const uint64_t *)right_pointer;
    return (left > right) - (left < right);
}

int main(void)
{
    cpu_set_t affinity;
    uint64_t samples[SAMPLES];
    uint32_t random_word = 11;
    uint64_t checksum = 0;

    CPU_ZERO(&affinity);
    CPU_SET(BENCH_CPU, &affinity);
    if (sched_setaffinity(0, sizeof(affinity), &affinity) != 0) {
        perror("sched_setaffinity CPU3");
        return 1;
    }

    for (int fixture = 0; fixture < FIXTURES; ++fixture) {
        for (int lane = 0; lane < 768; ++lane) {
            random_word = 1664525U * random_word + 1013904223U;
            inputs[fixture].lane[lane] = (int16_t)(random_word % D4AOS_Q);
        }
    }

    for (int iteration = 0; iteration < WARMUP; ++iteration) {
        gt_d4aos_f32x3_invntt32_ct_merged_asm(
            &output, &inputs[(iteration * 17) & (FIXTURES - 1)]);
    }

    for (int sample = 0; sample < SAMPLES; ++sample) {
        const int fixture = (sample & 1) == 0 ?
            (sample * 17) & (FIXTURES - 1) : (sample * 13 + 7) & (FIXTURES - 1);
        const uint64_t start = tsc_begin();

        gt_d4aos_f32x3_invntt32_ct_merged_asm(&output, &inputs[fixture]);
        samples[sample] = tsc_end() - start;
        checksum += (uint16_t)output.lane[sample % 768];
    }

    qsort(samples, SAMPLES, sizeof(samples[0]), compare_u64);
    printf("f32x3-ct-ntt32 cpu=%d samples=%d median=%llu p10=%llu p90=%llu "
           "checksum=%llu\n",
        BENCH_CPU, SAMPLES,
        (unsigned long long)samples[SAMPLES / 2],
        (unsigned long long)samples[SAMPLES / 10],
        (unsigned long long)samples[9 * SAMPLES / 10],
        (unsigned long long)checksum);
    return 0;
}
