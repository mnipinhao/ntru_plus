/*
 * NTRU+ Raspberry Pi 5 benchmark harness.
 *
 * This follows the aarch64-bench style: each test performs NWARMUP warmup
 * calls, then measures NITERATIONS calls, repeated NTESTS times.  Setup,
 * random input preparation, correctness checks, and checksums stay outside the
 * measured region.
 */
#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "hal.h"
#include "params.h"
#include "poly.h"

#ifndef BENCH_ENABLE_KEM
#define BENCH_ENABLE_KEM 0
#endif

#if BENCH_ENABLE_KEM
#include "api.h"
#endif

#ifndef BENCH_MODE
#define BENCH_MODE "ntt_mul_pipeline"
#endif

#ifndef BENCH_NAME
#define BENCH_NAME "gt_ntt_mul_pipeline"
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

typedef void (*target_fn)(int idx);

static poly g_a[NITERATIONS];
static poly g_b[NITERATIONS];
static poly g_acc[NITERATIONS];
static poly g_ntt_a[NITERATIONS];
static poly g_ntt_b[NITERATIONS];
static poly g_ntt_acc[NITERATIONS];
static poly g_freq_out[NITERATIONS];
static poly g_out[NITERATIONS];

#if BENCH_ENABLE_KEM
static uint8_t g_pk[NTRUPLUS_PUBLICKEYBYTES];
static uint8_t g_sk[NTRUPLUS_SECRETKEYBYTES];
static uint8_t g_ct[NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t g_ss_enc[NTRUPLUS_SSBYTES];
static uint8_t g_ss_dec[NTRUPLUS_SSBYTES];
#endif

static volatile uint64_t g_sink;

static int cmp_uint64_t(const void *a, const void *b)
{
  const uint64_t aa = *((const uint64_t *)a);
  const uint64_t bb = *((const uint64_t *)b);

  return (aa > bb) - (aa < bb);
}

static void print_median(const char *txt, uint64_t cyc[NTESTS])
{
  printf("%10s cycles = %" PRIu64 "\n", txt, cyc[NTESTS >> 1] / NITERATIONS);
}

static int percentiles[] = {1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99};

static void print_percentile_legend(void)
{
  unsigned i;

  printf("%21s", "percentile");
  for (i = 0; i < sizeof(percentiles) / sizeof(percentiles[0]); i++)
  {
    printf("%7d", percentiles[i]);
  }
  printf("\n");
}

static void print_percentiles(const char *txt, uint64_t cyc[NTESTS])
{
  unsigned i;

  printf("%10s percentiles:", txt);
  for (i = 0; i < sizeof(percentiles) / sizeof(percentiles[0]); i++)
  {
    printf("%7" PRIu64,
           cyc[NTESTS * percentiles[i] / 100] / NITERATIONS);
  }
  printf("\n");
}

static uint32_t next_u32(uint32_t *state)
{
  *state = *state * 1664525u + 1013904223u;
  return *state;
}

static void fill_poly(poly *a, uint32_t seed)
{
  int i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    a->coeffs[i] =
        (int16_t)((int)(next_u32(&seed) % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
  }
}

static int modq(int64_t a)
{
  int r = (int)(a % NTRUPLUS_Q);

  if (r < 0)
  {
    r += NTRUPLUS_Q;
  }

  return r;
}

static int centered_modq(int64_t a)
{
  int r = modq(a);

  if (r > NTRUPLUS_Q / 2)
  {
    r -= NTRUPLUS_Q;
  }

  return r;
}

static int equal_modq(int16_t a, int16_t b)
{
  return modq((int)a - (int)b) == 0;
}

static void schoolbook_mul_reference(poly *r, const poly *a, const poly *b)
{
  static int64_t tmp[2 * NTRUPLUS_N - 1];
  int i, j;

  for (i = 0; i < 2 * NTRUPLUS_N - 1; i++)
  {
    tmp[i] = 0;
  }

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    for (j = 0; j < NTRUPLUS_N; j++)
    {
      tmp[i + j] += (int64_t)a->coeffs[i] * b->coeffs[j];
    }
  }

  /* NTRU+768 works modulo X^768 - X^384 + 1, so X^768 = X^384 - 1. */
  for (i = 2 * NTRUPLUS_N - 2; i >= NTRUPLUS_N; i--)
  {
    const int64_t c = tmp[i];
    tmp[i - NTRUPLUS_N / 2] += c;
    tmp[i - NTRUPLUS_N] -= c;
  }

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    r->coeffs[i] = (int16_t)centered_modq(tmp[i]);
  }
}

static uint64_t checksum_poly(const poly *a)
{
  uint64_t acc = 0x6a09e667f3bcc909ULL;
  int i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    acc ^= (uint16_t)a->coeffs[i];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }

  return acc;
}

