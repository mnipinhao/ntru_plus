#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "api.h"
void bench_randombytes_reset(uint32_t seed);
static int all_zero(const unsigned char *x, size_t n) {
    unsigned char a=0; for(size_t i=0;i<n;i++) a|=x[i]; return a==0;
}
int main(void) {
    unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
    unsigned char ct[CRYPTO_CIPHERTEXTBYTES], ss[CRYPTO_BYTES], ds[CRYPTO_BYTES];
    bench_randombytes_reset(7);
    if (crypto_kem_keypair(pk,sk) || crypto_kem_enc(ct,ss,pk)) return 1;
    ct[0]^=1; memset(ds,0xa5,sizeof ds);
    if (crypto_kem_dec(ds,ct,sk)!=1 || !all_zero(ds,sizeof ds)) return 2;
    memset(pk,0xff,sizeof pk); memset(ct,0xa5,sizeof ct); memset(ss,0xa5,sizeof ss);
    if (crypto_kem_enc(ct,ss,pk)!=1 || !all_zero(ct,sizeof ct) || !all_zero(ss,sizeof ss)) return 3;
    puts("public failure paths: modified ct and noncanonical pk zero outputs");
    return 0;
}
