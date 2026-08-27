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
static _Alignas(64) int16_t coeff[768],front[768],m[768],ql2[768],h[768],r[768],out[768];
static _Alignas(64) uint8_t wire[1152],pk[1152],coins[96],ct[1152],ss[32];
static uint64_t rs=UINT64_C(0x10355aa55aa55aa5);
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return (uint32_t)rs;}
static uint64_t ticks(void){unsigned a;_mm_lfence();uint64_t x=__rdtscp(&a);_mm_lfence();return x;}
static uint64_t now(int tsc){return tsc?ticks():(uint64_t)cpucycles();}
static int cmp(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return(x>y)-(x<y);}
static double med(double*x){qsort(x,S,sizeof*x,cmp);return x[S/2];}
static void pin(void){cpu_set_t s;CPU_ZERO(&s);CPU_SET(1,&s);(void)sched_setaffinity(0,sizeof s,&s);}
static void pairpk(void){for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;pk[3*i]=x;pk[3*i+1]=(uint8_t)((x>>8)|(y<<4));pk[3*i+2]=(uint8_t)(y>>4);}}
static void init(void){for(int i=0;i<768;i++){coeff[i]=(int16_t)((int)(rnd()%3457)-1728);h[i]=(int16_t)((int)(rnd()%3457)-1728);r[i]=(int16_t)((int)(rnd()%3457)-1728);}ntruplus768_ntt_frontend_avx2(front,coeff);ntruplus768_ntt_m_avx2(m,front);gt103_ntt_ql2_avx2(ql2,front);pairpk();for(int i=0;i<96;i++)coins[i]=(uint8_t)rnd();}
static void island0(void){ntruplus768_ntt_frontend_avx2(front,coeff);ntruplus768_ntt_m_avx2(m,front);ntruplus768_basemul_general_m_avx2(out,h,r);ntruplus768_pack_m_sum_highrange12699_avx2(wire,out,m);sink+=wire[0];}
static void island1(void){ntruplus768_ntt_frontend_avx2(front,coeff);gt103_ntt_ql2_avx2(ql2,front);gt103_basemul_general_ql2_avx2(out,h,r);gt103_pack_ql2_sum_avx2(wire,out,ql2);sink+=wire[0];}

int main(int argc,char**argv)
{
  int reverse=argc>1?atoi(argv[1]):0,tsc=argc>2?atoi(argv[2]):0,full=argc>3?atoi(argv[3]):0;pin();init();
  double f0[S],f1[S],b0[S],b1[S],q0[S],q1[S],i0[S],i1[S],e0[S]={0},e1[S]={0},x0[S]={0},x1[S]={0};
  for(int s=0;s<S;s++){
    int first=(s+reverse)&1;uint64_t x,y;unsigned I=256;
#define TIME(dst,code) do{x=now(tsc);for(unsigned z=0;z<I;z++){code;sink+=(uint16_t)out[z%768];}y=now(tsc);dst[s]=(double)(y-x)/I;}while(0)
    if(!first){TIME(f0,ntruplus768_ntt_m_avx2(out,front));TIME(f1,gt103_ntt_ql2_avx2(out,front));}else{TIME(f1,gt103_ntt_ql2_avx2(out,front));TIME(f0,ntruplus768_ntt_m_avx2(out,front));}
    if(!first){TIME(b0,ntruplus768_basemul_general_m_avx2(out,h,r));TIME(b1,gt103_basemul_general_ql2_avx2(out,h,r));}else{TIME(b1,gt103_basemul_general_ql2_avx2(out,h,r));TIME(b0,ntruplus768_basemul_general_m_avx2(out,h,r));}
    if(!first){TIME(q0,ntruplus768_pack_m_sum_highrange12699_avx2(wire,m,m));TIME(q1,gt103_pack_ql2_sum_avx2(wire,ql2,ql2));}else{TIME(q1,gt103_pack_ql2_sum_avx2(wire,ql2,ql2));TIME(q0,ntruplus768_pack_m_sum_highrange12699_avx2(wire,m,m));}
#undef TIME
    I=64;
#define TIMEI(dst,fn) do{x=now(tsc);for(unsigned z=0;z<I;z++)fn();y=now(tsc);dst[s]=(double)(y-x)/I;}while(0)
    if(!first){TIMEI(i0,island0);TIMEI(i1,island1);}else{TIMEI(i1,island1);TIMEI(i0,island0);}
#undef TIMEI
    if(full){I=16;
#define TIMEE(dst,code) do{x=now(tsc);for(unsigned z=0;z<I;z++){if((code)!=0)return 2;sink+=ct[z%1152]+ss[z%32];}y=now(tsc);dst[s]=(double)(y-x)/I;}while(0)
      if(!first){TIMEE(e0,ntruplus768_enc_derand_impl(ct,ss,pk,coins));TIMEE(e1,gt103_encap_ql2(ct,ss,pk,coins));}else{TIMEE(e1,gt103_encap_ql2(ct,ss,pk,coins));TIMEE(e0,ntruplus768_enc_derand_impl(ct,ss,pk,coins));}
      if(!first){TIMEE(x0,gt103_encap_matched_control(ct,ss,pk,coins));TIMEE(x1,gt103_encap_matched_candidate(ct,ss,pk,coins));}else{TIMEE(x1,gt103_encap_matched_candidate(ct,ss,pk,coins));TIMEE(x0,gt103_encap_matched_control(ct,ss,pk,coins));}
#undef TIMEE
    }
  }
#define TRIPLE(name,a,b) med(a),med(b),med(b)-med(a)
  printf("{\"backend\":\"%s\",\"reverse\":%d,\"full\":%d,\"forward\":[%.3f,%.3f,%.3f],\"b3\":[%.3f,%.3f,%.3f],\"q24\":[%.3f,%.3f,%.3f],\"island\":[%.3f,%.3f,%.3f],\"encap\":[%.3f,%.3f,%.3f],\"encap_matched\":[%.3f,%.3f,%.3f],\"sink\":%llu}\n",tsc?"rdtscp":cpucycles_implementation(),reverse,full,TRIPLE("f",f0,f1),TRIPLE("b",b0,b1),TRIPLE("q",q0,q1),TRIPLE("i",i0,i1),TRIPLE("e",e0,e1),TRIPLE("x",x0,x1),(unsigned long long)sink);
  return 0;
}
