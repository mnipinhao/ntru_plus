/* GT against Official, kernel by kernel, in cycles, mirroring kem.c exactly.
 *
 * Every call site is reproduced with the aliasing the real code uses, because
 * this campaign has now made the same mistake twice in both directions:
 *   - the harness once let Official copy before poly_invntt_scale, which its
 *     kem.c does not do (P92 caught it);
 *   - the correction then removed the copy before Official's *first* decap
 *     poly_ntt, which its kem.c DOES do -- `f = m;` -- because Official has no
 *     out-of-place form and m is still needed by poly_sotp_decode.
 * So the forward transform is priced twice: in place, as key generation and
 * encapsulation call it, and as decapsulation's first call, where GT's
 * out-of-place form saves Official's copy.
 */
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
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static inline int vrf(const uint8_t*a,const uint8_t*b,size_t n){
 uint8_t x=0; for(size_t i=0;i<n;i++) x|=(uint8_t)(a[i]^b[i]); return x!=0;}
static poly a,b,c,m;
static uint8_t buf[NTRUPLUS_POLYBYTES+64], bu2[NTRUPLUS_POLYBYTES+64];
static uint8_t seed[NTRUPLUS_N/4], msg[NTRUPLUS_N/8];

static int g00(void){return poly_frombytes(&b,buf);}
static int o00(void){return o_poly_frombytes(&b,buf);}
static int g01(void){poly_basemul_rinv(m.coeffs,a.coeffs,b.coeffs);return m.coeffs[0];}
static int o01(void){o_poly_basemul_scale(&m,&a,&b);return m.coeffs[0];}
/* both in place, as kem.c calls them */
static int g02(void){poly_invntt_ternary(&c,&c);return c.coeffs[0];}
static int o02(void){o_poly_invntt_scale(&c); o_poly_crepmod3(&c); return c.coeffs[0];}
/* keygen and encapsulation: in place on both sides */
static int g03(void){poly_ntt(&c,&c);return c.coeffs[0];}
static int o03(void){o_poly_ntt(&c);return c.coeffs[0];}
/* decapsulation's first call: GT out of place, Official f = m then in place */
static int g04(void){poly_ntt(&c,&m);return c.coeffs[0];}
static int o04(void){c=m; o_poly_ntt(&c); return c.coeffs[0];}
static int g05(void){poly_sub(&c,&a,&b);return c.coeffs[0];}
static int o05(void){o_poly_sub(&c,&a,&b);return c.coeffs[0];}
static int g06(void){poly_basemul(&c,&a,&b);return c.coeffs[0];}
static int o06(void){o_poly_basemul(&c,&a,&b);return c.coeffs[0];}
static int g07(void){poly_tobytes_small(buf,&a);return buf[0];}
static int o07(void){o_poly_tobytes(buf,&a);return buf[0];}
static int g08(void){poly_tobytes(buf,&a);return buf[0];}
static int o08(void){o_poly_tobytes(buf,&a);return buf[0];}
static int g09(void){return poly_sotp_decode(msg,&a,seed);}
static int o09(void){return o_poly_sotp_decode(msg,&a,seed);}
static int g10(void){poly_cbd1(&c,seed);return c.coeffs[0];}
static int o10(void){o_poly_cbd1(&c,seed);return c.coeffs[0];}
static int g11(void){return vrf(buf,bu2,NTRUPLUS_POLYBYTES);}
static int o11(void){return vrf(buf,bu2,NTRUPLUS_POLYBYTES);}
typedef int (*F)(void);
static F GF[]={g00,g01,g02,g03,g04,g05,g06,g07,g08,g09,g10,g11};
static F OF[]={o00,o01,o02,o03,o04,o05,o06,o07,o08,o09,o10,o11};
static const char*NM[]={"frombytes","basemul_rinv/scale","invntt(+crepmod3)",
  "ntt 原地 (keygen/encap)","ntt decap 第一次","sub","basemul","tobytes_small",
  "tobytes(full)","sotp_decode","cbd1","verify"};
/* calls per operation: keygen, encaps, decaps */
static const int CN[][3]={
  {0,1,3},   /* frombytes            */  {0,0,1},  /* basemul_rinv/scale */
  {0,0,1},   /* invntt               */  {2,2,1},  /* ntt in place       */
  {0,0,1},   /* ntt, decap's first   */  {0,0,1},  /* sub                */
  {2,0,1},   /* basemul              */  {2,1,1},  /* tobytes_small      */
  {1,0,1},   /* tobytes              */  {0,0,1},  /* sotp_decode        */
  {2,1,1},   /* cbd1                 */  {0,0,1}}; /* verify             */
#define NK ((int)(sizeof GF/sizeof*GF))
#define N 2000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(int i=0;i<NTRUPLUS_N;i++){a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
    b.coeffs[i]=(int16_t)((i*40503u)%3457)-1728; m.coeffs[i]=(int16_t)((i*104729u)%3)-1;
    c.coeffs[i]=m.coeffs[i];}
  for(size_t i=0;i<sizeof seed;i++) seed[i]=(uint8_t)(i*167u);
  for(size_t i=0;i<sizeof buf;i++){buf[i]=(uint8_t)(i*211u); bu2[i]=buf[i];}
  static uint64_t bg[NK],bo[NK]; for(int i=0;i<NK;i++){bg[i]=~0ull;bo[i]=~0ull;}
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NK;i++){for(int k=0;k<N;k++) sink+=GF[i]();
      for(int k=0;k<N;k++) sink+=OF[i]();}
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>3000000000ull) break; }
  enum {R=201};
  for(int r=0;r<R;r++) for(int i=0;i<NK;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=GF[i](); uint64_t d1=ns()-x;
    x=ns(); for(int k=0;k<N;k++) sink+=OF[i](); uint64_t d2=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d1<bg[i]) bg[i]=d1; if(d2<bo[i]) bo[i]=d2; }
  double gz=500000.0/(double)wf;
  printf("  N=%d  時脈見證 %.3f GHz\n\n",NTRUPLUS_N,gz);
  printf("  %-24s%9s%9s%7s   %s\n","kernel","GT cyc","Off cyc","x","呼叫 kg/en/de");
  double sg[3]={0,0,0}, so[3]={0,0,0};
  for(int i=0;i<NK;i++){
    double g=(double)bg[i]/N*gz, o=(double)bo[i]/N*gz;
    for(int op=0;op<3;op++){ sg[op]+=g*CN[i][op]; so[op]+=o*CN[i][op]; }
    printf("  %-24s%9.0f%9.0f%7.2f   %d/%d/%d\n",NM[i],g,o,g/o,
           CN[i][0],CN[i][1],CN[i][2]);
  }
  const char*ON[3]={"keygen*","encaps*","decaps"};
  printf("\n  %-10s%11s%11s%10s%9s\n","操作","GT cyc","Off cyc","差","%");
  for(int op=0;op<3;op++)
    printf("  %-10s%11.0f%11.0f%+10.0f%+8.1f%%\n",ON[op],sg[op],so[op],
           sg[op]-so[op],100.0*(sg[op]-so[op])/so[op]);
  puts("  * partial: key generation also runs baseinv x2 and triple x2,\n"
       "    encapsulation sotp_encode and basemul_add; decapsulation is complete.");
  return 0;}
