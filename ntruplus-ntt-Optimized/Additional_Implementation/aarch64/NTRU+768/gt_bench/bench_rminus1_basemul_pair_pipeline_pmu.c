#if !defined(__linux__)
#error "bench_rminus1_basemul_pair_pipeline_pmu requires Linux perf_event_open"
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

void poly_basemul_rminus1_pair_u2(poly *r, const poly *a, const poly *b);
void poly_basemul_rminus1_pair_slothy(poly *r, const poly *a, const poly *b);
void rminus1_production_abi_safe(poly *r, const poly *a, const poly *b);

typedef void (*basemul_fn)(poly *, const poly *, const poly *);

struct count {
    uint64_t cycles;
    uint64_t instructions;
};

struct sample {
    double cycles;
    double instructions;
};

static int leader_fd = -1;
static int member_fd = -1;
static poly input_a, input_b, output_poly;
static volatile uint64_t sink;

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
    if (read(leader_fd, &data, sizeof data) != (ssize_t)sizeof data ||
        data.nr != 2) {
        perror("perf group read");
        exit(2);
    }
    return (struct count){data.value[0], data.value[1]};
}

static struct count measure(basemul_fn fn)
{
    begin_pmu();
    for (int i = 0; i < NITERATIONS; i++)
        fn(&output_poly, &input_a, &input_b);
    struct count out = end_pmu();
    sink ^= (uint16_t)output_poly.coeffs[0];
    return out;
}

static int cmp_double(const void *a, const void *b)
{
    const double x = *(const double *)a;
    const double y = *(const double *)b;
    return (x > y) - (x < y);
}

static double median(const struct sample samples[NTESTS], int cycles)
{
    double values[NTESTS];
    for (int i = 0; i < NTESTS; i++)
        values[i] = cycles ? samples[i].cycles : samples[i].instructions;
    qsort(values, NTESTS, sizeof values[0], cmp_double);
    return values[NTESTS / 2];
}

static void report(const char *variant, const struct sample samples[NTESTS],
                   const struct sample baseline[NTESTS])
{
    double deltas[NTESTS];
    int wins = 0;
    for (int i = 0; i < NTESTS; i++) {
        deltas[i] = samples[i].cycles - baseline[i].cycles;
        wins += deltas[i] < 0.0;
    }
    qsort(deltas, NTESTS, sizeof deltas[0], cmp_double);
    const double cyc = median(samples, 1);
    const double ins = median(samples, 0);
    printf("pmu,variant=%s,cycles=%.2f,instructions=%.2f,cpi=%.4f,"
           "paired_delta_cycles=%.2f,wins=%d/%d\n",
           variant, cyc, ins, cyc / ins, deltas[NTESTS / 2], wins, NTESTS);
}

static void prepare(void)
{
    uint32_t state = 0x6b193d41u;
    for (int i = 0; i < NTRUPLUS_N; i++) {
        state = state * 1664525u + 1013904223u;
        input_a.coeffs[i] =
            (int16_t)((int)(state % NTRUPLUS_Q) - NTRUPLUS_Q / 2);
        state = state * 1664525u + 1013904223u;
        input_b.coeffs[i] =
            (int16_t)((int)(state % NTRUPLUS_Q) - NTRUPLUS_Q / 2);
    }
}

int main(void)
{
    const basemul_fn functions[] = {
        rminus1_production_abi_safe,
        poly_basemul_rminus1_pair_u2,
        poly_basemul_rminus1_pair_slothy,
    };
    struct sample samples[3][NTESTS] = {{{0}}};

    prepare();
    if (init_pmu() != 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return 2;
    }
    for (int i = 0; i < 300; i++)
        functions[i % 3](&output_poly, &input_a, &input_b);

    for (int sample = 0; sample < NTESTS; sample++) {
        for (int slot = 0; slot < 3; slot++) {
            const int variant = (slot + sample) % 3;
            const struct count count = measure(functions[variant]);
            samples[variant][sample].cycles =
                (double)count.cycles / NITERATIONS;
            samples[variant][sample].instructions =
                (double)count.instructions / NITERATIONS;
        }
    }

    report("production", samples[0], samples[0]);
    report("u2_source_order", samples[1], samples[0]);
    report("pair_slothy", samples[2], samples[0]);
    printf("sink=%" PRIu64 "\n", sink);
    return 0;
}
