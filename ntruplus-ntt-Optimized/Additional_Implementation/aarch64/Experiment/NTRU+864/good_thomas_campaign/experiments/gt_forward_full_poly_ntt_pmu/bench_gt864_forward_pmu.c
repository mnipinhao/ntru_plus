#if !defined(__linux__)
#error "bench_gt864_forward_pmu requires Linux perf_event_open"
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

typedef void (*ntt_fn)(int16_t *, const int16_t *);

struct counts {
    uint64_t cycles;
    uint64_t instructions;
};

struct guarded_poly {
    uint64_t pre[8];
    int16_t coeffs[N];
    uint64_t post[8];
} __attribute__((aligned(64)));

extern void poly_ntt(int16_t *out, const int16_t *in);
extern void gt864_forward_poly_ntt_experiment(int16_t *out,
                                               const int16_t *in);

static int leader_fd = -1;
static int member_fd = -1;
static int16_t inputs[NINPUTS][N] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng_state = 0x8645f00du;

static uint32_t random_u32(void)
{
    uint32_t x = rng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    rng_state = x;
    return x;
}

static int centered(int value)
{
    value %= Q;
    if (value < 0)
        value += Q;
    if (value > Q / 2)
        value -= Q;
    return value;
}

static void fill_inputs(void)
{
    for (int input = 0; input < NINPUTS; ++input)
        for (int i = 0; i < N; ++i)
            inputs[input][i] = (int16_t)((int)(random_u32() % Q) - 1728);
}

static void set_guards(struct guarded_poly *value, uint64_t tag)
{
    for (int i = 0; i < 8; ++i) {
        value->pre[i] = 0xa5a5000000000000ULL ^ tag ^ (uint64_t)i;
        value->post[i] = 0x5a5a000000000000ULL ^ tag ^ (uint64_t)i;
    }
}

static int guards_ok(const struct guarded_poly *value, uint64_t tag)
{
    for (int i = 0; i < 8; ++i)
        if (value->pre[i] != (0xa5a5000000000000ULL ^ tag ^ (uint64_t)i)
                || value->post[i] !=
                   (0x5a5a000000000000ULL ^ tag ^ (uint64_t)i))
            return 0;
    return 1;
}

static int outputs_match(const int16_t official[N], const int16_t fr0[N])
{
    for (int i = 0; i < N; ++i)
        if (centered(official[i]) !=
            centered(fr0[gt864_fr0_for_official[i]]))
            return 0;
    return 1;
}

static int run_correctness(void)
{
    int nonalias_cases = 0;
    int alias_cases = 0;

    for (int input = 0; input < NINPUTS; ++input) {
        struct guarded_poly official;
        struct guarded_poly candidate;
        struct guarded_poly official_alias;
        struct guarded_poly candidate_alias;
        int16_t preserved[N];
        const uint64_t tag = (uint64_t)input << 16;

        memcpy(preserved, inputs[input], sizeof(preserved));
        set_guards(&official, tag ^ 1);
        set_guards(&candidate, tag ^ 2);
        poly_ntt(official.coeffs, inputs[input]);
        gt864_forward_poly_ntt_experiment(candidate.coeffs, inputs[input]);
        if (!guards_ok(&official, tag ^ 1) ||
            !guards_ok(&candidate, tag ^ 2) ||
            memcmp(preserved, inputs[input], sizeof(preserved)) != 0 ||
            !outputs_match(official.coeffs, candidate.coeffs))
            return 1;
        ++nonalias_cases;

        set_guards(&official_alias, tag ^ 3);
        set_guards(&candidate_alias, tag ^ 4);
        memcpy(official_alias.coeffs, inputs[input], sizeof(preserved));
        memcpy(candidate_alias.coeffs, inputs[input], sizeof(preserved));
        poly_ntt(official_alias.coeffs, official_alias.coeffs);
        gt864_forward_poly_ntt_experiment(candidate_alias.coeffs,
                                           candidate_alias.coeffs);
        if (!guards_ok(&official_alias, tag ^ 3) ||
            !guards_ok(&candidate_alias, tag ^ 4) ||
            !outputs_match(official_alias.coeffs, candidate_alias.coeffs))
            return 1;
        ++alias_cases;
    }

    printf("correctness,status=pass,nonalias_cases=%d,alias_cases=%d\n",
           nonalias_cases, alias_cases);
    return 0;
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

static void setup_perf(void)
{
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        exit(2);
    }
}

static struct counts measure(ntt_fn fn, int candidate)
{
    struct {
        uint64_t nr;
        uint64_t value[2];
    } data = {0, {0, 0}};

    if (ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) != 0 ||
        ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP) != 0) {
        perror("perf begin");
        exit(2);
    }
    for (int i = 0; i < NITERATIONS; ++i)
        fn(output, inputs[i & (NINPUTS - 1)]);
    if (ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP) != 0) {
        perror("perf end");
        exit(2);
    }
    if (read(leader_fd, &data, sizeof(data)) != (ssize_t)sizeof(data) ||
        data.nr != 2) {
        perror("perf read");
        exit(2);
    }
    for (int i = 0; i < 16; ++i) {
        int physical = (i * 53) % N;
        int source = candidate ? gt864_fr0_for_official[physical] : physical;
        sink += (uint16_t)(centered(output[source]) + 1728);
    }
    return (struct counts){data.value[0], data.value[1]};
}

static void warmup(ntt_fn fn)
{
    for (int i = 0; i < NWARMUP; ++i)
        fn(output, inputs[i & (NINPUTS - 1)]);
}

int main(int argc, char **argv)
{
    const ntt_fn fns[2] = {poly_ntt, gt864_forward_poly_ntt_experiment};
    const char *names[2] = {"official", "gt"};
    int order[2];

    if (argc != 2 || (strcmp(argv[1], "OG") != 0 &&
                      strcmp(argv[1], "GO") != 0)) {
        fprintf(stderr, "usage: %s OG|GO\n", argv[0]);
        return 2;
    }
    order[0] = argv[1][0] == 'O' ? 0 : 1;
    order[1] = 1 - order[0];

    fill_inputs();
    if (run_correctness() != 0) {
        fprintf(stderr, "correctness,status=fail\n");
        return 1;
    }
    setup_perf();
    warmup(fns[0]);
    warmup(fns[1]);

    printf("config,order=%s,samples=%d,calls=%d,warmups=%d\n",
           argv[1], NTESTS, NITERATIONS, NWARMUP);
    for (int sample = 0; sample < NTESTS; ++sample) {
        for (int position = 0; position < 2; ++position) {
            int variant = order[position];
            struct counts value = measure(fns[variant], variant == 1);
            printf("sample,order=%s,index=%d,position=%d,variant=%s,"
                   "cycles=%.6f,instructions=%.6f\n",
                   argv[1], sample, position, names[variant],
                   (double)value.cycles / NITERATIONS,
                   (double)value.instructions / NITERATIONS);
        }
    }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(member_fd);
    close(leader_fd);
    return 0;
}
