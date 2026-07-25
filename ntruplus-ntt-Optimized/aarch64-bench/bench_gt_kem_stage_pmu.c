/*
 * Production-only GT KEM stage PMU breakdown.
 *
 * This harness measures the selected GT production variant and representative
 * keypair/encap/decap stages.  It deliberately does not enable rowspec,
 * ldrtrn, fused crep3, or other experiment gates.
 */
#if !defined(__linux__)
#error "bench_gt_kem_stage_pmu requires Linux perf_event_open"
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
#include "NO_CE/fips202.h"
#include "params.h"
#include "poly.h"
#include "randombytes.h"
#include "symmetric.h"

#ifndef NTESTS
#define NTESTS 31
#endif

#ifndef NITERATIONS
#define NITERATIONS 500
#endif

#ifndef NWARMUP
#define NWARMUP 50
#endif

#ifndef NINPUTS
#define NINPUTS 64
#endif

#define VARIANT_COUNT 20
#define PMU_EVENT_COUNT 8
#define HASH_H_INPUT_BYTES (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
#define HASH_H_OUTPUT_BYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)

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

int poly_baseinv_scaled_r(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
void poly_basemul(poly *r, const poly *a, const poly *b);
void poly_invntt(poly *r, const poly *a);
#ifdef GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3
void poly_ntt_mul3_add1(poly *out, const poly *a);
#endif

typedef void (*bench_target_fn)(size_t idx);

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
};

struct variant
{
  const char *name;
  bench_target_fn target;
  uint64_t text_size;
  uint64_t static_insns;
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
  int pos;
};

struct input_case
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ss_enc[CRYPTO_BYTES];
  uint8_t seed[32];
  uint8_t coins[HASH_H_INPUT_BYTES];
};

static struct input_case *g_inputs;
static uint8_t (*g_pk_workspace)[CRYPTO_PUBLICKEYBYTES];
static uint8_t (*g_sk_workspace)[CRYPTO_SECRETKEYBYTES];
static uint8_t (*g_ct_workspace)[CRYPTO_CIPHERTEXTBYTES];
static uint8_t (*g_ss_workspace)[CRYPTO_BYTES];
static uint8_t (*g_polybytes0)[NTRUPLUS_POLYBYTES];
static uint8_t (*g_polybytes1)[NTRUPLUS_POLYBYTES];
static uint8_t (*g_hashbuf)[NTRUPLUS_POLYBYTES];
static uint8_t (*g_msgbuf)[HASH_H_INPUT_BYTES];
static poly *g_c;
static poly *g_f;
static poly *g_hinv;
static poly *g_h;
static poly *g_r;
static poly *g_m;
static poly *g_m1_product;
static poly *g_m1_inv;
static poly *g_m1_crep;
static poly *g_m2;
static poly *g_csub;
static poly *g_r2;
static poly *g_baseinv0;
static poly *g_baseinv1;
static poly *g_poly_out0;
static poly *g_poly_out1;
static size_t g_iterations = NITERATIONS;
static uint32_t g_random_state = 0x12345678u;
static volatile uint64_t g_sink;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1, -1},
    {"branches", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_INSTRUCTIONS, -1,
     -1},
    {"branch_misses", PERF_TYPE_HARDWARE, PERF_COUNT_HW_BRANCH_MISSES, -1,
     -1},
    {"l1i_miss", PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1I | (PERF_COUNT_HW_CACHE_OP_READ << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16),
     -1, -1},
    {"l1d_load_miss", PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_READ << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16),
     -1, -1},
    {"l1d_store_miss", PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1D | (PERF_COUNT_HW_CACHE_OP_WRITE << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16),
     -1, -1},
    {"cache_miss", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CACHE_MISSES, -1, -1},
};

static int g_leader_fd = -1;
static int g_open_events;

