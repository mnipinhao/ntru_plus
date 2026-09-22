#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "internal.h"
#include "kat/rng.h"
int ntruplus768_exp001_enc_derand_eager(uint8_t*,uint8_t*,const uint8_t*,const uint8_t*);
int ntruplus768_exp001_dec_eager(uint8_t*,const uint8_t*,const uint8_t*);
int main(void){
 uint8_t seed[48],coins[NTRUPLUS_N/8],pk[NTRUPLUS_PUBLICKEYBYTES],sk[NTRUPLUS_SECRETKEYBYTES];
 uint8_t c0[NTRUPLUS_CIPHERTEXTBYTES],c1[sizeof c0],s0[32],s1[32],d0[32],d1[32];
 for(unsigned t=0;t<100;t++){
  for(unsigned i=0;i<sizeof seed;i++)seed[i]=(uint8_t)(t*73+i*19);
  for(unsigned i=0;i<sizeof coins;i++)coins[i]=(uint8_t)(t*31+i*71);
  randombytes_init(seed,NULL,256);if(ntruplus768_keypair_impl(pk,sk))abort();
  int a=ntruplus768_enc_derand_impl(c0,s0,pk,coins),b=ntruplus768_exp001_enc_derand_eager(c1,s1,pk,coins);
  if(a||b||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,32))abort();
  a=ntruplus768_dec_impl(d0,c0,sk);b=ntruplus768_exp001_dec_eager(d1,c0,sk);
  if(a||b||memcmp(d0,d1,32)||memcmp(d0,s0,32))abort();
  /* Both noncanonical and canonical-but-invalid ciphertexts. */
  for(int kind=0;kind<2;kind++){
   memcpy(c1,c0,sizeof c0);
   if(kind==0){c1[0]=255;c1[1]|=15;}else memset(c1,0,sizeof c1);
   a=ntruplus768_dec_impl(d0,c1,sk);b=ntruplus768_exp001_dec_eager(d1,c1,sk);
   if(a!=b||memcmp(d0,d1,32))abort();
  }
  pk[3*(t%384)]=255;pk[3*(t%384)+1]|=15;
  a=ntruplus768_enc_derand_impl(c0,s0,pk,coins);b=ntruplus768_exp001_enc_derand_eager(c1,s1,pk,coins);
  if(a!=b||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,32))abort();
 }
 puts("PASS shared eager: 100 distinct deterministic keys/Encap/Decap; invalid PK and both CT domains exact");
}
