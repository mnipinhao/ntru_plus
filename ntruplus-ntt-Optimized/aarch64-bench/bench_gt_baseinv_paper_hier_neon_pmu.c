/* PMU and differential harness for paper-exact recursive Neon hierarchy. */
#if !defined(__linux__)
#error "bench_gt_baseinv_paper_hier_neon_pmu requires Linux perf_event_open"
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
#include "ntt.h"
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

#define GT_DEN_VECTORS 24
#define GT_DEN_LANES 8
#define GT_DEN_WORDS (GT_DEN_VECTORS * GT_DEN_LANES)
#define PMU_EVENT_COUNT 2

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

int poly_baseinv_scaled_r(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_candidate(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
    poly *num, int16_t den[GT_DEN_WORDS], const poly *a);
int poly_baseinv_scaled_r_hier_k8_tree_for_bench(
    int16_t den[GT_DEN_WORDS]);
int gt_baseinv_paper_hier_k6_den_for_bench(int16_t den[GT_DEN_WORDS]);
int gt_baseinv_paper_hier_k8_den_for_bench(int16_t den[GT_DEN_WORDS]);
int gt_baseinv_paper_hier_k12_den_for_bench(int16_t den[GT_DEN_WORDS]);
int poly_baseinv_scaled_r_paper_hier_k6_for_bench(poly *r, const poly *a);
int poly_baseinv_scaled_r_paper_hier_k8_for_bench(poly *r, const poly *a);
int poly_baseinv_scaled_r_paper_hier_k12_for_bench(poly *r, const poly *a);
int kpqc_final_poly_baseinv_for_bench(poly *r, const poly *a);
int kpqc_final_poly_baseinv_gt_layout_for_bench(poly *r, const poly *a);
void kpqc_final_poly_baseinv_prepare_for_bench(
    poly *r, int16_t den_out[GT_DEN_WORDS], const poly *a);
int kpqc_final_poly_fqinv_batch_for_bench(int16_t den[GT_DEN_WORDS]);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);

typedef int (*baseinv_fn)(poly *r, const poly *a);
typedef int (*den_inv_fn)(int16_t den[GT_DEN_WORDS]);
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

struct correctness_variant
{
  const char *name;
  baseinv_fn baseinv;
  den_inv_fn den_inv;
};