static int perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                int cpu, int group_fd, unsigned long flags)
{
  return (int)syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static uint32_t next_u32(uint32_t *state)
{
  *state = *state * 1664525u + 1013904223u;
  return *state;
}

void randombytes(uint8_t *out, size_t outlen)
{
  size_t byte_idx;

  for (byte_idx = 0; byte_idx < outlen; byte_idx++)
  {
    if ((byte_idx & 3u) == 0u)
    {
      g_random_state = next_u32(&g_random_state);
    }
    out[byte_idx] = (uint8_t)(g_random_state >> ((byte_idx & 3u) * 8u));
  }
}

static int cmp_u64(const void *a, const void *b)
{
  const uint64_t aa = *(const uint64_t *)a;
  const uint64_t bb = *(const uint64_t *)b;

  return (aa > bb) - (aa < bb);
}

static void *xaligned_alloc(size_t alignment, size_t size)
{
  void *ptr = NULL;

  if (posix_memalign(&ptr, alignment, size) != 0)
  {
    fprintf(stderr, "posix_memalign failed for %zu bytes\n", size);
    exit(EXIT_FAILURE);
  }
  memset(ptr, 0, size);
  return ptr;
}

static int ct_verify_equal(const uint8_t *a, const uint8_t *b, size_t len)
{
  uint8_t acc = 0;
  size_t byte_idx;

  for (byte_idx = 0; byte_idx < len; byte_idx++)
  {
    acc |= (uint8_t)(a[byte_idx] ^ b[byte_idx]);
  }
  return (int)((-(uint64_t)acc) >> 63);
}

static uint64_t checksum_bytes(const uint8_t *data, size_t len)
{
  uint64_t acc = 0x6a09e667f3bcc909ULL;
  size_t byte_idx;

  for (byte_idx = 0; byte_idx < len; byte_idx++)
  {
    acc ^= data[byte_idx];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }
  return acc;
}

static uint64_t checksum_poly(const poly *a)
{
  uint64_t acc = 0xbb67ae8584caa73bULL;
  size_t coeff_idx;

  for (coeff_idx = 0; coeff_idx < NTRUPLUS_N; coeff_idx++)
  {
    acc ^= (uint16_t)a->coeffs[coeff_idx];
    acc *= 0x100000001b3ULL;
    acc ^= acc >> 32;
  }
  return acc;
}

static void checksum_outputs(void)
{
  size_t input_idx;

  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    uint64_t x = checksum_bytes(g_ss_workspace[input_idx], CRYPTO_BYTES);
    x ^= checksum_bytes(g_ct_workspace[input_idx], CRYPTO_CIPHERTEXTBYTES);
    x ^= checksum_bytes(g_polybytes0[input_idx], NTRUPLUS_POLYBYTES);
    x ^= checksum_poly(&g_poly_out0[input_idx]);
    x ^= checksum_poly(&g_poly_out1[input_idx]);
    g_sink ^= x + 0x9e3779b97f4a7c15ULL + (g_sink << 6) + (g_sink >> 2);
  }
}

static void fill_bytes(uint8_t *out, size_t len, uint32_t seed)
{
  size_t byte_idx;

  for (byte_idx = 0; byte_idx < len; byte_idx++)
  {
    if ((byte_idx & 3u) == 0u)
    {
      seed = next_u32(&seed);
    }
    out[byte_idx] = (uint8_t)(seed >> ((byte_idx & 3u) * 8u));
  }
}

static void sample_f_ntt_from_seed(poly *out, const uint8_t seed[32])
{
  uint8_t buf[NTRUPLUS_N / 4];

  shake256(buf, sizeof(buf), seed, 32);
  poly_cbd1(out, buf);
#ifdef GT_PRODUCTION_USE_KEYGEN_SAMPLE_NTT_MUL3
  poly_ntt_mul3_add1(out, out);
#else
  poly_triple(out, out);
  out->coeffs[0] += 1;
  poly_ntt(out, out);
#endif
}

static int compare_bytes(const char *label, const uint8_t *got,
                         const uint8_t *want, size_t len)
{
  size_t byte_idx;
  int mismatches = 0;

  for (byte_idx = 0; byte_idx < len; byte_idx++)
  {
    if (got[byte_idx] != want[byte_idx])
    {
      if (mismatches < 8)
      {
        fprintf(stderr, "%s mismatch idx=%zu got=%u want=%u\n", label,
                byte_idx, got[byte_idx], want[byte_idx]);
      }
      mismatches++;
    }
  }
  return mismatches;
}

