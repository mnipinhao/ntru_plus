#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
void tobytes_full_asm(uint8_t*,const int16_t*); void old_tobytes_full(uint8_t*,const int16_t*);
void tobytes_small_asm(uint8_t*,const int16_t*); void old_tobytes_small(uint8_t*,const int16_t*);
int tobytes_compare_asm(const uint8_t*,const int16_t*); int old_tobytes_compare(const uint8_t*,const int16_t*);
int frombytes_asm(int16_t*,const uint8_t*); int old_frombytes(int16_t*,const uint8_t*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t in[NTRUPLUS_N],dec[NTRUPLUS_N+32]; static uint8_t out[NTRUPLUS_POLYBYTES+64];
#define NF 8
static int a0(void){old_tobytes_full(out,in);return 0;}  static int b0(void){tobytes_full_asm(out,in);return 0;}
static int a1(void){old_tobytes_small(out,in);return 0;} static int b1(void){tobytes_small_asm(out,in);return 0;}
static int a2(void){return old_tobytes_compare(out,in);} static int b2(void){return tobytes_compare_asm(out,in);}
static int a3(void){return old_frombytes(dec,out);}      static int b3(void){return frombytes_asm(dec,out);}
static int (*F[NF])(void)={a0,b0,a1,b1,a2,b2,a3,b3};
static const char*nm[NF]={"舊 tobytes_full","新 tobytes_full","舊 tobytes_small","新 tobytes_small",
  "舊 tobytes_compare","新 tobytes_compare","舊 frombytes","新 frombytes"};
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<NTRUPLUS_N;i++) in[i]=(int16_t)((i*2654435761u)%3457);
  tobytes_full_asm(out,in);
  uint64_t wf=~0ull,best[NF]; int acc[NF];
  for(int i=0;i<NF;i++){best[i]=~0ull;acc[i]=0;}
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NF;i++) for(int k=0;k<3000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<41;r++) for(int i=0;i<NF;i++){
    uint64_t a=nsec(); for(int k=0;k<3000;k++) sink+=F[i](); uint64_t dt=nsec()-a;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  for(int i=0;i<NF;i+=2)
    printf("  %-20s %7.1f  ->  %-18s %7.1f   %+6.1f ns\n",nm[i],(double)best[i]/3000.0,nm[i+1],(double)best[i+1]/3000.0,
           ((double)best[i+1]-(double)best[i])/3000.0);
  return 0;}
