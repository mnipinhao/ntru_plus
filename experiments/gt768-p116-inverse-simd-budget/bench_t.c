/* P116 E2: fused inverse + crepmod3 vs (reference or E1) inverse then crepmod3, and Official's pair. */
#include <stdio.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
#include "test/reference/poly_reference.h"
void e1_poly_invntt(poly*,const poly*);
void e2t_poly_invntt(poly*,const poly*);
static inline unsigned long long nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static unsigned long long witness(void){unsigned long long x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 unsigned long long d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
static poly gin,oin,b;
static unsigned rng=777; static unsigned rnd(void){rng=rng*1103515245u+12345u; return rng>>8;}
static int k_ref(void){poly_invntt(&b,&gin); poly_crepmod3(&b,&b); return b.coeffs[3];}
static int k_e1(void){e1_poly_invntt(&b,&gin); poly_crepmod3(&b,&b); return b.coeffs[3];}
static int k_e2t(void){e2t_poly_invntt(&b,&gin); return b.coeffs[3];}
static int k_off(void){b=oin; poly_invntt_decap_scale(&b); poly_crepmod3(&b,&b); return b.coeffs[3];}
static int k_cp(void){b=oin; return b.coeffs[3];}
static int k_e2t_ip(void){b=gin; e2t_poly_invntt(&b,&b); return b.coeffs[3];}
static int k_cpg(void){b=gin; return b.coeffs[3];}
int main(void){ pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
 static unsigned char ct[NTRUPLUS_POLYBYTES],fb[NTRUPLUS_POLYBYTES]; poly t,c,f,r1,r2; long bad=0;
 for(int trial=0;trial<2000;trial++){
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
   poly_frombytes_encap(&c,ct); poly_frombytes_encap(&f,fb); poly_basemul(&gin,&c,&f);
   poly_invntt(&r1,&gin); poly_crepmod3(&r1,&r1); e2t_poly_invntt(&r2,&gin);
   for(int i=0;i<NTRUPLUS_N;i++) bad+=r1.coeffs[i]!=r2.coeffs[i]; }
 for(int trial=0;trial<200;trial++){ for(int i=0;i<NTRUPLUS_N;i++){int s=rnd()%3; gin.coeffs[i]=(short)(s==0?-(NTRUPLUS_Q-1):s==1?(NTRUPLUS_Q-1):(int)(rnd()%(2*NTRUPLUS_Q-1))-(NTRUPLUS_Q-1));}
   poly_invntt(&r1,&gin); poly_crepmod3(&r1,&r1); e2t_poly_invntt(&r2,&gin); for(int i=0;i<NTRUPLUS_N;i++) bad+=r1.coeffs[i]!=r2.coeffs[i]; }
 { poly ip=gin; poly_invntt(&r1,&gin); poly_crepmod3(&r1,&r1); e2t_poly_invntt(&ip,&ip); for(int i=0;i<NTRUPLUS_N;i++) bad+=r1.coeffs[i]!=ip.coeffs[i]; }
 printf("fused vs reference+crepmod3: %ld mismatches (2000 real products + 200 corner inputs)\n",bad); if(bad) return 1;
 poly_frombytes_basemul_decap_scale(&oin,&c,ct,fb);
 int (*F[7])(void)={k_ref,k_e1,k_e2t,k_off,k_cp,k_e2t_ip,k_cpg};
 unsigned long long wf=~0ull,best[7],t0=nsec(); int st=0; for(int i=0;i<7;i++) best[i]=~0ull;
 for(int w=0;w<4000;w++){ for(int i=0;i<7;i++) for(int k=0;k<500;k++) sink+=F[i]();
   unsigned long long d=witness(); if(d<wf){wf=d;st=0;} else st++; if(st>=5&&nsec()-t0>3000000000ull) break;}
 for(int r=0;r<301;r++) for(int i=0;i<7;i++){ unsigned long long x=nsec(); for(int k=0;k<1000;k++) sink+=F[i](); unsigned long long dt=nsec()-x;
   unsigned long long d=witness(); if(d<wf) wf=d; if(d*98<=wf*100&&dt<best[i]) best[i]=dt;}
 printf("inverse+crepmod3, ns:  GT reference %.1f | E1 %.1f | E2 fused %.1f | Official %.1f (copy-corrected %.1f)\n",
   best[0]/1e3,best[1]/1e3,best[2]/1e3,best[3]/1e3,(best[3]-best[4])/1e3);
 printf("in place, copy-corrected:  E2 fused %.1f | Official %.1f\n",(best[5]-best[6])/1e3,(best[3]-best[4])/1e3);
 return 0; }
