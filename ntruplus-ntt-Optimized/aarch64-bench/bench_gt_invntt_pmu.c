/*
 * PMU benchmark for GT production inverse NTT rminus1 paths.
 *
 * This is measurement-only.  It uses existing production symbols and exposed
 * stage45scratch ABIs; it does not prototype row-buffer/post fusion.
 */
#if !defined(__linux__)
#error "bench_gt_invntt_pmu requires Linux perf_event_open"
#endif

#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stddef.h>
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
#define NTESTS 31
#endif

#ifndef NITERATIONS
#define NITERATIONS 10000
#endif

#ifndef NWARMUP
#define NWARMUP 100
#endif

#define VARIANT_COUNT 5
#define PMU_EVENT_COUNT 8
#define ROW_STAGE45_I16 256

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_from_rminus1_stage45scratch(poly *r,
                                             const int16_t *scratch);
void gt_rminus1_block_major_to_stage123_stripe_scratch(int16_t *scratch,
                                                       const poly *a);
void bench_invntt_rminus1_row1_stage45_marked_canonical(
    int16_t *row_out, const int16_t *row_scratch);

typedef void (*bench_target_fn)(size_t idx);

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
};

struct variant
{
  const char *name;
  bench_target_fn target;
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
  int pos;
};

static poly *g_a;
static poly *g_b;
static poly *g_products;
static poly *g_tmp;
static poly *g_outputs;
static int16_t (*g_scratch)[NTRUPLUS_N];
static int16_t (*g_row1_stage45)[ROW_STAGE45_I16];
static size_t g_iterations = NITERATIONS;
static volatile uint64_t g_sink;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1, -1},
    {"branches", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, -1,
     -1},
    {"branch_misses", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES, -1,
     -1},
    {"l1i_miss", PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1I | (PERF_COUNT_HW_CACHE_OP_READ << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16),
     -1, -1},
    {"l1d_load_miss", PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_READ << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16),
     -1, -1},
    {"l1d_store_miss", PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16),
     -1, -1},
    {"cache_miss", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CACHE_MISSES, -1, -1},
};

static int g_leader_fd = -1;
static int g_open_events;

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
  return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static int cmp_u64(const void *a, const void *b)
{
  const uint64_t aa = *(const uint64_t *)a;
  const uint64_t bb = *(const uint64_t *)b;

  return (aa > bb) - (aa < bb);
}

static void *xaligned_alloc(size_t alignment, size_t size)
{
  void *ptr = NULL;

  if (posix_memalign(&ptr, alignment, size) != 0)
  {
    fprintf(stderr, "posix_memalign failed for %zu bytes\n", size);
    exit(EXIT_FAILURE);
  }
  memset(ptr, 0, size);
  return ptr;
}

static uint32_t next_u32(uint32_t *state)
{
  *state = *state * 1664525u + 1013904223u;
  return *state;
}

static int modq_i32(int x)
{
  int r = x % NTRUPLUS_Q;

  if (r < 0)
  {
    r += NTRUPLUS_Q;
  }
  return r;
}

static int centered_modq_i32(int x)
{
  int r = modq_i32(x);

  if (r > NTRUPLUS_Q / 2)
  {
    r -= NTRUPLUS_Q;
  }
  return r;
}

static void fill_poly(poly *a, uint32_t seed)
{
  size_t i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    uint32_t x = next_u32(&seed);
    int v = (int)(x % 4093u) - 2046;
    a->coeffs[i] = (int16_t)centered_modq_i32(v + (int)(i % 7));
  }
}

static uint64_t checksum_poly(const poly *a)
{
  uint64_t acc = 0x6a09e667f3bcc909ULL;
  size_t i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    acc ^= (uint16_t)a->coeffs[i];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }
  return acc;
}

static uint64_t checksum_scratch(const int16_t a[NTRUPLUS_N])
{
  uint64_t acc = 0xbb67ae8584caa73bULL;
  size_t i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    acc ^= (uint16_t)a[i];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }
  return acc;
}

static uint64_t checksum_row_stage45(const int16_t a[ROW_STAGE45_I16])
{
  uint64_t acc = 0x3c6ef372fe94f82bULL;
  size_t i;

  for (i = 0; i < ROW_STAGE45_I16; i++)
  {
    acc ^= (uint16_t)a[i];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }
  return acc;
}

