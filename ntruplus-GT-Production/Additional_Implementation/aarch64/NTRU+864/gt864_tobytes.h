#ifndef GT864_TOBYTES_H
#define GT864_TOBYTES_H
#include "poly.h"
/* FR0 R0 input, disjoint 1296-byte output. Full accepts all signed int16. */
void gt864_fr0_tobytes_full(uint8_t *out, const poly *in);
/* Decaps-private consumer: returns 0 iff Full serialization equals expected. */
int gt864_fr0_tobytes_full_compare(const uint8_t expected[1296], const poly *in);
/* Both operands use the identical FR0 coordinate order and R0 scale. */
int gt864_fr0_equal_modq_asm(const int16_t regenerated[864],
                             const int16_t recovered[864]);
/* Requires every coefficient strictly in (-3457,3457). D1 outputs satisfy
 * [-3023,3023]. Never use directly on unrestricted K1 Forward output. */
void gt864_fr0_tobytes_small(uint8_t *out, const poly *in);
#endif
