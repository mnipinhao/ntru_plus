#include <string.h>
#include "symmetric.h"
#include "secure_clear.h"
#include "fips202.h"
#include "pack_asm.h"

/*
 * NTRU+1152 symmetric layer, Milestone 1.
 *
 * Deliberately the generic sponge, not NTRU+864's fixed-size specialization.
 * That specialization (P53/P55) is the single largest lever in the 864 campaign
 * -- roughly 4358 and 4103 cycles -- but it is an optimization, and 864 itself
 * reached it at gate 53 of 58, long after correctness.  It is recorded as M2-1.
 *
 * Sizes differ anyway: hash_f absorbs 1 + 1728 = 12 blocks of 136 plus a
 * 97-byte tail, against 864's 9 blocks plus 73; hash_g squeezes 288 bytes, so
 * three blocks against 864's two.
 */

#define HASH_F_INBYTES  (NTRUPLUS_POLYBYTES)
#define HASH_F_OUTBYTES (32)
#define HASH_G_INBYTES  (NTRUPLUS_POLYBYTES)
#define HASH_G_OUTBYTES (NTRUPLUS_N / 4)
#define HASH_H_INBYTES  (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
#define HASH_H_OUTBYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)

void hash_f(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_F_INBYTES];

    data[0] = 0x00;
    memcpy(data + 1, msg, HASH_F_INBYTES);
    shake256(buf, HASH_F_OUTBYTES, data, HASH_F_INBYTES + 1);
    secure_clear(data, sizeof data);
}

void hash_g(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_G_INBYTES];

    data[0] = 0x01;
    memcpy(data + 1, msg, HASH_G_INBYTES);
    shake256(buf, HASH_G_OUTBYTES, data, HASH_G_INBYTES + 1);
    secure_clear(data, sizeof data);
}

/* Encapsulation-private boundary: serialize straight into the transcript. */
void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N])
{
    uint8_t data[1 + HASH_G_INBYTES];

    data[0] = 0x01;
    tobytes_full_asm(data + 1, coeffs);
    shake256(buf, HASH_G_OUTBYTES, data, HASH_G_INBYTES + 1);
    secure_clear(data, sizeof data);
}

void hash_h(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_H_INBYTES];

    data[0] = 0x02;
    memcpy(data + 1, msg, HASH_H_INBYTES);
    shake256(buf, HASH_H_OUTBYTES, data, HASH_H_INBYTES + 1);
    secure_clear(data, sizeof data);
}
