#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "api.h"
#include "crypto_kem.h"
#include "rng.h"

#define GUARD 32
static int guarded(const uint8_t *x, size_t n) {
  for (size_t i=0;i<GUARD;i++) if (x[i]!=0xa5 || x[GUARD+n+i]!=0xa5) return 0;
  return 1;
}
static int allzero(const uint8_t *x,size_t n) { uint8_t a=0; for(size_t i=0;i<n;i++) a|=x[i]; return a==0; }
int main(void) {
  uint8_t entropy[48], personalization[48];
  for (size_t i=0;i<48;i++) { entropy[i]=(uint8_t)(i*17+3); personalization[i]=(uint8_t)(i*29+7); }
  randombytes_init(entropy,personalization,256);
  for (int trial=0;trial<32;trial++) {
    uint8_t pkbuf[GUARD+CRYPTO_PUBLICKEYBYTES+GUARD], skbuf[GUARD+CRYPTO_SECRETKEYBYTES+GUARD];
    uint8_t ctbuf[GUARD+CRYPTO_CIPHERTEXTBYTES+GUARD], ss1buf[GUARD+CRYPTO_BYTES+GUARD];
    uint8_t ss2buf[GUARD+CRYPTO_BYTES+GUARD], pkcopy[CRYPTO_PUBLICKEYBYTES];
    uint8_t skcopy[CRYPTO_SECRETKEYBYTES], ctcopy[CRYPTO_CIPHERTEXTBYTES];
    memset(pkbuf,0xa5,sizeof pkbuf); memset(skbuf,0xa5,sizeof skbuf); memset(ctbuf,0xa5,sizeof ctbuf);
    memset(ss1buf,0xa5,sizeof ss1buf); memset(ss2buf,0xa5,sizeof ss2buf);
    uint8_t *pk=pkbuf+GUARD,*sk=skbuf+GUARD,*ct=ctbuf+GUARD,*ss1=ss1buf+GUARD,*ss2=ss2buf+GUARD;
    if (crypto_kem_keypair(pk,sk)) return 10;
    memcpy(pkcopy,pk,sizeof pkcopy); memcpy(skcopy,sk,sizeof skcopy);
    if (crypto_kem_enc(ct,ss1,pk)) return 11;
    if (memcmp(pk,pkcopy,sizeof pkcopy)) return 12;
    memcpy(ctcopy,ct,sizeof ctcopy);
    if (crypto_kem_dec(ss2,ct,sk) || memcmp(ss1,ss2,CRYPTO_BYTES)) return 13;
    if (memcmp(ct,ctcopy,sizeof ctcopy) || memcmp(sk,skcopy,sizeof skcopy)) return 14;
    if (!guarded(pkbuf,CRYPTO_PUBLICKEYBYTES)||!guarded(skbuf,CRYPTO_SECRETKEYBYTES)||
        !guarded(ctbuf,CRYPTO_CIPHERTEXTBYTES)||!guarded(ss1buf,CRYPTO_BYTES)||!guarded(ss2buf,CRYPTO_BYTES)) return 15;
    ct[trial%CRYPTO_CIPHERTEXTBYTES]^=1;
    memset(ss2,0x5a,CRYPTO_BYTES);
    if (!crypto_kem_dec(ss2,ct,sk) || !allzero(ss2,CRYPTO_BYTES)) return 16;
  }
  {
    uint8_t pk[CRYPTO_PUBLICKEYBYTES],ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES];
    memset(pk,0xff,sizeof pk); memset(ct,0x5a,sizeof ct); memset(ss,0x5a,sizeof ss);
    if (!crypto_kem_enc(ct,ss,pk) || !allzero(ct,sizeof ct) || !allzero(ss,sizeof ss)) return 17;
  }
  puts("api-semantics: 32 valid/tampered trials plus invalid-PK zeroization passed");
  return 0;
}
