#ifndef NTRUPLUS1152_EXP001_GT9X16_ORACLE_H
#define NTRUPLUS1152_EXP001_GT9X16_ORACLE_H

#include "gt9x16_shear.h"

void ntruplus1152_exp001_gt9x16_relabel(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *h_rows);
void ntruplus1152_exp001_gt9x16_oracle_y(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *r_rows);
void ntruplus1152_exp001_gt9x16_oracle_z(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *r_rows);
void ntruplus1152_exp001_gt9x16_oracle_stage8(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *materialized_y,
    const int16_t zeta[9]);
void ntruplus1152_exp001_gt9x16_oracle_ntt16_finish_row(
    int16_t output[16], const int16_t input[16],
    const int16_t zeta4[2], const int16_t zeta2[4], const int16_t zeta1[8]);

#endif
