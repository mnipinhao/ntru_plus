#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
void f1600(uint64_t*, const uint64_t*);
void ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t*, const uint64_t*);  /* GT */
extern const uint64_t KeccakF_RoundConstants[];
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t st[25];
static uint64_t wit(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static int fa(void){ f1600(st, KeccakF_RoundConstants); return (int)st[0]; }
static int fb(void){ ntruplus_keccak_f1600_x1_v84a_aarch64(st, KeccakF_RoundConstants); return (int)st[0]; }
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  int (*F[2])(void)={fa,fb}; const char*nm[2]={"upstream CE f1600","GT keccakf1600_v84a"};
  uint64_t wf=~0ull,best[2]={~0ull,~0ull}; int acc[2]={0,0};
  uint64_t t0=nsec(); int s=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<2;i++) for(int k=0;k<20000;k++) sink+=F[i]();
    uint64_t d=wit(); if(d<wf){wf=d;s=0;} else s++;
    if(s>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<201;r++) for(int i=0;i<2;i++){
    uint64_t a=nsec(); for(int k=0;k<20000;k++) sink+=F[i](); uint64_t dt=nsec()-a;
    uint64_t d=wit(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  for(int i=0;i<2;i++) printf("  %-24s %6.1f ns/次  (%d/201)\n",nm[i],(double)best[i]/20000.0,acc[i]);
  return 0;}
