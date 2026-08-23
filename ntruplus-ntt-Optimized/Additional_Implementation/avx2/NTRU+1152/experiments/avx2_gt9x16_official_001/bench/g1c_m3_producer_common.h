#ifndef NTRUPLUS1152_EXP001_G1C_M3_PRODUCER_COMMON_H
#define NTRUPLUS1152_EXP001_G1C_M3_PRODUCER_COMMON_H

#include <stdint.h>

#include "g1c-bmscale-live-tail.h"
#include "g1c-m3-inverse16.h"
#include "gt9x16-ntt9-paper-range.h"
#include "gt9x16_ntt16_asm.h"

#define G1C_M3_Q 3457
#define G1C_M3_QINV 12929
#define G1C_M3_R_MOD_Q 3310
#define G1C_M3_TRIALS 10003

typedef ntruplus1152_exp001_gt_terminal_major g1c_m3_terminal_major;

static uint64_t g1c_m3_random_state = UINT64_C(0x1152c3b5eed19a51);

static uint32_t g1c_m3_random_u32(void) {
  uint64_t value = g1c_m3_random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  g1c_m3_random_state = value;
  return (uint32_t)(value >> 16);
}

static int16_t g1c_m3_wrap16(int64_t value) {
  uint16_t reduced = (uint16_t)value;
  return reduced < UINT16_C(0x8000) ? (int16_t)reduced
                                    : (int16_t)((int32_t)reduced - 65536);
}

static int16_t g1c_m3_high16(int16_t left, int16_t right) {
  int32_t product = (int32_t)left * (int32_t)right;
  int32_t quotient = product / 65536;
  if (product < 0 && product % 65536 != 0) --quotient;
  return (int16_t)quotient;
}

static int16_t g1c_m3_montgomery_mul(int16_t left, int16_t right) {
  int16_t low_qinv = g1c_m3_wrap16((int32_t)left * G1C_M3_QINV);
  int16_t low_product = g1c_m3_wrap16((int32_t)low_qinv * right);
  return g1c_m3_wrap16((int32_t)g1c_m3_high16(left, right) -
                       g1c_m3_high16(low_product, G1C_M3_Q));
}

static int16_t g1c_m3_add16(int16_t left, int16_t right) {
  return g1c_m3_wrap16((int32_t)left + right);
}

static int16_t g1c_m3_centered_factor(int factor) {
  int value = (factor * G1C_M3_R_MOD_Q) % G1C_M3_Q;
  if (value > G1C_M3_Q / 2) value -= G1C_M3_Q;
  return (int16_t)value;
}

static int16_t g1c_m3_centered_reduce(int16_t input) {
  int value = input % G1C_M3_Q;
  if (value > G1C_M3_Q / 2) value -= G1C_M3_Q;
  if (value < -G1C_M3_Q / 2) value += G1C_M3_Q;
  return (int16_t)value;
}

static int64_t g1c_m3_absolute64(int64_t value) {
  return value < 0 ? -value : value;
}

static void g1c_m3_scalar_bmscale_vector(int16_t output[4],
                                         const int16_t a[4],
                                         const int16_t b[4], int16_t factor) {
  int16_t p13 = g1c_m3_montgomery_mul(a[1], b[3]);
  int16_t p31 = g1c_m3_montgomery_mul(a[3], b[1]);
  int16_t p33 = g1c_m3_montgomery_mul(a[3], b[3]);
  int16_t p22 = g1c_m3_montgomery_mul(a[2], b[2]);
  int16_t p23 = g1c_m3_montgomery_mul(a[2], b[3]);
  int16_t p32 = g1c_m3_montgomery_mul(a[3], b[2]);
  int16_t c0_high = g1c_m3_add16(g1c_m3_add16(p13, p31), p22);
  int16_t c1_high = g1c_m3_add16(p23, p32);
  int16_t c0 = g1c_m3_montgomery_mul(c0_high, factor);
  int16_t c1 = g1c_m3_montgomery_mul(c1_high, factor);
  int16_t c2 = g1c_m3_montgomery_mul(p33, factor);

  c0 = g1c_m3_add16(c0, g1c_m3_montgomery_mul(a[0], b[0]));
  c2 = g1c_m3_add16(c2, g1c_m3_montgomery_mul(a[0], b[2]));
  c2 = g1c_m3_add16(c2, g1c_m3_montgomery_mul(a[2], b[0]));
  c1 = g1c_m3_add16(c1, g1c_m3_montgomery_mul(a[0], b[1]));
  c1 = g1c_m3_add16(c1, g1c_m3_montgomery_mul(a[1], b[0]));
  c2 = g1c_m3_add16(c2, g1c_m3_montgomery_mul(a[1], b[1]));
  output[0] = c0;
  output[1] = c1;
  output[2] = c2;
  output[3] = g1c_m3_add16(
      g1c_m3_add16(g1c_m3_montgomery_mul(a[0], b[3]),
                   g1c_m3_montgomery_mul(a[1], b[2])),
      g1c_m3_add16(g1c_m3_montgomery_mul(a[2], b[1]),
                   g1c_m3_montgomery_mul(a[3], b[0])));
}

