/* P118: keygen / encaps / decaps of one NTRU+768 tree.  M2: witness-gated best; Linux: perf-cycle median. */
#include <stdio.h>
#include <stdint.h>
#include "api.h"
int crypto_kem_keypair(unsigned char*,unsigned char*);
int crypto_kem_enc(unsigned char*,unsigned char*,const unsigned char*);
int crypto_kem_dec(unsigned char*,const unsigned char*,const unsigned char*);
static unsigned char pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES],ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],ss2[CRYPTO_BYTES];
static volatile unsigned sink;
static void kg(void){crypto_kem_keypair(pk,sk);} static void en(void){crypto_kem_enc(ct,ss,pk);} static void de(void){crypto_kem_dec(ss2,ct,sk); sink+=ss2[0];}
static void (*F[3])(void)={kg,en,de};
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline unsigned long long nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static unsigned long long witness(void){unsigned long long x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 unsigned long long d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
int main(void){ pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
 kg(); en(); de(); for(int i=0;i<CRYPTO_BYTES;i++) if(ss[i]!=ss2[i]){puts("ss mismatch");return 1;}
 unsigned long long wf=~0ull,best[3]={~0ull,~0ull,~0ull},t0=nsec(); int st=0;
 for(int w=0;w<4000;w++){ for(int i=0;i<3;i++) for(int k=0;k<100;k++) F[i]();
   unsigned long long d=witness(); if(d<wf){wf=d;st=0;} else st++; if(st>=5&&nsec()-t0>3000000000ull) break;}
 for(int r=0;r<201;r++) for(int i=0;i<3;i++){ unsigned long long x=nsec(); for(int k=0;k<200;k++) F[i](); unsigned long long dt=nsec()-x;
   unsigned long long d=witness(); if(d<wf) wf=d; if(d*98<=wf*100&&dt<best[i]) best[i]=dt;}
 printf("keygen %.1f  encaps %.1f  decaps %.1f ns\n",best[0]/200.0,best[1]/200.0,best[2]/200.0); return 0;}
#else
#include "perf_counter.h"
int main(void){ kg(); en(); de(); for(int i=0;i<CRYPTO_BYTES;i++) if(ss[i]!=ss2[i]){puts("ss mismatch");return 1;}
 if(perf_counter_open()) return 2; enum{NS=61,IT=500}; static double s[3][NS];
 for(int w=0;w<50;w++) for(int i=0;i<3;i++) F[i]();
 for(int n=0;n<NS;n++) for(int i=0;i<3;i++){ perf_counter_start(); for(int k=0;k<IT;k++) F[i](); s[i][n]=(double)perf_counter_stop()/IT; }
 double m[3]; for(int i=0;i<3;i++){ for(int a=0;a<NS;a++) for(int b=a+1;b<NS;b++) if(s[i][b]<s[i][a]){double t=s[i][a];s[i][a]=s[i][b];s[i][b]=t;} m[i]=s[i][NS/2]; }
 printf("keygen %.0f  encaps %.0f  decaps %.0f cycles\n",m[0],m[1],m[2]); perf_counter_close(); return 0;}
#endif
