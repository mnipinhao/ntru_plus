#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16-full-forward-tables.h"
#include "gt9x16_ntt16_asm.h"
#include "gt9x16_shear.h"

#define TRIALS 10003

static uint64_t random_state = UINT64_C(0xc01151152a5a5a5a);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void fill_case(ntruplus1152_exp001_gt_rows *rows, int trial) {
  static const int16_t boundaries[] = {
      INT16_MIN, INT16_MIN + 1, -3457, -1728, -1,
      0, 1, 1728, 3457, INT16_MAX - 1, INT16_MAX};
  int lane, row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < NTRUPLUS1152_EXP001_GT_LANES; ++lane) {
      if (trial == 0) {
        rows->values[row][lane] = (int16_t)(row * 16 + lane);
      } else if (trial == 1) {
        rows->values[row][lane] = boundaries[(row + lane) %
            (int)(sizeof boundaries / sizeof boundaries[0])];
      } else if (trial == 2) {
        rows->values[row][lane] = (int16_t)(((row + lane) & 1) ? INT16_MIN : INT16_MAX);
      } else {
        rows->values[row][lane] = (int16_t)random_u32();
      }
    }
  }
}

static void reference_ntt16(ntruplus1152_exp001_gt_rows *output,
                            const ntruplus1152_exp001_gt_rows *input) {
  const int16_t zeta8[9] = {-147, -147, -147, -147, -147, -147, -147, -147, -147};
  const int16_t qinv8[9] = {-19, -19, -19, -19, -19, -19, -19, -19, -19};
  const ntruplus1152_exp001_ntt16_row_tables tables = {
      ntruplus1152_exp001_gt_stage4_zeta,
      ntruplus1152_exp001_gt_stage4_qinv,
      ntruplus1152_exp001_gt_stage2_zeta,
      ntruplus1152_exp001_gt_stage2_qinv,
      ntruplus1152_exp001_gt_stage1_zeta,
      ntruplus1152_exp001_gt_stage1_qinv};
  ntruplus1152_exp001_gt_rows stage8;
  int row;
  ntruplus1152_exp001_gt9x16_shear_stage8(&stage8, input, zeta8, qinv8);
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    ntruplus1152_exp001_gt9x16_ntt16_finish_row(
        output->values[row], stage8.values[row], &tables);
  }
}

static void compare(const char *label, int trial,
                    const ntruplus1152_exp001_gt_rows *expected,
                    const ntruplus1152_exp001_gt_rows *actual) {
  int lane, row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < NTRUPLUS1152_EXP001_GT_LANES; ++lane) {
      if (expected->values[row][lane] != actual->values[row][lane]) {
        fprintf(stderr, "%s trial=%d row=%d lane=%d expected=%" PRId16
                        " actual=%" PRId16 "\n",
                label, trial, row, lane, expected->values[row][lane],
                actual->values[row][lane]);
        exit(1);
      }
    }
  }
}

static void test_trial(int trial) {
  ntruplus1152_exp001_gt_rows input, expected, actual, alias, repeated;
  unsigned int repetition;
  fill_case(&input, trial);
  reference_ntt16(&expected, &input);
  ntruplus1152_exp001_gt9x16_ntt16_c0(&actual, &input);
  compare("c0", trial, &expected, &actual);
  ntruplus1152_exp001_gt9x16_ntt16_c1(&actual, &input);
  compare("c1", trial, &expected, &actual);

  memcpy(&alias, &input, sizeof alias);
  ntruplus1152_exp001_gt9x16_ntt16_c0(&alias, &alias);
  compare("c0-alias", trial, &expected, &alias);
  memcpy(&alias, &input, sizeof alias);
  ntruplus1152_exp001_gt9x16_ntt16_c1(&alias, &alias);
  compare("c1-alias", trial, &expected, &alias);

  if (trial < 64) {
    repeated = input;
    for (repetition = 0; repetition < 3; ++repetition) {
      reference_ntt16(&alias, &repeated);
      repeated = alias;
    }
    ntruplus1152_exp001_gt9x16_ntt16_c0_repeat(&actual, &input, 3);
    compare("c0-repeat3", trial, &repeated, &actual);
    ntruplus1152_exp001_gt9x16_ntt16_c0_repeat(&actual, &input, 0);
    compare("c0-repeat0", trial, &input, &actual);
    ntruplus1152_exp001_gt9x16_ntt16_c1_repeat(&actual, &input, 3);
    compare("c1-repeat3", trial, &repeated, &actual);
    ntruplus1152_exp001_gt9x16_ntt16_c1_repeat(&actual, &input, 0);
    compare("c1-repeat0", trial, &input, &actual);
  }
}

