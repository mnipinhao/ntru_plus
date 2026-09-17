#include <stdint.h>
#include "fips202.h"
#include "internal.h"
#include "symmetric.h"
#include "util.h"

__attribute__((noinline, section(".rhash_tail"), visibility("hidden")))
void ntruplus768_hash_g_from_m_avx2(uint8_t out[HASH_G_OUTBYTES],
                                    const int16_t r_m[NTRUPLUS_N])
{
    uint8_t data[1 + HASH_G_INBYTES];
    data[0] = 0x01;
    ntruplus768_pack_m_lazy10788_avx2(data + 1, r_m);
    shake256(out, HASH_G_OUTBYTES, data, sizeof data);
    secure_clear(data, sizeof data);
}
