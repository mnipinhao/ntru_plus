/* P116 E3: decap first product + inverse + crepmod3, Official chain vs Official front-end (st4 store) + GT E3 inverse. */
#include <stdio.h>
#include <string.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
int e3_poly_frombytes_basemul_decap_scale(poly*,poly*,const unsigned char*,const unsigned char*);
void e3_poly_invntt(poly*,const poly*);
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline unsigned long long nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static unsigned long long witness(void);
#else
#include "perf_counter.h"
#endif
static volatile unsigned sink;
#ifdef __APPLE__
static unsigned long long witness(void){unsigned long long x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 unsigned long long d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
#endif
static unsigned char ct[NTRUPLUS_POLYBYTES],fb[NTRUPLUS_POLYBYTES];
static poly m,c,pin;
static unsigned rng=4242; static unsigned rnd(void){rng=rng*1103515245u+12345u; return rng>>8;}
static int k_off(void){int r=poly_frombytes_basemul_decap_scale(&m,&c,ct,fb); poly_invntt_decap_scale(&m); poly_crepmod3(&m,&m); return r+m.coeffs[3];}
static int k_e3(void){int r=e3_poly_frombytes_basemul_decap_scale(&m,&c,ct,fb); e3_poly_invntt(&m,&m); return r+m.coeffs[3];}
static int k_ofe(void){return poly_frombytes_basemul_decap_scale(&m,&c,ct,fb)+m.coeffs[3];}
static int k_efe(void){return e3_poly_frombytes_basemul_decap_scale(&m,&c,ct,fb)+m.coeffs[3];}
static int k_oinv(void){m=pin; poly_invntt_decap_scale(&m); poly_crepmod3(&m,&m); return m.coeffs[3];}
static int k_einv(void){m=pin; e3_poly_invntt(&m,&m); return m.coeffs[3];}
static int k_cp(void){m=pin; return m.coeffs[3];}
#define NK 7
static int (*F[NK])(void)={k_off,k_e3,k_ofe,k_efe,k_oinv,k_einv,k_cp};
int main(void){
#ifdef __APPLE__
 pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
 poly t,a,ca,b,cb; long bad=0,badc=0,badr=0;
 for(int trial=0;trial<3000;trial++){
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(trial<4?(trial&1?NTRUPLUS_Q-1:0):rnd()%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
   if(trial%10==9){ int k=rnd()%NTRUPLUS_POLYBYTES; ct[k]|=0xff; if(k+1<NTRUPLUS_POLYBYTES) ct[k+1]|=0x0f; }   /* malformed */
   int ra=poly_frombytes_basemul_decap_scale(&a,&ca,ct,fb); poly_invntt_decap_scale(&a); poly_crepmod3(&a,&a);
   int rb=e3_poly_frombytes_basemul_decap_scale(&b,&cb,ct,fb); e3_poly_invntt(&b,&b);
   badr+= (ra!=0)!=(rb!=0);
   for(int i=0;i<NTRUPLUS_N;i++){ badc+=ca.coeffs[i]!=cb.coeffs[i]; if(!ra) bad+=a.coeffs[i]!=b.coeffs[i]; } }
 printf("E3 chain vs Official chain: %ld output, %ld decoded_ct, %ld fail-flag mismatches (3000 trials, 10%% malformed)\n",bad,badc,badr);
 if(bad||badc||badr) return 1;
 for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
 for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
 e3_poly_frombytes_basemul_decap_scale(&pin,&c,ct,fb);
 const char*nm[NK]={"chain  Official","chain  E3","front  Official (st1)","front  E3 (st4)","inv+crepmod3 Official","inv+crepmod3 E3","copy"};
 double v[NK];
#ifdef __APPLE__
 unsigned long long wf=~0ull,best[NK],t0=nsec(); int st=0; for(int i=0;i<NK;i++) best[i]=~0ull;
 for(int w=0;w<4000;w++){ for(int i=0;i<NK;i++) for(int k=0;k<500;k++) sink+=F[i]();
   unsigned long long d=witness(); if(d<wf){wf=d;st=0;} else st++; if(st>=5&&nsec()-t0>3000000000ull) break;}
 for(int r=0;r<301;r++) for(int i=0;i<NK;i++){ unsigned long long x=nsec(); for(int k=0;k<1000;k++) sink+=F[i](); unsigned long long dt=nsec()-x;
   unsigned long long d=witness(); if(d<wf) wf=d; if(d*98<=wf*100&&dt<best[i]) best[i]=dt;}
 for(int i=0;i<NK;i++) v[i]=best[i]/1e3; const char*u="ns";
#else
 if(perf_counter_open()) return 2; enum{NS=61,IT=2000}; static double smp[NK][NS];
 for(int w=0;w<200;w++) for(int i=0;i<NK;i++) sink+=F[i]();
 for(int s=0;s<NS;s++) for(int i=0;i<NK;i++){ perf_counter_start(); for(int k=0;k<IT;k++) sink+=F[i](); smp[i][s]=(double)perf_counter_stop()/IT; }
 for(int i=0;i<NK;i++){ for(int a1=0;a1<NS;a1++) for(int b1=a1+1;b1<NS;b1++) if(smp[i][b1]<smp[i][a1]){double q=smp[i][a1];smp[i][a1]=smp[i][b1];smp[i][b1]=q;} v[i]=smp[i][NS/2]; }
 const char*u="cycles";
#endif
 for(int i=0;i<NK;i++) printf("  %-24s %8.1f %s%s\n",nm[i],(i>=4&&i<6)?v[i]-v[6]:v[i],u,(i>=4&&i<6)?" (copy-corrected)":"");
 printf("  chain delta: %+.1f %s (%+.2f%%)\n",v[1]-v[0],u,100.0*(v[1]-v[0])/v[0]);
 return 0; }
