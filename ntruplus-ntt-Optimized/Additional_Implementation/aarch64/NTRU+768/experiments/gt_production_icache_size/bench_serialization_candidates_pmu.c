#define _GNU_SOURCE

#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "internal/keygen.h"

#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 20000
#endif
#ifndef NINPUTS
#define NINPUTS 256
#endif

typedef void (*pack_fn)(uint8_t *, const void *);

void poly_tobytes_shared_compact_candidate(uint8_t *, const poly *);
void gt_keygen_tobytes_cq_shared_candidate(uint8_t *, const gt_cq_poly *);

struct counts {
    uint64_t cycles;
    uint64_t instructions;
};

static poly inputs[NINPUTS] __attribute__((aligned(64)));
static uint8_t output[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;
static int leader_fd = -1;
static int instruction_fd = -1;

static void generic_baseline(uint8_t *out, const void *in)
{
    poly_tobytes(out, in);
}

static void generic_candidate(uint8_t *out, const void *in)
{
    poly_tobytes_shared_compact_candidate(out, in);
}

static void keygen_baseline(uint8_t *out, const void *in)
{
    gt_keygen_tobytes_cq(out, in);
}

static void keygen_candidate(uint8_t *out, const void *in)
{
    gt_keygen_tobytes_cq_shared_candidate(out, in);
}

static int perf_event_open_wrap(struct perf_event_attr *attr, int group_fd)
{
    return (int)syscall(__NR_perf_event_open, attr, 0, -1, group_fd, 0);
}

static int open_event(uint64_t config, int group_fd, int disabled)
{
    struct perf_event_attr attr;
    memset(&attr, 0, sizeof attr);
    attr.type = PERF_TYPE_HARDWARE;
    attr.size = sizeof attr;
    attr.config = config;
    attr.disabled = disabled;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP;
    return perf_event_open_wrap(&attr, group_fd);
}

static void setup_events(void)
{
    leader_fd = open_event(PERF_COUNT_HW_CPU_CYCLES, -1, 1);
    instruction_fd =
        open_event(PERF_COUNT_HW_INSTRUCTIONS, leader_fd, 0);
    if (leader_fd < 0 || instruction_fd < 0) {
        fprintf(stderr, "perf_event_open: %s\n", strerror(errno));
        exit(2);
    }
}

static struct counts measure(pack_fn fn)
{
    uint64_t values[3] = {0};
    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (size_t i = 0; i < NITERATIONS; i++) {
        fn(output, &inputs[i % NINPUTS]);
        sink ^= output[(i * 13) % NTRUPLUS_POLYBYTES];
    }
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, values, sizeof values) != (ssize_t)sizeof values) {
        perror("read perf group");
        exit(2);
    }
    return (struct counts){
        values[1] / NITERATIONS,
        values[2] / NITERATIONS,
    };
}

static int compare_u64(const void *left, const void *right)
{
    uint64_t a = *(const uint64_t *)left;
    uint64_t b = *(const uint64_t *)right;
    return (a > b) - (a < b);
}

static int compare_i64(const void *left, const void *right)
{
    int64_t a = *(const int64_t *)left;
    int64_t b = *(const int64_t *)right;
    return (a > b) - (a < b);
}

static void pin_core(int core)
{
    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(core, &set);
    if (sched_setaffinity(0, sizeof set, &set) != 0) {
        perror("sched_setaffinity");
        exit(2);
    }
}

static unsigned correctness(pack_fn baseline, pack_fn candidate)
{
    uint8_t expected[NTRUPLUS_POLYBYTES];
    uint8_t actual[NTRUPLUS_POLYBYTES];
    unsigned mismatches = 0;
    for (size_t test = 0; test < NINPUTS; test++) {
        baseline(expected, &inputs[test]);
        candidate(actual, &inputs[test]);
        mismatches += memcmp(expected, actual, sizeof expected) != 0;
    }
    return mismatches;
}

int main(int argc, char **argv)
{
    const char *mode = argc > 1 ? argv[1] : "generic";
    int core = argc > 2 ? atoi(argv[2]) : 3;
    pack_fn baseline;
    pack_fn candidate;
    uint64_t baseline_cycles[NTESTS];
    uint64_t candidate_cycles[NTESTS];
    uint64_t baseline_instructions[NTESTS];
    uint64_t candidate_instructions[NTESTS];
    int64_t paired_cycles[NTESTS];
    int64_t paired_instructions[NTESTS];

    if (strcmp(mode, "generic") == 0) {
        baseline = generic_baseline;
        candidate = generic_candidate;
    } else if (strcmp(mode, "keygen") == 0) {
        baseline = keygen_baseline;
        candidate = keygen_candidate;
    } else {
        fprintf(stderr, "mode must be generic or keygen\n");
        return 2;
    }

    pin_core(core);
    uint32_t state = 1;
    for (size_t test = 0; test < NINPUTS; test++)
        for (size_t i = 0; i < NTRUPLUS_N; i++) {
            state = state * 1664525u + 1013904223u;
            inputs[test].coeffs[i] =
                (int16_t)(state % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q;
        }

    unsigned mismatches = correctness(baseline, candidate);
    for (int i = 0; i < 1000; i++) {
        baseline(output, &inputs[i % NINPUTS]);
        candidate(output, &inputs[i % NINPUTS]);
    }
    setup_events();

    for (size_t test = 0; test < NTESTS; test++) {
        struct counts a;
        struct counts b;
        if ((test & 1) == 0) {
            a = measure(baseline);
            b = measure(candidate);
        } else {
            b = measure(candidate);
            a = measure(baseline);
        }
        baseline_cycles[test] = a.cycles;
        candidate_cycles[test] = b.cycles;
        baseline_instructions[test] = a.instructions;
        candidate_instructions[test] = b.instructions;
        paired_cycles[test] = (int64_t)b.cycles - (int64_t)a.cycles;
        paired_instructions[test] =
            (int64_t)b.instructions - (int64_t)a.instructions;
    }

    qsort(baseline_cycles, NTESTS, sizeof baseline_cycles[0], compare_u64);
    qsort(candidate_cycles, NTESTS, sizeof candidate_cycles[0], compare_u64);
    qsort(baseline_instructions, NTESTS, sizeof baseline_instructions[0],
          compare_u64);
    qsort(candidate_instructions, NTESTS, sizeof candidate_instructions[0],
          compare_u64);
    qsort(paired_cycles, NTESTS, sizeof paired_cycles[0], compare_i64);
    qsort(paired_instructions, NTESTS, sizeof paired_instructions[0],
          compare_i64);

    printf("mode=%s correctness_mismatches=%u tests=%d iterations=%d\n",
           mode, mismatches, NTESTS, NITERATIONS);
    printf("baseline_cycles_p50=%" PRIu64
           " candidate_cycles_p50=%" PRIu64
           " paired_cycles_p10=%" PRId64
           " paired_cycles_p50=%" PRId64
           " paired_cycles_p90=%" PRId64 "\n",
           baseline_cycles[NTESTS / 2], candidate_cycles[NTESTS / 2],
           paired_cycles[NTESTS / 10],
           paired_cycles[NTESTS / 2],
           paired_cycles[(NTESTS * 9) / 10]);
    printf("baseline_instructions_p50=%" PRIu64
           " candidate_instructions_p50=%" PRIu64
           " paired_instructions_p50=%" PRId64
           " sink=%" PRIu64 "\n",
           baseline_instructions[NTESTS / 2],
           candidate_instructions[NTESTS / 2],
           paired_instructions[NTESTS / 2], sink);
    return mismatches != 0;
}
