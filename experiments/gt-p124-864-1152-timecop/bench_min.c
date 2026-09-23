/* P120: min-of-blocks per operation (M2: mach time at P-core QoS; Linux: perf cycles), all three ops interleaved. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "api.h"
int crypto_kem_keypair(unsigned char*,unsigned char*); int crypto_kem_enc(unsigned char*,unsigned char*,const unsigned char*); int crypto_kem_dec(unsigned char*,const unsigned char*,const unsigned char*);
static unsigned char pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES],ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],ss2[CRYPTO_BYTES];
static volatile unsigned sink;
static void kg(void){crypto_kem_keypair(pk,sk);} static void en(void){crypto_kem_enc(ct,ss,pk);} static void de(void){crypto_kem_dec(ss2,ct,sk); sink+=ss2[0];}
static void (*F[3])(void)={kg,en,de};
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#define UNIT "ns"
#define START() uint64_t t0=now()
#define STOP() (double)(now()-t0)
#else
#include "perf_counter.h"
#define UNIT "cycles"
#define START() perf_counter_start()
#define STOP() (double)perf_counter_stop()
#endif
int main(void){
#ifdef __APPLE__
 pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#else
 if(perf_counter_open()) return 2;
#endif
 kg(); en(); de(); for(int i=0;i<CRYPTO_BYTES;i++) if(ss[i]!=ss2[i]){puts("ss mismatch");return 1;}
 for(int w=0;w<3000;w++) for(int i=0;i<3;i++) F[i]();
 double best[3]={1e30,1e30,1e30}; enum{IT=100};
 const char *only=getenv("ONLY"); int lo=only?atoi(only):0, hi=only?atoi(only)+1:3;
 for(int r=0;r<400;r++) for(int i=lo;i<hi;i++){ START(); for(int k=0;k<IT;k++) F[i](); double d=STOP()/IT; if(d<best[i]) best[i]=d; }
 printf("keygen %.1f  encaps %.1f  decaps %.1f %s\n",best[0],best[1],best[2],UNIT); return 0; }
