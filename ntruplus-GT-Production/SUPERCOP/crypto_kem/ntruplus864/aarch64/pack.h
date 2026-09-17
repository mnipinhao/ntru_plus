#ifndef NTRUPLUS_PACK_H
#define NTRUPLUS_PACK_H
#include "poly.h"
/* FR0 R0 input, disjoint 1296-byte output. Full accepts all signed int16. */
void poly_tobytes(uint8_t *out, const poly *in);
/* Decaps-private consumer: returns 0 iff Full serialization equals expected. */
int poly_tobytes_compare(const uint8_t expected[1296], const poly *in);
/* Requires every coefficient strictly in (-3457,3457). D1 outputs satisfy
 * [-3023,3023]. Never use directly on unrestricted K1 Forward output. */
void poly_tobytes_small(uint8_t *out, const poly *in);
#endif