static int prepare_inputs(void)
{
  size_t input_idx;
  int mismatches = 0;

  g_random_state = 0x31415926u;
  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    struct input_case *input = &g_inputs[input_idx];
    uint8_t ss_dec[CRYPTO_BYTES];
    uint8_t hash_h_buf[HASH_H_OUTPUT_BYTES];
    int fail;

    fill_bytes(input->seed, sizeof(input->seed),
               0x10000000u + (uint32_t)input_idx);
    fill_bytes(input->coins, sizeof(input->coins),
               0x20000000u + (uint32_t)input_idx);

    if (bench_crypto_kem_keypair_current(input->pk, input->sk) != 0)
    {
      fprintf(stderr, "keypair failed idx=%zu\n", input_idx);
      return -1;
    }
    if (bench_crypto_kem_enc_current(input->ct, input->ss_enc,
                                     input->pk) != 0)
    {
      fprintf(stderr, "enc failed idx=%zu\n", input_idx);
      return -1;
    }
    fail = bench_crypto_kem_dec_current(ss_dec, input->ct, input->sk);
    if (fail != 0)
    {
      fprintf(stderr, "dec failed idx=%zu fail=%d\n", input_idx, fail);
      mismatches++;
    }
    mismatches += compare_bytes("kem_dec.ss", ss_dec, input->ss_enc,
                                CRYPTO_BYTES);

    poly_frombytes(&g_c[input_idx], input->ct);
    poly_frombytes(&g_f[input_idx], input->sk);
    poly_frombytes(&g_hinv[input_idx], input->sk + NTRUPLUS_POLYBYTES);
    poly_frombytes(&g_h[input_idx], input->pk);

    poly_basemul(&g_m1_product[input_idx], &g_c[input_idx],
                         &g_f[input_idx]);
    poly_invntt(&g_m1_inv[input_idx],
                             &g_m1_product[input_idx]);
    poly_crepmod3(&g_m1_crep[input_idx], &g_m1_inv[input_idx]);
    poly_ntt(&g_m2[input_idx], &g_m1_crep[input_idx]);
    poly_sub(&g_csub[input_idx], &g_c[input_idx], &g_m2[input_idx]);
    poly_basemul(&g_r2[input_idx], &g_csub[input_idx],
                 &g_hinv[input_idx]);
    poly_tobytes(g_polybytes0[input_idx], &g_r2[input_idx]);
    hash_g(g_hashbuf[input_idx], g_polybytes0[input_idx]);
    (void)poly_sotp_decode(g_msgbuf[input_idx], &g_m1_crep[input_idx],
                           g_hashbuf[input_idx]);
    memcpy(g_msgbuf[input_idx] + NTRUPLUS_N / 8,
           input->sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
    hash_h(hash_h_buf, g_msgbuf[input_idx]);
    poly_cbd1(&g_r[input_idx], hash_h_buf + NTRUPLUS_SSBYTES);
    poly_ntt(&g_r[input_idx], &g_r[input_idx]);
    poly_tobytes(g_polybytes1[input_idx], &g_r[input_idx]);

    memcpy(g_msgbuf[input_idx], input->coins, NTRUPLUS_N / 8);
    hash_f(g_msgbuf[input_idx] + NTRUPLUS_N / 8, input->pk);
    hash_h(hash_h_buf, g_msgbuf[input_idx]);
    poly_cbd1(&g_r[input_idx], hash_h_buf + NTRUPLUS_SYMBYTES);
    poly_ntt(&g_r[input_idx], &g_r[input_idx]);
    poly_tobytes(g_polybytes0[input_idx], &g_r[input_idx]);
    hash_g(g_hashbuf[input_idx], g_polybytes0[input_idx]);
    poly_sotp_encode(&g_m[input_idx], g_msgbuf[input_idx],
                     g_hashbuf[input_idx]);
    poly_ntt(&g_m[input_idx], &g_m[input_idx]);

    sample_f_ntt_from_seed(&g_poly_out0[input_idx], input->seed);
    if (poly_baseinv_scaled_r(&g_baseinv0[input_idx], &g_f[input_idx]) != 0)
    {
      fprintf(stderr, "baseinv failed idx=%zu\n", input_idx);
      mismatches++;
    }
    if (poly_baseinv_scaled_r(&g_baseinv1[input_idx], &g_f[input_idx]) != 0)
    {
      fprintf(stderr, "baseinv2 failed idx=%zu\n", input_idx);
      mismatches++;
    }
  }

  printf("correctness,total_mismatches=%d,valid_cases=%d\n", mismatches,
         NINPUTS);
  return mismatches;
}

