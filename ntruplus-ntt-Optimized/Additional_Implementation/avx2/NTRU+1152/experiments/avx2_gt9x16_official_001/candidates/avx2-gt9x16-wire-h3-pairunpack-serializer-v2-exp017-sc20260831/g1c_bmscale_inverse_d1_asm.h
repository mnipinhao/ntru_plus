#ifndef NTRUPLUS1152_EXP001_G1C_BMSCALE_INVERSE_D1_ASM_H
#define NTRUPLUS1152_EXP001_G1C_BMSCALE_INVERSE_D1_ASM_H

#include "gt9x16_ntt16_asm.h"

void ntruplus1152_exp001_gt9x16_bmscale_raw(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);

/* Exact inlined current-boundary control: raw stores, D1 reloads, post-D1 stores. */
void ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);

void ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);

/*
 * M3 full inverse16 controls. All three include the proved D1-sum identity.
 * Internal KEM ABI: output, a, and b are pairwise non-aliasing.
 */
void ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c0(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);
void ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c1(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);
void ntruplus1152_exp001_gt9x16_bmscale_inverse16_m3_c2(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);

#endif
