#if !defined(__linux__)
#error "bench_gt_canonical_unpack_pmu requires Linux perf_event_open"
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
#define NWARMUP 1000
#endif
#ifndef NINPUTS
#define NINPUTS 256
#endif
#ifndef NVALID
#define NVALID 4096
#endif

#define VARIANT_COUNT 2
#define EVENT_COUNT 2

typedef void (*unpack_fn)(poly *out, const uint8_t *in);

void poly_frombytes_gt_chunk0_u0(poly *out, const uint8_t *in);
void poly_frombytes_gt_chunk0_u1(poly *out, const uint8_t *in);
void poly_frombytes_gt_canonical_u1(poly *out, const uint8_t *in);

struct counts {
    uint64_t cycles;
    uint64_t instructions;
};

struct variant {
    const char *name;
    unpack_fn fn;
};

static const struct variant variants[VARIANT_COUNT] = {
#if defined(BENCH_FULL_UNPACK)
    {"production", poly_frombytes_gt_canonical},
    {"u1", poly_frombytes_gt_canonical_u1},
#else
    {"u0", poly_frombytes_gt_chunk0_u0},
    {"u1", poly_frombytes_gt_chunk0_u1},
#endif
};

static const unsigned touched_byte_offsets[16] = {
    312, 288, 360, 336, 264, 240, 192, 216,
    72, 48, 0, 24, 168, 144, 96, 120,
};

static uint8_t inputs[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static poly output __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint64_t rng_state = 1;
static int leader_fd = -1;
static int event_fds[EVENT_COUNT] = {-1, -1};

static uint32_t next_u32(void)
{
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(rng_state >> 32);
}

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
    return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static void setup_events(void)
{
    static const uint64_t configs[EVENT_COUNT] = {
        PERF_COUNT_HW_CPU_CYCLES,
        PERF_COUNT_HW_INSTRUCTIONS,
    };

    for (int i = 0; i < EVENT_COUNT; i++) {
        struct perf_event_attr attr;
        memset(&attr, 0, sizeof attr);
        attr.type = PERF_TYPE_HARDWARE;
        attr.size = sizeof attr;
        attr.config = configs[i];
        attr.disabled = i == 0;
        attr.exclude_kernel = 1;
        attr.exclude_hv = 1;
        attr.read_format = PERF_FORMAT_GROUP;
        event_fds[i] = perf_event_open_wrap(&attr, 0, -1, leader_fd, 0);
        if (event_fds[i] < 0) {
            fprintf(stderr, "perf_event_open(%d): %s\n", i, strerror(errno));
            exit(1);
        }
        if (i == 0)
            leader_fd = event_fds[i];
    }
}

static void close_events(void)
{
    for (int i = 0; i < EVENT_COUNT; i++)
        if (event_fds[i] >= 0)
            close(event_fds[i]);
}

static struct counts measure(unpack_fn fn)
{
    uint64_t values[EVENT_COUNT + 1] = {0};

    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (size_t i = 0; i < NITERATIONS; i++) {
        fn(&output, inputs[i % NINPUTS]);
        sink ^= (uint16_t)output.coeffs[(i * 13) % NTRUPLUS_N];
    }
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, values, sizeof values) != (ssize_t)sizeof values) {
        perror("read perf group");
        exit(1);
    }
    return (struct counts){values[1] / NITERATIONS,
                           values[2] / NITERATIONS};
}

static int cmp_u64(const void *a, const void *b)
{
    const uint64_t av = *(const uint64_t *)a;
    const uint64_t bv = *(const uint64_t *)b;
    return (av > bv) - (av < bv);
}

static int cmp_i64(const void *a, const void *b)
{
    const int64_t av = *(const int64_t *)a;
    const int64_t bv = *(const int64_t *)b;
    return (av > bv) - (av < bv);
}

static unsigned compare_chunk(const poly *a, const poly *b)
{
    unsigned mismatches = 0;

    for (size_t block = 0; block < 16; block++) {
        const size_t first = touched_byte_offsets[block] / sizeof(int16_t);
        for (size_t lane = 0; lane < 4; lane++)
            mismatches += a->coeffs[first + lane] != b->coeffs[first + lane];
    }
    return mismatches;
}

