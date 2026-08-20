#ifndef NTRUPLUS1152_EXP001_NTT9_REFERENCE_H
#define NTRUPLUS1152_EXP001_NTT9_REFERENCE_H

#include "gt9x16_shear.h"

/* Two radix-3 layers; output rows retain two-trit-reversed order. */
void ntruplus1152_exp001_ntt9_reference(
    ntruplus1152_exp001_gt_rows *output,
    const ntruplus1152_exp001_gt_rows *input);

#endif
