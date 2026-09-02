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

#define N 864
#define Q 3457
#define NINPUTS 64
#define NTESTS 61
#define NITERATIONS 20000
#define NWARMUP 100

typedef void (*kernel_fn)(int16_t *, const int16_t *);
struct counts { uint64_t cycles, instructions; };
struct variant { char code; const char *name; kernel_fn fn; };

extern void gt864_forward_poly_ntt_all_one_mul_b3(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_friso2(int16_t *, const int16_t *);
extern void gt864_forward_noop(int16_t *, const int16_t *);

static int16_t inputs[NINPUTS][N] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static int leader_fd = -1, member_fd = -1;
static uint32_t rng_state = 0x864cf002u;

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
    return value > Q / 2 ? value - Q : value;
}

static int powmod(int base, int exponent)
{
    int result = 1;
    while (exponent) {
        if (exponent & 1) result = result * base % Q;
        base = base * base % Q;
        exponent >>= 1;
    }
    return result;
}

static size_t fr_index(int top, int row, int column, int component)
{
    int group = top * 18 + row * 2 + column / 8;
    return (size_t)(24 * group + 8 * component + column % 8);
}

static int outputs_match(const int16_t baseline[N], const int16_t candidate[N])
{
    for (int top = 0; top < 2; ++top)
        for (int row = 0; row < 9; ++row)
            for (int column = 0; column < 16; ++column) {
                int tau = powmod(9, 2 * column + 32 * row);
                if (top) tau = 27 * tau % Q;
                for (int component = 0; component < 3; ++component) {
                    size_t index = fr_index(top, row, column, component);
                    int expected = centered(baseline[index] *
                                            powmod(tau, component));
                    if (expected != centered(candidate[index])) return 0;
                }
            }
    return 1;
}

static void prepare(void)
{
    for (int k = 0; k < NINPUTS; ++k) {
        int16_t baseline[N], candidate[N], alias[N];
        for (int i = 0; i < N; ++i)
            inputs[k][i] = (int16_t)((int)(random_u32() % Q) - 1728);
        gt864_forward_poly_ntt_all_one_mul_b3(baseline, inputs[k]);
        gt864_forward_poly_ntt_friso2(candidate, inputs[k]);
        if (!outputs_match(baseline, candidate)) {
            fprintf(stderr, "nonalias differential failed at input %d\n", k);
            exit(1);
        }
        memcpy(alias, inputs[k], sizeof(alias));
        gt864_forward_poly_ntt_friso2(alias, alias);
        if (!outputs_match(baseline, alias)) {
            fprintf(stderr, "alias differential failed at input %d\n", k);
            exit(1);
        }
    }
    puts("correctness,status=pass,nonalias_cases=64,alias_cases=64");
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
        variant->fn(output, inputs[i & 63]);
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof(data)) != (ssize_t)sizeof(data) || data.nr != 2) {
        perror("perf read"); exit(2);
    }
    sink += (uint16_t)output[(unsigned)variant->code % N];
    return (struct counts){data.value[0], data.value[1]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'B', "baseline", gt864_forward_poly_ntt_all_one_mul_b3},
        {'C', "candidate", gt864_forward_poly_ntt_friso2},
        {'N', "noop", gt864_forward_noop},
    };
    if (argc != 2 || strlen(argv[1]) != 3) {
        fprintf(stderr, "usage: %s BCN|NCB\n", argv[0]); return 2;
    }
    prepare();
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno)); return 2;
    }
    for (unsigned v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
        for (int i = 0; i < NWARMUP; ++i) variants[v].fn(output, inputs[i & 63]);
    printf("config,order=%s,samples=%d,calls=%d,warmups=%d\n",
           argv[1], NTESTS, NITERATIONS, NWARMUP);
    for (int sample = 0; sample < NTESTS; ++sample)
        for (int position = 0; position < 3; ++position) {
            const struct variant *selected = NULL;
            for (unsigned v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (!selected) return 2;
            const struct counts value = measure(selected);
            printf("sample,order=%s,index=%d,position=%d,variant=%s,cycles=%.6f,instructions=%.6f\n",
                   argv[1], sample, position, selected->name,
                   (double)value.cycles / NITERATIONS,
                   (double)value.instructions / NITERATIONS);
        }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(member_fd); close(leader_fd);
    return 0;
}
