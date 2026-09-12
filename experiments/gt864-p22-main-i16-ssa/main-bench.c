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
#include "gt864_p13b_composite_tables.h"

enum { N = 864, SCRATCH_H = 896 };
typedef void (*i16fn)(int16_t *, const int16_t *, const int16_t *,
                      const int16_t *, const int16_t *);
struct counts { uint64_t n, v[3]; };

static _Alignas(16) int16_t scratch[SCRATCH_H];
static _Alignas(16) int16_t output[2][N];
static volatile uint32_t sink;
static int leader = -1;

void randombytes(uint8_t *out, size_t length) {
    while (length--) *out++ = 0;
}

static void *must_symbol(void *handle, const char *name) {
    void *symbol = dlsym(handle, name);
    if (!symbol) { fprintf(stderr, "dlsym %s: %s\n", name, dlerror()); exit(2); }
    return symbol;
}

static int event(uint64_t config, int group) {
    struct perf_event_attr attr = {0};
    attr.size = sizeof attr;
    attr.type = PERF_TYPE_HARDWARE;
    attr.config = config;
    attr.exclude_kernel = attr.exclude_hv = 1;
    attr.disabled = group < 0;
    attr.read_format = PERF_FORMAT_GROUP;
    return syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
}

static void run_main(i16fn fn, int slot) {
    for (int component = 0; component < 3; component++)
        for (int half = 0; half < 2; half++)
            fn(output[slot] + component + half * 12,
               scratch + component * 256 + half * 128, 0,
               &gt864_inverse16_stage_barrett[0][0],
               &gt864_p13b_main[0][0]);
}

static struct counts measure(i16fn fn, int slot, int repetitions) {
    struct counts before, after, result = {.n = 3};
    if (read(leader, &before, sizeof before) != sizeof before || before.n != 3)
        exit(3);
    for (int i = 0; i < repetitions; i++) {
        run_main(fn, slot);
        sink += (uint16_t)output[slot][(i * 313) % N];
    }
    if (read(leader, &after, sizeof after) != sizeof after || after.n != 3)
        exit(3);
    for (int i = 0; i < 3; i++) result.v[i] = after.v[i] - before.v[i];
    return result;
}

int main(int argc, char **argv) {
    if (argc != 4) return 2;
    void *handles[2] = {
        dlopen(argv[1], RTLD_NOW | RTLD_LOCAL),
        dlopen(argv[2], RTLD_NOW | RTLD_LOCAL)
    };
    if (!handles[0] || !handles[1]) { fputs(dlerror(), stderr); return 2; }
    i16fn functions[2] = {
        (i16fn)must_symbol(handles[0], "lazy_i16"),
        (i16fn)must_symbol(handles[1], "lazy_i16")
    };
    int reverse = atoi(argv[3]);
    for (int i = 0; i < SCRATCH_H; i++)
        scratch[i] = (int16_t)((i * 1877 + 911) % 5235 - 2617);
    memset(output, 0, sizeof output);
    run_main(functions[0], 0);
    run_main(functions[1], 1);
    if (memcmp(output[0], output[1], sizeof output[0])) {
        fputs("main-I16 output mismatch\n", stderr); return 4;
    }

    leader = event(PERF_COUNT_HW_CPU_CYCLES, -1);
    int instructions = event(PERF_COUNT_HW_INSTRUCTIONS, leader);
    int branches = event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, leader);
    if (leader < 0 || instructions < 0 || branches < 0) return 3;
    if (ioctl(leader, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP) < 0) {
        perror("PERF_EVENT_IOC_ENABLE");
        return 3;
    }

    for (int sample = -10; sample < 61; sample++) {
        for (int position = 0; position < 2; position++) {
            int candidate = position ^ reverse;
            struct counts count = measure(functions[candidate], candidate, 64);
            if (sample >= 0)
                printf("main_i16_x6,%s,%.3f,%.3f,%.3f\n",
                    candidate ? "candidate" : "baseline",
                    (double)count.v[0] / 64,
                    (double)count.v[1] / 64,
                    (double)count.v[2] / 64);
        }
    }
    return sink == 0xdeadbeefU;
}
