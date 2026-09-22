/* NTRU+864's forward transform, GT against Official, both in place.
 *
 * P92/P93 compared GT's out-of-place poly_ntt(&c,&m) against Official's
 * c = m; o_poly_ntt(&c), so the official side paid a 1,728-byte copy it does
 * not pay in kem.c.  Both sides call poly_ntt exactly twice in every
 * operation and neither specialises it, so in-place against in-place is the
 * comparison that matches the code. */
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
void poly_ntt(poly*, const poly*);
void o_poly_ntt(poly*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static poly a, c;
static int k_gt_ip(void){ poly_ntt(&c,&c); return c.coeffs[0]; }
static int k_of_ip(void){ o_poly_ntt(&c);  return c.coeffs[0]; }
static int k_gt_oop(void){ poly_ntt(&c,&a); return c.coeffs[0]; }
static int k_of_cp(void){ c=a; o_poly_ntt(&c); return c.coeffs[0]; }
static int k_copy(void){ c=a; return c.coeffs[0]; }
typedef struct { const char *n; int (*f)(void); } Case;
static Case CS[] = {
  {"GT poly_ntt  (in place)",        k_gt_ip},
  {"Official poly_ntt  (in place)",  k_of_ip},
  {"GT poly_ntt  (out of place)",    k_gt_oop},
  {"Official  複製 + in place",      k_of_cp},
  {"poly 複製本身 (1728 B)",         k_copy},
};
#define NC ((int)(sizeof CS/sizeof*CS))
#define N 3000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(int i=0;i<NTRUPLUS_N;i++){ a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
                                 c.coeffs[i]=a.coeffs[i]; }
  static uint64_t best[NC]; for(int i=0;i<NC;i++) best[i]=~0ull;
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NC;i++) for(int k=0;k<N;k++) sink+=CS[i].f();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++) for(int i=0;i<NC;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=CS[i].f();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[i]) best[i]=dt; }
  double gz=500000.0/(double)wf;
  printf("  時脈見證: %.3f GHz\n\n  %-32s%9s%9s\n", gz, "", "ns", "cycles");
  for(int i=0;i<NC;i++) printf("  %-32s%9.1f%9.0f\n",
      CS[i].n,(double)best[i]/N,(double)best[i]/N*gz);
  double g=(double)best[0]/N, o=(double)best[1]/N;
  printf("\n  就地對就地: GT/Official = %.3f, 每次呼叫 %+.1f ns (%+.0f cyc)\n",
         g/o, g-o, (g-o)*gz);
  printf("  每個操作呼叫兩次: %+.1f ns (%+.0f cyc)\n", 2*(g-o), 2*(g-o)*gz);
  return 0;}
