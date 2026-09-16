#if !defined(__linux__)
#error "A2 PMU benchmark requires Linux"
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "gt864_fr0_inverse_asm.h"

#include <asm/unistd.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#define NINPUTS 64
#define NTESTS 61
#define NITERATIONS 20000
#define NVARIANTS 5

typedef void (*kernel_fn)(int16_t *, const int16_t *);
struct variant { char code; const char *name; kernel_fn fn; const int16_t *in; size_t stride; };
struct counts { uint64_t cycles, instructions, branches; };

void gt864_fr0_inverse_finish_st1(int16_t out[864], const int16_t in[896]);

static int16_t fr0[NINPUTS][864] __attribute__((aligned(64)));
static int16_t p8[NINPUTS][896] __attribute__((aligned(64)));
static int16_t scratch[896] __attribute__((aligned(64)));
static int16_t output[864] __attribute__((aligned(64)));
static uint32_t rng = 0xa216U;
static volatile uint64_t sink;
static int leader = -1, instructions_fd = -1, branches_fd = -1;

static uint32_t random_u32(void)
{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng;
}

static void noop(int16_t *out, const int16_t *in)
{
    __asm__ volatile("" : : "r"(out), "r"(in) : "memory");
}

static void full_baseline(int16_t *out, const int16_t *in)
{
    gt864_fr0_inverse_ntt9_asm(scratch, in);
    gt864_fr0_inverse_finish_asm(out, scratch);
}

static void full_st1(int16_t *out, const int16_t *in)
{
    gt864_fr0_inverse_ntt9_asm(scratch, in);
    gt864_fr0_inverse_finish_st1(out, scratch);
}

static void prepare(void)
{
    int16_t baseline[864], candidate[864];
    for (int k = 0; k < NINPUTS; ++k) {
        for (int i = 0; i < 864; ++i)
            fr0[k][i] = (int16_t)((int)(random_u32() % 4411U) - 2205);
        gt864_fr0_inverse_ntt9_asm(p8[k], fr0[k]);
        gt864_fr0_inverse_finish_asm(baseline, p8[k]);
        gt864_fr0_inverse_finish_st1(candidate, p8[k]);
        if (memcmp(baseline, candidate, sizeof(baseline)) != 0) exit(1);
        full_baseline(baseline, fr0[k]);
        full_st1(candidate, fr0[k]);
        if (memcmp(baseline, candidate, sizeof(baseline)) != 0) exit(1);
    }
    puts("correctness,status=pass,i16=64,full_inverse=64");
}

static int perf_open(uint64_t config, int group)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe)); pe.type = PERF_TYPE_HARDWARE; pe.size = sizeof(pe);
    pe.config = config; pe.disabled = group == -1; pe.exclude_kernel = 1;
    pe.exclude_hv = 1; pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group, 0);
}

static void setup_perf(void)
{
    leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    instructions_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader);
    branches_fd = perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions_fd < 0 || branches_fd < 0) exit(2);
}

static struct counts measure(const struct variant *v)
{
    struct { uint64_t nr, value[3]; } data = {0, {0, 0, 0}};
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < NITERATIONS; ++i)
        v->fn(output, v->in + (size_t)(i & 63) * v->stride);
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &data, sizeof(data)) != (ssize_t)sizeof(data) || data.nr != 3) exit(2);
    sink += (uint16_t)output[(unsigned)v->code % 864];
    return (struct counts){data.value[0], data.value[1], data.value[2]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'a', "i16_baseline", gt864_fr0_inverse_finish_asm, &p8[0][0], 896},
        {'b', "i16_st1", gt864_fr0_inverse_finish_st1, &p8[0][0], 896},
        {'c', "full_baseline", full_baseline, &fr0[0][0], 864},
        {'d', "full_st1", full_st1, &fr0[0][0], 864},
        {'N', "noop", noop, &fr0[0][0], 864},
    };
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;
    prepare(); setup_perf();
    for (int v = 0; v < NVARIANTS; ++v)
        for (int i = 0; i < 100; ++i) variants[v].fn(output, variants[v].in);
    for (int sample = 0; sample < NTESTS; ++sample)
        for (int position = 0; position < NVARIANTS; ++position) {
            const struct variant *selected = 0;
            for (int v = 0; v < NVARIANTS; ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (!selected) return 2;
            struct counts c = measure(selected);
            printf("sample,index=%d,position=%d,variant=%s,cycles=%.6f,instructions=%.6f,branches=%.6f\n",
                   sample, position, selected->name,
                   (double)c.cycles / NITERATIONS,
                   (double)c.instructions / NITERATIONS,
                   (double)c.branches / NITERATIONS);
        }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(branches_fd); close(instructions_fd); close(leader);
    return 0;
}
