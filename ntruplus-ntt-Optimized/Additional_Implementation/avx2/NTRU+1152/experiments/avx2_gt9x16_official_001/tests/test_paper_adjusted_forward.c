#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16-ntt9-paper-range.h"
#include "gt9x16_ntt16_asm.h"
#include "ntt9_reference.h"

#define TRIALS 10003

static uint64_t random_state = UINT64_C(0xf3c1152a5a9c001);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int canonical(int32_t value) {
  value %= 3457;
  return value < 0 ? value + 3457 : value;
}

static int16_t montgomery_reduce(int32_t value) {
  int16_t low = (int16_t)value * 12929;
  return (int16_t)((value - (int32_t)low * 3457) >> 16);
}

static void fill_case(ntruplus1152_exp001_gt_persistent_pair *input, int trial) {
  int lane, row, stream;
  const int minimum = NTRUPLUS1152_EXP001_PAPER_INPUT_MIN;
  const int maximum = NTRUPLUS1152_EXP001_PAPER_INPUT_MAX;
  for (row = 0; row < 9; ++row)
    for (stream = 0; stream < 2; ++stream)
      for (lane = 0; lane < 16; ++lane) {
        int value;
        if (trial == 0) value = minimum;
        else if (trial == 1) value = maximum;
        else if (trial == 2) value = ((row + stream + lane) & 1) ? minimum : maximum;
        else if (trial == 3) value = 0;
        else value = minimum + (int)(random_u32() % (unsigned)(maximum - minimum + 1));
        input->state[row][stream][lane] = (int16_t)value;
      }
}

static void ntt9_pair(ntruplus1152_exp001_gt_persistent_pair *output,
                      const ntruplus1152_exp001_gt_persistent_pair *input, int r2) {
  int lane, row, stream;
  for (stream = 0; stream < 2; ++stream) {
    ntruplus1152_exp001_gt_rows source, transformed;
    for (row = 0; row < 9; ++row)
      for (lane = 0; lane < 16; ++lane)
        source.values[row][lane] = input->state[row][stream][lane];
    if (r2) ntruplus1152_exp001_ntt9_r2_reference(&transformed, &source);
    else ntruplus1152_exp001_ntt9_reference(&transformed, &source);
    for (row = 0; row < 9; ++row)
      for (lane = 0; lane < 16; ++lane)
        output->state[row][stream][lane] = transformed.values[row][lane];
  }
}

static void adjusted_reference(ntruplus1152_exp001_gt_persistent_pair *output,
                               const ntruplus1152_exp001_gt_persistent_pair *input,
                               const int source_rows[9]) {
  static const int distances[4] = {8, 4, 2, 1};
  int row, stream;
  for (row = 0; row < 9; ++row) {
    int16_t transformed[2][16];
    for (stream = 0; stream < 2; ++stream) {
      int stage;
      memcpy(transformed[stream], input->state[source_rows[row]][stream], 32);
      for (stage = 0; stage < 4; ++stage) {
        const int distance = distances[stage];
        const int16_t *zeta = stage == 0 ? ntruplus1152_exp001_paper_distance8_zeta[row] :
                              stage == 1 ? ntruplus1152_exp001_paper_distance4_zeta[row] :
                              stage == 2 ? ntruplus1152_exp001_paper_distance2_zeta[row] :
                                           ntruplus1152_exp001_paper_distance1_zeta[row];
        int group, lane;
        for (group = 0; group < 16 / (2 * distance); ++group)
          for (lane = 0; lane < distance; ++lane) {
            int left = group * 2 * distance + lane;
            int right = left + distance;
            int16_t a = transformed[stream][left];
            int16_t product = montgomery_reduce((int32_t)transformed[stream][right] * zeta[group]);
            transformed[stream][left] = (int16_t)(a + product);
            transformed[stream][right] = (int16_t)(a - product);
          }
      }
    }
    for (stream = 0; stream < 2; ++stream) {
      int lane;
      for (lane = 0; lane < 8; ++lane) {
        output->state[row][0][stream * 8 + lane] = transformed[stream][2 * lane];
        output->state[row][1][stream * 8 + lane] = transformed[stream][2 * lane + 1];
      }
    }
  }
}

