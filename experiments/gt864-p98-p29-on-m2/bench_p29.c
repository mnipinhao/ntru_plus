/* Production's main+tail+ternary against P29's paired main + direct tail +
 * ST3 route, on M2.  Values are not meaningful here -- the buffers are
 * plausible but unseeded by a real inverse9 -- only the instruction mix and
 * the memory traffic are, and neither kernel is data-dependent.  P29 was
 * rejected on A76 at +76.8 cycles; this asks what it is worth where stores
 * cost and instructions do not. */
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
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_tail_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void crepmod3_ternary_asm(int16_t*);
void p28_paired_i16(int16_t*,int16_t*,long,const int16_t*,const int16_t*);
void p29_tail_direct(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void p29_main_route(int16_t*,const int16_t*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t out[1024], scr[1024];
static const int BASE[6]={0,12,1,13,2,14};
static int prod(void){
  for(int i=0;i<6;i++)
    invntt16_asm(out+BASE[i],scr+128*i,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  invntt16_tail_asm(out+24,scr+768,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
  crepmod3_ternary_asm(out);
  return out[0]+out[863];
}
static int p29(void){
  for(int i=0;i<3;i++)
    p28_paired_i16(scr+256*i,scr+256*i+128,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  p29_tail_direct(out,scr+768,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
  p29_main_route(out,scr);
  return out[0]+out[863];
}
static int kk; static int f(void){ return kk?p29():prod(); }
#define N 2000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(int i=0;i<1024;i++) scr[i]=(int16_t)((i*2654435761u)%5235)-2617;
  const char*NM[2]={"production main+tail+ternary","P29 paired+direct+ST3 route"};
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(kk=0;kk<2;kk++) for(int k=0;k<N;k++) sink+=f();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=401}; uint64_t best[2]={~0ull,~0ull},bw[2]={0,0};
  for(int r=0;r<R;r++) for(kk=0;kk<2;kk++){ uint64_t x=ns();
    for(int k=0;k<N;k++) sink+=f();
    uint64_t dt=ns()-x,d=witness(); if(d<wf) wf=d;
    if(dt<best[kk]){best[kk]=dt; bw[kk]=d;} }
  for(int i=0;i<2;i++) printf("  %-30s %7.1f ns   見證 %.2f%%\n",
     NM[i],(double)best[i]/N,100.0*(double)bw[i]/(double)wf);
  printf("  差: %+.1f ns (%+.2f%%)\n",((double)best[1]-(double)best[0])/N,
     100.0*((double)best[1]-(double)best[0])/(double)best[0]);
  return 0;}
