#include <string.h>
#include "symmetric.h"
#include "util.h"

#include "fips202.h"

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
    /* hash_f input is public; follow the Official cleanup policy. */
}

void hash_g(uint8_t *buf, const uint8_t *msg)
{
    /* Absorb the virtual prefix || msg before writing any output (buf == msg
     * is used by Encap). No domain-prefixed message copy is materialized. */
    ntruplus_shake256_prefix(buf, HASH_G_OUTBYTES, 0x01, msg, HASH_G_INBYTES);
}

void hash_h(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_H_INBYTES];

    data[0] = 0x02;
    memcpy(data + 1, msg, HASH_H_INBYTES);
    shake256(buf, HASH_H_OUTBYTES, data, HASH_H_INBYTES + 1);
    secure_clear(data, sizeof data);
}
