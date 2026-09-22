/* The three trees' Keccak permutations, and upstream's CE one, side by side. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
void g768_ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t*, const uint64_t*);
void g864_ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t*, const uint64_t*);
void g1152_ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t*, const uint64_t*);
void f1600(uint64_t*, const uint64_t*);
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
typedef void (*P)(uint64_t*, const uint64_t*);
static P PS[4]={g768_ntruplus_keccak_f1600_x1_v84a_aarch64,
                g864_ntruplus_keccak_f1600_x1_v84a_aarch64,
                g1152_ntruplus_keccak_f1600_x1_v84a_aarch64, f1600};
static const char*NM[4]={"GT 768 v84a","GT 864 v84a","GT 1152 v84a","upstream CE f1600"};
static int which;
static int run(void){ PS[which](st,RC); return (int)st[0]; }
#define N 5000
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  /* all four must agree on one permutation of the same state */
  static uint64_t ref[25], t[25];
  for(int i=0;i<25;i++) ref[i]=i*0x9E3779B97F4A7C15ULL;
  uint64_t out[4][25];
  for(int i=0;i<4;i++){ memcpy(t,ref,sizeof t); PS[i](t,RC); memcpy(out[i],t,sizeof t); }
  int same=1; for(int i=1;i<4;i++) if(memcmp(out[0],out[i],sizeof ref)) same=0;
  printf("  四個置換輸出一致: %s\n\n", same?"是":"否");
  memcpy(st,ref,sizeof st);
  static uint64_t best[4]; for(int i=0;i<4;i++) best[i]=~0ull;
  uint64_t wf=~0ull,t0=ns(); int s=0;
  for(int w=0;w<4000;w++){ for(which=0;which<4;which++) for(int k=0;k<N;k++) sink+=run();
    uint64_t d=witness(); if(d<wf){wf=d;s=0;} else s++;
    if(s>=5 && ns()-t0>3000000000ull) break; }
  for(int r=0;r<301;r++) for(which=0;which<4;which++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=run();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[which]) best[which]=dt; }
  for(int i=0;i<4;i++) printf("  %-20s %6.2f ns\n",NM[i],(double)best[i]/N);
  return 0;}