static poly g_f[NINPUTS] __attribute__((aligned(64)));
static poly g_g[NINPUTS] __attribute__((aligned(64)));
static poly g_finv[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv[NINPUTS] __attribute__((aligned(64)));
static int16_t g_fden[NINPUTS][GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_gden[NINPUTS][GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_fden_kpqc[NINPUTS][GT_DEN_WORDS]
    __attribute__((aligned(64)));
static int16_t g_gden_kpqc[NINPUTS][GT_DEN_WORDS]
    __attribute__((aligned(64)));
static poly g_work0 __attribute__((aligned(64)));
static poly g_work1 __attribute__((aligned(64)));
static poly g_prepare_work0 __attribute__((aligned(64)));
static poly g_prepare_work1 __attribute__((aligned(64)));
static int16_t g_prepare_den0[GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_prepare_den1[GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_den_work0[GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_den_work1[GT_DEN_WORDS] __attribute__((aligned(64)));
static uint64_t g_rng_state = 1;
static volatile uint64_t g_sink;

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

static int modq_equal(int16_t a, int16_t b)
{
  int32_t d = (int32_t)a - b;

  d %= NTRUPLUS_Q;
  return d == 0;
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
    poly num;

    if (make_invertible_secret(&g_f[i], &g_finv[i]) ||
        make_invertible_secret(&g_g[i], &g_ginv[i]))
    {
      fprintf(stderr, "failed to generate invertible input\n");
      exit(1);
    }
    if (poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
            &num, g_fden[i], &g_f[i]) ||
        poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
            &num, g_gden[i], &g_g[i]))
    {
      fprintf(stderr, "baseinv prepare helper failed\n");
      exit(1);
    }
    kpqc_final_poly_baseinv_prepare_for_bench(
        &num, g_fden_kpqc[i], &g_f[i]);
    kpqc_final_poly_baseinv_prepare_for_bench(
        &num, g_gden_kpqc[i], &g_g[i]);
  }
}

static int check_zero_behavior(den_inv_fn fn)
{
  int16_t den[GT_DEN_WORDS];

  for (size_t i = 0; i < GT_DEN_WORDS; i++)
    den[i] = 1;
  den[5 * GT_DEN_LANES + 3] = 0;
  return fn(den) == 0;
}

static int check_variant(const struct correctness_variant *variant)
{
  uint64_t den_modq = 0;
  uint64_t den_exact = 0;
  uint64_t baseinv_modq = 0;
  uint64_t baseinv_exact = 0;
  uint64_t h_modq = 0;
  uint64_t h_exact = 0;
  uint64_t h_bytes = 0;
  uint64_t hinv_modq = 0;
  uint64_t hinv_exact = 0;
  uint64_t hinv_bytes = 0;
  uint64_t failures = 0;
  int zero_failure_mismatches;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    const poly *inputs[2] = {&g_f[input], &g_g[input]};
    const poly *oracles[2] = {&g_finv[input], &g_ginv[input]};
    const int16_t *raw_den[2] = {g_fden[input], g_gden[input]};

    for (size_t which = 0; which < 2; which++)
    {
      int16_t current_den[GT_DEN_WORDS] __attribute__((aligned(16)));
      int16_t candidate_den[GT_DEN_WORDS] __attribute__((aligned(16)));
      poly candidate;

      memcpy(current_den, raw_den[which], sizeof(current_den));
      memcpy(candidate_den, raw_den[which], sizeof(candidate_den));
      failures += poly_baseinv_scaled_r_hier_k8_tree_for_bench(current_den) != 0;
      failures += variant->den_inv(candidate_den) != 0;
      failures += variant->baseinv(&candidate, inputs[which]) != 0;

      for (size_t i = 0; i < GT_DEN_WORDS; i++)
      {
        den_modq += !modq_equal(current_den[i], candidate_den[i]);
        den_exact += current_den[i] != candidate_den[i];
      }
      for (size_t i = 0; i < NTRUPLUS_N; i++)
      {
        baseinv_modq += !modq_equal(oracles[which]->coeffs[i],
                                    candidate.coeffs[i]);
        baseinv_exact += oracles[which]->coeffs[i] != candidate.coeffs[i];
      }
    }

    {
      poly finv_candidate;
      poly ginv_candidate;
      poly h_current;
      poly h_candidate;
      poly hinv_current;
      poly hinv_candidate;
      uint8_t h_current_bytes[NTRUPLUS_POLYBYTES];
      uint8_t h_candidate_bytes[NTRUPLUS_POLYBYTES];
      uint8_t hinv_current_bytes[NTRUPLUS_POLYBYTES];
      uint8_t hinv_candidate_bytes[NTRUPLUS_POLYBYTES];

      failures += variant->baseinv(&finv_candidate, &g_f[input]) != 0;
      failures += variant->baseinv(&ginv_candidate, &g_g[input]) != 0;
      poly_basemul_scaled_r_input(&h_current, &g_g[input], &g_finv[input]);
      poly_basemul_scaled_r_input(&h_candidate, &g_g[input], &finv_candidate);
      poly_basemul_scaled_r_input(&hinv_current, &g_f[input], &g_ginv[input]);
      poly_basemul_scaled_r_input(&hinv_candidate, &g_f[input],
                                  &ginv_candidate);

      for (size_t i = 0; i < NTRUPLUS_N; i++)
      {
        h_modq += !modq_equal(h_current.coeffs[i], h_candidate.coeffs[i]);
        h_exact += h_current.coeffs[i] != h_candidate.coeffs[i];
        hinv_modq +=
            !modq_equal(hinv_current.coeffs[i], hinv_candidate.coeffs[i]);
        hinv_exact += hinv_current.coeffs[i] != hinv_candidate.coeffs[i];
      }

      poly_tobytes(h_current_bytes, &h_current);
      poly_tobytes(h_candidate_bytes, &h_candidate);
      poly_tobytes(hinv_current_bytes, &hinv_current);
      poly_tobytes(hinv_candidate_bytes, &hinv_candidate);
      for (size_t i = 0; i < NTRUPLUS_POLYBYTES; i++)
      {
        h_bytes += h_current_bytes[i] != h_candidate_bytes[i];
        hinv_bytes += hinv_current_bytes[i] != hinv_candidate_bytes[i];
      }
    }
  }

  zero_failure_mismatches = check_zero_behavior(variant->den_inv);
  printf("correctness,%s,failures=%" PRIu64
         ",den_modq_mismatches=%" PRIu64
         ",den_exact_mismatches=%" PRIu64
         ",baseinv_modq_mismatches=%" PRIu64
         ",baseinv_exact_mismatches=%" PRIu64
         ",h_modq_mismatches=%" PRIu64
         ",h_exact_mismatches=%" PRIu64
         ",h_byte_mismatches=%" PRIu64
         ",hinv_modq_mismatches=%" PRIu64
         ",hinv_exact_mismatches=%" PRIu64
         ",hinv_byte_mismatches=%" PRIu64
         ",zero_failure_mismatches=%d\n",
         variant->name, failures, den_modq, den_exact, baseinv_modq,
         baseinv_exact, h_modq, h_exact, h_bytes, hinv_modq, hinv_exact,
         hinv_bytes, zero_failure_mismatches);

  return failures != 0 || den_modq != 0 || baseinv_modq != 0 ||
         h_modq != 0 || h_bytes != 0 || hinv_modq != 0 ||
         hinv_bytes != 0 || zero_failure_mismatches != 0;
}

static int run_correctness(void)
{
  static const struct correctness_variant variants[] = {
      {"paper_hier_k6", poly_baseinv_scaled_r_paper_hier_k6_for_bench,
       gt_baseinv_paper_hier_k6_den_for_bench},
      {"paper_hier_k8", poly_baseinv_scaled_r_paper_hier_k8_for_bench,
       gt_baseinv_paper_hier_k8_den_for_bench},
      {"paper_hier_k12", poly_baseinv_scaled_r_paper_hier_k12_for_bench,
       gt_baseinv_paper_hier_k12_den_for_bench},
  };
  int failures = 0;

  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    failures += check_variant(&variants[i]);
  printf("correctness,total_mismatches=%d\n", failures);
  return failures;
}

static void run_kpqc_layout_contract_diagnostic(void)
{
  uint64_t inverse_modq_mismatches = 0;
  uint64_t inverse_exact_mismatches = 0;
  uint64_t product_modq_mismatches = 0;
  uint64_t product_exact_mismatches = 0;
  uint64_t failures = 0;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    const poly *operands[2] = {&g_f[input], &g_g[input]};

    for (size_t which = 0; which < 2; which++)
    {
      poly gt_inv;
      poly kpqc_inv;
      poly gt_product;
      poly kpqc_product;

      failures += poly_baseinv(&gt_inv, operands[which]) != 0;
      failures += kpqc_final_poly_baseinv_gt_layout_for_bench(
                      &kpqc_inv, operands[which]) != 0;
      poly_basemul(&gt_product, operands[which], &gt_inv);
      poly_basemul(&kpqc_product, operands[which], &kpqc_inv);
      for (size_t i = 0; i < NTRUPLUS_N; i++)
      {
        inverse_modq_mismatches +=
            !modq_equal(gt_inv.coeffs[i], kpqc_inv.coeffs[i]);
        inverse_exact_mismatches +=
            gt_inv.coeffs[i] != kpqc_inv.coeffs[i];
        product_modq_mismatches +=
            !modq_equal(gt_product.coeffs[i], kpqc_product.coeffs[i]);
        product_exact_mismatches +=
            gt_product.coeffs[i] != kpqc_product.coeffs[i];
      }
    }
  }

  printf("kpqc_layout_contract,failures=%" PRIu64
         ",inverse_modq_mismatches=%" PRIu64
         ",inverse_exact_mismatches=%" PRIu64
         ",product_modq_mismatches=%" PRIu64
         ",product_exact_mismatches=%" PRIu64 "\n",
         failures, inverse_modq_mismatches, inverse_exact_mismatches,
         product_modq_mismatches, product_exact_mismatches);
}

#define DEFINE_BASEINV_TARGET(NAME, FN)                                      \
  static NOINLINE void NAME(size_t idx)                                     \
  {                                                                         \
    const size_t input = idx % NINPUTS;                                     \
    (void)FN(&g_work0, &g_f[input]);                                        \
    (void)FN(&g_work1, &g_g[input]);                                        \
    g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];                   \
    g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];            \
  }

