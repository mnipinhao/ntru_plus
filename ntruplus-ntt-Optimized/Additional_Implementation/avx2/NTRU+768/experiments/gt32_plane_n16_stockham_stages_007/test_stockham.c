#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "generated/plane_n16_probe.h"

#define Q 3457
#define N 32

static int modq(int64_t value) {
  value %= Q;
  if (value < 0) value += Q;
  return (int)value;
}

static int omega32(void) {
  int64_t base = 675;
  int exponent = 3;
  int result = 1;
  while (exponent) {
    if (exponent & 1) result = modq(result * base);
    base = modq(base * base);
    exponent >>= 1;
  }
  return result;
}

static int power(int base, int exponent) {
  int result = 1;
  while (exponent) {
    if (exponent & 1) result = modq((int64_t)result * base);
    base = modq((int64_t)base * base);
    exponent >>= 1;
  }
  return result;
}

static int forward_power(int stage, int group) {
  /* Same CT edge rule as generate_tile4.forward_power(). */
  int index = group >> (6 - stage);
  int bits = stage - 1;
  int reversed = 0;
  for (int i = 0; i < bits; ++i)
    reversed |= ((index >> i) & 1) << (bits - 1 - i);
  return reversed << (5 - stage);
}

static void reference(int out[4][32], const int in[4][32]) {
  memcpy(out, in, sizeof(int) * 4 * 32);
  int root = omega32();
  for (int stage = 2; stage <= 5; ++stage) {
    int distance = N >> stage;
    for (int group = 0; group < N; group += 2 * distance) {
      int factor = power(root, forward_power(stage, group));
      for (int lane = 0; lane < distance; ++lane) {
        int low = group + lane;
        int high = low + distance;
        for (int degree = 0; degree < 4; ++degree) {
          int left = out[degree][low];
          int right = modq((int64_t)factor * out[degree][high]);
          out[degree][low] = modq(left + right);
          out[degree][high] = modq(left - right);
        }
      }
    }
  }
}

typedef void (*kernel)(int16_t *, const int16_t *);

static int check_one(kernel fn, const uint8_t start_map[128],
                     const uint8_t terminal_map[128], uint32_t *seed) {
  _Alignas(32) int16_t input[128], output[128], alias[128];
  int semantic[4][32], expected[4][32];
  memset(input, 0, sizeof(input));
  for (int degree = 0; degree < 4; ++degree) {
    for (int q = 0; q < 32; ++q) {
      *seed = *seed * 1664525u + 1013904223u;
      semantic[degree][q] = (int)(*seed % Q);
      int index = degree | (q << 2);
      input[start_map[index]] = (int16_t)semantic[degree][q];
    }
  }
  reference(expected, semantic);
  fn(output, input);
  memcpy(alias, input, sizeof(input));
  fn(alias, alias);
  if (memcmp(output, alias, sizeof(output)) != 0) return 1;
  for (int degree = 0; degree < 4; ++degree)
    for (int q = 0; q < 32; ++q) {
      int index = degree | (q << 2);
      int got = modq(output[terminal_map[index]]);
      if (got != expected[degree][q]) {
        fprintf(stderr, "mismatch degree=%d q=%d got=%d expected=%d physical=%u\n",
                degree, q, got, expected[degree][q], terminal_map[index]);
        return 1;
      }
    }
  return 0;
}

int main(void) {
  kernel functions[] = {
    gt32_plane_n16_folded_asm,
    gt32_plane_n16_reuse_one_asm,
    gt32_plane_n16_reuse_pair_asm,
    gt32_plane_n16_progressive_control_asm,
    gt32_plane_n16_pair_control_asm,
  };
  uint32_t seed = 1;
  for (int trial = 0; trial < 1000; ++trial)
    for (unsigned i = 0; i < sizeof(functions) / sizeof(functions[0]); ++i)
      if (check_one(functions[i],
                    i == 3 ? progressive_start_semantic_to_physical
                           : i == 4 ? pair_start_semantic_to_physical
                                    : start_semantic_to_physical,
                    i == 3 ? progressive_terminal_semantic_to_physical
                           : i == 4 ? pair_terminal_semantic_to_physical
                                    : terminal_semantic_to_physical,
                    &seed)) {
        fprintf(stderr, "trial %d function %u failed\n", trial, i);
        return 1;
      }
  puts("1000-trial N16 and alias differential: ok");
  return 0;
}
