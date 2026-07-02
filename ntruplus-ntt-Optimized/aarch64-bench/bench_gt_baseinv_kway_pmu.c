/*
 * Benchmark-only flat k-way batch inversion harness for the GT baseinv path.
 *
 * Production poly_baseinv_scaled_r remains unchanged.  This harness compares
 * the linked production batch inversion against a C/NEON fqinv_new + flat
 * k-way prototype and a benchmark-only scaled-baseinv wrapper.
 */
#if !defined(__linux__)
#error "bench_gt_baseinv_kway_pmu requires Linux perf_event_open"
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
#define NITERATIONS 5000
#endif

#ifndef NWARMUP
#define NWARMUP 100
#endif

#ifndef NINPUTS
#define NINPUTS 256
#endif

#define PMU_EVENT_COUNT 2
#define DEN24_WORDS (24 * 8)
#define DEN36_WORDS (36 * 8)
#define M24_K_COUNT 8
#define M36_K_COUNT 9

int gt_baseinv_fqinv_batch_old_24_for_bench(int16_t r[DEN24_WORDS]);
int gt_baseinv_fqinv_batch_new_24_for_bench(int16_t r[DEN24_WORDS]);
int gt_baseinv_fqinv_kway_new_24_for_bench(int16_t r[DEN24_WORDS], int k);
int gt_baseinv_fqinv_batch_new_36_for_bench(int16_t r[DEN36_WORDS]);
int gt_baseinv_fqinv_kway_new_36_for_bench(int16_t r[DEN36_WORDS], int k);
void gt_baseinv_fqmul_vec_for_bench(int16_t out[8], const int16_t a[8],
                                    const int16_t b[8]);
int poly_baseinv_scaled_r(poly *r, const poly *a);
int poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(poly *r, const poly *a,
                                                      int k);

enum variant_mode
{
  MODE_M24_OLD = 0,
  MODE_M24_NEW = 1,
  MODE_M36_NEW = 2,
  MODE_BASEINV_CURRENT_X2 = 3,
  MODE_BASEINV_KWAY_X2 = 4,
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
  int pos;
};

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
};

struct variant
{
  const char *name;
  enum variant_mode mode;
  int k;
};

static const int g_m24_k[M24_K_COUNT] = {1, 2, 3, 4, 6, 8, 12, 24};
static const int g_m36_k[M36_K_COUNT] = {1, 2, 3, 4, 6, 9, 12, 18, 36};

static int16_t g_den24[NINPUTS][DEN24_WORDS] __attribute__((aligned(64)));
static int16_t g_den36[NINPUTS][DEN36_WORDS] __attribute__((aligned(64)));
static int16_t g_work36[DEN36_WORDS] __attribute__((aligned(64)));
static poly g_poly_inputs[NINPUTS] __attribute__((aligned(64)));
static poly g_poly_inputs_alt[NINPUTS] __attribute__((aligned(64)));
static poly g_poly_out0 __attribute__((aligned(64)));
static poly g_poly_out1 __attribute__((aligned(64)));
static size_t g_iterations = NITERATIONS;
static volatile uint64_t g_sink;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1, -1},
};

static int g_leader_fd = -1;
static int g_open_events;

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
  return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static uint32_t next_u32(uint32_t *state)
{
  *state = *state * 1664525u + 1013904223u;
  return *state;
}

static int16_t sample_nonzero_modq(uint32_t *state)
{
  int32_t v = (int32_t)(next_u32(state) % (NTRUPLUS_Q - 1)) + 1;

  if (v > NTRUPLUS_Q / 2)
    v -= NTRUPLUS_Q;
  return (int16_t)v;
}

static int16_t sample_centered_modq(uint32_t *state)
{
  int32_t v = (int32_t)(next_u32(state) % NTRUPLUS_Q);

  if (v > NTRUPLUS_Q / 2)
    v -= NTRUPLUS_Q;
  return (int16_t)v;
}

static void fill_den_inputs(void)
{
  uint32_t state = 0x6d2b79f5u;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    for (size_t i = 0; i < DEN24_WORDS; i++)
      g_den24[input][i] = sample_nonzero_modq(&state);
    for (size_t i = 0; i < DEN36_WORDS; i++)
      g_den36[input][i] = sample_nonzero_modq(&state);
  }
}

static int prepare_poly_input(poly *dst, uint32_t *state)
{
  poly tmp;

  for (int attempt = 0; attempt < 10000; attempt++)
  {
    for (size_t i = 0; i < NTRUPLUS_N; i++)
      dst->coeffs[i] = sample_centered_modq(state);

    if (poly_baseinv_scaled_r(&tmp, dst) == 0)
      return 0;
  }

  return 1;
}

