#include <string.h>

#include "gt9x16_forward.h"
#include "ntt9_reference.h"
#include "gt9x16-full-forward-tables.h"

static void ntt16_all_rows(ntruplus1152_exp001_gt_rows *output,
                           const ntruplus1152_exp001_gt_rows *input) {
  static const int16_t stage8[9] = {-147, -147, -147, -147, -147, -147, -147, -147, -147};
  static const int16_t stage8_qinv[9] = {-19, -19, -19, -19, -19, -19, -19, -19, -19};
  ntruplus1152_exp001_gt_rows first;
  int row;
  const ntruplus1152_exp001_ntt16_row_tables tables = {
      ntruplus1152_exp001_gt_stage4_zeta,
      ntruplus1152_exp001_gt_stage4_qinv,
      ntruplus1152_exp001_gt_stage2_zeta,
      ntruplus1152_exp001_gt_stage2_qinv,
      ntruplus1152_exp001_gt_stage1_zeta,
      ntruplus1152_exp001_gt_stage1_qinv};
  ntruplus1152_exp001_gt9x16_shear_stage8(
      &first, input, stage8, stage8_qinv);
  for (row = 0; row < 9; ++row) {
    ntruplus1152_exp001_gt9x16_ntt16_finish_row(
        output->values[row], first.values[row], &tables);
  }
}

void ntruplus1152_exp001_gt9x16_forward_small(
    int16_t output[NTRUPLUS1152_EXP001_N],
    const int16_t input[NTRUPLUS1152_EXP001_N]) {
  int16_t split[NTRUPLUS1152_EXP001_N];
  int16_t result[NTRUPLUS1152_EXP001_N];
  int branch, coefficient, lane, row;
  ntruplus1152_exp001_top_split_small(split, input);
  for (branch = 0; branch < 2; ++branch) {
    const int16_t *position_map = branch == 0
        ? ntruplus1152_exp001_official_avx2_position_branch0
        : ntruplus1152_exp001_official_avx2_position_branch1;
    for (coefficient = 0; coefficient < 4; ++coefficient) {
      ntruplus1152_exp001_gt_rows adapted, ntt16, ntt9;
      ntruplus1152_exp001_top_split_to_gt_adapter(
          &adapted, split, branch, coefficient);
      ntt16_all_rows(&ntt16, &adapted);
      ntruplus1152_exp001_ntt9_reference(&ntt9, &ntt16);
      for (row = 0; row < 9; ++row) {
        for (lane = 0; lane < 16; ++lane) {
          int private_component = 16 * row + lane;
          int official_position = position_map[4 * private_component + coefficient];
          result[official_position] =
              ntt9.values[row][lane];
        }
      }
    }
  }
  memcpy(output, result, sizeof result);
}
