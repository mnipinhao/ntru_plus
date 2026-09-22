#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "inverse_tables.h"
void packed_i9(int16_t*,int16_t*,const int16_t*,const int16_t*);
void packed_i9_scatter(int16_t*,int16_t*,const int16_t*,const int16_t*);
typedef void (*K)(int16_t*,int16_t*,const int16_t*,const int16_t*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t scratch[896], in[864];
static const int SC[12]={0,64,256,320,512,576,4,68,260,324,516,580};   /* halfwords */
static const int TL[12]={768,832,769,833,770,834,771,835,772,836,773,837};
static const int IN[12]={0,24,8,32,16,40,432,456,440,464,448,472};
static const int TW[12]={0,144,0,144,0,144,288,432,288,432,288,432};
static int run(K k){ for(int i=0;i<12;i++)
    k(scratch+SC[i],scratch+TL[i],in+IN[i],&invntt9_constants[0][0][0][0][0]+TW[i]);
  return scratch[0]+scratch[800]; }
static int f0(void){return run(packed_i9);}
static int f1(void){return run(packed_i9_scatter);}
#define N 2000
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<864;i++) in[i]=(int16_t)((i*2654435761u)%5235)-2617;
  int (*F[2])(void)={f0,f1};
  const char*nm[2]={"現行 packed_i9 (24 store)","P95 所需的散射 (72 store)"};
  uint64_t wf=~0ull,best[2]={~0ull,~0ull},bw[2]={0,0};
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<2;i++) for(int k=0;k<N;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  enum {R=401}; static uint64_t dt[2][R], wt[2][R];
  for(int r=0;r<R;r++) for(int i=0;i<2;i++){
    uint64_t x=nsec(); for(int k=0;k<N;k++) sink+=F[i](); dt[i][r]=nsec()-x;
    wt[i][r]=witness(); if(wt[i][r]<wf) wf=wt[i][r]; }
  for(int i=0;i<2;i++) for(int r=0;r<R;r++)
    if(dt[i][r]<best[i]){best[i]=dt[i][r]; bw[i]=wt[i][r];}
  for(int i=0;i<2;i++) printf("  %-28s %7.1f ns / 12 calls   見證 %.2f%%\n",
      nm[i],(double)best[i]/N,100.0*(double)bw[i]/(double)wf);
  printf("  差: %+.1f ns (%+.2f%%)\n",((double)best[1]-(double)best[0])/N,
      100.0*((double)best[1]-(double)best[0])/(double)best[0]);
  return 0;}
