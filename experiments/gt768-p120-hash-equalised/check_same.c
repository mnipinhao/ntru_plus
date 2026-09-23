/* Prints a digest of pk/sk/ct/ss over 200 deterministic keypair/enc/dec runs; identical KEMs print identical lines. */
#include <stdio.h>
#include <stdint.h>
#include "api.h"
int crypto_kem_keypair(unsigned char*,unsigned char*);
int crypto_kem_enc(unsigned char*,unsigned char*,const unsigned char*);
int crypto_kem_dec(unsigned char*,const unsigned char*,const unsigned char*);
void rb_seed_det(uint64_t);
static uint64_t h=1469598103934665603ULL; static void mix(const unsigned char*p,size_t n){for(size_t i=0;i<n;i++){h^=p[i];h*=1099511628211ULL;}}
int main(void){ static unsigned char pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES],ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],ss2[CRYPTO_BYTES]; int bad=0;
 for(int t=0;t<200;t++){ rb_seed_det(1000+t); crypto_kem_keypair(pk,sk); crypto_kem_enc(ct,ss,pk); crypto_kem_dec(ss2,ct,sk);
   for(int i=0;i<CRYPTO_BYTES;i++) bad|=ss[i]!=ss2[i]; mix(pk,sizeof pk); mix(sk,sizeof sk); mix(ct,sizeof ct); mix(ss,sizeof ss);
   ct[t%CRYPTO_CIPHERTEXTBYTES]^=1; crypto_kem_dec(ss2,ct,sk); mix(ss2,sizeof ss2); }
 printf("digest %016llx roundtrip-mismatch %d\n",(unsigned long long)h,bad); return bad; }
