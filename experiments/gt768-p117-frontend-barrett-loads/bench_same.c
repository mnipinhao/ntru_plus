/* P117: E2b vs E3 inverse in one binary, same harness, in place from a fresh copy. */
#include <stdio.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
#include "test/reference/poly_reference.h"
int e3_poly_frombytes_basemul_decap_scale(poly*,poly*,const unsigned char*,const unsigned char*);
void e2b_poly_invntt(poly*,const poly*);
void e3_poly_invntt(poly*,const poly*);
static inline unsigned long long nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static unsigned long long witness(void){unsigned long long x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 unsigned long long d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly gb,ga,b,c,f;
static int k2b(void){b=gb; e2b_poly_invntt(&b,&b); return b.coeffs[3];}
static int k3(void){b=ga; e3_poly_invntt(&b,&b); return b.coeffs[3];}
static int k2b_o(void){e2b_poly_invntt(&b,&gb); return b.coeffs[3];}
static int k3_o(void){e3_poly_invntt(&b,&ga); return b.coeffs[3];}
static int kc(void){b=gb; return b.coeffs[3];}
int main(void){ pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
 static unsigned char ct[NTRUPLUS_POLYBYTES],fb[NTRUPLUS_POLYBYTES]; poly t,r1,r2;
 for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)((i*2654435761u+17)%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
 for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)((i*40503u+99)%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
 poly_frombytes_encap(&c,ct); poly_frombytes_encap(&f,fb); poly_basemul(&gb,&c,&f);
 e3_poly_frombytes_basemul_decap_scale(&ga,&c,ct,fb);
 e2b_poly_invntt(&r1,&gb); e3_poly_invntt(&r2,&ga); int bad=0; for(int i=0;i<NTRUPLUS_N;i++) bad+=r1.coeffs[i]!=r2.coeffs[i];
 printf("E2b(block-major) vs E3(st4 product): %d mismatches\n",bad);
 int (*F[5])(void)={k2b,k3,k2b_o,k3_o,kc}; const char*nm[5]={"E2b in place","E3 in place","E2b out of place","E3 out of place","copy"};
 unsigned long long wf=~0ull,best[5],t0=nsec(); int st=0; for(int i=0;i<5;i++) best[i]=~0ull;
 for(int w=0;w<4000;w++){ for(int i=0;i<5;i++) for(int k=0;k<500;k++) sink+=F[i]();
   unsigned long long d=witness(); if(d<wf){wf=d;st=0;} else st++; if(st>=5&&nsec()-t0>3000000000ull) break;}
 for(int r=0;r<301;r++) for(int i=0;i<5;i++){ unsigned long long x=nsec(); for(int k=0;k<1000;k++) sink+=F[i](); unsigned long long dt=nsec()-x;
   unsigned long long d=witness(); if(d<wf) wf=d; if(d*98<=wf*100&&dt<best[i]) best[i]=dt;}
 for(int i=0;i<5;i++) printf("  %-18s %6.1f ns%s\n",nm[i],(i<2?best[i]-best[4]:best[i])/1e3,i<2?" (copy-corrected)":"");
 return 0;}
