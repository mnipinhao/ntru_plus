/*
 * PMU/correctness harness for keygen sample -> SAMPLE-DAG Slothy-scheduled NTT input-path fusion.
 *
 * Candidate symbols are benchmark-only and are intentionally not declared in
 * poly.h:
 *   poly_ntt_mul3_reference(out, a)           == poly_ntt(3*a)
 *   poly_ntt_mul3_add1_reference(out, a)      == poly_ntt(3*a + 1 at coeff 0)
 *   poly_ntt_mul3(out, a)      == poly_ntt(3*a)
 *   poly_ntt_mul3_add1(out, a) == poly_ntt(3*a + 1 at coeff 0)
 */
#if !defined(__linux__)
#error "bench_gt_keygen_sample_ntt_fusion_pmu requires Linux perf_event_open"
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
#define SAMPLE_BUF_BYTES (NTRUPLUS_N / 4)

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

void poly_ntt_mul3_reference(poly *out, const poly *a);
void poly_ntt_mul3_add1_reference(poly *out, const poly *a);
void poly_ntt_mul3(poly *out, const poly *a);
void poly_ntt_mul3_add1(poly *out, const poly *a);
int poly_baseinv_scaled_r(poly *r, const poly *a);

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

static uint8_t g_buf_f[NINPUTS][SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static uint8_t g_buf_g[NINPUTS][SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static poly g_f_small[NINPUTS] __attribute__((aligned(64)));
static poly g_g_small[NINPUTS] __attribute__((aligned(64)));
static poly g_f_ref[NINPUTS] __attribute__((aligned(64)));
static poly g_g_ref[NINPUTS] __attribute__((aligned(64)));
static poly g_f_symbolic[NINPUTS] __attribute__((aligned(64)));
static poly g_g_symbolic[NINPUTS] __attribute__((aligned(64)));
static poly g_f_slothy[NINPUTS] __attribute__((aligned(64)));
static poly g_g_slothy[NINPUTS] __attribute__((aligned(64)));
static poly g_work0 __attribute__((aligned(64)));
static poly g_work1 __attribute__((aligned(64)));
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

static void reference_ntt_triple(poly *out, const poly *small)
{
  *out = *small;
  poly_triple(out, out);
  poly_ntt(out, out);
}

static void reference_ntt_triple_add1(poly *out, const poly *small)
{
  *out = *small;
  poly_triple(out, out);
  out->coeffs[0] += 1;
  poly_ntt(out, out);
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
  {
    fill_bytes(g_buf_f[i], sizeof(g_buf_f[i]));
    fill_bytes(g_buf_g[i], sizeof(g_buf_g[i]));

    poly_cbd1(&g_f_small[i], g_buf_f[i]);
    poly_cbd1(&g_g_small[i], g_buf_g[i]);

    reference_ntt_triple_add1(&g_f_ref[i], &g_f_small[i]);
    reference_ntt_triple(&g_g_ref[i], &g_g_small[i]);
    poly_ntt_mul3_add1_reference(&g_f_symbolic[i], &g_f_small[i]);
    poly_ntt_mul3_reference(&g_g_symbolic[i], &g_g_small[i]);
    poly_ntt_mul3_add1(&g_f_slothy[i], &g_f_small[i]);
    poly_ntt_mul3(&g_g_slothy[i], &g_g_small[i]);
  }
}

static int baseinv_compare_mismatches(const poly *ref, const poly *cand,
                                      int *checked_cases)
{
  poly ref_inv;
  poly cand_inv;
  int ref_ret = poly_baseinv_scaled_r(&ref_inv, ref);
  int cand_ret = poly_baseinv_scaled_r(&cand_inv, cand);

  if (ref_ret != cand_ret)
    return 1;
  if (ref_ret != 0)
    return 0;

  *checked_cases += 1;
  return poly_exact_mismatches(&ref_inv, &cand_inv);
}

static int run_correctness(void)
{
  int f_symbolic_mismatches = 0;
  int g_symbolic_mismatches = 0;
  int f_slothy_mismatches = 0;
  int g_slothy_mismatches = 0;
  int baseinv_symbolic_mismatches = 0;
  int baseinv_slothy_mismatches = 0;
  int baseinv_checked_cases = 0;

  for (size_t i = 0; i < NVALID_ORACLE; i++)
  {
    poly small;
    poly ref;
    poly symbolic;
    poly slothy;
    uint8_t buf[SAMPLE_BUF_BYTES];

    fill_bytes(buf, sizeof(buf));
    poly_cbd1(&small, buf);

    reference_ntt_triple_add1(&ref, &small);
    poly_ntt_mul3_add1_reference(&symbolic, &small);
    poly_ntt_mul3_add1(&slothy, &small);
    f_symbolic_mismatches += poly_exact_mismatches(&ref, &symbolic);
    f_slothy_mismatches += poly_exact_mismatches(&ref, &slothy);
    baseinv_symbolic_mismatches +=
        baseinv_compare_mismatches(&ref, &symbolic, &baseinv_checked_cases);
    baseinv_slothy_mismatches +=
        baseinv_compare_mismatches(&ref, &slothy, &baseinv_checked_cases);

    reference_ntt_triple(&ref, &small);
    poly_ntt_mul3_reference(&symbolic, &small);
    poly_ntt_mul3(&slothy, &small);
    g_symbolic_mismatches += poly_exact_mismatches(&ref, &symbolic);
    g_slothy_mismatches += poly_exact_mismatches(&ref, &slothy);
    baseinv_symbolic_mismatches +=
        baseinv_compare_mismatches(&ref, &symbolic, &baseinv_checked_cases);
    baseinv_slothy_mismatches +=
        baseinv_compare_mismatches(&ref, &slothy, &baseinv_checked_cases);
  }

  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("ntt_triple_add1_symbolic_mismatches=%d\n", f_symbolic_mismatches);
  printf("ntt_triple_add1_slothy_mismatches=%d\n", f_slothy_mismatches);
  printf("ntt_triple_symbolic_mismatches=%d\n", g_symbolic_mismatches);
  printf("ntt_triple_slothy_mismatches=%d\n", g_slothy_mismatches);
  printf("baseinv_downstream_checked_cases=%d\n", baseinv_checked_cases);
  printf("baseinv_downstream_symbolic_mismatches=%d\n",
         baseinv_symbolic_mismatches);
  printf("baseinv_downstream_slothy_mismatches=%d\n", baseinv_slothy_mismatches);
  printf("keygen_sample_ntt_fusion_slothy_correctness,total_mismatches=%d\n",
         f_symbolic_mismatches + f_slothy_mismatches + g_symbolic_mismatches +
             g_slothy_mismatches + baseinv_symbolic_mismatches +
             baseinv_slothy_mismatches);
  return f_symbolic_mismatches + f_slothy_mismatches + g_symbolic_mismatches +
         g_slothy_mismatches + baseinv_symbolic_mismatches +
         baseinv_slothy_mismatches;
}

static NOINLINE void target_current_triple_plus_ntt_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  reference_ntt_triple_add1(&g_work0, &g_f_small[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_symbolic_ntt_triple_add1_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_ntt_mul3_add1_reference(&g_work0, &g_f_small[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_slothy_ntt_triple_add1_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_ntt_mul3_add1(&g_work0, &g_f_small[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_current_triple_plus_ntt_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  reference_ntt_triple(&g_work1, &g_g_small[input_idx]);
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_symbolic_ntt_triple_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_ntt_mul3_reference(&g_work1, &g_g_small[input_idx]);
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_slothy_ntt_triple_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_ntt_mul3(&g_work1, &g_g_small[input_idx]);
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_post_cbd_x2_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  poly_triple(&g_work0, &g_work0);
  g_work0.coeffs[0] += 1;
  poly_triple(&g_work1, &g_work1);
  poly_ntt(&g_work0, &g_work0);
  poly_ntt(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 31) % NTRUPLUS_N];
}

static NOINLINE void target_post_cbd_x2_symbolic_candidate(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  poly_ntt_mul3_add1_reference(&g_work0, &g_work0);
  poly_ntt_mul3_reference(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 31) % NTRUPLUS_N];
}

static NOINLINE void target_post_cbd_x2_slothy_candidate(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  poly_ntt_mul3_add1(&g_work0, &g_work0);
  poly_ntt_mul3(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 31) % NTRUPLUS_N];
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
      {"current_triple_plus_ntt_f", target_current_triple_plus_ntt_f},
      {"symbolic_candidate_ntt_triple_add1_f", target_symbolic_ntt_triple_add1_f},
      {"slothy_candidate_ntt_triple_add1_f", target_slothy_ntt_triple_add1_f},
      {"current_triple_plus_ntt_g", target_current_triple_plus_ntt_g},
      {"symbolic_candidate_ntt_triple_g", target_symbolic_ntt_triple_g},
      {"slothy_candidate_ntt_triple_g", target_slothy_ntt_triple_g},
      {"post_cbd_x2_current", target_post_cbd_x2_current},
      {"post_cbd_x2_symbolic_candidate", target_post_cbd_x2_symbolic_candidate},
      {"post_cbd_x2_slothy_candidate", target_post_cbd_x2_slothy_candidate},
  };

  setup_perf_events();
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  bench_print_gt_production_config();
#ifdef GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3
  printf("build_config,GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3=1\n");
#else
  printf("build_config,GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3=0\n");
#endif

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
