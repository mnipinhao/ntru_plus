/*
 * Same-binary PMU/correctness harness for Wave 4 keygen candidates:
 *
 *   current
 *   SAMPLE-DAG Slothy Phase123 input fusion only
 *   hier_k8 tree candidate only
 *   SAMPLE-DAG + hier_k8 tree candidate
 *
 * All candidate calls are benchmark-only.  This file does not change
 * gt_production_default or overwrite generic symbols.
 */
#if !defined(__linux__)
#error "bench_gt_keygen_sample_hierk8_combo_pmu requires Linux perf_event_open"
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
#if defined(SUPPORTS_SHAKE256_ASM)
#include "CE/fips202.h"
#else
#include "NO_CE/fips202.h"
#endif
#include "params.h"
#include "poly.h"
#include "randombytes.h"
#include "symmetric.h"

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
#ifndef NKEYPAIR_ITERATIONS
#define NKEYPAIR_ITERATIONS 100
#endif
#ifndef NKEYPAIR_WARMUP
#define NKEYPAIR_WARMUP 5
#endif
#ifndef NKEYPAIR_VALID
#define NKEYPAIR_VALID 256
#endif

#define PMU_EVENT_COUNT 2
#define SAMPLE_BUF_BYTES (NTRUPLUS_N / 4)

#if defined(__GNUC__) || defined(__clang__)
#define NOINLINE __attribute__((noinline))
#else
#define NOINLINE
#endif

