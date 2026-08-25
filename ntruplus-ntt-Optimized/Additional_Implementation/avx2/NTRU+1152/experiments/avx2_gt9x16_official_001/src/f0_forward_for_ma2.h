#ifndef NTRUPLUS1152_EXP001_F0_FORWARD_FOR_MA2_H
#define NTRUPLUS1152_EXP001_F0_FORWARD_FOR_MA2_H

#include <stdint.h>

#define NTRUPLUS1152_EXP001_F0_N 1152

/*
 * Coefficient-domain KEM-small input to the exact materialized F0 ABI used by
 * MA2.  The actual encapsulation callers provide 32-byte-aligned arrays with
 * coefficients in [-1,1].  In-place operation is supported.
 */
void ntruplus1152_exp001_f0_forward_for_ma2(
    int16_t output[NTRUPLUS1152_EXP001_F0_N],
    const int16_t input[NTRUPLUS1152_EXP001_F0_N]);

#endif
