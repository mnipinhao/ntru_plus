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
#include "gt864_fr0_to_official_map.h"

#define N 864
#define Q 3457
#define NINPUTS 64
#define NTESTS 61
#define NITERATIONS 20000
#define NWARMUP 100

typedef void (*kernel_fn)(int16_t *, const int16_t *);
struct counts { uint64_t cycles, instructions; };
struct variant { char code; const char *name; kernel_fn fn; };
extern void poly_ntt(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_all_one_mul_b3(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_friso2(int16_t *, const int16_t *);
extern void gt864_forward_poly_ntt_cf5b(int16_t *, const int16_t *);
extern void gt864_forward_noop(int16_t *, const int16_t *);

static int16_t inputs[NINPUTS][N] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink;
static int leader_fd = -1, member_fd = -1;
static uint32_t rng_state = 0xcf5b864u;

static uint32_t random_u32(void) {
    uint32_t x = rng_state; x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return rng_state = x;
}
static int centered(int value) {
    value %= Q; if (value < 0) value += Q; if (value > Q / 2) value -= Q;
    return value;
}
static int fr0_matches(const int16_t official[N], const int16_t fr0[N]) {
    for (int i = 0; i < N; ++i)
        if (centered(official[i]) != centered(fr0[gt864_fr0_for_official[i]])) return 0;
    return 1;
}
static int same_modq(const int16_t a[N], const int16_t b[N]) {
    for (int i = 0; i < N; ++i) if (centered(a[i]) != centered(b[i])) return 0;
    return 1;
}
static void prepare(void) {
    for (int k = 0; k < NINPUTS; ++k) {
        int16_t official[N], m5rd[N], cf0[N], cf5b[N], alias[N];
        for (int i = 0; i < N; ++i) inputs[k][i] = (int16_t)((int)(random_u32() % Q) - 1728);
        poly_ntt(official, inputs[k]);
        gt864_forward_poly_ntt_all_one_mul_b3(m5rd, inputs[k]);
        gt864_forward_poly_ntt_friso2(cf0, inputs[k]);
        gt864_forward_poly_ntt_cf5b(cf5b, inputs[k]);
        if (!fr0_matches(official, m5rd) || !same_modq(cf0, cf5b)) {
            fprintf(stderr, "differential failed at input %d\n", k); exit(1);
        }
        memcpy(alias, inputs[k], sizeof(alias));
        gt864_forward_poly_ntt_cf5b(alias, alias);
        if (!same_modq(cf0, alias)) { fprintf(stderr, "alias failed at input %d\n", k); exit(1); }
    }
    puts("correctness,status=pass,m5rd_nonalias=64,cf0_nonalias=64,cf5b_nonalias=64,cf5b_alias=64");
}
static int perf_open(uint64_t config, int group_fd) {
    struct perf_event_attr pe; memset(&pe, 0, sizeof(pe));
    pe.type = PERF_TYPE_HARDWARE; pe.size = sizeof(pe); pe.config = config;
    pe.disabled = group_fd == -1; pe.exclude_kernel = 1; pe.exclude_hv = 1;
    pe.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &pe, 0, -1, group_fd, 0);
}
static struct counts measure(const struct variant *variant) {
    struct { uint64_t nr, value[2]; } data = {0, {0, 0}};
    ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < NITERATIONS; ++i) variant->fn(output, inputs[i & 63]);
    ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader_fd, &data, sizeof(data)) != (ssize_t)sizeof(data) || data.nr != 2) {
        perror("perf read"); exit(2);
    }
    sink += (uint16_t)output[(unsigned)variant->code % N];
    return (struct counts){data.value[0], data.value[1]};
}
int main(int argc, char **argv) {
    const struct variant variants[] = {
        {'O', "official", poly_ntt},
        {'D', "m5rd", gt864_forward_poly_ntt_all_one_mul_b3},
        {'F', "cf0", gt864_forward_poly_ntt_friso2},
        {'C', "cf5b", gt864_forward_poly_ntt_cf5b},
        {'N', "noop", gt864_forward_noop},
    };
    if (argc != 2 || strlen(argv[1]) != 5) { fprintf(stderr, "usage: %s ODFCN|NCFDO\n", argv[0]); return 2; }
    prepare();
    leader_fd = perf_open(PERF_COUNT_HW_CPU_CYCLES, -1);
    member_fd = perf_open(PERF_COUNT_HW_INSTRUCTIONS, leader_fd);
    if (leader_fd < 0 || member_fd < 0) { fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno)); return 2; }
    for (unsigned v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
        for (int i = 0; i < NWARMUP; ++i) variants[v].fn(output, inputs[i & 63]);
    printf("config,order=%s,samples=%d,calls=%d,warmups=%d\n", argv[1], NTESTS, NITERATIONS, NWARMUP);
    for (int sample = 0; sample < NTESTS; ++sample) {
        for (int position = 0; position < 5; ++position) {
            const struct variant *selected = NULL;
            for (unsigned v = 0; v < sizeof(variants) / sizeof(variants[0]); ++v)
                if (variants[v].code == argv[1][position]) selected = &variants[v];
            if (!selected) return 2;
            const struct counts value = measure(selected);
            printf("sample,order=%s,index=%d,position=%d,variant=%s,cycles=%.6f,instructions=%.6f\n",
                   argv[1], sample, position, selected->name,
                   (double)value.cycles / NITERATIONS, (double)value.instructions / NITERATIONS);
        }
    }
    printf("meta,sink=%" PRIu64 "\n", sink);
    close(member_fd); close(leader_fd); return 0;
}
