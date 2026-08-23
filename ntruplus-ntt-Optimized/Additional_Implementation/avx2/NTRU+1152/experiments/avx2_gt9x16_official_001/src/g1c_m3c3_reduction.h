#ifndef NTRUPLUS1152_EXP001_G1C_M3C3_REDUCTION_H
#define NTRUPLUS1152_EXP001_G1C_M3C3_REDUCTION_H

#include <stdint.h>

#define NTRUPLUS1152_EXP001_M3C3_VALUES 1152

void ntruplus1152_exp001_g1c_m3c3_reduce_barrett(
    int16_t *output, const int16_t *input);
void ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity(
    int16_t *output, const int16_t *input);

#endif
