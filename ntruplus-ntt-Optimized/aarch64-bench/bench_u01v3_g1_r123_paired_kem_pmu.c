/* Same-binary paired full-KEM PMU for production vs G1R123+S2. */
#if !defined(__linux__)
#error "bench_u01v3_g1_r123_paired_kem_pmu requires Linux perf_event_open"
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
#ifndef BENCH_VARIANTS_LABEL
#define BENCH_VARIANTS_LABEL "A_production/B_g1r123_s2"
#endif
#ifndef BENCH_EVENT_LIMIT
#define BENCH_EVENT_LIMIT EVENT_COUNT
#endif

#define VARIANT_COUNT 2
#define SCOPE_COUNT 6
#define EVENT_COUNT 7
#define SITE_COUNT 4

enum variant_id {
  VARIANT_A = 0,
  VARIANT_B = 1
};

enum scope_id {
  SCOPE_ENCAP_TOTAL = 0,
  SCOPE_DECAP_TOTAL,
  SCOPE_ENCAP_NTT_R,
  SCOPE_ENCAP_NTT_M,
  SCOPE_DECAP_NTT_M1,
  SCOPE_DECAP_NTT_R1
};

enum event_id {
  EVENT_CYCLES = 0,
  EVENT_INSTRUCTIONS,
  EVENT_BRANCH_MISSES,
  EVENT_L1I_REFILL,
  EVENT_L1I_MISS,
  EVENT_STALL_FRONTEND,
  EVENT_STALL_BACKEND
};

enum event_source {
  EVENT_SOURCE_FIXED = 0,
  EVENT_SOURCE_CPU_PMU
};

