/*
 * Benchmark-only cross-backend gate for GT production encap with stock
 * poly_basemul_add.
 *
 * This does not change production defaults.  It checks whether the stock
 * NO_CE poly_basemul_add can be dropped into the GT production encap path,
 * then measures direct poly_basemul_add and full encap PMU windows.
 */
#if !defined(__linux__)
#error "bench_gt_stock_basemul_add_gate_pmu requires Linux perf_event_open"
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

#define PMU_EVENT_COUNT 8
#define VARIANT_COUNT 6
#define MSG_BYTES (NTRUPLUS_N / 8)
#define HASH_G_INPUT_BYTES NTRUPLUS_POLYBYTES

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
int bench_crypto_kem_enc_stock_basemul_add(uint8_t *ct, uint8_t *ss,
                                           const uint8_t *pk);
int bench_crypto_kem_enc_direct32_basemul_add(uint8_t *ct, uint8_t *ss,
                                              const uint8_t *pk);
int bench_crypto_kem_enc_direct32_q31_basemul_add(uint8_t *ct, uint8_t *ss,
                                                  const uint8_t *pk);

void poly_basemul_add_stock_noce_experimental(poly *r, const poly *a,
                                              const poly *b,
                                              const poly *c);
void poly_basemul_add_direct32_finalizer_prototype(poly *r, const poly *a,
                                                   const poly *b,
                                                   const poly *c);
void poly_basemul_add_direct32_q31_tobytes_contract_prototype(poly *r,
                                                              const poly *a,
                                                              const poly *b,
                                                              const poly *c);

typedef void (*basemul_add_fn)(poly *r, const poly *a, const poly *b,
                               const poly *c);
typedef void (*bench_target_fn)(size_t idx);

