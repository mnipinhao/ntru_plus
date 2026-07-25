#if !defined(__linux__)
#error "This benchmark requires Linux perf_event_open"
#endif
#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

#include "api.h"
#include "gt/keygen_bpq_cq.h"
#include "gt/keygen_cq.h"
#include "NO_CE/fips202.h"
#include "poly.h"
#include "symmetric.h"

#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 2000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif
#ifndef NINPUTS
#define NINPUTS 32
#endif

#define VARIANT_COUNT 2
#define EVENT_COUNT 2

typedef int (*keygen_fn)(uint8_t *, uint8_t *, size_t);

struct counts {
  uint64_t cycles;
  uint64_t instructions;
};

static uint8_t pk_work[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk_work[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static int leader_fd = -1;
static int event_fds[EVENT_COUNT] = {-1, -1};
static volatile uint64_t sink;

static void seed_for(uint8_t seed[NTRUPLUS_SYMBYTES], size_t input,
                     unsigned which, unsigned attempt)
{
  uint64_t state = UINT64_C(0x9e3779b97f4a7c15) ^
                   (UINT64_C(0x100000001b3) * (input + 1)) ^
                   ((uint64_t)which << 48) ^ attempt;
  size_t i;

  for (i = 0; i < NTRUPLUS_SYMBYTES; i++) {
    state = state * UINT64_C(6364136223846793005) +
            UINT64_C(1442695040888963407);
    seed[i] = (uint8_t)(state >> 56);
  }
}

static void sample_small(poly *out, size_t input, unsigned which,
                         unsigned attempt)
{
  uint8_t seed[NTRUPLUS_SYMBYTES];
  uint8_t buf[NTRUPLUS_N / 4];

  seed_for(seed, input, which, attempt);
  shake256(buf, sizeof buf, seed, sizeof seed);
  poly_cbd1(out, buf);
}

static int generate_mixed_inverse(gt_bpq_poly *value, gt_cq_poly *inverse,
                                  size_t input, unsigned which, int add_one)
{
  unsigned attempt;

  for (attempt = 0; ; attempt++) {
    poly block_major;

    sample_small(&value->storage, input, which, attempt);
    poly_triple(&value->storage, &value->storage);
    if (add_one)
      value->storage.coeffs[0] += 1;
    poly_ntt(&block_major, &value->storage);
    gt_keygen_blockmajor_to_bpq(value, &block_major);
    if (!gt_keygen_baseinv_bpq_to_cq_scaled_r(inverse, value))
      return 0;
  }
}

static int generate_cq_inverse(gt_cq_poly *value, gt_cq_poly *inverse,
                               size_t input, unsigned which, int add_one)
{
  unsigned attempt;

  for (attempt = 0; ; attempt++) {
    sample_small(&value->storage, input, which, attempt);
    poly_triple(&value->storage, &value->storage);
    if (add_one)
      value->storage.coeffs[0] += 1;
    gt_keygen_poly_ntt_to_cq(value, &value->storage);
    if (!gt_keygen_baseinv_cq_to_cq_scaled_r(inverse, value))
      return 0;
  }
}

static int keygen_mixed(uint8_t *pk, uint8_t *sk, size_t input)
{
  gt_bpq_poly f;
  gt_bpq_poly g;
  gt_cq_poly finv;
  gt_cq_poly ginv;
  gt_cq_poly h;
  gt_cq_poly hinv;

  generate_mixed_inverse(&f, &finv, input, 0, 1);
  generate_mixed_inverse(&g, &ginv, input, 1, 0);
  gt_keygen_basemul_bpq_cq_to_cq_scaled_r(&h, &g, &finv);
  gt_keygen_basemul_bpq_cq_to_cq_scaled_r(&hinv, &f, &ginv);
  gt_keygen_tobytes_cq(pk, &h);
  gt_keygen_tobytes_bpq_p1(sk, &f);
  gt_keygen_tobytes_cq(sk + NTRUPLUS_POLYBYTES, &hinv);
  hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
  return 0;
}

static int keygen_cq(uint8_t *pk, uint8_t *sk, size_t input)
{
  gt_cq_poly f;
  gt_cq_poly g;
  gt_cq_poly finv;
  gt_cq_poly ginv;
  gt_cq_poly h;
  gt_cq_poly hinv;

  generate_cq_inverse(&f, &finv, input, 0, 1);
  generate_cq_inverse(&g, &ginv, input, 1, 0);
  gt_keygen_basemul_cq_cq_to_cq_scaled_r(&h, &g, &finv);
  gt_keygen_basemul_cq_cq_to_cq_scaled_r(&hinv, &f, &ginv);
  gt_keygen_tobytes_cq(pk, &h);
  gt_keygen_tobytes_cq(sk, &f);
  gt_keygen_tobytes_cq(sk + NTRUPLUS_POLYBYTES, &hinv);
  hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
  return 0;
}

static const keygen_fn variants[VARIANT_COUNT] = {
    keygen_mixed,
    keygen_cq,
};
static const char *const variant_names[VARIANT_COUNT] = {
    "mixed",
    "cq",
};

static int perf_event_open_wrap(struct perf_event_attr *attr, int group_fd)
{
  return (int)syscall(__NR_perf_event_open, attr, 0, -1, group_fd, 0);
}

static void setup_events(void)
{
  static const uint64_t configs[EVENT_COUNT] = {
      PERF_COUNT_HW_CPU_CYCLES,
      PERF_COUNT_HW_INSTRUCTIONS,
  };
  size_t i;

  for (i = 0; i < EVENT_COUNT; i++) {
    struct perf_event_attr attr;

    memset(&attr, 0, sizeof attr);
    attr.type = PERF_TYPE_HARDWARE;
    attr.size = sizeof attr;
    attr.config = configs[i];
    attr.disabled = i == 0;
    attr.exclude_kernel = 1;
    attr.exclude_hv = 1;
    attr.read_format = PERF_FORMAT_GROUP;
    event_fds[i] = perf_event_open_wrap(&attr, leader_fd);
    if (event_fds[i] < 0) {
      fprintf(stderr, "perf_event_open(%zu): %s\n", i, strerror(errno));
      exit(1);
    }
    if (i == 0)
      leader_fd = event_fds[i];
  }
}

static void close_events(void)
{
  size_t i;

  for (i = 0; i < EVENT_COUNT; i++)
    if (event_fds[i] >= 0)
      close(event_fds[i]);
}

static struct counts measure(keygen_fn fn)
{
  uint64_t values[EVENT_COUNT + 1] = {0};
  size_t i;

  ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (i = 0; i < NITERATIONS; i++) {
    fn(pk_work, sk_work, i % NINPUTS);
    sink ^= pk_work[i % CRYPTO_PUBLICKEYBYTES];
    sink ^= sk_work[i % CRYPTO_SECRETKEYBYTES];
  }
  ioctl(leader_fd, PERF_EVENT_IOC_DISABLE, PERF_IOC_FLAG_GROUP);
  if (read(leader_fd, values, sizeof values) != (ssize_t)sizeof values) {
    perror("read perf group");
    exit(1);
  }
  return (struct counts){
      values[1] / NITERATIONS,
      values[2] / NITERATIONS,
  };
}

static int cmp_u64(const void *a, const void *b)
{
  const uint64_t av = *(const uint64_t *)a;
  const uint64_t bv = *(const uint64_t *)b;
  return (av > bv) - (av < bv);
}

static int cmp_i64(const void *a, const void *b)
{
  const int64_t av = *(const int64_t *)a;
  const int64_t bv = *(const int64_t *)b;
  return (av > bv) - (av < bv);
}

static int prepare_and_check(void)
{
  uint8_t mixed_pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t mixed_sk[CRYPTO_SECRETKEYBYTES];
  uint8_t cq_pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t cq_sk[CRYPTO_SECRETKEYBYTES];
  unsigned mismatches = 0;
  size_t input;

  for (input = 0; input < NINPUTS; input++) {
    keygen_mixed(mixed_pk, mixed_sk, input);
    keygen_cq(cq_pk, cq_sk, input);
    mismatches += memcmp(mixed_pk, cq_pk, sizeof mixed_pk) != 0;
    mismatches += memcmp(mixed_sk, cq_sk, sizeof mixed_sk) != 0;
  }
  printf("correctness,total_mismatches=%u,inputs=%d\n",
         mismatches, NINPUTS);
  return mismatches != 0;
}

static void print_variant(size_t variant,
                          uint64_t cycles[VARIANT_COUNT][NTESTS],
                          uint64_t instructions[VARIANT_COUNT][NTESTS])
{
  uint64_t c[NTESTS];
  uint64_t insn[NTESTS];

  memcpy(c, cycles[variant], sizeof c);
  memcpy(insn, instructions[variant], sizeof insn);
  qsort(c, NTESTS, sizeof c[0], cmp_u64);
  qsort(insn, NTESTS, sizeof insn[0], cmp_u64);
  printf("pmu,%s,cycles_p10=%" PRIu64 ",cycles_p50=%" PRIu64
         ",cycles_p90=%" PRIu64 ",cycles_min=%" PRIu64
         ",cycles_max=%" PRIu64 ",instr_p50=%" PRIu64
         ",cpi_x1000=%" PRIu64 ",addr_mod32=%" PRIuPTR
         ",addr_mod64=%" PRIuPTR "\n",
         variant_names[variant], c[NTESTS / 10], c[NTESTS / 2],
         c[(9 * NTESTS) / 10], c[0], c[NTESTS - 1],
         insn[NTESTS / 2],
         (1000 * c[NTESTS / 2]) / insn[NTESTS / 2],
         (uintptr_t)variants[variant] % 32,
         (uintptr_t)variants[variant] % 64);
}

int main(void)
{
  uint64_t cycles[VARIANT_COUNT][NTESTS];
  uint64_t instructions[VARIANT_COUNT][NTESTS];
  int64_t delta[NTESTS];
  unsigned cq_wins = 0;
  size_t test;

  if (prepare_and_check() != 0)
    return 1;
  for (test = 0; test < NWARMUP; test++) {
    variants[test & 1](pk_work, sk_work, test % NINPUTS);
    variants[(test & 1) ^ 1](pk_work, sk_work, test % NINPUTS);
  }

  setup_events();
  for (test = 0; test < NTESTS; test++) {
    size_t position;
    for (position = 0; position < VARIANT_COUNT; position++) {
      const size_t variant = (test + position) % VARIANT_COUNT;
      const struct counts count = measure(variants[variant]);
      cycles[variant][test] = count.cycles;
      instructions[variant][test] = count.instructions;
    }
  }
  close_events();

  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  print_variant(0, cycles, instructions);
  print_variant(1, cycles, instructions);
  for (test = 0; test < NTESTS; test++) {
    delta[test] =
        (int64_t)cycles[0][test] - (int64_t)cycles[1][test];
    cq_wins += delta[test] > 0;
  }
  qsort(delta, NTESTS, sizeof delta[0], cmp_i64);
  printf("paired,mixed_minus_cq,delta_p10=%" PRId64
         ",delta_p50=%" PRId64 ",delta_p90=%" PRId64
         ",cq_wins=%u/%d\n",
         delta[NTESTS / 10], delta[NTESTS / 2],
         delta[(9 * NTESTS) / 10], cq_wins, NTESTS);
  printf("sink=%" PRIu64 "\n", sink);
  return 0;
}
