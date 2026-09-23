#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "api.h"
#include "params.h"

static void set_coeff(uint8_t *x, size_t i, uint16_t v)
{
    size_t o = 3 * (i / 2);
    if (!(i & 1)) { x[o] = (uint8_t)v; x[o + 1] = (x[o + 1] & 0xf0) | (v >> 8); }
    else { x[o + 1] = (x[o + 1] & 0x0f) | ((v & 15) << 4); x[o + 2] = v >> 4; }
}
static int zero(const uint8_t *x, size_t n) { uint8_t a=0; while(n--) a|=*x++; return a==0; }

int main(void)
{
    static const uint16_t bad[] = {NTRUPLUS_Q, NTRUPLUS_Q + 1, 4095};
    uint8_t pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES], ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss[CRYPTO_BYTES], got[CRYPTO_BYTES], xpk[CRYPTO_PUBLICKEYBYTES];
    uint8_t xsk[CRYPTO_SECRETKEYBYTES], xct[CRYPTO_CIPHERTEXTBYTES];
    size_t cases=0, failures=0;
    if (crypto_kem_keypair(pk,sk) || crypto_kem_enc(ct,ss,pk) ||
        crypto_kem_dec(got,ct,sk) || memcmp(ss,got,sizeof ss)) return 1;
    for (size_t v=0; v<sizeof bad/sizeof bad[0]; v++) for (size_t i=0;i<NTRUPLUS_N;i++) {
        memcpy(xpk,pk,sizeof xpk); set_coeff(xpk,i,bad[v]); memset(xct,0xa5,sizeof xct); memset(got,0xa5,sizeof got);
        failures += crypto_kem_enc(xct,got,xpk) != 1 || !zero(xct,sizeof xct) || !zero(got,sizeof got); cases++;
        memcpy(xct,ct,sizeof xct); set_coeff(xct,i,bad[v]); memset(got,0xa5,sizeof got);
        failures += crypto_kem_dec(got,xct,sk) != 1 || !zero(got,sizeof got); cases++;
        memcpy(xsk,sk,sizeof xsk); set_coeff(xsk,i,bad[v]); memset(got,0xa5,sizeof got);
        failures += crypto_kem_dec(got,ct,xsk) != 1 || !zero(got,sizeof got); cases++;
        memcpy(xsk,sk,sizeof xsk); set_coeff(xsk+NTRUPLUS_POLYBYTES,i,bad[v]); memset(got,0xa5,sizeof got);
        failures += crypto_kem_dec(got,ct,xsk) != 1 || !zero(got,sizeof got); cases++;
    }
    printf("canonical-boundary: cases=%zu failures=%zu\n",cases,failures);
    return failures != 0;
}