static NOINLINE void target_empty(size_t idx)
{
  __asm__ volatile("" : : "r"(idx), "r"(g_inputs), "r"(g_ss_workspace)
                   : "memory");
}

static NOINLINE void target_keypair_total(size_t idx)
{
  (void)bench_crypto_kem_keypair_current(g_pk_workspace[idx % NINPUTS],
                                         g_sk_workspace[idx % NINPUTS]);
}

static NOINLINE void target_encap_total(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];

  (void)bench_crypto_kem_enc_current(g_ct_workspace[idx % NINPUTS],
                                     g_ss_workspace[idx % NINPUTS],
                                     input->pk);
}

static NOINLINE void target_decap_total(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];

  (void)bench_crypto_kem_dec_current(g_ss_workspace[idx % NINPUTS], input->ct,
                                     input->sk);
}

static NOINLINE void target_keypair_sample_ntt(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];

  sample_f_ntt_from_seed(&g_poly_out0[idx % NINPUTS], input->seed);
}

static NOINLINE void target_keypair_baseinv_scaled_x2(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  (void)poly_baseinv_scaled_r(&g_baseinv0[input_idx], &g_f[input_idx]);
  (void)poly_baseinv_scaled_r(&g_baseinv1[input_idx], &g_f[input_idx]);
}

static NOINLINE void target_keypair_basemul_scaled_x2(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul_scaled_r_input(&g_poly_out0[input_idx], &g_f[input_idx],
                              &g_baseinv0[input_idx]);
  poly_basemul_scaled_r_input(&g_poly_out1[input_idx], &g_h[input_idx],
                              &g_baseinv1[input_idx]);
}

static NOINLINE void target_keypair_pack_hashf(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];
  size_t input_idx = idx % NINPUTS;

  poly_tobytes(g_pk_workspace[input_idx], &g_h[input_idx]);
  poly_tobytes(g_sk_workspace[input_idx], &g_f[input_idx]);
  poly_tobytes(g_sk_workspace[input_idx] + NTRUPLUS_POLYBYTES,
               &g_hinv[input_idx]);
  hash_f(g_sk_workspace[input_idx] + 2 * NTRUPLUS_POLYBYTES, input->pk);
}

static NOINLINE void target_encap_hash_cbd_ntt_r(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];
  size_t input_idx = idx % NINPUTS;
  uint8_t hash_h_buf[HASH_H_OUTPUT_BYTES];

  memcpy(g_msgbuf[input_idx], input->coins, NTRUPLUS_N / 8);
  hash_f(g_msgbuf[input_idx] + NTRUPLUS_N / 8, input->pk);
  hash_h(hash_h_buf, g_msgbuf[input_idx]);
  poly_cbd1(&g_r[input_idx], hash_h_buf + NTRUPLUS_SYMBYTES);
  poly_ntt(&g_r[input_idx], &g_r[input_idx]);
}

static NOINLINE void target_encap_pack_hashg_sotp_ntt_m(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_tobytes(g_polybytes0[input_idx], &g_r[input_idx]);
  hash_g(g_hashbuf[input_idx], g_polybytes0[input_idx]);
  poly_sotp_encode(&g_m[input_idx], g_msgbuf[input_idx],
                   g_hashbuf[input_idx]);
  poly_ntt(&g_m[input_idx], &g_m[input_idx]);
}

static NOINLINE void target_encap_frombytes_pk(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];

  poly_frombytes(&g_h[idx % NINPUTS], input->pk);
}

static NOINLINE void target_encap_basemul_add(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul_add(&g_c[input_idx], &g_h[input_idx], &g_r[input_idx],
                   &g_m[input_idx]);
}

static NOINLINE void target_encap_tobytes_ct(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_tobytes(g_ct_workspace[input_idx], &g_c[input_idx]);
}

