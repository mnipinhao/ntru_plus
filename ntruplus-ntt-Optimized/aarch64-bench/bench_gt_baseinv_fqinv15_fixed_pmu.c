/* Same-binary paired PMU for hierarchical baseinv with fixed Slothy fqinv. */
#if !defined(__linux__)
#error "bench_gt_baseinv_fqinv15_fixed_pmu requires Linux perf_event_open"
#endif
#if !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <asm/unistd.h>
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
#include "params.h"
#include "poly.h"
#include "randombytes.h"

#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 1000
#endif
#ifndef NKEYPAIR_ITERATIONS
#define NKEYPAIR_ITERATIONS 100
#endif
#ifndef NWARMUP
#define NWARMUP 50
#endif
#ifndef NINPUTS
#define NINPUTS 32
#endif

enum variant_id { VARIANT_A, VARIANT_B, VARIANT_COUNT };
enum scope_id { SCOPE_BASEINV, SCOPE_KEYPAIR, SCOPE_COUNT };
enum event_id { EVENT_CYCLES, EVENT_INSTRUCTIONS, EVENT_COUNT };

typedef int (*baseinv_fn)(poly *, const poly *);
typedef int (*keypair_fn)(uint8_t *, uint8_t *);

struct event_spec {
  const char *name;
  uint64_t config;
};

