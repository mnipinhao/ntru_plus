#ifndef NTRUPLUS1152_EXP001_GT9X16_NTT16_ASM_H
#define NTRUPLUS1152_EXP001_GT9X16_NTT16_ASM_H

#include "gt9x16_shear.h"

void ntruplus1152_exp001_gt9x16_ntt16_c0(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input);

/* Diagnostic arithmetic-only replay: loads/stores once around repeat bodies. */
void ntruplus1152_exp001_gt9x16_ntt16_c0_repeat(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input,
    unsigned int repetitions);

void ntruplus1152_exp001_gt9x16_ntt16_c1(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input);

void ntruplus1152_exp001_gt9x16_ntt16_c1_repeat(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input,
    unsigned int repetitions);

typedef struct {
  ntruplus1152_exp001_gt_rows coefficient[2];
} ntruplus1152_exp001_gt_row_pair;

void ntruplus1152_exp001_gt9x16_ntt16_c0_pair(
    ntruplus1152_exp001_gt_row_pair *output,
    const ntruplus1152_exp001_gt_row_pair *input);
void ntruplus1152_exp001_gt9x16_stage8_c0_pair(
    ntruplus1152_exp001_gt_row_pair *output,
    const ntruplus1152_exp001_gt_row_pair *input);
void ntruplus1152_exp001_gt9x16_stage8_c2_pair(
    ntruplus1152_exp001_gt_row_pair *output,
    const ntruplus1152_exp001_gt_row_pair *input);
void ntruplus1152_exp001_gt9x16_ntt16_c2_pair(
    ntruplus1152_exp001_gt_row_pair *output,
    const ntruplus1152_exp001_gt_row_pair *input);

typedef struct {
  int16_t coefficient[2][16];
} ntruplus1152_exp001_gt_ntt16_row_pair;

void ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair(
    ntruplus1152_exp001_gt_ntt16_row_pair *output,
    const ntruplus1152_exp001_gt_ntt16_row_pair *input);
void ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair(
    ntruplus1152_exp001_gt_ntt16_row_pair *output,
    const ntruplus1152_exp001_gt_ntt16_row_pair *input);

typedef struct { int16_t state[9][2][16]; } ntruplus1152_exp001_gt_persistent_pair;
void ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_row_pair *skewed_input);
void ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_row_pair *skewed_input);
void ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_row_pair *input);
void ntruplus1152_exp001_gt9x16_ntt16_c4_probe_row0(
    ntruplus1152_exp001_gt_ntt16_row_pair *output,
    const ntruplus1152_exp001_gt_row_pair *input);
void ntruplus1152_exp001_gt9x16_ntt9_d_a(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_persistent_pair *input);
void ntruplus1152_exp001_gt9x16_ntt9_r1(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_persistent_pair *input);
void ntruplus1152_exp001_gt9x16_ntt9_r2_memory(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_persistent_pair *input);
void ntruplus1152_exp001_gt9x16_ntt9_r2_cached(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_persistent_pair *input);
/* Input is R2 physical-row canonical lanes; output is terminal persistent S/D. */
void ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_persistent_pair *r2_input);
/* Includes the real R2 store -> adjusted-NTT16 reload memory boundary. */
void ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body(
    ntruplus1152_exp001_gt_persistent_pair *output,
    const ntruplus1152_exp001_gt_persistent_pair *input);

#endif
