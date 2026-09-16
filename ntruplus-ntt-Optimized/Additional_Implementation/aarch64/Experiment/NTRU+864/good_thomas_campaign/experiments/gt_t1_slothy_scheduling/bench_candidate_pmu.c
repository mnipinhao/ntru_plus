#if !defined(__linux__)
#error "A1 full-boundary PMU benchmark requires Linux"
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
#define P8N 896
#define Q 3457
#define NINPUTS 64
#define NVARIANTS 7
#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 10000
#endif

typedef void (*kernel_fn)(int16_t *, const int16_t *);
struct variant { char code; const char *name; kernel_fn fn; const int16_t *input; size_t stride; };
struct counts { uint64_t cycles, instructions, branches; };

extern void gt864_top_split_ld3(int16_t *, const int16_t *);
extern void gt864_tail_layout_bank_major_inplace(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t1(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t1(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_a1_t1(int16_t *, const int16_t *);
extern void gt864_one_bank_a1_t1_slothy(int16_t *, const int16_t *);
extern void gt864_forward_six_bank_pass2_a1_t1_slothy(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_a1_t1_slothy(int16_t *, const int16_t *);

static int16_t natural[NINPUTS][N] __attribute__((aligned(64)));
static int16_t p8_t1[NINPUTS][P8N] __attribute__((aligned(64)));
static int16_t output[P8N] __attribute__((aligned(64)));
static uint32_t rng = 0xa1f011U;
static volatile uint64_t sink;
static int leader = -1, instructions_fd = -1, branches_fd = -1;

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

static int equal_modq(const int16_t *a, const int16_t *b, int count)
{
    for (int i = 0; i < count; ++i)
        if (centered(a[i]) != centered(b[i])) return 0;
    return 1;
}

static void prepare(void)
{
    int16_t reference[P8N], candidate[P8N];
    for (int k = 0; k < NINPUTS; ++k) {
        for (int i = 0; i < N; ++i)
            natural[k][i] = (int16_t)((int)(random_u32() % Q) - 1728);
        gt864_top_split_ld3(p8_t1[k], natural[k]);
        gt864_tail_layout_bank_major_inplace(p8_t1[k] + 768, p8_t1[k] + 768);
        gt864_one_bank_a1_t1(reference, p8_t1[k]);
        gt864_one_bank_a1_t1_slothy(candidate, p8_t1[k]);
        if (!equal_modq(reference, candidate, 144)) exit(1);
        gt864_forward_six_bank_pass2_a1_t1(reference, p8_t1[k]);
        gt864_forward_six_bank_pass2_a1_t1_slothy(candidate, p8_t1[k]);
        if (!equal_modq(reference, candidate, N)) exit(1);
        gt864_forward_poly_ntt_a1_t1(reference, natural[k]);
        gt864_forward_poly_ntt_a1_t1_slothy(candidate, natural[k]);
        if (!equal_modq(reference, candidate, N)) exit(1);
    }
    puts("correctness,status=pass,one_bank=64,six_bank=64,full=64,slothy=64");
}

static int perf_open(uint64_t config, int group)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(pe)); pe.type = PERF_TYPE_HARDWARE; pe.size = sizeof(pe);
    pe.config = config; pe.disabled = group == -1; pe.exclude_kernel = 1;
    pe.exclude_hv = 1; pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group, 0);
}

static struct counts measure(const struct variant *variant)
{
    struct { uint64_t nr, value[3]; } data = {0, {0, 0, 0}};
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < NITERATIONS; ++i)
        variant->fn(output, variant->input + (size_t)(i & 63) * variant->stride);
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &data, sizeof(data)) != (ssize_t)sizeof(data) || data.nr != 3) exit(2);
    sink += (uint16_t)output[(unsigned)variant->code % N];
    return (struct counts){data.value[0], data.value[1], data.value[2]};
}

int main(int argc, char **argv)
{
    const struct variant variants[] = {
        {'a', "one_T1", gt864_one_bank_a1_t1, &p8_t1[0][0], P8N},
        {'b', "one_T1S", gt864_one_bank_a1_t1_slothy, &p8_t1[0][0], P8N},
        {'c', "six_T1", gt864_forward_six_bank_pass2_a1_t1, &p8_t1[0][0], P8N},
        {'d', "six_T1S", gt864_forward_six_bank_pass2_a1_t1_slothy, &p8_t1[0][0], P8N},
        {'e', "full_T1", gt864_forward_poly_ntt_a1_t1, &natural[0][0], N},
        {'f', "full_T1S", gt864_forward_poly_ntt_a1_t1_slothy, &natural[0][0], N},
        {'N', "noop", noop, &natural[0][0], N},
    };
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;
    prepare();
    leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    instructions_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader);
    branches_fd = perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions_fd < 0 || branches_fd < 0) return 2;
    for (int v = 0; v < NVARIANTS; ++v)
        for (int i = 0; i < 100; ++i) variants[v].fn(output, variants[v].input);
    for (int sample = 0; sample < NTESTS; ++sample)
        for (int position = 0; position < NVARIANTS; ++position) {
            const struct variant *selected = NULL;
            for (int v = 0; v < NVARIANTS; ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (!selected) return 2;
            struct counts c = measure(selected);
            printf("sample,index=%d,position=%d,variant=%s,cycles=%.6f,instructions=%.6f,branches=%.6f\n",
                   sample, position, selected->name, (double)c.cycles / NITERATIONS,
                   (double)c.instructions / NITERATIONS, (double)c.branches / NITERATIONS);
        }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(branches_fd); close(instructions_fd); close(leader);
    return 0;
}
