#define _GNU_SOURCE
#include "d4_aos_f32x3_ref.h"

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { CPU = 3, FIXTURES = 32, SAMPLES = 10001, WARMUP = 2048, CASES = 4 };
typedef void (*kernel)(d4aos_f32x3_state *, const d4aos_f32x3_state *);
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

static int compare_u64(const void *left, const void *right)
{
    const uint64_t a = *(const uint64_t *)left;
    const uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static int compare_i64(const void *left, const void *right)
{
    const int64_t a = *(const int64_t *)left;
    const int64_t b = *(const int64_t *)right;
    return (a > b) - (a < b);
}

int main(void)
{
    static uint64_t samples[CASES][SAMPLES];
    static int64_t y1_delta[SAMPLES];
    static int64_t y2_delta[SAMPLES];
    const char *names[CASES] = {"y1", "y1_dft3", "y2", "y2_dft3"};
    kernel functions[CASES] = {
        gt_d4aos_f32x3_invntt32_ct_merged_yang_asm,
        gt_d4aos_f32x3_yang_idft3_probe_asm,
        gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm,
        gt_d4aos_f32x3_yang_compact_idft3_probe_asm
    };
    cpu_set_t affinity;
    uint32_t random_word = 29;

    CPU_ZERO(&affinity);
    CPU_SET(CPU, &affinity);
    if (sched_setaffinity(0, sizeof(affinity), &affinity) != 0) {
        perror("sched_setaffinity");
        return 1;
    }
    for (int fixture = 0; fixture < FIXTURES; ++fixture) {
        for (int lane = 0; lane < 768; ++lane) {
            random_word = 1664525U * random_word + 1013904223U;
            inputs[fixture].lane[lane] = (int16_t)(random_word % D4AOS_Q);
        }
    }
    for (int warm = 0; warm < WARMUP; ++warm) {
        for (int candidate = 0; candidate < CASES; ++candidate) {
            functions[candidate](&output, &inputs[warm & 31]);
        }
    }
    for (int sample = 0; sample < SAMPLES; ++sample) {
        const int fixture = (17 * sample + 5) & 31;
        for (int position = 0; position < CASES; ++position) {
            const int candidate = (position + sample) % CASES;
            const uint64_t start = tsc_begin();
            functions[candidate](&output, &inputs[fixture]);
            samples[candidate][sample] = tsc_end() - start;
        }
        y1_delta[sample] =
            (int64_t)samples[1][sample] - (int64_t)samples[0][sample];
        y2_delta[sample] =
            (int64_t)samples[3][sample] - (int64_t)samples[2][sample];
    }
    for (int candidate = 0; candidate < CASES; ++candidate) {
        qsort(samples[candidate], SAMPLES, sizeof(uint64_t), compare_u64);
        printf("%s median=%llu p10=%llu p90=%llu\n", names[candidate],
            (unsigned long long)samples[candidate][SAMPLES / 2],
            (unsigned long long)samples[candidate][SAMPLES / 10],
            (unsigned long long)samples[candidate][9 * SAMPLES / 10]);
    }
    qsort(y1_delta, SAMPLES, sizeof(int64_t), compare_i64);
    qsort(y2_delta, SAMPLES, sizeof(int64_t), compare_i64);
    printf("y1_dft3_delta median=%lld p10=%lld p90=%lld\n",
        (long long)y1_delta[SAMPLES / 2], (long long)y1_delta[SAMPLES / 10],
        (long long)y1_delta[9 * SAMPLES / 10]);
    printf("y2_dft3_delta median=%lld p10=%lld p90=%lld\n",
        (long long)y2_delta[SAMPLES / 2], (long long)y2_delta[SAMPLES / 10],
        (long long)y2_delta[9 * SAMPLES / 10]);
    return 0;
}