static void test_pair(int trial) {
  ntruplus1152_exp001_gt_row_pair input, expected, actual, skewed, stage8_expected;
  int coefficient;
  fill_case(&input.coefficient[0], trial);
  fill_case(&input.coefficient[1], trial + 10007);
  for (coefficient = 0; coefficient < 2; ++coefficient) {
    ntruplus1152_exp001_gt9x16_ntt16_c0(
        &expected.coefficient[coefficient], &input.coefficient[coefficient]);
    ntruplus1152_exp001_gt9x16_shear_z(
        &skewed.coefficient[coefficient], &input.coefficient[coefficient]);
  }
  ntruplus1152_exp001_gt9x16_ntt16_c0_pair(&actual, &input);
  compare("c0-pair-0", trial, &expected.coefficient[0], &actual.coefficient[0]);
  compare("c0-pair-1", trial, &expected.coefficient[1], &actual.coefficient[1]);
  ntruplus1152_exp001_gt9x16_stage8_c0_pair(&stage8_expected, &skewed);
  ntruplus1152_exp001_gt9x16_stage8_c2_pair(&actual, &skewed);
  compare("c2-stage8-0", trial, &stage8_expected.coefficient[0], &actual.coefficient[0]);
  compare("c2-stage8-1", trial, &stage8_expected.coefficient[1], &actual.coefficient[1]);
  ntruplus1152_exp001_gt9x16_ntt16_c2_pair(&actual, &input);
  compare("c2-pair-0", trial, &expected.coefficient[0], &actual.coefficient[0]);
  compare("c2-pair-1", trial, &expected.coefficient[1], &actual.coefficient[1]);

  if (trial < 64) {
    actual = input;
    ntruplus1152_exp001_gt9x16_ntt16_c2_pair(&actual, &actual);
    compare("c2-pair-alias-0", trial, &expected.coefficient[0], &actual.coefficient[0]);
    compare("c2-pair-alias-1", trial, &expected.coefficient[1], &actual.coefficient[1]);
    actual = skewed;
    ntruplus1152_exp001_gt9x16_stage8_c2_pair(&actual, &actual);
    compare("c2-stage8-alias-0", trial, &stage8_expected.coefficient[0], &actual.coefficient[0]);
    compare("c2-stage8-alias-1", trial, &stage8_expected.coefficient[1], &actual.coefficient[1]);
  }
}

static void test_canaries(void) {
  struct guarded {
    uint64_t before[4];
    ntruplus1152_exp001_gt_rows rows;
    uint64_t after[4];
  } output;
  ntruplus1152_exp001_gt_rows input;
  uint64_t before[4], after[4];
  int index;
  fill_case(&input, 91);
  for (index = 0; index < 4; ++index) {
    output.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
    output.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
  }
  memcpy(before, output.before, sizeof before);
  memcpy(after, output.after, sizeof after);
  ntruplus1152_exp001_gt9x16_ntt16_c0(&output.rows, &input);
  if (memcmp(before, output.before, sizeof before) != 0 ||
      memcmp(after, output.after, sizeof after) != 0) {
    fputs("c0 output canary corruption\n", stderr);
    exit(1);
  }
  ntruplus1152_exp001_gt9x16_ntt16_c1(&output.rows, &input);
  if (memcmp(before, output.before, sizeof before) != 0 ||
      memcmp(after, output.after, sizeof after) != 0) {
    fputs("c1 output canary corruption\n", stderr);
    exit(1);
  }
}

int main(void) {
  int trial;
  for (trial = 0; trial < TRIALS; ++trial) {
    test_trial(trial);
    test_pair(trial);
  }
  test_canaries();
  puts("GT9x16 NTT16 C0/C1/C2: 10003 bit-exact, alias, repeat, and canary cases passed");
  return 0;
}
