#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "params.h"
void hash_f(uint8_t*, const uint8_t*);   void o_hash_f(uint8_t*, const uint8_t*);
void hash_g(uint8_t*, const uint8_t*);   void o_hash_g(uint8_t*, const uint8_t*);
void hash_h(uint8_t*, const uint8_t*);   void o_hash_h(uint8_t*, const uint8_t*);
static uint8_t pk[NTRUPLUS_POLYBYTES], msg[NTRUPLUS_N/8+NTRUPLUS_SYMBYTES];
static uint8_t a[4096], b[4096];
int main(void){
  int bad=0;
  for(int t=0;t<64;t++){
    for(size_t i=0;i<sizeof pk;i++)  pk[i]=(uint8_t)(i*211u+t);
    for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)(i*167u+t);
    memset(a,0,sizeof a); memset(b,0,sizeof b);
    hash_f(a,pk);  o_hash_f(b,pk);  if(memcmp(a,b,NTRUPLUS_SYMBYTES)) bad|=1;
    memset(a,0,sizeof a); memset(b,0,sizeof b);
    hash_g(a,pk);  o_hash_g(b,pk);  if(memcmp(a,b,NTRUPLUS_N/4)) bad|=2;
    memset(a,0,sizeof a); memset(b,0,sizeof b);
    hash_h(a,msg); o_hash_h(b,msg); if(memcmp(a,b,NTRUPLUS_SYMBYTES+NTRUPLUS_N/4)) bad|=4;
  }
  printf("  N=%d  hash_f %s, hash_g %s, hash_h %s\n", NTRUPLUS_N,
         bad&1?"不同":"相同", bad&2?"不同":"相同", bad&4?"不同":"相同");
  return bad!=0;
}
