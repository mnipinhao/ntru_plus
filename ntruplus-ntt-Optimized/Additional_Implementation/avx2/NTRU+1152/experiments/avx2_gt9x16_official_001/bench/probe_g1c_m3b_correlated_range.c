#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

#include "g1c-bmscale-live-tail.h"
#include "g1c-m3-inverse16.h"
#include "gt9x16-ntt9-paper-range.h"
#include "gt9x16_ntt16_asm.h"

#define Q 3457
#define QINV 12929
#define R_MOD_Q 3310
#define TRIALS 10003

typedef ntruplus1152_exp001_gt_terminal_major terminal_major;

struct stage_range {
  int64_t maximum_input;
  int64_t maximum_sum;
  int64_t maximum_difference;
  int64_t maximum_twisted;
  uint64_t unsafe_sum_count;
  uint64_t unsafe_difference_count;
};

struct first_unsafe {
  int found, trial, branch, row, coefficient, stage, left_lane, right_lane;
  int32_t left, right, value;
  const char *operation;
};

static uint64_t random_state = UINT64_C(0x1152c3b5eed19a51);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static int16_t wrap16(int64_t value) {
  uint16_t reduced = (uint16_t)value;
  return reduced < UINT16_C(0x8000) ? (int16_t)reduced
                                    : (int16_t)((int32_t)reduced - 65536);
}

static int16_t high16(int16_t left, int16_t right) {
  int32_t product = (int32_t)left * (int32_t)right;
  int32_t quotient = product / 65536;
  if (product < 0 && product % 65536 != 0) --quotient;
  return (int16_t)quotient;
}

static int16_t montgomery_mul(int16_t left, int16_t right) {
  int16_t low_qinv = wrap16((int32_t)left * QINV);
  int16_t low_product = wrap16((int32_t)low_qinv * right);
  return wrap16((int32_t)high16(left, right) - high16(low_product, Q));
}

static int16_t add16(int16_t left, int16_t right) {
  return wrap16((int32_t)left + right);
}

static int16_t centered_factor(int factor) {
  int value = (factor * R_MOD_Q) % Q;
  if (value > Q / 2) value -= Q;
  return (int16_t)value;
}

static int64_t absolute64(int64_t value) { return value < 0 ? -value : value; }

static void scalar_bmscale_vector(int16_t output[4], const int16_t a[4],
                                  const int16_t b[4], int16_t factor) {
  int16_t p13 = montgomery_mul(a[1], b[3]);
  int16_t p31 = montgomery_mul(a[3], b[1]);
  int16_t p33 = montgomery_mul(a[3], b[3]);
  int16_t p22 = montgomery_mul(a[2], b[2]);
  int16_t p23 = montgomery_mul(a[2], b[3]);
  int16_t p32 = montgomery_mul(a[3], b[2]);
  int16_t c0_high = add16(add16(p13, p31), p22);
  int16_t c1_high = add16(p23, p32);
  int16_t c0 = montgomery_mul(c0_high, factor);
  int16_t c1 = montgomery_mul(c1_high, factor);
  int16_t c2 = montgomery_mul(p33, factor);

  c0 = add16(c0, montgomery_mul(a[0], b[0]));
  c2 = add16(c2, montgomery_mul(a[0], b[2]));
  c2 = add16(c2, montgomery_mul(a[2], b[0]));
  c1 = add16(c1, montgomery_mul(a[0], b[1]));
  c1 = add16(c1, montgomery_mul(a[1], b[0]));
  c2 = add16(c2, montgomery_mul(a[1], b[1]));
  output[0] = c0;
  output[1] = c1;
  output[2] = c2;
  output[3] = add16(add16(montgomery_mul(a[0], b[3]),
                          montgomery_mul(a[1], b[2])),
                    add16(montgomery_mul(a[2], b[1]),
                          montgomery_mul(a[3], b[0])));
}

static void fill_producer_input(ntruplus1152_exp001_gt_persistent_pair input[4],
                                int trial, int salt) {
  const int minimum = NTRUPLUS1152_EXP001_PAPER_INPUT_MIN;
  const int maximum = NTRUPLUS1152_EXP001_PAPER_INPUT_MAX;
  int lane, pair, row, stream;
  for (pair = 0; pair < 4; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          int value;
          if (trial == 0) value = 0;
          else if (trial == 1) value = minimum;
          else if (trial == 2) value = maximum;
          else if (trial == 3)
            value = ((salt + pair + row + stream + lane) & 1) ? minimum : maximum;
          else if (trial == 4)
            value = ((lane / 2 + salt + row) & 1) ? minimum : maximum;
          else
            value = minimum + (int)(random_u32() % (unsigned)(maximum - minimum + 1));
          input[pair].state[row][stream][lane] = (int16_t)value;
        }
}