#define DEFINE_DEN_TARGET(NAME, FN)                                          \
  static NOINLINE void NAME(size_t idx)                                     \
  {                                                                         \
    const size_t input = idx % NINPUTS;                                     \
    memcpy(g_den_work0, g_fden[input], sizeof(g_den_work0));                 \
    memcpy(g_den_work1, g_gden[input], sizeof(g_den_work1));                 \
    (void)FN(g_den_work0);                                                   \
    (void)FN(g_den_work1);                                                   \
    g_sink ^= (uint16_t)g_den_work0[idx % GT_DEN_WORDS];                    \
    g_sink ^= (uint16_t)g_den_work1[(idx + 23) % GT_DEN_WORDS];             \
  }

DEFINE_BASEINV_TARGET(target_current_baseinv_x2, poly_baseinv_scaled_r)
DEFINE_BASEINV_TARGET(target_current_hier_k8_baseinv_x2,
                      poly_baseinv_scaled_r_hier_k8_candidate)
DEFINE_BASEINV_TARGET(target_paper_k6_baseinv_x2,
                      poly_baseinv_scaled_r_paper_hier_k6_for_bench)
DEFINE_BASEINV_TARGET(target_paper_k8_baseinv_x2,
                      poly_baseinv_scaled_r_paper_hier_k8_for_bench)
