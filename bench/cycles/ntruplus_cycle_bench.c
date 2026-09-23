#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if __has_include("api.h")
#include "api.h"
#include "poly.h"
#elif __has_include("../../ntruplus-ntt-Optimized/Reference_Implementation/NTRU+768/api.h")
#include "../../ntruplus-ntt-Optimized/Reference_Implementation/NTRU+768/api.h"
#include "../../ntruplus-ntt-Optimized/Reference_Implementation/NTRU+768/poly.h"
#else
#error "Unable to locate NTRU+ headers (api.h/poly.h)."
#endif

#ifndef BENCH_LABEL
#define BENCH_LABEL "unknown"
#endif

typedef uint64_t (*bench_fn_t)(void);

typedef struct {
  uint64_t min;
  uint64_t max;
  double mean;
  double median;
  double stddev;
} stats_t;

#if defined(BENCH_GT_KEYPAIR_COMPARISON)
int crypto_kem_keypair_gt(unsigned char *pk, unsigned char *sk);
#endif

static unsigned long long g_counter_gap = 0;
static int g_iterations = 1000;
static int g_warmup = 100;
#if defined(__aarch64__)
static const char *g_unit = "cntvct_ticks";
#elif defined(__x86_64__) || defined(__i386__)
static const char *g_unit = "tsc_ticks";
#else
static const char *g_unit = "ns";
#endif

static poly g_poly_a;
static poly g_poly_b;
static poly g_poly_c;
static uint8_t g_seed_buf[NTRUPLUS_N / 4];
static uint8_t g_msg_buf[NTRUPLUS_N / 8];

static unsigned char g_pk[CRYPTO_PUBLICKEYBYTES];
static unsigned char g_sk[CRYPTO_SECRETKEYBYTES];
static unsigned char g_ct[CRYPTO_CIPHERTEXTBYTES];
static unsigned char g_ss[CRYPTO_BYTES];
static unsigned char g_dss[CRYPTO_BYTES];

#if defined(__aarch64__)
static inline uint64_t raw_counter(void) {
  uint64_t t;
  __asm__ volatile("mrs %0, cntvct_el0" : "=r"(t));
  return t;
}
#elif defined(__x86_64__) || defined(__i386__)
static inline uint64_t raw_counter(void) {
  uint64_t result;
  __asm__ volatile("lfence; rdtsc; shlq $32,%%rdx; orq %%rdx,%%rax"
                   : "=a"(result)
                   :
                   : "%rdx", "memory");
  return result;
}
#else
static inline uint64_t raw_counter(void) {
  struct timespec ts;
  clock_gettime(CLOCK_MONOTONIC, &ts);
  return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}
#endif

static inline uint64_t measured_cycles(bench_fn_t fn) {
  uint64_t start = raw_counter();
  (void)fn();
  uint64_t end = raw_counter();
  uint64_t delta = end - start;
  if (delta > g_counter_gap) {
    delta -= g_counter_gap;
  }
  return delta;
}

static void setup_counter_gap(void) {
  const int loops = 20000;
  unsigned long long accum = 0;
  for (int i = 0; i < loops; ++i) {
    uint64_t c1 = raw_counter();
    uint64_t c2 = raw_counter();
    accum += (unsigned long long)(c2 - c1);
  }
  g_counter_gap = accum / (unsigned long long)loops;
}

static void sort_u64(uint64_t *samples, int count) {
  for (int i = 0; i < count - 1; ++i) {
    for (int j = i + 1; j < count; ++j) {
      if (samples[i] > samples[j]) {
        uint64_t tmp = samples[i];
        samples[i] = samples[j];
        samples[j] = tmp;
      }
    }
  }
}

static stats_t compute_stats(uint64_t *samples, int count) {
  stats_t s;
  s.min = UINT64_MAX;
  s.max = 0;
  uint64_t total = 0;

  for (int i = 0; i < count; ++i) {
    uint64_t v = samples[i];
    if (v < s.min) {
      s.min = v;
    }
    if (v > s.max) {
      s.max = v;
    }
    total += v;
  }

  s.mean = (double)total / (double)count;
  sort_u64(samples, count);
  if ((count % 2) == 0) {
    s.median = ((double)samples[count / 2 - 1] + (double)samples[count / 2]) / 2.0;
  } else {
    s.median = (double)samples[count / 2];
  }

  double variance = 0.0;
  for (int i = 0; i < count; ++i) {
    double diff = (double)samples[i] - s.mean;
    variance += diff * diff;
  }
  variance /= (double)count;
  s.stddev = sqrt(variance);
  if (!isfinite(s.mean)) {
    s.mean = 0.0;
  }
  if (!isfinite(s.median)) {
    s.median = 0.0;
  }
  if (!isfinite(s.stddev)) {
    s.stddev = 0.0;
  }
  return s;
}

