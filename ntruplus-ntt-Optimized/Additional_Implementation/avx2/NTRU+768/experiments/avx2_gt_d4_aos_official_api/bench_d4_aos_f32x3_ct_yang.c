#define _GNU_SOURCE
#include "d4_aos_f32x3_ref.h"

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum { CPU = 3, FIXTURES = 32, SAMPLES = 10001, WARMUP = 2048, CASES = 8 };
typedef void (*kernel)(d4aos_f32x3_state *, const d4aos_f32x3_state *);

static d4aos_f32x3_state native[FIXTURES];
static d4aos_f32x3_state post_l2[FIXTURES];
static d4aos_f32x3_state output;

extern void gt_invntt_soa_ntt32_asm(int16_t out[768], const int16_t in[768]);

static __attribute__((noinline)) void empty_control(
    d4aos_f32x3_state *out, const d4aos_f32x3_state *in)
{
    __asm__ volatile("" : : "r"(out), "r"(in) : "memory");
}

static __attribute__((noinline)) void copy_control(
    d4aos_f32x3_state *out, const d4aos_f32x3_state *in)
{
    memcpy(out, in, sizeof(*out));
}

static void soa_ntt32(d4aos_f32x3_state *out, const d4aos_f32x3_state *in)
{
    gt_invntt_soa_ntt32_asm(out->lane, in->lane);
}

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

static int compare_u64(const void *a, const void *b)
{
    const uint64_t x = *(const uint64_t *)a;
    const uint64_t y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static int compare_i64(const void *a, const void *b)
{
    const int64_t x = *(const int64_t *)a;
    const int64_t y = *(const int64_t *)b;
    return (x > y) - (x < y);
}

int main(void)
{
    static uint64_t samples[CASES][SAMPLES];
    static int64_t y1_minus_y0[SAMPLES];
    static int64_t y2_minus_y1[SAMPLES];
    const char *names[CASES] = {
        "empty", "copy", "l0_l2", "l3_l4", "y0", "y1", "y2", "soa_ntt32"
    };
    kernel functions[CASES] = {
        empty_control, copy_control,
        gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm,
        gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm,
        gt_d4aos_f32x3_invntt32_ct_merged_asm,
        gt_d4aos_f32x3_invntt32_ct_merged_yang_asm,
        gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm,
        soa_ntt32
    };
    cpu_set_t set;
    uint32_t random_word = 19;

    CPU_ZERO(&set);
    CPU_SET(CPU, &set);
    if (sched_setaffinity(0, sizeof(set), &set) != 0) {
        perror("sched_setaffinity");
        return 1;
    }

    for (int fixture = 0; fixture < FIXTURES; ++fixture) {
        for (int lane = 0; lane < 768; ++lane) {
            random_word = 1664525U * random_word + 1013904223U;
            native[fixture].lane[lane] = (int16_t)(random_word % D4AOS_Q);
        }
        gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm(
            &post_l2[fixture], &native[fixture]);
    }

    for (int warm = 0; warm < WARMUP; ++warm) {
        for (int candidate = 0; candidate < CASES; ++candidate) {
            const d4aos_f32x3_state *input = candidate == 3 ?
                &post_l2[warm & 31] : &native[warm & 31];
            functions[candidate](&output, input);
        }
    }

    for (int sample = 0; sample < SAMPLES; ++sample) {
        const int fixture = (sample * 17 + 3) & 31;
        for (int position = 0; position < CASES; ++position) {
            const int candidate = (position + sample) % CASES;
            const d4aos_f32x3_state *input = candidate == 3 ?
                &post_l2[fixture] : &native[fixture];
            const uint64_t start = begin_tsc();
            functions[candidate](&output, input);
            samples[candidate][sample] = end_tsc() - start;
        }
    }

    for (int sample = 0; sample < SAMPLES; ++sample) {
        y1_minus_y0[sample] = (int64_t)samples[5][sample] - (int64_t)samples[4][sample];
        y2_minus_y1[sample] = (int64_t)samples[6][sample] - (int64_t)samples[5][sample];
    }
    for (int candidate = 0; candidate < CASES; ++candidate) {
        qsort(samples[candidate], SAMPLES, sizeof(uint64_t), compare_u64);
        printf("%s median=%llu p10=%llu p90=%llu\n", names[candidate],
            (unsigned long long)samples[candidate][SAMPLES / 2],
            (unsigned long long)samples[candidate][SAMPLES / 10],
            (unsigned long long)samples[candidate][9 * SAMPLES / 10]);
    }
    qsort(y1_minus_y0, SAMPLES, sizeof(int64_t), compare_i64);
    qsort(y2_minus_y1, SAMPLES, sizeof(int64_t), compare_i64);
    printf("paired_y1_minus_y0 median=%lld p10=%lld p90=%lld\n",
        (long long)y1_minus_y0[SAMPLES / 2],
        (long long)y1_minus_y0[SAMPLES / 10],
        (long long)y1_minus_y0[9 * SAMPLES / 10]);
    printf("paired_y2_minus_y1 median=%lld p10=%lld p90=%lld\n",
        (long long)y2_minus_y1[SAMPLES / 2],
        (long long)y2_minus_y1[SAMPLES / 10],
        (long long)y2_minus_y1[9 * SAMPLES / 10]);
    return 0;
}