static NOINLINE void target_decap_frombytes(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];
  size_t input_idx = idx % NINPUTS;

  poly_frombytes(&g_c[input_idx], input->ct);
  poly_frombytes(&g_f[input_idx], input->sk);
  poly_frombytes(&g_hinv[input_idx], input->sk + NTRUPLUS_POLYBYTES);
}

static NOINLINE void target_decap_basemul_rminus1(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul(&g_m1_product[input_idx], &g_c[input_idx],
                       &g_f[input_idx]);
}

static NOINLINE void target_decap_invntt_rminus1(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_invntt(&g_m1_inv[input_idx],
                           &g_m1_product[input_idx]);
}

static NOINLINE void target_decap_crepmod3(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_crepmod3(&g_m1_crep[input_idx], &g_m1_inv[input_idx]);
}

static NOINLINE void target_decap_ntt_sub(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_ntt(&g_m2[input_idx], &g_m1_crep[input_idx]);
  poly_sub(&g_csub[input_idx], &g_c[input_idx], &g_m2[input_idx]);
}

static NOINLINE void target_decap_verify_basemul(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul(&g_r2[input_idx], &g_csub[input_idx],
               &g_hinv[input_idx]);
}

static NOINLINE void target_decap_pack_hashg_sotp(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_tobytes(g_polybytes0[input_idx], &g_r2[input_idx]);
  hash_g(g_hashbuf[input_idx], g_polybytes0[input_idx]);
  (void)poly_sotp_decode(g_msgbuf[input_idx], &g_m1_crep[input_idx],
                         g_hashbuf[input_idx]);
}

