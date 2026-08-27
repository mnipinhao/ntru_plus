#include <stdint.h>
#include <stdio.h>
#include "candidate.h"
#include "internal.h"
static _Alignas(64) int16_t h[768],r[768],m[768],p[768],scratch[768];
static uint8_t wire[1152],pk[1152],coins[96],ct[1152],ss[32];static volatile uint64_t sink;static uint64_t st=7;
static uint32_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return st;}
static uint64_t tick(void){unsigned lo,hi;__asm__ volatile("lfence;rdtsc":"=a"(lo),"=d"(hi)::"memory");return ((uint64_t)hi<<32)|lo;}
static void init(void){for(int i=0;i<768;i++){h[i]=(int16_t)((int)(rnd()%3457)-1728);r[i]=(int16_t)((int)(rnd()%3457)-1728);m[i]=(int16_t)((int)(rnd()%21577)-10788);}for(int i=0;i<384;i++){uint16_t a=rnd()%3457,b=rnd()%3457;pk[3*i]=a;pk[3*i+1]=(uint8_t)((a>>8)|(b<<4));pk[3*i+2]=(uint8_t)(b>>4);}for(int i=0;i<96;i++)coins[i]=rnd();}
#define TIME(label,code) do{uint64_t z=tick();for(int j=0;j<64;j++){code;}uint64_t e=tick();printf(label " %llu\n",(unsigned long long)((e-z)/64));}while(0)
int main(void){init();for(int k=0;k<1024;k++){int rev=k&1;if(!rev){TIME("island control",gt103_basemul_general_ql2_avx2(p,h,r);gt103_pack_ql2_sum_avx2(wire,p,m);sink+=wire[0]);TIME("island candidate",gt105_b3_ql2_virtual_pack_direct_avx2(scratch,h,r,m,wire);sink+=wire[0]);TIME("encap control",ntruplus768_enc_derand_impl(ct,ss,pk,coins);sink+=ct[0]);TIME("encap candidate",gt105_encap_virtual_direct(ct,ss,pk,coins);sink+=ct[0]);}else{TIME("island candidate",gt105_b3_ql2_virtual_pack_direct_avx2(scratch,h,r,m,wire);sink+=wire[0]);TIME("island control",gt103_basemul_general_ql2_avx2(p,h,r);gt103_pack_ql2_sum_avx2(wire,p,m);sink+=wire[0]);TIME("encap candidate",gt105_encap_virtual_direct(ct,ss,pk,coins);sink+=ct[0]);TIME("encap control",ntruplus768_enc_derand_impl(ct,ss,pk,coins);sink+=ct[0]);}}fprintf(stderr,"sink=%llu\n",(unsigned long long)sink);}