static int prepare_poly_inputs(void)
{
  uint32_t state = 0x12345678u;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    if (prepare_poly_input(&g_poly_inputs[input], &state) != 0)
      return 1;
    if (prepare_poly_input(&g_poly_inputs_alt[input], &state) != 0)
      return 1;
  }

  return 0;
}

static int compare_i16(const int16_t *a, const int16_t *b, size_t n)
{
  for (size_t i = 0; i < n; i++)
  {
    if (a[i] != b[i])
      return 1;
  }
  return 0;
}

static int modq_equal_i16(int16_t a, int16_t b)
{
  int32_t diff = (int32_t)a - (int32_t)b;

  diff %= NTRUPLUS_Q;
  if (diff < 0)
    diff += NTRUPLUS_Q;
  return diff == 0;
}

static int compare_i16_modq(const int16_t *a, const int16_t *b, size_t n)
{
  for (size_t i = 0; i < n; i++)
  {
    if (!modq_equal_i16(a[i], b[i]))
      return 1;
  }
  return 0;
}

static int compare_poly(const poly *a, const poly *b)
{
  return compare_i16(a->coeffs, b->coeffs, NTRUPLUS_N);
}

static int compare_poly_modq(const poly *a, const poly *b)
{
  return compare_i16_modq(a->coeffs, b->coeffs, NTRUPLUS_N);
}

static uint64_t check_product_oracle(const int16_t *orig, const int16_t *old_inv,
                                     const int16_t *new_inv, int m)
{
  uint64_t mismatches = 0;
  int16_t old_prod[8];
  int16_t new_prod[8];

  for (int i = 0; i < m; i++)
  {
    gt_baseinv_fqmul_vec_for_bench(old_prod, orig + 8 * i,
                                   old_inv + 8 * i);
    gt_baseinv_fqmul_vec_for_bench(new_prod, orig + 8 * i,
                                   new_inv + 8 * i);
    if (compare_i16(old_prod, new_prod, 8) != 0)
      mismatches++;
  }

  return mismatches;
}

static uint64_t run_correctness(void)
{
  uint64_t mismatches = 0;
  uint64_t fqinv_mismatches = 0;
  uint64_t product_mismatches = 0;
  uint64_t baseinv_scaled_mismatches = 0;
  uint64_t exact_rep_mismatches = 0;
  int16_t old24[DEN24_WORDS];
  int16_t got36_base[DEN36_WORDS];
  int16_t got[DEN36_WORDS];
  poly current0;
  poly current1;
  poly candidate0;
  poly candidate1;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    memcpy(old24, g_den24[input], sizeof(old24));
    if (gt_baseinv_fqinv_batch_old_24_for_bench(old24) != 0)
    {
      mismatches++;
      continue;
    }

    for (size_t ki = 0; ki < M24_K_COUNT; ki++)
    {
      const int k = g_m24_k[ki];

      memcpy(got, g_den24[input], sizeof(g_den24[input]));
      if (gt_baseinv_fqinv_kway_new_24_for_bench(got, k) != 0)
      {
        mismatches++;
        fqinv_mismatches++;
        continue;
      }
      if (compare_i16_modq(old24, got, DEN24_WORDS) != 0)
      {
        mismatches++;
        fqinv_mismatches++;
      }
      if (compare_i16(old24, got, DEN24_WORDS) != 0)
        exact_rep_mismatches++;
      product_mismatches += check_product_oracle(g_den24[input], old24, got,
                                                 24);
    }

    memcpy(got36_base, g_den36[input], sizeof(got36_base));
    if (gt_baseinv_fqinv_batch_new_36_for_bench(got36_base) != 0)
    {
      mismatches++;
      continue;
    }

    for (size_t ki = 0; ki < M36_K_COUNT; ki++)
    {
      const int k = g_m36_k[ki];

      memcpy(got, g_den36[input], sizeof(g_den36[input]));
      if (gt_baseinv_fqinv_kway_new_36_for_bench(got, k) != 0)
      {
        mismatches++;
        fqinv_mismatches++;
        continue;
      }
      if (compare_i16_modq(got36_base, got, DEN36_WORDS) != 0)
      {
        mismatches++;
        fqinv_mismatches++;
      }
      if (compare_i16(got36_base, got, DEN36_WORDS) != 0)
        exact_rep_mismatches++;
    }

    if (poly_baseinv_scaled_r(&current0, &g_poly_inputs[input]) != 0 ||
        poly_baseinv_scaled_r(&current1, &g_poly_inputs_alt[input]) != 0)
    {
      mismatches++;
      continue;
    }

    for (size_t ki = 0; ki < M24_K_COUNT; ki++)
    {
      const int k = g_m24_k[ki];

      if (poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(
              &candidate0, &g_poly_inputs[input], k) != 0 ||
          poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(
              &candidate1, &g_poly_inputs_alt[input], k) != 0)
      {
        mismatches++;
        baseinv_scaled_mismatches++;
        continue;
      }
      if (compare_poly_modq(&current0, &candidate0) != 0 ||
          compare_poly_modq(&current1, &candidate1) != 0)
      {
        mismatches++;
        baseinv_scaled_mismatches++;
      }
      if (compare_poly(&current0, &candidate0) != 0 ||
          compare_poly(&current1, &candidate1) != 0)
        exact_rep_mismatches++;
    }
  }

  memcpy(got, g_den24[0], sizeof(g_den24[0]));
  got[5] = 0;
  if (gt_baseinv_fqinv_kway_new_24_for_bench(got, 4) == 0)
    mismatches++;

  printf("correctness,total_mismatches=%" PRIu64
         ",fqinv_mismatches=%" PRIu64
         ",product_oracle_mismatches=%" PRIu64
         ",baseinv_scaled_mismatches=%" PRIu64
         ",exact_rep_mismatches=%" PRIu64
         ",valid_cases=%d\n",
         mismatches + product_mismatches, fqinv_mismatches, product_mismatches,
         baseinv_scaled_mismatches, exact_rep_mismatches, NINPUTS);

  return mismatches + product_mismatches;
}

