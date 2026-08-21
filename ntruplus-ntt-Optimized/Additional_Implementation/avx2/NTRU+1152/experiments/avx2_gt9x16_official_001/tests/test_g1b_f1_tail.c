#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16-ntt9-paper-range.h"
#include "gt9x16_ntt16_asm.h"

#define PAIRS 4
#define TRIALS 10003

typedef void (*f1_tail)(ntruplus1152_exp001_gt_persistent_pair *,
                        const ntruplus1152_exp001_gt_persistent_pair *, int16_t *);

static uint64_t random_state = UINT64_C(0x61b1152f1a11ed9);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void fill_case(ntruplus1152_exp001_gt_persistent_pair input[PAIRS], int trial) {
  int lane, pair, row, stream;
  const int minimum = NTRUPLUS1152_EXP001_PAPER_INPUT_MIN;
  const int maximum = NTRUPLUS1152_EXP001_PAPER_INPUT_MAX;
  for (pair = 0; pair < PAIRS; ++pair)
    for (row = 0; row < 9; ++row)
      for (stream = 0; stream < 2; ++stream)
        for (lane = 0; lane < 16; ++lane) {
          int value;
          if (trial == 0) value = minimum;
          else if (trial == 1) value = maximum;
          else if (trial == 2) value = ((pair + row + stream + lane) & 1) ? minimum : maximum;
          else if (trial == 3) value = 0;
          else value = minimum + (int)(random_u32() % (unsigned)(maximum - minimum + 1));
          input[pair].state[row][stream][lane] = (int16_t)value;
        }
}

static void persistent_to_terminal(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_persistent_pair input[PAIRS]) {
  int branch, coefficient, lane, pair, row, terminal_pair;
  for (pair = 0; pair < PAIRS; ++pair) {
    branch = pair / 2;
    terminal_pair = pair % 2;
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 2; ++coefficient)
        for (lane = 0; lane < 16; ++lane)
          output->state[branch][row][2 * terminal_pair + coefficient][lane] =
              input[pair].state[row][lane & 1][coefficient * 8 + lane / 2];
  }
}

static void run_f1(f1_tail function, ntruplus1152_exp001_gt_terminal_major *output,
                   const ntruplus1152_exp001_gt_persistent_pair input[PAIRS]) {
  ntruplus1152_exp001_gt_persistent_pair scratch[PAIRS];
  int pair;
  memset(output, 0x5a, sizeof *output);
  for (pair = 0; pair < PAIRS; ++pair) {
    int branch = pair / 2;
    int terminal_pair = pair % 2;
    function(&scratch[pair], &input[pair],
             &output->state[branch][0][2 * terminal_pair][0]);
  }
}

static void compare(const char *label, int trial,
                    const ntruplus1152_exp001_gt_terminal_major *expected,
                    const ntruplus1152_exp001_gt_terminal_major *actual) {
  int branch, coefficient, lane, row;
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (coefficient = 0; coefficient < 4; ++coefficient)
        for (lane = 0; lane < 16; ++lane)
          if (expected->state[branch][row][coefficient][lane] !=
              actual->state[branch][row][coefficient][lane]) {
            fprintf(stderr, "%s trial=%d b=%d row=%d j=%d lane=%d expected=%" PRId16
                            " actual=%" PRId16 "\n", label, trial, branch, row,
                    coefficient, lane, expected->state[branch][row][coefficient][lane],
                    actual->state[branch][row][coefficient][lane]);
            exit(1);
          }
}

static void test_canary(void) {
  struct guarded {
    uint64_t before[4];
    ntruplus1152_exp001_gt_terminal_major value;
    uint64_t after[4];
  } output;
  ntruplus1152_exp001_gt_persistent_pair input[PAIRS];
  ntruplus1152_exp001_gt_persistent_pair scratch[PAIRS];
  const f1_tail functions[] = {ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b0,
                               ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1};
  size_t selected;
  int index, pair;
  fill_case(input, 19);
  for (selected = 0; selected < sizeof functions / sizeof functions[0]; ++selected) {
    for (index = 0; index < 4; ++index) {
      output.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
      output.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
    }
    for (pair = 0; pair < PAIRS; ++pair) {
      int branch = pair / 2;
      int terminal_pair = pair % 2;
      functions[selected](&scratch[pair], &input[pair],
                          &output.value.state[branch][0][2 * terminal_pair][0]);
    }
    for (index = 0; index < 4; ++index)
      if (output.before[index] != (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
          output.after[index] != (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index)) {
        fprintf(stderr, "G1B canary corruption function=%zu\n", selected);
        exit(1);
      }
  }
}

int main(void) {
  int trial;
  for (trial = 0; trial < TRIALS; ++trial) {
    ntruplus1152_exp001_gt_persistent_pair input[PAIRS], persistent[PAIRS];
    ntruplus1152_exp001_gt_terminal_major expected, b0, b1;
    int pair;
    fill_case(input, trial);
    for (pair = 0; pair < PAIRS; ++pair)
      ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1(&persistent[pair], &input[pair]);
    persistent_to_terminal(&expected, persistent);
    run_f1(ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b0, &b0, input);
    run_f1(ntruplus1152_exp001_gt9x16_r2_adjusted_forward_f1_b1, &b1, input);
    compare("F1-B0", trial, &expected, &b0);
    compare("F1-B1", trial, &expected, &b1);
  }
  test_canary();
  printf("G1B F1-B0/B1: %d cases x 1152 terminal-major cells, scale-4 and canary passed\n",
         TRIALS);
  return 0;
}