#if BENCH_ENABLE_KEM
static uint64_t checksum_bytes(const uint8_t *a, size_t len)
{
  uint64_t acc = 0x9e3779b97f4a7c15ULL;
  size_t i;

  for (i = 0; i < len; i++)
  {
    acc ^= (uint64_t)a[i] + 0x9e3779b97f4a7c15ULL + (acc << 6) + (acc >> 2);
  }

  return acc;
}
#endif

static void checksum_outputs(void)
{
  int i;

  for (i = 0; i < NITERATIONS; i++)
  {
    g_sink ^= checksum_poly(&g_out[i]);
    g_sink = (g_sink << 7) ^ (g_sink >> 3) ^ checksum_poly(&g_freq_out[i]);
  }

#if BENCH_ENABLE_KEM
  g_sink ^= checksum_bytes(g_ss_dec, sizeof(g_ss_dec));
#endif
}

static int compare_poly_modq(const char *label, const poly *got,
                             const poly *want)
{
  int i;

  for (i = 0; i < NTRUPLUS_N; i++)
  {
    if (!equal_modq(got->coeffs[i], want->coeffs[i]))
    {
      fprintf(stderr, "%s mismatch at %d: got=%d want=%d\n", label, i,
              got->coeffs[i], want->coeffs[i]);
      return 0;
    }
  }

  return 1;
}

static void prepare_poly_inputs(void)
{
  int i;

  for (i = 0; i < NITERATIONS; i++)
  {
    fill_poly(&g_a[i], 0x243f6a88u + (uint32_t)i);
    fill_poly(&g_b[i], 0x85a308d3u + (uint32_t)i);
    fill_poly(&g_acc[i], 0x13198a2eu + (uint32_t)i);
    poly_ntt(&g_ntt_a[i], &g_a[i]);
    poly_ntt(&g_ntt_b[i], &g_b[i]);
    poly_ntt(&g_ntt_acc[i], &g_acc[i]);
    poly_basemul(&g_freq_out[i], &g_ntt_a[i], &g_ntt_b[i]);
    poly_invntt(&g_out[i], &g_freq_out[i]);
  }
}

#if BENCH_ENABLE_KEM
static int prepare_kem_inputs(void)
{
  if (crypto_kem_keypair(g_pk, g_sk) != 0 ||
      crypto_kem_enc(g_ct, g_ss_enc, g_pk) != 0 ||
      crypto_kem_dec(g_ss_dec, g_ct, g_sk) != 0)
  {
    fprintf(stderr, "kem_dec setup failed\n");
    return 0;
  }

  if (memcmp(g_ss_enc, g_ss_dec, sizeof(g_ss_enc)) != 0)
  {
    fprintf(stderr, "kem_dec setup correctness failed\n");
    return 0;
  }

  return 1;
}
#endif

static int check_ntt_roundtrip(void)
{
  poly freq;
  poly got;

  poly_ntt(&freq, &g_a[0]);
  poly_invntt(&got, &freq);
  return compare_poly_modq("ntt roundtrip", &got, &g_a[0]);
}

static int check_mul_pipeline(void)
{
  poly want;
  poly got;
  poly ntt_a;
  poly ntt_b;
  poly freq;

  schoolbook_mul_reference(&want, &g_a[0], &g_b[0]);
  poly_ntt(&ntt_a, &g_a[0]);
  poly_ntt(&ntt_b, &g_b[0]);
  poly_basemul(&freq, &ntt_a, &ntt_b);
  poly_invntt(&got, &freq);
  return compare_poly_modq("ntt_mul_pipeline", &got, &want);
}

static int check_add_pipeline(void)
{
  poly want;
  poly got;
  poly ntt_a;
  poly ntt_b;
  poly ntt_acc;
  poly freq;
  int i;

  schoolbook_mul_reference(&want, &g_a[0], &g_b[0]);
  for (i = 0; i < NTRUPLUS_N; i++)
  {
    want.coeffs[i] =
        (int16_t)centered_modq((int64_t)want.coeffs[i] + g_acc[0].coeffs[i]);
  }

  poly_ntt(&ntt_a, &g_a[0]);
  poly_ntt(&ntt_b, &g_b[0]);
  poly_ntt(&ntt_acc, &g_acc[0]);
  poly_basemul_add(&freq, &ntt_a, &ntt_b, &ntt_acc);
  poly_invntt(&got, &freq);
  return compare_poly_modq("ntt_basemul_add_pipeline", &got, &want);
}

