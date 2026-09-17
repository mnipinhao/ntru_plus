#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "candidate.h"
#include "cpucycles.h"
#include "internal.h"
#include "symmetric.h"

#define S 31
static volatile uint64_t sink;
static uint64_t ticks(void){unsigned a;_mm_lfence();uint64_t x=__rdtscp(&a);_mm_lfence();return x;}
static int cmp(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return(x>y)-(x<y);}
static double med(double*x){qsort(x,S,sizeof*x,cmp);return x[S/2];}
static void pin(void){cpu_set_t s;CPU_ZERO(&s);CPU_SET(1,&s);(void)sched_setaffinity(0,sizeof s,&s);}
static uint64_t now(int tsc){return tsc?ticks():(uint64_t)cpucycles();}
static uint64_t rs=UINT64_C(0x14255aa55aa55aa5);
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)rs;}
static void pairpk(uint8_t*p){for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;p[3*i]=(uint8_t)x;p[3*i+1]=(uint8_t)((x>>8)|(y<<4));p[3*i+2]=(uint8_t)(y>>4);}}

int main(int argc,char**argv)
{
    int reverse=argc>1?atoi(argv[1]):0,tsc=argc>2?atoi(argv[2]):0;pin();
    _Alignas(64) int16_t coeff[768],front[768],m[768];
    _Alignas(64) uint8_t pk[1152],coins[96],out[1152],ss[32];
    for(int i=0;i<768;i++)coeff[i]=(int16_t)((int)(rnd()%3457)-1728);
    ntruplus768_ntt_frontend_avx2(front,coeff);ntruplus768_ntt_m_avx2(m,front);
    pairpk(pk);for(int i=0;i<96;i++)coins[i]=(uint8_t)rnd();
    double p0[S],p1[S],e0[S],e1[S];
    for(int s=0;s<S;s++){
        int first=(s+reverse)&1;uint64_t x,y;unsigned I=64;
#define TIMEP(dst,code) do{x=now(tsc);for(unsigned i=0;i<I;i++){code;sink+=out[i%192];}y=now(tsc);dst[s]=(double)(y-x)/I;}while(0)
        if(!first){TIMEP(p0,ntruplus768_pack_m_lazy10788_avx2(out,m);hash_g(out,out));TIMEP(p1,gt142_hash_g_from_m(out,m));}
        else{TIMEP(p1,gt142_hash_g_from_m(out,m));TIMEP(p0,ntruplus768_pack_m_lazy10788_avx2(out,m);hash_g(out,out));}
#undef TIMEP
        I=16;
#define TIMEE(dst,code) do{x=now(tsc);for(unsigned i=0;i<I;i++){if((code)!=0)return 2;sink+=out[i%1152]+ss[i%32];}y=now(tsc);dst[s]=(double)(y-x)/I;}while(0)
        if(!first){TIMEE(e0,ntruplus768_enc_derand_impl(out,ss,pk,coins));TIMEE(e1,gt142_enc_derand(out,ss,pk,coins));}
        else{TIMEE(e1,gt142_enc_derand(out,ss,pk,coins));TIMEE(e0,ntruplus768_enc_derand_impl(out,ss,pk,coins));}
#undef TIMEE
    }
    double P0=med(p0),P1=med(p1),E0=med(e0),E1=med(e1);
    printf("{\"backend\":\"%s\",\"reverse\":%d,\"pack_hash\":[%.3f,%.3f,%.3f],\"encap\":[%.3f,%.3f,%.3f],\"sink\":%llu}\n",tsc?"rdtscp":cpucycles_implementation(),reverse,P0,P1,P1-P0,E0,E1,E1-E0,(unsigned long long)sink);
    return 0;
}
