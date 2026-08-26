#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16_prod3_aos_c1_tile.h"

#define Q 3457
#define D4_BOUND 16691
#define FINAL_MIN (-20751)
#define FINAL_MAX 20753
#define RANDOM_TRIALS 10003
#define STORAGE_BYTES 256
#define WORD_BYTES (NTRUPLUS1152_EXP001_PROD3_AOS_TILE_WORDS * sizeof(int16_t))
#define UNALIGNED_OFFSET 34

static uint64_t random_state = UINT64_C(0x3a051152c1a0d401);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int16_t montgomery_reduce(int32_t value) {
  int16_t low = (int16_t)value * 12929;
  return (int16_t)((value - (int32_t)low * Q) >> 16);
}

static void reference(int16_t output[64], const int16_t input[64]) {
  static const int16_t d2_zeta[4] = {-147, 366, -109, 1118};
  static const int16_t d1_zeta[8] = {
      -147, 366, -109, 1118, 1339, -794, 1181, 446};
  int16_t state[16][4];
  int block, coefficient, q;

  for (q = 0; q < 16; ++q)
    for (coefficient = 0; coefficient < 4; ++coefficient)
      state[q][coefficient] = input[4 * q + coefficient];

  for (block = 0; block < 16; block += 4)
    for (q = 0; q < 2; ++q)
      for (coefficient = 0; coefficient < 4; ++coefficient) {
        int left = block + q;
        int right = left + 2;
        int factor = block / 4;
        int16_t a = state[left][coefficient];
        int16_t t = montgomery_reduce(
            (int32_t)state[right][coefficient] * d2_zeta[factor]);
        state[left][coefficient] = (int16_t)(a + t);
        state[right][coefficient] = (int16_t)(a - t);
      }

  for (q = 0; q < 16; q += 2)
    for (coefficient = 0; coefficient < 4; ++coefficient) {
      int16_t a = state[q][coefficient];
      int16_t t = montgomery_reduce(
          (int32_t)state[q + 1][coefficient] * d1_zeta[q / 2]);
      state[q][coefficient] = (int16_t)(a + t);
      state[q + 1][coefficient] = (int16_t)(a - t);
    }

  for (coefficient = 0; coefficient < 4; ++coefficient)
    for (q = 0; q < 16; ++q)
      output[16 * coefficient + q] = state[q][coefficient];
}

static void compare(const char *label, int trial, const int16_t expected[64],
                    const int16_t actual[64]) {
  int index;
  for (index = 0; index < 64; ++index)
    if (expected[index] != actual[index]) {
      fprintf(stderr,
              "%s trial=%d index=%d expected=%" PRId16 " actual=%" PRId16 "\n",
              label, trial, index, expected[index], actual[index]);
      exit(1);
    }
  for (index = 0; index < 64; ++index)
    if (actual[index] < FINAL_MIN || actual[index] > FINAL_MAX) {
      fprintf(stderr, "%s trial=%d index=%d escaped proved range: %" PRId16 "\n",
              label, trial, index, actual[index]);
      exit(1);
    }
}

static void run_case(const char *label, int trial, const int16_t source[64]) {
  _Alignas(32) unsigned char input_storage[STORAGE_BYTES];
  _Alignas(32) unsigned char output_storage[STORAGE_BYTES];
  unsigned char input_before[STORAGE_BYTES];
  int16_t expected[64];
  int16_t alias[64];
  int16_t actual[64];
  int16_t *input = (int16_t *)(void *)(input_storage + UNALIGNED_OFFSET);
  int16_t *output = (int16_t *)(void *)(output_storage + UNALIGNED_OFFSET);
  size_t index;

  memset(input_storage, 0xa5, sizeof input_storage);
  memset(output_storage, 0x5a, sizeof output_storage);
  memcpy(input, source, WORD_BYTES);
  memcpy(input_before, input_storage, sizeof input_storage);
  reference(expected, source);

  ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0(output, input);
  memcpy(actual, output, WORD_BYTES);
  compare(label, trial, expected, actual);
  if (memcmp(input_before, input_storage, sizeof input_storage) != 0) {
    fprintf(stderr, "%s trial=%d modified input\n", label, trial);
    exit(1);
  }
  for (index = 0; index < sizeof output_storage; ++index)
    if ((index < UNALIGNED_OFFSET || index >= UNALIGNED_OFFSET + WORD_BYTES) &&
        output_storage[index] != 0x5a) {
      fprintf(stderr, "%s trial=%d output canary changed at %zu\n",
              label, trial, index);
      exit(1);
    }

  memcpy(alias, source, sizeof alias);
  ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0(alias, alias);
  compare("alias", trial, expected, alias);
}

int main(void) {
  int16_t input[64];
  int trial, index;

  memset(input, 0, sizeof input);
  run_case("zero", 0, input);
  for (index = 0; index < 64; ++index) {
    memset(input, 0, sizeof input);
    input[index] = 1;
    run_case("positive-impulse", index, input);
    input[index] = -1;
    run_case("negative-impulse", index, input);
  }
  for (index = 0; index < 64; ++index)
    input[index] = (int16_t)((index & 1) ? D4_BOUND : -D4_BOUND);
  run_case("alternating-bound", 0, input);

  for (trial = 0; trial < RANDOM_TRIALS; ++trial) {
    for (index = 0; index < 64; ++index)
      input[index] = (int16_t)(-D4_BOUND +
          (int)(random_u32() % (unsigned)(2 * D4_BOUND + 1)));
    run_case("random-d4-range", trial, input);
  }

  puts("GT9X16-PROD3-AOS-ASM0 C1 tile correctness passed");
  return 0;
}
