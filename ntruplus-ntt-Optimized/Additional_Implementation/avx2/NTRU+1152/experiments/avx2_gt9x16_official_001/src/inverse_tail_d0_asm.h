#ifndef NTRUPLUS1152_EXP001_INVERSE_TAIL_D0_ASM_H
#define NTRUPLUS1152_EXP001_INVERSE_TAIL_D0_ASM_H

#include "gt9x16_ntt16_asm.h"

/* Input is the repaired-D1 materialized state; output is centered natural P. */
void ntruplus1152_exp001_inverse_tail_d0_m0(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *repaired_d1);
void ntruplus1152_exp001_inverse_tail_d0_m1(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *repaired_d1);

#endif
