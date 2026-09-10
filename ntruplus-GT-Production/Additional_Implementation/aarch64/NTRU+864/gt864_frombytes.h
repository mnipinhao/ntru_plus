#ifndef GT864_FROMBYTES_H
#define GT864_FROMBYTES_H
#include "poly.h"
/* Decode FR0 without reduction. Return 0 iff all 864 values are < q,
 * otherwise 1. Output on failure remains decoded and must not be consumed. */
int gt864_fr0_frombytes_checked(poly *out,const uint8_t in[NTRUPLUS_POLYBYTES]);
#endif
