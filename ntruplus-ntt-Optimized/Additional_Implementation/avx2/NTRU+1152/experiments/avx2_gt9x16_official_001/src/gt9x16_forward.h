#ifndef NTRUPLUS1152_EXP001_GT9X16_FORWARD_H
#define NTRUPLUS1152_EXP001_GT9X16_FORWARD_H

#include <stdint.h>

#include "gt9x16_shear.h"

#define NTRUPLUS1152_EXP001_N 1152

/* Bit-exact copy of the existing AVX2 small-input top-split arithmetic. */
void ntruplus1152_exp001_top_split_small(
    int16_t output[NTRUPLUS1152_EXP001_N],
    const int16_t input[NTRUPLUS1152_EXP001_N]);

/* Explicit gather/relabel/pre-twist adapter; top-split arithmetic is not here. */
void ntruplus1152_exp001_top_split_to_gt_adapter(
    ntruplus1152_exp001_gt_rows *output,
    const int16_t split[NTRUPLUS1152_EXP001_N], int branch, int coefficient);

/* Correctness-first full forward, scattered back into Official output order. */
void ntruplus1152_exp001_gt9x16_forward_small(
    int16_t output[NTRUPLUS1152_EXP001_N],
    const int16_t input[NTRUPLUS1152_EXP001_N]);

#endif
