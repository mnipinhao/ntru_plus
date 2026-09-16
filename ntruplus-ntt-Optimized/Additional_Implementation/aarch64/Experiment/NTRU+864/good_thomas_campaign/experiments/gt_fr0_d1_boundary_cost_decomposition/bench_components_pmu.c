#if !defined(__linux__)
#error "D1-P2 PMU requires Linux"
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "gt864_poly_api.h"
#include "p2_components.h"

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

#define NSAMPLES 41
#define NVARIANTS 3
#define NOPS 11

struct operation { const char *name; int iterations; int comparative; };
struct counts { uint64_t cycles, instructions, branches; };

static poly natural, official_ntt, fr0_ntt, official_product, fr0_product;
static poly output_poly;
static uint8_t packed[NTRUPLUS_POLYBYTES], output_bytes[NTRUPLUS_POLYBYTES];
static volatile uint64_t sink;
static int leader = -1, instructions_fd = -1, branches_fd = -1;

static int perf_open(uint64_t config, int group)
{
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof pe);
    pe.type = PERF_TYPE_HARDWARE; pe.size = sizeof pe; pe.config = config;
    pe.disabled = group == -1; pe.exclude_kernel = 1; pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group, 0);
}

__attribute__((noinline))
static void run_operation(int op, int candidate)
{
    switch (op) {
    case 0:
        if (candidate) gt_p2_official_to_fr0(&output_poly, &official_ntt);
        break;
    case 1:
        if (candidate) gt_p2_fr0_to_official_raw(&output_poly, &fr0_ntt);
        break;
    case 2:
        if (candidate) gt_p2_normalize_nonnegative(&output_poly, &fr0_ntt);
        break;
    case 3:
        if (candidate) gt_p2_normalize_centered(&output_poly, &fr0_ntt);
        break;
    case 4:
        if (candidate) gt_p2_fr0_to_official_nonnegative(&output_poly, &fr0_ntt);
        break;
    case 5:
        if (candidate) gt_old_poly_ntt(&output_poly, &natural);
        else poly_ntt(&output_poly, &natural);
        break;
    case 6:
        if (candidate) gt_p2_inverse_raw(&output_poly, &fr0_product);
        else poly_invntt(&output_poly, &official_product);
        break;
    case 7:
        if (candidate) gt_old_poly_invntt(&output_poly, &fr0_product);
        else poly_invntt(&output_poly, &official_product);
        break;
    case 8:
        if (candidate) gt_old_poly_tobytes(output_bytes, &fr0_ntt);
        else poly_tobytes(output_bytes, &official_ntt);
        break;
    case 9:
        if (candidate) gt_old_poly_frombytes(&output_poly, packed);
        else poly_frombytes(&output_poly, packed);
        break;
    case 10:
        if (candidate) (void)gt_old_poly_baseinv(&output_poly, &fr0_ntt);
        else (void)poly_baseinv(&output_poly, &official_ntt);
        break;
    default: exit(3);
    }
}

static struct counts measure(int op, char variant, int iterations)
{
    struct { uint64_t nr, value[3]; } data = {0, {0, 0, 0}};
    int candidate = variant == 'C';
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < iterations; i++) {
        if (variant == 'N')
            __asm__ volatile("" : : "r"(&output_poly) : "memory");
        else
            run_operation(op, candidate);
    }
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &data, sizeof data) != (ssize_t)sizeof data || data.nr != 3)
        exit(2);
    sink += (uint16_t)output_poly.coeffs[(op * 79) % NTRUPLUS_N];
    sink += output_bytes[op % NTRUPLUS_POLYBYTES];
    return (struct counts){data.value[0], data.value[1], data.value[2]};
}

int main(int argc, char **argv)
{
    const struct operation operations[NOPS] = {
        {"perm_o2f", 1000, 0}, {"perm_f2o", 1000, 0},
        {"norm_nonnegative", 1000, 0}, {"norm_centered", 1000, 0},
        {"fused_f2o_nonnegative", 1000, 0}, {"forward", 200, 1},
        {"inverse_raw", 100, 1}, {"inverse_api", 100, 1},
        {"tobytes", 500, 1}, {"frombytes", 500, 1},
        {"baseinv", 40, 1},
    };
    if (argc != 2 || strlen(argv[1]) != NVARIANTS) return 2;
    memset(&natural, 0, sizeof natural);
    natural.coeffs[0] = 1;
    poly_ntt(&official_ntt, &natural);
    gt_old_poly_ntt(&fr0_ntt, &natural);
    poly_basemul(&official_product, &official_ntt, &official_ntt);
    gt_d1_poly_basemul(&fr0_product, &fr0_ntt, &fr0_ntt);
    poly_tobytes(packed, &official_ntt);
    puts("correctness,status=prepared,D1-P2_boundaries=11");

    leader = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    instructions_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader);
    branches_fd = perf_open(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions_fd < 0 || branches_fd < 0) return 2;
    for (int op = 0; op < NOPS; op++)
        for (int sample = 0; sample < NSAMPLES; sample++)
            for (int position = 0; position < NVARIANTS; position++) {
                char code = argv[1][position];
                const char *name = code == 'B' ? "baseline" :
                                   code == 'C' ? "candidate" : "noop";
                struct counts value = measure(op, code, operations[op].iterations);
                printf("sample,operation=%s,index=%d,position=%d,variant=%s,"
                       "comparative=%d,cycles=%.6f,instructions=%.6f,branches=%.6f\n",
                       operations[op].name, sample, position, name,
                       operations[op].comparative,
                       (double)value.cycles / operations[op].iterations,
                       (double)value.instructions / operations[op].iterations,
                       (double)value.branches / operations[op].iterations);
            }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(branches_fd); close(instructions_fd); close(leader);
    return 0;
}
