/* warm to the P-cluster, then loop one operation forever for `sample` */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <sys/qos.h>
#include <time.h>
#include "api.h"
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static uint8_t pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],got[CRYPTO_BYTES];
static volatile unsigned sink;
int main(int argc,char**argv){
  int op = argc>1 ? atoi(argv[1]) : 2;
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  if(crypto_kem_keypair(pk,sk)||crypto_kem_enc(ct,ss,pk)||crypto_kem_dec(got,ct,sk)
     ||memcmp(ss,got,CRYPTO_BYTES)){fputs("selftest failed\n",stderr);return 1;}
  uint64_t t0=nsec(); while(nsec()-t0 < 3000000000ull){
    crypto_kem_keypair(pk,sk); crypto_kem_enc(ct,ss,pk); crypto_kem_dec(got,ct,sk); sink+=got[0]; }
  /* Report this loop's own ns/op.  Converting sample fractions with a time
   * measured by a different harness is wrong: the spin loop runs one operation
   * back to back and is faster than the round-robin one, by a factor that is
   * not the same for every build and operation. */
  { uint64_t best=~0ull;
    for(int r=0;r<25;r++){ uint64_t a=nsec();
      for(int k=0;k<300;k++){ if(op==0){crypto_kem_keypair(pk,sk);sink+=sk[0];}
        else if(op==1){crypto_kem_enc(ct,ss,pk);sink+=ct[0];}
        else {crypto_kem_dec(got,ct,sk);sink+=got[0];} }
      uint64_t d=nsec()-a; if(d<best) best=d; }
    fprintf(stderr,"NSOP %.1f\n",(double)best/300.0); fflush(stderr); }
  for(;;){ if(op==0){crypto_kem_keypair(pk,sk);sink+=sk[0];}
           else if(op==1){crypto_kem_enc(ct,ss,pk);sink+=ct[0];}
           else {crypto_kem_dec(got,ct,sk);sink+=got[0];} }
}
