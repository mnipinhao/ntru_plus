#define _GNU_SOURCE
#include <errno.h>
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <x86intrin.h>

#include "generated/plane_n16_probe.h"

#define WORDS 128
#define VARIANTS 5
#define SAMPLES 20

typedef void (*kernel)(int16_t *, const int16_t *);

static const char *const names[VARIANTS] = {
  "folded", "reuse_one", "reuse_pair", "progressive", "pair"
};
static kernel const kernels[VARIANTS] = {
  gt32_plane_n16_folded_asm,
  gt32_plane_n16_reuse_one_asm,
  gt32_plane_n16_reuse_pair_asm,
  gt32_plane_n16_progressive_control_asm,
  gt32_plane_n16_pair_control_asm,
};
static _Alignas(64) int16_t input[WORDS];
static _Alignas(64) int16_t output[WORDS];
static volatile uint64_t sink;

static uint64_t start_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t stop_tsc(void) {
  unsigned auxiliary;
  uint64_t result = __rdtscp(&auxiliary);
  _mm_lfence();
  return result;
}

static double measure_tsc(kernel fn, unsigned iterations) {
  uint64_t begin = start_tsc();
  for (unsigned i = 0; i < iterations; ++i) fn(output, input);
  uint64_t end = stop_tsc();
  sink += (uint16_t)output[iterations & (WORDS - 1)];
  return (double)(end - begin) / iterations;
}

struct pmu_spec { const char *name; uint32_t type; uint64_t config; };

static int perf_open(const struct pmu_spec *spec, int group_fd, int disabled) {
  struct perf_event_attr attr;
  memset(&attr, 0, sizeof attr);
  attr.size = sizeof attr;
  attr.type = spec->type;
  attr.config = spec->config;
  attr.disabled = disabled;
  attr.exclude_kernel = 1;
  attr.exclude_hv = 1;
  attr.read_format = PERF_FORMAT_GROUP;
  return (int)syscall(SYS_perf_event_open, &attr, 0, -1, group_fd, 0UL);
}

static int measure_pmu(kernel fn, unsigned iterations, const char *label,
                       const struct pmu_spec *specs, unsigned count) {
  int fds[4];
  for (unsigned i = 0; i < count; ++i) {
    fds[i] = perf_open(&specs[i], i ? fds[0] : -1, i == 0);
    if (fds[i] < 0) {
      if (i == 0) fprintf(stderr, "PMU unavailable: %s\n", strerror(errno));
      while (i) close(fds[--i]);
      return 0;
    }
  }
  uint64_t values[5] = {0};
  (void)ioctl(fds[0], PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  (void)ioctl(fds[0], PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (unsigned i = 0; i < iterations; ++i) fn(output, input);
  (void)ioctl(fds[0], PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
  ssize_t got = read(fds[0], values, sizeof(uint64_t) * (count + 1));
  for (unsigned i = 0; i < count; ++i) close(fds[i]);
  if (got != (ssize_t)(sizeof(uint64_t) * (count + 1)) || values[0] != count)
    return 0;
  printf("PMU,%s", label);
  for (unsigned i = 0; i < count; ++i)
    printf(",%s,%.6f", specs[i].name, (double)values[i + 1] / iterations);
  putchar('\n');
  sink += (uint16_t)output[0];
  return 1;
}

int main(int argc, char **argv) {
  static const struct pmu_spec basic[] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS},
    {"loads", PERF_TYPE_RAW, 0x81d0},
    {"stores", PERF_TYPE_RAW, 0x82d0},
  };
  static const struct pmu_spec delivery[] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES},
    {"dsb_uops", PERF_TYPE_RAW, 0x0879},
    {"mite_uops", PERF_TYPE_RAW, 0x0479},
    {"idq_not_delivered", PERF_TYPE_RAW, 0x019c},
  };
  static const struct pmu_spec execution[] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES},
    {"port_5_11_uops", PERF_TYPE_RAW, 0x20b2},
  };
  unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 10) : 100000;
  unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 10) : 1;
  const char *mode = argc > 3 ? argv[3] : "both";
  cpu_set_t set;
  CPU_ZERO(&set);
  CPU_SET(cpu, &set);
  if (sched_setaffinity(0, sizeof set, &set) != 0) {
    perror("sched_setaffinity");
    return 2;
  }
  for (unsigned i = 0; i < WORDS; ++i)
    input[i] = (int16_t)(((i * 197U + 31U) % 6901U) - 3450);
  for (unsigned warm = 0; warm < 20; ++warm)
    for (unsigned variant = 0; variant < VARIANTS; ++variant)
      (void)measure_tsc(kernels[variant], 200);

  printf("META,experiment=GT32-PLANE-N16-STOCKHAM-STAGES-007,iterations=%u,cpu=%u\n",
         iterations, cpu);
  if (strcmp(mode, "pmu") != 0) {
    for (unsigned sample = 0; sample < SAMPLES; ++sample) {
      unsigned order[VARIANTS] = {0, 1, 2, 3, 4};
      if (sample & 1U) {
        order[0] = 4; order[1] = 3; order[3] = 1; order[4] = 0;
      }
      double values[VARIANTS];
      for (unsigned position = 0; position < VARIANTS; ++position) {
        unsigned variant = order[position];
        values[variant] = measure_tsc(kernels[variant], iterations);
      }
      printf("SAMPLE,%u,folded,%.6f,reuse_one,%.6f,reuse_pair,%.6f,progressive,%.6f,pair,%.6f\n",
             sample, values[0], values[1], values[2], values[3], values[4]);
    }
  }
  if (strcmp(mode, "tsc") != 0)
    for (unsigned variant = 0; variant < VARIANTS; ++variant) {
      char label[64];
      snprintf(label, sizeof label, "%s:basic", names[variant]);
      if (!measure_pmu(kernels[variant], iterations, label, basic, 4)) break;
      snprintf(label, sizeof label, "%s:delivery", names[variant]);
      if (!measure_pmu(kernels[variant], iterations, label, delivery, 4)) break;
      snprintf(label, sizeof label, "%s:execution", names[variant]);
      if (!measure_pmu(kernels[variant], iterations, label, execution, 2)) break;
    }
  return sink == UINT64_MAX;
}
