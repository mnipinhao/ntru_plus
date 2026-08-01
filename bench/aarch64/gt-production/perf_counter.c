#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#if !defined(__linux__)
#error "The release benchmark requires Linux perf_event_open."
#endif

#include "perf_counter.h"

#include <errno.h>
#include <linux/perf_event.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

static int counter_fd = -1;

static int perf_event_open(struct perf_event_attr *attr)
{
    return (int)syscall(__NR_perf_event_open, attr, 0, -1, -1, 0);
}

int perf_counter_open(void)
{
    struct perf_event_attr attr;

    memset(&attr, 0, sizeof(attr));
    attr.type = PERF_TYPE_HARDWARE;
    attr.size = sizeof(attr);
    attr.config = PERF_COUNT_HW_CPU_CYCLES;
    attr.disabled = 1;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;

    counter_fd = perf_event_open(&attr);
    if (counter_fd < 0) {
        fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
        return -1;
    }
    return 0;
}

void perf_counter_close(void)
{
    if (counter_fd >= 0)
        close(counter_fd);
    counter_fd = -1;
}

int perf_counter_start(void)
{
    if (ioctl(counter_fd, PERF_EVENT_IOC_RESET, 0) != 0 ||
        ioctl(counter_fd, PERF_EVENT_IOC_ENABLE, 0) != 0) {
        fprintf(stderr, "perf counter start failed: %s\n", strerror(errno));
        return -1;
    }
    return 0;
}

uint64_t perf_counter_stop(void)
{
    uint64_t value = 0;
    ssize_t count;

    if (ioctl(counter_fd, PERF_EVENT_IOC_DISABLE, 0) != 0) {
        fprintf(stderr, "perf counter stop failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
    count = read(counter_fd, &value, sizeof(value));
    if (count != (ssize_t)sizeof(value)) {
        fprintf(stderr, "perf counter read failed: %s\n", strerror(errno));
        exit(EXIT_FAILURE);
    }
    return value;
}
