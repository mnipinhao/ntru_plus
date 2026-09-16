#include <string.h>
#include "symmetric.h"

#ifdef SUPPORTS_SHAKE256_ASM
#include "CE/fips202.h"
#else
#include "NO_CE/fips202.h"
#endif

#define HASH_F_INBYTES  (NTRUPLUS_POLYBYTES)
#define HASH_F_OUTBYTES (32)

#define HASH_G_INBYTES  (NTRUPLUS_POLYBYTES)
#define HASH_G_OUTBYTES (NTRUPLUS_N / 4)

#define HASH_H_INBYTES  (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
#define HASH_H_OUTBYTES (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)

void gt864_p18_tobytes_full_asm(uint8_t *, const int16_t *);
void ntruplus_hash_g_fixed(uint8_t output[216], const uint8_t input[1296]);

void hash_f(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_F_INBYTES];

    data[0] = 0x00;
    memcpy(data + 1, msg, HASH_F_INBYTES);
    shake256(buf, HASH_F_OUTBYTES, data, HASH_F_INBYTES + 1);
}

void hash_g(uint8_t *buf, const uint8_t *msg)
{
    ntruplus_hash_g_fixed(buf, msg);
}

void hash_g_fr0(uint8_t *buf, const int16_t coeffs[NTRUPLUS_N])
{
    uint8_t data[HASH_G_INBYTES];

    gt864_p18_tobytes_full_asm(data, coeffs);
    ntruplus_hash_g_fixed(buf, data);
}

void hash_h(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_H_INBYTES];

    data[0] = 0x02;
    memcpy(data + 1, msg, HASH_H_INBYTES);
    shake256(buf, HASH_H_OUTBYTES, data, HASH_H_INBYTES + 1);
}