static int open_pmu_events(void)
{
  for (int i = 0; i < PMU_EVENT_COUNT; i++)
  {
    struct perf_event_attr attr;
    int group_fd = i == 0 ? -1 : g_leader_fd;

    memset(&attr, 0, sizeof(attr));
    attr.type = g_events[i].type;
    attr.size = sizeof(attr);
    attr.config = g_events[i].config;
    attr.disabled = 1;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP;

    g_events[i].fd = perf_event_open_wrap(&attr, 0, -1, group_fd, 0);
    if (g_events[i].fd < 0)
      return -1;
    if (i == 0)
      g_leader_fd = g_events[i].fd;
    g_events[i].pos = i;
    g_open_events++;
  }

  return 0;
}

static void close_pmu_events(void)
{
  for (int i = 0; i < PMU_EVENT_COUNT; i++)
  {
    if (g_events[i].fd >= 0)
      close(g_events[i].fd);
    g_events[i].fd = -1;
  }
  g_leader_fd = -1;
  g_open_events = 0;
}

static int read_counts(struct counts *out)
{
  uint64_t values[1 + PMU_EVENT_COUNT];
  ssize_t nread;

  memset(out, 0, sizeof(*out));
  nread = read(g_leader_fd, values, sizeof(values));
  if (nread < (ssize_t)sizeof(values))
    return -1;

  for (int i = 0; i < PMU_EVENT_COUNT; i++)
    out->v[i] = values[1 + i];
  return 0;
}

static void run_variant_once(const struct variant *variant, size_t idx)
{
  const size_t input = idx % NINPUTS;
  int ret = 0;

  switch (variant->mode)
  {
  case MODE_M24_OLD:
    memcpy(g_work36, g_den24[input], sizeof(g_den24[input]));
    ret = gt_baseinv_fqinv_batch_old_24_for_bench(g_work36);
    g_sink ^= (uint16_t)g_work36[(idx + 17) % DEN24_WORDS];
    break;
  case MODE_M24_NEW:
    memcpy(g_work36, g_den24[input], sizeof(g_den24[input]));
    ret = gt_baseinv_fqinv_kway_new_24_for_bench(g_work36, variant->k);
    g_sink ^= (uint16_t)g_work36[(idx + 23) % DEN24_WORDS];
    break;
  case MODE_M36_NEW:
    memcpy(g_work36, g_den36[input], sizeof(g_den36[input]));
    ret = gt_baseinv_fqinv_kway_new_36_for_bench(g_work36, variant->k);
    g_sink ^= (uint16_t)g_work36[(idx + 31) % DEN36_WORDS];
    break;
  case MODE_BASEINV_CURRENT_X2:
    ret = poly_baseinv_scaled_r(&g_poly_out0, &g_poly_inputs[input]);
    ret |= poly_baseinv_scaled_r(&g_poly_out1, &g_poly_inputs_alt[input]);
    g_sink ^= (uint16_t)g_poly_out0.coeffs[(idx + 7) % NTRUPLUS_N];
    g_sink ^= (uint16_t)g_poly_out1.coeffs[(idx + 11) % NTRUPLUS_N];
    break;
  case MODE_BASEINV_KWAY_X2:
    ret = poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(
        &g_poly_out0, &g_poly_inputs[input], variant->k);
    ret |= poly_baseinv_gt_batch_scaled_r_kway_new_for_bench(
        &g_poly_out1, &g_poly_inputs_alt[input], variant->k);
    g_sink ^= (uint16_t)g_poly_out0.coeffs[(idx + 13) % NTRUPLUS_N];
    g_sink ^= (uint16_t)g_poly_out1.coeffs[(idx + 19) % NTRUPLUS_N];
    break;
  }

  g_sink ^= (uint64_t)(unsigned)ret;
}