static int check_correctness(const char *mode)
{
  if (strcmp(mode, "kem_dec") == 0)
  {
    return 1;
  }
  if (strcmp(mode, "ntt") == 0 || strcmp(mode, "invntt") == 0)
  {
    return check_ntt_roundtrip();
  }
  if (strcmp(mode, "basemul") == 0 ||
      strcmp(mode, "ntt_mul_pipeline") == 0)
  {
    return check_mul_pipeline();
  }
  if (strcmp(mode, "basemul_add") == 0)
  {
    return check_add_pipeline();
  }
  if (strcmp(mode, "ntt_basemul_add_pipeline") == 0 ||
      strcmp(mode, "basemul_add_pipeline") == 0)
  {
    return check_add_pipeline();
  }

  return 0;
}

static void target_ntt(int idx)
{
  poly_ntt(&g_out[idx], &g_a[idx]);
}

static void target_invntt(int idx)
{
  poly_invntt(&g_out[idx], &g_ntt_a[idx]);
}

static void target_basemul(int idx)
{
  poly_basemul(&g_freq_out[idx], &g_ntt_a[idx], &g_ntt_b[idx]);
}

static void target_basemul_add(int idx)
{
  poly_basemul_add(&g_freq_out[idx], &g_ntt_a[idx], &g_ntt_b[idx],
                   &g_ntt_acc[idx]);
}

static void target_pipeline(int idx)
{
  poly_ntt(&g_ntt_a[idx], &g_a[idx]);
  poly_ntt(&g_ntt_b[idx], &g_b[idx]);
  poly_basemul(&g_freq_out[idx], &g_ntt_a[idx], &g_ntt_b[idx]);
  poly_invntt(&g_out[idx], &g_freq_out[idx]);
}

static void target_add_pipeline(int idx)
{
  poly_ntt(&g_ntt_a[idx], &g_a[idx]);
  poly_ntt(&g_ntt_b[idx], &g_b[idx]);
  poly_ntt(&g_ntt_acc[idx], &g_acc[idx]);
  poly_basemul_add(&g_freq_out[idx], &g_ntt_a[idx], &g_ntt_b[idx],
                   &g_ntt_acc[idx]);
  poly_invntt(&g_out[idx], &g_freq_out[idx]);
}

#if BENCH_ENABLE_KEM
static void target_kem_dec(int idx)
{
  (void)idx;
  crypto_kem_dec(g_ss_dec, g_ct, g_sk);
}
#endif

static target_fn select_target(const char *mode)
{
  if (strcmp(mode, "ntt") == 0)
  {
    return target_ntt;
  }
  if (strcmp(mode, "invntt") == 0)
  {
    return target_invntt;
  }
  if (strcmp(mode, "basemul") == 0)
  {
    return target_basemul;
  }
  if (strcmp(mode, "basemul_add") == 0)
  {
    return target_basemul_add;
  }
  if (strcmp(mode, "ntt_mul_pipeline") == 0)
  {
    return target_pipeline;
  }
  if (strcmp(mode, "ntt_basemul_add_pipeline") == 0 ||
      strcmp(mode, "basemul_add_pipeline") == 0)
  {
    return target_add_pipeline;
  }
#if BENCH_ENABLE_KEM
  if (strcmp(mode, "kem_dec") == 0)
  {
    return target_kem_dec;
  }
#endif

  return NULL;
}

static int bench(const char *name, const char *mode, target_fn target)
{
  uint64_t cycles[NTESTS];
  int i, j;

  for (i = 0; i < NTESTS; i++)
  {
    for (j = 0; j < NWARMUP; j++)
    {
      target(j % NITERATIONS);
    }

    {
      const uint64_t t0 = get_cyclecounter();
      for (j = 0; j < NITERATIONS; j++)
      {
        target(j);
      }
      cycles[i] = get_cyclecounter() - t0;
    }
  }

  qsort(cycles, NTESTS, sizeof(uint64_t), cmp_uint64_t);
  checksum_outputs();

  printf("bench_name = %s\n", name);
  printf("bench_mode = %s\n", mode);
  print_median(name, cycles);
  printf("\n");
  print_percentile_legend();
  print_percentiles(name, cycles);
  printf("sink = %" PRIu64 "\n", g_sink);

  return 0;
}

int main(void)
{
  const char *mode = BENCH_MODE;
  target_fn target;

  prepare_poly_inputs();
#if BENCH_ENABLE_KEM
  if (!prepare_kem_inputs())
  {
    return 1;
  }
#endif

  target = select_target(mode);
  if (target == NULL)
  {
    fprintf(stderr,
            "unknown BENCH_MODE=%s "
            "(use ntt, invntt, basemul, basemul_add, ntt_mul_pipeline, "
            "ntt_basemul_add_pipeline, kem_dec)\n",
            mode);
    return 1;
  }

  if (!check_correctness(mode))
  {
    fprintf(stderr, "correctness check failed for BENCH_MODE=%s\n", mode);
    return 1;
  }

  enable_cyclecounter();
  bench(BENCH_NAME, mode, target);
  disable_cyclecounter();

  return 0;
}