static stats_t run_bench(bench_fn_t fn) {
  uint64_t *samples = calloc((size_t)g_iterations, sizeof(uint64_t));
  if (samples == NULL) {
    fprintf(stderr, "allocation failed for benchmark samples\n");
    exit(1);
  }

  for (int i = 0; i < g_warmup; ++i) {
    (void)measured_cycles(fn);
  }
  for (int i = 0; i < g_iterations; ++i) {
    samples[i] = measured_cycles(fn);
  }

  stats_t s = compute_stats(samples, g_iterations);
  free(samples);
  return s;
}

#if defined(BENCH_GT_KEYPAIR_COMPARISON)
static void run_bench_pair(bench_fn_t first, bench_fn_t second,
                           stats_t *first_stats, stats_t *second_stats) {
  uint64_t *first_samples =
      calloc((size_t)g_iterations, sizeof(uint64_t));
  uint64_t *second_samples =
      calloc((size_t)g_iterations, sizeof(uint64_t));
  if (first_samples == NULL || second_samples == NULL) {
    fprintf(stderr, "allocation failed for paired benchmark samples\n");
    free(first_samples);
    free(second_samples);
    exit(1);
  }

  for (int i = 0; i < g_warmup; ++i) {
    if ((i & 1) == 0) {
      (void)measured_cycles(first);
      (void)measured_cycles(second);
    } else {
      (void)measured_cycles(second);
      (void)measured_cycles(first);
    }
  }
  for (int i = 0; i < g_iterations; ++i) {
    if ((i & 1) == 0) {
      first_samples[i] = measured_cycles(first);
      second_samples[i] = measured_cycles(second);
    } else {
      second_samples[i] = measured_cycles(second);
      first_samples[i] = measured_cycles(first);
    }
  }

  *first_stats = compute_stats(first_samples, g_iterations);
  *second_stats = compute_stats(second_samples, g_iterations);
  free(first_samples);
  free(second_samples);
}
#endif

static uint64_t bench_poly_cbd1(void) {
  poly_cbd1(&g_poly_a, g_seed_buf);
  return 0;
}

static uint64_t bench_poly_sotp_encode(void) {
  poly_sotp_encode(&g_poly_a, g_msg_buf, g_seed_buf);
  return 0;
}

static uint64_t bench_poly_sotp_decode(void) {
  return (uint64_t)poly_sotp_decode(g_msg_buf, &g_poly_a, g_seed_buf);
}

static uint64_t bench_poly_ntt(void) {
#if defined(BENCH_PRODUCTION_INPLACE)
  poly_ntt(&g_poly_b);
#else
  poly_ntt(&g_poly_b, &g_poly_a);
#endif
  return 0;
}

static uint64_t bench_poly_baseinv(void) {
  return (uint64_t)poly_baseinv(&g_poly_c, &g_poly_b);
}

static uint64_t bench_keygen(void) {
  return (uint64_t)crypto_kem_keypair(g_pk, g_sk);
}

#if defined(BENCH_GT_KEYPAIR_COMPARISON)
static uint64_t bench_keygen_gt(void) {
  return (uint64_t)crypto_kem_keypair_gt(g_pk, g_sk);
}
#endif

static uint64_t bench_encap(void) {
  return (uint64_t)crypto_kem_enc(g_ct, g_ss, g_pk);
}

static uint64_t bench_decap(void) {
  return (uint64_t)crypto_kem_dec(g_dss, g_ct, g_sk);
}

