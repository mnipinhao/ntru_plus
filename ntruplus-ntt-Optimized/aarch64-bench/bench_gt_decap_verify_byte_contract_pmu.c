/*
 * PMU and correctness harness for the decap verify
 * poly_basemul -> poly_tobytes byte-contract boundary.
 *
 * This harness is intentionally benchmark-only.  The reference helper measured
 * here still calls poly_basemul followed by poly_tobytes; it exists to lock the
 * future optimized helper's API and correctness oracle.
 */
#if !defined(__linux__)
#error "bench_gt_decap_verify_byte_contract_pmu requires Linux perf_event_open"
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
#define NINPUTS 256
#endif

#define HASH_G_BYTES (NTRUPLUS_N / 4)
#define HASH_H_INPUT_BYTES (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
#define HASH_H_OUTPUT_BYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)
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
int bench_crypto_kem_dec_decap_verify_contract_ref(uint8_t *ss,
                                                   const uint8_t *ct,
                                                   const uint8_t *sk);

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void gt_decap_verify_basemul_tobytes_contract_ref(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv);

typedef void (*bench_target_fn)(size_t idx);

struct input_case
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ss_enc[CRYPTO_BYTES];
};

struct decap_trace
{
  uint8_t buf1[NTRUPLUS_POLYBYTES];
  uint8_t hashg_out[HASH_G_BYTES];
  uint8_t msg[HASH_H_INPUT_BYTES];
  uint8_t hashh_out[HASH_H_OUTPUT_BYTES];
  uint8_t r1_bytes[NTRUPLUS_POLYBYTES];
  uint8_t ss[CRYPTO_BYTES];
  int sotp_fail;
  int verify_fail;
  int final_fail;
};

struct pmu_event
{
  const char *name;
  uint32_t type;
  uint64_t config;
  int fd;
  int pos;
};

struct variant
{
  const char *name;
  bench_target_fn target;
};

struct counts
{
  uint64_t v[PMU_EVENT_COUNT];
};

static struct input_case *g_inputs;
static poly *g_cminus_m2;
static poly *g_hinv;
static poly *g_r2;
static poly *g_synth_a;
static poly *g_synth_b;
static poly *g_tmp_poly;
static uint8_t (*g_bytes0)[NTRUPLUS_POLYBYTES];
static uint8_t (*g_bytes1)[NTRUPLUS_POLYBYTES];
static uint8_t (*g_ss_workspace)[CRYPTO_BYTES];
static uint32_t g_random_state = 0x5eed1234u;
static uint64_t g_iterations = NITERATIONS;
static volatile uint64_t g_sink;

