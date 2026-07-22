#if !defined(__linux__)
#error "bench_gt_canonical_serialization_next_pmu requires Linux perf_event_open"
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

#define VARIANT_COUNT 3
#define MAX_EVENTS 3

typedef void (*pack_fn)(uint8_t *, const poly *);

void poly_tobytes_gt_canonical_p1(uint8_t *, const poly *);
void poly_tobytes_gt_canonical_cross_chunk(uint8_t *, const poly *);
void poly_tobytes_gt_canonical_compact(uint8_t *, const poly *);

struct variant {
    const char *name;
    pack_fn fn;
};

struct counts {
    uint64_t cycles;
    uint64_t instructions;
    uint64_t l1i_refills;
};

static const struct variant variants[VARIANT_COUNT] = {
    {"p1_expanded", poly_tobytes_gt_canonical_p1},
    {"cross_chunk", poly_tobytes_gt_canonical_cross_chunk},
    {"compact", poly_tobytes_gt_canonical_compact},
};

static poly inputs[NINPUTS] __attribute__((aligned(64)));
static uint8_t output[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint64_t rng_state = 1;
static int leader_fd = -1;
static int event_fds[MAX_EVENTS] = {-1, -1, -1};
static int event_count;
static int have_l1i;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(rng_state >> 32);
}

static int perf_event_open_wrap(struct perf_event_attr *attr, int group_fd)
{
    return (int)syscall(__NR_perf_event_open, attr, 0, -1, group_fd, 0);
}

static int add_event(uint32_t type, uint64_t config, int required)
{
    struct perf_event_attr attr;
    int fd;

    memset(&attr, 0, sizeof attr);
    attr.type = type;
    attr.size = sizeof attr;
    attr.config = config;
    attr.disabled = event_count == 0;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP;
    fd = perf_event_open_wrap(&attr, leader_fd);
    if (fd < 0) {
        if (required) {
            fprintf(stderr, "required perf event type=%u config=%" PRIu64
                            ": %s\n",
                    type, config, strerror(errno));
            exit(1);
        }
        return 0;
    }
    event_fds[event_count++] = fd;
    if (leader_fd < 0)
        leader_fd = fd;
    return 1;
}

static void setup_events(void)
{
    const uint64_t l1i_read_miss =
        PERF_COUNT_HW_CACHE_L1I |
        ((uint64_t)PERF_COUNT_HW_CACHE_OP_READ << 8) |
        ((uint64_t)PERF_COUNT_HW_CACHE_RESULT_MISS << 16);

    add_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, 1);
    add_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, 1);
    have_l1i = add_event(PERF_TYPE_HW_CACHE, l1i_read_miss, 0);
    printf("pmu_capability,l1i_read_miss=%s\n",
           have_l1i ? "available" : "unavailable");
}

static void close_events(void)
{
    for (int i = 0; i < event_count; i++)
        close(event_fds[i]);
}

static struct counts measure(pack_fn fn)
{
    uint64_t values[MAX_EVENTS + 1] = {0};
    const size_t bytes = (size_t)(event_count + 1) * sizeof(uint64_t);

    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (size_t i = 0; i < NITERATIONS; i++) {
        fn(output, &inputs[i % NINPUTS]);
        sink ^= output[(i * 13) % NTRUPLUS_POLYBYTES];
    }
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, values, bytes) != (ssize_t)bytes) {
        perror("read perf group");
        exit(1);
    }
    if (values[0] != (uint64_t)event_count) {
        fprintf(stderr, "unexpected perf group count=%" PRIu64 "\n", values[0]);
        exit(1);
    }
    return (struct counts){
        values[1] / NITERATIONS,
        values[2] / NITERATIONS,
        have_l1i ? values[3] / NITERATIONS : 0,
    };
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

