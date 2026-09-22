#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "internal.h"
#include "kat/rng.h"
static void emit(const void*p,size_t n){if(fwrite(p,1,n,stdout)!=n)abort();}
int main(void){
 uint8_t seed[48],coins[NTRUPLUS_N/8],pk[NTRUPLUS_PUBLICKEYBYTES],sk[NTRUPLUS_SECRETKEYBYTES];
 uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],bad[sizeof ct],ss[32],ds[32],zero[32]={0};
 for(unsigned t=0;t<100;t++){
  for(unsigned i=0;i<sizeof seed;i++)seed[i]=(uint8_t)(t*73+i*19);
  for(unsigned i=0;i<sizeof coins;i++)coins[i]=(uint8_t)(t*31+i*71);
  randombytes_init(seed,NULL,256);
  if(ntruplus768_keypair_impl(pk,sk)||ntruplus768_enc_derand_impl(ct,ss,pk,coins))abort();
  if(ntruplus768_dec_impl(ds,ct,sk)||memcmp(ds,ss,32))abort();
  emit(pk,sizeof pk);emit(sk,sizeof sk);emit(ct,sizeof ct);emit(ss,32);emit(ds,32);
  for(int kind=0;kind<2;kind++){
   memcpy(bad,ct,sizeof bad);
   if(kind==0){bad[0]=255;bad[1]|=15;}else memset(bad,0,sizeof bad);
   int rc=ntruplus768_dec_impl(ds,bad,sk);
   if(rc!=1||memcmp(ds,zero,32))abort();
   emit(&rc,sizeof rc);emit(ds,32);
  }
  pk[3*(t%384)]=255;pk[3*(t%384)+1]|=15;
  int rc=ntruplus768_enc_derand_impl(ct,ss,pk,coins);
  if(rc!=1)abort();
  emit(&rc,sizeof rc);emit(ct,sizeof ct);emit(ss,32);
 }
 fprintf(stderr,"PASS installed KEM: 100 distinct keys; PK/SK/CT/SS transcript; invalid PK and both CT domains\n");
 return 0;
}
