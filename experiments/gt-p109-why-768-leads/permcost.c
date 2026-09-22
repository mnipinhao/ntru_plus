/* One Keccak permutation, both backends, on the same data. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
extern void f1600(uint64_t*, const uint64_t*);
extern void ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t*, const uint64_t*);
static const uint64_t RC[24]={
 0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
 0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,
 0x000000000000008aULL,0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,
 0x000000008000808bULL,0x800000000000008bULL,0x8000000000008089ULL,0x8000000000008003ULL,
 0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,0x800000008000000aULL,
 0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static uint64_t st[25];
static int f0(void){ f1600(st,RC); return (int)st[0]; }
static int f1(void){ ntruplus_keccak_f1600_x1_v84a_aarch64(st,RC); return (int)st[0]; }
#define N 5000
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<25;i++) st[i]=i*0x9E3779B97F4A7C15ULL;
  int (*F[2])(void)={f0,f1}; const char*NM[2]={"upstream CE f1600","GT keccakf1600_v84a"};
  uint64_t best[2]={~0ull,~0ull},wf=~0ull,t0=ns(); int s=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<2;i++) for(int k=0;k<N;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;s=0;} else s++;
    if(s>=5 && ns()-t0>3000000000ull) break; }
  for(int r=0;r<301;r++) for(int i=0;i<2;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=F[i](); uint64_t dt=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(dt<best[i]) best[i]=dt; }
  for(int i=0;i<2;i++) printf("  %-22s %6.2f ns\n",NM[i],(double)best[i]/N);
  return 0;}
