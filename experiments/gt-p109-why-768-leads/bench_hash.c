/* hash_f, hash_g, hash_h -- GT against Official, same sizes, same data. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
void hash_f(uint8_t*, const uint8_t*);   void o_hash_f(uint8_t*, const uint8_t*);
void hash_g(uint8_t*, const uint8_t*);   void o_hash_g(uint8_t*, const uint8_t*);
void hash_h(uint8_t*, const uint8_t*);   void o_hash_h(uint8_t*, const uint8_t*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
/* kem.c's own sizes: hash_f and hash_g read a public key (POLYBYTES), hash_h
 * reads N/8 + SYMBYTES.  Outputs are 32, N/4 and SYMBYTES + N/4. */
static uint8_t pk[NTRUPLUS_POLYBYTES+64];
static uint8_t msg[NTRUPLUS_N/8+NTRUPLUS_SYMBYTES+64];
static uint8_t out[NTRUPLUS_SYMBYTES+NTRUPLUS_N/4+NTRUPLUS_POLYBYTES+64];
static int g0(void){hash_f(out,pk);return out[0];}  static int o0(void){o_hash_f(out,pk);return out[0];}
static int g1(void){hash_g(out,pk);return out[0];}  static int o1(void){o_hash_g(out,pk);return out[0];}
static int g2(void){hash_h(out,msg);return out[0];}  static int o2(void){o_hash_h(out,msg);return out[0];}
typedef int(*F)(void);
static F GS[3]={g0,g1,g2}, OS[3]={o0,o1,o2};
static const char*NM[3]={"hash_f","hash_g","hash_h"};
#define N 3000
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)(i*167u);
  for(size_t i=0;i<sizeof pk;i++)  pk[i]=(uint8_t)(i*211u);
  uint64_t bg[3],bo[3],wf=~0ull; for(int i=0;i<3;i++){bg[i]=~0ull;bo[i]=~0ull;}
  uint64_t t0=ns(); int s=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<3;i++){for(int k=0;k<N;k++) sink+=GS[i]();
      for(int k=0;k<N;k++) sink+=OS[i]();}
    uint64_t d=witness(); if(d<wf){wf=d;s=0;} else s++;
    if(s>=5 && ns()-t0>3000000000ull) break; }
  for(int r=0;r<301;r++) for(int i=0;i<3;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=GS[i](); uint64_t d1=ns()-x;
    x=ns(); for(int k=0;k<N;k++) sink+=OS[i](); uint64_t d2=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d1<bg[i]) bg[i]=d1; if(d2<bo[i]) bo[i]=d2; }
  printf("  N=%d  %-10s%9s%9s%8s\n",NTRUPLUS_N,"","GT","Official","比");
  for(int i=0;i<3;i++) printf("  %-16s%9.1f%9.1f%8.2f\n",NM[i],
     (double)bg[i]/N,(double)bo[i]/N,(double)bg[i]/(double)bo[i]);
  return 0;}
