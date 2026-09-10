#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

struct counts { uint64_t n, v[2]; };
void p6_empty_bridge(uint64_t);
void p6_memory_bridge(uint8_t *, uint64_t);
void p6_gpr_bridge(uint64_t);
static uint8_t scratch[432] __attribute__((aligned(64)));
static int fd;

static int event(uint64_t config, int group)
{
    struct perf_event_attr attr = {0};
    attr.size = sizeof attr; attr.type = PERF_TYPE_HARDWARE; attr.config = config;
    attr.exclude_kernel = attr.exclude_hv = 1; attr.disabled = group < 0;
    attr.read_format = PERF_FORMAT_GROUP;
    return syscall(__NR_perf_event_open, &attr, 0, -1, group, 0);
}

static struct counts tick(void)
{
    struct counts value;
    if (read(fd, &value, sizeof value) != sizeof value || value.n != 2) exit(2);
    return value;
}

int main(void)
{
    const uint64_t repetitions = 4096;
    fd = event(PERF_COUNT_HW_CPU_CYCLES, -1);
    int fi = event(PERF_COUNT_HW_INSTRUCTIONS, fd);
    if (fd < 0 || fi < 0) return 2;
    ioctl(fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
    for (int warm = 0; warm < 10; ++warm) {
        p6_memory_bridge(scratch, repetitions);
        p6_gpr_bridge(repetitions);
    }
    for (int sample = 0; sample < 101; ++sample) {
        struct counts a = tick(); p6_empty_bridge(repetitions); struct counts b = tick();
        p6_memory_bridge(scratch, repetitions); struct counts c = tick();
        p6_gpr_bridge(repetitions); struct counts d = tick();
        double empty_c = (double)(b.v[0] - a.v[0]) / repetitions;
        double empty_i = (double)(b.v[1] - a.v[1]) / repetitions;
        printf("%d,%.6f,%.6f,%.6f,%.6f\n", sample,
               (double)(c.v[0] - b.v[0]) / repetitions - empty_c,
               (double)(d.v[0] - c.v[0]) / repetitions - empty_c,
               (double)(c.v[1] - b.v[1]) / repetitions - empty_i,
               (double)(d.v[1] - c.v[1]) / repetitions - empty_i);
    }
    return 0;
}
