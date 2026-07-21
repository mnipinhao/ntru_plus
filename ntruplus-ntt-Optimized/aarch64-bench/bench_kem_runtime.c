/*
 * Minimal deterministic full-KEM benchmark harness.
 *
 * Unlike bench.c, this file does not reference standalone generic polynomial
 * primitives that are absent from the selected production KEM call graph.
 * This keeps full-KEM text size and instruction placement representative of
 * the runtime being measured. Component modes continue to use bench.c.
 */
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"
#include "bench_build_config.h"
#include "hal.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"

#ifdef SUPPORTS_SHAKE256_ASM
#include "CE/fips202.h"
#else
#include "NO_CE/fips202.h"
#endif

#ifdef GT_PRODUCTION_USE_BPQ_CQ_KEYGEN
#include "gt/keygen_bpq_cq.h"

static void bench_keygen_ntt_mul3(poly *out, const poly *small)
{
  gt_keygen_ntt_bpq_mul3((gt_bpq_poly *)(void *)out, small);
}

static void bench_keygen_ntt_mul3_add1(poly *out, const poly *small)
{
  gt_keygen_ntt_bpq_mul3_add1((gt_bpq_poly *)(void *)out, small);
}

static int bench_keygen_baseinv(poly *out, const poly *in)
{
  return gt_keygen_baseinv_bpq_to_cq_scaled_r(
      (gt_cq_poly *)(void *)out,
      (const gt_bpq_poly *)(const void *)in);
}

static void bench_keygen_basemul(poly *out, const poly *bpq,
                                 const poly *cq)
{
  gt_keygen_basemul_bpq_cq_to_cq_scaled_r(
      (gt_cq_poly *)(void *)out,
      (const gt_bpq_poly *)(const void *)bpq,
      (const gt_cq_poly *)(const void *)cq);
}

static void bench_keygen_tobytes_cq(uint8_t *out, const poly *in)
{
  gt_keygen_tobytes_cq(out, (const gt_cq_poly *)(const void *)in);
}

static void bench_keygen_tobytes_bpq_p1(uint8_t *out, const poly *in)
{
  gt_keygen_tobytes_bpq_p1(out,
                           (const gt_bpq_poly *)(const void *)in);
}

#define BENCH_KEYGEN_NTT_MUL3 bench_keygen_ntt_mul3
#define BENCH_KEYGEN_NTT_MUL3_ADD1 bench_keygen_ntt_mul3_add1
#define BENCH_KEYPAIR_BASEINV bench_keygen_baseinv
#define BENCH_KEYPAIR_BASEMUL bench_keygen_basemul
#define BENCH_KEYGEN_TOBYTES_PUBLIC bench_keygen_tobytes_cq
#define BENCH_KEYGEN_TOBYTES_SECRET_F bench_keygen_tobytes_bpq_p1
#define BENCH_KEYGEN_TOBYTES_SECRET_HINV bench_keygen_tobytes_cq
#endif

#if defined(BENCH_VARIANT_GT) && BENCH_VARIANT_GT
#define BENCH_NTT_TOBYTES poly_tobytes_gt_canonical
#define BENCH_NTT_FROMBYTES poly_frombytes_gt_canonical
#else
#define BENCH_NTT_TOBYTES poly_tobytes
#define BENCH_NTT_FROMBYTES poly_frombytes
#endif

#ifndef BENCH_KEYGEN_TOBYTES_PUBLIC
#if defined(GT_PRODUCTION_USE_KEYGEN_CANONICAL_PACK_P1)
#define BENCH_KEYGEN_TOBYTES_PUBLIC poly_tobytes_gt_canonical_p1
#else
#define BENCH_KEYGEN_TOBYTES_PUBLIC BENCH_NTT_TOBYTES
#endif
#endif

#ifndef BENCH_KEYGEN_TOBYTES_SECRET_F
#define BENCH_KEYGEN_TOBYTES_SECRET_F BENCH_KEYGEN_TOBYTES_PUBLIC
#endif

