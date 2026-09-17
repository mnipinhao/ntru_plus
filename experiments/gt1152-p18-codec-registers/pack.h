#ifndef NTRUPLUS1152_HARNESS_PACK_H
#define NTRUPLUS1152_HARNESS_PACK_H
#include <stdint.h>
#define NTRUPLUS1152_N 1152
#define NTRUPLUS1152_POLYBYTES 1728
/* Good-Thomas layout input, disjoint 1728-byte output. Full accepts all signed int16. */
void poly_tobytes(uint8_t out[NTRUPLUS1152_POLYBYTES], const int16_t in[NTRUPLUS1152_N]);
/* Requires every coefficient strictly in (-3457,3457). Never on raw Forward output. */
void poly_tobytes_small(uint8_t out[NTRUPLUS1152_POLYBYTES], const int16_t in[NTRUPLUS1152_N]);
/* Returns 0 iff the Full serialization equals expected. Constant time. */
int poly_tobytes_compare(const uint8_t expected[NTRUPLUS1152_POLYBYTES],
                         const int16_t in[NTRUPLUS1152_N]);
/* Decode without reduction. 0 iff every value < q. Output written either way. */
int poly_frombytes(int16_t out[NTRUPLUS1152_N], const uint8_t in[NTRUPLUS1152_POLYBYTES]);
#endif
