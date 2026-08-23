#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>

#include "g1c_m3_producer_common.h"

#define NODE_COUNT (2 * 9 * 4 * 8)
#define ACTION_COUNT 4

struct node_range {
  int64_t maximum_abs_input[2];
  int64_t maximum_abs_centered[2];
  int64_t maximum_abs_sum_or_difference[ACTION_COUNT];
  uint64_t unsafe_count[ACTION_COUNT];
};

static int node_index(int branch, int row, int coefficient, int pair) {
  return (((branch * 9 + row) * 4 + coefficient) * 8 + pair);
}

static void decode_node(int index, int *branch, int *row, int *coefficient,
                        int *pair) {
  *pair = index % 8;
  index /= 8;
  *coefficient = index % 4;
  index /= 4;
  *row = index % 9;
  *branch = index / 9;
}

static void observe_action(struct node_range *node, int action, int16_t left,
                           int16_t right) {
  int32_t sum = (int32_t)left + right;
  int32_t difference = (int32_t)left - right;
  int64_t maximum = g1c_m3_absolute64(sum);
  if (g1c_m3_absolute64(difference) > maximum)
    maximum = g1c_m3_absolute64(difference);
  if (maximum > node->maximum_abs_sum_or_difference[action])
    node->maximum_abs_sum_or_difference[action] = maximum;
  if (sum < -32768 || sum > 32767 || difference < -32768 ||
      difference > 32767)
    ++node->unsafe_count[action];
}

int main(void) {
  g1c_m3_terminal_major a __attribute__((aligned(32)));
  g1c_m3_terminal_major b __attribute__((aligned(32)));
  struct node_range nodes[NODE_COUNT] = {0};
  uint64_t pre_d8_failures = 0;
  int trial;

  for (trial = 0; trial < G1C_M3_TRIALS; ++trial) {
    g1c_m3_terminal_major state __attribute__((aligned(32)));
    int branch, coefficient, pair, row;
    g1c_m3_fill_case(&a, &b, trial);
    g1c_m3_compute_bmscale(&state, &a, &b);
    if (!g1c_m3_propagate_stage(&state, 0) ||
        !g1c_m3_propagate_stage(&state, 1) ||
        !g1c_m3_propagate_stage(&state, 2)) {
      ++pre_d8_failures;
      continue;
    }
    for (branch = 0; branch < 2; ++branch)
      for (row = 0; row < 9; ++row)
        for (coefficient = 0; coefficient < 4; ++coefficient)
          for (pair = 0; pair < 8; ++pair) {
            int index = node_index(branch, row, coefficient, pair);
            int16_t left = state.state[branch][row][coefficient][pair];
            int16_t right = state.state[branch][row][coefficient][pair + 8];
            int16_t reduced_left = g1c_m3_centered_reduce(left);
            int16_t reduced_right = g1c_m3_centered_reduce(right);
            if (g1c_m3_absolute64(left) > nodes[index].maximum_abs_input[0])
              nodes[index].maximum_abs_input[0] = g1c_m3_absolute64(left);
            if (g1c_m3_absolute64(right) > nodes[index].maximum_abs_input[1])
              nodes[index].maximum_abs_input[1] = g1c_m3_absolute64(right);
            if (g1c_m3_absolute64(reduced_left) >
                nodes[index].maximum_abs_centered[0])
              nodes[index].maximum_abs_centered[0] =
                  g1c_m3_absolute64(reduced_left);
            if (g1c_m3_absolute64(reduced_right) >
                nodes[index].maximum_abs_centered[1])
              nodes[index].maximum_abs_centered[1] =
                  g1c_m3_absolute64(reduced_right);
            observe_action(&nodes[index], 0, left, right);
            observe_action(&nodes[index], 1, reduced_left, right);
            observe_action(&nodes[index], 2, left, reduced_right);
            observe_action(&nodes[index], 3, reduced_left, reduced_right);
          }
  }

  printf("{\"trials\":%d,\"pre_d8_failures\":%" PRIu64
         ",\"actions\":[\"none\",\"reduce_left\",\"reduce_right\","
         "\"reduce_both\"],\"nodes\":[",
         G1C_M3_TRIALS, pre_d8_failures);
  for (trial = 0; trial < NODE_COUNT; ++trial) {
    int action, branch, coefficient, pair, row;
    decode_node(trial, &branch, &row, &coefficient, &pair);
    if (trial) putchar(',');
    printf("{\"branch\":%d,\"row\":%d,\"coefficient\":%d,\"pair\":%d,"
           "\"physical_lanes\":[%d,%d],\"maximum_abs_input\":[%" PRId64
           ",%" PRId64 "],\"maximum_abs_centered\":[%" PRId64 ",%" PRId64
           "],\"maximum_abs_sum_or_difference\":[",
           branch, row, coefficient, pair, pair, pair + 8,
           nodes[trial].maximum_abs_input[0], nodes[trial].maximum_abs_input[1],
           nodes[trial].maximum_abs_centered[0],
           nodes[trial].maximum_abs_centered[1]);
    for (action = 0; action < ACTION_COUNT; ++action) {
      if (action) putchar(',');
      printf("%" PRId64, nodes[trial].maximum_abs_sum_or_difference[action]);
    }
    printf("],\"unsafe_count\":[");
    for (action = 0; action < ACTION_COUNT; ++action) {
      if (action) putchar(',');
      printf("%" PRIu64, nodes[trial].unsafe_count[action]);
    }
    printf("]}");
  }
  printf("],\"proof_status\":\"fixed-corpus-candidate-selection-not-exact-proof\"}\n");
  return pre_d8_failures == 0 ? 0 : 1;
}
