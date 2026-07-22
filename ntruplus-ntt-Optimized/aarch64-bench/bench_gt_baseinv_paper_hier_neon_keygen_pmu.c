/* Same-binary KEM differential and keygen PMU for paper-exact hier_k8. */
#if !defined(__linux__)
#error "paper hier keygen PMU requires Linux perf_event_open"
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
#include "randombytes.h"

#ifndef NTESTS
#define NTESTS 31
#endif
#ifndef NITERATIONS
#define NITERATIONS 500
#endif
#ifndef NWARMUP
#define NWARMUP 20
#endif
#ifndef NKEMDIFF
#define NKEMDIFF 1000
#endif

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
int bench_crypto_kem_keypair_paper_hier_k8(uint8_t *pk, uint8_t *sk);

typedef void (*bench_target_fn)(size_t idx);

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
};

static uint8_t g_pk0[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_pk1[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk0[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk1[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_ct0[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ct1[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ss0[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss1[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss2[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss3[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint64_t g_rng_state = 1;
static volatile uint64_t g_sink;

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

static size_t first_byte_mismatch(const uint8_t *a, const uint8_t *b,
                                  size_t len)
{
  for (size_t i = 0; i < len; i++)
    if (a[i] != b[i])
      return i;
  return len;
}

static int run_kem_correctness(void)
{
  uint64_t keypair_ret_mismatches = 0;
  uint64_t pk_mismatches = 0;
  uint64_t sk_mismatches = 0;
  uint64_t enc_ret_mismatches = 0;
  uint64_t dec_ret_mismatches = 0;
  uint64_t ct_mismatches = 0;
  uint64_t enc_ss_mismatches = 0;
  uint64_t dec_ss_mismatches = 0;
  int first_reported = 0;

  for (size_t i = 0; i < NKEMDIFF; i++)
  {
    size_t off;
    int ret_key0;
    int ret_key1;
    int ret_enc0;
    int ret_enc1;
    int ret_dec0;
    int ret_dec1;

    randombytes_reset(seed_for_index(i, 0x6b65797061697231ULL));
    ret_key0 = bench_crypto_kem_keypair_current(g_pk0, g_sk0);
    randombytes_reset(seed_for_index(i, 0x6b65797061697231ULL));
    ret_key1 = bench_crypto_kem_keypair_paper_hier_k8(g_pk1, g_sk1);
    keypair_ret_mismatches += ret_key0 != ret_key1;

    off = first_byte_mismatch(g_pk0, g_pk1, sizeof(g_pk0));
    pk_mismatches += off != sizeof(g_pk0);
    if (!first_reported && off != sizeof(g_pk0))
    {
      printf("first_mismatch,kind=pk,seed=%zu,offset=%zu,current=%u,"
             "candidate=%u\n",
             i, off, g_pk0[off], g_pk1[off]);
      first_reported = 1;
    }
    off = first_byte_mismatch(g_sk0, g_sk1, sizeof(g_sk0));
    sk_mismatches += off != sizeof(g_sk0);
    if (!first_reported && off != sizeof(g_sk0))
    {
      printf("first_mismatch,kind=sk,seed=%zu,offset=%zu,current=%u,"
             "candidate=%u\n",
             i, off, g_sk0[off], g_sk1[off]);
      first_reported = 1;
    }

    randombytes_reset(seed_for_index(i, 0x656e636170737531ULL));
    ret_enc0 = bench_crypto_kem_enc_current(g_ct0, g_ss0, g_pk0);
    ret_dec0 = bench_crypto_kem_dec_current(g_ss1, g_ct0, g_sk0);
    randombytes_reset(seed_for_index(i, 0x656e636170737531ULL));
    ret_enc1 = bench_crypto_kem_enc_current(g_ct1, g_ss2, g_pk1);
    ret_dec1 = bench_crypto_kem_dec_current(g_ss3, g_ct1, g_sk1);

    enc_ret_mismatches += ret_enc0 != ret_enc1;
    dec_ret_mismatches += ret_dec0 != 0 || ret_dec1 != 0;
    ct_mismatches +=
        first_byte_mismatch(g_ct0, g_ct1, sizeof(g_ct0)) != sizeof(g_ct0);
    enc_ss_mismatches +=
        first_byte_mismatch(g_ss0, g_ss2, sizeof(g_ss0)) != sizeof(g_ss0);
    dec_ss_mismatches +=
        first_byte_mismatch(g_ss0, g_ss1, sizeof(g_ss0)) != sizeof(g_ss0);
    dec_ss_mismatches +=
        first_byte_mismatch(g_ss2, g_ss3, sizeof(g_ss2)) != sizeof(g_ss2);
  }

  printf("kem_correctness,valid_seeds=%d,keypair_ret_mismatches=%" PRIu64
         ",pk_mismatch_seeds=%" PRIu64 ",sk_mismatch_seeds=%" PRIu64
         ",enc_ret_mismatches=%" PRIu64 ",dec_ret_mismatches=%" PRIu64
         ",ct_mismatch_seeds=%" PRIu64 ",enc_ss_mismatch_seeds=%" PRIu64
         ",dec_ss_mismatch_seeds=%" PRIu64 "\n",
         NKEMDIFF, keypair_ret_mismatches, pk_mismatches, sk_mismatches,
         enc_ret_mismatches, dec_ret_mismatches, ct_mismatches,
         enc_ss_mismatches, dec_ss_mismatches);

  return keypair_ret_mismatches != 0 || pk_mismatches != 0 ||
         sk_mismatches != 0 || enc_ret_mismatches != 0 ||
         dec_ret_mismatches != 0 || ct_mismatches != 0 ||
         enc_ss_mismatches != 0 || dec_ss_mismatches != 0;
}

static NOINLINE void target_keypair_current(size_t idx)
{
  randombytes_reset(seed_for_index(idx, 0x3141592653589793ULL));
  (void)bench_crypto_kem_keypair_current(g_pk0, g_sk0);
  g_sink ^= g_pk0[idx % sizeof(g_pk0)];
  g_sink ^= (uint64_t)g_sk0[(idx + 17) % sizeof(g_sk0)] << 8;
}

static NOINLINE void target_keypair_paper_hier_k8(size_t idx)
{
  randombytes_reset(seed_for_index(idx, 0x3141592653589793ULL));
  (void)bench_crypto_kem_keypair_paper_hier_k8(g_pk1, g_sk1);
  g_sink ^= g_pk1[idx % sizeof(g_pk1)];
  g_sink ^= (uint64_t)g_sk1[(idx + 19) % sizeof(g_sk1)] << 8;
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

static struct counts measure_once(bench_target_fn fn)
{
  uint64_t values[PMU_EVENT_COUNT + 1] = {0};

  ioctl(g_leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(g_leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (size_t i = 0; i < NITERATIONS; i++)
    fn(i);
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

  for (size_t i = 0; i < NWARMUP; i++)
    variant->target(i);
  for (size_t t = 0; t < NTESTS; t++)
  {
    struct counts c = measure_once(variant->target);

    cycles[t] = c.cycles / NITERATIONS;
    instructions[t] = c.instructions / NITERATIONS;
  }
  qsort(cycles, NTESTS, sizeof(cycles[0]), cmp_u64);
  qsort(instructions, NTESTS, sizeof(instructions[0]), cmp_u64);
  p25 = cycles[NTESTS / 4];
  p50 = cycles[NTESTS / 2];
  p75 = cycles[(3 * NTESTS) / 4];

  printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_min=%" PRIu64
         ",cycles_max=%" PRIu64 ",cycles_iqr=%" PRIu64
         ",instr_p50=%" PRIu64 ",ipc=%.3f\n",
         variant->name, p50, cycles[0], cycles[NTESTS - 1], p75 - p25,
         instructions[NTESTS / 2],
         p50 == 0 ? 0.0 : (double)instructions[NTESTS / 2] / (double)p50);
}

static void run_pmu(void)
{
  static const struct variant variants[] = {
      {"keypair_current_gt", target_keypair_current},
      {"keypair_paper_hier_k8", target_keypair_paper_hier_k8},
  };

  setup_perf_events();
  printf("pmu_settings,NTESTS=%d,NITERATIONS=%d,NWARMUP=%d,NKEMDIFF=%d\n",
         NTESTS, NITERATIONS, NWARMUP, NKEMDIFF);
  bench_print_gt_production_config();
  for (size_t i = 0; i < sizeof(variants) / sizeof(variants[0]); i++)
    run_one_variant(&variants[i]);
  printf("sink=%" PRIu64 "\n", g_sink);
  close_perf_events();
}

int main(void)
{
  if (run_kem_correctness() != 0)
    return 1;
  run_pmu();
  return 0;
}
