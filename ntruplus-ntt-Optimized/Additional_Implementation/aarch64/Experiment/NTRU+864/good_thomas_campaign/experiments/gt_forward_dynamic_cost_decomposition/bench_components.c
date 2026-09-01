#if !defined(__linux__)
#error "bench_components requires Linux perf_event_open"
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

#include "gt864_fr0_to_official_map.h"

#define N 864
#define P8N 896
#define Q 3457
#define NINPUTS 64
#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 20000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif

typedef void (*kernel_fn)(int16_t *, const int16_t *);
struct counts { uint64_t cycles, instructions; };
struct variant {
    char code;
    const char *name;
    kernel_fn fn;
    const int16_t *input;
    size_t stride;
};

extern void poly_ntt(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_experiment(int16_t *, const int16_t *);
extern void gt864_top_split_ld3(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2(int16_t *, const int16_t *);
extern void gt864_forward_noop(int16_t *, const int16_t *);

static int16_t inputs[NINPUTS][N] __attribute__((aligned(64)));
static int16_t p8_inputs[NINPUTS][P8N] __attribute__((aligned(64)));
static int16_t output[P8N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static int leader_fd = -1, member_fd = -1;
static uint32_t rng_state = 0x8645f00du;

static uint32_t random_u32(void)
{
    uint32_t x = rng_state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return rng_state = x;
}

static int centered(int value)
{
    value %= Q;
    if (value < 0) value += Q;
    if (value > Q / 2) value -= Q;
    return value;
}

static int outputs_match(const int16_t official[N], const int16_t fr0[N])
{
    for (int i = 0; i < N; ++i)
        if (centered(official[i]) !=
            centered(fr0[gt864_fr0_for_official[i]]))
            return 0;
    return 1;
}

static void prepare(void)
{
    for (int k = 0; k < NINPUTS; ++k) {
        int16_t official[N], fr0[N], alias[N];
        for (int i = 0; i < N; ++i)
            inputs[k][i] = (int16_t)((int)(random_u32() % Q) - 1728);
        gt864_top_split_ld3(p8_inputs[k], inputs[k]);
        poly_ntt(official, inputs[k]);
        gt864_forward_poly_ntt_experiment(fr0, inputs[k]);
        if (!outputs_match(official, fr0)) {
            fprintf(stderr, "nonalias differential failed at input %d\n", k);
            exit(1);
        }
        memcpy(alias, inputs[k], sizeof(alias));
        gt864_forward_poly_ntt_experiment(alias, alias);
        if (!outputs_match(official, alias)) {
            fprintf(stderr, "alias differential failed at input %d\n", k);
            exit(1);
        }
    }
    printf("correctness,status=pass,nonalias_cases=64,alias_cases=64\n");
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
    for (int i = 0; i < NITERATIONS; ++i)
        variant->fn(output, variant->input + (size_t)(i & 63) * variant->stride);
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof(data)) != (ssize_t)sizeof(data) ||
        data.nr != 2) {
        perror("perf read");
        exit(2);
    }
    sink += (uint16_t)output[(unsigned)variant->code % N];
    return (struct counts){data.value[0], data.value[1]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'O', "official", poly_ntt, &inputs[0][0], N},
        {'F', "full_gt", gt864_forward_poly_ntt_experiment, &inputs[0][0], N},
        {'T', "top_split", gt864_top_split_ld3, &inputs[0][0], N},
        {'P', "pass2", gt864_forward_six_bank_pass2, &p8_inputs[0][0], P8N},
        {'N', "noop", gt864_forward_noop, &inputs[0][0], N},
    };
    if (argc != 2 || strlen(argv[1]) != 5) {
        fprintf(stderr, "usage: %s OFTPN|NPTFO\n", argv[0]);
        return 2;
    }
    prepare();
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return 2;
    }
    for (size_t v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
        for (int i = 0; i < NWARMUP; ++i)
            variants[v].fn(output, variants[v].input + (size_t)(i & 63) * variants[v].stride);

    printf("config,order=%s,samples=%d,calls=%d,warmups=%d\n",
           argv[1], NTESTS, NITERATIONS, NWARMUP);
    for (int sample = 0; sample < NTESTS; ++sample) {
        for (int position = 0; position < 5; ++position) {
            const struct variant *selected = NULL;
            for (size_t v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (selected == NULL) return 2;
            struct counts value = measure(selected);
            printf("sample,order=%s,index=%d,position=%d,variant=%s,"
                   "cycles=%.6f,instructions=%.6f\n",
                   argv[1], sample, position, selected->name,
                   (double)value.cycles / NITERATIONS,
                   (double)value.instructions / NITERATIONS);
        }
    }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(member_fd); close(leader_fd);
    return 0;
}
