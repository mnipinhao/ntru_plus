/*
 * Same-binary differential and PMU harness for the benchmark-only hier_k8
 * scaled-baseinv candidate.
 */
#if !defined(__linux__)
#error "bench_gt_baseinv_hier_k8_diff requires Linux perf_event_open"
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
#include "NO_CE/fips202.h"
#include "params.h"
#include "poly.h"
#include "randombytes.h"
#include "symmetric.h"

#ifndef NTESTS
#define NTESTS 21
#endif

#ifndef NITERATIONS
#define NITERATIONS 1000
#endif

#ifndef NWARMUP
#define NWARMUP 50
#endif

#ifndef NINPUTS
#define NINPUTS 64
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
int bench_crypto_kem_keypair_hier_k8(uint8_t *pk, uint8_t *sk);

int poly_baseinv_scaled_r_current_reference(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_candidate(poly *r, const poly *a);
int poly_baseinv_scaled_r_fqinv16_reference(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_fqinv16_candidate(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);

typedef int (*baseinv_fn)(poly *r, const poly *a);
typedef void (*bench_target_fn)(size_t idx);

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
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

struct poly_diff
{
  uint64_t modq_mismatches;
  uint64_t exact_mismatches;
  int first_modq_idx;
  int first_exact_idx;
  int16_t first_modq_a;
  int16_t first_modq_b;
  int16_t first_exact_a;
  int16_t first_exact_b;
};

struct byte_diff
{
  uint64_t mismatches;
  int first_idx;
  uint8_t first_a;
  uint8_t first_b;
};

static poly g_baseinv_inputs[NINPUTS] __attribute__((aligned(64)));
static poly g_poly_out0 __attribute__((aligned(64)));
static poly g_poly_out1 __attribute__((aligned(64)));
static uint8_t g_pk0[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_pk1[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk0[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk1[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_ct[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ss0[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss1[CRYPTO_BYTES] __attribute__((aligned(64)));
static volatile uint64_t g_sink;
static uint64_t g_rng_state;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1},
};

static int g_leader_fd = -1;

static const char *canon_mode(void)
{
#if defined(GT_BASEINV_HIER_K8_OUTPUT_CANON)
  return "output_canon";
#elif defined(GT_BASEINV_HIER_K8_EACH_INV_CANON)
  return "each_inv_canon";
#else
  return "no_canon";
#endif
}

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
  return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

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
  {
    if ((i & 3) == 0)
      g_rng_state ^= (uint64_t)deterministic_u32() << 17;
    out[i] = (uint8_t)(deterministic_u32() >> ((i & 3) * 8));
  }
}

static int32_t modq_i32(int32_t x)
{
  x %= NTRUPLUS_Q;
  if (x < 0)
    x += NTRUPLUS_Q;
  return x;
}

static int modq_equal_i16(int16_t a, int16_t b)
{
  return modq_i32((int32_t)a - (int32_t)b) == 0;
}

static int compare_bytes(const uint8_t *a, const uint8_t *b, size_t n,
                         struct byte_diff *out)
{
  memset(out, 0, sizeof(*out));
  out->first_idx = -1;

  for (size_t i = 0; i < n; i++)
  {
    if (a[i] == b[i])
      continue;
    if (out->first_idx < 0)
    {
      out->first_idx = (int)i;
      out->first_a = a[i];
      out->first_b = b[i];
    }
    out->mismatches++;
  }

  return out->mismatches != 0;
}

static void collect_poly_diff(const poly *a, const poly *b,
                              struct poly_diff *out)
{
  memset(out, 0, sizeof(*out));
  out->first_modq_idx = -1;
  out->first_exact_idx = -1;

  for (int i = 0; i < NTRUPLUS_N; i++)
  {
    if (!modq_equal_i16(a->coeffs[i], b->coeffs[i]))
    {
      if (out->first_modq_idx < 0)
      {
        out->first_modq_idx = i;
        out->first_modq_a = a->coeffs[i];
        out->first_modq_b = b->coeffs[i];
      }
      out->modq_mismatches++;
    }
    if (a->coeffs[i] != b->coeffs[i])
    {
      if (out->first_exact_idx < 0)
      {
        out->first_exact_idx = i;
        out->first_exact_a = a->coeffs[i];
        out->first_exact_b = b->coeffs[i];
      }
      out->exact_mismatches++;
    }
  }
}

static void compare_poly_stage(const char *name, const poly *a, const poly *b,
                               struct poly_diff *out)
{
  collect_poly_diff(a, b, out);

  printf("stage_poly,%s,modq_mismatches=%" PRIu64
         ",exact_mismatches=%" PRIu64
         ",first_modq_idx=%d,first_modq_current=%d,"
         "first_modq_candidate=%d,first_exact_idx=%d,"
         "first_exact_current=%d,first_exact_candidate=%d\n",
         name, out->modq_mismatches, out->exact_mismatches,
         out->first_modq_idx, out->first_modq_a, out->first_modq_b,
         out->first_exact_idx, out->first_exact_a, out->first_exact_b);
}

static void print_byte_stage(const char *name, const uint8_t *a,
                             const uint8_t *b, size_t n)
{
  struct byte_diff diff;

  compare_bytes(a, b, n, &diff);
  printf("stage_bytes,%s,mismatches=%" PRIu64
         ",first_idx=%d,first_current=%u,first_candidate=%u\n",
         name, diff.mismatches, diff.first_idx, diff.first_a, diff.first_b);
}

static void sample_f_from_coins(poly *f, const uint8_t coins[32])
{
  uint8_t buf[NTRUPLUS_N / 4];

  shake256(buf, sizeof(buf), coins, 32);
  poly_cbd1(f, buf);
  poly_triple(f, f);
  f->coeffs[0] += 1;
  poly_ntt(f, f);
}

static void sample_g_from_coins(poly *g, const uint8_t coins[32])
{
  uint8_t buf[NTRUPLUS_N / 4];

  shake256(buf, sizeof(buf), coins, 32);
  poly_cbd1(g, buf);
  poly_triple(g, g);
  poly_ntt(g, g);
}

static int prepare_keygen_polys(poly *f, poly *finv_current,
                                poly *finv_candidate, poly *g,
                                poly *ginv_current, poly *ginv_candidate,
                                uint8_t fcoins[32], uint8_t gcoins[32])
{
  int current_ret;
  int candidate_ret;

  for (;;)
  {
    randombytes(fcoins, 32);
    sample_f_from_coins(f, fcoins);
    current_ret = poly_baseinv_scaled_r_current_reference(finv_current, f);
    candidate_ret = poly_baseinv_scaled_r_hier_k8_candidate(finv_candidate, f);
    if (current_ret == 0)
      break;
  }
  if (candidate_ret != current_ret)
    return 1;

  for (;;)
  {
    randombytes(gcoins, 32);
    sample_g_from_coins(g, gcoins);
    current_ret = poly_baseinv_scaled_r_current_reference(ginv_current, g);
    candidate_ret = poly_baseinv_scaled_r_hier_k8_candidate(ginv_candidate, g);
    if (current_ret == 0)
      break;
  }

  return candidate_ret != current_ret;
}

static int prepare_baseinv_inputs(void)
{
  uint32_t state = 0x9e3779b9u;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    for (int attempt = 0; attempt < 10000; attempt++)
    {
      for (int i = 0; i < NTRUPLUS_N; i++)
      {
        state = state * 1664525u + 1013904223u;
        int32_t v = (int32_t)(state % NTRUPLUS_Q);
        if (v > NTRUPLUS_Q / 2)
          v -= NTRUPLUS_Q;
        g_baseinv_inputs[input].coeffs[i] = (int16_t)v;
      }
      if (poly_baseinv_scaled_r_current_reference(&g_poly_out0,
                                                  &g_baseinv_inputs[input]) ==
          0)
        break;
      if (attempt == 9999)
        return 1;
    }
  }

  return 0;
}

static uint64_t run_baseinv_ab(baseinv_fn current, baseinv_fn candidate,
                               const char *name)
{
  uint64_t mismatches = 0;
  uint64_t exact = 0;
  uint64_t modq = 0;
  int first_input = -1;
  struct poly_diff first_diff;
  struct poly_diff diff;

  memset(&first_diff, 0, sizeof(first_diff));
  first_diff.first_modq_idx = -1;
  first_diff.first_exact_idx = -1;

  for (size_t input = 0; input < NINPUTS; input++)
  {
    int ret0 = current(&g_poly_out0, &g_baseinv_inputs[input]);
    int ret1 = candidate(&g_poly_out1, &g_baseinv_inputs[input]);

    if (ret0 != ret1)
    {
      mismatches++;
      if (first_input < 0)
        first_input = (int)input;
      continue;
    }
    if (ret0 != 0)
      continue;
    collect_poly_diff(&g_poly_out0, &g_poly_out1, &diff);
    modq += diff.modq_mismatches;
    exact += diff.exact_mismatches;
    if ((diff.modq_mismatches || diff.exact_mismatches) && first_input < 0)
    {
      first_input = (int)input;
      first_diff = diff;
    }
  }

  printf("baseinv_ab,%s,ret_mismatches=%" PRIu64
         ",modq_mismatches=%" PRIu64
         ",exact_mismatches=%" PRIu64
         ",first_input=%d,first_modq_idx=%d,first_modq_current=%d,"
         "first_modq_candidate=%d,first_exact_idx=%d,"
         "first_exact_current=%d,first_exact_candidate=%d\n",
         name, mismatches, modq, exact, first_input,
         first_diff.first_modq_idx, first_diff.first_modq_a,
         first_diff.first_modq_b, first_diff.first_exact_idx,
         first_diff.first_exact_a, first_diff.first_exact_b);
  return mismatches + modq;
}

static void run_stage_diff(void)
{
  poly f, g;
  poly finv_current, finv_candidate;
  poly ginv_current, ginv_candidate;
  poly h_current, h_candidate;
  poly hinv_current, hinv_candidate;
  uint8_t fcoins[32];
  uint8_t gcoins[32];
  uint8_t pk_current[CRYPTO_PUBLICKEYBYTES];
  uint8_t pk_candidate[CRYPTO_PUBLICKEYBYTES];
  uint8_t hinv_bytes_current[NTRUPLUS_POLYBYTES];
  uint8_t hinv_bytes_candidate[NTRUPLUS_POLYBYTES];
  uint8_t hash_current[32];
  uint8_t hash_candidate[32];
  struct poly_diff diff;

  randombytes_reset(0x4b455947454eULL);
  if (prepare_keygen_polys(&f, &finv_current, &finv_candidate, &g,
                           &ginv_current, &ginv_candidate, fcoins,
                           gcoins) != 0)
  {
    printf("stage_error,keygen_poly_prepare,ret_mismatch=1\n");
    return;
  }

  compare_poly_stage("baseinv_scaled_f", &finv_current, &finv_candidate,
                     &diff);
  compare_poly_stage("baseinv_scaled_g", &ginv_current, &ginv_candidate,
                     &diff);

  poly_basemul_scaled_r_input(&h_current, &g, &finv_current);
  poly_basemul_scaled_r_input(&h_candidate, &g, &finv_candidate);
  compare_poly_stage("poly_basemul_scaled_r_input_h", &h_current,
                     &h_candidate, &diff);

  poly_basemul_scaled_r_input(&hinv_current, &f, &ginv_current);
  poly_basemul_scaled_r_input(&hinv_candidate, &f, &ginv_candidate);
  compare_poly_stage("poly_basemul_scaled_r_input_hinv", &hinv_current,
                     &hinv_candidate, &diff);

  poly_tobytes(pk_current, &h_current);
  poly_tobytes(pk_candidate, &h_candidate);
  print_byte_stage("poly_tobytes_pk_h", pk_current, pk_candidate,
                   sizeof(pk_current));

  poly_tobytes(hinv_bytes_current, &hinv_current);
  poly_tobytes(hinv_bytes_candidate, &hinv_candidate);
  print_byte_stage("poly_tobytes_sk_hinv", hinv_bytes_current,
                   hinv_bytes_candidate, sizeof(hinv_bytes_current));

  hash_f(hash_current, pk_current);
  hash_f(hash_candidate, pk_candidate);
  print_byte_stage("hash_f_pk", hash_current, hash_candidate,
                   sizeof(hash_current));
  printf("stage_note,invntt,not_applicable=1,path=keygen_scaled_baseinv\n");
}

static void run_kem_byte_diff(void)
{
  struct byte_diff pk_diff;
  struct byte_diff sk_diff;
  struct byte_diff ss_diff;
  int enc_ret;
  int dec_ret;

  randombytes_reset(0x1234567812345678ULL);
  (void)bench_crypto_kem_keypair_current(g_pk0, g_sk0);
  randombytes_reset(0x1234567812345678ULL);
  (void)bench_crypto_kem_keypair_hier_k8(g_pk1, g_sk1);

  compare_bytes(g_pk0, g_pk1, sizeof(g_pk0), &pk_diff);
  compare_bytes(g_sk0, g_sk1, sizeof(g_sk0), &sk_diff);
  printf("kem_byte_diff,pk_mismatches=%" PRIu64
         ",pk_first=%d,pk_current=%u,pk_candidate=%u,"
         "sk_mismatches=%" PRIu64
         ",sk_first=%d,sk_current=%u,sk_candidate=%u\n",
         pk_diff.mismatches, pk_diff.first_idx, pk_diff.first_a,
         pk_diff.first_b, sk_diff.mismatches, sk_diff.first_idx,
         sk_diff.first_a, sk_diff.first_b);

  randombytes_reset(0xabcdef0102030405ULL);
  enc_ret = bench_crypto_kem_enc_current(g_ct, g_ss0, g_pk0);
  dec_ret = bench_crypto_kem_dec_current(g_ss1, g_ct, g_sk0);
  compare_bytes(g_ss0, g_ss1, sizeof(g_ss0), &ss_diff);
  printf("kem_functional,current,enc_ret=%d,dec_ret=%d,ss_mismatches=%" PRIu64
         ",first=%d\n",
         enc_ret, dec_ret, ss_diff.mismatches, ss_diff.first_idx);

  randombytes_reset(0xabcdef0102030405ULL);
  enc_ret = bench_crypto_kem_enc_current(g_ct, g_ss0, g_pk1);
  dec_ret = bench_crypto_kem_dec_current(g_ss1, g_ct, g_sk1);
  compare_bytes(g_ss0, g_ss1, sizeof(g_ss0), &ss_diff);
  printf("kem_functional,hier_k8,enc_ret=%d,dec_ret=%d,ss_mismatches=%" PRIu64
         ",first=%d\n",
         enc_ret, dec_ret, ss_diff.mismatches, ss_diff.first_idx);
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

static NOINLINE void target_baseinv_current(size_t idx)
{
  (void)poly_baseinv_scaled_r_current_reference(
      &g_poly_out0, &g_baseinv_inputs[idx % NINPUTS]);
  g_sink ^= (uint16_t)g_poly_out0.coeffs[(idx + 3) % NTRUPLUS_N];
}

static NOINLINE void target_baseinv_hier_k8(size_t idx)
{
  (void)poly_baseinv_scaled_r_hier_k8_candidate(
      &g_poly_out0, &g_baseinv_inputs[idx % NINPUTS]);
  g_sink ^= (uint16_t)g_poly_out0.coeffs[(idx + 5) % NTRUPLUS_N];
}

static NOINLINE void target_baseinv_fqinv16(size_t idx)
{
  (void)poly_baseinv_scaled_r_fqinv16_reference(
      &g_poly_out0, &g_baseinv_inputs[idx % NINPUTS]);
  g_sink ^= (uint16_t)g_poly_out0.coeffs[(idx + 7) % NTRUPLUS_N];
}

static NOINLINE void target_baseinv_hier_k8_fqinv16(size_t idx)
{
  (void)poly_baseinv_scaled_r_hier_k8_fqinv16_candidate(
      &g_poly_out0, &g_baseinv_inputs[idx % NINPUTS]);
  g_sink ^= (uint16_t)g_poly_out0.coeffs[(idx + 11) % NTRUPLUS_N];
}

static void run_variant_once(const struct variant *variant, size_t idx)
{
  variant->target(idx);
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

  for (size_t i = 0; i < NITERATIONS; i++)
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
    cycles[test] = (double)counts.v[0] / (double)NITERATIONS;
    instr[test] = (double)counts.v[1] / (double)NITERATIONS;
  }

  qsort(cycles, NTESTS, sizeof(cycles[0]), compare_double);
  qsort(instr, NTESTS, sizeof(instr[0]), compare_double);
  printf("pmu,%s,cycles_p50=%.3f,cycles_iqr=%.3f,instr_p50=%.3f,"
         "instr_iqr=%.3f,ipc_p50=%.3f\n",
         variant->name, cycles[NTESTS / 2],
         cycles[(3 * NTESTS) / 4] - cycles[NTESTS / 4],
         instr[NTESTS / 2],
         instr[(3 * NTESTS) / 4] - instr[NTESTS / 4],
         instr[NTESTS / 2] / cycles[NTESTS / 2]);
}

int main(void)
{
  const struct variant variants[] = {
      {"baseinv_scaled_current", target_baseinv_current},
      {"baseinv_scaled_hier_k8_fqinv15_asm", target_baseinv_hier_k8},
      {"baseinv_scaled_fqinv16", target_baseinv_fqinv16},
      {"baseinv_scaled_hier_k8_fqinv16", target_baseinv_hier_k8_fqinv16},
  };

  printf("settings,canon_mode=%s,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,"
         "NINPUTS=%d\n",
         canon_mode(), NTESTS, NITERATIONS, NWARMUP, NINPUTS);

  if (prepare_baseinv_inputs() != 0)
  {
    fprintf(stderr, "failed to prepare invertible baseinv inputs\n");
    return 1;
  }

  (void)run_baseinv_ab(poly_baseinv_scaled_r_current_reference,
                       poly_baseinv_scaled_r_hier_k8_candidate,
                       "current_vs_hier_k8_fqinv15_asm");
  (void)run_baseinv_ab(poly_baseinv_scaled_r_fqinv16_reference,
                       poly_baseinv_scaled_r_hier_k8_fqinv16_candidate,
                       "fqinv16_vs_hier_k8_fqinv16");
  run_kem_byte_diff();
  run_stage_diff();

  if (open_pmu_events() != 0)
  {
    fprintf(stderr, "perf_event_open failed: %s\n", strerror(errno));
    close_pmu_events();
    return 1;
  }

  printf("columns,name,cycles_p50,cycles_iqr,instr_p50,instr_iqr,ipc_p50\n");
  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    summarize_variant(&variants[i]);

  close_pmu_events();
  printf("sink=%" PRIu64 "\n", g_sink);
  return 0;
}
