/* P115: decaps first product + inverse, split into parts, GT (retired) vs Official-layout (production). */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
#include "test/reference/poly_reference.h"
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static uint8_t ct[NTRUPLUS_POLYBYTES], fb[NTRUPLUS_POLYBYTES];
static poly c,f,m,m2,gin;
static uint8_t scr[2144] __attribute__((aligned(64)));
static int o_full(void){int r=poly_frombytes_basemul_decap_scale(&m,&c,ct,fb); poly_invntt_decap_scale(&m); return r+m.coeffs[5];}
static int o_dbm(void){return poly_frombytes_basemul_decap_scale(&m,&c,ct,fb)+m.coeffs[5];}
static int o_inv(void){m2=gin; poly_invntt_decap_scale(&m2); return m2.coeffs[5];}
static int g_full(void){int r=poly_frombytes_encap(&c,ct); r|=poly_frombytes_encap(&f,fb); poly_basemul(&m,&c,&f); poly_invntt(&m,&m); memset_s(scr,sizeof scr,0,sizeof scr); return r+m.coeffs[5];}
static int g_dec(void){int r=poly_frombytes_encap(&c,ct); r|=poly_frombytes_encap(&f,fb); return r+c.coeffs[3]+f.coeffs[3];}
static int g_bm(void){poly_basemul(&m,&c,&f); return m.coeffs[5];}
static int g_inv(void){poly_invntt(&m2,&gin); return m2.coeffs[5];}
static int g_clr(void){memset_s(scr,sizeof scr,0,sizeof scr); return scr[7];}
static int o_dec(void){return poly_frombytes_decap(&c,ct)+poly_frombytes_decap(&f,fb)+c.coeffs[3];}
static int o_bm(void){poly_basemul_decap(&m,&c,&f); return m.coeffs[5];}
static int g_inv_ip(void){m2=gin; poly_invntt(&m2,&m2); return m2.coeffs[5];}
static int cp(void){m2=gin; return m2.coeffs[5];}
#define NF 13
static int (*F[NF])(void)={o_full,o_dbm,o_inv,g_full,g_dec,g_bm,g_inv,g_clr,o_dec,o_bm,g_inv_ip,cp,cp};
static const char*nm[NF]={"Official: decode+basemul+inv","  Off decode+basemul (fused)","  Off inv (incl. 1536B copy)","GT: decode+basemul+inv+clear","  GT decode ct+f (block-major)","  GT basemul","  GT inv (out-of-place)","  clear 2144B (memset_s)","  Off decode ct+f alone (x2 frombytes_decap)","  Off basemul_decap alone (D1, normal domain)","  GT inv in-place (incl. copy)","copy 1536B","copy 1536B"};
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  /* valid inputs: random canonical polys serialized through GT's encoder */
  poly t; for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(int16_t)((i*2654435761u+17)%NTRUPLUS_Q);
  poly_tobytes_encap(ct,&t);
  for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(int16_t)((i*40503u+99)%NTRUPLUS_Q);
  poly_tobytes_encap(fb,&t);
  /* correctness: both chains, then crepmod3, must agree */
  poly a,b; if(poly_frombytes_basemul_decap_scale(&a,&c,ct,fb)) {puts("decode fail O");return 1;}
  poly_invntt_decap_scale(&a); poly_crepmod3(&a,&a);
  if(poly_frombytes_encap(&c,ct)|poly_frombytes_encap(&f,fb)){puts("decode fail G");return 1;}
  poly_basemul(&b,&c,&f); gin=b; poly_invntt(&b,&b); poly_crepmod3(&b,&b);
  int bad=0; for(int i=0;i<NTRUPLUS_N;i++) bad+=a.coeffs[i]!=b.coeffs[i];
  printf("mismatches after crepmod3: %d / %d\n",bad,NTRUPLUS_N); if(bad) return 1;
  uint64_t wf=~0ull,best[NF]; for(int i=0;i<NF;i++) best[i]=~0ull;
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NF;i++) for(int k=0;k<500;k++) sink+=F[i]();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<301;r++) for(int i=0;i<NF;i++){
    uint64_t x=nsec(); for(int k=0;k<1000;k++) sink+=F[i](); uint64_t dt=nsec()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(d*98<=wf*100 && dt<best[i]) best[i]=dt; }
  printf("witness %.3f ms (lower = P-core at full clock)\n",wf/1e6);
  for(int i=0;i<NF-1;i++) printf("  %-34s %7.1f ns\n",nm[i],best[i]/1000.0);
  return 0;}
