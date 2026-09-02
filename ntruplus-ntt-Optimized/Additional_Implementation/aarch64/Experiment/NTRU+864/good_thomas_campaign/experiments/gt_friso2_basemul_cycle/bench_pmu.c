#if !defined(__linux__)
#error "bench_pmu requires Linux perf_event_open"
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

#include "gt864_friso2_basemul_neon.h"

#define N 864
#define Q 3457
#define NINPUTS 64
#define NTESTS 61
#define NITERATIONS 20000
#define NWARMUP 100

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *,
                          const int16_t *);
struct counts { uint64_t cycles, instructions; };
struct variant { char code; const char *name; kernel_fn fn; };

static int16_t inputs_a[NINPUTS][N] __attribute__((aligned(64)));
static int16_t inputs_b[NINPUTS][N] __attribute__((aligned(64)));
static int16_t inputs_c[NINPUTS][N] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static int leader_fd = -1, member_fd = -1;
static uint32_t rng_state = 0x864b51u;

static uint32_t random_u32(void)
{
    uint32_t x = rng_state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return rng_state = x;
}

static int canonical(int value)
{
    value %= Q;
    return value < 0 ? value + Q : value;
}

static int outputs_match(const int16_t a[N], const int16_t b[N])
{
    for (int i = 0; i < N; ++i)
        if (canonical(a[i]) != canonical(b[i])) return 0;
    return 1;
}

__attribute__((noinline))
static void staged_wrap(int16_t *out, const int16_t *a, const int16_t *b,
                        const int16_t *c)
{
    (void)c;
    gt864_friso2_basemul_staged(out, a, b);
}

__attribute__((noinline))
static void direct_wrap(int16_t *out, const int16_t *a, const int16_t *b,
                        const int16_t *c)
{
    (void)c;
    gt864_friso2_basemul_direct(out, a, b);
}

__attribute__((noinline))
static void staged_add_wrap(int16_t *out, const int16_t *a, const int16_t *b,
                            const int16_t *c)
{
    gt864_friso2_basemul_add_staged(out, a, b, c);
}

__attribute__((noinline))
static void direct_add_wrap(int16_t *out, const int16_t *a, const int16_t *b,
                            const int16_t *c)
{
    gt864_friso2_basemul_add_direct(out, a, b, c);
}

__attribute__((noinline))
static void noop_wrap(int16_t *out, const int16_t *a, const int16_t *b,
                      const int16_t *c)
{
    __asm__ volatile("" : : "r"(out), "r"(a), "r"(b), "r"(c) : "memory");
}

static void prepare(void)
{
    int16_t staged[N], direct[N], alias[N];
    for (int k = 0; k < NINPUTS; ++k) {
        for (int i = 0; i < N; ++i) {
            int component = i % 24 / 8;
            int bound = component == 0 ? 26306 : 5185;
            inputs_a[k][i] = (int16_t)((int)(random_u32() %
                (uint32_t)(2 * bound + 1)) - bound);
            inputs_b[k][i] = (int16_t)((int)(random_u32() %
                (uint32_t)(2 * bound + 1)) - bound);
            inputs_c[k][i] = (int16_t)((int)(random_u32() %
                (uint32_t)(2 * bound + 1)) - bound);
        }
        gt864_friso2_basemul_staged(staged, inputs_a[k], inputs_b[k]);
        gt864_friso2_basemul_direct(direct, inputs_a[k], inputs_b[k]);
        if (!outputs_match(staged, direct)) {
            fprintf(stderr, "BaseMul differential failed at input %d\n", k);
            exit(1);
        }
        memcpy(alias, inputs_a[k], sizeof(alias));
        gt864_friso2_basemul_direct(alias, alias, inputs_b[k]);
        if (!outputs_match(staged, alias)) {
            fprintf(stderr, "BaseMul alias failed at input %d\n", k);
            exit(1);
        }
        gt864_friso2_basemul_add_staged(staged, inputs_a[k], inputs_b[k],
                                        inputs_c[k]);
        gt864_friso2_basemul_add_direct(direct, inputs_a[k], inputs_b[k],
                                        inputs_c[k]);
        if (!outputs_match(staged, direct)) {
            fprintf(stderr, "BaseMulAdd differential failed at input %d\n", k);
            exit(1);
        }
    }
    puts("correctness,status=pass,basemul=64,basemul_alias=64,basemuladd=64");
}

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

static struct counts measure(const struct variant *variant)
{
    struct { uint64_t nr, value[2]; } data = {0, {0, 0}};
    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < NITERATIONS; ++i) {
        int input = i & 63;
        variant->fn(output, inputs_a[input], inputs_b[input], inputs_c[input]);
    }
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof(data)) != (ssize_t)sizeof(data)
        || data.nr != 2) {
        perror("perf read");
        exit(2);
    }
    sink += (uint16_t)output[(unsigned)variant->code % N];
    return (struct counts){data.value[0], data.value[1]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'S', "staged", staged_wrap},
        {'D', "direct", direct_wrap},
        {'A', "staged_add", staged_add_wrap},
        {'B', "direct_add", direct_add_wrap},
        {'N', "noop", noop_wrap},
    };
    if (argc != 2 || strlen(argv[1]) != 5) {
        fprintf(stderr, "usage: %s SDBAN|NABDS\n", argv[0]);
        return 2;
    }
    prepare();
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return 2;
    }
    for (unsigned v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
        for (int i = 0; i < NWARMUP; ++i)
            variants[v].fn(output, inputs_a[i & 63], inputs_b[i & 63],
                           inputs_c[i & 63]);
    printf("config,order=%s,samples=%d,calls=%d,warmups=%d\n",
           argv[1], NTESTS, NITERATIONS, NWARMUP);
    for (int sample = 0; sample < NTESTS; ++sample) {
        for (int position = 0; position < 5; ++position) {
            const struct variant *selected = NULL;
            for (unsigned v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (selected == NULL) return 2;
            const struct counts value = measure(selected);
            printf("sample,order=%s,index=%d,position=%d,variant=%s,"
                   "cycles=%.6f,instructions=%.6f\n",
                   argv[1], sample, position, selected->name,
                   (double)value.cycles / NITERATIONS,
                   (double)value.instructions / NITERATIONS);
        }
    }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(member_fd);
    close(leader_fd);
    return 0;
}
