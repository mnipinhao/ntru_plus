/*
 * PMU harness for a benchmark-only hier_k8 denominator-tree candidate.
 *
 * This target compares the production hier_k8 tree with a specialized k=8,
 * group-size-3 candidate.  It does not change production dispatch.
 */
#if !defined(__linux__)
#error "bench_gt_baseinv_hier_k8_tree_candidate_pmu requires Linux perf_event_open"
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

#ifndef NVALID_ORACLE
#define NVALID_ORACLE 4096
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
int poly_baseinv_scaled_r_hier_k8_prepare_for_bench(poly *num,
                                                    int16_t den[GT_DEN_WORDS],
                                                    const poly *a);
int poly_baseinv_scaled_r_hier_k8_tree_for_bench(int16_t den[GT_DEN_WORDS]);
int poly_baseinv_scaled_r_hier_k8_tree_candidate(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_prepare_fused_candidate(poly *r,
                                                          const poly *a);
int poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate(poly *r,
                                                              const poly *a);
int poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate(poly *r,
                                                               const poly *a);
int poly_baseinv_scaled_r_hier_k8_prepare2_slothy_candidate(poly *r,
                                                            const poly *a);
int poly_baseinv_scaled_r_hier_k8_full_asm_candidate(poly *r,
                                                     const poly *a);
int poly_baseinv_scaled_r_hier_k8_prepare2_slothy_paper_candidate(
    poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate(poly *r,
                                                           const poly *a);
int baseinv_prepare_hier_k8_prepare2_slothy_diff_for_bench(
    const poly *a, int *kind, int *index, int16_t *baseline,
    int16_t *candidate);
void baseinv_prepare_hier_k8_group_products_prepare2_asm(
    int16_t *dst, int16_t *den, int16_t *c01, int16_t *group_prod,
    const int16_t *src, const int16_t *lambda, const int16_t *con);
void baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm(
    int16_t *dst, int16_t *den, int16_t *c01, int16_t *group_prod,
    const int16_t *src, const int16_t *lambda, const int16_t *con);
int poly_baseinv_scaled_r_hier_k8_tree_candidate_for_bench(
    int16_t den[GT_DEN_WORDS]);
int kpqc_final_poly_baseinv_for_bench(poly *r, const poly *a);
void kpqc_final_poly_basemul_for_bench(poly *r, const poly *a,
                                       const poly *b);
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
static poly g_finv_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_fused[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_fused[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_fused_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_fused_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_prepare2_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_prepare2_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_prepare2_slothy[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_prepare2_slothy[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_full_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_full_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_prepare2_paper[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_prepare2_paper[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_paper_full_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_paper_full_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_kpqc[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_kpqc[NINPUTS] __attribute__((aligned(64)));
static poly g_fproduct_kpqc[NINPUTS] __attribute__((aligned(64)));
static poly g_gproduct_kpqc[NINPUTS] __attribute__((aligned(64)));
static poly g_h[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv[NINPUTS] __attribute__((aligned(64)));
static poly g_h_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_h_fused[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_fused[NINPUTS] __attribute__((aligned(64)));
static poly g_h_fused_asm[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_fused_asm[NINPUTS] __attribute__((aligned(64)));
static int16_t g_fden[NINPUTS][GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_gden[NINPUTS][GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_fden_current[NINPUTS][GT_DEN_WORDS]
    __attribute__((aligned(64)));
static int16_t g_gden_current[NINPUTS][GT_DEN_WORDS]
    __attribute__((aligned(64)));
static int16_t g_fden_candidate[NINPUTS][GT_DEN_WORDS]
    __attribute__((aligned(64)));
static int16_t g_gden_candidate[NINPUTS][GT_DEN_WORDS]
    __attribute__((aligned(64)));
static uint8_t g_h_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_h_candidate_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_candidate_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_h_fused_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_fused_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_h_fused_asm_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_fused_asm_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static poly g_work0 __attribute__((aligned(64)));
static poly g_work1 __attribute__((aligned(64)));
static poly g_prepare_num0 __attribute__((aligned(64)));
static poly g_prepare_num1 __attribute__((aligned(64)));
static int16_t g_prepare_den0[GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_prepare_den1[GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_prepare_c01_0[8 * GT_DEN_LANES]
    __attribute__((aligned(64)));
static int16_t g_prepare_c01_1[8 * GT_DEN_LANES]
    __attribute__((aligned(64)));
static int16_t g_prepare_group0[8 * GT_DEN_LANES]
    __attribute__((aligned(64)));
static int16_t g_prepare_group1[8 * GT_DEN_LANES]
    __attribute__((aligned(64)));
static const int16_t g_prepare_consts[8] __attribute__((aligned(16))) = {
    3457, 19412, -12929, -147, -1393, -682, -6464, 0};
static int16_t g_den_work0[GT_DEN_WORDS] __attribute__((aligned(64)));
static int16_t g_den_work1[GT_DEN_WORDS] __attribute__((aligned(64)));
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

static int den_mismatches(const int16_t *a, const int16_t *b)
{
  int mismatches = 0;

  for (size_t i = 0; i < GT_DEN_WORDS; i++)
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

static void prepare_one(size_t i)
{
  poly fnum;
  poly gnum;

  if (make_invertible_secret(&g_f[i], &g_finv[i]) ||
      make_invertible_secret(&g_g[i], &g_ginv[i]))
  {
    fprintf(stderr, "failed to generate invertible keygen inputs\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_tree_candidate(
          &g_finv_candidate[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_tree_candidate(
          &g_ginv_candidate[i], &g_g[i]))
  {
    fprintf(stderr, "hier_k8 tree candidate failed on prepared input\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_prepare_fused_candidate(
          &g_finv_fused[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_prepare_fused_candidate(
          &g_ginv_fused[i], &g_g[i]))
  {
    fprintf(stderr, "hier_k8 prepare-fused candidate failed on input\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate(
          &g_finv_fused_asm[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate(
          &g_ginv_fused_asm[i], &g_g[i]))
  {
    fprintf(stderr, "hier_k8 prepare-fused ASM candidate failed on input\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate(
          &g_finv_prepare2_asm[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate(
          &g_ginv_prepare2_asm[i], &g_g[i]))
  {
    fprintf(stderr, "hier_k8 prepare2-fused ASM candidate failed on input\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_prepare2_slothy_candidate(
          &g_finv_prepare2_slothy[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_prepare2_slothy_candidate(
          &g_ginv_prepare2_slothy[i], &g_g[i]))
  {
    int kind = 0;
    int index = 0;
    int16_t baseline = 0;
    int16_t candidate = 0;

    (void)baseinv_prepare_hier_k8_prepare2_slothy_diff_for_bench(
        &g_f[i], &kind, &index, &baseline, &candidate);
    fprintf(stderr,
            "hier_k8 prepare2 Slothy candidate failed: input=%zu "
            "buffer_kind=%d index=%d baseline=%d candidate=%d\n",
            i, kind, index, baseline, candidate);
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_full_asm_candidate(
          &g_finv_full_asm[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_full_asm_candidate(
          &g_ginv_full_asm[i], &g_g[i]))
  {
    fprintf(stderr, "complete hier_k8 ASM candidate failed on input\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_prepare2_slothy_paper_candidate(
          &g_finv_prepare2_paper[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_prepare2_slothy_paper_candidate(
          &g_ginv_prepare2_paper[i], &g_g[i]))
  {
    fprintf(stderr, "prepare2 Slothy plus paper-k8 candidate failed\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate(
          &g_finv_paper_full_asm[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate(
          &g_ginv_paper_full_asm[i], &g_g[i]))
  {
    fprintf(stderr, "complete paper-HIER_K8 ASM candidate failed\n");
    exit(1);
  }

  if (kpqc_final_poly_baseinv_for_bench(&g_finv_kpqc[i], &g_f[i]) ||
      kpqc_final_poly_baseinv_for_bench(&g_ginv_kpqc[i], &g_g[i]))
  {
    fprintf(stderr, "KPQC-final baseinv failed on GT-shaped raw input\n");
    exit(1);
  }
  kpqc_final_poly_basemul_for_bench(&g_fproduct_kpqc[i], &g_f[i],
                                    &g_finv_kpqc[i]);
  kpqc_final_poly_basemul_for_bench(&g_gproduct_kpqc[i], &g_g[i],
                                    &g_ginv_kpqc[i]);

  poly_basemul_scaled_r_input(&g_h[i], &g_g[i], &g_finv[i]);
  poly_basemul_scaled_r_input(&g_hinv[i], &g_f[i], &g_ginv[i]);
  poly_basemul_scaled_r_input(&g_h_candidate[i], &g_g[i],
                              &g_finv_candidate[i]);
  poly_basemul_scaled_r_input(&g_hinv_candidate[i], &g_f[i],
                              &g_ginv_candidate[i]);
  poly_basemul_scaled_r_input(&g_h_fused[i], &g_g[i], &g_finv_fused[i]);
  poly_basemul_scaled_r_input(&g_hinv_fused[i], &g_f[i], &g_ginv_fused[i]);
  poly_basemul_scaled_r_input(&g_h_fused_asm[i], &g_g[i],
                              &g_finv_fused_asm[i]);
  poly_basemul_scaled_r_input(&g_hinv_fused_asm[i], &g_f[i],
                              &g_ginv_fused_asm[i]);
  poly_tobytes(g_h_bytes[i], &g_h[i]);
  poly_tobytes(g_hinv_bytes[i], &g_hinv[i]);
  poly_tobytes(g_h_candidate_bytes[i], &g_h_candidate[i]);
  poly_tobytes(g_hinv_candidate_bytes[i], &g_hinv_candidate[i]);
  poly_tobytes(g_h_fused_bytes[i], &g_h_fused[i]);
  poly_tobytes(g_hinv_fused_bytes[i], &g_hinv_fused[i]);
  poly_tobytes(g_h_fused_asm_bytes[i], &g_h_fused_asm[i]);
  poly_tobytes(g_hinv_fused_asm_bytes[i], &g_hinv_fused_asm[i]);

  if (poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
          &fnum, g_fden[i], &g_f[i]) ||
      poly_baseinv_scaled_r_hier_k8_prepare_for_bench(
          &gnum, g_gden[i], &g_g[i]))
  {
    fprintf(stderr, "hier_k8 prepare failed on prepared input\n");
    exit(1);
  }

  memcpy(g_fden_current[i], g_fden[i], sizeof(g_fden[i]));
  memcpy(g_gden_current[i], g_gden[i], sizeof(g_gden[i]));
  memcpy(g_fden_candidate[i], g_fden[i], sizeof(g_fden[i]));
  memcpy(g_gden_candidate[i], g_gden[i], sizeof(g_gden[i]));

  if (poly_baseinv_scaled_r_hier_k8_tree_for_bench(g_fden_current[i]) ||
      poly_baseinv_scaled_r_hier_k8_tree_for_bench(g_gden_current[i]) ||
      poly_baseinv_scaled_r_hier_k8_tree_candidate_for_bench(
          g_fden_candidate[i]) ||
      poly_baseinv_scaled_r_hier_k8_tree_candidate_for_bench(
          g_gden_candidate[i]))
  {
    fprintf(stderr, "hier_k8 current/candidate tree failed on input\n");
    exit(1);
  }
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
    prepare_one(i);
}

static int run_correctness(void)
{
  poly zero_input = {{0}};
  poly zero_output;
  int total = 0;
  int finv_exact = 0;
  int ginv_exact = 0;
  int h_exact = 0;
  int hinv_exact = 0;
  int h_bytes = 0;
  int hinv_bytes = 0;
  int fden_exact = 0;
  int gden_exact = 0;
  int fused_finv_exact = 0;
  int fused_ginv_exact = 0;
  int fused_h_exact = 0;
  int fused_hinv_exact = 0;
  int fused_h_bytes = 0;
  int fused_hinv_bytes = 0;
  int fused_asm_finv_exact = 0;
  int fused_asm_ginv_exact = 0;
  int fused_asm_h_exact = 0;
  int fused_asm_hinv_exact = 0;
  int fused_asm_h_bytes = 0;
  int fused_asm_hinv_bytes = 0;
  int kpqc_product_mismatches = 0;
  int prepare2_finv_exact = 0;
  int prepare2_ginv_exact = 0;
  int prepare2_slothy_finv_exact = 0;
  int prepare2_slothy_ginv_exact = 0;
  int full_asm_finv_exact = 0;
  int full_asm_ginv_exact = 0;
  int full_asm_zero_failure_mismatches = 0;
  int prepare2_paper_zero_failure_mismatches = 0;
  int prepare2_paper_finv_exact = 0;
  int prepare2_paper_ginv_exact = 0;
  int paper_full_asm_zero_failure_mismatches = 0;
  int paper_full_asm_finv_exact = 0;
  int paper_full_asm_ginv_exact = 0;

  memset(&zero_output, 0x5a, sizeof(zero_output));
  full_asm_zero_failure_mismatches +=
      poly_baseinv_scaled_r_hier_k8_full_asm_candidate(&zero_output,
                                                       &zero_input) != 1;
  for (size_t i = 0; i < NTRUPLUS_N; i++)
    full_asm_zero_failure_mismatches += zero_output.coeffs[i] != 0;

  memset(&zero_output, 0x5a, sizeof(zero_output));
  prepare2_paper_zero_failure_mismatches +=
      poly_baseinv_scaled_r_hier_k8_prepare2_slothy_paper_candidate(
          &zero_output, &zero_input) != 1;
  for (size_t i = 0; i < NTRUPLUS_N; i++)
    prepare2_paper_zero_failure_mismatches += zero_output.coeffs[i] != 0;

  memset(&zero_output, 0x5a, sizeof(zero_output));
  paper_full_asm_zero_failure_mismatches +=
      poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate(
          &zero_output, &zero_input) != 1;
  for (size_t i = 0; i < NTRUPLUS_N; i++)
    paper_full_asm_zero_failure_mismatches += zero_output.coeffs[i] != 0;

  for (size_t i = 0; i < NVALID_ORACLE; i++)
  {
    const size_t slot = i % NINPUTS;

    finv_exact += poly_exact_mismatches(&g_finv[slot],
                                        &g_finv_candidate[slot]);
    ginv_exact += poly_exact_mismatches(&g_ginv[slot],
                                        &g_ginv_candidate[slot]);
    h_exact += poly_exact_mismatches(&g_h[slot], &g_h_candidate[slot]);
    hinv_exact += poly_exact_mismatches(&g_hinv[slot],
                                        &g_hinv_candidate[slot]);
    h_bytes += byte_mismatches(g_h_bytes[slot], g_h_candidate_bytes[slot],
                               NTRUPLUS_POLYBYTES);
    hinv_bytes += byte_mismatches(g_hinv_bytes[slot],
                                  g_hinv_candidate_bytes[slot],
                                  NTRUPLUS_POLYBYTES);
    fden_exact += den_mismatches(g_fden_current[slot],
                                 g_fden_candidate[slot]);
    gden_exact += den_mismatches(g_gden_current[slot],
                                 g_gden_candidate[slot]);
    fused_finv_exact += poly_exact_mismatches(&g_finv[slot],
                                              &g_finv_fused[slot]);
    fused_ginv_exact += poly_exact_mismatches(&g_ginv[slot],
                                              &g_ginv_fused[slot]);
    fused_h_exact += poly_exact_mismatches(&g_h[slot], &g_h_fused[slot]);
    fused_hinv_exact += poly_exact_mismatches(&g_hinv[slot],
                                              &g_hinv_fused[slot]);
    fused_h_bytes += byte_mismatches(g_h_bytes[slot], g_h_fused_bytes[slot],
                                     NTRUPLUS_POLYBYTES);
    fused_hinv_bytes += byte_mismatches(g_hinv_bytes[slot],
                                        g_hinv_fused_bytes[slot],
                                        NTRUPLUS_POLYBYTES);
    fused_asm_finv_exact += poly_exact_mismatches(&g_finv[slot],
                                                  &g_finv_fused_asm[slot]);
    fused_asm_ginv_exact += poly_exact_mismatches(&g_ginv[slot],
                                                  &g_ginv_fused_asm[slot]);
    fused_asm_h_exact += poly_exact_mismatches(&g_h[slot],
                                               &g_h_fused_asm[slot]);
    fused_asm_hinv_exact += poly_exact_mismatches(&g_hinv[slot],
                                                  &g_hinv_fused_asm[slot]);
    fused_asm_h_bytes += byte_mismatches(g_h_bytes[slot],
                                         g_h_fused_asm_bytes[slot],
                                         NTRUPLUS_POLYBYTES);
    fused_asm_hinv_bytes += byte_mismatches(g_hinv_bytes[slot],
                                            g_hinv_fused_asm_bytes[slot],
                                            NTRUPLUS_POLYBYTES);
    prepare2_finv_exact += poly_exact_mismatches(&g_finv[slot],
                                                 &g_finv_prepare2_asm[slot]);
    prepare2_ginv_exact += poly_exact_mismatches(&g_ginv[slot],
                                                 &g_ginv_prepare2_asm[slot]);
    prepare2_slothy_finv_exact +=
        poly_exact_mismatches(&g_finv[slot],
                              &g_finv_prepare2_slothy[slot]);
    prepare2_slothy_ginv_exact +=
        poly_exact_mismatches(&g_ginv[slot],
                              &g_ginv_prepare2_slothy[slot]);
    full_asm_finv_exact +=
        poly_exact_mismatches(&g_finv[slot], &g_finv_full_asm[slot]);
    full_asm_ginv_exact +=
        poly_exact_mismatches(&g_ginv[slot], &g_ginv_full_asm[slot]);
    prepare2_paper_finv_exact +=
        poly_exact_mismatches(&g_finv[slot], &g_finv_prepare2_paper[slot]);
    prepare2_paper_ginv_exact +=
        poly_exact_mismatches(&g_ginv[slot], &g_ginv_prepare2_paper[slot]);
    paper_full_asm_finv_exact +=
        poly_exact_mismatches(&g_finv[slot], &g_finv_paper_full_asm[slot]);
    paper_full_asm_ginv_exact +=
        poly_exact_mismatches(&g_ginv[slot], &g_ginv_paper_full_asm[slot]);
    for (size_t block = 0; block < 24; block++)
    {
      const size_t offset = 32 * block;

      for (size_t lane = 0; lane < 8; lane++)
      {
        kpqc_product_mismatches +=
            g_fproduct_kpqc[slot].coeffs[offset + lane] != 1;
        kpqc_product_mismatches +=
            g_gproduct_kpqc[slot].coeffs[offset + lane] != 1;
      }
      for (size_t lane = 8; lane < 32; lane++)
      {
        kpqc_product_mismatches +=
            g_fproduct_kpqc[slot].coeffs[offset + lane] != 0;
        kpqc_product_mismatches +=
            g_gproduct_kpqc[slot].coeffs[offset + lane] != 0;
      }
    }
  }

  total = finv_exact + ginv_exact + h_exact + hinv_exact + h_bytes +
          hinv_bytes + fden_exact + gden_exact + fused_finv_exact +
          fused_ginv_exact + fused_h_exact + fused_hinv_exact +
          fused_h_bytes + fused_hinv_bytes + fused_asm_finv_exact +
          fused_asm_ginv_exact + fused_asm_h_exact + fused_asm_hinv_exact +
          fused_asm_h_bytes + fused_asm_hinv_bytes + kpqc_product_mismatches +
          prepare2_finv_exact + prepare2_ginv_exact +
          prepare2_slothy_finv_exact + prepare2_slothy_ginv_exact +
          full_asm_finv_exact + full_asm_ginv_exact +
          full_asm_zero_failure_mismatches +
          prepare2_paper_zero_failure_mismatches +
          prepare2_paper_finv_exact + prepare2_paper_ginv_exact +
          paper_full_asm_zero_failure_mismatches +
          paper_full_asm_finv_exact + paper_full_asm_ginv_exact;

  printf("oracle,oracle_current_hier_k8=1\n");
  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("tree_candidate_finv_exact_mismatches=%d\n", finv_exact);
  printf("tree_candidate_ginv_exact_mismatches=%d\n", ginv_exact);
  printf("tree_candidate_h_exact_mismatches=%d\n", h_exact);
  printf("tree_candidate_hinv_exact_mismatches=%d\n", hinv_exact);
  printf("tree_candidate_h_bytes_mismatches=%d\n", h_bytes);
  printf("tree_candidate_hinv_bytes_mismatches=%d\n", hinv_bytes);
  printf("tree_candidate_fden_exact_mismatches=%d\n", fden_exact);
  printf("tree_candidate_gden_exact_mismatches=%d\n", gden_exact);
  printf("prepare_fused_finv_exact_mismatches=%d\n", fused_finv_exact);
  printf("prepare_fused_ginv_exact_mismatches=%d\n", fused_ginv_exact);
  printf("prepare_fused_h_exact_mismatches=%d\n", fused_h_exact);
  printf("prepare_fused_hinv_exact_mismatches=%d\n", fused_hinv_exact);
  printf("prepare_fused_h_bytes_mismatches=%d\n", fused_h_bytes);
  printf("prepare_fused_hinv_bytes_mismatches=%d\n", fused_hinv_bytes);
  printf("prepare_fused_asm_finv_exact_mismatches=%d\n",
         fused_asm_finv_exact);
  printf("prepare_fused_asm_ginv_exact_mismatches=%d\n",
         fused_asm_ginv_exact);
  printf("prepare_fused_asm_h_exact_mismatches=%d\n", fused_asm_h_exact);
  printf("prepare_fused_asm_hinv_exact_mismatches=%d\n",
         fused_asm_hinv_exact);
  printf("prepare_fused_asm_h_bytes_mismatches=%d\n", fused_asm_h_bytes);
  printf("prepare_fused_asm_hinv_bytes_mismatches=%d\n",
         fused_asm_hinv_bytes);
  printf("kpqc_final_product_identity_mismatches=%d\n",
         kpqc_product_mismatches);
  printf("prepare2_fused_asm_finv_exact_mismatches=%d\n",
         prepare2_finv_exact);
  printf("prepare2_fused_asm_ginv_exact_mismatches=%d\n",
         prepare2_ginv_exact);
  printf("prepare2_slothy_finv_exact_mismatches=%d\n",
         prepare2_slothy_finv_exact);
  printf("prepare2_slothy_ginv_exact_mismatches=%d\n",
         prepare2_slothy_ginv_exact);
  printf("full_asm_finv_exact_mismatches=%d\n", full_asm_finv_exact);
  printf("full_asm_ginv_exact_mismatches=%d\n", full_asm_ginv_exact);
  printf("full_asm_zero_failure_mismatches=%d\n",
         full_asm_zero_failure_mismatches);
  printf("prepare2_paper_zero_failure_mismatches=%d\n",
         prepare2_paper_zero_failure_mismatches);
  printf("prepare2_paper_finv_exact_mismatches=%d\n",
         prepare2_paper_finv_exact);
  printf("prepare2_paper_ginv_exact_mismatches=%d\n",
         prepare2_paper_ginv_exact);
  printf("paper_full_asm_zero_failure_mismatches=%d\n",
         paper_full_asm_zero_failure_mismatches);
  printf("paper_full_asm_finv_exact_mismatches=%d\n",
         paper_full_asm_finv_exact);
  printf("paper_full_asm_ginv_exact_mismatches=%d\n",
         paper_full_asm_ginv_exact);
  printf("baseinv_hier_k8_tree_candidate_correctness,total_mismatches=%d\n",
         total);

  return total;
}

static NOINLINE void target_current_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r(&g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r(&g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_candidate_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_prepare_fused_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_prepare_fused_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_prepare_fused_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_prepare_fused_asm_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_prepare_fused_asm_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_kpqc_final_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)kpqc_final_poly_baseinv_for_bench(&g_work0, &g_f[input_idx]);
  (void)kpqc_final_poly_baseinv_for_bench(&g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_prepare2_fused_asm_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_prepare2_fused_asm_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_prepare2_slothy_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_prepare2_slothy_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_prepare2_slothy_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_full_asm_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_full_asm_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_full_asm_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_prepare2_paper_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_prepare2_slothy_paper_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_prepare2_slothy_paper_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_paper_full_asm_hier_k8_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_prepare2_fused_asm_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  baseinv_prepare_hier_k8_group_products_prepare2_asm(
      g_prepare_num0.coeffs, g_prepare_den0, g_prepare_c01_0,
      g_prepare_group0, g_f[input_idx].coeffs, &gt_rowbitrev_lambda[0][0],
      g_prepare_consts);
  baseinv_prepare_hier_k8_group_products_prepare2_asm(
      g_prepare_num1.coeffs, g_prepare_den1, g_prepare_c01_1,
      g_prepare_group1, g_g[input_idx].coeffs, &gt_rowbitrev_lambda[0][0],
      g_prepare_consts);
  g_sink ^= (uint16_t)g_prepare_num0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_prepare_group1[(idx + 17) % (8 * GT_DEN_LANES)];
}

static NOINLINE void target_prepare2_slothy_asm_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm(
      g_prepare_num0.coeffs, g_prepare_den0, g_prepare_c01_0,
      g_prepare_group0, g_f[input_idx].coeffs, &gt_rowbitrev_lambda[0][0],
      g_prepare_consts);
  baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm(
      g_prepare_num1.coeffs, g_prepare_den1, g_prepare_c01_1,
      g_prepare_group1, g_g[input_idx].coeffs, &gt_rowbitrev_lambda[0][0],
      g_prepare_consts);
  g_sink ^= (uint16_t)g_prepare_num0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_prepare_group1[(idx + 17) % (8 * GT_DEN_LANES)];
}

static NOINLINE void target_current_tree_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  memcpy(g_den_work0, g_fden[input_idx], sizeof(g_den_work0));
  memcpy(g_den_work1, g_gden[input_idx], sizeof(g_den_work1));
  (void)poly_baseinv_scaled_r_hier_k8_tree_for_bench(g_den_work0);
  (void)poly_baseinv_scaled_r_hier_k8_tree_for_bench(g_den_work1);
  g_sink ^= (uint16_t)g_den_work0[idx % GT_DEN_WORDS];
  g_sink ^= (uint16_t)g_den_work1[(idx + 23) % GT_DEN_WORDS];
}

static NOINLINE void target_candidate_tree_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  memcpy(g_den_work0, g_fden[input_idx], sizeof(g_den_work0));
  memcpy(g_den_work1, g_gden[input_idx], sizeof(g_den_work1));
  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate_for_bench(g_den_work0);
  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate_for_bench(g_den_work1);
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
         ",instr_p50=%" PRIu64 "\n",
         variant->name, p50, cycles[0], cycles[NTESTS - 1], p75 - p25,
         instructions[NTESTS / 2]);
}

static void run_pmu(void)
{
  static const struct variant variants[] = {
      {"prepare2_fused_asm_x2", target_prepare2_fused_asm_x2},
      {"prepare2_slothy_asm_x2", target_prepare2_slothy_asm_x2},
      {"baseinv_scaled_x2_current_hier_k8",
       target_current_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_tree_candidate",
       target_candidate_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_prepare_fused_candidate",
       target_prepare_fused_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_prepare_fused_asm_candidate",
       target_prepare_fused_asm_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_prepare2_fused_asm_candidate",
       target_prepare2_fused_asm_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_prepare2_slothy_candidate",
       target_prepare2_slothy_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_hier_k8_full_asm_candidate",
       target_full_asm_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_prepare2_slothy_paper_candidate",
       target_prepare2_paper_hier_k8_baseinv_x2},
      {"baseinv_scaled_x2_paper_full_asm_candidate",
       target_paper_full_asm_hier_k8_baseinv_x2},
      {"kpqc_final_baseinv_x2", target_kpqc_final_baseinv_x2},
      {"hier_k8_tree_current_x2", target_current_tree_x2},
      {"hier_k8_tree_candidate_x2", target_candidate_tree_x2},
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
