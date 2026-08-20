#include <string.h>

#include "gt9x16_oracle.h"

void ntruplus1152_exp001_gt9x16_relabel(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *h_rows) {
  ntruplus1152_exp001_gt_rows temporary;
  int row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    memcpy(temporary.values[row], h_rows->values[(5 * row) % 9], sizeof temporary.values[row]);
  }
  memcpy(output, &temporary, sizeof temporary);
}

void ntruplus1152_exp001_gt9x16_oracle_y(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *r_rows) {
  ntruplus1152_exp001_gt_rows temporary;
  int lane, row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < NTRUPLUS1152_EXP001_GT_LANES; ++lane) {
      temporary.values[row][lane] = r_rows->values[(row + lane) % 9][lane];
    }
  }
  memcpy(output, &temporary, sizeof temporary);
}

void ntruplus1152_exp001_gt9x16_oracle_z(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *r_rows) {
  ntruplus1152_exp001_gt_rows y_rows;
  int lane, row;
  ntruplus1152_exp001_gt9x16_oracle_y(&y_rows, r_rows);
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < 8; ++lane) {
      output->values[row][lane] = y_rows.values[row][lane];
      output->values[row][lane + 8] = y_rows.values[(row + 1) % 9][lane + 8];
    }
  }
}

static int16_t montgomery_reduce(int32_t value) {
  int16_t low = (int16_t)value * 12929;
  return (int16_t)((value - (int32_t)low * 3457) >> 16);
}

void ntruplus1152_exp001_gt9x16_oracle_stage8(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *materialized_y,
    const int16_t zeta[9]) {
  int lane, row;
  for (row = 0; row < NTRUPLUS1152_EXP001_GT_ROWS; ++row) {
    for (lane = 0; lane < 8; ++lane) {
      int16_t a = materialized_y->values[row][lane];
      int16_t t = montgomery_reduce((int32_t)materialized_y->values[row][lane + 8] * zeta[row]);
      output->values[row][lane] = (int16_t)(a + t);
      output->values[row][lane + 8] = (int16_t)(a - t);
    }
  }
}

void ntruplus1152_exp001_gt9x16_oracle_ntt16_finish_row(
    int16_t output[16], const int16_t input[16],
    const int16_t zeta4[2], const int16_t zeta2[4], const int16_t zeta1[8]) {
  int16_t values[16];
  int distance, group, lane;
  const int16_t *tables[3] = {zeta4, zeta2, zeta1};
  const int distances[3] = {4, 2, 1};
  memcpy(values, input, sizeof values);
  for (int stage = 0; stage < 3; ++stage) {
    distance = distances[stage];
    for (group = 0; group < 16 / (2 * distance); ++group) {
      int start = group * 2 * distance;
      for (lane = 0; lane < distance; ++lane) {
        int16_t a = values[start + lane];
        int16_t t = montgomery_reduce((int32_t)values[start + distance + lane]
                                      * tables[stage][group]);
        values[start + lane] = (int16_t)(a + t);
        values[start + distance + lane] = (int16_t)(a - t);
      }
    }
  }
  memcpy(output, values, sizeof values);
}