static void checksum_outputs(void)
{
  size_t i;

  for (i = 0; i < g_iterations; i++)
  {
    uint64_t x = checksum_poly(&g_outputs[i]);
    x ^= checksum_poly(&g_tmp[i]);
    x ^= checksum_scratch(g_scratch[i]);
    x ^= checksum_row_stage45(g_row1_stage45[i]);
    g_sink ^= x + 0x9e3779b97f4a7c15ULL + (g_sink << 6) + (g_sink >> 2);
  }
}

static int compare_poly_modq(const char *label, const poly *got,
                             const poly *want)
{
  size_t i;
  int mismatches = 0;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    if (modq_i32((int)got->coeffs[i] - (int)want->coeffs[i]) != 0)
    {
      if (mismatches < 8)
      {
        fprintf(stderr, "%s mismatch idx=%zu got=%d want=%d\n", label, i,
                got->coeffs[i], want->coeffs[i]);
      }
      mismatches++;
    }
  }
  return mismatches;
}

static void prepare_inputs(void)
{
  size_t i;

  for (i = 0; i < g_iterations; i++)
  {
    fill_poly(&g_a[i], 0x243f6a88u + (uint32_t)i);
    fill_poly(&g_b[i], 0x85a308d3u + (uint32_t)i);
    poly_basemul_rminus1(&g_products[i], &g_a[i], &g_b[i]);
    gt_rminus1_block_major_to_stage123_stripe_scratch(g_scratch[i],
                                                      &g_products[i]);
  }
}

static int run_correctness(void)
{
  poly a;
  poly b;
  poly product;
  poly full;
  poly split;
  int16_t scratch[NTRUPLUS_N] __attribute__((aligned(16)));
  int16_t row1_canonical[ROW_STAGE45_I16] __attribute__((aligned(16)));
  int mismatches = 0;

  fill_poly(&a, 101);
  fill_poly(&b, 202);
  poly_basemul_rminus1(&product, &a, &b);

  poly_invntt_from_rminus1(&full, &product);
  gt_rminus1_block_major_to_stage123_stripe_scratch(scratch, &product);
  poly_invntt_from_rminus1_stage45scratch(&split, scratch);
  mismatches += compare_poly_modq("rminus1.stage45scratch", &split, &full);

  memset(row1_canonical, 0, sizeof(row1_canonical));
  bench_invntt_rminus1_row1_stage45_marked_canonical(row1_canonical,
                                                     scratch + 256);

  printf("correctness,total_mismatches=%d\n", mismatches);
  return mismatches;
}

static void target_empty(size_t idx)
{
  __asm__ volatile("" : : "r"(idx), "r"(g_products), "r"(g_outputs)
                   : "memory");
}

static void target_invntt_full(size_t idx)
{
  poly_invntt_from_rminus1(&g_outputs[idx], &g_products[idx]);
}

static void target_invntt_plus_crep3(size_t idx)
{
  poly_invntt_from_rminus1(&g_tmp[idx], &g_products[idx]);
  poly_crepmod3(&g_outputs[idx], &g_tmp[idx]);
}

static void target_block_to_stage123_scratch(size_t idx)
{
  gt_rminus1_block_major_to_stage123_stripe_scratch(g_scratch[idx],
                                                    &g_products[idx]);
}

static void target_stage45scratch_tail(size_t idx)
{
  poly_invntt_from_rminus1_stage45scratch(&g_outputs[idx], g_scratch[idx]);
}

static void target_row1_stage45_marked_canonical(size_t idx)
{
  bench_invntt_rminus1_row1_stage45_marked_canonical(g_row1_stage45[idx],
                                                     g_scratch[idx] + 256);
}

static void target_split_stage123scratch_invntt(size_t idx)
{
  gt_rminus1_block_major_to_stage123_stripe_scratch(g_scratch[idx],
                                                    &g_products[idx]);
  poly_invntt_from_rminus1_stage45scratch(&g_outputs[idx], g_scratch[idx]);
}

static struct variant g_variants[VARIANT_COUNT] = {
    {"poly_invntt_from_rminus1", target_invntt_full},
    {"poly_invntt_from_rminus1_plus_crep3", target_invntt_plus_crep3},
    {"block_major_to_stage123_scratch", target_block_to_stage123_scratch},
    {"poly_invntt_from_rminus1_stage45scratch", target_stage45scratch_tail},
    {"row1_stage45_materialized_canonical",
     target_row1_stage45_marked_canonical},
    {"split_stage123scratch_invntt", target_split_stage123scratch_invntt},
};

