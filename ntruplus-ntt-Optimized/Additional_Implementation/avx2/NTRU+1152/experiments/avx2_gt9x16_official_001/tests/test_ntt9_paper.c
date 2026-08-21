#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16_ntt16_asm.h"
#include "gt9x16-ntt9-paper-range.h"
#include "ntt9_reference.h"

#define TRIALS 10003

static uint64_t random_state = UINT64_C(0xf3b1152a5a9c001);

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
  return value < 0 ? (int)(value + 3457) : (int)value;
}

static int centered(int32_t value) {
  int result = canonical(value);
  return result > 1728 ? result - 3457 : result;
}

static void fill_case(ntruplus1152_exp001_gt_persistent_pair *input, int trial) {
  int lane, row, stream;
  for (row = 0; row < 9; ++row) {
    for (stream = 0; stream < 2; ++stream) {
      for (lane = 0; lane < 16; ++lane) {
        int16_t value;
        if (trial == 0)
          value = NTRUPLUS1152_EXP001_PAPER_INPUT_MIN;
        else if (trial == 1)
          value = NTRUPLUS1152_EXP001_PAPER_INPUT_MAX;
        else if (trial == 2)
          value = (int16_t)(((row + lane + stream) & 1) ?
              NTRUPLUS1152_EXP001_PAPER_INPUT_MIN :
              NTRUPLUS1152_EXP001_PAPER_INPUT_MAX);
        else if (trial == 3)
          value = 0;
        else
          value = (int16_t)(NTRUPLUS1152_EXP001_PAPER_INPUT_MIN +
              random_u32() % (NTRUPLUS1152_EXP001_PAPER_INPUT_MAX -
                              NTRUPLUS1152_EXP001_PAPER_INPUT_MIN + 1));
        input->state[row][stream][lane] = value;
      }
    }
  }
}

static void reference_pair(ntruplus1152_exp001_gt_persistent_pair *output,
                           const ntruplus1152_exp001_gt_persistent_pair *input,
                           int r2) {
  int lane, row, stream;
  for (stream = 0; stream < 2; ++stream) {
    ntruplus1152_exp001_gt_rows source, result;
    for (row = 0; row < 9; ++row)
      for (lane = 0; lane < 16; ++lane)
        source.values[row][lane] = input->state[row][stream][lane];
    if (r2)
      ntruplus1152_exp001_ntt9_r2_reference(&result, &source);
    else
      ntruplus1152_exp001_ntt9_r1_reference(&result, &source);
    for (row = 0; row < 9; ++row)
      for (lane = 0; lane < 16; ++lane)
        output->state[row][stream][lane] = result.values[row][lane];
  }
}

static void compare_exact(const char *label, int trial,
                          const ntruplus1152_exp001_gt_persistent_pair *expected,
                          const ntruplus1152_exp001_gt_persistent_pair *actual) {
  int lane, row, stream;
  for (row = 0; row < 9; ++row)
    for (stream = 0; stream < 2; ++stream)
      for (lane = 0; lane < 16; ++lane)
        if (expected->state[row][stream][lane] != actual->state[row][stream][lane]) {
          fprintf(stderr, "%s trial=%d row=%d stream=%d lane=%d expected=%" PRId16
                          " actual=%" PRId16 "\n", label, trial, row, stream, lane,
                  expected->state[row][stream][lane], actual->state[row][stream][lane]);
          exit(1);
        }
}

static uint64_t representative_equal, representative_total;

static void compare_scaled(const char *label, int trial,
                           const ntruplus1152_exp001_gt_persistent_pair *r0,
                           const ntruplus1152_exp001_gt_persistent_pair *paper,
                           int r2) {
  static const int r2_to_r0[9] = {0, 1, 2, 3, 4, 5, 8, 6, 7};
  int lane, row, stream;
  for (row = 0; row < 9; ++row) {
    int source_row = r2 ? r2_to_r0[row] : row;
    for (stream = 0; stream < 2; ++stream) {
      for (lane = 0; lane < 16; ++lane) {
        int expected = 4 * (int32_t)r0->state[source_row][stream][lane];
        int16_t actual = paper->state[row][stream][lane];
        if (canonical(expected) != canonical(actual)) {
          fprintf(stderr, "%s modulo-q mismatch trial=%d row=%d source-row=%d "
                          "stream=%d lane=%d expected=%d actual=%" PRId16 "\n",
                  label, trial, row, source_row, stream, lane, expected, actual);
          exit(1);
        }
        representative_equal += actual == centered(expected);
        ++representative_total;
      }
    }
  }
}