static NOINLINE void target_decap_hashh_cbd_ntt_pack_verify(size_t idx)
{
  const struct input_case *input = &g_inputs[idx % NINPUTS];
  size_t input_idx = idx % NINPUTS;
  uint8_t hash_h_buf[HASH_H_OUTPUT_BYTES];
  int fail;

  memcpy(g_msgbuf[input_idx] + NTRUPLUS_N / 8,
         input->sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
  hash_h(hash_h_buf, g_msgbuf[input_idx]);
  poly_cbd1(&g_r[input_idx], hash_h_buf + NTRUPLUS_SSBYTES);
  poly_ntt(&g_r[input_idx], &g_r[input_idx]);
  poly_tobytes(g_polybytes1[input_idx], &g_r[input_idx]);
  fail = ct_verify_equal(g_polybytes0[input_idx], g_polybytes1[input_idx],
                         NTRUPLUS_POLYBYTES);
  g_ss_workspace[input_idx][0] ^= (uint8_t)fail;
}

static struct variant g_variants[VARIANT_COUNT] = {
    {"keypair_total", target_keypair_total, 0, 0},
    {"encap_total", target_encap_total, 0, 0},
    {"decap_total", target_decap_total, 0, 0},
    {"keypair_sample_ntt", target_keypair_sample_ntt, 0, 0},
    {"keypair_baseinv_scaled_x2", target_keypair_baseinv_scaled_x2, 0, 0},
    {"keypair_basemul_scaled_x2", target_keypair_basemul_scaled_x2, 0, 0},
    {"keypair_pack_hashf", target_keypair_pack_hashf, 0, 0},
    {"encap_hash_cbd_ntt_r", target_encap_hash_cbd_ntt_r, 0, 0},
    {"encap_pack_hashg_sotp_ntt_m", target_encap_pack_hashg_sotp_ntt_m, 0, 0},
    {"encap_frombytes_pk", target_encap_frombytes_pk, 0, 0},
    {"encap_basemul_add", target_encap_basemul_add, 0, 0},
    {"encap_tobytes_ct", target_encap_tobytes_ct, 0, 0},
    {"decap_frombytes", target_decap_frombytes, 0, 0},
    {"decap_basemul_rminus1", target_decap_basemul_rminus1, 0, 0},
    {"decap_invntt_rminus1", target_decap_invntt_rminus1, 0, 0},
    {"decap_crepmod3", target_decap_crepmod3, 0, 0},
    {"decap_ntt_sub", target_decap_ntt_sub, 0, 0},
    {"decap_verify_basemul", target_decap_verify_basemul, 0, 0},
    {"decap_pack_hashg_sotp", target_decap_pack_hashg_sotp, 0, 0},
    {"decap_hashh_cbd_ntt_pack_verify",
     target_decap_hashh_cbd_ntt_pack_verify, 0, 0},
};

static void load_static_stats(void)
{
  const char *path = getenv("GT_KEM_STAGE_STATS_FILE");
  FILE *stats;
  char line[512];

  if (path == NULL || path[0] == '\0')
  {
    return;
  }

  stats = fopen(path, "r");
  if (stats == NULL)
  {
    fprintf(stderr, "warning: could not open stats file %s: %s\n", path,
            strerror(errno));
    return;
  }

  while (fgets(line, sizeof(line), stats) != NULL)
  {
    char *name;
    char *text_size_str;
    char *static_insns_str;
    size_t variant_idx;

    if (line[0] == '#')
    {
      continue;
    }

    name = strtok(line, ",");
    text_size_str = strtok(NULL, ",");
    static_insns_str = strtok(NULL, ",");
    if (name == NULL || text_size_str == NULL || static_insns_str == NULL)
    {
      continue;
    }

    for (variant_idx = 0; variant_idx < VARIANT_COUNT; variant_idx++)
    {
      if (strcmp(name, g_variants[variant_idx].name) == 0)
      {
        g_variants[variant_idx].text_size =
            strtoull(text_size_str, NULL, 10);
        g_variants[variant_idx].static_insns =
            strtoull(static_insns_str, NULL, 10);
      }
    }
  }

  fclose(stats);
}

static void setup_perf_events(void)
{
  size_t event_idx;

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    struct perf_event_attr attr;

    memset(&attr, 0, sizeof(attr));
    attr.type = g_events[event_idx].type;
    attr.size = sizeof(attr);
    attr.config = g_events[event_idx].config;
    attr.disabled = (event_idx == 0) ? 1 : 0;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP | PERF_FORMAT_TOTAL_TIME_ENABLED |
                       PERF_FORMAT_TOTAL_TIME_RUNNING;

    g_events[event_idx].fd =
        perf_event_open_wrap(&attr, 0, -1, g_leader_fd, 0);
    if (g_events[event_idx].fd < 0)
    {
      fprintf(stderr, "warning: perf event %s unavailable: %s\n",
              g_events[event_idx].name, strerror(errno));
      g_events[event_idx].pos = -1;
      continue;
    }

    if (g_leader_fd < 0)
    {
      g_leader_fd = g_events[event_idx].fd;
    }
    g_events[event_idx].pos = g_open_events++;
  }

  if (g_leader_fd < 0)
  {
    fprintf(stderr,
            "perf_event_open failed for all events. Try: "
            "sudo taskset -c 3 ./bench_gt_kem_stage_pmu_bin\n");
    exit(EXIT_FAILURE);
  }
}

static void close_perf_events(void)
{
  size_t event_idx;

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    if (g_events[event_idx].fd >= 0)
    {
      close(g_events[event_idx].fd);
      g_events[event_idx].fd = -1;
    }
    g_events[event_idx].pos = -1;
  }
  g_leader_fd = -1;
  g_open_events = 0;
}

static void perf_measure(bench_target_fn target, struct counts *out)
{
  struct
  {
    uint64_t nr;
    uint64_t time_enabled;
    uint64_t time_running;
    uint64_t values[PMU_EVENT_COUNT];
  } data;
  size_t iter_idx;
  size_t event_idx;

  memset(out, 0, sizeof(*out));
  memset(&data, 0, sizeof(data));

  if (ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) != 0 ||
      ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP) != 0)
  {
    perror("perf ioctl enable");
    exit(EXIT_FAILURE);
  }

  for (iter_idx = 0; iter_idx < g_iterations; iter_idx++)
  {
    target(iter_idx);
  }

  if (ioctl(g_leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP) != 0)
  {
    perror("perf ioctl disable");
    exit(EXIT_FAILURE);
  }

  if (read(g_leader_fd, &data, sizeof(data)) < 0)
  {
    perror("perf read");
    exit(EXIT_FAILURE);
  }

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    int pos = g_events[event_idx].pos;
    uint64_t value;

    if (pos < 0 || (uint64_t)pos >= data.nr)
    {
      out->v[event_idx] = 0;
      continue;
    }
    value = data.values[pos];
    if (data.time_running != 0 && data.time_enabled > data.time_running)
    {
      long double scaled = (long double)value *
                           (long double)data.time_enabled /
                           (long double)data.time_running;
      value = (uint64_t)(scaled + 0.5L);
    }
    out->v[event_idx] = value;
  }
}

