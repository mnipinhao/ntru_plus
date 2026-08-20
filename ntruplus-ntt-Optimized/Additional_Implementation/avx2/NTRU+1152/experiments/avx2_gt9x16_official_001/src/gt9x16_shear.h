#ifndef NTRUPLUS1152_EXP001_GT9X16_SHEAR_H
#define NTRUPLUS1152_EXP001_GT9X16_SHEAR_H

#include <stdint.h>

#define NTRUPLUS1152_EXP001_GT_ROWS 9
#define NTRUPLUS1152_EXP001_GT_LANES 16

typedef struct {
  int16_t values[NTRUPLUS1152_EXP001_GT_ROWS][NTRUPLUS1152_EXP001_GT_LANES];
} ntruplus1152_exp001_gt_rows;

typedef struct {
  const int16_t *zeta4;
  const int16_t *qinv4;
  const int16_t *zeta2;
  const int16_t *qinv2;
  const int16_t *zeta1;
  const int16_t *qinv1;
} ntruplus1152_exp001_ntt16_row_tables;

/* Produce Z[a] = Y[a].low || Y[(a+1)%9].high using 27 vpblendw. */
void ntruplus1152_exp001_gt9x16_shear_z(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input);

/* Debug baseline: materialize Y with 27 vpblendw plus 9 vperm2i128. */
void ntruplus1152_exp001_gt9x16_shear_materialized(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input);

/* Validation candidate: 27-blend shear feeding distance-8 without Y storage. */
void ntruplus1152_exp001_gt9x16_shear_stage8(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input,
    const int16_t zeta[9],
    const int16_t zeta_qinv[9]);

/* Complete distances 4,2,1 for one materialized stage-8 row. */
void ntruplus1152_exp001_gt9x16_ntt16_finish_row(
    int16_t output[16],
    const int16_t input[16],
    const ntruplus1152_exp001_ntt16_row_tables *tables);

#endif
