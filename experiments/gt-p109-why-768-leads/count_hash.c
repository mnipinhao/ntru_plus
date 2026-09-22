#include <stdio.h>
#include <stdint.h>
#include "params.h"
extern unsigned long perm_calls;
void hash_f(uint8_t*, const uint8_t*); void hash_g(uint8_t*, const uint8_t*); void hash_h(uint8_t*, const uint8_t*);
static uint8_t pk[NTRUPLUS_POLYBYTES], msg[NTRUPLUS_N/8+NTRUPLUS_SYMBYTES], out[4096];
int main(void){
  for(size_t i=0;i<sizeof pk;i++) pk[i]=(uint8_t)(i*211u);
  for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)(i*167u);
  unsigned long a,b,c; const int N=100;
  perm_calls=0; for(int i=0;i<N;i++) hash_f(out,pk);  a=perm_calls;
  perm_calls=0; for(int i=0;i<N;i++) hash_g(out,pk);  b=perm_calls;
  perm_calls=0; for(int i=0;i<N;i++) hash_h(out,msg); c=perm_calls;
  printf("hash_f %.0f  hash_g %.0f  hash_h %.0f\n",(double)a/N,(double)b/N,(double)c/N);
  return 0;}
