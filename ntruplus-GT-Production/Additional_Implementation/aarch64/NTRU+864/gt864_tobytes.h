#ifndef GT864_TOBYTES_H
#define GT864_TOBYTES_H
#include "poly.h"
/* FR0 R0 input, disjoint 1296-byte output. Full accepts all signed int16. */
void gt864_fr0_tobytes_full(uint8_t *out, const poly *in);
/* Requires every coefficient strictly in (-3457,3457). D1 outputs satisfy
 * [-3023,3023]. Never use directly on unrestricted K1 Forward output. */
void gt864_fr0_tobytes_small(uint8_t *out, const poly *in);
#endif