static unsigned run_correctness(void)
{
    uint8_t reference[NTRUPLUS_POLYBYTES];
    uint8_t got[NTRUPLUS_POLYBYTES];
    unsigned mismatches = 0;

    for (size_t test = 0; test < NVALID; test++) {
        poly input;
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            input.coeffs[i] =
                (int16_t)(next_u32() % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q;
        variants[0].fn(reference, &input);
        for (size_t v = 1; v < VARIANT_COUNT; v++) {
            variants[v].fn(got, &input);
            mismatches += memcmp(got, reference, sizeof got) != 0;
        }
    }
    printf("correctness,total_mismatches=%u\n", mismatches);
    return mismatches;
}

static void prepare_inputs(void)
{
    for (size_t input = 0; input < NINPUTS; input++)
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            inputs[input].coeffs[i] =
                (int16_t)(next_u32() % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q;
}

static void report(uint64_t cycles[VARIANT_COUNT][NTESTS],
                   uint64_t instructions[VARIANT_COUNT][NTESTS],
                   uint64_t l1i[VARIANT_COUNT][NTESTS])
{
    for (size_t v = 0; v < VARIANT_COUNT; v++) {
        uint64_t c[NTESTS], insn[NTESTS], misses[NTESTS];
        memcpy(c, cycles[v], sizeof c);
        memcpy(insn, instructions[v], sizeof insn);
        memcpy(misses, l1i[v], sizeof misses);
        qsort(c, NTESTS, sizeof c[0], cmp_u64);
        qsort(insn, NTESTS, sizeof insn[0], cmp_u64);
        qsort(misses, NTESTS, sizeof misses[0], cmp_u64);
        printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_min=%" PRIu64
               ",cycles_max=%" PRIu64 ",instr_p50=%" PRIu64
               ",cpi_x1000=%" PRIu64 ",l1i_refill_p50=",
               variants[v].name, c[NTESTS / 2], c[0], c[NTESTS - 1],
               insn[NTESTS / 2],
               (1000 * c[NTESTS / 2]) / insn[NTESTS / 2]);
        if (have_l1i)
            printf("%" PRIu64, misses[NTESTS / 2]);
        else
            printf("unavailable");
        printf(",addr_mod32=%" PRIuPTR ",addr_mod64=%" PRIuPTR "\n",
               (uintptr_t)variants[v].fn % 32,
               (uintptr_t)variants[v].fn % 64);
    }

    for (size_t v = 1; v < VARIANT_COUNT; v++) {
        int64_t delta[NTESTS];
        unsigned wins = 0;
        for (size_t test = 0; test < NTESTS; test++) {
            delta[test] =
                (int64_t)cycles[v][test] - (int64_t)cycles[0][test];
            wins += delta[test] < 0;
        }
        qsort(delta, NTESTS, sizeof delta[0], cmp_i64);
        printf("paired,%s_vs_p1,delta_p10=%" PRId64
               ",delta_p50=%" PRId64 ",delta_p90=%" PRId64
               ",wins=%u/%d\n",
               variants[v].name, delta[NTESTS / 10], delta[NTESTS / 2],
               delta[(9 * NTESTS) / 10], wins, NTESTS);
    }
}

int main(void)
{
    uint64_t cycles[VARIANT_COUNT][NTESTS];
    uint64_t instructions[VARIANT_COUNT][NTESTS];
    uint64_t l1i[VARIANT_COUNT][NTESTS];

    if (run_correctness() != 0)
        return 1;
    prepare_inputs();
    for (size_t variant = 0; variant < VARIANT_COUNT; variant++)
        for (size_t i = 0; i < NWARMUP; i++)
            variants[variant].fn(output, &inputs[i % NINPUTS]);

    setup_events();
    for (size_t test = 0; test < NTESTS; test++) {
        for (size_t position = 0; position < VARIANT_COUNT; position++) {
            const size_t variant = (test + position) % VARIANT_COUNT;
            const struct counts c = measure(variants[variant].fn);
            cycles[variant][test] = c.cycles;
            instructions[variant][test] = c.instructions;
            l1i[variant][test] = c.l1i_refills;
        }
    }
    close_events();
    printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
           NTESTS, NITERATIONS, NWARMUP, NINPUTS);
    report(cycles, instructions, l1i);
    printf("sink=%" PRIu64 "\n", sink);
    return 0;
}
