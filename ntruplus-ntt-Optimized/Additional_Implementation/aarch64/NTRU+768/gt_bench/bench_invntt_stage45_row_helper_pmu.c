#if !defined(__linux__)
#error "bench_invntt_stage45_row_helper_pmu requires Linux perf_event_open"
#endif
#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "params.h"
#include "poly.h"

#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 20000
#endif
#ifndef NWARMUP
#define NWARMUP 300
#endif
#ifndef NINPUTS
#define NINPUTS 64
#endif

typedef void (*invntt_fn)(poly *, const poly *);

struct count {
    uint64_t cycles;
    uint64_t instructions;
};

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_rminus1_stage45_row_helper(poly *r, const poly *a);

static int leader_fd = -1;
static int member_fd = -1;
static poly inputs[NINPUTS] __attribute__((aligned(64)));
static poly output __attribute__((aligned(64)));
static volatile uint64_t sink;

static int perf_open(uint64_t config, int group_fd)
{
    struct perf_event_attr pe;

    memset(&pe, 0, sizeof(pe));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(pe);
    pe.config = config;
    pe.disabled = group_fd == -1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group_fd, 0);
}

static int init_pmu(void)
{
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    if (leader_fd < 0)
        return -1;
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    return member_fd < 0 ? -1 : 0;
}

static void begin_pmu(void)
{
    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
}

static struct count end_pmu(void)
{
    struct {
        uint64_t nr;
        uint64_t value[2];
    } data = {0, {0, 0}};

    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof(data)) != (ssize_t)sizeof(data) ||
        data.nr != 2) {
        perror("perf group read");
        exit(EXIT_FAILURE);
    }
    return (struct count){data.value[0], data.value[1]};
}

static struct count measure(invntt_fn fn, int sample)
{
    int i;

    begin_pmu();
    for (i = 0; i < NITERATIONS; i++)
        fn(&output, &inputs[(i + sample) % NINPUTS]);
    {
        struct count result = end_pmu();
        sink ^= (uint16_t)output.coeffs[(unsigned)sample % NTRUPLUS_N];
        return result;
    }
}

static int cmp_u64(const void *a, const void *b)
{
    const uint64_t aa = *(const uint64_t *)a;
    const uint64_t bb = *(const uint64_t *)b;

    return (aa > bb) - (aa < bb);
}

static int cmp_i64(const void *a, const void *b)
{
    const int64_t aa = *(const int64_t *)a;
    const int64_t bb = *(const int64_t *)b;

    return (aa > bb) - (aa < bb);
}

static size_t percentile_index(unsigned percentile)
{
    return ((size_t)percentile * (NTESTS - 1)) / 100u;
}

static uint32_t rng_state = UINT32_C(0x45a11e5d);

static uint32_t next_u32(void)
{
    rng_state = rng_state * UINT32_C(1664525) + UINT32_C(1013904223);
    return rng_state;
}

static int prepare(void)
{
    poly a;
    poly b;
    poly antt;
    poly bntt;
    poly production;
    poly candidate;
    int mismatches = 0;
    int slot;
    int i;

    for (slot = 0; slot < NINPUTS; slot++) {
        for (i = 0; i < NTRUPLUS_N; i++) {
            a.coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
            b.coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
        }
        poly_ntt(&antt, &a);
        poly_ntt(&bntt, &b);
        poly_basemul_rminus1(&inputs[slot], &antt, &bntt);
        poly_invntt_from_rminus1(&production, &inputs[slot]);
        poly_invntt_rminus1_stage45_row_helper(&candidate, &inputs[slot]);
        for (i = 0; i < NTRUPLUS_N; i++)
            mismatches += production.coeffs[i] != candidate.coeffs[i];
    }
    printf("correctness,inputs=%d,mismatches=%d\n", NINPUTS, mismatches);
    return mismatches == 0 ? 0 : -1;
}

static void report(const char *event_name, const uint64_t a[NTESTS],
                   const uint64_t b[NTESTS])
{
    uint64_t sorted_a[NTESTS];
    uint64_t sorted_b[NTESTS];
    int64_t deltas[NTESTS];
    int64_t sorted_deltas[NTESTS];
    size_t wins = 0;
    int i;

    for (i = 0; i < NTESTS; i++) {
        sorted_a[i] = a[i];
        sorted_b[i] = b[i];
        deltas[i] = (int64_t)b[i] - (int64_t)a[i];
        sorted_deltas[i] = deltas[i];
        wins += deltas[i] < 0;
    }
    qsort(sorted_a, NTESTS, sizeof(sorted_a[0]), cmp_u64);
    qsort(sorted_b, NTESTS, sizeof(sorted_b[0]), cmp_u64);
    qsort(sorted_deltas, NTESTS, sizeof(sorted_deltas[0]), cmp_i64);
    printf("paired,event=%s,a_p50=%.3f,b_p50=%.3f,"
           "delta_p10=%.3f,delta_p50=%.3f,delta_p90=%.3f,"
           "wins=%zu/%d\n",
           event_name, (double)sorted_a[NTESTS / 2] / NITERATIONS,
           (double)sorted_b[NTESTS / 2] / NITERATIONS,
           (double)sorted_deltas[percentile_index(10)] / NITERATIONS,
           (double)sorted_deltas[NTESTS / 2] / NITERATIONS,
           (double)sorted_deltas[percentile_index(90)] / NITERATIONS, wins,
           NTESTS);
}

int main(void)
{
    const invntt_fn fns[2] = {
        poly_invntt_from_rminus1,
        poly_invntt_rminus1_stage45_row_helper,
    };
    struct count samples[2][NTESTS];
    uint64_t cycles[2][NTESTS];
    uint64_t instructions[2][NTESTS];
    int sample;
    int i;

    if (prepare() != 0)
        return EXIT_FAILURE;
    if (init_pmu() != 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return EXIT_FAILURE;
    }
    for (i = 0; i < NWARMUP; i++)
        fns[i & 1](&output, &inputs[i % NINPUTS]);
    for (sample = 0; sample < NTESTS; sample++) {
        const int first = sample & 1;
        const int second = first ^ 1;

        samples[first][sample] = measure(fns[first], sample);
        samples[second][sample] = measure(fns[second], sample);
        cycles[0][sample] = samples[0][sample].cycles;
        cycles[1][sample] = samples[1][sample].cycles;
        instructions[0][sample] = samples[0][sample].instructions;
        instructions[1][sample] = samples[1][sample].instructions;
    }

    printf("benchmark,variants=A_production/B_stage45_row_helper,"
           "NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
           NTESTS, NITERATIONS, NWARMUP, NINPUTS);
    report("cycles", cycles[0], cycles[1]);
    report("instructions", instructions[0], instructions[1]);
    printf("sink=%" PRIu64 "\n", sink);
    close(member_fd);
    close(leader_fd);
    return EXIT_SUCCESS;
}
