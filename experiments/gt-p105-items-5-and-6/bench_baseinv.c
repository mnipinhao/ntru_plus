/* Item 6: NTRU+864's baseinv, GT against Official.  Both keygen paths call it
 * twice, on f and on g, and both are out-of-place (poly *out, const poly *in),
 * so there is no copy to get wrong this time. */
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
int poly_baseinv(poly*, const poly*);
int o_poly_baseinv(poly*, const poly*);
void poly_ntt(poly*, const poly*);
void o_poly_ntt(poly*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
/* each side gets input in its own basis: its own forward transform's output */
static poly a,ao,b;
static int g0(void){return poly_baseinv(&b,&a)+b.coeffs[0];}
static int o0(void){return o_poly_baseinv(&b,&ao)+b.coeffs[0];}
#define N 3000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  /* a must be an NTT-domain polynomial with invertible base elements: take a
   * random ternary poly through GT's own forward transform */
  for(int i=0;i<NTRUPLUS_N;i++) a.coeffs[i]=(int16_t)((i*2654435761u)%3)-1;
  ao=a; poly_ntt(&a,&a); o_poly_ntt(&ao);
  int rg=poly_baseinv(&b,&a); poly bg=b;
  int ro=o_poly_baseinv(&b,&ao);
  printf("  可逆性回傳值 GT=%d Official=%d  (0 = 可逆)\n",rg,ro);
  int same=!memcmp(&bg,&b,sizeof b);
  printf("  兩邊輸出相同: %s\n", same?"是":"否（不同基底表示，僅比較成本）");
  uint64_t bgst=~0ull,bost=~0ull,wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int k=0;k<N;k++) sink+=g0();
    for(int k=0;k<N;k++) sink+=o0();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=g0(); uint64_t d1=ns()-x;
    x=ns(); for(int k=0;k<N;k++) sink+=o0(); uint64_t d2=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d1<bgst) bgst=d1; if(d2<bost) bost=d2; }
  double gz=500000.0/(double)wf, g=(double)bgst/N*gz, o=(double)bost/N*gz;
  printf("\n  時脈見證 %.3f GHz\n  GT %.0f cyc, Official %.0f cyc, 比 %.2f\n",gz,g,o,g/o);
  printf("  keygen 呼叫兩次: %+.0f cyc (%+.1f ns)\n",2*(g-o),2*(g-o)/gz);
  return 0;}