static struct pmu_event g_events[PMU_EVENT_COUNT] = {
    {"cycles", PERF_TYPE_HARDWARE, PERF_COUNT_HW_CPU_CYCLES, -1, -1},
    {"instructions", PERF_TYPE_HARDWARE, PERF_COUNT_HW_INSTRUCTIONS, -1, -1},
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

static uint8_t prng_byte(void)
{
  static uint32_t byte_state = 0x9e3779b9u;

  byte_state = next_u32(&byte_state);
  return (uint8_t)(byte_state >> 24);
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

static int compare_bytes(const char *label, const uint8_t *a, const uint8_t *b,
                         size_t len)
{
  size_t byte_idx;

  for (byte_idx = 0; byte_idx < len; byte_idx++)
  {
    if (a[byte_idx] != b[byte_idx])
    {
      fprintf(stderr,
              "%s mismatch at byte %zu: got=%u want=%u\n",
              label, byte_idx, (unsigned)a[byte_idx],
              (unsigned)b[byte_idx]);
      return 1;
    }
  }
  return 0;
}

static void fill_random_poly(poly *p)
{
  size_t coeff_idx;

  for (coeff_idx = 0; coeff_idx < NTRUPLUS_N; coeff_idx++)
  {
    const int value = (int)(prng_byte() | ((unsigned)prng_byte() << 8));
    p->coeffs[coeff_idx] = (int16_t)((value % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q);
  }
}

static void fill_boundary_poly(poly *p, size_t salt)
{
  static const int16_t values[] = {
      0, 1, -1, NTRUPLUS_Q - 1, -(NTRUPLUS_Q - 1),
      NTRUPLUS_Q, -NTRUPLUS_Q, 1728, -1728, 4095, -4095,
  };
  size_t coeff_idx;

  for (coeff_idx = 0; coeff_idx < NTRUPLUS_N; coeff_idx++)
  {
    p->coeffs[coeff_idx] =
        values[(coeff_idx + salt) % (sizeof(values) / sizeof(values[0]))];
  }
}

static void make_malformed_coeff_bytes(uint8_t out[CRYPTO_CIPHERTEXTBYTES])
{
  size_t pair_idx;

  for (pair_idx = 0; pair_idx < NTRUPLUS_N / 2; pair_idx++)
  {
    const uint16_t a = (uint16_t)(NTRUPLUS_Q + 1 + (pair_idx % 638));
    const uint16_t b = (uint16_t)(4095 - (pair_idx % 638));

    out[3 * pair_idx + 0] = (uint8_t)a;
    out[3 * pair_idx + 1] = (uint8_t)((a >> 8) | (b << 4));
    out[3 * pair_idx + 2] = (uint8_t)(b >> 4);
  }
}

static void derive_decap_verify_operands(poly *c_minus_m2, poly *hinv,
                                         const uint8_t *ct,
                                         const uint8_t *sk)
{
  poly c;
  poly f;
  poly m1;
  poly m2;

  poly_frombytes(&c, ct);
  poly_frombytes(&f, sk);
  poly_frombytes(hinv, sk + NTRUPLUS_POLYBYTES);

  poly_basemul_rminus1(&m1, &c, &f);
  poly_invntt_from_rminus1(&m1, &m1);
  poly_crepmod3(&m1, &m1);
  poly_ntt(&m2, &m1);
  poly_sub(c_minus_m2, &c, &m2);
}

static int compare_contract_bytes(const char *label, const poly *c_minus_m2,
                                  const poly *hinv)
{
  poly r2;
  uint8_t reference[NTRUPLUS_POLYBYTES];
  uint8_t contract[NTRUPLUS_POLYBYTES];

  poly_basemul(&r2, c_minus_m2, hinv);
  poly_tobytes(reference, &r2);
  gt_decap_verify_basemul_tobytes_contract_ref(contract, c_minus_m2, hinv);

  return compare_bytes(label, contract, reference, NTRUPLUS_POLYBYTES);
}

static int decap_trace(struct decap_trace *trace, const uint8_t *ct,
                       const uint8_t *sk, int use_contract)
{
  poly c;
  poly f;
  poly hinv;
  poly r1;
  poly r2;
  poly m1;
  poly m2;
  size_t byte_idx;

  memset(trace, 0, sizeof(*trace));

  poly_frombytes(&c, ct);
  poly_frombytes(&f, sk);
  poly_frombytes(&hinv, sk + NTRUPLUS_POLYBYTES);

  poly_basemul_rminus1(&m1, &c, &f);
  poly_invntt_from_rminus1(&m1, &m1);
  poly_crepmod3(&m1, &m1);

  poly_ntt(&m2, &m1);
  poly_sub(&c, &c, &m2);

  if (use_contract)
  {
    gt_decap_verify_basemul_tobytes_contract_ref(trace->buf1, &c, &hinv);
  }
  else
  {
    poly_basemul(&r2, &c, &hinv);
    poly_tobytes(trace->buf1, &r2);
  }

  hash_g(trace->hashg_out, trace->buf1);
  trace->sotp_fail = poly_sotp_decode(trace->msg, &m1, trace->hashg_out);

  for (byte_idx = 0; byte_idx < NTRUPLUS_SYMBYTES; byte_idx++)
  {
    trace->msg[byte_idx + NTRUPLUS_N / 8] =
        sk[byte_idx + 2 * NTRUPLUS_POLYBYTES];
  }

  hash_h(trace->hashh_out, trace->msg);
  poly_cbd1(&r1, trace->hashh_out + NTRUPLUS_SSBYTES);
  poly_ntt(&r1, &r1);
  poly_tobytes(trace->r1_bytes, &r1);

  trace->verify_fail =
      ct_verify_equal(trace->buf1, trace->r1_bytes, NTRUPLUS_POLYBYTES);
  trace->final_fail = trace->sotp_fail | trace->verify_fail;

  for (byte_idx = 0; byte_idx < NTRUPLUS_SSBYTES; byte_idx++)
  {
    trace->ss[byte_idx] =
        (uint8_t)(trace->hashh_out[byte_idx] & ~(-trace->final_fail));
  }

  return trace->final_fail;
}

static int compare_decap_traces(const char *label, const struct decap_trace *a,
                                const struct decap_trace *b)
{
  int mismatches = 0;

  mismatches += compare_bytes(label, a->buf1, b->buf1, NTRUPLUS_POLYBYTES);
  mismatches +=
      compare_bytes("hash_g output", a->hashg_out, b->hashg_out, HASH_G_BYTES);
  mismatches +=
      compare_bytes("hash_h input msg", a->msg, b->msg, HASH_H_INPUT_BYTES);
  mismatches += compare_bytes("hash_h output", a->hashh_out, b->hashh_out,
                              HASH_H_OUTPUT_BYTES);
  mismatches += compare_bytes("r1 tobytes", a->r1_bytes, b->r1_bytes,
                              NTRUPLUS_POLYBYTES);
  mismatches += compare_bytes("shared secret", a->ss, b->ss, CRYPTO_BYTES);

  if (a->sotp_fail != b->sotp_fail)
  {
    fprintf(stderr, "%s sotp_fail mismatch: got=%d want=%d\n", label,
            b->sotp_fail, a->sotp_fail);
    mismatches++;
  }
  if (a->verify_fail != b->verify_fail)
  {
    fprintf(stderr, "%s verify_fail mismatch: got=%d want=%d\n", label,
            b->verify_fail, a->verify_fail);
    mismatches++;
  }
  if (a->final_fail != b->final_fail)
  {
    fprintf(stderr, "%s final_fail mismatch: got=%d want=%d\n", label,
            b->final_fail, a->final_fail);
    mismatches++;
  }

  return mismatches;
}

static int direct_byte_oracle_test(void)
{
  int mismatches = 0;
  size_t input_idx;

  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    uint8_t malformed_ct[CRYPTO_CIPHERTEXTBYTES];
    char label[80];

    snprintf(label, sizeof(label), "valid_decap_derived_%zu", input_idx);
    mismatches += compare_contract_bytes(label, &g_cminus_m2[input_idx],
                                         &g_hinv[input_idx]);

    fill_random_poly(&g_synth_a[input_idx]);
    fill_random_poly(&g_synth_b[input_idx]);
    snprintf(label, sizeof(label), "synthetic_random_%zu", input_idx);
    mismatches += compare_contract_bytes(label, &g_synth_a[input_idx],
                                         &g_synth_b[input_idx]);

    fill_boundary_poly(&g_synth_a[input_idx], input_idx);
    fill_boundary_poly(&g_synth_b[input_idx], input_idx + 5);
    snprintf(label, sizeof(label), "synthetic_boundary_%zu", input_idx);
    mismatches += compare_contract_bytes(label, &g_synth_a[input_idx],
                                         &g_synth_b[input_idx]);

    make_malformed_coeff_bytes(malformed_ct);
    derive_decap_verify_operands(&g_synth_a[input_idx], &g_synth_b[input_idx],
                                 malformed_ct, g_inputs[input_idx].sk);
    snprintf(label, sizeof(label), "malformed_frombytes_%zu", input_idx);
    mismatches += compare_contract_bytes(label, &g_synth_a[input_idx],
                                         &g_synth_b[input_idx]);
  }

  printf("verify_basemul_tobytes_mismatches=%d\n", mismatches);
  return mismatches;
}

static void make_case_ct(uint8_t out[CRYPTO_CIPHERTEXTBYTES],
                         const struct input_case *input, size_t input_idx,
                         unsigned case_id)
{
  size_t byte_idx;

  switch (case_id)
  {
  case 0:
    memcpy(out, input->ct, CRYPTO_CIPHERTEXTBYTES);
    break;
  case 1:
    memcpy(out, input->ct, CRYPTO_CIPHERTEXTBYTES);
    out[input_idx % CRYPTO_CIPHERTEXTBYTES] ^=
        (uint8_t)(1u << (input_idx & 7u));
    break;
  case 2:
    for (byte_idx = 0; byte_idx < CRYPTO_CIPHERTEXTBYTES; byte_idx++)
    {
      out[byte_idx] = prng_byte();
    }
    break;
  case 3:
    memset(out, 0, CRYPTO_CIPHERTEXTBYTES);
    break;
  case 4:
    memset(out, 0xff, CRYPTO_CIPHERTEXTBYTES);
    break;
  default:
    make_malformed_coeff_bytes(out);
    break;
  }
}

static int full_decap_differential_test(void)
{
  enum
  {
    CASE_COUNT = 6
  };
  static const char *case_names[CASE_COUNT] = {
      "valid", "single_bit_flip", "random", "all_zero", "all_ff",
      "malformed_12bit",
  };
  int total_mismatches = 0;
  int valid_cases = 0;
  int invalid_cases = 0;
  size_t input_idx;

  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    unsigned case_id;

    for (case_id = 0; case_id < CASE_COUNT; case_id++)
    {
      uint8_t ct_case[CRYPTO_CIPHERTEXTBYTES];
      uint8_t ss_current[CRYPTO_BYTES];
      uint8_t ss_contract[CRYPTO_BYTES];
      struct decap_trace current_trace;
      struct decap_trace contract_trace;
      int fail_current_trace;
      int fail_contract_trace;
      int fail_current_api;
      int fail_contract_api;
      char label[96];

      make_case_ct(ct_case, &g_inputs[input_idx], input_idx, case_id);
      snprintf(label, sizeof(label), "%s_%zu", case_names[case_id],
               input_idx);

      fail_current_trace =
          decap_trace(&current_trace, ct_case, g_inputs[input_idx].sk, 0);
      fail_contract_trace =
          decap_trace(&contract_trace, ct_case, g_inputs[input_idx].sk, 1);

      total_mismatches += compare_decap_traces(label, &current_trace,
                                               &contract_trace);
      if (fail_current_trace != fail_contract_trace)
      {
        fprintf(stderr, "%s trace fail mismatch: got=%d want=%d\n", label,
                fail_contract_trace, fail_current_trace);
        total_mismatches++;
      }

      fail_current_api =
          bench_crypto_kem_dec_current(ss_current, ct_case,
                                       g_inputs[input_idx].sk);
      fail_contract_api =
          bench_crypto_kem_dec_decap_verify_contract_ref(
              ss_contract, ct_case, g_inputs[input_idx].sk);

      if (fail_current_api != fail_contract_api)
      {
        fprintf(stderr, "%s api fail mismatch: got=%d want=%d\n", label,
                fail_contract_api, fail_current_api);
        total_mismatches++;
      }
      total_mismatches +=
          compare_bytes("api shared secret", ss_contract, ss_current,
                        CRYPTO_BYTES);

      if (case_id == 0)
      {
        valid_cases++;
        if (fail_current_api != 0 ||
            compare_bytes("valid ss vs enc ss", ss_current,
                          g_inputs[input_idx].ss_enc, CRYPTO_BYTES) != 0)
        {
          fprintf(stderr, "%s valid decap failed current path\n", label);
          total_mismatches++;
        }
      }
      else
      {
        invalid_cases++;
      }
    }
  }

  printf("decap_verify_contract_total_mismatches=%d,valid_cases=%d,"
         "invalid_cases=%d\n",
         total_mismatches, valid_cases, invalid_cases);
  return total_mismatches;
}

static void prepare_inputs(void)
{
  size_t input_idx;

  for (input_idx = 0; input_idx < NINPUTS; input_idx++)
  {
    if (bench_crypto_kem_keypair_current(g_inputs[input_idx].pk,
                                         g_inputs[input_idx].sk) != 0)
    {
      fprintf(stderr, "keypair failed idx=%zu\n", input_idx);
      exit(EXIT_FAILURE);
    }
    if (bench_crypto_kem_enc_current(g_inputs[input_idx].ct,
                                     g_inputs[input_idx].ss_enc,
                                     g_inputs[input_idx].pk) != 0)
    {
      fprintf(stderr, "enc failed idx=%zu\n", input_idx);
      exit(EXIT_FAILURE);
    }

    derive_decap_verify_operands(&g_cminus_m2[input_idx], &g_hinv[input_idx],
                                 g_inputs[input_idx].ct,
                                 g_inputs[input_idx].sk);
    poly_basemul(&g_r2[input_idx], &g_cminus_m2[input_idx],
                 &g_hinv[input_idx]);
    poly_tobytes(g_bytes0[input_idx], &g_r2[input_idx]);
  }
}

static int open_events(void)
{
  struct perf_event_attr attr;
  int group_fd = -1;
  int event_idx;

  memset(&attr, 0, sizeof(attr));
  attr.size = sizeof(attr);
  attr.disabled = 1;
  attr.exclude_kernel = 1;
  attr.exclude_hv = 1;
  attr.read_format = PERF_FORMAT_GROUP;

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    attr.type = g_events[event_idx].type;
    attr.config = g_events[event_idx].config;
    g_events[event_idx].fd =
        perf_event_open_wrap(&attr, 0, -1, group_fd, 0);
    if (g_events[event_idx].fd < 0)
    {
      fprintf(stderr, "perf_event_open(%s) failed: %s\n",
              g_events[event_idx].name, strerror(errno));
      break;
    }
    if (group_fd < 0)
    {
      group_fd = g_events[event_idx].fd;
      g_leader_fd = group_fd;
    }
    g_events[event_idx].pos = event_idx;
    g_open_events++;
  }

