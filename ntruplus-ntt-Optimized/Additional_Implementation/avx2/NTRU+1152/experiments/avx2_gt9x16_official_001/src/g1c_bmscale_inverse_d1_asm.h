#ifndef NTRUPLUS1152_EXP001_G1C_BMSCALE_INVERSE_D1_ASM_H
#define NTRUPLUS1152_EXP001_G1C_BMSCALE_INVERSE_D1_ASM_H

#include "gt9x16_ntt16_asm.h"

void ntruplus1152_exp001_gt9x16_bmscale_raw(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);

void ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *a,
    const ntruplus1152_exp001_gt_terminal_major *b);

#endif
