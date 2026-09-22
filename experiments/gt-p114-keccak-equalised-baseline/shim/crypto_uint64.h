#ifndef CRYPTO_UINT64_H
#define CRYPTO_UINT64_H
#include <stdint.h>
typedef uint64_t crypto_uint64;
/* SUPERCOP's constant-time "is x nonzero", reproduced for the standalone
 * measurement build.  Same shape as supercop's crypto_uint64.h. */
static inline crypto_uint64 crypto_uint64_nonzero_01(crypto_uint64 x)
{
    __asm__ ("" : "+r"(x) : : );
    return (crypto_uint64)((x | (~x + 1)) >> 63);
}
#endif
