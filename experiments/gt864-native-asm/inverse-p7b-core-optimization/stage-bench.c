#define _GNU_SOURCE
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "gt864_native_scaled_tables.h"

enum { N = 864, SCRATCH_H = 896, EVENTS = 5 };
typedef struct { int16_t coeffs[N]; } poly;
typedef void (*i9fn)(int16_t *, int16_t *, const int16_t *, const int16_t *);
typedef void (*i16fn)(int16_t *, const int16_t *, const int16_t *,
                      const int16_t *, const int16_t *);
typedef void (*centerfn)(int16_t *);
typedef void (*inversefn)(poly *, const poly *);
struct counts { uint64_t n, v[EVENTS]; };

static i9fn packed_i9_fn;
static i16fn lazy_i16_fn, lazy_itail_fn, nostore_i16_fn, nostore_itail_fn;
static centerfn center864_fn;
static inversefn inverse_fn;
static _Alignas(16) int16_t input[N], scratch[SCRATCH_H], output[N];
static volatile uint32_t sink;
static uint64_t rng_state = 0x864700b0ULL;
static int leader = -1;

void randombytes(uint8_t *out, size_t length) {
    while (length--) {
        rng_state ^= rng_state << 13;
        rng_state ^= rng_state >> 7;
        rng_state ^= rng_state << 17;
        *out++ = (uint8_t)rng_state;
    }
}

static void *must_open(const char *path) {
    void *handle = dlopen(path, RTLD_NOW | RTLD_LOCAL);
    if (!handle) { fprintf(stderr, "dlopen %s: %s\n", path, dlerror()); exit(2); }
    return handle;
}

static void *must_symbol(void *handle, const char *name) {
    void *symbol = dlsym(handle, name);
    if (!symbol) { fprintf(stderr, "dlsym %s: %s\n", name, dlerror()); exit(2); }
    return symbol;
}

static int read_pmu_type(void) {
    FILE *file = fopen("/sys/bus/event_source/devices/armv8_cortex_a76/type", "r");
    int type = -1;
    if (!file || fscanf(file, "%d", &type) != 1) { perror("PMU type"); exit(3); }
    fclose(file);
    return type;
}

static int open_event(uint32_t type, uint64_t config, int group) {
    struct perf_event_attr attr = {0};
    attr.size = sizeof attr;
    attr.type = type;
    attr.config = config;
    attr.exclude_kernel = attr.exclude_hv = 1;
    attr.disabled = group < 0;
    attr.read_format = PERF_FORMAT_GROUP;
    int fd = syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
    if (fd < 0) { perror("perf_event_open"); exit(3); }
    return fd;
}

static void setup_perf(void) {
    leader = open_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1);
    (void)open_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, leader);
    (void)open_event(PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    int type = read_pmu_type();
    (void)open_event((uint32_t)type, 0x66, leader);
    (void)open_event((uint32_t)type, 0x67, leader);
}

static void run_i9(void) {
    for (int top = 0; top < 2; top++) for (int component = 0; component < 3; component++)
        for (int block = 0; block < 2; block++)
            packed_i9_fn(scratch + component * 256 + block * 64 + top * 4,
                scratch + 768 + block * 64 + top * 3 + component,
                input + top * 432 + block * 24 + component * 8,
                &gt864_inverse9_twist_barrett[top][block][0][0][0]);
}

static void run_main(i16fn fn) {
    for (int component = 0; component < 3; component++) for (int half = 0; half < 2; half++)
        fn(output + component + half * 12,
           scratch + component * 256 + half * 128, 0,
           &gt864_inverse16_stage_barrett[0][0],
           &gt864_inverse16_main_scale_barrett[0][0][0]);
}

static void run_tail(i16fn fn) {
    fn(output + 24, scratch + 768, 0,
       &gt864_inverse16_stage_barrett[0][0],
       &gt864_inverse16_tail_scale_barrett[0][0][0]);
}

static void operation(int which) {
    switch (which) {
    case 0: break;
    case 1: run_i9(); break;
    case 2: run_main(lazy_i16_fn); break;
    case 3: run_tail(lazy_itail_fn); break;
    case 4: run_main(nostore_i16_fn); break;
    case 5: run_tail(nostore_itail_fn); break;
    case 6: center864_fn(output); break;
    case 7: inverse_fn((poly *)output, (const poly *)input); break;
    default: abort();
    }
}

static struct counts measure(int which, int iterations) {
    struct counts result;
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
    ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int i = 0; i < iterations; i++) {
        operation(which);
        sink += (uint16_t)output[(i * 313) % N];
    }
    ioctl(leader, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
    if (read(leader, &result, sizeof result) != sizeof result || result.n != EVENTS) {
        fputs("incomplete PMU group\n", stderr); exit(3);
    }
    return result;
}

int main(int argc, char **argv) {
    if (argc != 4) return 2;
    void *production = must_open(argv[1]);
    void *diagnostic = must_open(argv[2]);
    int reverse = atoi(argv[3]);
    packed_i9_fn = (i9fn)must_symbol(production, "packed_i9");
    lazy_i16_fn = (i16fn)must_symbol(production, "lazy_i16");
    lazy_itail_fn = (i16fn)must_symbol(production, "lazy_itail");
    center864_fn = (centerfn)must_symbol(production, "center864");
    inverse_fn = (inversefn)must_symbol(production, "gt864_native_inverse");
    nostore_i16_fn = (i16fn)must_symbol(diagnostic, "p7b0_lazy_i16_nostore");
    nostore_itail_fn = (i16fn)must_symbol(diagnostic, "p7b0_lazy_itail_nostore");

    for (int i = 0; i < N; i++) input[i] = (int16_t)((i * 1877 + 911) % 4995 - 2497);
    memset(scratch, 0, sizeof scratch); memset(output, 0, sizeof output);
    run_i9(); run_main(lazy_i16_fn); run_tail(lazy_itail_fn);
    for (int i = 0; i < 64; i++) operation(7);
    setup_perf();

    static const char *names[] = {"empty", "inverse9_x12", "main_i16_x6", "tail_i16",
                                  "main_i16_nostore_x6", "tail_i16_nostore",
                                  "center864", "complete_inverse"};
    const int iterations = 64;
    for (int sample = 0; sample < 43; sample++) {
        for (int position = 0; position < 8; position++) {
            int which = reverse ? 7 - position : position;
            if (sample & 1) which = 7 - which;
            struct counts c = measure(which, iterations);
            printf("sample,%s,%d,%.3f,%.3f,%.3f,%.3f,%.3f\n", names[which], sample,
                   (double)c.v[0] / iterations, (double)c.v[1] / iterations,
                   (double)c.v[2] / iterations, (double)c.v[3] / iterations,
                   (double)c.v[4] / iterations);
        }
    }
    return sink == 0xdeadbeefU;
}
