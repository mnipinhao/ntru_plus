#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include "params.h"
void tobytes_full_asm(uint8_t*,const int16_t*);
int  tobytes_compare_asm(const uint8_t*,const int16_t*);
static inline uint64_t nsec(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
static inline int verify(const uint8_t*a,const uint8_t*b,size_t n){
 uint8_t x=0; for(size_t i=0;i<n;i++) x|=(uint8_t)(a[i]^b[i]); return x!=0;}
static int16_t in[NTRUPLUS_N]; static uint8_t o1[NTRUPLUS_POLYBYTES+64],o2[NTRUPLUS_POLYBYTES+64];
static volatile unsigned sink;
#define T(lab,expr) do{uint64_t b=~0ull; for(int r=0;r<41;r++){uint64_t a=nsec(); \
  for(int k=0;k<3000;k++){sink+=(expr);} uint64_t d=nsec()-a; if(d<b)b=d;} \
  printf("  %-22s %7.1f ns\n",lab,(double)b/3000.0);}while(0)
int main(void){
  for(int i=0;i<NTRUPLUS_N;i++) in[i]=(int16_t)((i*2654435761u)%3457);
  tobytes_full_asm(o1,in);
  for(int w=0;w<200;w++){tobytes_full_asm(o2,in); sink+=verify(o1,o2,NTRUPLUS_POLYBYTES); sink+=tobytes_compare_asm(o1,in);}
  T("tobytes_full",        (tobytes_full_asm(o2,in),0));
  T("verify",              verify(o1,o2,NTRUPLUS_POLYBYTES));
  T("tobytes+verify",      (tobytes_full_asm(o2,in),verify(o1,o2,NTRUPLUS_POLYBYTES)));
  T("fused compare",       tobytes_compare_asm(o1,in));
  return 0;}