static void setup_perf_events(void)
{
  size_t i;

  for (i = 0; i < PMU_EVENT_COUNT; i++)
  {
    struct perf_event_attr attr;

    memset(&attr, 0, sizeof(attr));
    attr.type = g_events[i].type;
    attr.size = sizeof(attr);
    attr.config = g_events[i].config;
    attr.disabled = (i == 0) ? 1 : 0;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP | PERF_FORMAT_TOTAL_TIME_ENABLED |
                       PERF_FORMAT_TOTAL_TIME_RUNNING;

    g_events[i].fd = perf_event_open_wrap(&attr, 0, -1, g_leader_fd, 0);
    if (g_events[i].fd < 0)
    {
      fprintf(stderr, "warning: perf event %s unavailable: %s\n",
              g_events[i].name, strerror(errno));
      g_events[i].pos = -1;
      continue;
    }

    if (g_leader_fd < 0)
    {
      g_leader_fd = g_events[i].fd;
    }
    g_events[i].pos = g_open_events++;
  }

  if (g_leader_fd < 0)
  {
    fprintf(stderr,
            "perf_event_open failed for all events. "
            "Try: sudo taskset -c 3 ./bench_gt_invntt_pmu_bin\n");
    exit(EXIT_FAILURE);
  }
}

static void close_perf_events(void)
{
  size_t i;

  for (i = 0; i < PMU_EVENT_COUNT; i++)
  {
    if (g_events[i].fd >= 0)
    {
      close(g_events[i].fd);
      g_events[i].fd = -1;
    }
    g_events[i].pos = -1;
  }
  g_leader_fd = -1;
  g_open_events = 0;
}

static void perf_measure(bench_target_fn target, struct counts *out)
{
  struct
  {
    uint64_t nr;
    uint64_t time_enabled;
    uint64_t time_running;
    uint64_t values[PMU_EVENT_COUNT];
  } data;
  size_t i;

  memset(out, 0, sizeof(*out));
  memset(&data, 0, sizeof(data));

  if (ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) != 0 ||
      ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP) != 0)
  {
    perror("perf ioctl enable");
    exit(EXIT_FAILURE);
  }

  for (i = 0; i < g_iterations; i++)
  {
    target(i);
  }

  if (ioctl(g_leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP) != 0)
  {
    perror("perf ioctl disable");
    exit(EXIT_FAILURE);
  }

  if (read(g_leader_fd, &data, sizeof(data)) < 0)
  {
    perror("perf read");
    exit(EXIT_FAILURE);
  }

  for (i = 0; i < PMU_EVENT_COUNT; i++)
  {
    int pos = g_events[i].pos;
    uint64_t value;

    if (pos < 0 || (uint64_t)pos >= data.nr)
    {
      out->v[i] = 0;
      continue;
    }
    value = data.values[pos];
    if (data.time_running != 0 && data.time_enabled > data.time_running)
    {
      long double scaled = (long double)value *
                           (long double)data.time_enabled /
                           (long double)data.time_running;
      value = (uint64_t)(scaled + 0.5L);
    }
    out->v[i] = value;
  }
}

static void subtract_counts(struct counts *x, const struct counts *overhead)
{
  size_t i;

  for (i = 0; i < PMU_EVENT_COUNT; i++)
  {
    if (x->v[i] > overhead->v[i])
    {
      x->v[i] -= overhead->v[i];
    }
    else
    {
      x->v[i] = 0;
    }
  }
}

static struct counts median_overhead(void)
{
  struct counts samples[NTESTS];
  struct counts out;
  size_t i;
  size_t e;

  for (i = 0; i < NTESTS; i++)
  {
    perf_measure(target_empty, &samples[i]);
  }

  memset(&out, 0, sizeof(out));
  for (e = 0; e < PMU_EVENT_COUNT; e++)
  {
    uint64_t tmp[NTESTS];
    for (i = 0; i < NTESTS; i++)
    {
      tmp[i] = samples[i].v[e];
    }
    qsort(tmp, NTESTS, sizeof(tmp[0]), cmp_u64);
    out.v[e] = tmp[NTESTS / 2];
  }
  return out;
}

static uint64_t percentile_u64(uint64_t values[NTESTS], unsigned p)
{
  size_t idx = ((size_t)p * (NTESTS - 1)) / 100u;
  return values[idx];
}

