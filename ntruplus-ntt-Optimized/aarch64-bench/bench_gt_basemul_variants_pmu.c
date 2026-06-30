/*
 * PMU benchmark for live GT production basemul symbols and final-store
 * contract variants.
 *
 * This binary links all symbols into one process and interleaves samples under
 * perf_event_open.  It is benchmark-only and does not change the production
 * GT KEM path.
 */
#if !defined(__linux__)
#error "bench_gt_basemul_variants_pmu requires Linux perf_event_open"
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

#include "ntt.h"
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

#define VARIANT_COUNT 8
#define PMU_EVENT_COUNT 8
#define GT_BENCH_R -147
#define GT_BENCH_QINV 12929

void poly_basemul_add32(poly *r, const poly *a, const poly *b, const poly *c);
void poly_basemul_ldrtrn_noadd(poly *r, const poly *a, const poly *b);
void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_basemul_rminus1_oldstore(poly *r, const poly *a, const poly *b);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
void poly_basemul_scaled_r_input_oldstore(poly *r, const poly *a,
                                          const poly *b_scaled_r);
void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b);
void poly_basemul_add_gt_ref(poly *r, const poly *a, const poly *b,
                             const poly *c);

typedef void (*bench_target_fn)(size_t idx);

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
};

struct variant_stats
{
  uint64_t text_size;
  uint64_t static_insns;
  uint64_t ld4;
  uint64_t st4;
  uint64_t ldr_qd;
  uint64_t ldp_qd;
  uint64_t str_qd;
  uint64_t stp_qd;
  uint64_t uzp;
  uint64_t trn;
  uint64_t zip;
  uint64_t mov_vec;
  uint64_t mul_reduce;
  uint64_t sp_mem;
};

