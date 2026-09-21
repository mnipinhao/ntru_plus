#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "api.h"
static int cmp(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return x<y?-1:x>y;}
static double ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return (double)t.tv_sec*1e9+(double)t.tv_nsec;}
#define R 41
#define N 300
static uint8_t pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],got[CRYPTO_BYTES];
static volatile unsigned sink;
int main(void){
  if(crypto_kem_keypair(pk,sk)||crypto_kem_enc(ct,ss,pk)||crypto_kem_dec(got,ct,sk)
     ||memcmp(ss,got,CRYPTO_BYTES)){fputs("selftest failed\n",stderr);return 1;}
  static double s[3][R];
  for(int r=0;r<R;r++) for(int op=0;op<3;op++){
    double t0=ns();
    for(int k=0;k<N;k++){
      if(op==0){crypto_kem_keypair(pk,sk); sink+=sk[0];}
      else if(op==1){crypto_kem_enc(ct,ss,pk); sink+=ct[0];}
      else {crypto_kem_dec(got,ct,sk); sink+=got[0];}
    }
    s[op][r]=(ns()-t0)/N;
  }
  const char*nm[3]={"keygen","encaps","decaps"};
  for(int op=0;op<3;op++){qsort(s[op],R,sizeof(double),cmp);printf("%s %.0f ",nm[op],s[op][0]);}
  printf("\n"); return 0;}
