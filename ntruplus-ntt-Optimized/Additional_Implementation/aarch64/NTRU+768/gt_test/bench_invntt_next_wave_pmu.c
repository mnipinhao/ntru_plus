#if !defined(__linux__)
#error "bench_invntt_next_wave_pmu requires Linux perf_event_open"
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
#ifndef INVNTT_ITERATIONS
#define INVNTT_ITERATIONS 20000
#endif
#ifndef BOUNDARY_ITERATIONS
#define BOUNDARY_ITERATIONS 50000
#endif

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_from_rminus1_baseline(poly *r, const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123_core(poly *r, const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123(poly *r, const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123_len16_core(poly *r,
                                                           const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123_len16(poly *r,
                                                      const poly *a);
void poly_invntt_rminus1_post_branchfold_slothy(poly *r, const poly *a);
void poly_invntt_rminus1_post_branchfold_slothy_core(poly *r, const poly *a);
void invntt_stage123_stage45_stripe0_baseline(int16_t *out, const poly *in,
                                               int16_t *scratch);
void invntt_stage123_stage45_stripe0_fused(int16_t *out, const poly *in,
                                            int16_t *scratch);
void invntt_stage45_post_stripe0_baseline(int16_t *out, const int16_t *row0,
                                           const int16_t *row1,
                                           const int16_t *stage123_scratch);
void invntt_stage45_post_stripe0_handoff(int16_t *out, const int16_t *row0,
                                          const int16_t *row1,
                                          const int16_t *stage123_scratch);

typedef void (*invntt_fn)(poly *, const poly *);
typedef void (*stage123_fn)(int16_t *, const poly *, int16_t *);
typedef void (*post_fn)(int16_t *, const int16_t *, const int16_t *,
                        const int16_t *);

struct count {
    uint64_t cycles;
    uint64_t instructions;
};

struct sample {
    double cycles;
    double instructions;
};

static int leader_fd = -1;
static int member_fd = -1;
static poly input_product, output_poly;
static int16_t scratch[256] __attribute__((aligned(64)));
static int16_t row0[8] __attribute__((aligned(64)));
static int16_t row1[8] __attribute__((aligned(64)));
static int16_t stage123[32] __attribute__((aligned(64)));
static int16_t output_coeffs[NTRUPLUS_N] __attribute__((aligned(64)));
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

static int init_pmu(void)
{
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    if (leader_fd < 0)
        return -1;
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    return member_fd < 0 ? -1 : 0;
}

static void begin_pmu(void)
{
    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
}

static struct count end_pmu(void)
{
    struct {
        uint64_t nr;
        uint64_t value[2];
    } data = {0, {0, 0}};
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof data) != (ssize_t)sizeof data ||
        data.nr != 2) {
        perror("perf group read");
        exit(2);
    }
    return (struct count){data.value[0], data.value[1]};
}

static struct count measure_invntt(invntt_fn fn)
{
    begin_pmu();
    for (int i = 0; i < INVNTT_ITERATIONS; i++)
        fn(&output_poly, &input_product);
    struct count out = end_pmu();
    sink ^= (uint16_t)output_poly.coeffs[0];
    return out;
}

static struct count measure_stage123(stage123_fn fn)
{
    begin_pmu();
    for (int i = 0; i < BOUNDARY_ITERATIONS; i++)
        fn(output_coeffs, &input_product, scratch);
    struct count out = end_pmu();
    sink ^= (uint16_t)output_coeffs[0];
    return out;
}

static struct count measure_post(post_fn fn)
{
    begin_pmu();
    for (int i = 0; i < BOUNDARY_ITERATIONS; i++)
        fn(output_coeffs, row0, row1, stage123);
    struct count out = end_pmu();
    sink ^= (uint16_t)output_coeffs[0];
    return out;
}

static int cmp_double(const void *a, const void *b)
{
    const double x = *(const double *)a;
    const double y = *(const double *)b;
    return (x > y) - (x < y);
}

static double median_metric(const struct sample samples[NTESTS], int cycles)
{
    double values[NTESTS];
    for (int i = 0; i < NTESTS; i++)
        values[i] = cycles ? samples[i].cycles : samples[i].instructions;
    qsort(values, NTESTS, sizeof values[0], cmp_double);
    return values[NTESTS / 2];
}

static void record(struct sample *dst, struct count value, int iterations)
{
    dst->cycles = (double)value.cycles / iterations;
    dst->instructions = (double)value.instructions / iterations;
}

static void report(const char *group, const char *variant,
                   const struct sample samples[NTESTS],
                   const struct sample baseline[NTESTS])
{
    double deltas[NTESTS];
    for (int i = 0; i < NTESTS; i++)
        deltas[i] = samples[i].cycles - baseline[i].cycles;
    qsort(deltas, NTESTS, sizeof deltas[0], cmp_double);
    const double cyc = median_metric(samples, 1);
    const double ins = median_metric(samples, 0);
    printf("pmu,group=%s,variant=%s,cycles=%.2f,instructions=%.2f,cpi=%.4f,"
           "paired_delta_cycles=%.2f\n",
           group, variant, cyc, ins, cyc / ins, deltas[NTESTS / 2]);
}

static uint32_t rng_state = 0x81f00d5au;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    return rng_state;
}

static void prepare(void)
{
    poly a, b, antt, bntt;
    for (int i = 0; i < NTRUPLUS_N; i++) {
        a.coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
        b.coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
    }
    poly_ntt(&antt, &a);
    poly_ntt(&bntt, &b);
    poly_basemul_rminus1(&input_product, &antt, &bntt);
    for (int i = 0; i < 8; i++) {
        row0[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
        row1[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
    }
    for (int i = 0; i < 32; i++)
        stage123[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
}

int main(void)
{
    const invntt_fn inv_fns[] = {
        poly_invntt_from_rminus1_baseline,
        poly_invntt_from_rminus1,
        poly_invntt_rminus1_lazy_twiddle1_stage123_core,
        poly_invntt_rminus1_lazy_twiddle1_stage123,
        poly_invntt_rminus1_lazy_twiddle1_stage123_len16_core,
        poly_invntt_rminus1_lazy_twiddle1_stage123_len16,
        poly_invntt_rminus1_post_branchfold_slothy_core,
        poly_invntt_rminus1_post_branchfold_slothy,
    };
    const stage123_fn s123_fns[] = {
        invntt_stage123_stage45_stripe0_baseline,
        invntt_stage123_stage45_stripe0_fused,
    };
    const post_fn post_fns[] = {
        invntt_stage45_post_stripe0_baseline,
        invntt_stage45_post_stripe0_handoff,
    };
    struct sample inv[8][NTESTS] = {{{0}}};
    struct sample s123[2][NTESTS] = {{{0}}};
    struct sample post[2][NTESTS] = {{{0}}};

    prepare();
    if (init_pmu() != 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return 2;
    }
    for (int i = 0; i < 200; i++) {
        inv_fns[i % 8](&output_poly, &input_product);
        s123_fns[i & 1](output_coeffs, &input_product, scratch);
        post_fns[i & 1](output_coeffs, row0, row1, stage123);
    }
    for (int sample = 0; sample < NTESTS; sample++) {
        for (int slot = 0; slot < 8; slot++) {
            const int variant = (slot + sample) % 8;
            record(&inv[variant][sample], measure_invntt(inv_fns[variant]),
                   INVNTT_ITERATIONS);
        }
        for (int slot = 0; slot < 2; slot++) {
            const int variant = (slot + sample) & 1;
            record(&s123[variant][sample], measure_stage123(s123_fns[variant]),
                   BOUNDARY_ITERATIONS);
            record(&post[variant][sample], measure_post(post_fns[variant]),
                   BOUNDARY_ITERATIONS);
        }
    }

    report("full_invntt", "baseline", inv[0], inv[0]);
    report("full_invntt", "promoted_production", inv[1], inv[0]);
    report("full_invntt", "lazy_core", inv[2], inv[0]);
    report("full_invntt", "lazy_abi_safe", inv[3], inv[0]);
    report("full_invntt", "lazy_len16_core", inv[4], inv[0]);
    report("full_invntt", "lazy_len16_abi_safe", inv[5], inv[0]);
    report("full_invntt", "post_branchfold_slothy_core", inv[6], inv[0]);
    report("full_invntt", "post_branchfold_slothy", inv[7], inv[0]);
    report("stage123_stage45_stripe0", "scratch", s123[0], s123[0]);
    report("stage123_stage45_stripe0", "register_handoff", s123[1], s123[0]);
    report("stage45_post_stripe0", "scratch", post[0], post[0]);
    report("stage45_post_stripe0", "register_handoff", post[1], post[0]);
    printf("sink=%" PRIu64 "\n", sink);
    close(member_fd);
    close(leader_fd);
    return 0;
}
