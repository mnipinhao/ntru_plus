#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "candidate.h"
#include "cpucycles.h"
#include "internal.h"

#define S 31
static volatile uint64_t sink;
static uint64_t ticks(void){unsigned a;_mm_lfence();uint64_t x=__rdtscp(&a);_mm_lfence();return x;}
static int cmp(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return(x>y)-(x<y);}
static double med(double*x){qsort(x,S,sizeof*x,cmp);return x[S/2];}
static void pin(void){cpu_set_t s;CPU_ZERO(&s);CPU_SET(1,&s);(void)sched_setaffinity(0,sizeof s,&s);}
static uint64_t now(int tsc){return tsc?ticks():(uint64_t)cpucycles();}
static uint64_t rs=UINT64_C(0x14755aa55aa55aa5);
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)rs;}

int main(int argc,char**argv) {
    int reverse=argc>1?atoi(argv[1]):0,tsc=argc>2?atoi(argv[2]):0;pin();
    _Alignas(64) int16_t coeff[768],front[768],m[768];
    _Alignas(64) uint8_t wire[1152];
    for(int i=0;i<768;i++)coeff[i]=(int16_t)((int)(rnd()%5)-2);
    ntruplus768_ntt_frontend_avx2(front,coeff);
    double c0[S],c1[S];
    for(int s=0;s<S;s++){
        int first=(s+reverse)&1;uint64_t x,y;unsigned I=128;
#define TIME(dst,code) do{x=now(tsc);for(unsigned i=0;i<I;i++){code;sink+=wire[i%1152]+(uint16_t)m[i%768];}y=now(tsc);dst[s]=(double)(y-x)/I;}while(0)
        if(!first){TIME(c0,ntruplus768_ntt_m_avx2(m,front);ntruplus768_pack_m_lazy10788_avx2(wire,m));TIME(c1,gt147_ntt_m_wire_avx2(m,front,wire));}
        else{TIME(c1,gt147_ntt_m_wire_avx2(m,front,wire));TIME(c0,ntruplus768_ntt_m_avx2(m,front);ntruplus768_pack_m_lazy10788_avx2(wire,m));}
#undef TIME
    }
    double C0=med(c0),C1=med(c1);
    printf("{\"backend\":\"%s\",\"reverse\":%d,\"forward_pack\":[%.3f,%.3f,%.3f],\"sink\":%llu}\n",tsc?"rdtscp":cpucycles_implementation(),reverse,C0,C1,C1-C0,(unsigned long long)sink);
    return 0;
}

