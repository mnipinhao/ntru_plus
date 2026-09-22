/* Three Keccak-f1600 permutations, head to head, same signature (state, rc). */
#include <stdio.h>
#include <stdint.h>
#include <pthread.h>
#include <sys/qos.h>
#include <time.h>
extern void ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t*, const uint64_t*);
extern void up_new_f1600(uint64_t*, const uint64_t*);
extern void up_old_f1600(uint64_t*, const uint64_t*);
static const uint64_t RC[24]={
 0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
 0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,
 0x000000000000008aULL,0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,
 0x000000008000808bULL,0x800000000000008bULL,0x8000000000008089ULL,0x8000000000008003ULL,
 0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,0x800000008000000aULL,
 0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
static inline uint64_t nsec(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
static volatile uint64_t sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=x; return d?d:1;}
static uint64_t st[25];
static uint64_t f0(void){ntruplus_keccak_f1600_x1_v84a_aarch64(st,RC);return st[0];}
static uint64_t f1(void){up_new_f1600(st,RC);return st[0];}
static uint64_t f2(void){up_old_f1600(st,RC);return st[0];}
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  /* correctness: all three must agree */
  uint64_t r[3][25];
  uint64_t (*F[3])(void)={f0,f1,f2};
  const char*nm[3]={"ours  keccakf1600_v84a.S","upstream CE/f1600.S (2026-08)","upstream CE/f1600.S (3月版+補丁)"};
  for(int i=0;i<3;i++){for(int k=0;k<25;k++) st[k]=k*0x0123456789abcdefULL; F[i]();
    for(int k=0;k<25;k++) r[i][k]=st[k];}
  int ok=1; for(int i=1;i<3;i++) for(int k=0;k<25;k++) if(r[i][k]!=r[0][k]) ok=0;
  printf("  三者輸出一致: %s\n\n", ok?"是":"否 <<< 有問題");
  uint64_t wf=~0ull,best[3]={~0ull,~0ull,~0ull}; int acc[3]={0,0,0};
  uint64_t t0=nsec(); int stall=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<3;i++) for(int k=0;k<4000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;stall=0;} else stall++;
    if(stall>=5 && nsec()-t0>3000000000ull) break; }
  for(int rr=0;rr<201;rr++) for(int i=0;i<3;i++){
    uint64_t x=nsec(); for(int k=0;k<4000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  double b0=(double)best[0]/4000.0;
  for(int i=0;i<3;i++){double v=(double)best[i]/4000.0;
    printf("  %-34s %7.2f ns  (%5.3f x ours)  [%d/201]\n",nm[i],v,v/b0,acc[i]);}
  return 0;}
