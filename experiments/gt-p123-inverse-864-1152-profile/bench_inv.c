/* The complete inverse-to-ternary, GT against Official, as kem.c calls it.
 *   768   poly_invntt_decap_scale (in place) then poly_crepmod3
 *   864   poly_invntt_ternary, which folds the reduction in
 *   1152  the same
 *   Official (all three)  poly_invntt_scale then poly_crepmod3, both in place
 * Nothing copies: kem.c calls every one of these in place. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
#else
static inline uint64_t ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
#endif
#include "params.h"
#include "poly.h"
#if NTRUPLUS_N == 768
void poly_invntt_decap_scale(poly*);
void poly_crepmod3(poly*, const poly*);
/* 768 has no generic forward entry; decapsulation's is poly_ntt_decap */
void poly_ntt_decap(poly*, const poly*);
#define poly_ntt poly_ntt_decap
static int gt(poly *c){ poly_invntt_decap_scale(c); poly_crepmod3(c,c); return c->coeffs[0]; }
#else
void poly_invntt_ternary(poly*, const poly*);
void poly_ntt(poly*, const poly*);
static int gt(poly *c){ poly_invntt_ternary(c,c); return c->coeffs[0]; }
#endif
void o_poly_invntt_scale(poly*);
void o_poly_crepmod3(poly*);
void o_poly_ntt(poly*);
static int off(poly *c){ o_poly_invntt_scale(c); o_poly_crepmod3(c); return c->coeffs[0]; }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static poly g, o;
static int f0(void){ return gt(&g); }
static int f1(void){ return off(&o); }
#define N 3000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  /* each side starts from its own forward transform's output */
  for(int i=0;i<NTRUPLUS_N;i++) g.coeffs[i]=(int16_t)((i*2654435761u)%3)-1;
  o = g; poly_ntt(&g,&g); o_poly_ntt(&o);
  int (*F[2])(void)={f0,f1};
  uint64_t best[2]={~0ull,~0ull},wf=~0ull,t0=ns(); int s=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<2;i++) for(int k=0;k<N;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;s=0;} else s++;
    if(s>=5 && ns()-t0>3000000000ull) break; }
  for(int r=0;r<301;r++) for(int i=0;i<2;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=F[i](); uint64_t dt=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(dt<best[i]) best[i]=dt; }
  double gz=500000.0/(double)wf;
  double a=(double)best[0]/N, b=(double)best[1]/N;
  printf("  N=%-5d GT %7.1f ns (%5.0f cyc)   Official %7.1f ns (%5.0f cyc)   x %.3f   %+6.1f ns\n",
         NTRUPLUS_N, a, a*gz, b, b*gz, a/b, a-b);
  return 0;}
