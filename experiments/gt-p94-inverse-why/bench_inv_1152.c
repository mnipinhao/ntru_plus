#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
void poly_invntt_ternary(poly*, const poly*);
void o_poly_invntt_scale(poly*);
void o_poly_crepmod3(poly*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly a,b;
static int k0(void){poly_invntt_ternary(&b,&a);return b.coeffs[0];}
static int k1(void){b=a; o_poly_invntt_scale(&b); o_poly_crepmod3(&b); return b.coeffs[0];}
static int k2(void){b=a; return b.coeffs[0];}
static int (*F[3])(void)={k0,k1,k2};
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<NTRUPLUS_N;i++) a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
  uint64_t wf=~0ull,best[3]={~0ull,~0ull,~0ull}; int acc[3]={0,0,0};
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<3;i++) for(int k=0;k<2000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<201;r++) for(int i=0;i<3;i++){
    uint64_t x=nsec(); for(int k=0;k<2000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  double G=(double)best[0]/2000,O=(double)best[1]/2000,C=(double)best[2]/2000;
  printf("  GT invntt_ternary        %7.1f ns  (%.3f ns/係數)\n",G,G/NTRUPLUS_N);
  printf("  Official invntt+crepmod3 %7.1f ns  扣複製 %.1f → %7.1f  (%.3f ns/係數)\n",O,C,O-C,(O-C)/NTRUPLUS_N);
  printf("  → GT / Official = %.2fx\n",G/(O-C));
  return 0;}