static void print_event_value(const struct counts *counts, size_t event_idx)
{
  if (g_events[event_idx].pos < 0)
  {
    printf("na");
  }
  else
  {
    printf("%" PRIu64, counts->v[event_idx]);
  }
}

static void warmup_target(bench_target_fn target)
{
  size_t i;

  for (i = 0; i < NWARMUP; i++)
  {
    target(i % g_iterations);
  }
}

static void run_benchmarks(void)
{
  struct counts overhead;
  struct counts samples[VARIANT_COUNT][NTESTS];
  size_t sample_counts[VARIANT_COUNT];
  size_t round;
  size_t v;

  memset(sample_counts, 0, sizeof(sample_counts));
  overhead = median_overhead();

  for (round = 0; round < NTESTS; round++)
  {
    int reverse = (round & 1u) != 0u;
    for (v = 0; v < VARIANT_COUNT; v++)
    {
      size_t idx = reverse ? (VARIANT_COUNT - 1 - v) : v;
      size_t dst = sample_counts[idx]++;

      warmup_target(g_variants[idx].target);
      perf_measure(g_variants[idx].target, &samples[idx][dst]);
      subtract_counts(&samples[idx][dst], &overhead);
      checksum_outputs();
    }
  }

  printf("variant,cycles,instructions,cycles_per_call,instructions_per_call,"
         "ipc,branches,branch_misses,l1i_miss,l1d_load_miss,"
         "l1d_store_miss,cache_miss,min_cycles,p10_cycles,median_cycles,"
         "p90_cycles,samples,iterations\n");

  for (v = 0; v < VARIANT_COUNT; v++)
  {
    struct counts median;
    uint64_t cycles_sorted[NTESTS];
    size_t e;
    size_t i;
    double cycles_per_call;
    double instructions_per_call;
    double ipc;

    memset(&median, 0, sizeof(median));
    for (e = 0; e < PMU_EVENT_COUNT; e++)
    {
      uint64_t tmp[NTESTS];
      for (i = 0; i < NTESTS; i++)
      {
        tmp[i] = samples[v][i].v[e];
        if (e == 0)
        {
          cycles_sorted[i] = samples[v][i].v[e];
        }
      }
      qsort(tmp, NTESTS, sizeof(tmp[0]), cmp_u64);
      median.v[e] = tmp[NTESTS / 2];
    }
    qsort(cycles_sorted, NTESTS, sizeof(cycles_sorted[0]), cmp_u64);

    cycles_per_call = (double)median.v[0] / (double)g_iterations;
    instructions_per_call = (double)median.v[1] / (double)g_iterations;
    ipc = median.v[0] ? (double)median.v[1] / (double)median.v[0] : 0.0;

    printf("%s,", g_variants[v].name);
    print_event_value(&median, 0);
    printf(",");
    print_event_value(&median, 1);
    printf(",%.3f,%.3f,%.4f,", cycles_per_call, instructions_per_call, ipc);
    print_event_value(&median, 2);
    printf(",");
    print_event_value(&median, 3);
    printf(",");
    print_event_value(&median, 4);
    printf(",");
    print_event_value(&median, 5);
    printf(",");
    print_event_value(&median, 6);
    printf(",");
    print_event_value(&median, 7);
    printf(",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%d,%zu\n",
           cycles_sorted[0], percentile_u64(cycles_sorted, 10),
           cycles_sorted[NTESTS / 2], percentile_u64(cycles_sorted, 90),
           NTESTS, g_iterations);
  }
}

int main(void)
{
  g_a = xaligned_alloc(64, g_iterations * sizeof(*g_a));
  g_b = xaligned_alloc(64, g_iterations * sizeof(*g_b));
  g_products = xaligned_alloc(64, g_iterations * sizeof(*g_products));
  g_tmp = xaligned_alloc(64, g_iterations * sizeof(*g_tmp));
  g_outputs = xaligned_alloc(64, g_iterations * sizeof(*g_outputs));
  g_scratch = xaligned_alloc(64, g_iterations * sizeof(*g_scratch));
  g_row1_stage45 =
      xaligned_alloc(64, g_iterations * sizeof(*g_row1_stage45));

  prepare_inputs();
  if (run_correctness() != 0)
  {
    return EXIT_FAILURE;
  }

  setup_perf_events();
  run_benchmarks();
  close_perf_events();

  fprintf(stderr, "sink=%" PRIu64 "\n", g_sink);
  return EXIT_SUCCESS;
}
