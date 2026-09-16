#if !defined(__linux__)
#error "D1-C1 PMU requires Linux"
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_d1.h"
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

#define N 864
#define NINPUTS 16
#define NTESTS 61
#define NITERATIONS 1000
#define NVARIANTS 3

typedef void (*chain_fn)(int16_t *, const int16_t *, const int16_t *);
struct variant { char code; const char *name; chain_fn fn; };
struct counts { uint64_t cycles, instructions, branches; };

void gt864_forward_poly_ntt_all_one_mul_b3(int16_t out[N],
                                            const int16_t in[N]);

static int16_t a[NINPUTS][N] __attribute__((aligned(64)));
static int16_t b[NINPUTS][N] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0xd1c1b864U;
static int leader = -1, instructions_fd = -1, branches_fd = -1;

static uint32_t random_u32(void)
{
    rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5;
    return rng;
}

static void inverse_fr0(int16_t out[N], const int16_t in[N])
{
    int16_t p8[896] = {0};
    gt864_fr0_inverse_ntt9_asm(p8, in);
    gt864_fr0_inverse_finish_asm(out, p8);
}

__attribute__((noinline))
static void old_chain(int16_t *out, const int16_t *left, const int16_t *right)
{
    int16_t fa[N], fb[N], fp[N];
    gt864_forward_poly_ntt_all_one_mul_b3(fa, left);
    gt864_forward_poly_ntt_all_one_mul_b3(fb, right);
    gt864_fr0_basemul_neon(fp, fa, fb);
    inverse_fr0(out, fp);
}

__attribute__((noinline))
static void d1_chain(int16_t *out, const int16_t *left, const int16_t *right)
{
    int16_t fa[N], fb[N], fp[N];
    gt864_forward_poly_ntt_all_one_mul_b3(fa, left);
    gt864_forward_poly_ntt_all_one_mul_b3(fb, right);
    gt864_fr0_basemul_d1_neon(fp, fa, fb);
    inverse_fr0(out, fp);
}

__attribute__((noinline))
static void noop(int16_t *out, const int16_t *left, const int16_t *right)
{
    __asm__ volatile("" : : "r"(out), "r"(left), "r"(right) : "memory");
}

static int centered(int value)
{
    value %= 3457;
    if (value < 0) value += 3457;
    if (value > 1728) value -= 3457;
    return value;
}

static void prepare(void)
{
    int16_t old[N], candidate[N];
    for (int k = 0; k < NINPUTS; k++)
        for (int i = 0; i < N; i++) {
            a[k][i] = (int16_t)((int)(random_u32() % 6913U) - 3456);
            b[k][i] = (int16_t)((int)(random_u32() % 6913U) - 3456);
        }
    for (int k = 0; k < NINPUTS; k++) {
        old_chain(old, a[k], b[k]); d1_chain(candidate, a[k], b[k]);
        for (int i = 0; i < N; i++)
            if (centered(old[i]) != centered(candidate[i])) exit(1);
    }
    puts("correctness,status=pass,complete_chain_pairs=16");
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
    for (int i = 0; i < NITERATIONS; i++) {
        int k = i & (NINPUTS - 1);
        variant->fn(output, a[k], b[k]);
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
        {'O', "old_chain", old_chain}, {'D', "d1_chain", d1_chain},
        {'N', "noop", noop},
    };
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;
    prepare();
    leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    instructions_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader);
    branches_fd = perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions_fd < 0 || branches_fd < 0) return 2;
    for (int v = 0; v < NVARIANTS; v++)
        for (int i = 0; i < 8; i++) variants[v].fn(output, a[i], b[i]);
    for (int sample = 0; sample < NTESTS; sample++)
        for (int position = 0; position < NVARIANTS; position++) {
            const struct variant *selected = NULL;
            for (int v = 0; v < NVARIANTS; v++)
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
