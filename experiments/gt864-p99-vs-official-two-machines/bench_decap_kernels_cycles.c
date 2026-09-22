/* NTRU+864 decapsulation, kernel by kernel, both implementations in one binary.
 * Direct timing, not sampling: P91 found the sampler disagrees with itself by
 * 5% on a 2000 ns bucket, which is 100 ns -- the size of the thing being looked
 * for here. */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <time.h>


#include "params.h"
#include "poly.h"
/* GT */
int  poly_frombytes(poly*, const uint8_t*);
void poly_basemul_rinv(int16_t*, const int16_t*, const int16_t*);
void poly_invntt_ternary(poly*, const poly*);
void poly_ntt(poly*, const poly*);
void poly_sub(poly*, const poly*, const poly*);
void poly_basemul(poly*, const poly*, const poly*);
void poly_tobytes_small(uint8_t*, const poly*);
void poly_tobytes(uint8_t*, const poly*);
int  poly_sotp_decode(uint8_t*, const poly*, const uint8_t*);
void poly_cbd1(poly*, const uint8_t*);
/* Official, renamed */
int  o_poly_frombytes(poly*, const uint8_t*);
void o_poly_basemul_scale(poly*, const poly*, const poly*);
void o_poly_invntt_scale(poly*);
void o_poly_crepmod3(poly*);
void o_poly_ntt(poly*);
void o_poly_sub(poly*, const poly*, const poly*);
void o_poly_basemul(poly*, const poly*, const poly*);
void o_poly_tobytes(uint8_t*, const poly*);
int  o_poly_sotp_decode(uint8_t*, const poly*, const uint8_t*);
void o_poly_cbd1(poly*, const uint8_t*);

#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#else
static inline uint64_t nsec(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
#endif
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static inline int verify(const uint8_t*a,const uint8_t*b,size_t n){
 uint8_t x=0; for(size_t i=0;i<n;i++) x|=(uint8_t)(a[i]^b[i]); return x!=0;}

static poly a,b,c,m; static uint8_t buf[NTRUPLUS_POLYBYTES+64], bu2[NTRUPLUS_POLYBYTES+64];
static uint8_t seed[NTRUPLUS_N/4], msg[NTRUPLUS_N/8];

#define NF 22
static int k00(void){return poly_frombytes(&b,buf);}          static int k01(void){return o_poly_frombytes(&b,buf);}
static int k02(void){poly_basemul_rinv(m.coeffs,a.coeffs,b.coeffs);return m.coeffs[0];}
static int k03(void){o_poly_basemul_scale(&m,&a,&b);return m.coeffs[0];}
static int k04(void){poly_invntt_ternary(&c,&m);return c.coeffs[0];}
static int k05(void){c=m; o_poly_invntt_scale(&c); o_poly_crepmod3(&c); return c.coeffs[0];}
static int k06(void){poly_ntt(&c,&m);return c.coeffs[0];}     static int k07(void){c=m; o_poly_ntt(&c); return c.coeffs[0];}
static int k08(void){poly_sub(&c,&a,&b);return c.coeffs[0];}  static int k09(void){o_poly_sub(&c,&a,&b);return c.coeffs[0];}
static int k10(void){poly_basemul(&c,&a,&b);return c.coeffs[0];} static int k11(void){o_poly_basemul(&c,&a,&b);return c.coeffs[0];}
static int k12(void){poly_tobytes_small(buf,&a);return buf[0];} static int k13(void){o_poly_tobytes(buf,&a);return buf[0];}
static int k14(void){poly_tobytes(buf,&a);return buf[0];}      static int k15(void){o_poly_tobytes(buf,&a);return buf[0];}
static int k16(void){return poly_sotp_decode(msg,&a,seed);}    static int k17(void){return o_poly_sotp_decode(msg,&a,seed);}
static int k18(void){poly_cbd1(&c,seed);return c.coeffs[0];}   static int k19(void){o_poly_cbd1(&c,seed);return c.coeffs[0];}
static int k20(void){return verify(buf,bu2,NTRUPLUS_POLYBYTES);} static int k21(void){return verify(buf,bu2,NTRUPLUS_POLYBYTES);}
static int (*F[NF])(void)={k00,k01,k02,k03,k04,k05,k06,k07,k08,k09,k10,k11,k12,k13,k14,k15,k16,k17,k18,k19,k20,k21};
static const char*nm[NF/2]={"frombytes","basemul_rinv/scale","invntt(+crepmod3)","ntt",
  "sub","basemul","tobytes_small","tobytes(full)","sotp_decode","cbd1","verify"};
static const int cnt[NF/2]={3,1,1,2,1,1,1,1,1,1,1};
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  
  for(int i=0;i<NTRUPLUS_N;i++){a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
    b.coeffs[i]=(int16_t)((i*40503u)%3457)-1728; m.coeffs[i]=(int16_t)((i*104729u)%3)-1;}
  for(size_t i=0;i<sizeof seed;i++) seed[i]=(uint8_t)(i*167u);
  for(size_t i=0;i<sizeof buf;i++){buf[i]=(uint8_t)(i*211u); bu2[i]=buf[i];}
  uint64_t wf=~0ull,best[NF]; int acc[NF];
  for(int i=0;i<NF;i++){best[i]=~0ull;acc[i]=0;}
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NF;i++) for(int k=0;k<2000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<201;r++) for(int i=0;i<NF;i++){
    uint64_t x=nsec(); for(int k=0;k<2000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(dt<best[i]){best[i]=dt; acc[i]++;} }
  double gz=500000.0/(double)wf, sg=0, so=0;
  printf("  時脈見證: %.3f GHz\n\n", gz);
  printf("  %-22s%9s%9s%7s%6s%10s%10s\n","kernel","GT cyc","Off cyc","x","呼叫","GT 合計","Off 合計");
  for(int i=0;i<NF;i+=2){
    double g=(double)best[i]/2000.0*gz, o=(double)best[i+1]/2000.0*gz;
    sg+=g*cnt[i/2]; so+=o*cnt[i/2];
    printf("  %-22s%9.0f%9.0f%7.2f%6d%10.0f%10.0f\n",nm[i/2],g,o,g/o,cnt[i/2],g*cnt[i/2],o*cnt[i/2]);
  }
  printf("  %-22s%9s%9s%7s%6s%10.0f%10.0f   差 %+.0f cyc (%+.1f%%)\n",
         "合計","","","","",sg,so,sg-so,100.0*(sg-so)/so);
  return 0;}
