/* P29's three components against the five they replaced, one at a time.
 * IPC is what blocks P29 on A76 (1.41 against 1.93), so this localises it. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
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
void invntt16_paired_asm(int16_t*,int16_t*,long,const int16_t*,const int16_t*);
void paired_spill_asm(int16_t*,int16_t*,long,const int16_t*,const int16_t*);
void invntt_tail_direct_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt_route_asm(int16_t*,const int16_t*);
void route_nost3_asm(int16_t*,const int16_t*);
void route_wide_asm(int16_t*,const int16_t*);
void old_invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void old_invntt16_tail_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void crepmod3_ternary_asm(int16_t*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t out[1024], scr[1024];
static const int BASE[6]={0,12,1,13,2,14};
static int c_paired(void){ for(int i=0;i<3;i++)
  invntt16_paired_asm(scr+256*i,scr+256*i+128,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  return scr[0]; }
static int c_spill(void){ for(int i=0;i<3;i++)
  paired_spill_asm(scr+256*i,scr+256*i+128,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  return scr[0]; }
static int c_tail(void){ invntt_tail_direct_asm(out,scr+768,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]); return out[0]; }
static int c_route(void){ invntt_route_asm(out,scr); return out[0]; }
static int c_route_q(void){ route_nost3_asm(out,scr); return out[0]; }
static int c_route_w(void){ route_wide_asm(out,scr); return out[0]; }
static int o_main(void){ for(int i=0;i<9;i++)
  old_invntt16_asm(out+BASE[i],scr+128*i,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  return out[0]; }
static int o_tail(void){ old_invntt16_tail_asm(out+24,scr+768,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]); return out[0]; }
static int o_tern(void){ crepmod3_ternary_asm(out); return out[0]; }
typedef int(*F)(void);
static F FS[9]={c_paired,c_spill,c_tail,c_route,c_route_w,c_route_q,o_main,o_tail,o_tern};
static const char*NM[9]={"P29 paired x3","paired 堆疊溢出 x3","P29 tail_direct",
  "P29 route (64 ST3.4H)","route 寬化 (32 ST3.8H)","route 改 STR Q (定價)",
  "舊 invntt16 x6","舊 tail","舊 crepmod3"};
static const int INS[9]={3*844,3*838,850,938,874,938,6*660,592,0};
#define N 3000
int main(int argc,char**argv){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  if(argc>1){ int m=atoi(argv[1]); long n=argc>2?atol(argv[2]):20000;
    for(int i=0;i<1024;i++) scr[i]=(int16_t)((i*2654435761u)%5235)-2617;
    for(long k=0;k<n;k++){ if(m>=1&&m<=9) sink+=FS[m-1](); }
    return 0; }
  for(int i=0;i<1024;i++) scr[i]=(int16_t)((i*2654435761u)%5235)-2617;
  static uint64_t best[9]; for(int i=0;i<9;i++) best[i]=~0ull;
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<9;i++) for(int k=0;k<N;k++) sink+=FS[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++) for(int i=0;i<9;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=FS[i]();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[i]) best[i]=dt; }
  double gz=500000.0/(double)wf;
  printf("  時脈見證 %.3f GHz\n  %-18s%9s%9s%8s\n",gz,"","cycles","指令","IPC");
  for(int i=0;i<9;i++){ double c=(double)best[i]/N*gz;
    printf("  %-18s%9.0f%9d%8.2f\n",NM[i],c,INS[i],INS[i]?INS[i]/c:0.0); }
  return 0;}
