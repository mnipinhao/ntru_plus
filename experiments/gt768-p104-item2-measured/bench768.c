#include "layout.h"
/* NTRU+768's serialization, GT against Official, in cycles.
 * 768 is the one set whose pack is still hand-written assembly (pack.S, 2,232
 * instructions); 864 and 1152 replaced theirs with C intrinsics in P87/P86 and
 * the C won.  Roadmap item 2 says +109 ns on encapsulation and +69 on key
 * generation, from the sampling profiler, which has been wrong by 2x twice. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
#else
static inline uint64_t ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
#endif
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
#include "keygen.h"
#include "ntt.h"
int  poly_frombytes_encap(poly*, const uint8_t*);
int  poly_frombytes_decap(poly*, const uint8_t*);
void poly_tobytes_encap_loose(uint8_t*, const poly*);
void poly_tobytes_encap(uint8_t*, const poly*);
void poly_tobytes_decap(uint8_t*, const poly*);
void poly_tobytes_keygen_cq(uint8_t*, const gt_cq_poly*);
int  o_poly_frombytes(poly*, const uint8_t*);
void o_poly_tobytes(uint8_t*, const poly*);
void o_poly_ntt(poly*);
void o_poly_cbd1(poly*, const uint8_t*);
void poly_ntt_encap_small_lazy(poly*, const poly*);
void poly_ntt_decap(poly*, const poly*);
void poly_cbd1(poly*, const uint8_t*);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static poly a; static gt_cq_poly cq; static uint8_t buf[NTRUPLUS_POLYBYTES+64];
static int g0(void){return poly_frombytes_encap(&a,buf);}
static int g1(void){return poly_frombytes_decap(&a,buf);}
static int g2(void){poly_tobytes_encap_loose(buf,&a);return buf[0];}
static int g3(void){poly_tobytes_encap(buf,&a);return buf[0];}
static int g4(void){poly_tobytes_decap(buf,&a);return buf[0];}
static int g5(void){poly_tobytes_keygen_cq(buf,&cq);return buf[0];}
static int of(void){return o_poly_frombytes(&a,buf);}
static int ot(void){o_poly_tobytes(buf,&a);return buf[0];}
/* the loose serializer exists because the lazy NTT does not reduce; pricing
 * one without the other is the fusion accounting error this session keeps
 * finding, so both sides of the trade are here */
static poly z;
static int g6(void){poly_ntt_encap_small_lazy(&z,&z);return z.coeffs[0];}
static int g7(void){poly_ntt_decap(&z,&z);return z.coeffs[0];}
static int g8(void){poly_cbd1(&z,buf);return z.coeffs[0];}
static int on(void){o_poly_ntt(&z);return z.coeffs[0];}
static int oc(void){o_poly_cbd1(&z,buf);return z.coeffs[0];}
typedef int(*F)(void);
static F GS[9]={g0,g1,g2,g3,g4,g5,g6,g7,g8};
static F OS[9]={of,of,ot,ot,ot,ot,on,on,oc};
static const char*NM[9]={"frombytes_encap","frombytes_decap","tobytes_encap_loose",
  "tobytes_encap","tobytes_decap","tobytes_keygen_cq","ntt_encap_small_lazy",
  "ntt_decap","cbd1"};
/* calls per operation: keygen / encaps / decaps */
static const int CN[9][3]={{0,1,0},{0,0,1},{0,1,0},{0,0,0},{0,0,2},{3,0,0},
  {0,2,0},{0,0,2},{1,1,1}};
#define N 4000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(int i=0;i<NTRUPLUS_N;i++) a.coeffs[i]=(int16_t)((i*2654435761u)%3457);
  memcpy(&cq,&a,sizeof cq);
  for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)(i*211u);
  static uint64_t bg[9],bo[9]; for(int i=0;i<9;i++){bg[i]=~0ull;bo[i]=~0ull;}
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<9;i++){for(int k=0;k<N;k++) sink+=GS[i]();
      for(int k=0;k<N;k++) sink+=OS[i]();}
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++) for(int i=0;i<9;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=GS[i](); uint64_t d1=ns()-x;
    x=ns(); for(int k=0;k<N;k++) sink+=OS[i](); uint64_t d2=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d1<bg[i]) bg[i]=d1; if(d2<bo[i]) bo[i]=d2; }
  double gz=500000.0/(double)wf;
  printf("  時脈見證 %.3f GHz\n\n  %-22s%9s%9s%7s   %s\n",gz,"","GT","Off","x","kg/en/de");
  double sg[3]={0,0,0},so[3]={0,0,0};
  for(int i=0;i<9;i++){
    double g=(double)bg[i]/N*gz,o=(double)bo[i]/N*gz;
    for(int q=0;q<3;q++){sg[q]+=g*CN[i][q];so[q]+=o*CN[i][q];}
    printf("  %-22s%9.0f%9.0f%7.2f   %d/%d/%d\n",NM[i],g,o,g/o,CN[i][0],CN[i][1],CN[i][2]);
  }
  const char*ON[3]={"keygen","encaps","decaps"};
  printf("\n  核心合計   %10s%10s%10s%9s\n","GT cyc","Off cyc","差","ns");
  for(int q=0;q<3;q++)
    printf("  %-12s%10.0f%10.0f%+10.0f%+9.1f\n",ON[q],sg[q],so[q],sg[q]-so[q],(sg[q]-so[q])/gz);
  return 0;}
