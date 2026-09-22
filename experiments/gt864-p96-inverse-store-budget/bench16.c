/* The six invntt16 calls as the driver issues them -- same output offsets, same
 * scratch stride, so the store pattern and its cache behaviour are the real
 * ones.  Warm-up is time-driven and the clock witness gates each batch; a
 * freshly woken thread sits in the E-cluster band for tens of milliseconds. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_st1_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_strq_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_lane_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
typedef void (*K)(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static int16_t out[896], scratch[896];
static const int BASE[6]={0,12,1,13,2,14};        /* halfwords, as inverse.S */
static int run(K k){
    for(int i=0;i<6;i++)
        k(out+BASE[i],scratch+128*i,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
    return out[0]+out[431];                        /* keep the stores live */
}
static int f0(void){return run(invntt16_asm);}
static int f1(void){return run(invntt16_st1_asm);}
/* Not wired to a repacked scratch, so its OUTPUT is wrong; it is here purely
 * to price 32 STR D against 128 STRH -- the same body, the same loads. */
static int f2(void){return run(invntt16_lane_asm);}
static int f3(void){return run(invntt16_strq_asm);}
#define N 2000
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<896;i++) scratch[i]=(int16_t)((i*2654435761u)%5235)-2617;
  int (*F[4])(void)={f0,f1,f2,f3};
  const char*nm[4]={"現行 128 umov+128 strh","128 st1 lane store","32 str d (P95 完整版)","16 str q (排版自由)"};
  uint64_t wf=~0ull,best[4]={~0ull,~0ull,~0ull,~0ull}; int acc[4]={0,0,0,0};
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<4;i++) for(int k=0;k<N;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  /* Collect first, gate afterwards: on a loaded machine the clock floor seen
   * during warm-up is not the floor of the measurement phase, so a gate fixed
   * up front can reject every round. */
  enum {R=401}; static uint64_t dt[4][R], wt[4][R];
  for(int r=0;r<R;r++) for(int i=0;i<4;i++){
    uint64_t x=nsec(); for(int k=0;k<N;k++) sink+=F[i](); dt[i][r]=nsec()-x;
    wt[i][r]=witness(); if(wt[i][r]<wf) wf=wt[i][r]; }
  /* Load is what the gate was rejecting, and load only ever adds time, so the
   * minimum batch is already the clean sample.  What has to be checked is that
   * the two minima were taken at the same clock: report each one's witness. */
  uint64_t bw[4]={0,0,0,0};
  for(int i=0;i<4;i++) for(int r=0;r<R;r++)
    if(dt[i][r]<best[i]){best[i]=dt[i][r]; bw[i]=wt[i][r]; acc[i]=r;}
  for(int i=0;i<4;i++) printf("  %-22s %7.1f ns / 6 calls   見證 %.3f ms (最佳的 %.2f%%)\n",
      nm[i],(double)best[i]/N,(double)bw[i]/1e6,100.0*(double)bw[i]/(double)wf);
  for(int i=1;i<4;i++) printf("  對現行的差: %+.1f ns (%+.2f%%)   %s\n",
      ((double)best[i]-(double)best[0])/N,
      100.0*((double)best[i]-(double)best[0])/(double)best[0], nm[i]);
  return 0;}
