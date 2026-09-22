#include <stdio.h>
#include <stdint.h>
#include <time.h>
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
#else
static inline uint64_t ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
#endif
void repack_asm(int16_t*,const int16_t*,const int16_t*);
void repack_tbl_asm(int16_t*,const int16_t*,const int16_t*);
void repack_strq_asm(int16_t*,const int16_t*,const int16_t*);
typedef void(*K)(int16_t*,const int16_t*,const int16_t*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t nat[864], mn[768], tl[96];
static K KS[3]={repack_asm,repack_tbl_asm,repack_strq_asm};
static const char*NM[3]={"st3 交錯","tbl 交錯 + str q","不交錯 (定價 st3 本身)"};
static int kk;
static int f(void){ KS[kk](nat,mn,tl); return nat[0]+nat[863]; }
#define N 4000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(int i=0;i<768;i++) mn[i]=(int16_t)i; for(int i=0;i<96;i++) tl[i]=(int16_t)i;
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(kk=0;kk<3;kk++) for(int k=0;k<N;k++) sink+=f();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=401}; uint64_t best[3]={~0ull,~0ull,~0ull},bw[3]={0,0,0};
  for(int r=0;r<R;r++) for(kk=0;kk<3;kk++){ uint64_t x=ns();
    for(int k=0;k<N;k++) sink+=f();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[kk]){best[kk]=dt; bw[kk]=d;} }
  for(int i=0;i<3;i++) printf("  %-26s %6.1f ns   見證 %.2f%%\n",
     NM[i],(double)best[i]/N,100.0*(double)bw[i]/(double)wf);
  return 0;}
