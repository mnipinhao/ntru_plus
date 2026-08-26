#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "f0-ma2-asm.h"
#include "f0_forward_for_ma2.h"
#include "f0_generic_to_ma2_planes.h"

#define N 1152
#define CT_BYTES 1728
#define RAW_RANDOM_TRIALS 1003
#define CONSUMER_TRIALS 257
#define GUARD_I16 16
#define GUARD_U8 32

static uint64_t random_state = UINT64_C(0xf0d2a52011520001);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void fail_i16(const char *label, int trial, int index,
                     int16_t expected, int16_t actual) {
  fprintf(stderr,
          "F0-PROD2 %s trial=%d i16=%d expected=%" PRId16
          " actual=%" PRId16 "\n",
          label, trial, index, expected, actual);
  exit(1);
}

static void fail_u8(const char *label, int trial, int index,
                    uint8_t expected, uint8_t actual) {
  fprintf(stderr,
          "F0-PROD2 %s trial=%d byte=%d expected=%u actual=%u\n",
          label, trial, index, (unsigned)expected, (unsigned)actual);
  exit(1);
}

/* Exact P1-H generic physical ABI -> MA2 coefficient-plane physical ABI. */
static void project_generic_to_ma2_oracle(int16_t output[N],
                                          const int16_t generic[N]) {
  int branch, row, coefficient, stream, lane;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient) {
        int pair = coefficient / 2;
        int half = coefficient & 1;
        int row_base = branch * 576 + row * 64;
        for (stream = 0; stream < 2; ++stream)
          for (lane = 0; lane < 8; ++lane)
            output[row_base + coefficient * 16 + stream * 8 + lane] =
                generic[row_base + pair * 32 + stream * 16 + half * 8 + lane];
      }
}

static void compare_i16(const char *label, int trial,
                        const int16_t expected[N], const int16_t actual[N]) {
  int index;
  for (index = 0; index < N; ++index)
    if (expected[index] != actual[index])
      fail_i16(label, trial, index, expected[index], actual[index]);
}

static void compare_u8(const char *label, int trial,
                       const uint8_t expected[CT_BYTES],
                       const uint8_t actual[CT_BYTES]) {
  int index;
  for (index = 0; index < CT_BYTES; ++index)
    if (expected[index] != actual[index])
      fail_u8(label, trial, index, expected[index], actual[index]);
}

static void raw_producer_case(const char *label, int trial,
                              const int16_t source[N]) {
  _Alignas(32) int16_t input[N], saved[N], generic[N], projected[N];
  _Alignas(32) int16_t projected_asm[N], alias[N];
  struct __attribute__((aligned(32))) guarded_output {
    int16_t before[GUARD_I16];
    int16_t value[N];
    int16_t after[GUARD_I16];
  } native;
  int index;

  memcpy(input, source, sizeof input);
  memcpy(saved, source, sizeof saved);
  for (index = 0; index < GUARD_I16; ++index) {
    native.before[index] = (int16_t)(0x1200 + index);
    native.after[index] = (int16_t)(0x2300 + index);
  }
  ntruplus1152_exp001_f0_forward_for_ma2_p1h(generic, input);
  project_generic_to_ma2_oracle(projected, generic);
  ntruplus1152_exp001_f0_generic_to_ma2_planes(projected_asm, generic);
  compare_i16("generic-projection-asm", trial, projected, projected_asm);
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(native.value, input);
  compare_i16(label, trial, projected, native.value);
  compare_i16("input-immutability", trial, saved, input);
  for (index = 0; index < N; ++index)
    if (native.value[index] < -20751 || native.value[index] > 20753)
      fail_i16("exact-range", trial, index, projected[index],
               native.value[index]);
  for (index = 0; index < GUARD_I16; ++index)
    if (native.before[index] != (int16_t)(0x1200 + index) ||
        native.after[index] != (int16_t)(0x2300 + index))
      fail_i16("producer-canary", trial, index, 0, 1);

  memcpy(alias, source, sizeof alias);
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(alias, alias);
  compare_i16("alias", trial, projected, alias);
}

static void fill_small(int16_t output[N], int trial, int salt) {
  int index;
  for (index = 0; index < N; ++index) {
    if (trial == 0)
      output[index] = 0;
    else if (trial == 1)
      output[index] = (int16_t)(((index + salt) & 1) ? -1 : 1);
    else
      output[index] = (int16_t)((int)(random_u32() % 3) - 1);
  }
}

