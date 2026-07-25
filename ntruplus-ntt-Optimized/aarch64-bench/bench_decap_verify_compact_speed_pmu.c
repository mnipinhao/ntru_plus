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
#include "randombytes.h"

#ifndef NTESTS
#define NTESTS 61
#endif
#ifndef NITERATIONS
#define NITERATIONS 1000
#endif
#ifndef NWARMUP
#define NWARMUP 100
#endif
#ifndef NINPUTS
#define NINPUTS 32
#endif
#ifndef BENCH_VARIANT_A_DEC
#define BENCH_VARIANT_A_DEC bench_crypto_kem_dec_compact
#endif
#ifndef BENCH_VARIANT_A_KEYPAIR
#define BENCH_VARIANT_A_KEYPAIR bench_crypto_kem_keypair_compact
#endif
#ifndef BENCH_VARIANT_A_ENC
#define BENCH_VARIANT_A_ENC bench_crypto_kem_enc_compact
#endif
#ifndef BENCH_VARIANT_A_NAME
#define BENCH_VARIANT_A_NAME "compact_f1"
#endif
#ifndef BENCH_VARIANT_B_DEC
#define BENCH_VARIANT_B_DEC bench_crypto_kem_dec_speed
#endif
#ifndef BENCH_VARIANT_B_NAME
#define BENCH_VARIANT_B_NAME "speed_f2"
#endif
#ifndef BENCH_PAIRED_LABEL
#define BENCH_PAIRED_LABEL "compact_minus_speed"
#endif

#define VARIANT_COUNT 2
#define EVENT_COUNT 2

typedef int (*dec_fn)(uint8_t *, const uint8_t *, const uint8_t *);

struct input_case {
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t ss[CRYPTO_BYTES];
};

struct counts {
  uint64_t cycles;
  uint64_t instructions;
};

int BENCH_VARIANT_A_KEYPAIR(uint8_t *pk, uint8_t *sk);
int BENCH_VARIANT_A_ENC(uint8_t *ct, uint8_t *ss, const uint8_t *pk);
int BENCH_VARIANT_A_DEC(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);
int BENCH_VARIANT_B_DEC(uint8_t *ss, const uint8_t *ct, const uint8_t *sk);

static const dec_fn variants[VARIANT_COUNT] = {
    BENCH_VARIANT_A_DEC,
    BENCH_VARIANT_B_DEC,
};
static const char *const variant_names[VARIANT_COUNT] = {
    BENCH_VARIANT_A_NAME,
    BENCH_VARIANT_B_NAME,
};

static struct input_case inputs[NINPUTS] __attribute__((aligned(64)));
static uint8_t ss_work[CRYPTO_BYTES] __attribute__((aligned(64)));
static uint64_t replay_state;
static int leader_fd = -1;
static int event_fds[EVENT_COUNT] = {-1, -1};
static volatile uint64_t sink;

void randombytes(uint8_t *out, size_t outlen)
{
  size_t i;

  for (i = 0; i < outlen; i++) {
    replay_state = replay_state * UINT64_C(6364136223846793005) +
                   UINT64_C(1442695040888963407);
    out[i] = (uint8_t)(replay_state >> 56);
  }
}

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

static struct counts measure(dec_fn fn)
{
  uint64_t values[EVENT_COUNT + 1] = {0};
  size_t i;

  ioctl(leader_fd, PERF_EVENT_IOC_RESET, PERF_IOC_FLAG_GROUP);
  ioctl(leader_fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);
  for (i = 0; i < NITERATIONS; i++) {
    const struct input_case *input = &inputs[i % NINPUTS];
    fn(ss_work, input->ct, input->sk);
    sink ^= ss_work[i % CRYPTO_BYTES];
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
  size_t i;
  unsigned mismatches = 0;

  for (i = 0; i < NINPUTS; i++) {
    uint8_t ss_compact[CRYPTO_BYTES];
    uint8_t ss_speed[CRYPTO_BYTES];
    uint8_t bad_ct[CRYPTO_CIPHERTEXTBYTES];
    int rc_compact;
    int rc_speed;

    replay_state = UINT64_C(0x100000001b3) ^ (uint64_t)i;
    if (BENCH_VARIANT_A_KEYPAIR(inputs[i].pk, inputs[i].sk) != 0)
      return 1;
    replay_state = UINT64_C(0x9e3779b97f4a7c15) ^ (uint64_t)i;
    if (BENCH_VARIANT_A_ENC(inputs[i].ct, inputs[i].ss, inputs[i].pk) != 0)
      return 1;

    rc_compact = BENCH_VARIANT_A_DEC(
        ss_compact, inputs[i].ct, inputs[i].sk);
    rc_speed = BENCH_VARIANT_B_DEC(ss_speed, inputs[i].ct, inputs[i].sk);
    if (rc_compact != rc_speed ||
        memcmp(ss_compact, ss_speed, sizeof ss_compact) != 0 ||
        memcmp(ss_compact, inputs[i].ss, sizeof ss_compact) != 0)
      mismatches++;

    memcpy(bad_ct, inputs[i].ct, sizeof bad_ct);
    bad_ct[(37 * i + 11) % sizeof bad_ct] ^= (uint8_t)(1u << (i & 7));
    rc_compact = BENCH_VARIANT_A_DEC(ss_compact, bad_ct, inputs[i].sk);
    rc_speed = BENCH_VARIANT_B_DEC(ss_speed, bad_ct, inputs[i].sk);
    if (rc_compact != rc_speed ||
        memcmp(ss_compact, ss_speed, sizeof ss_compact) != 0)
      mismatches++;
  }
  printf("correctness,total_mismatches=%u,valid=%d,invalid=%d\n",
         mismatches, NINPUTS, NINPUTS);
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
  printf("pmu,%s,cycles_p50=%" PRIu64 ",cycles_min=%" PRIu64
         ",cycles_max=%" PRIu64 ",instr_p50=%" PRIu64
         ",cpi_x1000=%" PRIu64 ",addr_mod32=%" PRIuPTR
         ",addr_mod64=%" PRIuPTR "\n",
         variant_names[variant], c[NTESTS / 2], c[0], c[NTESTS - 1],
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
  unsigned variant_a_wins = 0;
  size_t test;

  if (prepare_and_check() != 0)
    return 1;
  for (test = 0; test < NWARMUP; test++) {
    variants[test & 1](ss_work, inputs[test % NINPUTS].ct,
                       inputs[test % NINPUTS].sk);
    variants[(test & 1) ^ 1](ss_work, inputs[test % NINPUTS].ct,
                             inputs[test % NINPUTS].sk);
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
    variant_a_wins += delta[test] < 0;
  }
  qsort(delta, NTESTS, sizeof delta[0], cmp_i64);
  printf("paired,%s,delta_p10=%" PRId64
         ",delta_p50=%" PRId64 ",delta_p90=%" PRId64
         ",variant_a_wins=%u/%d\n",
         BENCH_PAIRED_LABEL,
         delta[NTESTS / 10], delta[NTESTS / 2],
         delta[(9 * NTESTS) / 10], variant_a_wins, NTESTS);
  printf("sink=%" PRIu64 "\n", sink);
  return 0;
}
