#define _GNU_SOURCE
#include "d4_aos_f32x3_ref.h"

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { CPU = 3, FIXTURES = 32, SAMPLES = 10001, WARMUP = 2048, CASES = 4 };
typedef void (*inverse_kernel)(int16_t *, const int16_t *);
static d4aos_f32x3_state inputs[CASES][FIXTURES];
static d4aos_coeff_poly output;

extern void gt_invntt_soa_rminus1_avx2_three_child_asm(int16_t *, const int16_t *);

static uint64_t begin_tsc(void)
{
    unsigned int low;
    unsigned int high;
    __asm__ volatile("lfence\n\trdtsc" : "=a"(low), "=d"(high) :: "memory");
    return ((uint64_t)high << 32) | low;
}

static uint64_t end_tsc(void)
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
    static int64_t differences[3][SAMPLES];
    const char *names[CASES] = {"official", "soa", "y1", "y2"};
    inverse_kernel kernels[CASES] = {
        NULL,
        gt_invntt_soa_rminus1_avx2_three_child_asm,
        (inverse_kernel)gt_d4aos_f32x3_yang_invntt_avx2_asm,
        (inverse_kernel)gt_d4aos_f32x3_yang_compact_invntt_avx2_asm
    };
    cpu_set_t affinity;
    uint32_t random_word = 37;

    CPU_ZERO(&affinity);
    CPU_SET(CPU, &affinity);
    if (sched_setaffinity(0, sizeof(affinity), &affinity) != 0) {
        perror("sched_setaffinity");
        return 1;
    }
    for (int candidate = 0; candidate < CASES; ++candidate) {
        for (int fixture = 0; fixture < FIXTURES; ++fixture) {
            for (int lane = 0; lane < 768; ++lane) {
                random_word = 1664525U * random_word + 1013904223U;
                inputs[candidate][fixture].lane[lane] =
                    (int16_t)(random_word % D4AOS_Q);
            }
        }
    }
    for (int warm = 0; warm < WARMUP; ++warm) {
        for (int candidate = 0; candidate < CASES; ++candidate) {
            if (candidate == 0) {
                memcpy(output.coeff, inputs[candidate][warm & 31].lane, sizeof(output));
                poly_invntt_scale((poly *)(void *)&output);
            } else {
                kernels[candidate](output.coeff, inputs[candidate][warm & 31].lane);
            }
        }
    }
    for (int sample = 0; sample < SAMPLES; ++sample) {
        const int fixture = (17 * sample + 9) & 31;
        for (int position = 0; position < CASES; ++position) {
            const int candidate = (position + sample) % CASES;
            if (candidate == 0) {
                memcpy(output.coeff, inputs[candidate][fixture].lane, sizeof(output));
            }
            const uint64_t start = begin_tsc();
            if (candidate == 0) {
                poly_invntt_scale((poly *)(void *)&output);
            } else {
                kernels[candidate](output.coeff, inputs[candidate][fixture].lane);
            }
            samples[candidate][sample] = end_tsc() - start;
        }
        differences[0][sample] =
            (int64_t)samples[2][sample] - (int64_t)samples[1][sample];
        differences[1][sample] =
            (int64_t)samples[3][sample] - (int64_t)samples[1][sample];
        differences[2][sample] =
            (int64_t)samples[3][sample] - (int64_t)samples[2][sample];
    }
    for (int candidate = 0; candidate < CASES; ++candidate) {
        qsort(samples[candidate], SAMPLES, sizeof(uint64_t), compare_u64);
        printf("%s median=%llu p10=%llu p90=%llu\n", names[candidate],
            (unsigned long long)samples[candidate][SAMPLES / 2],
            (unsigned long long)samples[candidate][SAMPLES / 10],
            (unsigned long long)samples[candidate][9 * SAMPLES / 10]);
    }
    for (int index = 0; index < 3; ++index) {
        const char *labels[3] = {"y1_minus_soa", "y2_minus_soa", "y2_minus_y1"};
        qsort(differences[index], SAMPLES, sizeof(int64_t), compare_i64);
        printf("%s median=%lld p10=%lld p90=%lld\n", labels[index],
            (long long)differences[index][SAMPLES / 2],
            (long long)differences[index][SAMPLES / 10],
            (long long)differences[index][9 * SAMPLES / 10]);
    }
    return 0;
}