static void compare_exact(const char *label, int trial,
                          const ntruplus1152_exp001_gt_persistent_pair *expected,
                          const ntruplus1152_exp001_gt_persistent_pair *actual) {
  int row, half, lane;
  for (row = 0; row < 9; ++row)
    for (half = 0; half < 2; ++half)
      for (lane = 0; lane < 16; ++lane)
        if (expected->state[row][half][lane] != actual->state[row][half][lane]) {
          fprintf(stderr, "%s trial=%d row=%d half=%d lane=%d expected=%" PRId16
                          " actual=%" PRId16 "\n", label, trial, row, half, lane,
                  expected->state[row][half][lane], actual->state[row][half][lane]);
          exit(1);
        }
}

static void compare_scaled(int trial,
                           const ntruplus1152_exp001_gt_persistent_pair *unscaled,
                           const ntruplus1152_exp001_gt_persistent_pair *scaled) {
  int row, half, lane;
  for (row = 0; row < 9; ++row)
    for (half = 0; half < 2; ++half)
      for (lane = 0; lane < 16; ++lane)
        if (canonical(4 * (int32_t)unscaled->state[row][half][lane]) !=
            canonical(scaled->state[row][half][lane])) {
          fprintf(stderr, "combined-vs-4x-unscaled trial=%d row=%d half=%d lane=%d\n",
                  trial, row, half, lane);
          exit(1);
        }
}

static void test_canary(void) {
  struct guarded { uint64_t before[4]; ntruplus1152_exp001_gt_persistent_pair value; uint64_t after[4]; } output;
  ntruplus1152_exp001_gt_persistent_pair input;
  typedef void (*function)(ntruplus1152_exp001_gt_persistent_pair *,
                           const ntruplus1152_exp001_gt_persistent_pair *);
  const function functions[] = {
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body,
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d0,
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1};
  int index;
  size_t selected;
  fill_case(&input, 19);
  for (selected = 0; selected < sizeof functions / sizeof functions[0]; ++selected) {
    for (index = 0; index < 4; ++index) {
      output.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
      output.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
    }
    functions[selected](&output.value, &input);
    for (index = 0; index < 4; ++index)
      if (output.before[index] != (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
          output.after[index] != (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index)) {
        fprintf(stderr, "F-R3C/D canary corruption function=%zu\n", selected);
        exit(1);
      }
  }
}

int main(void) {
  static const int identity[9] = {0, 1, 2, 3, 4, 5, 6, 7, 8};
  static const int r2_to_r0[9] = {0, 1, 2, 3, 4, 5, 8, 6, 7};
  int trial;
  for (trial = 0; trial < TRIALS; ++trial) {
    ntruplus1152_exp001_gt_persistent_pair input, r0, r2, expected, actual, unscaled, alias;
    fill_case(&input, trial);
    ntt9_pair(&r2, &input, 1);
    adjusted_reference(&expected, &r2, identity);
    ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16(&actual, &r2);
    compare_exact("adjusted-only", trial, &expected, &actual);
    ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d0(&actual, &r2);
    compare_exact("adjusted-d0", trial, &expected, &actual);
    ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d1(&actual, &r2);
    compare_exact("adjusted-d1", trial, &expected, &actual);
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body(&actual, &input);
    compare_exact("combined", trial, &expected, &actual);
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d0(&actual, &input);
    compare_exact("combined-d0", trial, &expected, &actual);
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1(&actual, &input);
    compare_exact("combined-d1", trial, &expected, &actual);
    ntt9_pair(&r0, &input, 0);
    adjusted_reference(&unscaled, &r0, r2_to_r0);
    compare_scaled(trial, &unscaled, &actual);
    if (trial < 64) {
      alias = r2;
      ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16(&alias, &alias);
      compare_exact("adjusted-only-alias", trial, &expected, &alias);
      alias = r2;
      ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d0(&alias, &alias);
      compare_exact("adjusted-d0-alias", trial, &expected, &alias);
      alias = r2;
      ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d1(&alias, &alias);
      compare_exact("adjusted-d1-alias", trial, &expected, &alias);
      alias = input;
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body(&alias, &alias);
      compare_exact("combined-alias", trial, &expected, &alias);
      alias = input;
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d0(&alias, &alias);
      compare_exact("combined-d0-alias", trial, &expected, &alias);
      alias = input;
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1(&alias, &alias);
      compare_exact("combined-d1-alias", trial, &expected, &alias);
    }
  }
  test_canary();
  printf("F-R3C/D0/D1 adjusted NTT16 and combined bodies: %d exact and modulo-q 4x-unscaled cases passed\n", TRIALS);
  return 0;
}
