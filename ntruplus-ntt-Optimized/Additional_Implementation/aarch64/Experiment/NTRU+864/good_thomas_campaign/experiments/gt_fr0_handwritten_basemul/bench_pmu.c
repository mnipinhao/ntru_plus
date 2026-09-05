#if !defined(__linux__)
#error "B1-0 PMU benchmark requires Linux"
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

#define N 864
#define Q 3457
#define BOUND 25569
#define NINPUTS 64
#define NTESTS 61
#define NITERATIONS 20000
#define NVARIANTS 3

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *,
                          const int16_t *);
struct variant { char code; const char *name; kernel_fn fn; };
struct counts { uint64_t cycles, instructions, branches; };

extern void gt864_fr0_basemul_neon(int16_t *, const int16_t *,
                                    const int16_t *);
extern void gt864_fr0_basemul_add_neon(int16_t *, const int16_t *,
                                        const int16_t *, const int16_t *);

static int16_t a[NINPUTS][N] __attribute__((aligned(64)));
static int16_t b[NINPUTS][N] __attribute__((aligned(64)));
static int16_t c[NINPUTS][N] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0xb100864u;
static int leader = -1, instructions_fd = -1, branches_fd = -1;

static uint32_t random_u32(void)
{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng;
}

__attribute__((noinline))
static void bm_wrap(int16_t *out, const int16_t *left, const int16_t *right,
                    const int16_t *addend)
{
    (void)addend;
    gt864_fr0_basemul_neon(out, left, right);
}

__attribute__((noinline))
static void add_wrap(int16_t *out, const int16_t *left, const int16_t *right,
                     const int16_t *addend)
{
    gt864_fr0_basemul_add_neon(out, left, right, addend);
}

__attribute__((noinline))
static void noop_wrap(int16_t *out, const int16_t *left, const int16_t *right,
                      const int16_t *addend)
{
    __asm__ volatile("" : : "r"(out), "r"(left), "r"(right), "r"(addend)
                     : "memory");
}

static void prepare(void)
{
    int16_t reference[N], alias[N];
    for (int k = 0; k < NINPUTS; ++k) {
        for (int i = 0; i < N; ++i) {
            a[k][i] = (int16_t)((int)(random_u32() % (2 * BOUND + 1)) - BOUND);
            b[k][i] = (int16_t)((int)(random_u32() % (2 * BOUND + 1)) - BOUND);
            c[k][i] = (int16_t)((int)(random_u32() % (2 * BOUND + 1)) - BOUND);
        }
        gt864_fr0_basemul_neon(reference, a[k], b[k]);
        memcpy(alias, a[k], sizeof(alias));
        gt864_fr0_basemul_neon(alias, alias, b[k]);
        if (memcmp(reference, alias, sizeof(alias)) != 0) exit(1);
        memcpy(alias, b[k], sizeof(alias));
        gt864_fr0_basemul_neon(alias, a[k], alias);
        if (memcmp(reference, alias, sizeof(alias)) != 0) exit(1);
        gt864_fr0_basemul_add_neon(reference, a[k], b[k], c[k]);
        memcpy(alias, c[k], sizeof(alias));
        gt864_fr0_basemul_add_neon(alias, a[k], b[k], alias);
        if (memcmp(reference, alias, sizeof(alias)) != 0) exit(1);
    }
    puts("correctness,status=pass,basemul_alias_a_b=64,basemuladd_alias_c=64");
}

static int perf_open(uint64_t config, int group)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe));
    pe.type = PERF_TYPE_HARDWARE; pe.size = sizeof(pe); pe.config = config;
    pe.disabled = group == -1; pe.exclude_kernel = 1; pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group, 0);
}

static struct counts measure(const struct variant *variant)
{
    struct { uint64_t nr, value[3]; } data = {0, {0, 0, 0}};
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < NITERATIONS; ++i) {
        int k = i & 63;
        variant->fn(output, a[k], b[k], c[k]);
    }
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &data, sizeof(data)) != (ssize_t)sizeof(data) || data.nr != 3)
        exit(2);
    sink += (uint16_t)output[(unsigned)variant->code % N];
    return (struct counts){data.value[0], data.value[1], data.value[2]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'B', "basemul", bm_wrap},
        {'A', "basemuladd", add_wrap},
        {'N', "noop", noop_wrap},
    };
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;
    prepare();
    leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    instructions_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader);
    branches_fd = perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions_fd < 0 || branches_fd < 0) return 2;
    for (int v = 0; v < NVARIANTS; ++v)
        for (int i = 0; i < 100; ++i)
            variants[v].fn(output, a[i & 63], b[i & 63], c[i & 63]);
    for (int sample = 0; sample < NTESTS; ++sample)
        for (int position = 0; position < NVARIANTS; ++position) {
            const struct variant *selected = NULL;
            for (int v = 0; v < NVARIANTS; ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (selected == NULL) return 2;
            struct counts value = measure(selected);
            printf("sample,index=%d,position=%d,variant=%s,cycles=%.6f,"
                   "instructions=%.6f,branches=%.6f\n", sample, position,
                   selected->name, (double)value.cycles / NITERATIONS,
                   (double)value.instructions / NITERATIONS,
                   (double)value.branches / NITERATIONS);
        }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(branches_fd); close(instructions_fd); close(leader);
    return 0;
}