int poly_baseinv_scaled_r(poly *r, const poly *a);
int poly_baseinv_scaled_r_fqinv15_fixed_candidate(poly *r, const poly *a);
int bench_crypto_kem_keypair_u01v3_prod(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_keypair_u01v3_candidate(uint8_t *pk, uint8_t *sk);

static const baseinv_fn g_baseinv[VARIANT_COUNT] = {
    poly_baseinv_scaled_r,
    poly_baseinv_scaled_r_fqinv15_fixed_candidate,
};
static const keypair_fn g_keypair[VARIANT_COUNT] = {
    bench_crypto_kem_keypair_u01v3_prod,
    bench_crypto_kem_keypair_u01v3_candidate,
};
static const struct event_spec g_events[EVENT_COUNT] = {
    {"cycles", PERF_COUNT_HW_CPU_CYCLES},
    {"instructions", PERF_COUNT_HW_INSTRUCTIONS},
};
static const char *const g_scope_names[SCOPE_COUNT] = {
    "poly_baseinv_scaled_r",
    "keypair_total",
};

static poly g_inputs[NINPUTS] __attribute__((aligned(64)));
static poly g_poly_work __attribute__((aligned(64)));
static poly g_poly_snapshot __attribute__((aligned(64)));
static uint8_t g_pk_work[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk_work[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_pk_snapshot[CRYPTO_PUBLICKEYBYTES]
    __attribute__((aligned(64)));
static uint8_t g_sk_snapshot[CRYPTO_SECRETKEYBYTES]
    __attribute__((aligned(64)));
static uint64_t g_rng_state;
static volatile uint64_t g_sink;
static int g_mismatches;

static uint64_t mix_seed(uint64_t x)
{
  x ^= x >> 30;
  x *= UINT64_C(0xbf58476d1ce4e5b9);
  x ^= x >> 27;
  x *= UINT64_C(0x94d049bb133111eb);
  return x ^ (x >> 31);
}

static void set_seed(uint64_t seed)
{
  g_rng_state = seed ? seed : 1;
}

void randombytes(uint8_t *out, size_t outlen)
{
  size_t i;

  for (i = 0; i < outlen; i++) {
    g_rng_state = g_rng_state * UINT64_C(6364136223846793005) +
                  UINT64_C(1442695040888963407);
    out[i] = (uint8_t)(g_rng_state >> 56);
  }
}

static int perf_event_open_wrap(struct perf_event_attr *attr)
{
  return (int)syscall(__NR_perf_event_open, attr, 0, -1, -1, 0);
}

static int open_event(uint64_t config)
{
  struct perf_event_attr attr;

  memset(&attr, 0, sizeof(attr));
  attr.type = PERF_TYPE_HARDWARE;
  attr.size = sizeof(attr);
  attr.config = config;
  attr.disabled = 1;
  attr.exclude_kernel = 1;
  attr.exclude_hv = 1;
  return perf_event_open_wrap(&attr);
}

static int cmp_u64(const void *a, const void *b)
{
  const uint64_t aa = *(const uint64_t *)a;
  const uint64_t bb = *(const uint64_t *)b;
  return (aa > bb) - (aa < bb);
}

static int cmp_i64(const void *a, const void *b)
{
  const int64_t aa = *(const int64_t *)a;
  const int64_t bb = *(const int64_t *)b;
  return (aa > bb) - (aa < bb);
}

static void prepare_inputs(void)
{
  size_t slot;

  for (slot = 0; slot < NINPUTS; slot++) {
    uint64_t state = mix_seed(UINT64_C(0x62617365696e7600) + slot);
    int attempts;

    for (attempts = 0; attempts < 1000; attempts++) {
      size_t i;
      poly out_a;
      poly out_b;
      int ret_a;
      int ret_b;

      for (i = 0; i < NTRUPLUS_N; i++) {
        state = state * UINT64_C(6364136223846793005) +
                UINT64_C(1442695040888963407);
        g_inputs[slot].coeffs[i] =
            (int16_t)((state >> 48) % NTRUPLUS_Q);
      }
      ret_a = g_baseinv[VARIANT_A](&out_a, &g_inputs[slot]);
      ret_b = g_baseinv[VARIANT_B](&out_b, &g_inputs[slot]);
      if (ret_a == 0 && ret_b == 0) {
        g_mismatches += memcmp(&out_a, &out_b, sizeof(out_a)) != 0;
        break;
      }
      g_mismatches += ret_a != ret_b;
    }
    if (attempts == 1000) {
      fprintf(stderr, "failed to find invertible input at slot %zu\n", slot);
      exit(EXIT_FAILURE);
    }
  }
}

static size_t iterations_for_scope(enum scope_id scope)
{
  return scope == SCOPE_BASEINV ? NITERATIONS : NKEYPAIR_ITERATIONS;
}

static void call_once(enum scope_id scope, enum variant_id variant,
                      size_t iteration, size_t sample)
{
  const size_t slot = (iteration + sample) % NINPUTS;

  if (scope == SCOPE_BASEINV) {
    (void)g_baseinv[variant](&g_poly_work, &g_inputs[slot]);
    g_sink ^= (uint16_t)g_poly_work.coeffs[
        (iteration + (size_t)variant) % NTRUPLUS_N];
  } else {
    set_seed(mix_seed(UINT64_C(0x6b65797061697200) + slot));
    (void)g_keypair[variant](g_pk_work, g_sk_work);
    g_sink ^= g_pk_work[(iteration + (size_t)variant) % sizeof(g_pk_work)];
  }
}

static void warmup(enum scope_id scope, enum variant_id variant, size_t sample)
{
  size_t i;

  for (i = 0; i < NWARMUP; i++)
    call_once(scope, variant, i, sample);
}

static uint64_t measure(int fd, enum scope_id scope, enum variant_id variant,
                        size_t sample)
{
  const size_t iterations = iterations_for_scope(scope);
  uint64_t value;
  size_t i;

  if (ioctl(fd, PERF_EVENT_IOC_RESET, 0) != 0 ||
      ioctl(fd, PERF_EVENT_IOC_ENABLE, 0) != 0) {
    perror("perf enable");
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < iterations; i++)
    call_once(scope, variant, i, sample);
  if (ioctl(fd, PERF_EVENT_IOC_DISABLE, 0) != 0) {
    perror("perf disable");
    exit(EXIT_FAILURE);
  }
  if (read(fd, &value, sizeof(value)) != (ssize_t)sizeof(value)) {
    perror("perf read");
    exit(EXIT_FAILURE);
  }
  return value;
}

static void save_snapshot(enum scope_id scope)
{
  if (scope == SCOPE_BASEINV) {
    g_poly_snapshot = g_poly_work;
  } else {
    memcpy(g_pk_snapshot, g_pk_work, sizeof(g_pk_snapshot));
    memcpy(g_sk_snapshot, g_sk_work, sizeof(g_sk_snapshot));
  }
}

static void compare_snapshot(enum scope_id scope)
{
  if (scope == SCOPE_BASEINV) {
    g_mismatches += memcmp(&g_poly_snapshot, &g_poly_work,
                           sizeof(g_poly_work)) != 0;
  } else {
    g_mismatches += memcmp(g_pk_snapshot, g_pk_work, sizeof(g_pk_work)) != 0;
    g_mismatches += memcmp(g_sk_snapshot, g_sk_work, sizeof(g_sk_work)) != 0;
  }
}

static void summarize(enum scope_id scope, enum event_id event,
                      uint64_t samples[VARIANT_COUNT][NTESTS])
{
  uint64_t sorted_a[NTESTS];
  uint64_t sorted_b[NTESTS];
  int64_t deltas[NTESTS];
  size_t wins = 0;
  size_t i;
  const double iterations = (double)iterations_for_scope(scope);

  for (i = 0; i < NTESTS; i++) {
    sorted_a[i] = samples[VARIANT_A][i];
    sorted_b[i] = samples[VARIANT_B][i];
    deltas[i] = (int64_t)samples[VARIANT_B][i] -
                (int64_t)samples[VARIANT_A][i];
    wins += deltas[i] < 0;
  }
  qsort(sorted_a, NTESTS, sizeof(sorted_a[0]), cmp_u64);
  qsort(sorted_b, NTESTS, sizeof(sorted_b[0]), cmp_u64);
  qsort(deltas, NTESTS, sizeof(deltas[0]), cmp_i64);
  printf("paired,scope=%s,event=%s,a_median=%.3f,b_median=%.3f,"
         "delta_median=%.3f,delta_p10=%.3f,delta_p90=%.3f,"
         "candidate_wins=%zu,samples=%d,iterations=%zu\n",
         g_scope_names[scope], g_events[event].name,
         sorted_a[NTESTS / 2] / iterations,
         sorted_b[NTESTS / 2] / iterations,
         deltas[NTESTS / 2] / iterations,
         deltas[(NTESTS - 1) / 10] / iterations,
         deltas[((NTESTS - 1) * 9) / 10] / iterations,
         wins, NTESTS, iterations_for_scope(scope));
}

static void run_event(enum event_id event)
{
  int fd = open_event(g_events[event].config);
  enum scope_id scope;

  if (fd < 0) {
    perror("perf_event_open");
    exit(EXIT_FAILURE);
  }
  for (scope = 0; scope < SCOPE_COUNT; scope++) {
    uint64_t samples[VARIANT_COUNT][NTESTS];
    size_t sample;

    warmup(scope, VARIANT_A, 0);
    warmup(scope, VARIANT_B, 0);
    for (sample = 0; sample < NTESTS; sample++) {
      enum variant_id first = (sample & 1u) ? VARIANT_B : VARIANT_A;
      enum variant_id second = first == VARIANT_A ? VARIANT_B : VARIANT_A;

      samples[first][sample] = measure(fd, scope, first, sample);
      save_snapshot(scope);
      samples[second][sample] = measure(fd, scope, second, sample);
      compare_snapshot(scope);
    }
    summarize(scope, event, samples);
  }
  close(fd);
}

int main(void)
{
  enum event_id event;

  prepare_inputs();
  printf("benchmark,variants=A_production/B_hier_fqinv15_fixed,"
         "same_binary=1,order=AB_BA,NTESTS=%d,NINPUTS=%d\n",
         NTESTS, NINPUTS);
  for (event = 0; event < EVENT_COUNT; event++)
    run_event(event);
  printf("correctness,mismatches=%d\n", g_mismatches);
  printf("sink=%" PRIu64 "\n", g_sink);
  return g_mismatches == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