struct variant
{
  const char *name;
  bench_target_fn target;
  struct variant_stats stats;
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
static poly *g_b_scaled_r;
static poly *g_c;
static poly *g_outputs;
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

static int16_t montgomery_reduce_ref(int32_t a)
{
  int16_t t;

  t = (int16_t)a * GT_BENCH_QINV;
  t = (int16_t)((a - (int32_t)t * NTRUPLUS_Q) >> 16);
  return t;
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

static void checksum_outputs(void)
{
  size_t i;

  for (i = 0; i < g_iterations; i++)
  {
    uint64_t x = checksum_poly(&g_outputs[i]);
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

static void basemul_raw_ref(int16_t r[4], const int16_t a[4],
                            const int16_t b[4], int16_t zeta)
{
  r[0] = montgomery_reduce_ref((int32_t)a[1] * b[3] +
                               (int32_t)a[2] * b[2] +
                               (int32_t)a[3] * b[1]);
  r[1] = montgomery_reduce_ref((int32_t)a[2] * b[3] +
                               (int32_t)a[3] * b[2]);
  r[2] = montgomery_reduce_ref((int32_t)a[3] * b[3]);

  r[0] = montgomery_reduce_ref((int32_t)r[0] * zeta +
                               (int32_t)a[0] * b[0]);
  r[1] = montgomery_reduce_ref((int32_t)r[1] * zeta +
                               (int32_t)a[0] * b[1] +
                               (int32_t)a[1] * b[0]);
  r[2] = montgomery_reduce_ref((int32_t)r[2] * zeta +
                               (int32_t)a[0] * b[2] +
                               (int32_t)a[1] * b[1] +
                               (int32_t)a[2] * b[0]);
  r[3] = montgomery_reduce_ref((int32_t)a[0] * b[3] +
                               (int32_t)a[1] * b[2] +
                               (int32_t)a[2] * b[1] +
                               (int32_t)a[3] * b[0]);
}

static void poly_basemul_raw_gt_ref(poly *r, const poly *a, const poly *b)
{
  int branch;

  for (branch = 0; branch < 2; branch++)
  {
    const int branch_start = branch * (NTRUPLUS_N / 2);
    int physical_j;

    for (physical_j = 0; physical_j < 96; physical_j++)
    {
      const int pos = branch_start + 4 * physical_j;

      basemul_raw_ref(r->coeffs + pos, a->coeffs + pos, b->coeffs + pos,
                      gt_rowbitrev_lambda[branch][physical_j]);
    }
  }
}

static void prepare_inputs(void)
{
  size_t i;

  for (i = 0; i < g_iterations; i++)
  {
    fill_poly(&g_a[i], 0x243f6a88u + (uint32_t)i);
    fill_poly(&g_b[i], 0x85a308d3u + (uint32_t)i);
    fill_poly(&g_c[i], 0x13198a2eu + (uint32_t)i);
    scale_poly_by_r(&g_b_scaled_r[i], &g_b[i]);
  }
}

static int run_correctness(void)
{
  poly a;
  poly b;
  poly b_scaled_r;
  poly c;
  poly want;
  poly got;
  int mismatches = 0;

  fill_poly(&a, 101);
  fill_poly(&b, 202);
  fill_poly(&c, 303);
  scale_poly_by_r(&b_scaled_r, &b);

  poly_basemul_gt_ref(&want, &a, &b);
  poly_basemul(&got, &a, &b);
  mismatches += compare_poly_modq("poly_basemul", &got, &want);
  poly_basemul_ldrtrn_noadd(&got, &a, &b);
  mismatches += compare_poly_modq("poly_basemul_ldrtrn_noadd", &got, &want);

  poly_basemul_add_gt_ref(&want, &a, &b, &c);
  poly_basemul_add(&got, &a, &b, &c);
  mismatches += compare_poly_modq("poly_basemul_add", &got, &want);
  poly_basemul_add32(&got, &a, &b, &c);
  mismatches += compare_poly_modq("poly_basemul_add32", &got, &want);

  poly_basemul_raw_gt_ref(&want, &a, &b);
  poly_basemul_rminus1(&got, &a, &b);
  mismatches += compare_poly_modq("poly_basemul_rminus1", &got, &want);
  poly_basemul_rminus1_oldstore(&got, &a, &b);
  mismatches +=
      compare_poly_modq("poly_basemul_rminus1_oldstore", &got, &want);

  poly_basemul_gt_ref(&want, &a, &b);
  poly_basemul_scaled_r_input(&got, &a, &b_scaled_r);
  mismatches += compare_poly_modq("poly_basemul_scaled_r_input", &got, &want);
  poly_basemul_scaled_r_input_oldstore(&got, &a, &b_scaled_r);
  mismatches +=
      compare_poly_modq("poly_basemul_scaled_r_input_oldstore", &got, &want);

  printf("correctness,total_mismatches=%d\n", mismatches);
  return mismatches;
}

static void target_empty(size_t idx)
{
  __asm__ volatile("" : : "r"(idx), "r"(g_outputs) : "memory");
}

static void target_basemul(size_t idx)
{
  poly_basemul(&g_outputs[idx], &g_a[idx], &g_b[idx]);
}

static void target_basemul_ldrtrn_noadd(size_t idx)
{
  poly_basemul_ldrtrn_noadd(&g_outputs[idx], &g_a[idx], &g_b[idx]);
}

static void target_basemul_add(size_t idx)
{
  poly_basemul_add(&g_outputs[idx], &g_a[idx], &g_b[idx], &g_c[idx]);
}

static void target_basemul_add32(size_t idx)
{
  poly_basemul_add32(&g_outputs[idx], &g_a[idx], &g_b[idx], &g_c[idx]);
}

static void target_rminus1(size_t idx)
{
  poly_basemul_rminus1(&g_outputs[idx], &g_a[idx], &g_b[idx]);
}

static void target_rminus1_oldstore(size_t idx)
{
  poly_basemul_rminus1_oldstore(&g_outputs[idx], &g_a[idx], &g_b[idx]);
}

static void target_scaled_r_input(size_t idx)
{
  poly_basemul_scaled_r_input(&g_outputs[idx], &g_a[idx], &g_b_scaled_r[idx]);
}

static void target_scaled_r_input_oldstore(size_t idx)
{
  poly_basemul_scaled_r_input_oldstore(&g_outputs[idx], &g_a[idx],
                                       &g_b_scaled_r[idx]);
}

static struct variant g_variants[VARIANT_COUNT] = {
    {"poly_basemul", target_basemul, {0}},
    {"poly_basemul_ldrtrn_noadd", target_basemul_ldrtrn_noadd, {0}},
    {"poly_basemul_add", target_basemul_add, {0}},
    {"poly_basemul_add32", target_basemul_add32, {0}},
    {"poly_basemul_rminus1", target_rminus1, {0}},
    {"poly_basemul_rminus1_oldstore", target_rminus1_oldstore, {0}},
    {"poly_basemul_scaled_r_input", target_scaled_r_input, {0}},
    {"poly_basemul_scaled_r_input_oldstore", target_scaled_r_input_oldstore,
     {0}},
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

    g_events[i].fd =
        perf_event_open_wrap(&attr, 0, -1, g_leader_fd, 0);
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
            "Try: sudo taskset -c 3 ./bench_gt_basemul_variants_pmu\n");
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

static void load_variant_stats_one(struct variant *variant)
{
  const char *path = getenv("GT_BASEMUL_STATS_FILE");
  char line[512];
  FILE *f;

  if (path == NULL || path[0] == '\0')
  {
    path = "bench_gt_basemul_variants_pmu.stats";
  }

  f = fopen(path, "r");
  if (f == NULL)
  {
    return;
  }

  while (fgets(line, sizeof(line), f) != NULL)
  {
    char name[160];
    struct variant_stats s;

    if (line[0] == '#')
    {
      continue;
    }

    memset(&s, 0, sizeof(s));
    if (sscanf(line,
               "%159[^,],%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64
               ",%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64
               ",%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64,
               name, &s.text_size, &s.static_insns, &s.ld4, &s.st4,
               &s.ldr_qd, &s.ldp_qd, &s.str_qd, &s.stp_qd, &s.uzp, &s.trn,
               &s.zip, &s.mov_vec, &s.mul_reduce, &s.sp_mem) == 15 &&
        strcmp(name, variant->name) == 0)
    {
      variant->stats = s;
      fclose(f);
      return;
    }
  }
  fclose(f);
}

static void load_variant_stats(void)
{
  size_t i;

  for (i = 0; i < VARIANT_COUNT; i++)
  {
    load_variant_stats_one(&g_variants[i]);
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
  load_variant_stats();
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
         "l1d_store_miss,cache_miss,text_size,static_insns,ld4,st4,"
         "ldr_qd,ldp_qd,str_qd,stp_qd,uzp,trn,zip,mov_vec,mul_reduce,"
         "sp_mem,min_cycles,p10_cycles,median_cycles,p90_cycles,samples,"
         "iterations\n");

  for (v = 0; v < VARIANT_COUNT; v++)
  {
    struct counts median;
    uint64_t cycles_sorted[NTESTS];
    size_t e;
    size_t i;
    double cycles_per_call;
    double instructions_per_call;
    double ipc;
    const struct variant_stats *s = &g_variants[v].stats;

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
    printf(",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
           ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
           ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
           ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%zu,%zu\n",
           s->text_size, s->static_insns, s->ld4, s->st4, s->ldr_qd,
           s->ldp_qd, s->str_qd, s->stp_qd, s->uzp, s->trn, s->zip,
           s->mov_vec, s->mul_reduce, s->sp_mem, cycles_sorted[0],
           percentile_u64(cycles_sorted, 10),
           cycles_sorted[NTESTS / 2], percentile_u64(cycles_sorted, 90),
           (size_t)NTESTS, g_iterations);
  }

  printf("checksum,%" PRIu64 "\n", g_sink);
}

int main(void)
{
  g_a = xaligned_alloc(64, g_iterations * sizeof(*g_a));
  g_b = xaligned_alloc(64, g_iterations * sizeof(*g_b));
  g_b_scaled_r = xaligned_alloc(64, g_iterations * sizeof(*g_b_scaled_r));
  g_c = xaligned_alloc(64, g_iterations * sizeof(*g_c));
  g_outputs = xaligned_alloc(64, g_iterations * sizeof(*g_outputs));

  prepare_inputs();
  if (run_correctness() != 0)
  {
    return EXIT_FAILURE;
  }

  setup_perf_events();
  run_benchmarks();
  close_perf_events();

  free(g_a);
  free(g_b);
  free(g_b_scaled_r);
  free(g_c);
  free(g_outputs);
  return EXIT_SUCCESS;
}
