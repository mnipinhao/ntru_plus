/* P116 E2: fused inverse + crepmod3 vs (reference or E1) inverse then crepmod3, and Official's pair. */
#include <stdio.h>
#include <stdlib.h>
#include "perf_counter.h"
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
#include "test/reference/poly_reference.h"
void e1_poly_invntt(poly*,const poly*);
void e2t_poly_invntt(poly*,const poly*);
static volatile unsigned sink;
static poly gin,oin,b;
static unsigned rng=777; static unsigned rnd(void){rng=rng*1103515245u+12345u; return rng>>8;}
static int k_ref(void){poly_invntt(&b,&gin); poly_crepmod3(&b,&b); return b.coeffs[3];}
static int k_e1(void){e1_poly_invntt(&b,&gin); poly_crepmod3(&b,&b); return b.coeffs[3];}
static int k_e2t(void){e2t_poly_invntt(&b,&gin); return b.coeffs[3];}
static int k_off(void){b=oin; poly_invntt_decap_scale(&b); poly_crepmod3(&b,&b); return b.coeffs[3];}
static int k_cp(void){b=oin; return b.coeffs[3];}
static int k_e2t_ip(void){b=gin; e2t_poly_invntt(&b,&b); return b.coeffs[3];}
static int k_cpg(void){b=gin; return b.coeffs[3];}
int main(void){
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
 if(perf_counter_open()) return 2;
 enum{NS=61,IT=2000}; static double smp[7][NS];
 for(int w=0;w<200;w++) for(int i=0;i<7;i++) sink+=F[i]();
 for(int s=0;s<NS;s++) for(int i=0;i<7;i++){ perf_counter_start(); for(int k=0;k<IT;k++) sink+=F[i](); smp[i][s]=(double)perf_counter_stop()/IT; }
 double med[7]; for(int i=0;i<7;i++){ for(int a=0;a<NS;a++) for(int b2=a+1;b2<NS;b2++) if(smp[i][b2]<smp[i][a]){double t=smp[i][a];smp[i][a]=smp[i][b2];smp[i][b2]=t;} med[i]=smp[i][NS/2]; }
 printf("A76 cycles, inverse+crepmod3:  GT reference %.0f | E1 %.0f | E2 fused %.0f | Official %.0f (copy-corrected %.0f)\n",med[0],med[1],med[2],med[3],med[3]-med[4]);
 printf("in place, copy-corrected:  E2 fused %.0f | Official %.0f\n",med[5]-med[6],med[3]-med[4]);
 perf_counter_close(); return 0; }
