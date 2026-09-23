#ifndef NTRUPLUS1152_EXP001_F0_PROD3_HASH_BRIDGE_H
#define NTRUPLUS1152_EXP001_F0_PROD3_HASH_BRIDGE_H

#include <stdint.h>

#include "poly.h"

void ntruplus1152_exp001_f0_ma2_planes_to_generic(
    int16_t output_generic[NTRUPLUS_N],
    const int16_t input_planes[NTRUPLUS_N]);

void ntruplus1152_exp001_prod3_hash_bytes(
    uint8_t output[NTRUPLUS_POLYBYTES],
    const int16_t input_planes[NTRUPLUS_N], poly *generic_scratch,
    poly *official_scratch);

#endif
