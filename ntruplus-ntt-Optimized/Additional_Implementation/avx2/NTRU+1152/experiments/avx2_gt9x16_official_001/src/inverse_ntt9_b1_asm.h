#ifndef NTRUPLUS1152_EXP001_INVERSE_NTT9_B1_ASM_H
#define NTRUPLUS1152_EXP001_INVERSE_NTT9_B1_ASM_H

#include "gt9x16_ntt16_asm.h"

/* ITAIL-ASM-B1: B0 arithmetic with only B1R-authorized reducers removed. */
void ntruplus1152_exp001_inverse_ntt9_b1(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *input);

#endif
