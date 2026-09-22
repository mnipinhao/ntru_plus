#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "api.h"
extern unsigned long perm_calls;
void rb_seed(void);
static uint8_t pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],got[CRYPTO_BYTES];
int main(void){
  rb_seed();
  unsigned long a,b,c; const int N=200;
  crypto_kem_keypair(pk,sk); crypto_kem_enc(ct,ss,pk); crypto_kem_dec(got,ct,sk);
  rb_seed();
  perm_calls=0; for(int i=0;i<N;i++) crypto_kem_keypair(pk,sk); a=perm_calls;
  perm_calls=0; for(int i=0;i<N;i++) crypto_kem_enc(ct,ss,pk); b=perm_calls;
  perm_calls=0; for(int i=0;i<N;i++) crypto_kem_dec(got,ct,sk); c=perm_calls;
  printf("keygen %.1f  encap %.1f  decap %.1f\n",(double)a/N,(double)b/N,(double)c/N);
  return 0;}
