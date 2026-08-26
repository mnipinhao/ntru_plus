#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16-prod3-ma2-hash-h1-map.h"
#include "gt9x16-prod3-ma2-hash-h1.h"
#include "gt9x16_forward.h"
#include "gt9x16_prod3_aos_full.h"
#include "poly.h"

#define N 1152
#define POLYBYTES 1728
#define RANDOM_PLANE_TRIALS 1003
#define RANDOM_CALLER_TRIALS 1003
#define GUARD 64

static uint64_t random_state = UINT64_C(0x48315f41534d3026);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int16_t bits_to_i16(uint16_t value) {
  int16_t result;
  memcpy(&result, &value, sizeof result);
  return result;
}

static int16_t mullo_i16(int16_t left, int16_t right) {
  return bits_to_i16((uint16_t)((uint32_t)(uint16_t)left *
                                (uint32_t)(uint16_t)right));
}

static int16_t mulhi_i16(int16_t left, int16_t right) {
  int32_t product = (int32_t)left * (int32_t)right;
  int32_t quotient = product / 65536;
  if (product < 0 && product % 65536 != 0)
    --quotient;
  return (int16_t)quotient;
}

static uint16_t remove_scale_and_canonicalize(int16_t value) {
  int16_t low = mullo_i16(value, 16379);
  int16_t high = mulhi_i16(value, -901);
  int16_t reduced = (int16_t)(high - mulhi_i16(low, 3457));
  if (reduced < 0)
    reduced = (int16_t)(reduced + 3457);
  if (reduced < 0 || reduced >= 3457) {
    fprintf(stderr, "scalar oracle range failure: input=%d output=%d\n",
            (int)value, (int)reduced);
    exit(1);
  }
  return (uint16_t)reduced;
}

static void scalar_serialize(uint8_t output[POLYBYTES],
                             const int16_t planes[N]) {
  int official;
  memset(output, 0, POLYBYTES);
  for (official = 0; official < N; ++official) {
    uint16_t value = remove_scale_and_canonicalize(
        planes[ntruplus1152_exp001_h1_source_for_official[official]]);
    uint16_t item;
    for (item = ntruplus1152_exp001_h1_contribution_offset[official];
         item < ntruplus1152_exp001_h1_contribution_offset[official + 1];
         ++item) {
      const ntruplus1152_exp001_h1_contribution *contribution =
          &ntruplus1152_exp001_h1_contribution_table[item];
      uint16_t mask = (uint16_t)((UINT16_C(1) << contribution->width) - 1);
      output[contribution->byte_index] |= (uint8_t)(
          ((value >> contribution->coefficient_low_bit) & mask)
          << contribution->byte_low_bit);
    }
  }
}

static void fail_mismatch(const char *label, int trial,
                          const uint8_t expected[POLYBYTES],
                          const uint8_t actual[POLYBYTES]) {
  size_t index;
  for (index = 0; index < POLYBYTES; ++index)
    if (expected[index] != actual[index])
      break;
  fprintf(stderr,
          "%s trial=%d byte=%zu expected=%u actual=%u\n",
          label, trial, index, (unsigned)expected[index],
          (unsigned)actual[index]);
  exit(1);
}

