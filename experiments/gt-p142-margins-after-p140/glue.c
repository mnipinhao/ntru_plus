/* P142: what GT's kem.c needs from its hash layer, on top of Official's (GitHub main's CE sponge):
 * hash_g_fr0 (864/1152) as serialize + Official hash_g, and shake256_x2 as two Official shake256
 * calls -- GT's arithmetic and KEM flow with Official's sponge, no two-state permutation. */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
void shake256(uint8_t *out, size_t outlen, const uint8_t *in, size_t inlen);
void shake256_x2(uint8_t *out0, uint8_t *out1, size_t outlen, const uint8_t *in0, const uint8_t *in1, size_t inlen)
{
    shake256(out0, outlen, in0, inlen);
    shake256(out1, outlen, in1, inlen);
}
#if NTRUPLUS_N != 768
void tobytes_full_asm(uint8_t *, const int16_t *);
void hash_g(uint8_t *buf, const uint8_t *msg);
void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N])
{
    uint8_t data[NTRUPLUS_POLYBYTES];
    tobytes_full_asm(data, coeffs);
    hash_g(buf, data);
    memset(data, 0, sizeof data);
}
#endif