static void g1c_m3_fill_producer_input(
    ntruplus1152_exp001_gt_persistent_pair input[4], int trial, int salt) {
  const int minimum = NTRUPLUS1152_EXP001_PAPER_INPUT_MIN;
  const int maximum = NTRUPLUS1152_EXP001_PAPER_INPUT_MAX;
  int lane, pair, row, stream;
  for (pair = 0; pair < 4; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          int value;
          if (trial == 0)
            value = 0;
          else if (trial == 1)
            value = minimum;
          else if (trial == 2)
            value = maximum;
          else if (trial == 3)
            value = ((salt + pair + row + stream + lane) & 1) ? minimum
                                                               : maximum;
          else if (trial == 4)
            value = ((lane / 2 + salt + row) & 1) ? minimum : maximum;
          else
            value = minimum +
                    (int)(g1c_m3_random_u32() %
                          (unsigned)(maximum - minimum + 1));
          input[pair].state[row][stream][lane] = (int16_t)value;
        }
}

static void g1c_m3_run_producer(
    g1c_m3_terminal_major *output,
    const ntruplus1152_exp001_gt_persistent_pair input[4]) {
  ntruplus1152_exp001_gt_persistent_pair scratch[4];
  int pair;
  for (pair = 0; pair < 4; ++pair) {
    int branch = pair / 2;
    int terminal_pair = pair % 2;
    ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1(
        &scratch[pair], &input[pair],
        &output->state[branch][0][2 * terminal_pair][0]);
  }
}

static void g1c_m3_fill_case(g1c_m3_terminal_major *a,
                             g1c_m3_terminal_major *b, int trial) {
  ntruplus1152_exp001_gt_persistent_pair input_a[4]
      __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_persistent_pair input_b[4]
      __attribute__((aligned(32)));
  g1c_m3_fill_producer_input(input_a, trial, 0);
  g1c_m3_fill_producer_input(input_b, trial, 1);
  g1c_m3_run_producer(a, input_a);
  g1c_m3_run_producer(b, input_b);
}

static void g1c_m3_compute_bmscale(g1c_m3_terminal_major *state,
                                   const g1c_m3_terminal_major *a,
                                   const g1c_m3_terminal_major *b) {
  int branch, coefficient, lane, row;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (lane = 0; lane < 16; ++lane) {
        int16_t av[4], bv[4], cv[4];
        int16_t factor = g1c_m3_centered_factor(
            ntruplus1152_exp001_g1c_bmscale_factor_mod_q[branch][row][lane]);
        for (coefficient = 0; coefficient < 4; ++coefficient) {
          av[coefficient] = a->state[branch][row][coefficient][lane];
          bv[coefficient] = b->state[branch][row][coefficient][lane];
        }
        g1c_m3_scalar_bmscale_vector(cv, av, bv, factor);
        for (coefficient = 0; coefficient < 4; ++coefficient)
          state->state[branch][row][coefficient][lane] = cv[coefficient];
      }
}

static int g1c_m3_propagate_stage(g1c_m3_terminal_major *state,
                                  int stage_index) {
  int branch, coefficient, row;
  int distance = ntruplus1152_exp001_g1c_m3_distances[stage_index];
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient) {
        int block, pair_index = 0;
        for (block = 0; block < 16; block += 2 * distance) {
          int within;
          for (within = 0; within < distance; ++within, ++pair_index) {
            int left_lane = block + within;
            int right_lane = left_lane + distance;
            int16_t left = state->state[branch][row][coefficient][left_lane];
            int16_t right = state->state[branch][row][coefficient][right_lane];
            int32_t sum = (int32_t)left + right;
            int32_t difference = (int32_t)left - right;
            if (sum < -32768 || sum > 32767 || difference < -32768 ||
                difference > 32767)
              return 0;
            state->state[branch][row][coefficient][left_lane] = (int16_t)sum;
            state->state[branch][row][coefficient][right_lane] =
                g1c_m3_montgomery_mul(
                    (int16_t)difference,
                    ntruplus1152_exp001_g1c_m3_inverse_mont[row][stage_index]
                                                                  [pair_index]);
          }
        }
      }
  return 1;
}

#endif
