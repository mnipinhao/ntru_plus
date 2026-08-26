#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0_prod3_hash_bridge.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"

#define RANDOM_TRIALS 4099

static uint64_t random_state = UINT64_C(0x1152f0a35a2026);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void run_case(const char *label, int trial, const poly *input) {
  poly official = *input;
  poly planes;
  poly planes_before;
  poly generic_scratch;
  poly official_scratch;
  uint8_t expected[NTRUPLUS_POLYBYTES];
  uint8_t actual[NTRUPLUS_POLYBYTES];

  poly_ntt(&official);
  poly_tobytes(expected, &official);

  ntruplus1152_exp001_top_split_small(planes.coeffs, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full(planes.coeffs);
  planes_before = planes;
  memset(actual, 0xa5, sizeof actual);
  ntruplus1152_exp001_prod3_hash_bytes(actual, planes.coeffs,
                                        &generic_scratch, &official_scratch);

  if (memcmp(&planes, &planes_before, sizeof planes) != 0) {
    fprintf(stderr, "%s trial=%d bridge changed MA2 planes\n", label, trial);
    exit(1);
  }
  if (memcmp(expected, actual, sizeof actual) != 0) {
    size_t index;
    for (index = 0; index < sizeof actual; ++index)
      if (expected[index] != actual[index])
        break;
    fprintf(stderr,
            "%s trial=%d hash-input byte mismatch index=%zu expected=%u "
            "actual=%u\n",
            label, trial, index, (unsigned)expected[index],
            (unsigned)actual[index]);
    exit(1);
  }
}

int main(void) {
  poly input;
  int index;
  int trial;

  memset(&input, 0, sizeof input);
  run_case("zero", 0, &input);
  for (index = 0; index < NTRUPLUS_N; ++index) {
    memset(&input, 0, sizeof input);
    input.coeffs[index] = 1;
    run_case("positive-impulse", index, &input);
    input.coeffs[index] = -1;
    run_case("negative-impulse", index, &input);
  }
  for (index = 0; index < NTRUPLUS_N; ++index)
    input.coeffs[index] = (int16_t)((index & 1) ? 1 : -1);
  run_case("alternating", 0, &input);

  for (trial = 0; trial < RANDOM_TRIALS; ++trial) {
    for (index = 0; index < NTRUPLUS_N; ++index)
      input.coeffs[index] = (int16_t)((int)(random_u32() % 3) - 1);
    run_case("random-small", trial, &input);
  }

  puts("PROD3 MA2 planes -> Official hash-input bytes: exact differential passed");
  return 0;
}