  return g_open_events > 0 ? 0 : -1;
}

static void close_events(void)
{
  int event_idx;

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    if (g_events[event_idx].fd >= 0)
    {
      close(g_events[event_idx].fd);
      g_events[event_idx].fd = -1;
    }
  }
  g_leader_fd = -1;
  g_open_events = 0;
}

static void read_counts(struct counts *out)
{
  uint64_t buffer[1 + PMU_EVENT_COUNT];
  ssize_t got;
  int event_idx;

  memset(buffer, 0, sizeof(buffer));
  got = read(g_leader_fd, buffer, sizeof(uint64_t) * (1 + g_open_events));
  if (got < 0)
  {
    perror("read perf counters");
    exit(EXIT_FAILURE);
  }

  for (event_idx = 0; event_idx < PMU_EVENT_COUNT; event_idx++)
  {
    out->v[event_idx] = event_idx < g_open_events ? buffer[1 + event_idx] : 0;
  }
}

static void target_decap_verify_basemul(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_basemul(&g_tmp_poly[input_idx], &g_cminus_m2[input_idx],
               &g_hinv[input_idx]);
  g_sink ^= (uint16_t)g_tmp_poly[input_idx].coeffs[idx & (NTRUPLUS_N - 1)];
}

static void target_decap_tobytes_r2(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_tobytes(g_bytes1[input_idx], &g_r2[input_idx]);
  g_sink ^= g_bytes1[input_idx][idx & (NTRUPLUS_POLYBYTES - 1)];
}

