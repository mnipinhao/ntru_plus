#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16_prod3_hash_fanout.h"

#define RANDOM_TRIALS 1003

static uint64_t random_state = UINT64_C(0xfac0115216352026);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void fail(const char *label, int trial, const char *reason) {
  fprintf(stderr, "%s trial=%d: %s\n", label, trial, reason);
  exit(1);
}

static void run_case(const char *label, int trial, const poly *input) {
  poly o0 = *input;
  poly o1 = *input;
  poly input_before = *input;
  poly generic_scratch;
  poly official_scratch;
  _Alignas(32) int16_t c0[NTRUPLUS_N];
  _Alignas(32) int16_t c1[NTRUPLUS_N];
  uint8_t o1_bytes[NTRUPLUS_POLYBYTES];
  uint8_t c1_bytes[NTRUPLUS_POLYBYTES];

  ntruplus1152_exp001_hash_fanout_o0(&o0);
  ntruplus1152_exp001_hash_fanout_o1(o1_bytes, &o1);
  ntruplus1152_exp001_hash_fanout_c0(c0, input);
  ntruplus1152_exp001_hash_fanout_c1(
      c1_bytes, c1, input, &generic_scratch, &official_scratch);

  if (memcmp(&o0, &o1, sizeof o0) != 0)
    fail(label, trial, "O0 and O1 Official states differ");
  if (memcmp(c0, c1, sizeof c0) != 0)
    fail(label, trial, "C0 and C1 MA2 planes differ");
  if (memcmp(o1_bytes, c1_bytes, sizeof o1_bytes) != 0)
    fail(label, trial, "O1 and C1 hash bytes differ");
  if (memcmp(input, &input_before, sizeof *input) != 0)
    fail(label, trial, "candidate changed coefficient input");
}

int main(void) {
  poly input;
  int index, trial;

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
  puts("PROD3 r hash fanout O0/O1/C0/C1 exact differential passed");
  return 0;
}
