#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
void poly_invntt_ternary(poly*, const poly*);
void off_invntt(void*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly a,b,c;
static int f0(void){ poly_invntt_ternary(&b,&a); return b.coeffs[0]; }
static int f1(void){ c=a; off_invntt(&c); return c.coeffs[0]; }
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<NTRUPLUS_N;i++) a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
  int (*F[2])(void)={f0,f1}; const char*nm[2]={"GT poly_invntt_ternary","Official poly_invntt_scale(+copy)"};
  uint64_t wf=~0ull,best[2]={~0ull,~0ull}; int acc[2]={0,0};
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<2;i++) for(int k=0;k<3000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<41;r++) for(int i=0;i<2;i++){
    uint64_t x=nsec(); for(int k=0;k<3000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  for(int i=0;i<2;i++) printf("  %-34s %7.1f ns  (%d/41)\n",nm[i],(double)best[i]/3000.0,acc[i]);
  return 0;}
