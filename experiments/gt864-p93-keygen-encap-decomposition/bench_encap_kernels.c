#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
int  poly_frombytes(poly*, const uint8_t*);  int  o_poly_frombytes(poly*, const uint8_t*);
void poly_cbd1(poly*, const uint8_t*);       void o_poly_cbd1(poly*, const uint8_t*);
void poly_ntt(poly*, const poly*);           void o_poly_ntt(poly*);
void poly_sotp_encode(poly*, const uint8_t*, const uint8_t*);
void o_poly_sotp_encode(poly*, const uint8_t*, const uint8_t*);
void poly_basemul_add(poly*, const poly*, const poly*, const poly*);
void o_poly_basemul_add(poly*, const poly*, const poly*, const poly*);
void poly_tobytes_small(uint8_t*, const poly*);
void o_poly_tobytes(uint8_t*, const poly*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly a,b,c,d2; static uint8_t seed[NTRUPLUS_N/4], msg[NTRUPLUS_N/8], buf[NTRUPLUS_POLYBYTES+64];
#define NF 12
static int k0(void){return poly_frombytes(&b,buf);}  static int k1(void){return o_poly_frombytes(&b,buf);}
static int k2(void){poly_cbd1(&c,seed);return c.coeffs[0];} static int k3(void){o_poly_cbd1(&c,seed);return c.coeffs[0];}
static int k4(void){poly_ntt(&c,&a);return c.coeffs[0];}    static int k5(void){c=a; o_poly_ntt(&c); return c.coeffs[0];}
static int k6(void){poly_sotp_encode(&c,msg,seed);return c.coeffs[0];}
static int k7(void){o_poly_sotp_encode(&c,msg,seed);return c.coeffs[0];}
static int k8(void){poly_basemul_add(&d2,&a,&b,&c);return d2.coeffs[0];}
static int k9(void){o_poly_basemul_add(&d2,&a,&b,&c);return d2.coeffs[0];}
static int k10(void){poly_tobytes_small(buf,&a);return buf[0];} static int k11(void){o_poly_tobytes(buf,&a);return buf[0];}
static int (*F[NF])(void)={k0,k1,k2,k3,k4,k5,k6,k7,k8,k9,k10,k11};
static const char*nm[NF/2]={"frombytes","cbd1","ntt","sotp_encode","basemul_add","pack"};
static const int cg[NF/2]={1,1,2,1,1,1};   /* GT 的呼叫次數 */
static const int co[NF/2]={1,1,2,1,1,2};   /* Official 的呼叫次數 */
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<NTRUPLUS_N;i++){a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;b.coeffs[i]=(int16_t)((i*40503u)%3457)-1728;}
  for(size_t i=0;i<sizeof seed;i++) seed[i]=(uint8_t)(i*167u);
  for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)(i*211u);
  o_poly_tobytes(buf,&a);
  uint64_t wf=~0ull,best[NF]; int acc[NF];
  for(int i=0;i<NF;i++){best[i]=~0ull;acc[i]=0;}
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NF;i++) for(int k=0;k<2000;k++) sink+=F[i]();
    uint64_t dd=witness(); if(dd<wf){wf=dd;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<201;r++) for(int i=0;i<NF;i++){
    uint64_t x=nsec(); for(int k=0;k<2000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t dd=witness(); if(dd<wf) wf=dd;
    if(dd*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  double sg=0,so=0;
  printf("  %-16s%8s%8s%7s%6s%6s%9s%9s\n","kernel","GT","Off","x","GT次","Off次","GT 合計","Off 合計");
  for(int i=0;i<NF;i+=2){
    double gg=(double)best[i]/2000.0, oo=(double)best[i+1]/2000.0;
    sg+=gg*cg[i/2]; so+=oo*co[i/2];
    printf("  %-16s%8.1f%8.1f%7.2f%6d%6d%9.0f%9.0f\n",nm[i/2],gg,oo,gg/oo,cg[i/2],co[i/2],gg*cg[i/2],oo*co[i/2]);
  }
  printf("  %-16s%8s%8s%7s%6s%6s%9.0f%9.0f   差 %+.0f ns\n","合計","","","","","",sg,so,sg-so);
  return 0;}