DEFINE_BASEINV_TARGET(target_paper_k12_baseinv_x2,
                      poly_baseinv_scaled_r_paper_hier_k12_for_bench)
DEFINE_BASEINV_TARGET(target_kpqc_baseinv_x2,
                      kpqc_final_poly_baseinv_for_bench)
DEFINE_BASEINV_TARGET(target_kpqc_gt_layout_baseinv_x2,
                      kpqc_final_poly_baseinv_gt_layout_for_bench)
DEFINE_DEN_TARGET(target_current_den_x2,
                  poly_baseinv_scaled_r_hier_k8_tree_for_bench)
DEFINE_DEN_TARGET(target_paper_k6_den_x2,
                  gt_baseinv_paper_hier_k6_den_for_bench)
DEFINE_DEN_TARGET(target_paper_k8_den_x2,
                  gt_baseinv_paper_hier_k8_den_for_bench)
DEFINE_DEN_TARGET(target_paper_k12_den_x2,
                  gt_baseinv_paper_hier_k12_den_for_bench)

static NOINLINE void target_gt_prepare_x2(size_t idx)
{
  const size_t input = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
      &g_prepare_work0, g_prepare_den0, &g_f[input]);
  (void)poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
      &g_prepare_work1, g_prepare_den1, &g_g[input]);
  g_sink ^= (uint16_t)g_prepare_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_prepare_den1[(idx + 17) % GT_DEN_WORDS];
}

static NOINLINE void target_kpqc_prepare_x2(size_t idx)
{
  const size_t input = idx % NINPUTS;

  kpqc_final_poly_baseinv_prepare_for_bench(
      &g_prepare_work0, g_prepare_den0, &g_f[input]);
  kpqc_final_poly_baseinv_prepare_for_bench(
      &g_prepare_work1, g_prepare_den1, &g_g[input]);
  g_sink ^= (uint16_t)g_prepare_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_prepare_den1[(idx + 17) % GT_DEN_WORDS];
}

static NOINLINE void target_kpqc_den_x2(size_t idx)
{
  const size_t input = idx % NINPUTS;

  memcpy(g_den_work0, g_fden_kpqc[input], sizeof(g_den_work0));
  memcpy(g_den_work1, g_gden_kpqc[input], sizeof(g_den_work1));
  (void)kpqc_final_poly_fqinv_batch_for_bench(g_den_work0);
  (void)kpqc_final_poly_fqinv_batch_for_bench(g_den_work1);
  g_sink ^= (uint16_t)g_den_work0[idx % GT_DEN_WORDS];
  g_sink ^= (uint16_t)g_den_work1[(idx + 23) % GT_DEN_WORDS];
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
         ",instr_p50=%" PRIu64 ",ipc=%.3f\n",
         variant->name, p50, cycles[0], cycles[NTESTS - 1], p75 - p25,
         instructions[NTESTS / 2],
         p50 == 0 ? 0.0 : (double)instructions[NTESTS / 2] / (double)p50);
}

static void run_pmu(void)
{
  static const struct variant variants[] = {
      {"prepare_gt_vld4_x2", target_gt_prepare_x2},
      {"prepare_kpqc_contiguous_q_x2", target_kpqc_prepare_x2},
      {"den_current_serial_inner_x2", target_current_den_x2},
      {"den_paper_hier_k6_x2", target_paper_k6_den_x2},
      {"den_paper_hier_k8_x2", target_paper_k8_den_x2},
      {"den_paper_hier_k12_x2", target_paper_k12_den_x2},
      {"den_kpqc_flat_batch_x2", target_kpqc_den_x2},
      {"baseinv_current_external_hier_k8_x2", target_current_baseinv_x2},
      {"baseinv_internal_monolith_hier_k8_x2",
       target_current_hier_k8_baseinv_x2},
      {"baseinv_paper_hier_k6_x2", target_paper_k6_baseinv_x2},
      {"baseinv_paper_hier_k8_x2", target_paper_k8_baseinv_x2},
      {"baseinv_paper_hier_k12_x2", target_paper_k12_baseinv_x2},
      {"baseinv_kpqc_final_x2", target_kpqc_baseinv_x2},
      {"baseinv_kpqc_final_gt_layout_roundtrip_x2",
       target_kpqc_gt_layout_baseinv_x2},
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
  run_kpqc_layout_contract_diagnostic();
  run_pmu();
  return 0;
}
