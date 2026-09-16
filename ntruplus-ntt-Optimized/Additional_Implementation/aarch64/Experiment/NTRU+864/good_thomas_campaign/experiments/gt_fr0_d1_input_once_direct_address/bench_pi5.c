#define _GNU_SOURCE
#include "direct_address_tobytes.h"

#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

void gt864_fr0_input_once_tobytes(uint8_t out[1296],
                                  const int16_t fr0[864]);

typedef void (*to_fn)(uint8_t *, const int16_t *);
static to_fn functions[2] = {
    gt864_fr0_input_once_tobytes,
    gt864_fr0_input_once_direct_address_tobytes,
};
static const char *names[2] = {"p3b6", "direct_address"};
static int16_t input[864] __attribute__((aligned(16)));
static uint8_t expected[1296] __attribute__((aligned(16)));
static uint8_t actual[1296] __attribute__((aligned(16)));
static volatile uint64_t sink;
static uint32_t rng = 1;

static uint32_t next_u32(void)
{
    rng = rng * 1664525u + 1013904223u;
    return rng;
}

static void check(void)
{
    for (int test = 0; test < 128; test++) {
        for (int index = 0; index < 864; index++) {
            if (test == 0)
                input[index] = (int16_t)index;
            else if (test == 1)
                input[index] = INT16_MIN;
            else if (test == 2)
                input[index] = INT16_MAX;
            else
                input[index] = (int16_t)next_u32();
        }
        functions[0](expected, input);
        functions[1](actual, input);
        if (memcmp(expected, actual, sizeof actual) != 0) {
            fprintf(stderr, "p3b8 correctness fail test=%d\n", test);
            exit(1);
        }
    }
    puts("p3b8_pi_correctness=pass cases=128 bytes=1296");
}

static int open_counter(uint64_t config, int group)
{
    struct perf_event_attr event = {0};
    event.size = sizeof event;
    event.type = PERF_TYPE_HARDWARE;
    event.config = config;
    event.disabled = group < 0;
    event.exclude_kernel = 1;
    event.exclude_hv = 1;
    event.read_format = PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open, &event, 0, -1, group, 0);
}

int main(int argc, char **argv)
{
    check();
    if (argc == 1)
        return 0;
    int reverse = atoi(argv[1]);
    int cycles = open_counter(PERF_COUNT_HW_CPU_CYCLES, -1);
    int instructions = open_counter(PERF_COUNT_HW_INSTRUCTIONS, cycles);
    int branches = open_counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, cycles);
    if (cycles < 0 || instructions < 0 || branches < 0) {
        perror("perf_event_open");
        return 2;
    }
    for (int index = 0; index < 864; index++)
        input[index] = (int16_t)next_u32();
    for (int repetition = 0; repetition < 41; repetition++) {
        for (int position = 0; position < 2; position++) {
            int variant = reverse ? 1 - position : position;
            struct { uint64_t count, value[3]; } result;
            ioctl(cycles, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
            ioctl(cycles, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
            for (int iteration = 0; iteration < 400; iteration++)
                functions[variant](actual, input);
            ioctl(cycles, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
            if (read(cycles, &result, sizeof result) != (ssize_t)sizeof result ||
                result.count != 3)
                return 2;
            sink += actual[repetition % 1296];
            printf("sample,to_%s,%.3f,%.3f,%.3f\n", names[variant],
                   result.value[0] / 400.0, result.value[1] / 400.0,
                   result.value[2] / 400.0);
        }
    }
    return 0;
}
