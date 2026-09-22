/* poly_frombytes at 1152: current, fully unrolled, and Official's. */
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
int frombytes_asm(int16_t*, const uint8_t*);
int u_frombytes_asm(int16_t*, const uint8_t*);
int o_poly_frombytes(poly*, const uint8_t*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static poly p, q; static uint8_t buf[NTRUPLUS_POLYBYTES+64];
static int f0(void){return frombytes_asm(p.coeffs,buf)+p.coeffs[0];}
static int f1(void){return u_frombytes_asm(q.coeffs,buf)+q.coeffs[0];}
static int f2(void){return o_poly_frombytes(&p,buf)+p.coeffs[0];}
typedef int(*F)(void);
static F FS[3]={f0,f1,f2};
static const char*NM[3]={"GT 現行","GT 樹狀歸約","Official"};
#define N 4000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)(i*211u);
  /* the two GT forms must agree, bit for bit, and on the range verdict */
  int r0=frombytes_asm(p.coeffs,buf), r1=u_frombytes_asm(q.coeffs,buf);
  if(r0!=r1 || memcmp(p.coeffs,q.coeffs,sizeof p.coeffs)){
    puts("  展開版與現行版輸出不同!"); return 1; }
  for(int t=0;t<64;t++){
    for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)((i*167u)^(t*97u));
    r0=frombytes_asm(p.coeffs,buf); r1=u_frombytes_asm(q.coeffs,buf);
    if(r0!=r1 || memcmp(p.coeffs,q.coeffs,sizeof p.coeffs)){
      printf("  第 %d 組輸入不一致!\n",t); return 1; }
  }
  puts("  65 組輸入下兩個 GT 版本位元相同, 範圍判定相同");
  static uint64_t best[3]={~0ull,~0ull,~0ull};
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<3;i++) for(int k=0;k<N;k++) sink+=FS[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++) for(int i=0;i<3;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=FS[i]();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[i]) best[i]=dt; }
  double gz=500000.0/(double)wf;
  printf("\n  時脈見證 %.3f GHz\n  %-14s%9s%9s%8s\n", gz, "", "ns", "cycles", "對 Off");
  for(int i=0;i<3;i++) printf("  %-14s%9.1f%9.0f%8.2f\n",NM[i],(double)best[i]/N,
      (double)best[i]/N*gz,(double)best[i]/(double)best[2]);
  printf("  展開對現行: %+.0f cyc (%+.1f%%), decap 呼叫三次 = %+.0f cyc\n",
     ((double)best[1]-(double)best[0])/N*gz,
     100.0*((double)best[1]-(double)best[0])/(double)best[0],
     3*((double)best[1]-(double)best[0])/N*gz);
  return 0;}