#ifndef BENCH_KEYGEN_TOBYTES_SECRET_HINV
#define BENCH_KEYGEN_TOBYTES_SECRET_HINV BENCH_KEYGEN_TOBYTES_PUBLIC
#endif

#if defined(GT_PRODUCTION_USE_BPQ_CQ_KEYGEN)
#elif defined(GT_PRODUCTION_USE_SCALED_KEYPAIR)
int poly_baseinv_scaled_r(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
#define BENCH_KEYPAIR_BASEINV poly_baseinv_scaled_r
#define BENCH_KEYPAIR_BASEMUL poly_basemul_scaled_r_input
#else
#define BENCH_KEYPAIR_BASEINV poly_baseinv
#define BENCH_KEYPAIR_BASEMUL poly_basemul
#endif

#ifdef GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3
void poly_ntt_mul3(poly *out, const poly *a);
void poly_ntt_mul3_add1(poly *out, const poly *a);
#endif

#ifdef GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
void poly_basemul_add_encap_direct32_q31_tobytes_contract(
    poly *r, const poly *a, const poly *b, const poly *c);
#endif

#ifndef BENCH_MODE
#define BENCH_MODE "kem_enc"
#endif

#ifndef BENCH_NAME
#define BENCH_NAME "ntruplus_kem"
#endif

#ifndef NWARMUP
#define NWARMUP 50
#endif

#ifndef NITERATIONS
#define NITERATIONS 300
#endif

#ifndef NTESTS
#define NTESTS 500
#endif

#ifndef BENCH_COUNTER_NAME
#define BENCH_COUNTER_NAME "cycles"
#endif

typedef void (*target_fn)(void);

static uint8_t g_fcoins[NTRUPLUS_SYMBYTES];
static uint8_t g_gcoins[NTRUPLUS_SYMBYTES];
static uint8_t g_ecoins[NTRUPLUS_N / 8];
static uint8_t g_pk[NTRUPLUS_PUBLICKEYBYTES];
static uint8_t g_sk[NTRUPLUS_SECRETKEYBYTES];
static uint8_t g_ct[NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t g_ss_enc[NTRUPLUS_SSBYTES];
static uint8_t g_ss_dec[NTRUPLUS_SSBYTES];
static volatile uint64_t g_sink;

static int cmp_uint64_t(const void *a, const void *b)
{
  const uint64_t aa = *(const uint64_t *)a;
  const uint64_t bb = *(const uint64_t *)b;

  return (aa > bb) - (aa < bb);
}

static void fill_bytes(uint8_t *out, size_t len, uint32_t seed)
{
  uint32_t state = seed ? seed : 1;
  size_t i;

  for (i = 0; i < len; i++)
  {
    state = state * 1664525u + 1013904223u;
    out[i] = (uint8_t)(state >> 24);
  }
}

static uint64_t checksum_bytes(const uint8_t *a, size_t len)
{
  uint64_t acc = UINT64_C(0x9e3779b97f4a7c15);
  size_t i;

  for (i = 0; i < len; i++)
  {
    acc ^= (uint64_t)a[i] + UINT64_C(0x9e3779b97f4a7c15) +
           (acc << 6) + (acc >> 2);
  }

  return acc;
}

static void keygen_ntt_mul3_add1(poly *out, const poly *small)
{
#ifdef BENCH_KEYGEN_NTT_MUL3_ADD1
  BENCH_KEYGEN_NTT_MUL3_ADD1(out, small);
#elif defined(GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3)
  poly_ntt_mul3_add1(out, small);
#else
  poly_triple(out, small);
  out->coeffs[0] += 1;
  poly_ntt(out, out);
#endif
}

static void keygen_ntt_mul3(poly *out, const poly *small)
{
#ifdef BENCH_KEYGEN_NTT_MUL3
  BENCH_KEYGEN_NTT_MUL3(out, small);
#elif defined(GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3)
  poly_ntt_mul3(out, small);
#else
  poly_triple(out, small);
  poly_ntt(out, out);
#endif
}

static int genf_derand(poly *f, poly *finv, const uint8_t *coins)
{
  uint8_t buf[NTRUPLUS_N / 4];

  shake256(buf, sizeof(buf), coins, NTRUPLUS_SYMBYTES);
  poly_cbd1(f, buf);
  keygen_ntt_mul3_add1(f, f);
  return BENCH_KEYPAIR_BASEINV(finv, f);
}

static int geng_derand(poly *g, poly *ginv, const uint8_t *coins)
{
  uint8_t buf[NTRUPLUS_N / 4];

  shake256(buf, sizeof(buf), coins, NTRUPLUS_SYMBYTES);
  poly_cbd1(g, buf);
  keygen_ntt_mul3(g, g);
  return BENCH_KEYPAIR_BASEINV(ginv, g);
}

static void keypair_derand(uint8_t *pk, uint8_t *sk,
                           const uint8_t *fcoins,
                           const uint8_t *gcoins)
{
  poly f;
  poly finv;
  poly g;
  poly ginv;
  poly h;
  poly hinv;

  if (genf_derand(&f, &finv, fcoins) != 0 ||
      geng_derand(&g, &ginv, gcoins) != 0)
  {
    fprintf(stderr, "deterministic keypair coins became non-invertible\n");
    abort();
  }

  BENCH_KEYPAIR_BASEMUL(&h, &g, &finv);
  BENCH_KEYPAIR_BASEMUL(&hinv, &f, &ginv);
  BENCH_KEYGEN_TOBYTES_PUBLIC(pk, &h);
  BENCH_KEYGEN_TOBYTES_SECRET_F(sk, &f);
  BENCH_KEYGEN_TOBYTES_SECRET_HINV(sk + NTRUPLUS_POLYBYTES, &hinv);
  hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

static void enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk,
                       const uint8_t *coins)
{
  uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
  uint8_t buf1[NTRUPLUS_SYMBYTES + NTRUPLUS_N / 4];
  uint8_t buf2[NTRUPLUS_POLYBYTES];
  poly c;
  poly h;
  poly r;
  poly m;

  memcpy(msg, coins, NTRUPLUS_N / 8);
  hash_f(msg + NTRUPLUS_N / 8, pk);
  hash_h(buf1, msg);

  poly_cbd1(&r, buf1 + NTRUPLUS_SYMBYTES);
  poly_ntt(&r, &r);
  BENCH_NTT_TOBYTES(buf2, &r);
  hash_g(buf2, buf2);
  poly_sotp_encode(&m, msg, buf2);
  poly_ntt(&m, &m);
  BENCH_NTT_FROMBYTES(&h, pk);

#ifdef GT_PRODUCTION_USE_DIRECT32_Q31_BASEMUL_ADD_ENCAP
  poly_basemul_add_encap_direct32_q31_tobytes_contract(&c, &h, &r, &m);
#else
  poly_basemul_add(&c, &h, &r, &m);
#endif
  BENCH_NTT_TOBYTES(ct, &c);
  memcpy(ss, buf1, NTRUPLUS_SSBYTES);
}

static void find_invertible_coins(uint8_t coins[NTRUPLUS_SYMBYTES],
                                  int is_f, uint32_t start_seed)
{
  poly value;
  poly inverse;
  uint32_t seed;

  for (seed = start_seed;; seed++)
  {
    fill_bytes(coins, NTRUPLUS_SYMBYTES, seed);
    if ((is_f && genf_derand(&value, &inverse, coins) == 0) ||
        (!is_f && geng_derand(&value, &inverse, coins) == 0))
    {
      return;
    }
  }
}

static int prepare_inputs(void)
{
  find_invertible_coins(g_fcoins, 1, 1);
  find_invertible_coins(g_gcoins, 0, 1001);
  fill_bytes(g_ecoins, sizeof(g_ecoins), 2001);

  keypair_derand(g_pk, g_sk, g_fcoins, g_gcoins);
  enc_derand(g_ct, g_ss_enc, g_pk, g_ecoins);
  if (crypto_kem_dec(g_ss_dec, g_ct, g_sk) != 0 ||
      memcmp(g_ss_enc, g_ss_dec, sizeof(g_ss_enc)) != 0)
  {
    fprintf(stderr, "deterministic KEM setup failed\n");
    return 0;
  }

  return 1;
}

static void target_keygen(void)
{
  keypair_derand(g_pk, g_sk, g_fcoins, g_gcoins);
}

static void target_enc(void)
{
  enc_derand(g_ct, g_ss_enc, g_pk, g_ecoins);
}

static void target_dec(void)
{
  (void)crypto_kem_dec(g_ss_dec, g_ct, g_sk);
}

static target_fn select_target(const char *mode)
{
  if (strcmp(mode, "kem_keygen") == 0)
  {
    return target_keygen;
  }
  if (strcmp(mode, "kem_enc") == 0)
  {
    return target_enc;
  }
  if (strcmp(mode, "kem_dec") == 0)
  {
    return target_dec;
  }

  return NULL;
}

static void print_distribution(const uint64_t samples[NTESTS])
{
  static const unsigned percentiles[] = {
      1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99};
  size_t i;

  printf("%10s %s = %" PRIu64 "\n", BENCH_NAME, BENCH_COUNTER_NAME,
         samples[NTESTS / 2] / NITERATIONS);
  printf("%21s", "percentile");
  for (i = 0; i < sizeof(percentiles) / sizeof(percentiles[0]); i++)
  {
    printf("%7u", percentiles[i]);
  }
  printf("\n%10s percentiles:", BENCH_NAME);
  for (i = 0; i < sizeof(percentiles) / sizeof(percentiles[0]); i++)
  {
    printf("%7" PRIu64,
           samples[NTESTS * percentiles[i] / 100] / NITERATIONS);
  }
  printf("\n");
}

static int run_benchmark(target_fn target)
{
  uint64_t samples[NTESTS];
  int i;
  int j;

  for (i = 0; i < NTESTS; i++)
  {
    for (j = 0; j < NWARMUP; j++)
    {
      target();
    }

    {
      const uint64_t start = get_cyclecounter();
      for (j = 0; j < NITERATIONS; j++)
      {
        target();
      }
      samples[i] = get_cyclecounter() - start;
    }
  }

  qsort(samples, NTESTS, sizeof(samples[0]), cmp_uint64_t);
  if (crypto_kem_dec(g_ss_dec, g_ct, g_sk) != 0 ||
      memcmp(g_ss_enc, g_ss_dec, sizeof(g_ss_enc)) != 0)
  {
    fprintf(stderr, "post-benchmark KEM correctness failed\n");
    return 0;
  }

  g_sink ^= checksum_bytes(g_pk, sizeof(g_pk));
  g_sink ^= checksum_bytes(g_sk, sizeof(g_sk));
  g_sink ^= checksum_bytes(g_ct, sizeof(g_ct));
  g_sink ^= checksum_bytes(g_ss_enc, sizeof(g_ss_enc));
  g_sink ^= checksum_bytes(g_ss_dec, sizeof(g_ss_dec));

  printf("bench_name = %s\n", BENCH_NAME);
  printf("bench_mode = %s\n", BENCH_MODE);
  printf("bench_counter = %s\n", BENCH_COUNTER_NAME);
  print_distribution(samples);
  printf("sink = %" PRIu64 "\n", g_sink);
  return 1;
}

int main(void)
{
  target_fn target = select_target(BENCH_MODE);

  if (target == NULL)
  {
    fprintf(stderr, "minimal KEM harness does not support BENCH_MODE=%s\n",
            BENCH_MODE);
    return 1;
  }
  if (!prepare_inputs())
  {
    return 1;
  }

  bench_print_gt_production_config();
  enable_cyclecounter();
  if (!run_benchmark(target))
  {
    disable_cyclecounter();
    return 1;
  }
  disable_cyclecounter();
  return 0;
}
