/*
 * PMU benchmark for GT production basemul final-store contracts in their
 * immediate KEM consumers.
 *
 * This is benchmark-only.  It compares the current rminus1/scaled-r final st4
 * register contract against oldstore wrappers without changing the production
 * GT KEM path.
 */
#if !defined(__linux__)
#error "bench_gt_basemul_pipeline_pmu requires Linux perf_event_open"
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

#define VARIANT_COUNT 6
#define PMU_EVENT_COUNT 8
#define GT_BENCH_R -147

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_basemul_rminus1_oldstore(poly *r, const poly *a, const poly *b);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
void poly_basemul_scaled_r_input_oldstore(poly *r, const poly *a,
                                          const poly *b_scaled_r);
void poly_invntt_from_rminus1(poly *r, const poly *a);

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
static poly *g_c;
static poly *g_d;
static poly *g_b_scaled_r;
static poly *g_d_scaled_r;
static poly *g_tmp0;
static poly *g_tmp1;
static poly *g_out0;
static uint8_t (*g_bytes0)[NTRUPLUS_POLYBYTES];
static uint8_t (*g_bytes1)[NTRUPLUS_POLYBYTES];
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

static void scale_poly_by_r(poly *r, const poly *a)
{
  size_t i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    r->coeffs[i] =
        (int16_t)centered_modq_i32((int32_t)a->coeffs[i] * GT_BENCH_R);
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

static uint64_t checksum_bytes(const uint8_t a[NTRUPLUS_POLYBYTES])
{
  uint64_t acc = 0xbb67ae8584caa73bULL;
  size_t i;

  for (i = 0; i < NTRUPLUS_POLYBYTES; i++)
  {
    acc ^= a[i];
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
    uint64_t x = checksum_poly(&g_out0[i]);
    x ^= checksum_poly(&g_tmp0[i]);
    x ^= checksum_bytes(g_bytes0[i]);
    x ^= checksum_bytes(g_bytes1[i]);
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

static int compare_bytes(const char *label,
                         const uint8_t got[NTRUPLUS_POLYBYTES],
                         const uint8_t want[NTRUPLUS_POLYBYTES])
{
  size_t i;
  int mismatches = 0;

  for (i = 0; i < NTRUPLUS_POLYBYTES; i++)
  {
    if (got[i] != want[i])
    {
      if (mismatches < 8)
      {
        fprintf(stderr, "%s mismatch idx=%zu got=%u want=%u\n", label, i,
                (unsigned)got[i], (unsigned)want[i]);
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
    fill_poly(&g_c[i], 0x13198a2eu + (uint32_t)i);
    fill_poly(&g_d[i], 0x03707344u + (uint32_t)i);
    scale_poly_by_r(&g_b_scaled_r[i], &g_b[i]);
    scale_poly_by_r(&g_d_scaled_r[i], &g_d[i]);
  }
}

static int run_correctness(void)
{
  poly a;
  poly b;
  poly c;
  poly d;
  poly b_scaled_r;
  poly d_scaled_r;
  poly current0;
  poly current1;
  poly old0;
  poly old1;
  uint8_t current_bytes0[NTRUPLUS_POLYBYTES];
  uint8_t current_bytes1[NTRUPLUS_POLYBYTES];
  uint8_t old_bytes0[NTRUPLUS_POLYBYTES];
  uint8_t old_bytes1[NTRUPLUS_POLYBYTES];
  int mismatches = 0;

  fill_poly(&a, 101);
  fill_poly(&b, 202);
  fill_poly(&c, 303);
  fill_poly(&d, 404);
  scale_poly_by_r(&b_scaled_r, &b);
  scale_poly_by_r(&d_scaled_r, &d);

  poly_basemul_scaled_r_input(&current0, &a, &b_scaled_r);
  poly_basemul_scaled_r_input(&current1, &c, &d_scaled_r);
  poly_tobytes(current_bytes0, &current0);
  poly_tobytes(current_bytes1, &current1);

  poly_basemul_scaled_r_input_oldstore(&old0, &a, &b_scaled_r);
  poly_basemul_scaled_r_input_oldstore(&old1, &c, &d_scaled_r);
  poly_tobytes(old_bytes0, &old0);
  poly_tobytes(old_bytes1, &old1);

  mismatches += compare_poly_modq("keypair_scaled.product0", &old0, &current0);
  mismatches += compare_poly_modq("keypair_scaled.product1", &old1, &current1);
  mismatches += compare_bytes("keypair_scaled.bytes0", old_bytes0,
                              current_bytes0);
  mismatches += compare_bytes("keypair_scaled.bytes1", old_bytes1,
                              current_bytes1);

  poly_basemul_rminus1(&current0, &a, &b);
  poly_invntt_from_rminus1(&current1, &current0);
  poly_basemul_rminus1_oldstore(&old0, &a, &b);
  poly_invntt_from_rminus1(&old1, &old0);
  mismatches += compare_poly_modq("decap_rminus1.product", &old0, &current0);
  mismatches += compare_poly_modq("decap_rminus1.invntt", &old1, &current1);

  poly_crepmod3(&current1, &current1);
  poly_crepmod3(&old1, &old1);
  mismatches += compare_poly_modq("decap_rminus1.crep3", &old1, &current1);

  printf("correctness,total_mismatches=%d\n", mismatches);
  return mismatches;
}

static void target_empty(size_t idx)
{
  __asm__ volatile("" : : "r"(idx), "r"(g_tmp0), "r"(g_out0) : "memory");
}

static void target_keypair_scaled_pair_tobytes(size_t idx)
{
  poly_basemul_scaled_r_input(&g_tmp0[idx], &g_a[idx], &g_b_scaled_r[idx]);
  poly_basemul_scaled_r_input(&g_tmp1[idx], &g_c[idx], &g_d_scaled_r[idx]);
  poly_tobytes(g_bytes0[idx], &g_tmp0[idx]);
  poly_tobytes(g_bytes1[idx], &g_tmp1[idx]);
}

static void target_keypair_scaled_pair_tobytes_oldstore(size_t idx)
{
  poly_basemul_scaled_r_input_oldstore(&g_tmp0[idx], &g_a[idx],
                                       &g_b_scaled_r[idx]);
  poly_basemul_scaled_r_input_oldstore(&g_tmp1[idx], &g_c[idx],
                                       &g_d_scaled_r[idx]);
  poly_tobytes(g_bytes0[idx], &g_tmp0[idx]);
  poly_tobytes(g_bytes1[idx], &g_tmp1[idx]);
}

static void target_decap_rminus1_invntt(size_t idx)
{
  poly_basemul_rminus1(&g_tmp0[idx], &g_a[idx], &g_b[idx]);
  poly_invntt_from_rminus1(&g_out0[idx], &g_tmp0[idx]);
}

static void target_decap_rminus1_invntt_oldstore(size_t idx)
{
  poly_basemul_rminus1_oldstore(&g_tmp0[idx], &g_a[idx], &g_b[idx]);
  poly_invntt_from_rminus1(&g_out0[idx], &g_tmp0[idx]);
}

static void target_decap_rminus1_invntt_crep3(size_t idx)
{
  poly_basemul_rminus1(&g_tmp0[idx], &g_a[idx], &g_b[idx]);
  poly_invntt_from_rminus1(&g_out0[idx], &g_tmp0[idx]);
  poly_crepmod3(&g_out0[idx], &g_out0[idx]);
}

static void target_decap_rminus1_invntt_crep3_oldstore(size_t idx)
{
  poly_basemul_rminus1_oldstore(&g_tmp0[idx], &g_a[idx], &g_b[idx]);
  poly_invntt_from_rminus1(&g_out0[idx], &g_tmp0[idx]);
  poly_crepmod3(&g_out0[idx], &g_out0[idx]);
}

static struct variant g_variants[VARIANT_COUNT] = {
    {"keypair_scaled_pair_tobytes", target_keypair_scaled_pair_tobytes},
    {"keypair_scaled_pair_tobytes_oldstore",
     target_keypair_scaled_pair_tobytes_oldstore},
    {"decap_rminus1_invntt", target_decap_rminus1_invntt},
    {"decap_rminus1_invntt_oldstore", target_decap_rminus1_invntt_oldstore},
    {"decap_rminus1_invntt_crep3", target_decap_rminus1_invntt_crep3},
    {"decap_rminus1_invntt_crep3_oldstore",
     target_decap_rminus1_invntt_crep3_oldstore},
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
            "Try: sudo taskset -c 3 ./bench_gt_basemul_pipeline_pmu_bin\n");
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
  g_c = xaligned_alloc(64, g_iterations * sizeof(*g_c));
  g_d = xaligned_alloc(64, g_iterations * sizeof(*g_d));
  g_b_scaled_r = xaligned_alloc(64, g_iterations * sizeof(*g_b_scaled_r));
  g_d_scaled_r = xaligned_alloc(64, g_iterations * sizeof(*g_d_scaled_r));
  g_tmp0 = xaligned_alloc(64, g_iterations * sizeof(*g_tmp0));
  g_tmp1 = xaligned_alloc(64, g_iterations * sizeof(*g_tmp1));
  g_out0 = xaligned_alloc(64, g_iterations * sizeof(*g_out0));
  g_bytes0 = xaligned_alloc(64, g_iterations * sizeof(*g_bytes0));
  g_bytes1 = xaligned_alloc(64, g_iterations * sizeof(*g_bytes1));

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
