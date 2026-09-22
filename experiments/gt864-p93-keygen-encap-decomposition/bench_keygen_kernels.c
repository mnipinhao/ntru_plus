/* NTRU+864 key generation, kernel by kernel, both implementations linked. */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
void poly_cbd1(poly*, const uint8_t*);       void o_poly_cbd1(poly*, const uint8_t*);
void poly_triple(poly*, const poly*);        void o_poly_triple(poly*, const poly*);
void poly_ntt(poly*, const poly*);           void o_poly_ntt(poly*);
int  poly_baseinv(poly*, const poly*);       int  o_poly_baseinv(poly*, const poly*);
void poly_basemul(poly*, const poly*, const poly*); void o_poly_basemul(poly*, const poly*, const poly*);
void poly_tobytes_small(uint8_t*, const poly*);
void poly_tobytes(uint8_t*, const poly*);    void o_poly_tobytes(uint8_t*, const poly*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly f,g,inv,prod; static uint8_t seed[NTRUPLUS_N/4], buf[NTRUPLUS_POLYBYTES+64];
#define NF 12
static int k0(void){poly_cbd1(&g,seed);return g.coeffs[0];}   static int k1(void){o_poly_cbd1(&g,seed);return g.coeffs[0];}
static int k2(void){poly_triple(&g,&f);return g.coeffs[0];}   static int k3(void){o_poly_triple(&g,&f);return g.coeffs[0];}
static int k4(void){poly_ntt(&g,&f);return g.coeffs[0];}      static int k5(void){g=f; o_poly_ntt(&g); return g.coeffs[0];}
static int k6(void){return poly_baseinv(&inv,&f);}            static int k7(void){return o_poly_baseinv(&inv,&f);}
static int k8(void){poly_basemul(&prod,&f,&inv);return prod.coeffs[0];}
static int k9(void){o_poly_basemul(&prod,&f,&inv);return prod.coeffs[0];}
static int k10(void){poly_tobytes_small(buf,&f);return buf[0];} static int k11(void){o_poly_tobytes(buf,&f);return buf[0];}
static int (*F[NF])(void)={k0,k1,k2,k3,k4,k5,k6,k7,k8,k9,k10,k11};
static const char*nm[NF/2]={"cbd1","triple","ntt","baseinv","basemul","tobytes_small vs tobytes"};
static const int cnt[NF/2]={2,2,2,2,2,2};
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(size_t i=0;i<sizeof seed;i++) seed[i]=(uint8_t)((i*2654435761u)>>19);
  /* f = ntt(3*cbd1 + 1), the polynomial genf_derand hands to baseinv */
  poly_cbd1(&f,seed); poly_triple(&f,&f); f.coeffs[0]+=1; poly_ntt(&f,&f);
  int rc=poly_baseinv(&inv,&f);
  printf("  baseinv 可逆: %s\n", rc?"否 (換種子)":"是");
  if(rc) return 1;
  uint64_t wf=~0ull,best[NF]; int acc[NF];
  for(int i=0;i<NF;i++){best[i]=~0ull;acc[i]=0;}
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NF;i++) for(int k=0;k<2000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<201;r++) for(int i=0;i<NF;i++){
    uint64_t x=nsec(); for(int k=0;k<2000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  double sg=0,so=0;
  printf("  %-26s%8s%8s%7s%7s%9s%9s\n","kernel","GT","Off","x","呼叫","GT 合計","Off 合計");
  for(int i=0;i<NF;i+=2){
    double gg=(double)best[i]/2000.0, oo=(double)best[i+1]/2000.0;
    sg+=gg*cnt[i/2]; so+=oo*cnt[i/2];
    printf("  %-26s%8.1f%8.1f%7.2f%7d%9.0f%9.0f\n",nm[i/2],gg,oo,gg/oo,cnt[i/2],gg*cnt[i/2],oo*cnt[i/2]);
  }
  /* the third pack: GT full vs Official full */
  printf("  %-26s%8s%8s%7s%7s%9s%9s\n","(第三次 tobytes 兩邊同為 full)","","","","1","","");
  printf("  %-26s%8s%8s%7s%7s%9.0f%9.0f   差 %+.0f ns\n","合計 (不含第三次 pack)","","","","",sg,so,sg-so);
  return 0;}
