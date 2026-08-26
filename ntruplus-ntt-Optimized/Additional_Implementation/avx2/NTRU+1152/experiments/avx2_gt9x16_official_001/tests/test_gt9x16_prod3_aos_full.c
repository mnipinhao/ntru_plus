#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0-prod2-ma2-asm.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"

#define N 1152
#define RANDOM_TRIALS 4099
#define STORAGE_BYTES 2432
#define UNALIGNED_OFFSET 34

static uint64_t random_state = UINT64_C(0x1152f011a05c2026);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void fail_difference(const char *label, int trial, int index,
                            int16_t expected, int16_t actual) {
  fprintf(stderr,
          "%s trial=%d raw full-state mismatch index=%d expected=%" PRId16
          " actual=%" PRId16 "\n",
          label, trial, index, expected, actual);
  exit(1);
}

static void run_case(const char *label, int trial, const int16_t input[N]) {
  _Alignas(32) int16_t split[N];
  _Alignas(32) int16_t split_before[N];
  _Alignas(32) int16_t control[N];
  _Alignas(32) unsigned char storage[STORAGE_BYTES];
  int16_t *candidate = (int16_t *)(void *)(storage + UNALIGNED_OFFSET);
  int index;

  memset(control, 0x5a, sizeof control);
  memset(storage, 0xa5, sizeof storage);
  ntruplus1152_exp001_top_split_small(split, input);
  memcpy(split_before, split, sizeof split);
  memcpy(candidate, split, sizeof split);

  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(control, split, 0, 0);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(control, split, 0, 1);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(control, split, 1, 0);
  ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(control, split, 1, 1);
  ntruplus1152_exp001_gt9x16_prod3_aos_full(candidate);

  if (memcmp(split, split_before, sizeof split) != 0) {
    fprintf(stderr, "%s trial=%d P2-B control changed its source\n", label,
            trial);
    exit(1);
  }
  for (index = 0; index < N; ++index)
    if (candidate[index] != control[index])
      fail_difference(label, trial, index, control[index], candidate[index]);
  for (index = 0; index < UNALIGNED_OFFSET; ++index)
    if (storage[index] != 0xa5) {
      fprintf(stderr, "%s trial=%d prefix canary changed at %d\n", label,
              trial, index);
      exit(1);
    }
  for (index = UNALIGNED_OFFSET + (int)sizeof split; index < STORAGE_BYTES;
       ++index)
    if (storage[index] != 0xa5) {
      fprintf(stderr, "%s trial=%d suffix canary changed at %d\n", label,
              trial, index);
      exit(1);
    }
}

int main(void) {
  int16_t input[N];
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
  for (index = 0; index < N; ++index)
    input[index] = (int16_t)((index & 1) ? 1 : -1);
  run_case("alternating", 0, input);

  for (trial = 0; trial < RANDOM_TRIALS; ++trial) {
    for (index = 0; index < N; ++index)
      input[index] = (int16_t)((int)(random_u32() % 3) - 1);
    run_case("random-small", trial, input);
  }

  puts("GT9X16-PROD3-AOS-FULL raw 2304-byte P2-B differential passed");
  return 0;
}
