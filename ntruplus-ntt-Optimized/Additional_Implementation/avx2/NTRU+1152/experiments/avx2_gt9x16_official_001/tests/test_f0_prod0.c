#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0-official-to-f0.h"
#include "f0-prod0-ranges.h"
#include "f0_forward_for_ma2.h"
#include "poly.h"

#define RANDOM_TRIALS 1003

static uint64_t random_state = UINT64_C(0xf0d01152a55a0001);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int canonical(int value) {
  value %= 3457;
  return value < 0 ? value + 3457 : value;
}

static void compare_case(const char *label, int trial, const int16_t *expected,
                         const int16_t *actual, int exact) {
  int index;
  for (index = 0; index < NTRUPLUS1152_EXP001_F0_N; ++index)
    if ((exact && expected[index] != actual[index]) ||
        (!exact && canonical(expected[index]) != canonical(actual[index]))) {
      fprintf(stderr,
              "%s trial=%d index=%d expected=%" PRId16 " actual=%" PRId16
              "\n",
              label, trial, index, expected[index], actual[index]);
      exit(1);
    }
}

static void run_case(const char *label, int trial, const int16_t *source) {
  _Alignas(32) int16_t input[NTRUPLUS1152_EXP001_F0_N];
  _Alignas(32) int16_t expected[NTRUPLUS1152_EXP001_F0_N];
  _Alignas(32) int16_t actual[NTRUPLUS1152_EXP001_F0_N];
  _Alignas(32) int16_t alias[NTRUPLUS1152_EXP001_F0_N];
  poly official;

  memcpy(input, source, sizeof input);
  memcpy(official.coeffs, source, sizeof official.coeffs);
  poly_ntt(&official);
  ntruplus1152_exp001_official_to_f0(expected, official.coeffs);

  ntruplus1152_exp001_f0_forward_for_ma2(actual, input);
  for (int index = 0; index < NTRUPLUS1152_EXP001_F0_N; ++index)
    if (actual[index] < ntruplus1152_exp001_f0_prod0_min[index] ||
        actual[index] > ntruplus1152_exp001_f0_prod0_max[index]) {
      fprintf(stderr, "%s trial=%d index=%d raw F0 value out of proved range\n",
              label, trial, index);
      exit(1);
    }
  compare_case(label, trial, expected, actual, 0);
  compare_case("input-immutability", trial, source, input, 1);

  memcpy(alias, source, sizeof alias);
  ntruplus1152_exp001_f0_forward_for_ma2(alias, alias);
  compare_case("alias", trial, expected, alias, 0);
}

static void test_canary(void) {
  struct __attribute__((aligned(32))) guarded {
    uint64_t before[4];
    int16_t value[NTRUPLUS1152_EXP001_F0_N];
    uint64_t after[4];
  } output;
  _Alignas(32) int16_t input[NTRUPLUS1152_EXP001_F0_N] = {0};
  int index;
  for (index = 0; index < 4; ++index) {
    output.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
    output.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
  }
  ntruplus1152_exp001_f0_forward_for_ma2(output.value, input);
  for (index = 0; index < 4; ++index)
    if (output.before[index] !=
            (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
        output.after[index] !=
            (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index)) {
      fputs("F0-PROD0 output canary corruption\n", stderr);
      exit(1);
    }
}

int main(void) {
  _Alignas(32) int16_t input[NTRUPLUS1152_EXP001_F0_N];
  int index, trial;

  memset(input, 0, sizeof input);
  run_case("zero", 0, input);
  for (index = 0; index < NTRUPLUS1152_EXP001_F0_N; ++index) {
    memset(input, 0, sizeof input);
    input[index] = 1;
    run_case("positive-impulse", index, input);
    input[index] = -1;
    run_case("negative-impulse", index, input);
  }
  for (index = 0; index < NTRUPLUS1152_EXP001_F0_N; ++index)
    input[index] = (int16_t)((index & 1) ? -1 : 1);
  run_case("alternating-bound", 0, input);

  for (trial = 0; trial < RANDOM_TRIALS; ++trial) {
    for (index = 0; index < NTRUPLUS1152_EXP001_F0_N; ++index)
      input[index] = (int16_t)((int)(random_u32() % 3) - 1);
    run_case("random-kem-small", trial, input);
  }
  test_canary();
  printf("F0-PROD0: coefficient->scale4-F0 canonical differential for 2304 "
         "impulses, %d random, "
         "boundary, alias, immutability, and canary cases\n",
         RANDOM_TRIALS);
  return 0;
}