typedef int (*enc_fn)(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
typedef int (*dec_fn)(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
typedef void (*ntt_fn)(poly *r, const poly *a);

struct input_case {
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ss[CRYPTO_BYTES];
  uint64_t enc_seed;
};

struct event_spec {
  const char *name;
  enum event_source source;
  uint32_t type;
  uint64_t config;
};

int bench_crypto_kem_keypair_u01v3_prod(uint8_t *pk, uint8_t *sk);
int bench_crypto_kem_enc_u01v3_prod(uint8_t *ct, uint8_t *ss,
                                    const uint8_t *pk);
int bench_crypto_kem_dec_u01v3_prod(uint8_t *ss, const uint8_t *ct,
                                    const uint8_t *sk);
int bench_crypto_kem_enc_u01v3_candidate(uint8_t *ct, uint8_t *ss,
                                         const uint8_t *pk);
int bench_crypto_kem_dec_u01v3_candidate(uint8_t *ss, const uint8_t *ct,
                                         const uint8_t *sk);
int bench_crypto_kem_enc_u01v3_capture(uint8_t *ct, uint8_t *ss,
                                       const uint8_t *pk);
int bench_crypto_kem_dec_u01v3_capture(uint8_t *ss, const uint8_t *ct,
                                       const uint8_t *sk);
void poly_ntt_u01v3_g1_r123_s2(poly *r, const poly *a);
void bench_u01v3_capture_poly_ntt(poly *r, const poly *a);

static const char *const g_scope_names[SCOPE_COUNT] = {
    "encap_total", "decap_total", "encap_ntt_r", "encap_ntt_m",
    "decap_ntt_m1", "decap_ntt_r1"};

static const struct event_spec g_event_specs[EVENT_COUNT] = {
    {"cycles", EVENT_SOURCE_FIXED, PERF_TYPE_HARDWARE,
     PERF_COUNT_HW_CPU_CYCLES},
    {"instructions", EVENT_SOURCE_FIXED, PERF_TYPE_HARDWARE,
     PERF_COUNT_HW_INSTRUCTIONS},
    {"branch_misses", EVENT_SOURCE_FIXED, PERF_TYPE_HARDWARE,
     PERF_COUNT_HW_BRANCH_MISSES},
    {"l1i_refill", EVENT_SOURCE_CPU_PMU, 0, 0x0001},
    {"l1i_miss", EVENT_SOURCE_FIXED, PERF_TYPE_HW_CACHE,
     PERF_COUNT_HW_CACHE_L1I | (PERF_COUNT_HW_CACHE_OP_READ << 8) |
         (PERF_COUNT_HW_CACHE_RESULT_MISS << 16)},
    {"stall_frontend", EVENT_SOURCE_CPU_PMU, 0, 0x0023},
    {"stall_backend", EVENT_SOURCE_CPU_PMU, 0, 0x0024},
};

static const enc_fn g_enc_fns[VARIANT_COUNT] = {
    bench_crypto_kem_enc_u01v3_prod,
    bench_crypto_kem_enc_u01v3_candidate,
};

static const dec_fn g_dec_fns[VARIANT_COUNT] = {
    bench_crypto_kem_dec_u01v3_prod,
    bench_crypto_kem_dec_u01v3_candidate,
};

static const ntt_fn g_ntt_fns[VARIANT_COUNT] = {
    poly_ntt,
    poly_ntt_u01v3_g1_r123_s2,
};

static struct input_case g_inputs[NINPUTS] __attribute__((aligned(64)));
static poly g_site_inputs[SITE_COUNT][NINPUTS] __attribute__((aligned(64)));
static poly g_site_work[NINPUTS] __attribute__((aligned(64)));
static poly g_site_snapshot[NINPUTS] __attribute__((aligned(64)));
static uint8_t g_ct_work[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ss_work[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ct_snapshot[CRYPTO_CIPHERTEXTBYTES]
    __attribute__((aligned(64)));
static uint8_t g_ss_snapshot[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint64_t g_median_raw[SCOPE_COUNT][VARIANT_COUNT][EVENT_COUNT];
static uint64_t g_replay_state;
static size_t g_capture_slot;
static size_t g_capture_call;
static int g_capture_enabled;
static int g_capture_error;
static int g_pair_mismatches;
static size_t g_pair_checks;
static volatile uint64_t g_sink;

static long perf_event_open_wrap(struct perf_event_attr *attr, pid_t pid,
                                 int cpu, int group_fd,
                                 unsigned long flags)
{
  return syscall(__NR_perf_event_open, attr, pid, cpu, group_fd, flags);
}

static uint64_t mix_seed(uint64_t x)
{
  x ^= x >> 30;
  x *= UINT64_C(0xbf58476d1ce4e5b9);
  x ^= x >> 27;
  x *= UINT64_C(0x94d049bb133111eb);
  return x ^ (x >> 31);
}

static void set_replay_seed(uint64_t seed)
{
  g_replay_state = seed;
}

void randombytes(uint8_t *out, size_t outlen)
{
  size_t i;

  for (i = 0; i < outlen; i++) {
    g_replay_state = g_replay_state * UINT64_C(6364136223846793005) +
                     UINT64_C(1442695040888963407);
    out[i] = (uint8_t)(g_replay_state >> 56);
  }
}

void bench_u01v3_capture_poly_ntt(poly *r, const poly *a)
{
  if (!g_capture_enabled || g_capture_slot >= NINPUTS ||
      g_capture_call >= SITE_COUNT) {
    g_capture_error = 1;
  } else {
    g_site_inputs[g_capture_call][g_capture_slot] = *a;
    g_capture_call++;
  }
  poly_ntt(r, a);
}

static int compare_bytes(const uint8_t *a, const uint8_t *b, size_t len)
{
  size_t i;
  int mismatches = 0;

  for (i = 0; i < len; i++)
    mismatches += a[i] != b[i];
  return mismatches;
}

static int prepare_inputs(void)
{
  size_t slot;
  int mismatches = 0;

  for (slot = 0; slot < NINPUTS; slot++) {
    struct input_case *input = &g_inputs[slot];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss[CRYPTO_BYTES];
    uint8_t ss_dec[CRYPTO_BYTES];
    uint64_t key_seed = mix_seed(UINT64_C(0x100000000) + slot);

    input->enc_seed = mix_seed(UINT64_C(0x200000000) + slot);
    set_replay_seed(key_seed);
    if (bench_crypto_kem_keypair_u01v3_prod(input->pk, input->sk) != 0)
      return -1;

    set_replay_seed(input->enc_seed);
    if (bench_crypto_kem_enc_u01v3_prod(input->ct, input->ss,
                                        input->pk) != 0)
      return -1;
    if (bench_crypto_kem_dec_u01v3_prod(ss_dec, input->ct, input->sk) != 0)
      return -1;
    mismatches += compare_bytes(ss_dec, input->ss, sizeof(ss_dec));

    g_capture_slot = slot;
    g_capture_call = 0;
    g_capture_enabled = 1;
    set_replay_seed(input->enc_seed);
    if (bench_crypto_kem_enc_u01v3_capture(ct, ss, input->pk) != 0)
      return -1;
    if (bench_crypto_kem_dec_u01v3_capture(ss_dec, input->ct,
                                           input->sk) != 0)
      return -1;
    g_capture_enabled = 0;
    if (g_capture_call != SITE_COUNT)
      g_capture_error = 1;
    mismatches += compare_bytes(ct, input->ct, sizeof(ct));
    mismatches += compare_bytes(ss, input->ss, sizeof(ss));
    mismatches += compare_bytes(ss_dec, input->ss, sizeof(ss_dec));

    set_replay_seed(input->enc_seed);
    if (bench_crypto_kem_enc_u01v3_candidate(ct, ss, input->pk) != 0)
      return -1;
    if (bench_crypto_kem_dec_u01v3_candidate(ss_dec, input->ct,
                                             input->sk) != 0)
      return -1;
    mismatches += compare_bytes(ct, input->ct, sizeof(ct));
    mismatches += compare_bytes(ss, input->ss, sizeof(ss));
    mismatches += compare_bytes(ss_dec, input->ss, sizeof(ss_dec));
  }

  printf("correctness,phase=prepare,inputs=%d,mismatches=%d,capture_error=%d\n",
         NINPUTS, mismatches, g_capture_error);
  return mismatches == 0 && !g_capture_error ? 0 : -1;
}

static void reset_scope(enum scope_id scope)
{
  if (scope >= SCOPE_ENCAP_NTT_R) {
    size_t site = (size_t)scope - (size_t)SCOPE_ENCAP_NTT_R;
    memcpy(g_site_work, g_site_inputs[site], sizeof(g_site_work));
  } else {
    memset(g_ct_work, 0, sizeof(g_ct_work));
    memset(g_ss_work, 0, sizeof(g_ss_work));
  }
}

static void call_scope_once(enum scope_id scope, enum variant_id variant,
                            size_t iteration, size_t sample)
{
  size_t slot = (iteration + sample) % NINPUTS;

  switch (scope) {
  case SCOPE_ENCAP_TOTAL:
    set_replay_seed(g_inputs[slot].enc_seed);
    (void)g_enc_fns[variant](g_ct_work, g_ss_work, g_inputs[slot].pk);
    g_sink ^= g_ct_work[(iteration + (size_t)variant) % sizeof(g_ct_work)];
    break;
  case SCOPE_DECAP_TOTAL:
    (void)g_dec_fns[variant](g_ss_work, g_inputs[slot].ct,
                             g_inputs[slot].sk);
    g_sink ^= g_ss_work[(iteration + (size_t)variant) % sizeof(g_ss_work)];
    break;
  default:
    g_ntt_fns[variant](&g_site_work[slot], &g_site_work[slot]);
    g_sink ^= (uint16_t)g_site_work[slot].coeffs[
        (iteration + (size_t)variant) % NTRUPLUS_N];
    break;
  }
}

static void warmup_scope(enum scope_id scope, enum variant_id variant,
                         size_t sample)
{
  size_t i;

  reset_scope(scope);
  for (i = 0; i < NWARMUP; i++)
    call_scope_once(scope, variant, i, sample);
}

static uint64_t measure_scope(int fd, enum scope_id scope,
                              enum variant_id variant, size_t sample)
{
  uint64_t value = 0;
  size_t i;

  reset_scope(scope);
  if (ioctl(fd, PERF_EVENT_IOC_RESET, 0) != 0 ||
      ioctl(fd, PERF_EVENT_IOC_ENABLE, 0) != 0) {
    perror("perf ioctl enable");
    exit(EXIT_FAILURE);
  }
  for (i = 0; i < NITERATIONS; i++)
    call_scope_once(scope, variant, i, sample);
  if (ioctl(fd, PERF_EVENT_IOC_DISABLE, 0) != 0) {
    perror("perf ioctl disable");
    exit(EXIT_FAILURE);
  }
  if (read(fd, &value, sizeof(value)) != (ssize_t)sizeof(value)) {
    perror("perf read");
    exit(EXIT_FAILURE);
  }
  return value;
}

static void save_scope_snapshot(enum scope_id scope)
{
  if (scope == SCOPE_ENCAP_TOTAL) {
    memcpy(g_ct_snapshot, g_ct_work, sizeof(g_ct_snapshot));
    memcpy(g_ss_snapshot, g_ss_work, sizeof(g_ss_snapshot));
  } else if (scope == SCOPE_DECAP_TOTAL) {
    memcpy(g_ss_snapshot, g_ss_work, sizeof(g_ss_snapshot));
  } else {
    memcpy(g_site_snapshot, g_site_work, sizeof(g_site_snapshot));
  }
}

static int compare_scope_snapshot(enum scope_id scope)
{
  if (scope == SCOPE_ENCAP_TOTAL)
    return compare_bytes(g_ct_snapshot, g_ct_work, sizeof(g_ct_snapshot)) +
           compare_bytes(g_ss_snapshot, g_ss_work, sizeof(g_ss_snapshot));
  if (scope == SCOPE_DECAP_TOTAL)
    return compare_bytes(g_ss_snapshot, g_ss_work, sizeof(g_ss_snapshot));
  return memcmp(g_site_snapshot, g_site_work, sizeof(g_site_snapshot)) != 0;
}

static int read_cpu_pmu_type(void)
{
  static const char path[] =
      "/sys/bus/event_source/devices/armv8_cortex_a76/type";
  FILE *file = fopen(path, "r");
  int type = -1;

  if (file == NULL)
    return -1;
  if (fscanf(file, "%d", &type) != 1)
    type = -1;
  fclose(file);
  return type;
}

static int open_event(const struct event_spec *spec, int cpu_pmu_type)
{
  struct perf_event_attr attr;

  if (spec->source == EVENT_SOURCE_CPU_PMU && cpu_pmu_type < 0)
    return -1;
  memset(&attr, 0, sizeof(attr));
  attr.type = spec->source == EVENT_SOURCE_CPU_PMU
                  ? (uint32_t)cpu_pmu_type
                  : spec->type;
  attr.size = sizeof(attr);
  attr.config = spec->config;
  attr.disabled = 1;
  attr.exclude_kernel = 1;
  attr.exclude_hv = 1;
  return (int)perf_event_open_wrap(&attr, 0, -1, -1, 0);
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

static size_t percentile_index(unsigned percentile)
{
  return ((size_t)percentile * (NTESTS - 1)) / 100u;
}

static void summarize(enum scope_id scope, enum event_id event,
                      uint64_t samples[VARIANT_COUNT][NTESTS])
{
  uint64_t sorted_a[NTESTS];
  uint64_t sorted_b[NTESTS];
  int64_t deltas[NTESTS];
  int64_t sorted_deltas[NTESTS];
  uint64_t deviations[NTESTS];
  int64_t delta_median;
  size_t win_rate_milli_percent;
  size_t tie_rate_milli_percent;
  size_t i;
  size_t wins = 0;
  size_t ties = 0;

  for (i = 0; i < NTESTS; i++) {
    sorted_a[i] = samples[VARIANT_A][i];
    sorted_b[i] = samples[VARIANT_B][i];
    deltas[i] = (int64_t)samples[VARIANT_B][i] -
                (int64_t)samples[VARIANT_A][i];
    sorted_deltas[i] = deltas[i];
  }
  qsort(sorted_a, NTESTS, sizeof(sorted_a[0]), cmp_u64);
  qsort(sorted_b, NTESTS, sizeof(sorted_b[0]), cmp_u64);
  qsort(sorted_deltas, NTESTS, sizeof(sorted_deltas[0]), cmp_i64);
  for (i = 0; i < NTESTS; i++) {
    if (sorted_deltas[i] < 0)
      wins++;
    else if (sorted_deltas[i] == 0)
      ties++;
  }
  delta_median = sorted_deltas[NTESTS / 2];
  for (i = 0; i < NTESTS; i++) {
    int64_t distance = deltas[i] - delta_median;
    deviations[i] = (uint64_t)(distance < 0 ? -distance : distance);
  }
  qsort(deviations, NTESTS, sizeof(deviations[0]), cmp_u64);
  win_rate_milli_percent = (wins * 100000u) / NTESTS;
  tie_rate_milli_percent = (ties * 100000u) / NTESTS;

  g_median_raw[scope][VARIANT_A][event] = sorted_a[NTESTS / 2];
  g_median_raw[scope][VARIANT_B][event] = sorted_b[NTESTS / 2];
  printf("paired_raw,scope=%s,event=%s,a_p10=%" PRIu64
         ",a_p50=%" PRIu64 ",a_p90=%" PRIu64 ",b_p10=%" PRIu64
         ",b_p50=%" PRIu64 ",b_p90=%" PRIu64 ",delta_p10=%" PRId64
         ",delta_p50=%" PRId64 ",delta_p90=%" PRId64 ",mad=%" PRIu64 ","
         "candidate_win_rate_milli_percent=%zu,tie_rate_milli_percent=%zu,"
         "wins=%zu,ties=%zu,"
         "samples=%d,iterations=%d\n",
         g_scope_names[scope], g_event_specs[event].name,
         sorted_a[percentile_index(10)], sorted_a[NTESTS / 2],
         sorted_a[percentile_index(90)], sorted_b[percentile_index(10)],
         sorted_b[NTESTS / 2], sorted_b[percentile_index(90)],
         sorted_deltas[percentile_index(10)], delta_median,
         sorted_deltas[percentile_index(90)], deviations[NTESTS / 2],
         win_rate_milli_percent, tie_rate_milli_percent, wins, ties, NTESTS,
         NITERATIONS);
}

static uintptr_t address_from_enc_fn(enc_fn fn)
{
  uintptr_t address = 0;
  memcpy(&address, &fn, sizeof(fn) < sizeof(address) ? sizeof(fn)
                                                    : sizeof(address));
  return address;
}

static uintptr_t address_from_dec_fn(dec_fn fn)
{
  uintptr_t address = 0;
  memcpy(&address, &fn, sizeof(fn) < sizeof(address) ? sizeof(fn)
                                                    : sizeof(address));
  return address;
}

static uintptr_t address_from_ntt_fn(ntt_fn fn)
{
  uintptr_t address = 0;
  memcpy(&address, &fn, sizeof(fn) < sizeof(address) ? sizeof(fn)
                                                    : sizeof(address));
  return address;
}

static void print_address(const char *symbol, uintptr_t address)
{
  printf("layout_runtime,symbol=%s,address=0x%" PRIxPTR
         ",addr_mod32=%" PRIuPTR ",addr_mod64=%" PRIuPTR "\n",
         symbol, address, address & 31u, address & 63u);
}

static void print_layout(void)
{
  print_address("bench_crypto_kem_enc_u01v3_prod",
                address_from_enc_fn(bench_crypto_kem_enc_u01v3_prod));
  print_address("bench_crypto_kem_enc_u01v3_candidate",
                address_from_enc_fn(bench_crypto_kem_enc_u01v3_candidate));
  print_address("bench_crypto_kem_dec_u01v3_prod",
                address_from_dec_fn(bench_crypto_kem_dec_u01v3_prod));
  print_address("bench_crypto_kem_dec_u01v3_candidate",
                address_from_dec_fn(bench_crypto_kem_dec_u01v3_candidate));
  print_address("poly_ntt", address_from_ntt_fn(poly_ntt));
  print_address("poly_ntt_u01v3_g1_r123_s2",
                address_from_ntt_fn(poly_ntt_u01v3_g1_r123_s2));
  printf("layout_runtime,buffer=ct,address=%p,addr_mod64=%" PRIuPTR "\n",
         (void *)g_ct_work, (uintptr_t)g_ct_work & 63u);
  printf("layout_runtime,buffer=ss,address=%p,addr_mod64=%" PRIuPTR "\n",
         (void *)g_ss_work, (uintptr_t)g_ss_work & 63u);
  printf("layout_runtime,buffer=ntt_workspace,address=%p,addr_mod64=%" PRIuPTR
         "\n",
         (void *)g_site_work, (uintptr_t)g_site_work & 63u);
}

static void run_event(enum event_id event, int cpu_pmu_type)
{
  int fd = open_event(&g_event_specs[event], cpu_pmu_type);
  enum scope_id scope;

  if (fd < 0) {
    printf("event_support,event=%s,available=0,errno=%d\n",
           g_event_specs[event].name, errno);
    return;
  }
  printf("event_support,event=%s,available=1,type=%u,config=0x%" PRIx64
         "\n",
         g_event_specs[event].name,
         g_event_specs[event].source == EVENT_SOURCE_CPU_PMU
             ? (unsigned)cpu_pmu_type
             : g_event_specs[event].type,
         g_event_specs[event].config);

  for (scope = 0; scope < SCOPE_COUNT; scope++) {
    uint64_t samples[VARIANT_COUNT][NTESTS];
    size_t sample;

    warmup_scope(scope, VARIANT_A, 0);
    warmup_scope(scope, VARIANT_B, 0);
    for (sample = 0; sample < NTESTS; sample++) {
      enum variant_id first = (sample & 1u) ? VARIANT_B : VARIANT_A;
      enum variant_id second = first == VARIANT_A ? VARIANT_B : VARIANT_A;

      samples[first][sample] = measure_scope(fd, scope, first, sample);
      save_scope_snapshot(scope);
      samples[second][sample] = measure_scope(fd, scope, second, sample);
      g_pair_mismatches += compare_scope_snapshot(scope);
      g_pair_checks++;
    }
    summarize(scope, event, samples);
  }
  close(fd);
}

static void print_cpi_summary(void)
{
  enum scope_id scope;

  for (scope = 0; scope < SCOPE_COUNT; scope++) {
    double a_cycles = (double)g_median_raw[scope][VARIANT_A][EVENT_CYCLES] /
                      NITERATIONS;
    double b_cycles = (double)g_median_raw[scope][VARIANT_B][EVENT_CYCLES] /
                      NITERATIONS;
    double a_instructions =
        (double)g_median_raw[scope][VARIANT_A][EVENT_INSTRUCTIONS] /
        NITERATIONS;
    double b_instructions =
        (double)g_median_raw[scope][VARIANT_B][EVENT_INSTRUCTIONS] /
        NITERATIONS;
    printf("cpi_summary,scope=%s,a_cycles=%.3f,b_cycles=%.3f,"
           "a_instructions=%.3f,b_instructions=%.3f,a_cpi=%.6f,"
           "b_cpi=%.6f\n",
           g_scope_names[scope], a_cycles, b_cycles, a_instructions,
           b_instructions, a_instructions ? a_cycles / a_instructions : 0.0,
           b_instructions ? b_cycles / b_instructions : 0.0);
  }
}

int main(void)
{
  int cpu_pmu_type;
  enum event_id event;

  printf("benchmark,same_binary=1,variants=%s,"
         "order=AB_BA,dispatch_inside_poly_ntt=0,same_buffers=1,"
         "NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NINPUTS=%d\n",
         BENCH_VARIANTS_LABEL, NTESTS, NITERATIONS, NWARMUP, NINPUTS);
  if (prepare_inputs() != 0)
    return EXIT_FAILURE;
  print_layout();
  cpu_pmu_type = read_cpu_pmu_type();
  printf("pmu,cpu_pmu_type=%d,cpu_pmu_name=armv8_cortex_a76\n",
         cpu_pmu_type);
  for (event = 0; event < BENCH_EVENT_LIMIT; event++)
    run_event(event, cpu_pmu_type);
  print_cpi_summary();
  printf("correctness,phase=paired,checks=%zu,mismatches=%d\n",
         g_pair_checks, g_pair_mismatches);
  printf("sink=%" PRIu64 "\n", g_sink);
  return g_pair_mismatches == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