static void warmup_variant(const struct variant *variant)
{
  for (size_t i = 0; i < NWARMUP; i++)
    run_variant_once(variant, i);
}

static int measure_variant(const struct variant *variant, struct counts *out)
{
  warmup_variant(variant);

  if (ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) < 0)
    return -1;
  if (ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP) < 0)
    return -1;

  for (size_t i = 0; i < g_iterations; i++)
    run_variant_once(variant, i);

  if (ioctl(g_leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP) < 0)
    return -1;

  return read_counts(out);
}

static int compare_double(const void *a, const void *b)
{
  const double av = *(const double *)a;
  const double bv = *(const double *)b;

  return (av > bv) - (av < bv);
}

static void summarize_variant(const struct variant *variant)
{
  double cycles[NTESTS];
  double instr[NTESTS];
  struct counts counts;

  for (int test = 0; test < NTESTS; test++)
  {
    if (measure_variant(variant, &counts) != 0)
    {
      fprintf(stderr, "PMU read failed for %s\n", variant->name);
      exit(1);
    }

    cycles[test] = (double)counts.v[0] / (double)g_iterations;
    instr[test] = (double)counts.v[1] / (double)g_iterations;
  }

  qsort(cycles, NTESTS, sizeof(cycles[0]), compare_double);
  qsort(instr, NTESTS, sizeof(instr[0]), compare_double);

  printf("pmu,%s,cycles_p50=%.3f,cycles_iqr=%.3f,cycles_min=%.3f,"
         "cycles_max=%.3f,instr_p50=%.3f,instr_iqr=%.3f\n",
         variant->name, cycles[NTESTS / 2],
         cycles[(3 * NTESTS) / 4] - cycles[NTESTS / 4], cycles[0],
         cycles[NTESTS - 1], instr[NTESTS / 2],
         instr[(3 * NTESTS) / 4] - instr[NTESTS / 4]);
}

int main(void)
{
  struct variant variants[1 + M24_K_COUNT + M36_K_COUNT + 1 + M24_K_COUNT];
  size_t nvariants = 0;

  fill_den_inputs();
  if (prepare_poly_inputs() != 0)
  {
    fprintf(stderr, "failed to prepare invertible baseinv inputs\n");
    return 1;
  }

  if (run_correctness() != 0)
    return 1;

  variants[nvariants++] =
      (struct variant){"m24_old_batch_fqinv15_asm", MODE_M24_OLD, 1};
  for (size_t i = 0; i < M24_K_COUNT; i++)
  {
    static char names[M24_K_COUNT][48];

    snprintf(names[i], sizeof(names[i]), "m24_new_k%d", g_m24_k[i]);
    variants[nvariants++] =
        (struct variant){names[i], MODE_M24_NEW, g_m24_k[i]};
  }
  for (size_t i = 0; i < M36_K_COUNT; i++)
  {
    static char names[M36_K_COUNT][48];

    snprintf(names[i], sizeof(names[i]), "m36_new_k%d", g_m36_k[i]);
    variants[nvariants++] =
        (struct variant){names[i], MODE_M36_NEW, g_m36_k[i]};
  }
  variants[nvariants++] =
      (struct variant){"baseinv_scaled_x2_current", MODE_BASEINV_CURRENT_X2,
                       1};
  for (size_t i = 0; i < M24_K_COUNT; i++)
  {
    static char names[M24_K_COUNT][64];

    snprintf(names[i], sizeof(names[i]), "baseinv_scaled_x2_new_k%d",
             g_m24_k[i]);
    variants[nvariants++] =
        (struct variant){names[i], MODE_BASEINV_KWAY_X2, g_m24_k[i]};
  }

  if (open_pmu_events() != 0)
  {
    fprintf(stderr,
            "perf_event_open failed: %s. Try: sudo taskset -c 3 "
            "./bench_gt_baseinv_kway_pmu_bin\n",
            strerror(errno));
    close_pmu_events();
    return 1;
  }

  printf("settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  printf("columns,name,cycles_p50,cycles_iqr,cycles_min,cycles_max,"
         "instr_p50,instr_iqr\n");

  for (size_t i = 0; i < nvariants; i++)
    summarize_variant(&variants[i]);

  close_pmu_events();
  printf("sink=%" PRIu64 "\n", g_sink);
  return 0;
}