static void check_range(const char *label, int trial,
                        const ntruplus1152_exp001_gt_persistent_pair *value,
                        int minimum, int maximum) {
  int lane, row, stream;
  for (row = 0; row < 9; ++row)
    for (stream = 0; stream < 2; ++stream)
      for (lane = 0; lane < 16; ++lane)
        if (value->state[row][stream][lane] < minimum ||
            value->state[row][stream][lane] > maximum) {
          fprintf(stderr, "%s range failure trial=%d row=%d stream=%d lane=%d "
                          "value=%" PRId16 " allowed=[%d,%d]\n",
                  label, trial, row, stream, lane,
                  value->state[row][stream][lane], minimum, maximum);
          exit(1);
        }
}

static void test_canaries(void) {
  struct guarded {
    uint64_t before[4];
    ntruplus1152_exp001_gt_persistent_pair value;
    uint64_t after[4];
  } output;
  ntruplus1152_exp001_gt_persistent_pair input;
  typedef void (*function)(ntruplus1152_exp001_gt_persistent_pair *,
                           const ntruplus1152_exp001_gt_persistent_pair *);
  const function functions[] = {
      ntruplus1152_exp001_gt9x16_ntt9_r1,
      ntruplus1152_exp001_gt9x16_ntt9_r2_memory,
      ntruplus1152_exp001_gt9x16_ntt9_r2_cached};
  size_t selected;
  int index;
  fill_case(&input, 29);
  for (selected = 0; selected < sizeof functions / sizeof functions[0]; ++selected) {
    for (index = 0; index < 4; ++index) {
      output.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
      output.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
    }
    functions[selected](&output.value, &input);
    for (index = 0; index < 4; ++index)
      if (output.before[index] != (UINT64_C(0x0123456789abcdef) ^ (uint64_t)index) ||
          output.after[index] != (UINT64_C(0xfedcba9876543210) ^ (uint64_t)index)) {
        fprintf(stderr, "paper NTT9 canary failure function=%zu\n", selected);
        exit(1);
      }
  }
}

int main(void) {
  int trial;
  for (trial = 0; trial < TRIALS; ++trial) {
    ntruplus1152_exp001_gt_persistent_pair input, r0, r1, r2_memory, r2_cached;
    ntruplus1152_exp001_gt_persistent_pair expected_r1, expected_r2, alias;
    fill_case(&input, trial);
    reference_pair(&expected_r1, &input, 0);
    reference_pair(&expected_r2, &input, 1);
    ntruplus1152_exp001_gt9x16_ntt9_d_a(&r0, &input);
    ntruplus1152_exp001_gt9x16_ntt9_r1(&r1, &input);
    ntruplus1152_exp001_gt9x16_ntt9_r2_memory(&r2_memory, &input);
    ntruplus1152_exp001_gt9x16_ntt9_r2_cached(&r2_cached, &input);
    compare_exact("R1 schedule", trial, &expected_r1, &r1);
    compare_exact("R2-memory schedule", trial, &expected_r2, &r2_memory);
    compare_exact("R2-cached schedule", trial, &expected_r2, &r2_cached);
    compare_scaled("R1 vs 4*R0", trial, &r0, &r1, 0);
    compare_scaled("R2-memory vs 4*R0", trial, &r0, &r2_memory, 1);
    compare_scaled("R2-cached vs 4*R0", trial, &r0, &r2_cached, 1);
    check_range("R1", trial, &r1,
                NTRUPLUS1152_EXP001_PAPER_R1_FINAL_MIN,
                NTRUPLUS1152_EXP001_PAPER_R1_FINAL_MAX);
    check_range("R2-memory", trial, &r2_memory,
                NTRUPLUS1152_EXP001_PAPER_R2_FINAL_MIN,
                NTRUPLUS1152_EXP001_PAPER_R2_FINAL_MAX);
    check_range("R2-cached", trial, &r2_cached,
                NTRUPLUS1152_EXP001_PAPER_R2_FINAL_MIN,
                NTRUPLUS1152_EXP001_PAPER_R2_FINAL_MAX);
    if (trial < 64) {
      alias = input;
      ntruplus1152_exp001_gt9x16_ntt9_r1(&alias, &alias);
      compare_exact("R1 alias", trial, &expected_r1, &alias);
      alias = input;
      ntruplus1152_exp001_gt9x16_ntt9_r2_memory(&alias, &alias);
      compare_exact("R2-memory alias", trial, &expected_r2, &alias);
      alias = input;
      ntruplus1152_exp001_gt9x16_ntt9_r2_cached(&alias, &alias);
      compare_exact("R2-cached alias", trial, &expected_r2, &alias);
    }
  }
  test_canaries();
  printf("F-R3B R1/R2: %d schedule-exact and modulo-q 4*R0 cases passed; "
         "representative equality diagnostic=%" PRIu64 "/%" PRIu64 "\n",
         TRIALS, representative_equal, representative_total);
  return 0;
}
