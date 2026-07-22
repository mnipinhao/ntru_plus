#if !defined(__linux__)
#error "bench_q31_pair_pipeline_pmu requires Linux perf_event_open"
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

typedef void (*q31_fn)(poly *, const poly *, const poly *, const poly *);

void poly_basemul_add_encap_direct32_q31_tobytes_contract(
    poly *r, const poly *a, const poly *b, const poly *c);
void poly_basemul_add_encap_direct32_q31_pair_u2(
    poly *r, const poly *a, const poly *b, const poly *c);
void poly_basemul_add_encap_direct32_q31_pair_slothy(
    poly *r, const poly *a, const poly *b, const poly *c);

struct count { uint64_t cycles, instructions; };
struct sample { double cycles, instructions; };

static int leader_fd = -1, member_fd = -1;
static poly a, b, c, output;
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

static struct count measure(q31_fn fn)
{
    begin();
    for (int i = 0; i < NITERATIONS; i++)
        fn(&output, &a, &b, &c);
    struct count value = end();
    sink ^= (uint16_t)output.coeffs[0];
    return value;
}

static int cmp_double(const void *left, const void *right)
{
    double a0 = *(const double *)left, b0 = *(const double *)right;
    return (a0 > b0) - (a0 < b0);
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
    double cycles = median(values, 1), instructions = median(values, 0);
    printf("pmu,variant=%s,cycles=%.2f,instructions=%.2f,cpi=%.4f,"
           "paired_delta_cycles=%.2f\n", name, cycles, instructions,
           cycles / instructions, delta[NTESTS / 2]);
}

int main(void)
{
    const q31_fn fns[3] = {
        poly_basemul_add_encap_direct32_q31_tobytes_contract,
        poly_basemul_add_encap_direct32_q31_pair_u2,
        poly_basemul_add_encap_direct32_q31_pair_slothy,
    };
    struct sample samples[3][NTESTS] = {{{0}}};
    uint32_t state = 0x2468ace1u;
    for (int i = 0; i < NTRUPLUS_N; i++) {
        state = state * 1664525u + 1013904223u;
        a.coeffs[i] = (int16_t)((int)(state % 3457u) - 1728);
        state = state * 1664525u + 1013904223u;
        b.coeffs[i] = (int16_t)((int)(state % 3457u) - 1728);
        state = state * 1664525u + 1013904223u;
        c.coeffs[i] = (int16_t)((int)(state % 3457u) - 1728);
    }
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return 2;
    }
    for (int i = 0; i < 300; i++)
        fns[i % 3](&output, &a, &b, &c);
    for (int sample = 0; sample < NTESTS; sample++) {
        for (int slot = 0; slot < 3; slot++) {
            int variant = (sample + slot) % 3;
            struct count value = measure(fns[variant]);
            samples[variant][sample].cycles =
                (double)value.cycles / NITERATIONS;
            samples[variant][sample].instructions =
                (double)value.instructions / NITERATIONS;
        }
    }
    report("production", samples[0], samples[0]);
    report("pair_u2", samples[1], samples[0]);
    report("pair_slothy", samples[2], samples[0]);
    printf("sink=%" PRIu64 "\n", sink);
    close(member_fd);
    close(leader_fd);
    return 0;
}
