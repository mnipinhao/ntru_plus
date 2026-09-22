/* P116: GT inverse variants vs reference and Official on M2: bit-exactness on real products, then timing. */
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
#include "test/reference/poly_reference.h"
#ifndef VARIANT
#define VARIANT e1
#endif
#define CAT2(a,b) a##b
#define CAT(a,b) CAT2(a,b)
#define VINV CAT(VARIANT,_poly_invntt)
void VINV(poly*,const poly*);
static inline unsigned long long nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static unsigned long long witness(void){unsigned long long x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 unsigned long long d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly gin,oin,b;
static unsigned rng=12345; static unsigned rnd(void){rng=rng*1103515245u+12345u; return rng>>8;}
static int k_ref(void){poly_invntt(&b,&gin); return b.coeffs[3];}
static int k_var(void){VINV(&b,&gin); return b.coeffs[3];}
static int k_off(void){b=oin; poly_invntt_decap_scale(&b); return b.coeffs[3];}
static int k_cp(void){b=oin; return b.coeffs[3];}
int main(void){ pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
 static unsigned char ct[NTRUPLUS_POLYBYTES],fb[NTRUPLUS_POLYBYTES]; poly t,c,f,r1,r2;
 long bad=0,bad3=0;
 for(int trial=0;trial<2000;trial++){
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(trial<8? (trial&1? NTRUPLUS_Q-1:0) + (trial&2? 0:(i&1)) : rnd()%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
   poly_frombytes_encap(&c,ct); poly_frombytes_encap(&f,fb); poly_basemul(&gin,&c,&f);
   poly_invntt(&r1,&gin); VINV(&r2,&gin);
   for(int i=0;i<NTRUPLUS_N;i++) bad+=r1.coeffs[i]!=r2.coeffs[i];
   poly_crepmod3(&r1,&r1); poly_crepmod3(&r2,&r2);
   for(int i=0;i<NTRUPLUS_N;i++) bad3+=r1.coeffs[i]!=r2.coeffs[i]; }
 /* extreme synthetic inputs too: full int16 corners are outside the contract, so use +-q-1 */
 for(int trial=0;trial<200;trial++){ for(int i=0;i<NTRUPLUS_N;i++){int s=rnd()%3; gin.coeffs[i]=(short)(s==0?-(NTRUPLUS_Q-1):s==1?(NTRUPLUS_Q-1):(int)(rnd()%(2*NTRUPLUS_Q-1))-(NTRUPLUS_Q-1));}
   poly_invntt(&r1,&gin); VINV(&r2,&gin); for(int i=0;i<NTRUPLUS_N;i++) bad+=r1.coeffs[i]!=r2.coeffs[i]; }
 printf("vs reference: %ld raw mismatches, %ld after crepmod3 (2000 real products + 200 corner inputs)\n",bad,bad3);
 if(bad) return 1;
 poly_frombytes_basemul_decap_scale(&oin,&c,ct,fb);
 int (*F[4])(void)={k_ref,k_var,k_off,k_cp}; const char*nm[4]={"GT reference","GT " "variant","Official (incl copy)","copy"};
 unsigned long long wf=~0ull,best[4]={~0ull,~0ull,~0ull,~0ull},t0=nsec(); int st=0;
 for(int w=0;w<4000;w++){ for(int i=0;i<4;i++) for(int k=0;k<500;k++) sink+=F[i]();
   unsigned long long d=witness(); if(d<wf){wf=d;st=0;} else st++; if(st>=5&&nsec()-t0>3000000000ull) break;}
 for(int r=0;r<301;r++) for(int i=0;i<4;i++){ unsigned long long x=nsec(); for(int k=0;k<1000;k++) sink+=F[i](); unsigned long long dt=nsec()-x;
   unsigned long long d=witness(); if(d<wf) wf=d; if(d*98<=wf*100&&dt<best[i]) best[i]=dt;}
 #define STR2(x) #x
#define STR(x) STR2(x)
 printf("GT reference %.1f | GT %s %.1f | Official %.1f (copy-corrected %.1f) ns\n",best[0]/1e3,
   STR(VARIANT),best[1]/1e3,best[2]/1e3,(best[2]-best[3])/1e3);
 return 0; }
