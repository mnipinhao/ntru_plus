#if !defined(__linux__)
#error "bench_direct_bpq_endpoint_pmu requires Linux perf_event_open"
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

typedef struct { int16_t coeffs[NTRUPLUS_N]; } bpq_poly;
typedef void (*bench_fn)(void);
struct count { uint64_t cycles, instructions; };
struct sample { double cycles, instructions; };

void gt_experiment_poly_ntt_to_bpq(bpq_poly *r, const poly *a);

static const uint8_t slot_for_k32[32] = {
    3, 7, 1, 0, 6, 2, 5, 4,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
};

static int leader_fd = -1, member_fd = -1;
static poly input, blockmajor;
static bpq_poly bpq_output;
static volatile uint64_t sink;

static void blockmajor_to_bpq(bpq_poly *out, const poly *in)
{
    for (int row = 0; row < 3; row++) {
        for (int k32 = 0; k32 < 32; k32++) {
            const int j = (32 * row + 3 * k32) % 96;
            const int slot = 32 * row + slot_for_k32[k32];
            memcpy(&out->coeffs[8 * slot], &in->coeffs[4 * j], 8);
            memcpy(&out->coeffs[8 * slot + 4], &in->coeffs[384 + 4 * j], 8);
        }
    }
}

static void run_production_raw(void)
{
    poly_ntt(&blockmajor, &input);
}

static void run_production_bpq_endpoint(void)
{
    poly_ntt(&blockmajor, &input);
    blockmajor_to_bpq(&bpq_output, &blockmajor);
}

static void run_direct_bpq_endpoint(void)
{
    gt_experiment_poly_ntt_to_bpq(&bpq_output, &input);
}

static int perf_open(uint64_t config, int group_fd)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof pe);
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof pe;
    pe.config = config;
    pe.disabled = group_fd == -1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group_fd, 0);
}

static void begin(void)
{
    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
}

static struct count end(void)
{
    struct { uint64_t nr, value[2]; } data = {0, {0, 0}};
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof data) != (ssize_t)sizeof data ||
        data.nr != 2) {
        perror("perf read");
        exit(2);
    }
    return (struct count){data.value[0], data.value[1]};
}

static struct count measure(bench_fn fn)
{
    begin();
    for (int i = 0; i < NITERATIONS; i++)
        fn();
    struct count value = end();
    sink ^= (uint16_t)bpq_output.coeffs[0];
    sink ^= (uint16_t)blockmajor.coeffs[0];
    return value;
}

static int cmp_double(const void *left, const void *right)
{
    double a = *(const double *)left, b = *(const double *)right;
    return (a > b) - (a < b);
}

static double median(const struct sample values[NTESTS], int cycles)
{
    double sorted[NTESTS];
    for (int i = 0; i < NTESTS; i++)
        sorted[i] = cycles ? values[i].cycles : values[i].instructions;
    qsort(sorted, NTESTS, sizeof sorted[0], cmp_double);
    return sorted[NTESTS / 2];
}

static void report(const char *name, const struct sample values[NTESTS],
                   const struct sample baseline[NTESTS])
{
    double delta[NTESTS];
    for (int i = 0; i < NTESTS; i++)
        delta[i] = values[i].cycles - baseline[i].cycles;
    qsort(delta, NTESTS, sizeof delta[0], cmp_double);
    const double cycles = median(values, 1);
    const double instructions = median(values, 0);
    printf("pmu,variant=%s,cycles=%.2f,instructions=%.2f,cpi=%.4f,"
           "paired_delta_cycles=%.2f\n", name, cycles, instructions,
           cycles / instructions, delta[NTESTS / 2]);
}

int main(void)
{
    const bench_fn fns[3] = {
        run_production_raw,
        run_production_bpq_endpoint,
        run_direct_bpq_endpoint,
    };
    struct sample samples[3][NTESTS] = {{{0}}};
    uint32_t state = 0x42505143u;

    for (int i = 0; i < NTRUPLUS_N; i++) {
        state = state * 1664525u + 1013904223u;
        input.coeffs[i] = (int16_t)((int)(state % 3457u) - 1728);
    }
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return 2;
    }
    for (int i = 0; i < 300; i++)
        fns[i % 3]();
    for (int sample = 0; sample < NTESTS; sample++) {
        for (int slot = 0; slot < 3; slot++) {
            const int variant = (sample + slot) % 3;
            const struct count value = measure(fns[variant]);
            samples[variant][sample].cycles =
                (double)value.cycles / NITERATIONS;
            samples[variant][sample].instructions =
                (double)value.instructions / NITERATIONS;
        }
    }
    report("production_raw_blockmajor", samples[0], samples[0]);
    report("production_plus_bpq_adapter", samples[1], samples[1]);
    report("direct_bpq_endpoint", samples[2], samples[1]);
    printf("sink=%" PRIu64 "\n", sink);
    close(member_fd);
    close(leader_fd);
    return 0;
}
