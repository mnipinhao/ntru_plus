/*
 * Same-binary full-keygen PMU harness for the benchmark-only hier_k8 tree
 * scheduling candidate.
 *
 * The candidate is wired only through bench_kem_hier_k8_tree_candidate_wrapper.c.
 * Production gt_production_default remains unchanged.
 */
#if !defined(__linux__)
#error "bench_gt_baseinv_hier_k8_tree_fullkeygen_pmu requires Linux perf_event_open"
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

#include "api.h"
#include "bench_build_config.h"
#include "params.h"
#include "poly.h"
#include "randombytes.h"

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

#ifndef NKEMDIFF
#define NKEMDIFF 256
#endif

#ifndef NKEYPAIR_ITERATIONS
#define NKEYPAIR_ITERATIONS 100
#endif

#ifndef NKEYPAIR_WARMUP
#define NKEYPAIR_WARMUP 5
#endif

#define PMU_EVENT_COUNT 2

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

int bench_crypto_kem_keypair_current(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_enc_current(uint8_t *ct, uint8_t *ss,
                                 const uint8_t *pk);
int bench_crypto_kem_dec_current(uint8_t *ss, const uint8_t *ct,
                                 const uint8_t *sk);
int bench_crypto_kem_keypair_hier_k8_tree_candidate(uint8_t *pk,
                                                    uint8_t *sk);

int poly_baseinv_scaled_r(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_tree_candidate(poly *r, const poly *a);
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
  size_t iterations;
  size_t warmup;
};

static poly g_f[NINPUTS] __attribute__((aligned(64)));
static poly g_g[NINPUTS] __attribute__((aligned(64)));
static poly g_finv[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_h[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv[NINPUTS] __attribute__((aligned(64)));
static poly g_h_candidate[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_candidate[NINPUTS] __attribute__((aligned(64)));
static uint8_t g_h_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_h_candidate_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_hinv_candidate_bytes[NINPUTS][NTRUPLUS_POLYBYTES]
    __attribute__((aligned(64)));
static poly g_work0 __attribute__((aligned(64)));
static poly g_work1 __attribute__((aligned(64)));
static uint8_t g_pk0[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_pk1[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk0[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk1[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_ct[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ss0[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss1[CRYPTO_BYTES] __attribute__((aligned(64)));
static volatile uint64_t g_sink;
static uint64_t g_rng_state = 1;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1},
};
static int g_leader_fd = -1;

static void randombytes_reset(uint64_t seed)
{
  g_rng_state = seed ? seed : 1;
}

static uint32_t deterministic_u32(void)
{
  g_rng_state = g_rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
  return (uint32_t)(g_rng_state >> 32);
}

void randombytes(uint8_t *out, size_t outlen)
{
  for (size_t i = 0; i < outlen; i++)
    out[i] = (uint8_t)(deterministic_u32() >> ((i & 3) * 8));
}

static uint64_t seed_for_index(size_t idx, uint64_t domain)
{
  return domain ^ (0x9e3779b97f4a7c15ULL * (uint64_t)(idx + 1));
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

static int make_keygen_ntt_secret(poly *a, poly *ainv, int add_one)
{
  uint8_t buf[NTRUPLUS_N / 4];

  for (int attempt = 0; attempt < 10000; attempt++)
  {
    for (size_t i = 0; i < sizeof(buf); i++)
      buf[i] = (uint8_t)(deterministic_u32() >> ((i & 3) * 8));

    poly_cbd1(a, buf);
    poly_triple(a, a);
    if (add_one)
      a->coeffs[0]++;
    poly_ntt(a, a);

    if (poly_baseinv_scaled_r(ainv, a) == 0)
      return 0;
  }

  return 1;
}

static void prepare_one(size_t i)
{
  randombytes_reset(seed_for_index(i, 0x6271736576656e31ULL));
  if (make_keygen_ntt_secret(&g_f[i], &g_finv[i], 1) ||
      make_keygen_ntt_secret(&g_g[i], &g_ginv[i], 0))
  {
    fprintf(stderr, "failed to generate invertible keygen-shaped input\n");
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

  poly_basemul_scaled_r_input(&g_h[i], &g_g[i], &g_finv[i]);
  poly_basemul_scaled_r_input(&g_hinv[i], &g_f[i], &g_ginv[i]);
  poly_basemul_scaled_r_input(&g_h_candidate[i], &g_g[i],
                              &g_finv_candidate[i]);
  poly_basemul_scaled_r_input(&g_hinv_candidate[i], &g_f[i],
                              &g_ginv_candidate[i]);
  poly_tobytes(g_h_bytes[i], &g_h[i]);
  poly_tobytes(g_hinv_bytes[i], &g_hinv[i]);
  poly_tobytes(g_h_candidate_bytes[i], &g_h_candidate[i]);
  poly_tobytes(g_hinv_candidate_bytes[i], &g_hinv_candidate[i]);
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
    prepare_one(i);
}

static int run_baseinv_correctness(void)
{
  int total = 0;
  int finv_exact = 0;
  int ginv_exact = 0;
  int h_exact = 0;
  int hinv_exact = 0;
  int h_bytes = 0;
  int hinv_bytes = 0;

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
  }

  total = finv_exact + ginv_exact + h_exact + hinv_exact + h_bytes +
          hinv_bytes;

  printf("oracle,oracle_current_hier_k8=1\n");
  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("tree_fullkeygen_finv_exact_mismatches=%d\n", finv_exact);
  printf("tree_fullkeygen_ginv_exact_mismatches=%d\n", ginv_exact);
  printf("tree_fullkeygen_h_exact_mismatches=%d\n", h_exact);
  printf("tree_fullkeygen_hinv_exact_mismatches=%d\n", hinv_exact);
  printf("tree_fullkeygen_h_bytes_mismatches=%d\n", h_bytes);
  printf("tree_fullkeygen_hinv_bytes_mismatches=%d\n", hinv_bytes);
  printf("baseinv_hier_k8_tree_fullkeygen_baseinv_correctness,"
         "total_mismatches=%d\n",
         total);

  return total;
}

static int run_kem_correctness(void)
{
  int total = 0;
  int keypair_ret_mismatches = 0;
  int pk_mismatches = 0;
  int sk_mismatches = 0;
  int decap_mismatches = 0;
  int ss_mismatches = 0;

  for (size_t i = 0; i < NKEMDIFF; i++)
  {
    int ret0;
    int ret1;
    int dret;

    randombytes_reset(seed_for_index(i, 0x6b65797061697231ULL));
    ret0 = bench_crypto_kem_keypair_current(g_pk0, g_sk0);
    randombytes_reset(seed_for_index(i, 0x6b65797061697231ULL));
    ret1 = bench_crypto_kem_keypair_hier_k8_tree_candidate(g_pk1, g_sk1);

    keypair_ret_mismatches += ret0 != ret1;
    pk_mismatches += byte_mismatches(g_pk0, g_pk1, sizeof(g_pk0));
    sk_mismatches += byte_mismatches(g_sk0, g_sk1, sizeof(g_sk0));

    randombytes_reset(seed_for_index(i, 0x656e636170737531ULL));
    (void)bench_crypto_kem_enc_current(g_ct, g_ss0, g_pk1);
    dret = bench_crypto_kem_dec_current(g_ss1, g_ct, g_sk1);
    decap_mismatches += dret != 0;
    ss_mismatches += byte_mismatches(g_ss0, g_ss1, sizeof(g_ss0));
  }

  total = keypair_ret_mismatches + pk_mismatches + sk_mismatches +
          decap_mismatches + ss_mismatches;

  printf("kem_correctness,valid_cases=%d\n", NKEMDIFF);
  printf("tree_fullkeygen_keypair_ret_mismatches=%d\n",
         keypair_ret_mismatches);
  printf("tree_fullkeygen_pk_mismatches=%d\n", pk_mismatches);
  printf("tree_fullkeygen_sk_mismatches=%d\n", sk_mismatches);
  printf("tree_fullkeygen_decap_mismatches=%d\n", decap_mismatches);
  printf("tree_fullkeygen_shared_secret_mismatches=%d\n", ss_mismatches);
  printf("baseinv_hier_k8_tree_fullkeygen_kem_correctness,"
         "total_mismatches=%d\n",
         total);

  return total;
}

static NOINLINE void target_current_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r(&g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r(&g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_candidate_baseinv_x2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate(
      &g_work0, &g_f[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate(
      &g_work1, &g_g[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_keypair_current(size_t idx)
{
  randombytes_reset(seed_for_index(idx, 0x3141592653589793ULL));
  (void)bench_crypto_kem_keypair_current(g_pk0, g_sk0);
  g_sink ^= g_pk0[idx % sizeof(g_pk0)];
  g_sink ^= (uint64_t)g_sk0[(idx + 17) % sizeof(g_sk0)] << 8;
}

static NOINLINE void target_keypair_candidate(size_t idx)
{
  randombytes_reset(seed_for_index(idx, 0x3141592653589793ULL));
  (void)bench_crypto_kem_keypair_hier_k8_tree_candidate(g_pk1, g_sk1);
  g_sink ^= g_pk1[idx % sizeof(g_pk1)];
  g_sink ^= (uint64_t)g_sk1[(idx + 19) % sizeof(g_sk1)] << 8;
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

static struct counts measure_once(const struct variant *variant)
{
  uint64_t values[PMU_EVENT_COUNT + 1] = {0};

  ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (size_t i = 0; i < variant->iterations; i++)
    variant->target(i);
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

  for (size_t i = 0; i < variant->warmup; i++)
    variant->target(i);

  for (size_t t = 0; t < NTESTS; t++)
  {
    struct counts c = measure_once(variant);

    cycles[t] = c.cycles / variant->iterations;
    instructions[t] = c.instructions / variant->iterations;
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
      {"keygen_polyinv_scaled_x2_current", target_current_baseinv_x2,
       NITERATIONS, NWARMUP},
      {"keygen_polyinv_scaled_x2_hierk8_tree_candidate",
       target_candidate_baseinv_x2, NITERATIONS, NWARMUP},
      {"full_keygen_current", target_keypair_current, NKEYPAIR_ITERATIONS,
       NKEYPAIR_WARMUP},
      {"full_keygen_hierk8_tree_candidate", target_keypair_candidate,
       NKEYPAIR_ITERATIONS, NKEYPAIR_WARMUP},
  };

  setup_perf_events();
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d,"
         "NKEYPAIR_ITERATIONS=%d,NKEYPAIR_WARMUP=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS, NKEYPAIR_ITERATIONS,
         NKEYPAIR_WARMUP);
  bench_print_gt_production_config();
  printf("experiment,GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE=1\n");

  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    run_one_variant(&variants[i]);

  printf("sink=%" PRIu64 "\n", g_sink);
  close_perf_events();
}

int main(void)
{
  prepare_inputs();
  if (run_baseinv_correctness() != 0)
    return 1;
  if (run_kem_correctness() != 0)
    return 1;

  run_pmu();
  return 0;
}