static void target_decap_verify_basemul_plus_tobytes(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  poly_basemul(&g_tmp_poly[input_idx], &g_cminus_m2[input_idx],
               &g_hinv[input_idx]);
  poly_tobytes(g_bytes1[input_idx], &g_tmp_poly[input_idx]);
  g_sink ^= g_bytes1[input_idx][idx & (NTRUPLUS_POLYBYTES - 1)];
}

static void target_decap_verify_contract_ref(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  gt_decap_verify_basemul_tobytes_contract_ref(g_bytes1[input_idx],
                                               &g_cminus_m2[input_idx],
                                               &g_hinv[input_idx]);
  g_sink ^= g_bytes1[input_idx][idx & (NTRUPLUS_POLYBYTES - 1)];
}

static void target_full_decap_current(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  g_sink ^= (uint64_t)bench_crypto_kem_dec_current(
      g_ss_workspace[input_idx], g_inputs[input_idx].ct,
      g_inputs[input_idx].sk);
  g_sink ^= g_ss_workspace[input_idx][idx & (CRYPTO_BYTES - 1)];
}

static void target_full_decap_contract_ref(size_t idx)
{
  const size_t input_idx = idx % NINPUTS;

  g_sink ^= (uint64_t)bench_crypto_kem_dec_decap_verify_contract_ref(
      g_ss_workspace[input_idx], g_inputs[input_idx].ct,
      g_inputs[input_idx].sk);
  g_sink ^= g_ss_workspace[input_idx][idx & (CRYPTO_BYTES - 1)];
}

