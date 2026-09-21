#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include <stddef.h>
#include "params.h"
void tobytes_full_asm(uint8_t*,const int16_t*);  void p87_tobytes_full(uint8_t*,const int16_t*);
void tobytes_small_asm(uint8_t*,const int16_t*); void p87_tobytes_small(uint8_t*,const int16_t*);
int  tobytes_compare_asm(const uint8_t*,const int16_t*); int p87_tobytes_compare(const uint8_t*,const int16_t*);
void off_tobytes(uint8_t*,const void*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t in[NTRUPLUS_N]; static uint8_t out[NTRUPLUS_POLYBYTES+64];
#define NF 9
static uint8_t tmp[NTRUPLUS_POLYBYTES+64];
static inline int verify(const uint8_t*a,const uint8_t*b,size_t n){uint8_t x=0;for(size_t i=0;i<n;i++)x|=(uint8_t)(a[i]^b[i]);return x!=0;}
static int f0(void){off_tobytes(out,in);return 0;}
static int f1(void){tobytes_full_asm(out,in);return 0;}  static int f2(void){p87_tobytes_full(out,in);return 0;}
static int f3(void){tobytes_small_asm(out,in);return 0;} static int f4(void){p87_tobytes_small(out,in);return 0;}
static int f5(void){return tobytes_compare_asm(out,in);} static int f6(void){return p87_tobytes_compare(out,in);}
static int f7(void){p87_tobytes_full(tmp,in);return verify(out,tmp,NTRUPLUS_POLYBYTES);}
static int f8(void){tobytes_full_asm(tmp,in);return verify(out,tmp,NTRUPLUS_POLYBYTES);}
static int (*F[NF])(void)={f0,f1,f2,f3,f4,f5,f6,f7,f8};
static const char*nm[NF]={"Official tobytes","GT asm tobytes_full","P87 tobytes_full",
  "GT asm tobytes_small","P87 tobytes_small","GT asm tobytes_compare","P87 tobytes_compare","P87 pack + verify","GT asm pack + verify"};
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
  for(int i=0;i<NF;i++) printf("  %-24s %7.1f ns  (%d/41)\n",nm[i],(double)best[i]/3000.0,acc[i]);
  return 0;}
