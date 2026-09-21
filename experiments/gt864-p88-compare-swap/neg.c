/* decapsulation must agree with the previous implementation on corrupted
 * ciphertexts too, where the fused compare used to decide the rejection */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "api.h"
int crypto_kem_keypair(uint8_t*,uint8_t*);
int crypto_kem_enc(uint8_t*,uint8_t*,const uint8_t*);
int crypto_kem_dec(uint8_t*,const uint8_t*,const uint8_t*);
static uint8_t pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],got[CRYPTO_BYTES];
int main(void){
  for(int t=0;t<200;t++){
    crypto_kem_keypair(pk,sk); crypto_kem_enc(ct,ss,pk);
    int r=crypto_kem_dec(got,ct,sk);
    printf("ok %d %d ",r,(int)(memcmp(ss,got,CRYPTO_BYTES)==0));
    for(int b=0;b<CRYPTO_BYTES;b++) printf("%02x",got[b]); printf("\n");
    for(int k=0;k<3;k++){
      uint8_t bad[CRYPTO_CIPHERTEXTBYTES]; memcpy(bad,ct,sizeof bad);
      size_t p=((size_t)(t*7919+k*104729))%CRYPTO_CIPHERTEXTBYTES;
      bad[p]^=(uint8_t)(1u<<((t+k)%8));
      r=crypto_kem_dec(got,bad,sk);
      printf("bad %d ",r);
      for(int b=0;b<CRYPTO_BYTES;b++) printf("%02x",got[b]); printf("\n");
    }
  }
  return 0;}
