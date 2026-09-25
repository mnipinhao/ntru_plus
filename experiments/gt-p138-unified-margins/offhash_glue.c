/* P138: GT's encapsulation-private hash_g_fr0 on top of Official's hash_g,
 * exactly as GT's symmetric.c builds it on its own: serialize, then hash. */
#include <stdint.h>
#include <string.h>
#include "params.h"
void tobytes_full_asm(uint8_t *, const int16_t *);
void hash_g(uint8_t *buf, const uint8_t *msg);
void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N])
{
    uint8_t data[NTRUPLUS_POLYBYTES];
    tobytes_full_asm(data, coeffs);
    hash_g(buf, data);
    memset(data, 0, sizeof data);
}
