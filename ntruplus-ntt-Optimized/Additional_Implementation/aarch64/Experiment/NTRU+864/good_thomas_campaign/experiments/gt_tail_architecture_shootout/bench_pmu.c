#if !defined(__linux__)
#error "A1 PMU benchmark requires Linux"
#endif
#ifndef _GNU_SOURCE
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

#define Q 3457
#define NINPUTS 64
#define NVARIANTS 4
#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 50000
#endif

typedef void (*tail_fn)(int16_t *, const int16_t *);
struct variant { char code; const char *name; tail_fn fn; const int16_t *input; size_t stride; };
struct counts { uint64_t cycles, instructions, loads, stores, branches; };

extern void gt864_tail_t0_current(int16_t *, const int16_t *);
extern void gt864_tail_t1_bank_major(int16_t *, const int16_t *);
extern void gt864_tail_t2_six_bank_simd(int16_t *, const int16_t *);

static int16_t column_inputs[NINPUTS][128] __attribute__((aligned(64)));
static int16_t bank_inputs[NINPUTS][96] __attribute__((aligned(64)));
static int16_t output[96] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0xa1864U;
static int fds[5] = {-1, -1, -1, -1, -1};

static uint32_t random_u32(void)
{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng;
}

static int centered(int value)
{
    value %= Q;
    if (value < 0) value += Q;
    if (value > Q / 2) value -= Q;
    return value;
}

static void noop(int16_t *out, const int16_t *in)
{
    __asm__ volatile("" : : "r"(out), "r"(in) : "memory");
}

static void prepare(void)
{
    int16_t reference[96], candidate[96];
    for (int k = 0; k < NINPUTS; ++k) {
        memset(column_inputs[k], 0, sizeof(column_inputs[k]));
        for (int t = 0; t < 16; ++t)
            for (int bank = 0; bank < 6; ++bank) {
                int16_t value = (int16_t)((int)(random_u32() % Q) - 1728);
                column_inputs[k][8 * t + bank] = value;
                bank_inputs[k][16 * bank + t] = value;
            }
        gt864_tail_t0_current(reference, column_inputs[k]);
        gt864_tail_t1_bank_major(candidate, bank_inputs[k]);
        if (memcmp(reference, candidate, sizeof(reference)) != 0) exit(1);
        gt864_tail_t2_six_bank_simd(candidate, column_inputs[k]);
        for (int i = 0; i < 96; ++i)
            if (centered(reference[i]) != centered(candidate[i])) exit(1);
    }
    puts("correctness,status=pass,cases=64");
}

static int perf_open(uint32_t type, uint64_t config, int group)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe));
    pe.type = type;
    pe.size = sizeof(pe);
    pe.config = config;
    pe.disabled = group == -1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group, 0);
}

static void setup_perf(void)
{
    fds[0] = perf_open(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1);
    fds[1] = perf_open(PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, fds[0]);
    fds[2] = perf_open(PERF_TYPE_RAW, 0x06, fds[0]); /* LD_RETIRED */
    fds[3] = perf_open(PERF_TYPE_RAW, 0x07, fds[0]); /* ST_RETIRED */
    fds[4] = perf_open(PERF_TYPE_RAW, 0x21, fds[0]); /* BR_RETIRED */
    for (int i = 0; i < 5; ++i)
        if (fds[i] < 0) {
            fprintf(stderr, "perf event %d failed: %s\n", i, strerror(errno));
            exit(2);
        }
}

static struct counts measure(const struct variant *variant)
{
    struct { uint64_t nr, value[5]; } data = {0, {0, 0, 0, 0, 0}};
    ioctl(fds[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(fds[0], PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < NITERATIONS; ++i)
        variant->fn(output, variant->input + (size_t)(i & 63) * variant->stride);
    ioctl(fds[0], PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(fds[0], &data, sizeof(data)) != (ssize_t)sizeof(data) || data.nr != 5) exit(2);
    sink += (uint16_t)output[(unsigned)variant->code % 96];
    return (struct counts){data.value[0], data.value[1], data.value[2], data.value[3], data.value[4]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'0', "T0", gt864_tail_t0_current, &column_inputs[0][0], 128},
        {'1', "T1", gt864_tail_t1_bank_major, &bank_inputs[0][0], 96},
        {'2', "T2", gt864_tail_t2_six_bank_simd, &column_inputs[0][0], 128},
        {'N', "noop", noop, &column_inputs[0][0], 128},
    };
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;
    prepare();
    setup_perf();
    for (int v = 0; v < NVARIANTS; ++v)
        for (int i = 0; i < 200; ++i) variants[v].fn(output, variants[v].input);
    for (int sample = 0; sample < NTESTS; ++sample)
        for (int position = 0; position < NVARIANTS; ++position) {
            const struct variant *selected = NULL;
            for (int v = 0; v < NVARIANTS; ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (!selected) return 2;
            struct counts c = measure(selected);
            printf("sample,index=%d,position=%d,variant=%s,cycles=%.6f,instructions=%.6f,loads=%.6f,stores=%.6f,branches=%.6f\n",
                   sample, position, selected->name,
                   (double)c.cycles / NITERATIONS,
                   (double)c.instructions / NITERATIONS,
                   (double)c.loads / NITERATIONS, (double)c.stores / NITERATIONS,
                   (double)c.branches / NITERATIONS);
        }
    printf("meta,sink=%" PRIu64 "\n", sink);
    for (int i = 4; i >= 0; --i) close(fds[i]);
    return 0;
}
