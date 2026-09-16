#define _GNU_SOURCE
#include "fused_tobytes.h"
#include "p3b5_tables.h"

#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

void p3b5_baseline_r9_to(uint8_t out[1296], const int16_t fr0[864]);

typedef void (*to_fn)(uint8_t *, const int16_t *);

static to_fn functions[2] = {
    p3b5_baseline_r9_to,
    gt864_fr0_fused_tobytes,
};
static const char *names[2] = {"r9", "fused"};
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

static int16_t canonical(int16_t value)
{
    int32_t result = value % 3457;
    return (int16_t)(result < 0 ? result + 3457 : result);
}

static void oracle(uint8_t out[1296], const int16_t fr0[864])
{
    for (int pair = 0; pair < 432; pair++) {
        uint16_t a = (uint16_t)canonical(fr0[p3b5_map[2 * pair]]);
        uint16_t b = (uint16_t)canonical(fr0[p3b5_map[2 * pair + 1]]);
        out[3 * pair] = (uint8_t)a;
        out[3 * pair + 1] = (uint8_t)((a >> 8) | (b << 4));
        out[3 * pair + 2] = (uint8_t)(b >> 4);
    }
}

static void check(void)
{
    int baseline_mismatch = 0;
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
        oracle(expected, input);
        for (int variant = 0; variant < 2; variant++) {
            memset(actual, 0xa5, sizeof actual);
            functions[variant](actual, input);
            if (memcmp(expected, actual, sizeof actual) != 0) {
                if (variant == 1 || !baseline_mismatch) {
                    fprintf(stderr, "correctness fail test=%d variant=%s\n",
                            test, names[variant]);
                    for (int byte = 0; byte < 1296; byte++) {
                        if (expected[byte] != actual[byte]) {
                            fprintf(stderr,
                                    "first mismatch byte=%d expected=%u actual=%u\n",
                                    byte, expected[byte], actual[byte]);
                            break;
                        }
                    }
                }
                if (variant == 1)
                    exit(1);
                baseline_mismatch = 1;
            }
        }
    }
    if (baseline_mismatch) {
        puts("p3b5_fused_correctness=pass baseline_oracle=fail");
        exit(1);
    }
    puts("p3b5_pi_correctness=pass cases=128 bytes=1296");
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
            struct {
                uint64_t count;
                uint64_t value[3];
            } result;
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
                   result.value[0] / 400.0,
                   result.value[1] / 400.0,
                   result.value[2] / 400.0);
        }
    }
    return 0;
}
