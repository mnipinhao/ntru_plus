#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
void poly_cbd1(poly*, const uint8_t*);
void poly_triple(poly*, const poly*);
void poly_sub(poly*, const poly*, const poly*);
void poly_sotp_encode(poly*, const uint8_t*, const uint8_t*);
int  poly_sotp_decode(uint8_t*, const poly*, const uint8_t*);
void o_cbd1(void*, const uint8_t*); void o_triple(void*, const void*);
void o_sub(void*, const void*, const void*); void o_enc(void*, const uint8_t*, const uint8_t*);
int  o_dec(uint8_t*, const void*, const uint8_t*);
void v_sub(poly*,const poly*,const poly*); void v_triple(poly*,const poly*);
void u_sub(poly*,const poly*,const poly*); void u_triple(poly*,const poly*);
void n_cbd1(poly*,const uint8_t*);
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly a,b,c; static uint8_t buf[NTRUPLUS_N/4], msg[NTRUPLUS_N/8];
#define NF 16
static int f0(void){poly_cbd1(&b,buf);return b.coeffs[0];}   static int f1(void){o_cbd1(&b,buf);return b.coeffs[0];}
static int f2(void){poly_triple(&b,&a);return b.coeffs[0];}  static int f3(void){o_triple(&b,&a);return b.coeffs[0];}
static int f4(void){poly_sub(&c,&a,&b);return c.coeffs[0];}  static int f5(void){o_sub(&c,&a,&b);return c.coeffs[0];}
static int f6(void){poly_sotp_encode(&c,msg,buf);return c.coeffs[0];} static int f7(void){o_enc(&c,msg,buf);return c.coeffs[0];}
static int f8(void){return poly_sotp_decode(msg,&a,buf);}    static int f9(void){return o_dec(msg,&a,buf);}
static int f10(void){v_sub(&c,&a,&b);return c.coeffs[0];}  static int f11(void){o_sub(&c,&a,&b);return c.coeffs[0];}
static int f12(void){v_triple(&b,&a);return b.coeffs[0];}  static int f13(void){u_triple(&b,&a);return b.coeffs[0];}
static int f14(void){n_cbd1(&b,buf);return b.coeffs[0];}   static int f15(void){o_cbd1(&b,buf);return b.coeffs[0];}
static int (*F[NF])(void)={f0,f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13,f14,f15};
static const char*nm[NF]={"GT cbd1","Off cbd1","GT triple","Off triple","GT sub","Off sub",
                          "GT sotp_encode","Off sotp_encode","GT sotp_decode","Off sotp_decode","x12 sub","Off sub(2)","x12 triple","unroll4 triple","bitslice cbd1","Off cbd1(2)"};
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<NTRUPLUS_N;i++){a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;b.coeffs[i]=(int16_t)((i*40503u)%3457)-1728;}
  for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)(i*167u);
  for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)(i*211u);
  uint64_t wf=~0ull,best[NF]; int acc[NF];
  for(int i=0;i<NF;i++){best[i]=~0ull;acc[i]=0;}
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NF;i++) for(int k=0;k<3000;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<41;r++) for(int i=0;i<NF;i++){
    uint64_t x=nsec(); for(int k=0;k<3000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100){acc[i]++; if(dt<best[i]) best[i]=dt;} }
  for(int i=0;i<NF;i+=2)
    printf("  %-16s %7.1f  |  %-16s %7.1f   %+7.1f ns\n",nm[i],(double)best[i]/3000.0,nm[i+1],(double)best[i+1]/3000.0,
           ((double)best[i]-(double)best[i+1])/3000.0);
  return 0;}
