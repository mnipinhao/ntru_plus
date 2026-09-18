#include <string.h>
#include "symmetric.h"
#include "secure_clear.h"
#include "fips202.h"
#include "pack_asm.h"

/*
 * NTRU+1152 symmetric layer.
 *
 * hash_f and hash_g use the fused fixed-size kernels: their input is always one
 * domain byte followed by exactly NTRUPLUS_POLYBYTES, and their output is always
 * the same length, so the sponge needs no state array, no length arithmetic, and
 * no copy to prepend the domain byte.  1 + 1728 is 12 blocks of 136 plus a
 * 97-byte tail; hash_g's 288 bytes are two squeeze blocks plus 16.
 *
 * hash_h keeps the generic sponge.  Its input is 176 bytes, a single block,
 * where the fusion would have nothing to amortize.
 */

#define HASH_F_INBYTES  (NTRUPLUS_POLYBYTES)
#define HASH_F_OUTBYTES (32)
#define HASH_G_INBYTES  (NTRUPLUS_POLYBYTES)
#define HASH_G_OUTBYTES (NTRUPLUS_N / 4)
#define HASH_H_INBYTES  (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
#define HASH_H_OUTBYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)

void ntruplus_hash_f_fixed(uint8_t output[HASH_F_OUTBYTES],
                           const uint8_t input[HASH_F_INBYTES]);
void ntruplus_hash_g_fixed(uint8_t output[HASH_G_OUTBYTES],
                           const uint8_t input[HASH_G_INBYTES]);

void hash_f(uint8_t *buf, const uint8_t *msg)
{
    ntruplus_hash_f_fixed(buf, msg);
}

void hash_g(uint8_t *buf, const uint8_t *msg)
{
    ntruplus_hash_g_fixed(buf, msg);
}

/* Encapsulation-private boundary: serialize straight into the transcript. */
void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N])
{
    uint8_t data[HASH_G_INBYTES];

    tobytes_full_asm(data, coeffs);
    ntruplus_hash_g_fixed(buf, data);
    secure_clear(data, sizeof data);
}

void hash_h(uint8_t *buf, const uint8_t *msg)
{
    /*
     * The prefixed entry point absorbs 0x02 || msg without building it, so
     * this no longer keeps a copy of the message on the stack, and no longer
     * routes it through the generic sponge's malloc'd state -- which
     * shake256_ctx_release() frees without wiping.
     */
    shake256_prefixed(buf, HASH_H_OUTBYTES, 0x02, msg, HASH_H_INBYTES);
}