static unsigned run_correctness(void)
{
    uint8_t input[NTRUPLUS_POLYBYTES];
    poly reference;
    poly got;
    unsigned mismatches = 0;

    for (size_t test = 0; test < NVALID; test++) {
        for (size_t i = 0; i < sizeof input; i++)
            input[i] = (uint8_t)next_u32();
        poly_frombytes_gt_canonical(&reference, input);
        for (size_t v = 0; v < VARIANT_COUNT; v++) {
            memset(&got, 0, sizeof got);
            variants[v].fn(&got, input);
#if defined(BENCH_FULL_UNPACK)
            mismatches += memcmp(&got, &reference, sizeof got) != 0;
#else
            mismatches += compare_chunk(&got, &reference);
#endif
        }
    }
    printf("correctness,total_mismatches=%u\n", mismatches);
    return mismatches;
}

static void prepare_inputs(void)
{
    for (size_t input = 0; input < NINPUTS; input++)
        for (size_t i = 0; i < NTRUPLUS_POLYBYTES; i++)
            inputs[input][i] = (uint8_t)next_u32();
}

static void report(uint64_t cycles[VARIANT_COUNT][NTESTS],
                   uint64_t instructions[VARIANT_COUNT][NTESTS])
{
    for (size_t v = 0; v < VARIANT_COUNT; v++) {
        uint64_t c[NTESTS];
        uint64_t insn[NTESTS];
        memcpy(c, cycles[v], sizeof c);
        memcpy(insn, instructions[v], sizeof insn);
        qsort(c, NTESTS, sizeof c[0], cmp_u64);
        qsort(insn, NTESTS, sizeof insn[0], cmp_u64);
        printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_min=%" PRIu64
               ",cycles_max=%" PRIu64 ",instr_p50=%" PRIu64
               ",cpi_x1000=%" PRIu64 ",addr_mod32=%" PRIuPTR
               ",addr_mod64=%" PRIuPTR "\n",
               variants[v].name, c[NTESTS / 2], c[0], c[NTESTS - 1],
               insn[NTESTS / 2],
               (1000 * c[NTESTS / 2]) / insn[NTESTS / 2],
               (uintptr_t)variants[v].fn % 32, (uintptr_t)variants[v].fn % 64);
    }

    {
        int64_t delta[NTESTS];
        unsigned wins = 0;
        for (size_t t = 0; t < NTESTS; t++) {
            delta[t] = (int64_t)cycles[1][t] - (int64_t)cycles[0][t];
            wins += delta[t] < 0;
        }
        qsort(delta, NTESTS, sizeof delta[0], cmp_i64);
        printf("paired,u1_vs_baseline,delta_p10=%" PRId64
               ",delta_p50=%" PRId64 ",delta_p90=%" PRId64
               ",wins=%u/%d\n",
               delta[NTESTS / 10], delta[NTESTS / 2],
               delta[(9 * NTESTS) / 10], wins, NTESTS);
    }
}

int main(void)
{
    uint64_t cycles[VARIANT_COUNT][NTESTS];
    uint64_t instructions[VARIANT_COUNT][NTESTS];

    if (run_correctness() != 0)
        return 1;
    prepare_inputs();
    for (size_t v = 0; v < VARIANT_COUNT; v++)
        for (size_t i = 0; i < NWARMUP; i++)
            variants[v].fn(&output, inputs[i % NINPUTS]);

    setup_events();
    for (size_t test = 0; test < NTESTS; test++) {
        for (size_t position = 0; position < VARIANT_COUNT; position++) {
            const size_t variant = (test + position) % VARIANT_COUNT;
            const struct counts c = measure(variants[variant].fn);
            cycles[variant][test] = c.cycles;
            instructions[variant][test] = c.instructions;
        }
    }
    close_events();

    printf("pmu_settings,scope=%s,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
#if defined(BENCH_FULL_UNPACK)
           "full_unpack",
#else
           "chunk0",
#endif
           NTESTS, NITERATIONS, NWARMUP, NINPUTS);
    report(cycles, instructions);
    printf("sink=%" PRIu64 "\n", sink);
    return 0;
}
