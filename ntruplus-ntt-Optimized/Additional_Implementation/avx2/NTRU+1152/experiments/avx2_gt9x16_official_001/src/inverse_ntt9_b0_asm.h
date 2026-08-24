#ifndef NTRUPLUS1152_EXP001_INVERSE_NTT9_B0_ASM_H
#define NTRUPLUS1152_EXP001_INVERSE_NTT9_B0_ASM_H

#include "gt9x16_ntt16_asm.h"

typedef struct {
  int16_t state[2][9][4][16];
} ntruplus1152_exp001_inverse9_vector_canonical_p;

/* ITAIL-ASM-B0: B physical-P input, natural-s centered output. */
void ntruplus1152_exp001_inverse_ntt9_b0(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *input);

/* Optimized A control: materialize natural P, then use the same B0 core. */
void ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p(
    ntruplus1152_exp001_inverse9_vector_canonical_p *output,
    const ntruplus1152_exp001_gt_terminal_major *input);
void ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_inverse9_vector_canonical_p *input);

#endif