static void consumer_case(int trial) {
  _Alignas(32) int16_t r_input[N], m_input[N], h[N], saved_h[N];
  _Alignas(32) int16_t r_generic[N], m_generic[N];
  _Alignas(32) int16_t r_projected[N], m_projected[N];
  _Alignas(32) int16_t r_native[N], m_native[N];
  struct __attribute__((aligned(32))) guarded_scratch {
    int16_t before[GUARD_I16];
    int16_t value[128];
    int16_t after[GUARD_I16];
  } generic_scratch, native_scratch;
  struct guarded_bytes {
    uint8_t before[GUARD_U8];
    uint8_t value[CT_BYTES];
    uint8_t after[GUARD_U8];
  } generic_ct, native_ct;
  int index;

  fill_small(r_input, trial, 0);
  fill_small(m_input, trial, 1);
  for (index = 0; index < N; ++index)
    h[index] = (int16_t)(random_u32() % 3457U);
  memcpy(saved_h, h, sizeof h);

  ntruplus1152_exp001_f0_forward_for_ma2_p1h(r_generic, r_input);
  ntruplus1152_exp001_f0_forward_for_ma2_p1h(m_generic, m_input);
  ntruplus1152_exp001_f0_generic_to_ma2_planes(r_projected, r_generic);
  ntruplus1152_exp001_f0_generic_to_ma2_planes(m_projected, m_generic);
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(r_native, r_input);
  ntruplus1152_exp001_f0_forward_for_ma2_p2b(m_native, m_input);
  compare_i16("consumer-r-raw-plane", trial, r_projected, r_native);
  compare_i16("consumer-m-raw-plane", trial, m_projected, m_native);

  memset(&generic_scratch, 0x5a, sizeof generic_scratch);
  memset(&native_scratch, 0x6b, sizeof native_scratch);
  memset(&generic_ct, 0xa5, sizeof generic_ct);
  memset(&native_ct, 0xc7, sizeof native_ct);
  for (index = 0; index < GUARD_I16; ++index) {
    generic_scratch.before[index] = native_scratch.before[index] =
        (int16_t)(0x3400 + index);
    generic_scratch.after[index] = native_scratch.after[index] =
        (int16_t)(0x4500 + index);
  }
  for (index = 0; index < GUARD_U8; ++index) {
    generic_ct.before[index] = native_ct.before[index] = (uint8_t)(0x51 + index);
    generic_ct.after[index] = native_ct.after[index] = (uint8_t)(0x91 + index);
  }

  ntruplus1152_exp001_f0_ma2_full(generic_ct.value, r_generic, m_generic, h,
                                   generic_scratch.value);
  ntruplus1152_exp001_f0_ma2_native_full(
      native_ct.value, r_native, m_native, h, native_scratch.value);
  compare_u8("full-ma2-consumer", trial, generic_ct.value, native_ct.value);
  compare_i16("h-immutability", trial, saved_h, h);
  for (index = 0; index < GUARD_I16; ++index)
    if (generic_scratch.before[index] != (int16_t)(0x3400 + index) ||
        native_scratch.before[index] != (int16_t)(0x3400 + index) ||
        generic_scratch.after[index] != (int16_t)(0x4500 + index) ||
        native_scratch.after[index] != (int16_t)(0x4500 + index))
      fail_i16("scratch-canary", trial, index, 0, 1);
  for (index = 0; index < GUARD_U8; ++index)
    if (generic_ct.before[index] != (uint8_t)(0x51 + index) ||
        native_ct.before[index] != (uint8_t)(0x51 + index) ||
        generic_ct.after[index] != (uint8_t)(0x91 + index) ||
        native_ct.after[index] != (uint8_t)(0x91 + index))
      fail_u8("ciphertext-canary", trial, index, 0, 1);
}

int main(void) {
  _Alignas(32) int16_t input[N];
  int index, trial;

  memset(input, 0, sizeof input);
  raw_producer_case("zero-raw-plane", 0, input);
  for (index = 0; index < N; ++index) {
    memset(input, 0, sizeof input);
    input[index] = 1;
    raw_producer_case("positive-impulse-raw-plane", index, input);
    input[index] = -1;
    raw_producer_case("negative-impulse-raw-plane", index, input);
  }
  for (index = 0; index < N; ++index)
    input[index] = (int16_t)((index & 1) ? -1 : 1);
  raw_producer_case("alternating-bound-raw-plane", 0, input);
  for (trial = 0; trial < RAW_RANDOM_TRIALS; ++trial) {
    fill_small(input, trial + 2, 0);
    raw_producer_case("random-raw-plane", trial, input);
  }
  for (trial = 0; trial < CONSUMER_TRIALS; ++trial)
    consumer_case(trial);

  printf("F0-PROD2 P2-B ASM0: raw 2304-byte exact differential for 2304 "
         "impulses, %d random/boundary/alias cases; %d full MA2 byte-exact "
         "consumer cases passed\n", RAW_RANDOM_TRIALS, CONSUMER_TRIALS);
  return 0;
}
