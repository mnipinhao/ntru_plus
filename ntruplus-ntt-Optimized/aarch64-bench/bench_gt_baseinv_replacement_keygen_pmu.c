/* Single-backend full-keygen PMU harness for baseinv replacement builds. */
#if !defined(__linux__)
#error "bench_gt_baseinv_replacement_keygen_pmu requires Linux perf_event_open"
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
#include "poly.h"
#include "randombytes.h"

#ifndef GT_BASEINV_REPLACEMENT_VARIANT
#define GT_BASEINV_REPLACEMENT_VARIANT "unknown"
#endif

int poly_baseinv_scaled_r(poly *r, const poly *a);

enum event_source {
  EVENT_SOURCE_FIXED = 0,
  EVENT_SOURCE_CPU_PMU
};

struct event_spec {
  const char *name;
  enum event_source source;
  uint32_t type;
  uint64_t config;
};

static const struct event_spec g_events[] = {
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

static uint8_t g_pk[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_sk[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t g_ct[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t g_ss_enc[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint8_t g_ss_dec[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint64_t g_replay_state;
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

static uint64_t digest_bytes(uint64_t digest, const uint8_t *buf, size_t len)
{
  size_t i;

  for (i = 0; i < len; i++) {
    digest ^= buf[i];
    digest *= UINT64_C(1099511628211);
  }
  return digest;
}

static uint64_t key_seed(size_t sample, size_t iteration, uint64_t domain)
{
  return mix_seed(domain ^ ((uint64_t)sample << 32) ^ iteration);
}

static int run_keypairs(size_t count, size_t sample, uint64_t domain)
{
  size_t i;

  for (i = 0; i < count; i++) {
    set_replay_seed(key_seed(sample, i, domain));
    if (crypto_kem_keypair(g_pk, g_sk) != 0)
      return -1;
    g_sink ^= g_pk[(i + sample) % sizeof(g_pk)];
    g_sink ^= (uint64_t)g_sk[(i + sample + 17) % sizeof(g_sk)] << 8;
  }
  return 0;
}

static uint64_t final_output_digest(void)
{
  uint64_t digest = UINT64_C(1469598103934665603);

  digest = digest_bytes(digest, g_pk, sizeof(g_pk));
  return digest_bytes(digest, g_sk, sizeof(g_sk));
}

static int run_correctness(size_t count)
{
  uint64_t digest = UINT64_C(1469598103934665603);
  size_t i;
  int decap_failures = 0;
  int shared_secret_mismatches = 0;

  for (i = 0; i < count; i++) {
    set_replay_seed(key_seed(0, i, UINT64_C(0x6b65797061697231)));
    if (crypto_kem_keypair(g_pk, g_sk) != 0)
      return -1;
    set_replay_seed(key_seed(0, i, UINT64_C(0x656e636170737531)));
    if (crypto_kem_enc(g_ct, g_ss_enc, g_pk) != 0)
      return -1;
    decap_failures += crypto_kem_dec(g_ss_dec, g_ct, g_sk) != 0;
    shared_secret_mismatches +=
        memcmp(g_ss_enc, g_ss_dec, sizeof(g_ss_enc)) != 0;
    digest = digest_bytes(digest, g_pk, sizeof(g_pk));
    digest = digest_bytes(digest, g_sk, sizeof(g_sk));
    digest = digest_bytes(digest, g_ct, sizeof(g_ct));
    digest = digest_bytes(digest, g_ss_enc, sizeof(g_ss_enc));
  }

  printf("correctness,variant=%s,cases=%zu,decap_failures=%d,"
         "shared_secret_mismatches=%d,digest=%016" PRIx64 "\n",
         GT_BASEINV_REPLACEMENT_VARIANT, count, decap_failures,
         shared_secret_mismatches, digest);
  return decap_failures == 0 && shared_secret_mismatches == 0 ? 0 : -1;
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

static const struct event_spec *find_event(const char *name)
{
  size_t i;

  for (i = 0; i < sizeof(g_events) / sizeof(g_events[0]); i++)
    if (strcmp(name, g_events[i].name) == 0)
      return &g_events[i];
  return NULL;
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

static int run_sample(const char *event_name, size_t iterations,
                      size_t warmup, size_t sample)
{
  const struct event_spec *spec = find_event(event_name);
  uint64_t count = 0;
  uint64_t digest;
  int cpu_pmu_type = read_cpu_pmu_type();
  int fd;

  if (spec == NULL) {
    fprintf(stderr, "unknown event: %s\n", event_name);
    return -1;
  }
  fd = open_event(spec, cpu_pmu_type);
  if (fd < 0) {
    printf("event_support,variant=%s,event=%s,available=0,errno=%d\n",
           GT_BASEINV_REPLACEMENT_VARIANT, event_name, errno);
    return 2;
  }

  if (run_keypairs(warmup, sample, UINT64_C(0x7761726d75703031)) != 0)
    return -1;
  if (ioctl(fd, PERF_EVENT_IOC_RESET, 0) != 0 ||
      ioctl(fd, PERF_EVENT_IOC_ENABLE, 0) != 0) {
    perror("perf ioctl enable");
    close(fd);
    return -1;
  }
  if (run_keypairs(iterations, sample,
                   UINT64_C(0x6d65617375726531)) != 0) {
    close(fd);
    return -1;
  }
  if (ioctl(fd, PERF_EVENT_IOC_DISABLE, 0) != 0 ||
      read(fd, &count, sizeof(count)) != (ssize_t)sizeof(count)) {
    perror("perf disable/read");
    close(fd);
    return -1;
  }
  close(fd);
  digest = final_output_digest();

  printf("sample,variant=%s,event=%s,sample=%zu,iterations=%zu,raw=%" PRIu64
         ",per_keypair=%.6f,digest=%016" PRIx64 "\n",
         GT_BASEINV_REPLACEMENT_VARIANT, event_name, sample, iterations,
         count, iterations ? (double)count / (double)iterations : 0.0,
         digest);
  return 0;
}

static uintptr_t address_from_keypair(void)
{
  int (*fn)(uint8_t *, uint8_t *) = crypto_kem_keypair;
  uintptr_t address = 0;

  memcpy(&address, &fn, sizeof(fn) < sizeof(address) ? sizeof(fn)
                                                    : sizeof(address));
  return address;
}

static uintptr_t address_from_baseinv(void)
{
  int (*fn)(poly *, const poly *) = poly_baseinv_scaled_r;
  uintptr_t address = 0;

  memcpy(&address, &fn, sizeof(fn) < sizeof(address) ? sizeof(fn)
                                                    : sizeof(address));
  return address;
}

static void print_layout(void)
{
  uintptr_t keypair = address_from_keypair();
  uintptr_t baseinv = address_from_baseinv();

  printf("layout,variant=%s,symbol=crypto_kem_keypair,address=0x%" PRIxPTR
         ",mod32=%" PRIuPTR ",mod64=%" PRIuPTR "\n",
         GT_BASEINV_REPLACEMENT_VARIANT, keypair, keypair & 31u,
         keypair & 63u);
  printf("layout,variant=%s,symbol=poly_baseinv_scaled_r,address=0x%" PRIxPTR
         ",mod32=%" PRIuPTR ",mod64=%" PRIuPTR "\n",
         GT_BASEINV_REPLACEMENT_VARIANT, baseinv, baseinv & 31u,
         baseinv & 63u);
  printf("layout,variant=%s,buffer=pk,address=%p,mod64=%" PRIuPTR "\n",
         GT_BASEINV_REPLACEMENT_VARIANT, (void *)g_pk,
         (uintptr_t)g_pk & 63u);
}

static size_t parse_size(const char *value, const char *label)
{
  char *end = NULL;
  unsigned long long parsed = strtoull(value, &end, 10);

  if (value[0] == '\0' || end == NULL || *end != '\0') {
    fprintf(stderr, "invalid %s: %s\n", label, value);
    exit(EXIT_FAILURE);
  }
  return (size_t)parsed;
}

int main(int argc, char **argv)
{
  printf("build,variant=%s,single_kem_body=1,direct_backend=1\n",
         GT_BASEINV_REPLACEMENT_VARIANT);
  if (argc == 2 && strcmp(argv[1], "--layout") == 0) {
    print_layout();
    return EXIT_SUCCESS;
  }
  if (argc == 3 && strcmp(argv[1], "--correctness") == 0)
    return run_correctness(parse_size(argv[2], "correctness cases")) == 0
               ? EXIT_SUCCESS
               : EXIT_FAILURE;
  if (argc == 6 && strcmp(argv[1], "--sample") == 0) {
    int ret = run_sample(argv[2], parse_size(argv[3], "iterations"),
                         parse_size(argv[4], "warmup"),
                         parse_size(argv[5], "sample"));
    return ret == 0 ? EXIT_SUCCESS : ret == 2 ? 2 : EXIT_FAILURE;
  }

  fprintf(stderr,
          "usage: %s --layout | --correctness CASES | "
          "--sample EVENT ITERATIONS WARMUP SAMPLE\n",
          argv[0]);
  return EXIT_FAILURE;
}