static void subtract_counts(struct counts *x, const struct counts *overhead)
{
  size_t event_idx;

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    if (x->v[event_idx] > overhead->v[event_idx])
    {
      x->v[event_idx] -= overhead->v[event_idx];
    }
    else
    {
      x->v[event_idx] = 0;
    }
  }
}

static struct counts median_overhead(void)
{
  struct counts samples[NTESTS];
  struct counts out;
  size_t sample_idx;
  size_t event_idx;

  for (sample_idx = 0; sample_idx < NTESTS; sample_idx++)
  {
    perf_measure(target_empty, &samples[sample_idx]);
  }

  memset(&out, 0, sizeof(out));
  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    uint64_t tmp[NTESTS];
    for (sample_idx = 0; sample_idx < NTESTS; sample_idx++)
    {
      tmp[sample_idx] = samples[sample_idx].v[event_idx];
    }
    qsort(tmp, NTESTS, sizeof(tmp[0]), cmp_u64);
    out.v[event_idx] = tmp[NTESTS / 2];
  }
  return out;
}

static uint64_t percentile_u64(uint64_t values[NTESTS], unsigned p)
{
  size_t idx = ((size_t)p * (NTESTS - 1)) / 100u;

  return values[idx];
}

static void print_event_value(const struct counts *counts, size_t event_idx)
{
  if (g_events[event_idx].pos < 0)
  {
    printf("na");
  }
  else
  {
    printf("%" PRIu64, counts->v[event_idx]);
  }
}

static void warmup_target(bench_target_fn target)
{
  size_t warm_idx;

  for (warm_idx = 0; warm_idx < NWARMUP; warm_idx++)
  {
    target(warm_idx);
  }
}

static void run_benchmarks(void)
{
  struct counts overhead;
  struct counts samples[VARIANT_COUNT][NTESTS];
  size_t sample_counts[VARIANT_COUNT];
  size_t round_idx;
  size_t variant_loop_idx;

  memset(sample_counts, 0, sizeof(sample_counts));
  overhead = median_overhead();

  for (round_idx = 0; round_idx < NTESTS; round_idx++)
  {
    int reverse = (round_idx & 1u) != 0u;
    for (variant_loop_idx = 0; variant_loop_idx < VARIANT_COUNT;
         variant_loop_idx++)
    {
      size_t variant_idx =
          reverse ? (VARIANT_COUNT - 1 - variant_loop_idx) : variant_loop_idx;
      size_t dst = sample_counts[variant_idx]++;

      warmup_target(g_variants[variant_idx].target);
      perf_measure(g_variants[variant_idx].target, &samples[variant_idx][dst]);
      subtract_counts(&samples[variant_idx][dst], &overhead);
      checksum_outputs();
    }
  }

  printf("variant,text_size,static_insns,cycles,instructions,"
         "cycles_per_call,instructions_per_call,ipc,branches,branch_misses,"
         "l1i_miss,l1d_load_miss,l1d_store_miss,cache_miss,min_cycles,"
         "p10_cycles,median_cycles,p90_cycles,samples,iterations\n");

  for (variant_loop_idx = 0; variant_loop_idx < VARIANT_COUNT;
       variant_loop_idx++)
  {
    struct counts median;
    uint64_t cycles_sorted[NTESTS];
    size_t event_idx;
    size_t sample_idx;
    double cycles_per_call;
    double instructions_per_call;
    double ipc;

    memset(&median, 0, sizeof(median));
    for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
    {
      uint64_t tmp[NTESTS];
      for (sample_idx = 0; sample_idx < NTESTS; sample_idx++)
      {
        tmp[sample_idx] = samples[variant_loop_idx][sample_idx].v[event_idx];
        if (event_idx == 0)
        {
          cycles_sorted[sample_idx] =
              samples[variant_loop_idx][sample_idx].v[event_idx];
        }
      }
      qsort(tmp, NTESTS, sizeof(tmp[0]), cmp_u64);
      median.v[event_idx] = tmp[NTESTS / 2];
    }
    qsort(cycles_sorted, NTESTS, sizeof(cycles_sorted[0]), cmp_u64);

    cycles_per_call = (double)median.v[0] / (double)g_iterations;
    instructions_per_call = (double)median.v[1] / (double)g_iterations;
    ipc = median.v[0] ? (double)median.v[1] / (double)median.v[0] : 0.0;

    printf("%s,%" PRIu64 ",%" PRIu64 ",", g_variants[variant_loop_idx].name,
           g_variants[variant_loop_idx].text_size,
           g_variants[variant_loop_idx].static_insns);
    print_event_value(&median, 0);
    printf(",");
    print_event_value(&median, 1);
    printf(",%.3f,%.3f,%.4f,", cycles_per_call, instructions_per_call, ipc);
    print_event_value(&median, 2);
    printf(",");
    print_event_value(&median, 3);
    printf(",");
    print_event_value(&median, 4);
    printf(",");
    print_event_value(&median, 5);
    printf(",");
    print_event_value(&median, 6);
    printf(",");
    print_event_value(&median, 7);
    printf(",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%d,%zu\n",
           cycles_sorted[0], percentile_u64(cycles_sorted, 10),
           cycles_sorted[NTESTS / 2], percentile_u64(cycles_sorted, 90),
           NTESTS, g_iterations);
  }
}

