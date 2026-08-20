#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16_forward.h"

extern void poly_ntt(int16_t value[NTRUPLUS1152_EXP001_N]);

static uint64_t random_state = UINT64_C(0x1152f0119a16cafe);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int16_t canonical(int16_t value) {
  int32_t result = value % 3457;
  if (result < 0) {
    result += 3457;
  }
  return (int16_t)result;
}

static void fill_case(int16_t input[NTRUPLUS1152_EXP001_N], int trial) {
  int index;
  for (index = 0; index < NTRUPLUS1152_EXP001_N; ++index) {
    if (trial == 0) {
      input[index] = 0;
    } else if (trial == 10) {
      input[index] = (index & 1) ? -3 : 4;
    } else if (trial >= 1 && trial < 10) {
      input[index] = index == trial - 1 ? 1 : 0;
    } else {
      input[index] = (int16_t)((int)(random_u32() % 8) - 3);
    }
  }
}

static void compare_forward(const int16_t expected[NTRUPLUS1152_EXP001_N],
                            const int16_t actual[NTRUPLUS1152_EXP001_N],
                            int trial, const char *label) {
  int index;
  for (index = 0; index < NTRUPLUS1152_EXP001_N; ++index) {
    int16_t left = canonical(expected[index]);
    int16_t right = canonical(actual[index]);
    if (left != right) {
      fprintf(stderr,
              "%s trial=%d coefficient=%d official=%" PRId16
              " candidate=%" PRId16 " official_raw=%" PRId16
              " candidate_raw=%" PRId16 "\n",
              label, trial, index, left, right, expected[index], actual[index]);
      exit(1);
    }
  }
}

static void test_top_split(void) {
  _Alignas(32) int16_t input[NTRUPLUS1152_EXP001_N];
  _Alignas(32) int16_t output[NTRUPLUS1152_EXP001_N];
  _Alignas(32) int16_t alias[NTRUPLUS1152_EXP001_N];
  int index;
  fill_case(input, 10);
  ntruplus1152_exp001_top_split_small(output, input);
  for (index = 0; index < 576; ++index) {
    int16_t product = (int16_t)(-722 * input[index + 576]);
    int16_t first = (int16_t)(input[index] + product);
    int16_t second = (int16_t)(input[index] + input[index + 576] - product);
    if (output[index] != first || output[index + 576] != second) {
      fputs("top-split arithmetic mismatch\n", stderr);
      exit(1);
    }
  }
  memcpy(alias, input, sizeof alias);
  ntruplus1152_exp001_top_split_small(alias, alias);
  if (memcmp(alias, output, sizeof alias) != 0) {
    fputs("top-split alias mismatch\n", stderr);
    exit(1);
  }
}

static void test_canary(void) {
  struct guarded {
    uint64_t before[4];
    _Alignas(32) int16_t value[NTRUPLUS1152_EXP001_N];
    uint64_t after[4];
  } output;
  _Alignas(32) int16_t input[NTRUPLUS1152_EXP001_N];
  uint64_t before[4], after[4];
  int index;
  fill_case(input, 17);
  for (index = 0; index < 4; ++index) {
    output.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
    output.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
  }
  memcpy(before, output.before, sizeof before);
  memcpy(after, output.after, sizeof after);
  ntruplus1152_exp001_gt9x16_forward_small(output.value, input);
  if (memcmp(before, output.before, sizeof before) != 0 ||
      memcmp(after, output.after, sizeof after) != 0) {
    fputs("full-forward output canary corruption\n", stderr);
    exit(1);
  }
}

int main(void) {
  _Alignas(32) int16_t input[NTRUPLUS1152_EXP001_N];
  _Alignas(32) int16_t official[NTRUPLUS1152_EXP001_N];
  _Alignas(32) int16_t candidate[NTRUPLUS1152_EXP001_N];
  _Alignas(32) int16_t alias[NTRUPLUS1152_EXP001_N];
  int trial;
  test_top_split();
  for (trial = 0; trial < 1010; ++trial) {
    fill_case(input, trial);
    memcpy(official, input, sizeof official);
    poly_ntt(official);
    ntruplus1152_exp001_gt9x16_forward_small(candidate, input);
    compare_forward(official, candidate, trial, "full-forward");
    if (trial < 20) {
      memcpy(alias, input, sizeof alias);
      ntruplus1152_exp001_gt9x16_forward_small(alias, alias);
      compare_forward(official, alias, trial, "full-forward-alias");
    }
  }
  test_canary();
  puts("full forward: 1010 official differentials plus alias/canary passed");
  return 0;
}
