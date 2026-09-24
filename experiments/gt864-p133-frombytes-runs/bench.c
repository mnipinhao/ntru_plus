/* P133: production frombytes against frombytes_runs, same binary. */
#include <stdio.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
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
#define UNIT "cyc"
#define START() perf_counter_start()
#define STOP() (double)perf_counter_stop()
#endif
int poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
int frombytes_runs(int16_t out[864], const uint8_t in[1296]);
static uint8_t in[NTRUPLUS_POLYBYTES]; static poly r; static volatile int sink;
static void f_old(void){ sink += poly_frombytes(&r, in); }
static void f_new(void){ sink += frombytes_runs(r.coeffs, in); }
static double best(void (*f)(void)){ double b = 1e30; for (int w = 0; w < 5000; w++) f();
  for (int k = 0; k < 400; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { f_old(); f_new(); } }
#else
  if (perf_counter_open()) return 2;
#endif
  poly a; uint32_t s = 7; for (int i = 0; i < NTRUPLUS_N; i++){ s ^= s << 13; s ^= s >> 17; s ^= s << 5; a.coeffs[i] = s % 3457; }
  poly_tobytes(in, &a);
  for (int r_ = 0; r_ < 3; r_++) printf("frombytes  production %.1f  runs %.1f %s\n", best(f_old), best(f_new), UNIT);
  return 0; }