int main(void)
{
  g_inputs = xaligned_alloc(64, NINPUTS * sizeof(*g_inputs));
  g_pk_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_pk_workspace));
  g_sk_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_sk_workspace));
  g_ct_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_ct_workspace));
  g_ss_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_ss_workspace));
  g_polybytes0 = xaligned_alloc(64, NINPUTS * sizeof(*g_polybytes0));
  g_polybytes1 = xaligned_alloc(64, NINPUTS * sizeof(*g_polybytes1));
  g_hashbuf = xaligned_alloc(64, NINPUTS * sizeof(*g_hashbuf));
  g_msgbuf = xaligned_alloc(64, NINPUTS * sizeof(*g_msgbuf));
  g_c = xaligned_alloc(64, NINPUTS * sizeof(*g_c));
  g_f = xaligned_alloc(64, NINPUTS * sizeof(*g_f));
  g_hinv = xaligned_alloc(64, NINPUTS * sizeof(*g_hinv));
  g_h = xaligned_alloc(64, NINPUTS * sizeof(*g_h));
  g_r = xaligned_alloc(64, NINPUTS * sizeof(*g_r));
  g_m = xaligned_alloc(64, NINPUTS * sizeof(*g_m));
  g_m1_product = xaligned_alloc(64, NINPUTS * sizeof(*g_m1_product));
  g_m1_inv = xaligned_alloc(64, NINPUTS * sizeof(*g_m1_inv));
  g_m1_crep = xaligned_alloc(64, NINPUTS * sizeof(*g_m1_crep));
  g_m2 = xaligned_alloc(64, NINPUTS * sizeof(*g_m2));
  g_csub = xaligned_alloc(64, NINPUTS * sizeof(*g_csub));
  g_r2 = xaligned_alloc(64, NINPUTS * sizeof(*g_r2));
  g_baseinv0 = xaligned_alloc(64, NINPUTS * sizeof(*g_baseinv0));
  g_baseinv1 = xaligned_alloc(64, NINPUTS * sizeof(*g_baseinv1));
  g_poly_out0 = xaligned_alloc(64, NINPUTS * sizeof(*g_poly_out0));
  g_poly_out1 = xaligned_alloc(64, NINPUTS * sizeof(*g_poly_out1));

  if (prepare_inputs() != 0)
  {
    return EXIT_FAILURE;
  }

  bench_print_gt_production_config();
  load_static_stats();
  setup_perf_events();
  run_benchmarks();
  close_perf_events();

  fprintf(stderr, "sink=%" PRIu64 "\n", g_sink);
  return EXIT_SUCCESS;
}
