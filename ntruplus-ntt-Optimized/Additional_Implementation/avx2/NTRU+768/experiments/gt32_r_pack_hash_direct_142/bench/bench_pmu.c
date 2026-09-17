#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "candidate.h"
#include "internal.h"
#include "symmetric.h"
static volatile uint64_t sink;
static uint64_t rs=UINT64_C(0x1420cafe12345678);
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)rs;}
static void pairpk(uint8_t*p){for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;p[3*i]=(uint8_t)x;p[3*i+1]=(uint8_t)((x>>8)|(y<<4));p[3*i+2]=(uint8_t)(y>>4);}}
int main(int argc,char**argv){if(argc!=2)return 64;cpu_set_t s;CPU_ZERO(&s);CPU_SET(1,&s);sched_setaffinity(0,sizeof s,&s);
 _Alignas(64) int16_t a[768],f[768],m[768];_Alignas(64) uint8_t pk[1152],coins[96],o[1152],ss[32];
 for(int i=0;i<768;i++)a[i]=(int16_t)((int)(rnd()%3457)-1728);
 ntruplus768_ntt_frontend_avx2(f,a);ntruplus768_ntt_m_avx2(m,f);pairpk(pk);
 for(int i=0;i<96;i++)coins[i]=(uint8_t)rnd();
 if(!strcmp(argv[1],"pack-control"))for(int i=0;i<200000;i++){ntruplus768_pack_m_lazy10788_avx2(o,m);hash_g(o,o);sink+=o[i%192];}
 else if(!strcmp(argv[1],"pack-candidate"))for(int i=0;i<200000;i++){gt142_hash_g_from_m(o,m);sink+=o[i%192];}
 else if(!strcmp(argv[1],"enc-control"))for(int i=0;i<20000;i++){ntruplus768_enc_derand_impl(o,ss,pk,coins);sink+=o[i%1152];}
 else if(!strcmp(argv[1],"enc-candidate"))for(int i=0;i<20000;i++){gt142_enc_derand(o,ss,pk,coins);sink+=o[i%1152];}
 else return 64;
 printf("%llu\n",(unsigned long long)sink);return 0;}