static void measure_variant(const struct variant *variant)
{
  uint64_t cycle_samples[NTESTS];
  uint64_t instr_samples[NTESTS];
  uint64_t test_idx;
  uint64_t warm_idx;
  uint64_t iter_idx;

  for (test_idx = 0; test_idx < NTESTS; test_idx++)
  {
    struct counts before;
    struct counts after;

    for (warm_idx = 0; warm_idx < NWARMUP; warm_idx++)
    {
      variant->target(warm_idx);
    }

    if (ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP) != 0 ||
        ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP) != 0)
    {
      perror("enable perf counters");
      exit(EXIT_FAILURE);
    }
    read_counts(&before);
    for (iter_idx = 0; iter_idx < g_iterations; iter_idx++)
    {
      variant->target(iter_idx);
    }
    read_counts(&after);
    if (ioctl(g_leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP) != 0)
    {
      perror("disable perf counters");
      exit(EXIT_FAILURE);
    }

    cycle_samples[test_idx] =
        (after.v[0] - before.v[0]) / (uint64_t)g_iterations;
    instr_samples[test_idx] =
        (after.v[1] - before.v[1]) / (uint64_t)g_iterations;
  }

  qsort(cycle_samples, NTESTS, sizeof(cycle_samples[0]), cmp_u64);
  qsort(instr_samples, NTESTS, sizeof(instr_samples[0]), cmp_u64);

  printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_p25=%" PRIu64
         ",cycles_p75=%" PRIu64 ",cycles_iqr=%" PRIu64
         ",instr_p50=%" PRIu64 "\n",
         variant->name, cycle_samples[NTESTS / 2], cycle_samples[NTESTS / 4],
         cycle_samples[(3 * NTESTS) / 4],
         cycle_samples[(3 * NTESTS) / 4] - cycle_samples[NTESTS / 4],
         instr_samples[NTESTS / 2]);
}

