/*
 * PMU harness for Task B finish_loop -> h/hinv fused dataflow model.
 */
#if !defined(__linux__)
#error "bench_gt_keygen_finish_to_h_hinv_pmu requires Linux perf_event_open"
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

#include "bench_build_config.h"
#include "params.h"
#include "poly.h"

#ifndef NTESTS
#define NTESTS 31
#endif
#ifndef NITERATIONS
#define NITERATIONS 5000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif
#ifndef NINPUTS
#define NINPUTS 64
#endif
#ifndef NVALID_ORACLE
#define NVALID_ORACLE 4096
#endif

#define PMU_EVENT_COUNT 2

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

int poly_baseinv_scaled_r(poly *r, const poly *a);
int poly_keygen_compute_h_hinv_direct_model(poly *h, poly *hinv,
                                            const poly *f, const poly *g);
int poly_keygen_finish_to_h_hinv_model(poly *h, poly *hinv, const poly *f,
                                       const poly *g);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);

typedef void (*bench_target_fn)(size_t idx);

struct counts
{
  uint64_t cycles;
  uint64_t instructions;
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
};

struct variant
{
  const char *name;
  bench_target_fn target;
};

static poly g_f[NINPUTS] __attribute__((aligned(64)));
static poly g_g[NINPUTS] __attribute__((aligned(64)));
static poly g_finv[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv[NINPUTS] __attribute__((aligned(64)));
static poly g_h[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv[NINPUTS] __attribute__((aligned(64)));
static poly g_h_direct[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_direct[NINPUTS] __attribute__((aligned(64)));
static poly g_h_finish[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_finish[NINPUTS] __attribute__((aligned(64)));
static poly g_work0 __attribute__((aligned(64)));
static poly g_work1 __attribute__((aligned(64)));
static poly g_work2 __attribute__((aligned(64)));
static poly g_work3 __attribute__((aligned(64)));
static uint8_t g_h_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_h_finish_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_finish_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static volatile uint64_t g_sink;
static uint64_t g_rng_state = 1;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1},
};
static int g_leader_fd = -1;

static uint32_t deterministic_u32(void)
{
  g_rng_state = g_rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (uint32_t)(g_rng_state >> 32);
}

static void fill_bytes(uint8_t *out, size_t outlen)
{
  for (size_t i = 0; i < outlen; i++)
    out[i] = (uint8_t)(deterministic_u32() >> ((i & 3) * 8));
}

static int poly_exact_mismatches(const poly *a, const poly *b)
{
  int mismatches = 0;

  for (size_t i = 0; i < NTRUPLUS_N; i++)
    mismatches += a->coeffs[i] != b->coeffs[i];
  return mismatches;
}

static int byte_mismatches(const uint8_t *a, const uint8_t *b, size_t n)
{
  int mismatches = 0;

  for (size_t i = 0; i < n; i++)
    mismatches += a[i] != b[i];
  return mismatches;
}

static int make_invertible_secret(poly *a, poly *ainv)
{
  uint8_t buf[NTRUPLUS_N / 4];

  for (int attempt = 0; attempt < 10000; attempt++)
  {
    fill_bytes(buf, sizeof(buf));
    poly_cbd1(a, buf);
    poly_ntt(a, a);
    if (poly_baseinv_scaled_r(ainv, a) == 0)
      return 0;
  }

  return 1;
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
  {
    if (make_invertible_secret(&g_f[i], &g_finv[i]) ||
        make_invertible_secret(&g_g[i], &g_ginv[i]))
    {
      fprintf(stderr, "failed to generate invertible keygen inputs\n");
      exit(1);
    }

    poly_basemul_scaled_r_input(&g_h[i], &g_g[i], &g_finv[i]);
    poly_basemul_scaled_r_input(&g_hinv[i], &g_f[i], &g_ginv[i]);
    if (poly_keygen_compute_h_hinv_direct_model(&g_h_direct[i],
                                                &g_hinv_direct[i], &g_f[i],
                                                &g_g[i]) != 0 ||
        poly_keygen_finish_to_h_hinv_model(&g_h_finish[i],
                                           &g_hinv_finish[i], &g_f[i],
                                           &g_g[i]) != 0)
    {
      fprintf(stderr, "finish_to_h_hinv model failed on prepared input\n");
      exit(1);
    }

    poly_tobytes(g_h_bytes[i], &g_h[i]);
    poly_tobytes(g_hinv_bytes[i], &g_hinv[i]);
    poly_tobytes(g_h_finish_bytes[i], &g_h_finish[i]);
    poly_tobytes(g_hinv_finish_bytes[i], &g_hinv_finish[i]);
  }
}

static int run_correctness(void)
{
  int direct_h = 0;
  int direct_hinv = 0;
  int finish_h = 0;
  int finish_hinv = 0;
  int finish_h_bytes = 0;
  int finish_hinv_bytes = 0;

  for (size_t i = 0; i < NVALID_ORACLE; i++)
  {
    const size_t slot = i % NINPUTS;

    direct_h += poly_exact_mismatches(&g_h[slot], &g_h_direct[slot]);
    direct_hinv += poly_exact_mismatches(&g_hinv[slot],
                                         &g_hinv_direct[slot]);
    finish_h += poly_exact_mismatches(&g_h[slot], &g_h_finish[slot]);
    finish_hinv += poly_exact_mismatches(&g_hinv[slot],
                                         &g_hinv_finish[slot]);
    finish_h_bytes += byte_mismatches(g_h_bytes[slot], g_h_finish_bytes[slot],
                                      NTRUPLUS_POLYBYTES);
    finish_hinv_bytes += byte_mismatches(g_hinv_bytes[slot],
                                         g_hinv_finish_bytes[slot],
                                         NTRUPLUS_POLYBYTES);
  }

  printf("oracle,oracle_current_hier_k8=1\n");
  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("direct_h_exact_mismatches=%d\n", direct_h);
  printf("direct_hinv_exact_mismatches=%d\n", direct_hinv);
  printf("finish_h_exact_mismatches=%d\n", finish_h);
  printf("finish_hinv_exact_mismatches=%d\n", finish_hinv);
  printf("finish_h_bytes_mismatches=%d\n", finish_h_bytes);
  printf("finish_hinv_bytes_mismatches=%d\n", finish_hinv_bytes);
  printf("finish_to_h_hinv_correctness,total_mismatches=%d\n",
         direct_h + direct_hinv + finish_h + finish_hinv + finish_h_bytes +
             finish_hinv_bytes);
  return direct_h + direct_hinv + finish_h + finish_hinv + finish_h_bytes +
         finish_hinv_bytes;
}

static NOINLINE void target_current_baseinv_plus_public_arithmetic(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r(&g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r(&g_work1, &g_g[input_idx]);
  poly_basemul_scaled_r_input(&g_work2, &g_g[input_idx], &g_work0);
  poly_basemul_scaled_r_input(&g_work3, &g_f[input_idx], &g_work1);
  g_sink ^= (uint16_t)g_work2.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work3.coeffs[(idx + 31) % NTRUPLUS_N];
}

static NOINLINE void target_direct_h_hinv_model_v1(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_keygen_compute_h_hinv_direct_model(&g_work2, &g_work3,
                                                &g_f[input_idx],
                                                &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work2.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work3.coeffs[(idx + 31) % NTRUPLUS_N];
}

static NOINLINE void target_finish_to_h_hinv_model(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_keygen_finish_to_h_hinv_model(&g_work2, &g_work3,
                                           &g_f[input_idx], &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work2.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work3.coeffs[(idx + 31) % NTRUPLUS_N];
}

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
  return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static void setup_perf_events(void)
{
  for (int i = 0; i < PMU_EVENT_COUNT; i++)
  {
    struct perf_event_attr attr;

    memset(&attr, 0, sizeof(attr));
    attr.type = g_events[i].type;
    attr.size = sizeof(attr);
    attr.config = g_events[i].config;
    attr.disabled = i == 0;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP;

    g_events[i].fd = perf_event_open_wrap(&attr, 0, -1, g_leader_fd, 0);
    if (g_events[i].fd < 0)
    {
      fprintf(stderr, "perf_event_open(%s): %s\n", g_events[i].name,
              strerror(errno));
      exit(1);
    }
    if (i == 0)
      g_leader_fd = g_events[i].fd;
  }
}

static void close_perf_events(void)
{
  for (int i = 0; i < PMU_EVENT_COUNT; i++)
  {
    if (g_events[i].fd >= 0)
      close(g_events[i].fd);
    g_events[i].fd = -1;
  }
  g_leader_fd = -1;
}

static struct counts measure_once(bench_target_fn fn)
{
  uint64_t values[PMU_EVENT_COUNT + 1] = {0};

  ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (size_t i = 0; i < NITERATIONS; i++)
    fn(i);
  ioctl(g_leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);

  if (read(g_leader_fd, values, sizeof(values)) != (ssize_t)sizeof(values))
  {
    perror("read perf group");
    exit(1);
  }

  return (struct counts){values[1], values[2]};
}

static int cmp_u64(const void *a, const void *b)
{
  uint64_t av = *(const uint64_t *)a;
  uint64_t bv = *(const uint64_t *)b;

  return (av > bv) - (av < bv);
}

static void run_one_variant(const struct variant *variant)
{
  uint64_t cycles[NTESTS];
  uint64_t instructions[NTESTS];
  uint64_t p25;
  uint64_t p50;
  uint64_t p75;

  for (size_t i = 0; i < NWARMUP; i++)
    variant->target(i);

  for (size_t t = 0; t < NTESTS; t++)
  {
    struct counts c = measure_once(variant->target);

    cycles[t] = c.cycles / NITERATIONS;
    instructions[t] = c.instructions / NITERATIONS;
  }

  qsort(cycles, NTESTS, sizeof(cycles[0]), cmp_u64);
  qsort(instructions, NTESTS, sizeof(instructions[0]), cmp_u64);
  p25 = cycles[NTESTS / 4];
  p50 = cycles[NTESTS / 2];
  p75 = cycles[(3 * NTESTS) / 4];

  printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_min=%" PRIu64
         ",cycles_max=%" PRIu64 ",cycles_iqr=%" PRIu64
         ",instr_p50=%" PRIu64 "\n",
         variant->name, p50, cycles[0], cycles[NTESTS - 1], p75 - p25,
         instructions[NTESTS / 2]);
}

static void run_pmu(void)
{
  static const struct variant variants[] = {
      {"current_baseinv_plus_public_arith",
       target_current_baseinv_plus_public_arithmetic},
      {"direct_h_hinv_model_v1", target_direct_h_hinv_model_v1},
      {"finish_to_h_hinv_model", target_finish_to_h_hinv_model},
  };

  setup_perf_events();
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  bench_print_gt_production_config();

  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    run_one_variant(&variants[i]);

  printf("sink=%" PRIu64 "\n", g_sink);
  close_perf_events();
}

int main(void)
{
  prepare_inputs();
  if (run_correctness() != 0)
    return 1;

  run_pmu();
  return 0;
}