struct input_case
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t coins[MSG_BYTES];
  uint8_t ct_current[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ct_stock_add[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ct_direct32_add[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ct_direct32_q31_add[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ss_current[CRYPTO_BYTES];
  uint8_t ss_stock_add[CRYPTO_BYTES];
  uint8_t ss_direct32_add[CRYPTO_BYTES];
  uint8_t ss_direct32_q31_add[CRYPTO_BYTES];
  uint8_t hashg_current[HASH_G_INPUT_BYTES];
  uint8_t hashg_stock_add[HASH_G_INPUT_BYTES];
  uint8_t hashg_direct32_add[HASH_G_INPUT_BYTES];
  uint8_t hashg_direct32_q31_add[HASH_G_INPUT_BYTES];
  uint32_t key_seed;
  uint32_t enc_seed;
};

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
};

struct variant
{
  const char *name;
  bench_target_fn target;
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
  int pos;
};

static struct input_case *g_inputs;
static poly *g_h;
static poly *g_r;
static poly *g_m;
static poly *g_out_current;
static poly *g_out_stock_add;
static poly *g_out_direct32_add;
static poly *g_out_direct32_q31_add;
static uint8_t (*g_ct_workspace)[CRYPTO_CIPHERTEXTBYTES];
static uint8_t (*g_ss_workspace)[CRYPTO_BYTES];
static size_t g_iterations = NITERATIONS;
static uint32_t g_random_state = 0x12345678u;
static volatile uint64_t g_sink;
static int g_compare_prints;
static int g_stock_total_mismatches;
static int g_direct32_c_total_mismatches;
static int g_direct32_q31_total_mismatches;

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

static uint64_t checksum_bytes(const uint8_t *data, size_t len)
{
  uint64_t acc = 0x9e3779b97f4a7c15ULL;
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

static void print_limited_failure(const char *label, size_t input_idx,
                                  int fail)
{
  if (g_compare_prints < 32)
  {
    fprintf(stderr, "%s idx=%zu fail=%d\n", label, input_idx, fail);
    g_compare_prints++;
  }
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
      if (g_compare_prints < 32)
      {
        fprintf(stderr, "%s mismatch idx=%zu got=%u want=%u\n", label,
                byte_idx, got[byte_idx], want[byte_idx]);
        g_compare_prints++;
      }
      mismatches++;
    }
  }
  return mismatches;
}

static void encap_trace(uint8_t *ct, uint8_t *ss, uint8_t *hashg_input,
                        poly *h_out, poly *r_out, poly *m_out,
                        const uint8_t *pk, const uint8_t *coins,
                        basemul_add_fn basemul_add)
{
  uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
  uint8_t buf1[NTRUPLUS_SYMBYTES + NTRUPLUS_N / 4];
  uint8_t buf2[NTRUPLUS_POLYBYTES];
  poly c;
  size_t byte_idx;

  for (byte_idx = 0; byte_idx < MSG_BYTES; byte_idx++)
  {
    msg[byte_idx] = coins[byte_idx];
  }

  hash_f(msg + MSG_BYTES, pk);
  hash_h(buf1, msg);
  poly_cbd1(r_out, buf1 + NTRUPLUS_SYMBYTES);
  poly_ntt(r_out, r_out);

  poly_tobytes(hashg_input, r_out);
  memcpy(buf2, hashg_input, NTRUPLUS_POLYBYTES);
  hash_g(buf2, buf2);
  poly_sotp_encode(m_out, msg, buf2);
  poly_ntt(m_out, m_out);

  poly_frombytes(h_out, pk);
  basemul_add(&c, h_out, r_out, m_out);
  poly_tobytes(ct, &c);

  for (byte_idx = 0; byte_idx < NTRUPLUS_SSBYTES; byte_idx++)
  {
    ss[byte_idx] = buf1[byte_idx];
  }
}

static void current_basemul_add(poly *r, const poly *a, const poly *b,
                                const poly *c)
{
  poly_basemul_add(r, a, b, c);
}

static void stock_basemul_add(poly *r, const poly *a, const poly *b,
                              const poly *c)
{
  poly_basemul_add_stock_noce_experimental(r, a, b, c);
}

static void direct32_basemul_add(poly *r, const poly *a, const poly *b,
                                 const poly *c)
{
  poly_basemul_add_direct32_finalizer_prototype(r, a, b, c);
}

static void direct32_q31_basemul_add(poly *r, const poly *a, const poly *b,
                                     const poly *c)
{
  poly_basemul_add_direct32_q31_tobytes_contract_prototype(r, a, b, c);
}

static int prepare_inputs(void)
{
  int common_wrapper_mismatches = 0;
  int stock_ciphertext_mismatches = 0;
  int stock_hashg_input_mismatches = 0;
  int stock_shared_secret_mismatches = 0;
  int stock_kem_wrapper_mismatches = 0;
  int stock_decap_mismatches = 0;
  int direct32_ciphertext_mismatches = 0;
  int direct32_hashg_input_mismatches = 0;
  int direct32_shared_secret_mismatches = 0;
  int direct32_kem_wrapper_mismatches = 0;
  int direct32_decap_mismatches = 0;
  int direct32_q31_ciphertext_mismatches = 0;
  int direct32_q31_hashg_input_mismatches = 0;
  int direct32_q31_shared_secret_mismatches = 0;
  int direct32_q31_kem_wrapper_mismatches = 0;
  int direct32_q31_decap_mismatches = 0;
  int direct32_q31_tobytes_mismatches = 0;
  size_t input_idx;

  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    struct input_case *input = &g_inputs[input_idx];
    uint8_t ct_trace_current[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ct_trace_stock[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ct_trace_direct32[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ct_trace_direct32_q31[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss_trace_current[CRYPTO_BYTES];
    uint8_t ss_trace_stock[CRYPTO_BYTES];
    uint8_t ss_trace_direct32[CRYPTO_BYTES];
    uint8_t ss_trace_direct32_q31[CRYPTO_BYTES];
    uint8_t ss_dec_current[CRYPTO_BYTES];
    uint8_t ss_dec_stock[CRYPTO_BYTES];
    uint8_t ss_dec_direct32[CRYPTO_BYTES];
    uint8_t ss_dec_direct32_q31[CRYPTO_BYTES];
    uint8_t coins_check[MSG_BYTES];
    uint8_t tobytes_current[NTRUPLUS_POLYBYTES];
    uint8_t tobytes_direct32_q31[NTRUPLUS_POLYBYTES];
    poly h_stock;
    poly r_stock;
    poly m_stock;
    poly h_direct32;
    poly r_direct32;
    poly m_direct32;
    poly h_direct32_q31;
    poly r_direct32_q31;
    poly m_direct32_q31;
    int fail_current;
    int fail_stock;
    int fail_direct32;
    int fail_direct32_q31;

    input->key_seed = 0x31415926u + (uint32_t)(0x101u * input_idx);
    input->enc_seed = 0x27182818u + (uint32_t)(0x181u * input_idx);

    g_random_state = input->key_seed;
    if (bench_crypto_kem_keypair_current(input->pk, input->sk) != 0)
    {
      fprintf(stderr, "current keypair failed idx=%zu\n", input_idx);
      return -1;
    }

    g_random_state = input->enc_seed;
    randombytes(input->coins, sizeof(input->coins));

    g_random_state = input->enc_seed;
    if (bench_crypto_kem_enc_current(input->ct_current, input->ss_current,
                                     input->pk) != 0)
    {
      fprintf(stderr, "current enc failed idx=%zu\n", input_idx);
      return -1;
    }
    g_random_state = input->enc_seed;
    if (bench_crypto_kem_enc_stock_basemul_add(input->ct_stock_add,
                                               input->ss_stock_add,
                                               input->pk) != 0)
    {
      fprintf(stderr, "stock-add enc failed idx=%zu\n", input_idx);
      return -1;
    }
    g_random_state = input->enc_seed;
    if (bench_crypto_kem_enc_direct32_basemul_add(input->ct_direct32_add,
                                                  input->ss_direct32_add,
                                                  input->pk) != 0)
    {
      fprintf(stderr, "direct32-add enc failed idx=%zu\n", input_idx);
      return -1;
    }
    g_random_state = input->enc_seed;
    if (bench_crypto_kem_enc_direct32_q31_basemul_add(
            input->ct_direct32_q31_add, input->ss_direct32_q31_add,
            input->pk) != 0)
    {
      fprintf(stderr, "direct32-q31-add enc failed idx=%zu\n", input_idx);
      return -1;
    }
    g_random_state = input->enc_seed;
    randombytes(coins_check, sizeof(coins_check));
    common_wrapper_mismatches += compare_bytes("coins", coins_check,
                                               input->coins,
                                               sizeof(coins_check));

    encap_trace(ct_trace_current, ss_trace_current, input->hashg_current,
                &g_h[input_idx], &g_r[input_idx], &g_m[input_idx], input->pk,
                input->coins, current_basemul_add);
    encap_trace(ct_trace_stock, ss_trace_stock, input->hashg_stock_add,
                &h_stock, &r_stock, &m_stock, input->pk, input->coins,
                stock_basemul_add);
    encap_trace(ct_trace_direct32, ss_trace_direct32,
                input->hashg_direct32_add, &h_direct32, &r_direct32,
                &m_direct32, input->pk, input->coins, direct32_basemul_add);
    encap_trace(ct_trace_direct32_q31, ss_trace_direct32_q31,
                input->hashg_direct32_q31_add, &h_direct32_q31,
                &r_direct32_q31, &m_direct32_q31, input->pk, input->coins,
                direct32_q31_basemul_add);

    common_wrapper_mismatches += compare_bytes("current trace ct",
                                               ct_trace_current,
                                               input->ct_current,
                                               CRYPTO_CIPHERTEXTBYTES);
    common_wrapper_mismatches += compare_bytes("current trace ss",
                                               ss_trace_current,
                                               input->ss_current,
                                               CRYPTO_BYTES);
    stock_kem_wrapper_mismatches += compare_bytes("stock-add trace ct",
                                                  ct_trace_stock,
                                                  input->ct_stock_add,
                                                  CRYPTO_CIPHERTEXTBYTES);
    stock_kem_wrapper_mismatches += compare_bytes("stock-add trace ss",
                                                  ss_trace_stock,
                                                  input->ss_stock_add,
                                                  CRYPTO_BYTES);
    direct32_kem_wrapper_mismatches += compare_bytes("direct32-add trace ct",
                                                     ct_trace_direct32,
                                                     input->ct_direct32_add,
                                                     CRYPTO_CIPHERTEXTBYTES);
    direct32_kem_wrapper_mismatches += compare_bytes("direct32-add trace ss",
                                                     ss_trace_direct32,
                                                     input->ss_direct32_add,
                                                     CRYPTO_BYTES);
    direct32_q31_kem_wrapper_mismatches +=
        compare_bytes("direct32-q31-add trace ct", ct_trace_direct32_q31,
                      input->ct_direct32_q31_add, CRYPTO_CIPHERTEXTBYTES);
    direct32_q31_kem_wrapper_mismatches +=
        compare_bytes("direct32-q31-add trace ss", ss_trace_direct32_q31,
                      input->ss_direct32_q31_add, CRYPTO_BYTES);

    stock_ciphertext_mismatches += compare_bytes("stock cross ciphertext",
                                                 input->ct_stock_add,
                                                 input->ct_current,
                                                 CRYPTO_CIPHERTEXTBYTES);
    stock_hashg_input_mismatches += compare_bytes("stock cross hash_g input",
                                                  input->hashg_stock_add,
                                                  input->hashg_current,
                                                  HASH_G_INPUT_BYTES);
    stock_shared_secret_mismatches += compare_bytes("stock cross shared secret",
                                                    input->ss_stock_add,
                                                    input->ss_current,
                                                    CRYPTO_BYTES);
    direct32_ciphertext_mismatches +=
        compare_bytes("direct32 cross ciphertext", input->ct_direct32_add,
                      input->ct_current, CRYPTO_CIPHERTEXTBYTES);
    direct32_hashg_input_mismatches +=
        compare_bytes("direct32 cross hash_g input",
                      input->hashg_direct32_add, input->hashg_current,
                      HASH_G_INPUT_BYTES);
    direct32_shared_secret_mismatches +=
        compare_bytes("direct32 cross shared secret",
                      input->ss_direct32_add, input->ss_current,
                      CRYPTO_BYTES);
    direct32_q31_ciphertext_mismatches +=
        compare_bytes("direct32-q31 cross ciphertext",
                      input->ct_direct32_q31_add, input->ct_current,
                      CRYPTO_CIPHERTEXTBYTES);
    direct32_q31_hashg_input_mismatches +=
        compare_bytes("direct32-q31 cross hash_g input",
                      input->hashg_direct32_q31_add, input->hashg_current,
                      HASH_G_INPUT_BYTES);
    direct32_q31_shared_secret_mismatches +=
        compare_bytes("direct32-q31 cross shared secret",
                      input->ss_direct32_q31_add, input->ss_current,
                      CRYPTO_BYTES);

    poly_basemul_add(&g_out_current[input_idx], &g_h[input_idx],
                     &g_r[input_idx], &g_m[input_idx]);
    poly_basemul_add_direct32_q31_tobytes_contract_prototype(
        &g_out_direct32_q31_add[input_idx], &g_h[input_idx], &g_r[input_idx],
        &g_m[input_idx]);
    poly_tobytes(tobytes_current, &g_out_current[input_idx]);
    poly_tobytes(tobytes_direct32_q31, &g_out_direct32_q31_add[input_idx]);
    direct32_q31_tobytes_mismatches +=
        compare_bytes("direct32-q31 poly_tobytes", tobytes_direct32_q31,
                      tobytes_current, NTRUPLUS_POLYBYTES);

    fail_current = bench_crypto_kem_dec_current(ss_dec_current,
                                                input->ct_current,
                                                input->sk);
    fail_stock = bench_crypto_kem_dec_current(ss_dec_stock,
                                              input->ct_stock_add,
                                              input->sk);
    fail_direct32 = bench_crypto_kem_dec_current(ss_dec_direct32,
                                                input->ct_direct32_add,
                                                input->sk);
    fail_direct32_q31 =
        bench_crypto_kem_dec_current(ss_dec_direct32_q31,
                                     input->ct_direct32_q31_add, input->sk);
    if (fail_current != 0)
    {
      print_limited_failure("current dec failed", input_idx, fail_current);
      common_wrapper_mismatches++;
    }
    if (fail_stock != 0)
    {
      print_limited_failure("stock-add dec failed", input_idx, fail_stock);
      stock_decap_mismatches++;
    }
    if (fail_direct32 != 0)
    {
      print_limited_failure("direct32-add dec failed", input_idx,
                            fail_direct32);
      direct32_decap_mismatches++;
    }
    if (fail_direct32_q31 != 0)
    {
      print_limited_failure("direct32-q31-add dec failed", input_idx,
                            fail_direct32_q31);
      direct32_q31_decap_mismatches++;
    }
    common_wrapper_mismatches += compare_bytes("current dec ss",
                                               ss_dec_current,
                                               input->ss_current,
                                               CRYPTO_BYTES);
    stock_decap_mismatches += compare_bytes("stock-add dec ss", ss_dec_stock,
                                            input->ss_stock_add,
                                            CRYPTO_BYTES);
    direct32_decap_mismatches +=
        compare_bytes("direct32-add dec ss", ss_dec_direct32,
                      input->ss_direct32_add, CRYPTO_BYTES);
    direct32_q31_decap_mismatches +=
        compare_bytes("direct32-q31-add dec ss", ss_dec_direct32_q31,
                      input->ss_direct32_q31_add, CRYPTO_BYTES);
  }

  g_stock_total_mismatches =
      stock_ciphertext_mismatches + stock_hashg_input_mismatches +
      stock_shared_secret_mismatches + common_wrapper_mismatches +
      stock_kem_wrapper_mismatches + stock_decap_mismatches;
  g_direct32_c_total_mismatches =
      direct32_ciphertext_mismatches + direct32_hashg_input_mismatches +
      direct32_shared_secret_mismatches + common_wrapper_mismatches +
      direct32_kem_wrapper_mismatches + direct32_decap_mismatches;
  g_direct32_q31_total_mismatches =
      direct32_q31_ciphertext_mismatches +
      direct32_q31_hashg_input_mismatches +
      direct32_q31_shared_secret_mismatches + common_wrapper_mismatches +
      direct32_q31_kem_wrapper_mismatches + direct32_q31_decap_mismatches +
      direct32_q31_tobytes_mismatches;

  printf("stock_dropin_correctness,ciphertext_mismatches=%d,"
         "hash_g_input_mismatches=%d,shared_secret_mismatches=%d,"
         "common_wrapper_mismatches=%d,kem_wrapper_mismatches=%d,"
         "decap_mismatches=%d,total_mismatches=%d,valid_cases=%d\n",
         stock_ciphertext_mismatches, stock_hashg_input_mismatches,
         stock_shared_secret_mismatches, common_wrapper_mismatches,
         stock_kem_wrapper_mismatches, stock_decap_mismatches,
         g_stock_total_mismatches, NINPUTS);
  printf("direct32_correctness,ciphertext_mismatches=%d,"
         "hash_g_input_mismatches=%d,shared_secret_mismatches=%d,"
         "common_wrapper_mismatches=%d,kem_wrapper_mismatches=%d,"
         "decap_mismatches=%d,total_mismatches=%d,valid_cases=%d\n",
         direct32_ciphertext_mismatches, direct32_hashg_input_mismatches,
         direct32_shared_secret_mismatches, common_wrapper_mismatches,
         direct32_kem_wrapper_mismatches, direct32_decap_mismatches,
         g_direct32_c_total_mismatches, NINPUTS);
  printf("direct32_q31_correctness,ciphertext_mismatches=%d,"
         "hash_g_input_mismatches=%d,shared_secret_mismatches=%d,"
         "common_wrapper_mismatches=%d,kem_wrapper_mismatches=%d,"
         "decap_mismatches=%d,poly_tobytes_mismatches=%d,"
         "total_mismatches=%d,valid_cases=%d\n",
         direct32_q31_ciphertext_mismatches,
         direct32_q31_hashg_input_mismatches,
         direct32_q31_shared_secret_mismatches, common_wrapper_mismatches,
         direct32_q31_kem_wrapper_mismatches,
         direct32_q31_decap_mismatches, direct32_q31_tobytes_mismatches,
         g_direct32_q31_total_mismatches, NINPUTS);
  if (stock_ciphertext_mismatches != 0)
  {
    printf("layout_incompatibility=1,reason=stock_poly_basemul_add_output_"
           "differs_on_GT_operands\n");
  }
  else
  {
    printf("layout_incompatibility=0\n");
  }
  printf("direct32_byte_compatibility=%d\n",
         g_direct32_c_total_mismatches == 0);
  printf("direct32_q31_byte_compatibility=%d\n",
         g_direct32_q31_total_mismatches == 0);
  return g_direct32_c_total_mismatches + g_direct32_q31_total_mismatches;
}

static void checksum_outputs(void)
{
  size_t input_idx;

  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    uint64_t x = checksum_poly(&g_out_current[input_idx]);
    x ^= checksum_poly(&g_out_stock_add[input_idx]);
    x ^= checksum_poly(&g_out_direct32_add[input_idx]);
    x ^= checksum_poly(&g_out_direct32_q31_add[input_idx]);
    x ^= checksum_bytes(g_ct_workspace[input_idx], CRYPTO_CIPHERTEXTBYTES);
    x ^= checksum_bytes(g_ss_workspace[input_idx], CRYPTO_BYTES);
    g_sink ^= x + 0x9e3779b97f4a7c15ULL + (g_sink << 6) + (g_sink >> 2);
  }
}

static NOINLINE void target_empty(size_t idx)
{
  __asm__ volatile("" : : "r"(idx), "r"(g_inputs), "r"(g_out_current)
                   : "memory");
}

static NOINLINE void target_encap_basemul_add_current(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul_add(&g_out_current[input_idx], &g_h[input_idx],
                   &g_r[input_idx], &g_m[input_idx]);
}

static NOINLINE void target_encap_basemul_add_stock(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul_add_stock_noce_experimental(&g_out_stock_add[input_idx],
                                           &g_h[input_idx], &g_r[input_idx],
                                           &g_m[input_idx]);
}

static NOINLINE void target_encap_basemul_add_direct32(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul_add_direct32_finalizer_prototype(
      &g_out_direct32_add[input_idx], &g_h[input_idx], &g_r[input_idx],
      &g_m[input_idx]);
}

static NOINLINE void target_encap_basemul_add_direct32_q31(size_t idx)
{
  size_t input_idx = idx % NINPUTS;

  poly_basemul_add_direct32_q31_tobytes_contract_prototype(
      &g_out_direct32_q31_add[input_idx], &g_h[input_idx], &g_r[input_idx],
      &g_m[input_idx]);
}

static NOINLINE void target_encap_total_current(size_t idx)
{
  size_t input_idx = idx % NINPUTS;
  const struct input_case *input = &g_inputs[input_idx];

  g_random_state = input->enc_seed;
  (void)bench_crypto_kem_enc_current(g_ct_workspace[input_idx],
                                     g_ss_workspace[input_idx], input->pk);
}

static NOINLINE void target_encap_total_stock_basemul_add(size_t idx)
{
  size_t input_idx = idx % NINPUTS;
  const struct input_case *input = &g_inputs[input_idx];

  g_random_state = input->enc_seed;
  (void)bench_crypto_kem_enc_stock_basemul_add(g_ct_workspace[input_idx],
                                               g_ss_workspace[input_idx],
                                               input->pk);
}

static NOINLINE void target_encap_total_direct32_basemul_add(size_t idx)
{
  size_t input_idx = idx % NINPUTS;
  const struct input_case *input = &g_inputs[input_idx];

  g_random_state = input->enc_seed;
  (void)bench_crypto_kem_enc_direct32_basemul_add(g_ct_workspace[input_idx],
                                                  g_ss_workspace[input_idx],
                                                  input->pk);
}

static NOINLINE void target_encap_total_direct32_q31_basemul_add(size_t idx)
{
  size_t input_idx = idx % NINPUTS;
  const struct input_case *input = &g_inputs[input_idx];

  g_random_state = input->enc_seed;
  (void)bench_crypto_kem_enc_direct32_q31_basemul_add(
      g_ct_workspace[input_idx], g_ss_workspace[input_idx], input->pk);
}

static struct variant g_variants[VARIANT_COUNT] = {
    {"encap_basemul_add_current", target_encap_basemul_add_current},
    {"encap_basemul_add_stock_dropin", target_encap_basemul_add_stock},
    {"encap_basemul_add_direct32_c", target_encap_basemul_add_direct32},
    {"encap_basemul_add_direct32_q31_asm",
     target_encap_basemul_add_direct32_q31},
    {"encap_total_current", target_encap_total_current},
    {"encap_total_direct32_q31_optin",
     target_encap_total_direct32_q31_basemul_add},
};

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
            "sudo taskset -c 3 ./bench_gt_stock_basemul_add_gate_pmu_bin\n");
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

  printf("variant,cycles,instructions,cycles_per_call,instructions_per_call,"
         "ipc,branches,branch_misses,l1i_miss,l1d_load_miss,"
         "l1d_store_miss,cache_miss,min_cycles,p10_cycles,median_cycles,"
         "p90_cycles,samples,iterations\n");

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

    printf("%s,", g_variants[variant_loop_idx].name);
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
  int correctness_mismatches;

  g_inputs = xaligned_alloc(64, NINPUTS * sizeof(*g_inputs));
  g_h = xaligned_alloc(64, NINPUTS * sizeof(*g_h));
  g_r = xaligned_alloc(64, NINPUTS * sizeof(*g_r));
  g_m = xaligned_alloc(64, NINPUTS * sizeof(*g_m));
  g_out_current = xaligned_alloc(64, NINPUTS * sizeof(*g_out_current));
  g_out_stock_add = xaligned_alloc(64, NINPUTS * sizeof(*g_out_stock_add));
  g_out_direct32_add =
      xaligned_alloc(64, NINPUTS * sizeof(*g_out_direct32_add));
  g_out_direct32_q31_add =
      xaligned_alloc(64, NINPUTS * sizeof(*g_out_direct32_q31_add));
  g_ct_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_ct_workspace));
  g_ss_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_ss_workspace));

  correctness_mismatches = prepare_inputs();
  if (correctness_mismatches < 0)
  {
    return EXIT_FAILURE;
  }
  if (g_stock_total_mismatches != 0)
  {
    fprintf(stderr,
            "warning: stock poly_basemul_add drop-in is not correctness "
            "compatible; PMU results are diagnostic only\n");
  }
  if (correctness_mismatches != 0)
  {
    fprintf(stderr,
            "direct32 poly_basemul_add correctness failed; not running PMU\n");
    return EXIT_FAILURE;
  }

  setup_perf_events();
  run_benchmarks();
  close_perf_events();

  fprintf(stderr, "stock_basemul_add_gate_sink=%" PRIu64 "\n", g_sink);
  return EXIT_SUCCESS;
}
