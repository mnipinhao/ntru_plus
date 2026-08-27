#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"

void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_lazy_reduce(
    int16_t *state);

#define N 1152
#define RANDOM_TRIALS 1003
#define STORAGE_BYTES 2432
#define UNALIGNED_OFFSET 34
#define Q 3457
#define CANDIDATE_BOUND 21333

static uint64_t random_state = UINT64_C(0x7430626574616173);
static int observed_min = 32767;
static int observed_max = -32768;
static uint64_t raw_differences;

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int canonical(int value) {
  value %= Q;
  if (value < 0) value += Q;
  return value;
}

static void fail(const char *label, int trial, int index,
                 int expected, int actual) {
  fprintf(stderr, "%s trial=%d index=%d expected=%d actual=%d\n",
          label, trial, index, expected, actual);
  exit(1);
}

static void check_canary(const char *label, int trial,
                         const unsigned char storage[STORAGE_BYTES]) {
  int index;
  for (index = 0; index < UNALIGNED_OFFSET; ++index)
    if (storage[index] != 0xa5) fail(label, trial, index, 0xa5, storage[index]);
  for (index = UNALIGNED_OFFSET + 2 * N; index < STORAGE_BYTES; ++index)
    if (storage[index] != 0xa5) fail(label, trial, index, 0xa5, storage[index]);
}

static void run_case(const char *label, int trial, const int16_t input[N]) {
  _Alignas(32) int16_t input_before[N], split[N];
  _Alignas(32) unsigned char control_storage[STORAGE_BYTES];
  _Alignas(32) unsigned char candidate_storage[STORAGE_BYTES];
  _Alignas(32) unsigned char lazy_storage[STORAGE_BYTES];
  int16_t *control = (int16_t *)(void *)(control_storage + UNALIGNED_OFFSET);
  int16_t *candidate = (int16_t *)(void *)(candidate_storage + UNALIGNED_OFFSET);
  int16_t *lazy = (int16_t *)(void *)(lazy_storage + UNALIGNED_OFFSET);
  int index;

  memcpy(input_before, input, sizeof input_before);
  ntruplus1152_exp001_top_split_small(split, input);
  memset(control_storage, 0xa5, sizeof control_storage);
  memset(candidate_storage, 0xa5, sizeof candidate_storage);
  memset(lazy_storage, 0xa5, sizeof lazy_storage);
  memcpy(control, split, sizeof split);
  memcpy(candidate, split, sizeof split);
  memcpy(lazy, split, sizeof split);

  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(control);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(candidate);
  ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_lazy_reduce(lazy);

  if (memcmp(input, input_before, sizeof input_before) != 0)
    fail("coefficient-input-immutability", trial, 0, 0, 1);
  for (index = 0; index < N; ++index) {
    if (canonical(control[index]) != canonical(candidate[index]))
      fail(label, trial, index, canonical(control[index]),
           canonical(candidate[index]));
    if (canonical(candidate[index]) != canonical(lazy[index]))
      fail("lazy-reduction-canonical", trial, index,
           canonical(candidate[index]), canonical(lazy[index]));
    raw_differences += control[index] != candidate[index];
    if (candidate[index] < observed_min) observed_min = candidate[index];
    if (candidate[index] > observed_max) observed_max = candidate[index];
    if (candidate[index] < -CANDIDATE_BOUND ||
        candidate[index] > CANDIDATE_BOUND)
      fail("candidate-range", trial, index, CANDIDATE_BOUND, candidate[index]);
    if (lazy[index] < -CANDIDATE_BOUND || lazy[index] > CANDIDATE_BOUND)
      fail("lazy-reduction-range", trial, index, CANDIDATE_BOUND, lazy[index]);
  }
  check_canary("control-canary", trial, control_storage);
  check_canary("candidate-canary", trial, candidate_storage);
  check_canary("lazy-reduction-canary", trial, lazy_storage);
}

int main(void) {
  _Alignas(32) int16_t input[N];
  int index, trial;

  memset(input, 0, sizeof input);
  run_case("zero", 0, input);
  for (index = 0; index < N; ++index) {
    memset(input, 0, sizeof input);
    input[index] = 1;
    run_case("positive-impulse", index, input);
    input[index] = -1;
    run_case("negative-impulse", index, input);
  }
  for (index = 0; index < N; ++index) input[index] = (index & 1) ? -1 : 1;
  run_case("alternating-boundary", 0, input);
  for (index = 0; index < N; ++index) input[index] = 1;
  run_case("positive-boundary", 0, input);
  for (index = 0; index < N; ++index) input[index] = -1;
  run_case("negative-boundary", 0, input);

  for (trial = 0; trial < RANDOM_TRIALS; ++trial) {
    for (index = 0; index < N; ++index)
      input[index] = (int16_t)((int)(random_u32() % 3U) - 1);
    run_case("random-small", trial, input);
  }
  if (!raw_differences) fail("representative-diagnostic", 0, 0, 1, 0);
  printf("T0-beta full Natural-Q canonical differential passed; raw-diff=%" PRIu64
         " observed=[%d,%d]\n", raw_differences, observed_min, observed_max);
  return 0;
}
