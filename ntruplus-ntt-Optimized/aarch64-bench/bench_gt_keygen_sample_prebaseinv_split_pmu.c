/*
 * PMU split for keygen sample_prebaseinv_x2:
 *   shake256 -> cbd1 -> triple -> optional f[0]+=1 -> poly_ntt
 */
#if !defined(__linux__)
#error "bench_gt_keygen_sample_prebaseinv_split_pmu requires Linux perf_event_open"
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
#include "NO_CE/fips202.h"
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

static uint8_t g_seed[NINPUTS][32] __attribute__((aligned(64)));
static uint8_t g_buf_f[NINPUTS][SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static uint8_t g_buf_g[NINPUTS][SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static uint8_t g_buf_work[SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static poly g_f_cbd[NINPUTS] __attribute__((aligned(64)));
static poly g_g_cbd[NINPUTS] __attribute__((aligned(64)));
static poly g_f_triple[NINPUTS] __attribute__((aligned(64)));
static poly g_g_triple[NINPUTS] __attribute__((aligned(64)));
static poly g_f_ntt[NINPUTS] __attribute__((aligned(64)));
static poly g_g_ntt[NINPUTS] __attribute__((aligned(64)));
static poly g_f_split[NINPUTS] __attribute__((aligned(64)));
static poly g_g_split[NINPUTS] __attribute__((aligned(64)));
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

static void sample_f_ntt_from_seed(poly *out, const uint8_t seed[32])
{
  uint8_t buf[SAMPLE_BUF_BYTES];

  shake256(buf, sizeof(buf), seed, 32);
  poly_cbd1(out, buf);
  poly_triple(out, out);
  out->coeffs[0] += 1;
  poly_ntt(out, out);
}

static void sample_g_ntt_from_seed(poly *out, const uint8_t seed[32])
{
  uint8_t buf[SAMPLE_BUF_BYTES];

  shake256(buf, sizeof(buf), seed, 32);
  poly_cbd1(out, buf);
  poly_triple(out, out);
  poly_ntt(out, out);
}

static int poly_exact_mismatches(const poly *a, const poly *b)
{
  int mismatches = 0;

  for (size_t i = 0; i < NTRUPLUS_N; i++)
    mismatches += a->coeffs[i] != b->coeffs[i];
  return mismatches;
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
  {
    fill_bytes(g_seed[i], sizeof(g_seed[i]));
    shake256(g_buf_f[i], sizeof(g_buf_f[i]), g_seed[i], 32);
    shake256(g_buf_g[i], sizeof(g_buf_g[i]), g_seed[i], 32);

    poly_cbd1(&g_f_cbd[i], g_buf_f[i]);
    poly_cbd1(&g_g_cbd[i], g_buf_g[i]);

    g_f_triple[i] = g_f_cbd[i];
    g_g_triple[i] = g_g_cbd[i];
    poly_triple(&g_f_triple[i], &g_f_triple[i]);
    poly_triple(&g_g_triple[i], &g_g_triple[i]);
    g_f_triple[i].coeffs[0] += 1;

    g_f_ntt[i] = g_f_triple[i];
    g_g_ntt[i] = g_g_triple[i];
    poly_ntt(&g_f_ntt[i], &g_f_ntt[i]);
    poly_ntt(&g_g_ntt[i], &g_g_ntt[i]);

    sample_f_ntt_from_seed(&g_f_split[i], g_seed[i]);
    sample_g_ntt_from_seed(&g_g_split[i], g_seed[i]);
  }
}

static int run_correctness(void)
{
  int f_mismatches = 0;
  int g_mismatches = 0;

  for (size_t i = 0; i < NVALID_ORACLE; i++)
  {
    const size_t slot = i % NINPUTS;

    f_mismatches += poly_exact_mismatches(&g_f_ntt[slot], &g_f_split[slot]);
    g_mismatches += poly_exact_mismatches(&g_g_ntt[slot], &g_g_split[slot]);
  }

  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("sample_f_exact_mismatches=%d\n", f_mismatches);
  printf("sample_g_exact_mismatches=%d\n", g_mismatches);
  printf("sample_prebaseinv_split_correctness,total_mismatches=%d\n",
         f_mismatches + g_mismatches);
  return f_mismatches + g_mismatches;
}

static NOINLINE void target_shake_f_seed_path(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  shake256(g_buf_work, sizeof(g_buf_work), g_seed[input_idx], 32);
  g_sink ^= g_buf_work[idx % SAMPLE_BUF_BYTES];
}

static NOINLINE void target_cbd1_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_triple_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  g_work0 = g_f_cbd[input_idx];
  poly_triple(&g_work0, &g_work0);
  g_work0.coeffs[0] += 1;
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_ntt_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  g_work0 = g_f_triple[input_idx];
  poly_ntt(&g_work0, &g_work0);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_post_shake_cbd_triple_ntt_f(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  poly_triple(&g_work0, &g_work0);
  g_work0.coeffs[0] += 1;
  poly_ntt(&g_work0, &g_work0);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_shake_g_seed_path(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  shake256(g_buf_work, sizeof(g_buf_work), g_seed[input_idx], 32);
  g_sink ^= g_buf_work[(idx + 17) % SAMPLE_BUF_BYTES];
}

static NOINLINE void target_cbd1_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  g_sink ^= (uint16_t)g_work1.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_triple_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  g_work1 = g_g_cbd[input_idx];
  poly_triple(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work1.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_ntt_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  g_work1 = g_g_triple[input_idx];
  poly_ntt(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work1.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_post_shake_cbd_triple_ntt_g(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  poly_triple(&g_work1, &g_work1);
  poly_ntt(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work1.coeffs[idx % NTRUPLUS_N];
}

static NOINLINE void target_sample_prebaseinv_x2_total(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  sample_f_ntt_from_seed(&g_work0, g_seed[input_idx]);
  sample_g_ntt_from_seed(&g_work1, g_seed[input_idx]);
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
      {"shake_f_seed_path", target_shake_f_seed_path},
      {"cbd1_f", target_cbd1_f},
      {"triple_f", target_triple_f},
      {"ntt_f", target_ntt_f},
      {"post_shake_cbd_triple_ntt_f", target_post_shake_cbd_triple_ntt_f},
      {"shake_g_seed_path", target_shake_g_seed_path},
      {"cbd1_g", target_cbd1_g},
      {"triple_g", target_triple_g},
      {"ntt_g", target_ntt_g},
      {"post_shake_cbd_triple_ntt_g", target_post_shake_cbd_triple_ntt_g},
      {"sample_prebaseinv_x2_total", target_sample_prebaseinv_x2_total},
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