static void run_producer(terminal_major *output,
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

static void fill_case(terminal_major *a, terminal_major *b, int trial) {
  ntruplus1152_exp001_gt_persistent_pair input_a[4] __attribute__((aligned(32)));
  ntruplus1152_exp001_gt_persistent_pair input_b[4] __attribute__((aligned(32)));
  fill_producer_input(input_a, trial, 0);
  fill_producer_input(input_b, trial, 1);
  run_producer(a, input_a);
  run_producer(b, input_b);
}

static void remember_unsafe(struct first_unsafe *first, int trial, int branch,
                            int row, int coefficient, int stage, int left_lane,
                            int right_lane, int32_t left, int32_t right,
                            int32_t value, const char *operation) {
  if (first->found) return;
  first->found = 1;
  first->trial = trial;
  first->branch = branch;
  first->row = row;
  first->coefficient = coefficient;
  first->stage = stage;
  first->left_lane = left_lane;
  first->right_lane = right_lane;
  first->left = left;
  first->right = right;
  first->value = value;
  first->operation = operation;
}

int main(void) {
  terminal_major a __attribute__((aligned(32)));
  terminal_major b __attribute__((aligned(32)));
  struct stage_range ranges[4] = {{0}};
  struct first_unsafe first = {0};
  int64_t maximum_raw = 0;
  int trial;

  for (trial = 0; trial < TRIALS; ++trial) {
    int branch, coefficient, lane, row, stage_index;
    terminal_major state __attribute__((aligned(32)));
    fill_case(&a, &b, trial);
    for (branch = 0; branch < 2; ++branch)
      for (row = 0; row < 9; ++row)
        for (lane = 0; lane < 16; ++lane) {
          int16_t av[4], bv[4], cv[4];
          int16_t factor = centered_factor(
              ntruplus1152_exp001_g1c_bmscale_factor_mod_q[branch][row][lane]);
          for (coefficient = 0; coefficient < 4; ++coefficient) {
            av[coefficient] = a.state[branch][row][coefficient][lane];
            bv[coefficient] = b.state[branch][row][coefficient][lane];
          }
          scalar_bmscale_vector(cv, av, bv, factor);
          for (coefficient = 0; coefficient < 4; ++coefficient) {
            state.state[branch][row][coefficient][lane] = cv[coefficient];
            if (absolute64(cv[coefficient]) > maximum_raw)
              maximum_raw = absolute64(cv[coefficient]);
          }
        }

    for (stage_index = 0; stage_index < 4; ++stage_index) {
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
                int16_t left = state.state[branch][row][coefficient][left_lane];
                int16_t right = state.state[branch][row][coefficient][right_lane];
                int32_t sum = (int32_t)left + right;
                int32_t difference = (int32_t)left - right;
                int16_t twisted = montgomery_mul(
                    wrap16(difference),
                    ntruplus1152_exp001_g1c_m3_inverse_mont[row][stage_index][pair_index]);
                if (absolute64(left) > ranges[stage_index].maximum_input)
                  ranges[stage_index].maximum_input = absolute64(left);
                if (absolute64(right) > ranges[stage_index].maximum_input)
                  ranges[stage_index].maximum_input = absolute64(right);
                if (absolute64(sum) > ranges[stage_index].maximum_sum)
                  ranges[stage_index].maximum_sum = absolute64(sum);
                if (absolute64(difference) > ranges[stage_index].maximum_difference)
                  ranges[stage_index].maximum_difference = absolute64(difference);
                if (absolute64(twisted) > ranges[stage_index].maximum_twisted)
                  ranges[stage_index].maximum_twisted = absolute64(twisted);
                if (sum < -32768 || sum > 32767) {
                  ++ranges[stage_index].unsafe_sum_count;
                  remember_unsafe(&first, trial, branch, row, coefficient,
                                  distance, left_lane, right_lane, left, right,
                                  sum, "sum");
                }
                if (difference < -32768 || difference > 32767) {
                  ++ranges[stage_index].unsafe_difference_count;
                  remember_unsafe(&first, trial, branch, row, coefficient,
                                  distance, left_lane, right_lane, left, right,
                                  difference, "difference");
                }
                state.state[branch][row][coefficient][left_lane] = wrap16(sum);
                state.state[branch][row][coefficient][right_lane] = twisted;
              }
            }
          }
    }
  }

  printf("{\"trials\":%d,\"cells_per_trial\":1152,\"maximum_raw\":%" PRId64
         ",\"stages\":[", TRIALS, maximum_raw);
  for (trial = 0; trial < 4; ++trial) {
    if (trial) putchar(',');
    printf("{\"distance\":%d,\"maximum_input\":%" PRId64
           ",\"maximum_sum\":%" PRId64 ",\"maximum_difference\":%" PRId64
           ",\"maximum_twisted\":%" PRId64 ",\"unsafe_sum_count\":%" PRIu64
           ",\"unsafe_difference_count\":%" PRIu64 "}",
           ntruplus1152_exp001_g1c_m3_distances[trial],
           ranges[trial].maximum_input, ranges[trial].maximum_sum,
           ranges[trial].maximum_difference, ranges[trial].maximum_twisted,
           ranges[trial].unsafe_sum_count, ranges[trial].unsafe_difference_count);
  }
  printf("],\"first_unsafe\":");
  if (!first.found) {
    printf("null");
  } else {
    printf("{\"trial\":%d,\"branch\":%d,\"row\":%d,\"coefficient\":%d,"
           "\"distance\":%d,\"physical_lanes\":[%d,%d],\"left\":%d,"
           "\"right\":%d,\"operation\":\"%s\",\"value\":%d}",
           first.trial, first.branch, first.row, first.coefficient, first.stage,
           first.left_lane, first.right_lane, first.left, first.right,
           first.operation, first.value);
  }
  printf(",\"proof_status\":\"empirical-counterexample-search-not-a-proof-of-safety\"}\n");
  return 0;
}