static void run_plane_case(const char *label, int trial,
                           const int16_t input[N], int unaligned) {
  _Alignas(32) uint8_t source_storage[GUARD + 2304 + GUARD + 1];
  uint8_t output_storage[GUARD + POLYBYTES + GUARD + 1];
  uint8_t source_before[sizeof source_storage];
  uint8_t expected[POLYBYTES];
  int16_t *source =
      (int16_t *)(void *)(source_storage + GUARD + 2 * unaligned);
  uint8_t *actual = output_storage + GUARD + unaligned;
  size_t index;

  memset(source_storage, 0x6b, sizeof source_storage);
  memset(output_storage, 0xa7, sizeof output_storage);
  memcpy(source, input, 2304);
  memcpy(source_before, source_storage, sizeof source_storage);
  scalar_serialize(expected, source);
  ntruplus1152_exp001_prod3_ma2_hash_h1(actual, source);
  if (memcmp(expected, actual, POLYBYTES) != 0)
    fail_mismatch(label, trial, expected, actual);
  if (memcmp(source_storage, source_before, sizeof source_storage) != 0) {
    fprintf(stderr, "%s trial=%d changed source\n", label, trial);
    exit(1);
  }
  for (index = 0; index < GUARD + (size_t)unaligned; ++index)
    if (output_storage[index] != 0xa7) {
      fprintf(stderr, "%s trial=%d output prefix canary\n", label, trial);
      exit(1);
    }
  for (index = GUARD + (size_t)unaligned + POLYBYTES;
       index < sizeof output_storage; ++index)
    if (output_storage[index] != 0xa7) {
      fprintf(stderr, "%s trial=%d output suffix canary\n", label, trial);
      exit(1);
    }
}

static void run_caller_case(const char *label, int trial, const poly *input) {
  poly official = *input;
  poly planes;
  poly planes_before;
  uint8_t expected[POLYBYTES];
  uint8_t actual[POLYBYTES];

  poly_ntt(&official);
  poly_tobytes(expected, &official);
  ntruplus1152_exp001_top_split_small(planes.coeffs, input->coeffs);
  ntruplus1152_exp001_gt9x16_prod3_aos_full(planes.coeffs);
  planes_before = planes;
  ntruplus1152_exp001_prod3_ma2_hash_h1(actual, planes.coeffs);
  if (memcmp(&planes, &planes_before, sizeof planes) != 0) {
    fprintf(stderr, "%s trial=%d changed caller planes\n", label, trial);
    exit(1);
  }
  if (memcmp(expected, actual, POLYBYTES) != 0)
    fail_mismatch(label, trial, expected, actual);
}

int main(void) {
  _Alignas(32) int16_t planes[N];
  poly input;
  int index;
  int trial;

  memset(planes, 0, sizeof planes);
  run_plane_case("zero-plane", 0, planes, 0);
  for (index = 0; index < N; ++index) {
    memset(planes, 0, sizeof planes);
    planes[index] = 1;
    run_plane_case("positive-plane-impulse", index, planes, index & 1);
    planes[index] = -1;
    run_plane_case("negative-plane-impulse", index, planes, index & 1);
  }
  for (index = 0; index < N; ++index)
    planes[index] = (int16_t)((index & 1) ? 20753 : -20751);
  run_plane_case("alternating-plane-bound", 0, planes, 1);
  for (trial = 0; trial < RANDOM_PLANE_TRIALS; ++trial) {
    for (index = 0; index < N; ++index)
      planes[index] = (int16_t)((int)(random_u32() % 41505) - 20751);
    run_plane_case("random-plane-range", trial, planes, trial & 1);
  }
  for (trial = -20751; trial <= 20753; ++trial) {
    for (index = 0; index < N; ++index)
      planes[index] = (int16_t)trial;
    run_plane_case("uniform-exhaustive-range", trial, planes, trial & 1);
  }

  memset(&input, 0, sizeof input);
  run_caller_case("caller-zero", 0, &input);
  for (index = 0; index < N; ++index) {
    memset(&input, 0, sizeof input);
    input.coeffs[index] = 1;
    run_caller_case("caller-positive-impulse", index, &input);
    input.coeffs[index] = -1;
    run_caller_case("caller-negative-impulse", index, &input);
  }
  for (index = 0; index < N; ++index)
    input.coeffs[index] = (int16_t)((index & 1) ? 1 : -1);
  run_caller_case("caller-alternating", 0, &input);
  for (trial = 0; trial < RANDOM_CALLER_TRIALS; ++trial) {
    for (index = 0; index < N; ++index)
      input.coeffs[index] = (int16_t)((int)(random_u32() % 3) - 1);
    run_caller_case("caller-random-small", trial, &input);
  }

  puts("H1 ASM0 full MA2 -> 1728-byte raw exact differential passed");
  return 0;
}
