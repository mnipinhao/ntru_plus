#include "api.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint64_t rng;
void randombytes(uint8_t *p,size_t n){while(n--){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;*p++=rng;}}
static void emit(const uint8_t*p,size_t n){while(n--)printf("%02x",*p++);putchar('\n');}
int main(void){
 uint8_t pk[1296],sk[2624],ct[1296],bad[1296],ss[32],got[32];
 for(int t=0;t<32;t++){
  rng=100+t;if(crypto_kem_keypair(pk,sk))return 1;
  rng=1000+t;if(crypto_kem_enc(ct,ss,pk))return 2;
  if(crypto_kem_dec(got,ct,sk)||memcmp(ss,got,32))return 3;
  emit(pk,sizeof pk);emit(sk,sizeof sk);emit(ct,sizeof ct);emit(ss,32);
  memcpy(bad,ct,sizeof ct);bad[11+37*t]^=128;
  int ret=crypto_kem_dec(got,bad,sk);if(ret==0)return 4;
  printf("tamper %d\n",ret);emit(got,32);
  for(int z=0;z<32;z++){
   for(int j=0;j<1296;j++)bad[j]=z==0?0:z==1?255:(uint8_t)(j*37+z*19);
   memset(got,0xa5,32);ret=crypto_kem_dec(got,bad,sk);
   printf("malformed %d\n",ret);emit(got,32);
  }
 }
 return 0;
}
