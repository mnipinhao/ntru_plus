#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gt9x16_oracle.h"
#include "gt9x16_shear.h"
#include "gt9x16-stage8-tables.h"

static uint64_t random_state = UINT64_C(0x9161152c0decafe);

static uint32_t random_u32(void) {
  uint64_t value = random_state;
  value ^= value << 13;
  value ^= value >> 7;
  value ^= value << 17;
  random_state = value;
  return (uint32_t)(value >> 16);
}

static void fail_at(const char *label, int trial, int row, int lane,
                    int16_t expected, int16_t actual) {
  fprintf(stderr,
          "%s trial=%d row=%d lane=%d expected=%" PRId16 " actual=%" PRId16 "\n",
          label, trial, row, lane, expected, actual);
  exit(1);
}

static void compare_rows(const char *label, int trial,
                         const ntruplus1152_exp001_gt_rows expected,
                         const ntruplus1152_exp001_gt_rows actual) {
  int lane, row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < NTRUPLUS1152_EXP001_GT_LANES; ++lane) {
      if (expected.values[row][lane] != actual.values[row][lane]) {
        fail_at(label, trial, row, lane, expected.values[row][lane], actual.values[row][lane]);
      }
    }
  }
}

static void fill_case(ntruplus1152_exp001_gt_rows *rows, int trial) {
  static const int16_t boundaries[] = {
      INT16_MIN, INT16_MIN + 1, -1728, -1, 0, 1, 1728, INT16_MAX - 1, INT16_MAX};
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

static void test_one(int trial) {
  ntruplus1152_exp001_gt_rows input, expected_y, expected_z, expected_stage8;
  ntruplus1152_exp001_gt_rows expected_ntt16, actual_ntt16, actual, alias;
  int branch, row;
  fill_case(&input, trial);
  ntruplus1152_exp001_gt9x16_oracle_y(&expected_y, &input);
  ntruplus1152_exp001_gt9x16_oracle_z(&expected_z, &input);

  ntruplus1152_exp001_gt9x16_shear_z(&actual, &input);
  compare_rows("shear-z", trial, expected_z, actual);
  ntruplus1152_exp001_gt9x16_shear_materialized(&actual, &input);
  compare_rows("materialized", trial, expected_y, actual);
  for (branch = 0; branch < 2; ++branch) {
    ntruplus1152_exp001_gt9x16_oracle_stage8(
        &expected_stage8, &expected_y, ntruplus1152_exp001_stage8_zeta[branch]);
    ntruplus1152_exp001_gt9x16_shear_stage8(
        &actual, &input, ntruplus1152_exp001_stage8_zeta[branch],
        ntruplus1152_exp001_stage8_qinv[branch]);
    compare_rows("fused-stage8", trial, expected_stage8, actual);
    for (row = 0; row < 9; ++row) {
      int16_t row_alias[16];
      ntruplus1152_exp001_ntt16_row_tables tables = {
          ntruplus1152_exp001_stage4_zeta[branch][row],
          ntruplus1152_exp001_stage4_qinv[branch][row],
          ntruplus1152_exp001_stage2_zeta[branch][row],
          ntruplus1152_exp001_stage2_qinv[branch][row],
          ntruplus1152_exp001_stage1_zeta[branch][row],
          ntruplus1152_exp001_stage1_qinv[branch][row]};
      ntruplus1152_exp001_gt9x16_oracle_ntt16_finish_row(
          expected_ntt16.values[row], expected_stage8.values[row],
          ntruplus1152_exp001_stage4_zeta[branch][row],
          ntruplus1152_exp001_stage2_zeta[branch][row],
          ntruplus1152_exp001_stage1_zeta[branch][row]);
      ntruplus1152_exp001_gt9x16_ntt16_finish_row(
          actual_ntt16.values[row], actual.values[row], &tables);
      memcpy(row_alias, actual.values[row], sizeof row_alias);
      ntruplus1152_exp001_gt9x16_ntt16_finish_row(row_alias, row_alias, &tables);
      if (memcmp(row_alias, expected_ntt16.values[row], sizeof row_alias) != 0) {
        fputs("ntt16 row alias mismatch\n", stderr);
        exit(1);
      }
    }
    compare_rows("ntt16-full", trial, expected_ntt16, actual_ntt16);
    memcpy(&alias, &input, sizeof alias);
    ntruplus1152_exp001_gt9x16_shear_stage8(
        &alias, &alias, ntruplus1152_exp001_stage8_zeta[branch],
        ntruplus1152_exp001_stage8_qinv[branch]);
    compare_rows("fused-stage8-alias", trial, expected_stage8, alias);
  }

  memcpy(&alias, &input, sizeof alias);
  ntruplus1152_exp001_gt9x16_shear_z(&alias, &alias);
  compare_rows("shear-z-alias", trial, expected_z, alias);
  memcpy(&alias, &input, sizeof alias);
  ntruplus1152_exp001_gt9x16_shear_materialized(&alias, &alias);
  compare_rows("materialized-alias", trial, expected_y, alias);
}

static void test_canaries(void) {
  struct guarded_rows {
    uint64_t before[4];
    ntruplus1152_exp001_gt_rows rows;
    uint64_t after[4];
  } guarded;
  ntruplus1152_exp001_gt_rows input;
  uint64_t expected_before[4], expected_after[4];
  int index;
  fill_case(&input, 17);
  for (index = 0; index < 4; ++index) {
    guarded.before[index] = UINT64_C(0x0123456789abcdef) ^ (uint64_t)index;
    guarded.after[index] = UINT64_C(0xfedcba9876543210) ^ (uint64_t)index;
  }
  memcpy(expected_before, guarded.before, sizeof expected_before);
  memcpy(expected_after, guarded.after, sizeof expected_after);
  ntruplus1152_exp001_gt9x16_shear_materialized(&guarded.rows, &input);
  if (memcmp(expected_before, guarded.before, sizeof expected_before) != 0 ||
      memcmp(expected_after, guarded.after, sizeof expected_after) != 0) {
    fputs("output canary corruption\n", stderr);
    exit(1);
  }
  ntruplus1152_exp001_gt9x16_shear_stage8(
      &guarded.rows, &input, ntruplus1152_exp001_stage8_zeta[0],
      ntruplus1152_exp001_stage8_qinv[0]);
  if (memcmp(expected_before, guarded.before, sizeof expected_before) != 0 ||
      memcmp(expected_after, guarded.after, sizeof expected_after) != 0) {
    fputs("stage8 output canary corruption\n", stderr);
    exit(1);
  }
}

int main(void) {
  int trial;
  for (trial = 0; trial < 10003; ++trial) {
    test_one(trial);
  }
  test_canaries();
  puts("gt9x16 shear/NTT16: 10003 cases, alias, and canary checks passed");
  return 0;
}