static void run_pmu(void)
{
  static const struct variant variants[] = {
      {"decap_verify_basemul", target_decap_verify_basemul},
      {"decap_tobytes_r2", target_decap_tobytes_r2},
      {"decap_verify_basemul_plus_tobytes_r2",
       target_decap_verify_basemul_plus_tobytes},
      {"decap_verify_contract_ref", target_decap_verify_contract_ref},
      {"full_decap_current", target_full_decap_current},
      {"full_decap_contract_ref", target_full_decap_contract_ref},
  };
  size_t variant_idx;

  if (open_events() != 0)
  {
    exit(EXIT_FAILURE);
  }

  printf("pmu_settings,ntests=%d,niterations=%d,nwarmup=%d,ninputs=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  for (variant_idx = 0; variant_idx < sizeof(variants) / sizeof(variants[0]);
       variant_idx++)
  {
    measure_variant(&variants[variant_idx]);
  }
  printf("pmu_sink=%" PRIu64 "\n", g_sink);

  close_events();
}

int main(void)
{
  int direct_mismatches;
  int decap_mismatches;

  g_inputs = xaligned_alloc(64, NINPUTS * sizeof(*g_inputs));
  g_cminus_m2 = xaligned_alloc(64, NINPUTS * sizeof(*g_cminus_m2));
  g_hinv = xaligned_alloc(64, NINPUTS * sizeof(*g_hinv));
  g_r2 = xaligned_alloc(64, NINPUTS * sizeof(*g_r2));
  g_synth_a = xaligned_alloc(64, NINPUTS * sizeof(*g_synth_a));
  g_synth_b = xaligned_alloc(64, NINPUTS * sizeof(*g_synth_b));
  g_tmp_poly = xaligned_alloc(64, NINPUTS * sizeof(*g_tmp_poly));
  g_bytes0 = xaligned_alloc(64, NINPUTS * sizeof(*g_bytes0));
  g_bytes1 = xaligned_alloc(64, NINPUTS * sizeof(*g_bytes1));
  g_ss_workspace = xaligned_alloc(64, NINPUTS * sizeof(*g_ss_workspace));

  prepare_inputs();
  direct_mismatches = direct_byte_oracle_test();
  decap_mismatches = full_decap_differential_test();

  if (direct_mismatches != 0 || decap_mismatches != 0)
  {
    fprintf(stderr,
            "decap verify byte-contract correctness failed; not running PMU\n");
    return 1;
  }

  run_pmu();
  return 0;
}
