#ifndef NTRUPLUS1152_EXP001_INVERSE_NTT9_REFERENCE_H
#define NTRUPLUS1152_EXP001_INVERSE_NTT9_REFERENCE_H

#include "gt9x16_ntt16_asm.h"

typedef struct {
  int16_t state[2][16][4][9];
} ntruplus1152_exp001_inverse9_canonical_p;

/*
 * Correctness-first two-layer inverse of the paper R2 radix-3 schedule.
 * Input rows use paper physical-p order. Output rows are natural time s.
 * Every output is centered modulo q; in-place operation is supported.
 */
void ntruplus1152_exp001_inverse_ntt9_r2_direct(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_gt_terminal_major *input);

/* Full-array canonical control used only to price the representation edge. */
void ntruplus1152_exp001_inverse9_repack_canonical_p(
    ntruplus1152_exp001_inverse9_canonical_p *output,
    const ntruplus1152_exp001_gt_terminal_major *input);
void ntruplus1152_exp001_inverse_ntt9_r2_from_canonical_p(
    ntruplus1152_exp001_gt_terminal_major *output,
    const ntruplus1152_exp001_inverse9_canonical_p *input);

#endif
