#ifndef NTRUPLUS1152_EXP001_GT9X16_PROD3_HASH_FANOUT_H
#define NTRUPLUS1152_EXP001_GT9X16_PROD3_HASH_FANOUT_H

#include <stdint.h>

#include "poly.h"

void ntruplus1152_exp001_hash_fanout_o0(poly *official_state);

void ntruplus1152_exp001_hash_fanout_o1(
    uint8_t hash_bytes[NTRUPLUS_POLYBYTES], poly *official_state);

void ntruplus1152_exp001_hash_fanout_c0(
    int16_t planes[NTRUPLUS_N], const poly *coefficient_input);

void ntruplus1152_exp001_hash_fanout_c1(
    uint8_t hash_bytes[NTRUPLUS_POLYBYTES], int16_t planes[NTRUPLUS_N],
    const poly *coefficient_input, poly *generic_scratch,
    poly *official_scratch);

#endif