void poly_ntt_mul3(poly *out, const poly *a);
void poly_ntt_mul3_add1(poly *out, const poly *a);
int poly_baseinv_scaled_r(poly *r, const poly *a);
int poly_baseinv_scaled_r_hier_k8_tree_candidate(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
int bench_crypto_kem_keypair_current(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_enc_current(uint8_t *ct, uint8_t *ss,
                                 const uint8_t *pk);
int bench_crypto_kem_dec_current(uint8_t *ss, const uint8_t *ct,
                                 const uint8_t *sk);

typedef void (*bench_target_fn)(size_t idx);

enum keygen_variant
{
  VAR_CURRENT = 0,
  VAR_SAMPLE_DAG,
  VAR_HIERK8,
  VAR_SAMPLE_DAG_HIERK8,
};

struct keygen_material
{
  poly f;
  poly finv;
  poly g;
  poly ginv;
  poly h;
  poly hinv;
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
};

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

static uint8_t g_buf_f[NINPUTS][SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static uint8_t g_buf_g[NINPUTS][SAMPLE_BUF_BYTES] __attribute__((aligned(64)));
static poly g_f_current[NINPUTS] __attribute__((aligned(64)));
static poly g_g_current[NINPUTS] __attribute__((aligned(64)));
static poly g_f_sample[NINPUTS] __attribute__((aligned(64)));
static poly g_g_sample[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_current[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_current[NINPUTS] __attribute__((aligned(64)));
static poly g_finv_hier[NINPUTS] __attribute__((aligned(64)));
static poly g_ginv_hier[NINPUTS] __attribute__((aligned(64)));
static poly g_h_current[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_current[NINPUTS] __attribute__((aligned(64)));
static poly g_h_combo[NINPUTS] __attribute__((aligned(64)));
static poly g_hinv_combo[NINPUTS] __attribute__((aligned(64)));
static uint8_t g_pk0[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_pk1[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk0[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk1[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_kem_pk[NINPUTS][CRYPTO_PUBLICKEYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_kem_sk[NINPUTS][CRYPTO_SECRETKEYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_kem_ct[NINPUTS][CRYPTO_CIPHERTEXTBYTES]
    __attribute__((aligned(64)));
static uint8_t g_kem_ss[NINPUTS][CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ct[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ss0[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss1[CRYPTO_BYTES] __attribute__((aligned(64)));
static poly g_work0 __attribute__((aligned(64)));
static poly g_work1 __attribute__((aligned(64)));
static uint8_t g_work_pk[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_work_sk[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
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

static int use_sample(enum keygen_variant variant)
{
  return variant == VAR_SAMPLE_DAG || variant == VAR_SAMPLE_DAG_HIERK8;
}

static int use_hierk8(enum keygen_variant variant)
{
  return variant == VAR_HIERK8 || variant == VAR_SAMPLE_DAG_HIERK8;
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

static int baseinv_variant(poly *inv, const poly *a, enum keygen_variant variant)
{
  if (use_hierk8(variant))
    return poly_baseinv_scaled_r_hier_k8_tree_candidate(inv, a);
  return poly_baseinv_scaled_r(inv, a);
}

static int genf_derand_variant(poly *f, poly *finv, const uint8_t *coins,
                               enum keygen_variant variant)
{
  uint8_t buf[SAMPLE_BUF_BYTES];

  shake256(buf, sizeof buf, coins, 32);
  poly_cbd1(f, buf);
  if (use_sample(variant))
    poly_ntt_mul3_add1(f, f);
  else
  {
    poly_triple(f, f);
    f->coeffs[0] += 1;
    poly_ntt(f, f);
  }

  return baseinv_variant(finv, f, variant);
}

static int geng_derand_variant(poly *g, poly *ginv, const uint8_t *coins,
                               enum keygen_variant variant)
{
  uint8_t buf[SAMPLE_BUF_BYTES];

  shake256(buf, sizeof buf, coins, 32);
  poly_cbd1(g, buf);
  if (use_sample(variant))
    poly_ntt_mul3(g, g);
  else
  {
    poly_triple(g, g);
    poly_ntt(g, g);
  }

  return baseinv_variant(ginv, g, variant);
}

static void keypair_derand_variant(uint8_t *pk, uint8_t *sk, const poly *f,
                                   const poly *finv, const poly *g,
                                   const poly *ginv, poly *h, poly *hinv)
{
  poly_basemul_scaled_r_input(h, g, finv);
  poly_basemul_scaled_r_input(hinv, f, ginv);

  poly_tobytes(pk, h);
  poly_tobytes(sk, f);
  poly_tobytes(sk + NTRUPLUS_POLYBYTES, hinv);
  hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

static int keypair_material_variant(struct keygen_material *material,
                                    enum keygen_variant variant,
                                    uint64_t seed)
{
  uint8_t coins[NTRUPLUS_SYMBYTES];

  randombytes_reset(seed);
  do
  {
    randombytes(coins, sizeof coins);
  } while (genf_derand_variant(&material->f, &material->finv, coins,
                               variant));

  do
  {
    randombytes(coins, sizeof coins);
  } while (geng_derand_variant(&material->g, &material->ginv, coins,
                               variant));

  keypair_derand_variant(material->pk, material->sk, &material->f,
                         &material->finv, &material->g, &material->ginv,
                         &material->h, &material->hinv);
  return 0;
}

static int keypair_variant(uint8_t *pk, uint8_t *sk,
                           enum keygen_variant variant, uint64_t seed)
{
  struct keygen_material material;

  (void)keypair_material_variant(&material, variant, seed);
  memcpy(pk, material.pk, CRYPTO_PUBLICKEYBYTES);
  memcpy(sk, material.sk, CRYPTO_SECRETKEYBYTES);
  return 0;
}

static void fill_bytes(uint8_t *out, size_t outlen)
{
  for (size_t i = 0; i < outlen; i++)
    out[i] = (uint8_t)(deterministic_u32() >> ((i & 3) * 8));
}

static int make_keygen_ntt_secret(poly *a, poly *ainv, int add_one,
                                  enum keygen_variant variant,
                                  const uint8_t buf[SAMPLE_BUF_BYTES])
{
  poly_cbd1(a, buf);
  if (use_sample(variant))
  {
    if (add_one)
      poly_ntt_mul3_add1(a, a);
    else
      poly_ntt_mul3(a, a);
  }
  else
  {
    poly_triple(a, a);
    if (add_one)
      a->coeffs[0]++;
    poly_ntt(a, a);
  }

  return baseinv_variant(ainv, a, variant);
}

static void prepare_one(size_t i)
{
  randombytes_reset(seed_for_index(i, 0x73616d706c653431ULL));

  for (;;)
  {
    fill_bytes(g_buf_f[i], sizeof(g_buf_f[i]));
    if (make_keygen_ntt_secret(&g_f_current[i], &g_finv_current[i], 1,
                               VAR_CURRENT, g_buf_f[i]) == 0)
      break;
  }

  for (;;)
  {
    fill_bytes(g_buf_g[i], sizeof(g_buf_g[i]));
    if (make_keygen_ntt_secret(&g_g_current[i], &g_ginv_current[i], 0,
                               VAR_CURRENT, g_buf_g[i]) == 0)
      break;
  }

  if (make_keygen_ntt_secret(&g_f_sample[i], &g_work0, 1, VAR_SAMPLE_DAG,
                             g_buf_f[i]) != 0 ||
      make_keygen_ntt_secret(&g_g_sample[i], &g_work1, 0, VAR_SAMPLE_DAG,
                             g_buf_g[i]) != 0)
  {
    fprintf(stderr, "sample DAG changed invertibility on prepared input\n");
    exit(1);
  }

  if (poly_baseinv_scaled_r_hier_k8_tree_candidate(&g_finv_hier[i],
                                                   &g_f_sample[i]) ||
      poly_baseinv_scaled_r_hier_k8_tree_candidate(&g_ginv_hier[i],
                                                   &g_g_sample[i]))
  {
    fprintf(stderr, "hier_k8 tree candidate failed on prepared input\n");
    exit(1);
  }

  poly_basemul_scaled_r_input(&g_h_current[i], &g_g_current[i],
                              &g_finv_current[i]);
  poly_basemul_scaled_r_input(&g_hinv_current[i], &g_f_current[i],
                              &g_ginv_current[i]);
  poly_basemul_scaled_r_input(&g_h_combo[i], &g_g_sample[i],
                              &g_finv_hier[i]);
  poly_basemul_scaled_r_input(&g_hinv_combo[i], &g_f_sample[i],
                              &g_ginv_hier[i]);
}

static void prepare_inputs(void)
{
  for (size_t i = 0; i < NINPUTS; i++)
  {
    prepare_one(i);

    randombytes_reset(seed_for_index(i, 0x6b656d6b65793431ULL));
    (void)bench_crypto_kem_keypair_current(g_kem_pk[i], g_kem_sk[i]);
    randombytes_reset(seed_for_index(i, 0x656e636170343131ULL));
    (void)bench_crypto_kem_enc_current(g_kem_ct[i], g_kem_ss[i],
                                       g_kem_pk[i]);
  }
}

static int run_component_correctness(void)
{
  int sample_f_exact = 0;
  int sample_g_exact = 0;
  int hier_finv_exact = 0;
  int hier_ginv_exact = 0;
  int combo_h_exact = 0;
  int combo_hinv_exact = 0;
  int total;

  for (size_t i = 0; i < NKEYPAIR_VALID; i++)
  {
    const size_t slot = i % NINPUTS;

    sample_f_exact += poly_exact_mismatches(&g_f_current[slot],
                                            &g_f_sample[slot]);
    sample_g_exact += poly_exact_mismatches(&g_g_current[slot],
                                            &g_g_sample[slot]);
    hier_finv_exact += poly_exact_mismatches(&g_finv_current[slot],
                                             &g_finv_hier[slot]);
    hier_ginv_exact += poly_exact_mismatches(&g_ginv_current[slot],
                                             &g_ginv_hier[slot]);
    combo_h_exact += poly_exact_mismatches(&g_h_current[slot],
                                           &g_h_combo[slot]);
    combo_hinv_exact += poly_exact_mismatches(&g_hinv_current[slot],
                                              &g_hinv_combo[slot]);
  }

  total = sample_f_exact + sample_g_exact + hier_finv_exact +
          hier_ginv_exact + combo_h_exact + combo_hinv_exact;

  printf("correctness,valid_cases=%d\n", NVALID_ORACLE);
  printf("sample_dag_f_exact_mismatches=%d\n", sample_f_exact);
  printf("sample_dag_g_exact_mismatches=%d\n", sample_g_exact);
  printf("hierk8_finv_exact_mismatches=%d\n", hier_finv_exact);
  printf("hierk8_ginv_exact_mismatches=%d\n", hier_ginv_exact);
  printf("combo_h_exact_mismatches=%d\n", combo_h_exact);
  printf("combo_hinv_exact_mismatches=%d\n", combo_hinv_exact);
  printf("sample_hierk8_combo_component_correctness,total_mismatches=%d\n",
         total);

  return total;
}

static int run_keypair_correctness(void)
{
  int sample_pk = 0;
  int sample_sk = 0;
  int hier_pk = 0;
  int hier_sk = 0;
  int combo_pk = 0;
  int combo_sk = 0;
  int combo_h = 0;
  int combo_hinv = 0;
  int total;

  for (size_t i = 0; i < NVALID_ORACLE; i++)
  {
    struct keygen_material cur;
    struct keygen_material sample;
    struct keygen_material hier;
    struct keygen_material combo;
    uint64_t seed = seed_for_index(i, 0x6b65797061697234ULL);

    keypair_material_variant(&cur, VAR_CURRENT, seed);
    keypair_material_variant(&sample, VAR_SAMPLE_DAG, seed);
    keypair_material_variant(&hier, VAR_HIERK8, seed);
    keypair_material_variant(&combo, VAR_SAMPLE_DAG_HIERK8, seed);

    sample_pk += byte_mismatches(cur.pk, sample.pk, sizeof(cur.pk));
    sample_sk += byte_mismatches(cur.sk, sample.sk, sizeof(cur.sk));
    hier_pk += byte_mismatches(cur.pk, hier.pk, sizeof(cur.pk));
    hier_sk += byte_mismatches(cur.sk, hier.sk, sizeof(cur.sk));
    combo_pk += byte_mismatches(cur.pk, combo.pk, sizeof(cur.pk));
    combo_sk += byte_mismatches(cur.sk, combo.sk, sizeof(cur.sk));
    combo_h += poly_exact_mismatches(&cur.h, &combo.h);
    combo_hinv += poly_exact_mismatches(&cur.hinv, &combo.hinv);
  }

  total = sample_pk + sample_sk + hier_pk + hier_sk + combo_pk + combo_sk +
          combo_h + combo_hinv;

  printf("keypair_correctness,valid_cases=%d\n", NKEYPAIR_VALID);
  printf("sample_dag_pk_exact_mismatches=%d\n", sample_pk);
  printf("sample_dag_sk_exact_mismatches=%d\n", sample_sk);
  printf("hierk8_pk_exact_mismatches=%d\n", hier_pk);
  printf("hierk8_sk_exact_mismatches=%d\n", hier_sk);
  printf("combo_pk_exact_mismatches=%d\n", combo_pk);
  printf("combo_sk_exact_mismatches=%d\n", combo_sk);
  printf("combo_keypair_h_exact_mismatches=%d\n", combo_h);
  printf("combo_keypair_hinv_exact_mismatches=%d\n", combo_hinv);
  printf("sample_hierk8_combo_keypair_correctness,total_mismatches=%d\n",
         total);

  return total;
}

static int run_kem_matrix_correctness(void)
{
  int total = 0;
  int combo_keypair_ret_mismatches = 0;
  int combo_keypair_pk_mismatches = 0;
  int combo_keypair_sk_mismatches = 0;
  int combo_decap_mismatches = 0;
  int combo_shared_secret_mismatches = 0;

  for (size_t i = 0; i < NKEYPAIR_VALID; i++)
  {
    uint64_t seed = seed_for_index(i, 0x6b656d636f6d3431ULL);
    int ret0;
    int ret1;
    int dret;

    randombytes_reset(seed);
    ret0 = bench_crypto_kem_keypair_current(g_pk0, g_sk0);
    ret1 = keypair_variant(g_pk1, g_sk1, VAR_SAMPLE_DAG_HIERK8, seed);

    combo_keypair_ret_mismatches += ret0 != ret1;
    combo_keypair_pk_mismatches += byte_mismatches(g_pk0, g_pk1,
                                                   sizeof(g_pk0));
    combo_keypair_sk_mismatches += byte_mismatches(g_sk0, g_sk1,
                                                   sizeof(g_sk0));

    randombytes_reset(seed_for_index(i, 0x656e636170343132ULL));
    (void)bench_crypto_kem_enc_current(g_ct, g_ss0, g_pk1);
    dret = bench_crypto_kem_dec_current(g_ss1, g_ct, g_sk1);
    combo_decap_mismatches += dret != 0;
    combo_shared_secret_mismatches += byte_mismatches(g_ss0, g_ss1,
                                                      sizeof(g_ss0));
  }

  total = combo_keypair_ret_mismatches + combo_keypair_pk_mismatches +
          combo_keypair_sk_mismatches + combo_decap_mismatches +
          combo_shared_secret_mismatches;

  printf("kem_matrix_correctness,valid_cases=%d\n", NKEYPAIR_VALID);
  printf("combo_kem_keypair_ret_mismatches=%d\n",
         combo_keypair_ret_mismatches);
  printf("combo_kem_keypair_pk_mismatches=%d\n",
         combo_keypair_pk_mismatches);
  printf("combo_kem_keypair_sk_mismatches=%d\n",
         combo_keypair_sk_mismatches);
  printf("combo_kem_decap_mismatches=%d\n", combo_decap_mismatches);
  printf("combo_kem_shared_secret_mismatches=%d\n",
         combo_shared_secret_mismatches);
  printf("sample_hierk8_combo_kem_matrix_correctness,total_mismatches=%d\n",
         total);

  return total;
}

static NOINLINE void target_sample_post_cbd_x2_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  poly_triple(&g_work0, &g_work0);
  g_work0.coeffs[0]++;
  poly_triple(&g_work1, &g_work1);
  poly_ntt(&g_work0, &g_work0);
  poly_ntt(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_sample_post_cbd_x2_sample_dag(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_cbd1(&g_work0, g_buf_f[input_idx]);
  poly_cbd1(&g_work1, g_buf_g[input_idx]);
  poly_ntt_mul3_add1(&g_work0, &g_work0);
  poly_ntt_mul3(&g_work1, &g_work1);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 17) % NTRUPLUS_N];
}

static NOINLINE void target_baseinv_scaled_x2_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r(&g_work0, &g_f_current[input_idx]);
  (void)poly_baseinv_scaled_r(&g_work1, &g_g_current[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 23) % NTRUPLUS_N];
}

static NOINLINE void target_baseinv_scaled_x2_hierk8(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate(
      &g_work0, &g_f_sample[input_idx]);
  (void)poly_baseinv_scaled_r_hier_k8_tree_candidate(
      &g_work1, &g_g_sample[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 23) % NTRUPLUS_N];
}

static NOINLINE void target_public_arithmetic_x2_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_basemul_scaled_r_input(&g_work0, &g_g_current[input_idx],
                              &g_finv_current[input_idx]);
  poly_basemul_scaled_r_input(&g_work1, &g_f_current[input_idx],
                              &g_ginv_current[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 29) % NTRUPLUS_N];
}

static NOINLINE void target_public_arithmetic_x2_combo(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_basemul_scaled_r_input(&g_work0, &g_g_sample[input_idx],
                              &g_finv_hier[input_idx]);
  poly_basemul_scaled_r_input(&g_work1, &g_f_sample[input_idx],
                              &g_ginv_hier[input_idx]);
  g_sink ^= (uint16_t)g_work0.coeffs[idx % NTRUPLUS_N];
  g_sink ^= (uint16_t)g_work1.coeffs[(idx + 29) % NTRUPLUS_N];
}

static void pack_hashf_from_material(uint8_t *pk, uint8_t *sk, const poly *f,
                                     const poly *h, const poly *hinv)
{
  poly_tobytes(pk, h);
  poly_tobytes(sk, f);
  poly_tobytes(sk + NTRUPLUS_POLYBYTES, hinv);
  hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

static NOINLINE void target_pack_hashf_total_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  pack_hashf_from_material(g_work_pk, g_work_sk, &g_f_current[input_idx],
                           &g_h_current[input_idx],
                           &g_hinv_current[input_idx]);
  g_sink ^= g_work_pk[idx % sizeof(g_work_pk)];
  g_sink ^= (uint64_t)g_work_sk[(idx + 31) % sizeof(g_work_sk)] << 8;
}

static NOINLINE void target_pack_hashf_total_combo(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  pack_hashf_from_material(g_work_pk, g_work_sk, &g_f_sample[input_idx],
                           &g_h_combo[input_idx], &g_hinv_combo[input_idx]);
  g_sink ^= g_work_pk[idx % sizeof(g_work_pk)];
  g_sink ^= (uint64_t)g_work_sk[(idx + 31) % sizeof(g_work_sk)] << 8;
}

static NOINLINE void target_keygen_current(size_t idx)
{
  (void)keypair_variant(g_pk0, g_sk0, VAR_CURRENT,
                        seed_for_index(idx, 0x3141592653589793ULL));
  g_sink ^= g_pk0[idx % sizeof(g_pk0)];
  g_sink ^= (uint64_t)g_sk0[(idx + 17) % sizeof(g_sk0)] << 8;
}

static NOINLINE void target_keygen_sample_dag_only(size_t idx)
{
  (void)keypair_variant(g_pk1, g_sk1, VAR_SAMPLE_DAG,
                        seed_for_index(idx, 0x3141592653589793ULL));
  g_sink ^= g_pk1[idx % sizeof(g_pk1)];
  g_sink ^= (uint64_t)g_sk1[(idx + 19) % sizeof(g_sk1)] << 8;
}

static NOINLINE void target_keygen_hierk8_only(size_t idx)
{
  (void)keypair_variant(g_pk1, g_sk1, VAR_HIERK8,
                        seed_for_index(idx, 0x3141592653589793ULL));
  g_sink ^= g_pk1[idx % sizeof(g_pk1)];
  g_sink ^= (uint64_t)g_sk1[(idx + 21) % sizeof(g_sk1)] << 8;
}

static NOINLINE void target_keygen_sample_dag_plus_hierk8(size_t idx)
{
  (void)keypair_variant(g_pk1, g_sk1, VAR_SAMPLE_DAG_HIERK8,
                        seed_for_index(idx, 0x3141592653589793ULL));
  g_sink ^= g_pk1[idx % sizeof(g_pk1)];
  g_sink ^= (uint64_t)g_sk1[(idx + 23) % sizeof(g_sk1)] << 8;
}

static NOINLINE void target_kem_enc_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  randombytes_reset(seed_for_index(idx, 0x656e636170706d31ULL));
  (void)bench_crypto_kem_enc_current(g_ct, g_ss0, g_kem_pk[input_idx]);
  g_sink ^= g_ct[idx % sizeof(g_ct)];
  g_sink ^= (uint64_t)g_ss0[(idx + 3) % sizeof(g_ss0)] << 8;
}

static NOINLINE void target_kem_enc_candidate_binary(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  randombytes_reset(seed_for_index(idx, 0x656e636170706d31ULL));
  (void)bench_crypto_kem_enc_current(g_ct, g_ss0, g_kem_pk[input_idx]);
  g_sink ^= g_ct[(idx + 5) % sizeof(g_ct)];
  g_sink ^= (uint64_t)g_ss0[(idx + 7) % sizeof(g_ss0)] << 8;
}

static NOINLINE void target_kem_dec_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)bench_crypto_kem_dec_current(g_ss1, g_kem_ct[input_idx],
                                     g_kem_sk[input_idx]);
  g_sink ^= g_ss1[idx % sizeof(g_ss1)];
}

static NOINLINE void target_kem_dec_candidate_binary(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  (void)bench_crypto_kem_dec_current(g_ss1, g_kem_ct[input_idx],
                                     g_kem_sk[input_idx]);
  g_sink ^= g_ss1[(idx + 11) % sizeof(g_ss1)];
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
      {"sample_post_cbd_x2_current", target_sample_post_cbd_x2_current,
       NITERATIONS, NWARMUP},
      {"sample_post_cbd_x2_sample_dag", target_sample_post_cbd_x2_sample_dag,
       NITERATIONS, NWARMUP},
      {"sample_post_cbd_x2_sample_dag_plus_hierk8",
       target_sample_post_cbd_x2_sample_dag, NITERATIONS, NWARMUP},
      {"baseinv_scaled_x2_current", target_baseinv_scaled_x2_current,
       NITERATIONS, NWARMUP},
      {"baseinv_scaled_x2_hierk8_candidate", target_baseinv_scaled_x2_hierk8,
       NITERATIONS, NWARMUP},
      {"baseinv_scaled_x2_sample_dag_plus_hierk8",
       target_baseinv_scaled_x2_hierk8, NITERATIONS, NWARMUP},
      {"public_arithmetic_x2_current", target_public_arithmetic_x2_current,
       NITERATIONS, NWARMUP},
      {"public_arithmetic_x2_sample_dag_plus_hierk8",
       target_public_arithmetic_x2_combo, NITERATIONS, NWARMUP},
      {"pack_hashf_total_current", target_pack_hashf_total_current,
       NITERATIONS, NWARMUP},
      {"pack_hashf_total_sample_dag_plus_hierk8",
       target_pack_hashf_total_combo, NITERATIONS, NWARMUP},
      {"keygen_current", target_keygen_current, NKEYPAIR_ITERATIONS,
       NKEYPAIR_WARMUP},
      {"keygen_sample_dag_only", target_keygen_sample_dag_only,
       NKEYPAIR_ITERATIONS, NKEYPAIR_WARMUP},
      {"keygen_hierk8_only", target_keygen_hierk8_only, NKEYPAIR_ITERATIONS,
       NKEYPAIR_WARMUP},
      {"keygen_sample_dag_plus_hierk8", target_keygen_sample_dag_plus_hierk8,
       NKEYPAIR_ITERATIONS, NKEYPAIR_WARMUP},
      {"kem_enc_current", target_kem_enc_current, NKEYPAIR_ITERATIONS,
       NKEYPAIR_WARMUP},
      {"kem_enc_candidate_binary_current_path",
       target_kem_enc_candidate_binary, NKEYPAIR_ITERATIONS, NKEYPAIR_WARMUP},
      {"kem_dec_current", target_kem_dec_current, NKEYPAIR_ITERATIONS,
       NKEYPAIR_WARMUP},
      {"kem_dec_candidate_binary_current_path",
       target_kem_dec_candidate_binary, NKEYPAIR_ITERATIONS, NKEYPAIR_WARMUP},
  };

  setup_perf_events();
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d,"
         "NKEYPAIR_ITERATIONS=%d,NKEYPAIR_WARMUP=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS, NKEYPAIR_ITERATIONS,
         NKEYPAIR_WARMUP);
  bench_print_gt_production_config();
  printf("experiment,GT_EXPERIMENT_USE_KEYGEN_SAMPLE_NTT_MUL3=1\n");
  printf("experiment,GT_EXPERIMENT_USE_HIERK8_TREE_CANDIDATE=1\n");

  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    run_one_variant(&variants[i]);

  printf("sink=%" PRIu64 "\n", g_sink);
  close_perf_events();
}

int main(void)
{
  prepare_inputs();
  if (run_component_correctness() != 0)
    return 1;
  if (run_keypair_correctness() != 0)
    return 1;
  if (run_kem_matrix_correctness() != 0)
    return 1;

  run_pmu();
  return 0;
}