static void init_inputs(void) {
  for (size_t i = 0; i < sizeof(g_seed_buf); ++i) {
    g_seed_buf[i] = (uint8_t)((i * 17U + 3U) & 0xFFU);
  }
  for (size_t i = 0; i < sizeof(g_msg_buf); ++i) {
    g_msg_buf[i] = (uint8_t)((i * 29U + 11U) & 0xFFU);
  }
  memset(&g_poly_a, 0, sizeof(g_poly_a));
  memset(&g_poly_b, 0, sizeof(g_poly_b));
  memset(&g_poly_c, 0, sizeof(g_poly_c));

  for (int i = 0; i < NTRUPLUS_N; ++i) {
    g_poly_a.coeffs[i] = (int16_t)((i * 7) % 1223);
  }
#if defined(BENCH_PRODUCTION_INPLACE)
  g_poly_b = g_poly_a;
#endif
  if (crypto_kem_keypair(g_pk, g_sk) != 0 ||
      crypto_kem_enc(g_ct, g_ss, g_pk) != 0 ||
      crypto_kem_dec(g_dss, g_ct, g_sk) != 0 ||
      memcmp(g_ss, g_dss, CRYPTO_BYTES) != 0) {
    fprintf(stderr, "KEM self-check failed before benchmark\n");
    exit(1);
  }
#if defined(BENCH_GT_KEYPAIR_COMPARISON)
  if (crypto_kem_keypair_gt(g_pk, g_sk) != 0 ||
      crypto_kem_enc(g_ct, g_ss, g_pk) != 0 ||
      crypto_kem_dec(g_dss, g_ct, g_sk) != 0 ||
      memcmp(g_ss, g_dss, CRYPTO_BYTES) != 0) {
    fprintf(stderr, "GT keygen KEM self-check failed before benchmark\n");
    exit(1);
  }
#endif
}

static void print_stats_json(FILE *out, const char *name, stats_t s, int with_trailing_comma) {
  fprintf(out, "    \"%s\": {\n", name);
  fprintf(out, "      \"min\": %" PRIu64 ",\n", s.min);
  fprintf(out, "      \"median\": %.3f,\n", s.median);
  fprintf(out, "      \"mean\": %.3f,\n", s.mean);
  fprintf(out, "      \"stddev\": %.3f,\n", s.stddev);
  fprintf(out, "      \"max\": %" PRIu64 "\n", s.max);
  fprintf(out, "    }%s\n", with_trailing_comma ? "," : "");
}

int main(int argc, char **argv) {
  if (argc < 2 || argc > 4) {
    fprintf(stderr, "usage: %s <output_json> [iterations] [warmup]\n", argv[0]);
    return 1;
  }

  if (argc >= 3) {
    g_iterations = atoi(argv[2]);
  }
  if (argc >= 4) {
    g_warmup = atoi(argv[3]);
  }
  if (g_iterations <= 0 || g_warmup < 0) {
    fprintf(stderr, "invalid iterations/warmup values\n");
    return 1;
  }

  setup_counter_gap();
  init_inputs();

  stats_t cbd1 = run_bench(bench_poly_cbd1);
  stats_t sotp_encode = run_bench(bench_poly_sotp_encode);
  stats_t sotp_decode = run_bench(bench_poly_sotp_decode);
  stats_t ntt = run_bench(bench_poly_ntt);
  stats_t baseinv = run_bench(bench_poly_baseinv);
  stats_t keygen;
#if defined(BENCH_GT_KEYPAIR_COMPARISON)
  stats_t keygen_gt;
  run_bench_pair(bench_keygen, bench_keygen_gt, &keygen, &keygen_gt);
#else
  keygen = run_bench(bench_keygen);
#endif
  stats_t encap = run_bench(bench_encap);
  stats_t decap = run_bench(bench_decap);

  FILE *out = fopen(argv[1], "w");
  if (out == NULL) {
    perror("fopen");
    return 1;
  }

  fprintf(out, "{\n");
  fprintf(out, "  \"label\": \"%s\",\n", BENCH_LABEL);
  fprintf(out, "  \"unit\": \"%s\",\n", g_unit);
  fprintf(out, "  \"iterations\": %d,\n", g_iterations);
  fprintf(out, "  \"warmup\": %d,\n", g_warmup);
  fprintf(out, "  \"counter_gap\": %llu,\n", g_counter_gap);
  fprintf(out, "  \"results\": {\n");
  print_stats_json(out, "poly_cbd1", cbd1, 1);
  print_stats_json(out, "poly_sotp_encode", sotp_encode, 1);
  print_stats_json(out, "poly_sotp_decode", sotp_decode, 1);
  print_stats_json(out, "poly_ntt", ntt, 1);
  print_stats_json(out, "poly_baseinv", baseinv, 1);
  print_stats_json(out, "keygen", keygen, 1);
#if defined(BENCH_GT_KEYPAIR_COMPARISON)
  print_stats_json(out, "keygen_gt", keygen_gt, 1);
#endif
  print_stats_json(out, "encap", encap, 1);
  print_stats_json(out, "decap", decap, 0);
  fprintf(out, "  }\n");
  fprintf(out, "}\n");

  fclose(out);
  return 0;
}
