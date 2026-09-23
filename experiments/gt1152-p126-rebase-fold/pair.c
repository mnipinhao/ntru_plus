/* basemul_rinv, the inverse, and the pair, as decapsulation calls them. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
#include "poly.h"
#include "inverse.h"
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
void poly_basemul_rinv(int16_t *out, const int16_t *a, const int16_t *b);
static poly c, f, m, m0; static uint8_t scratch[POLY_INVNTT_TERNARY_SCRATCHBYTES]; static volatile int sink;
static void bm(void){ poly_basemul_rinv(m.coeffs, c.coeffs, f.coeffs); }
static void inv(void){ memcpy(&m, &m0, sizeof m); poly_invntt_ternary(&m, &m, scratch); }
static void cp(void){ memcpy(&m, &m0, sizeof m); }
static void both(void){ poly_basemul_rinv(m.coeffs, c.coeffs, f.coeffs); poly_invntt_ternary(&m, &m, scratch); }
int main(void){
#ifdef __APPLE__
 pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#else
 if(perf_counter_open()) return 2;
#endif
 uint32_t s=5; for(int i=0;i<NTRUPLUS_N;i++){ s^=s<<13; s^=s>>17; s^=s<<5; c.coeffs[i]=s%3457; s^=s<<13; s^=s>>17; s^=s<<5; f.coeffs[i]=s%3457; }
 bm(); m0 = m; both(); uint32_t h=0; for(int i=0;i<NTRUPLUS_N;i++) h=h*31+(uint16_t)m.coeffs[i];
 void (*F[4])(void)={bm,inv,cp,both}; const char *nm[4]={"basemul","inv+copy","copy","pair"};
 double best[4]={1e30,1e30,1e30,1e30};
 for(int w=0;w<20000;w++) for(int i=0;i<4;i++) F[i]();
 for(int r=0;r<300;r++) for(int i=0;i<4;i++){ START(); for(int k=0;k<100;k++) F[i](); double d=STOP()/100; if(d<best[i]) best[i]=d; }
 printf("basemul %.1f  inverse %.1f  pair %.1f %s   (hash %08x)\n", best[0], best[1]-best[2], best[3], UNIT, h); return 0; }
