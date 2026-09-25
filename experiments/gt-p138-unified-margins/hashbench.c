/* P138: GT's hash layer against Official's, per call, same permutation (GT's) on both sides.
 * Official's symmetric.c and sponge are compiled with orename.h (o_* names).  Rows are the
 * calls kem.c makes; the per-operation sums weight them by calls per operation. */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include "params.h"
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
#if NTRUPLUS_N == 1152
#define RETRIES 2.80           /* f and g attempts per key generation (P124) */
#else
#define RETRIES 2.0
#endif
void hash_f(uint8_t *, const uint8_t *); void hash_g(uint8_t *, const uint8_t *); void hash_h(uint8_t *, const uint8_t *);
void shake256(uint8_t *, size_t, const uint8_t *, size_t);
void o_hash_f(uint8_t *, const uint8_t *); void o_hash_g(uint8_t *, const uint8_t *); void o_hash_h(uint8_t *, const uint8_t *);
void o_shake256(uint8_t *, size_t, const uint8_t *, size_t);
static uint8_t in[NTRUPLUS_POLYBYTES + 64], out[NTRUPLUS_POLYBYTES];
static void g_seed(void){ shake256(out, NTRUPLUS_N / 4, in, 32); }   static void o_seed(void){ o_shake256(out, NTRUPLUS_N / 4, in, 32); }
static void g_f(void){ hash_f(out, in); } static void o_f(void){ o_hash_f(out, in); }
static void g_g(void){ hash_g(out, in); } static void o_g(void){ o_hash_g(out, in); }
static void g_h(void){ hash_h(out, in); } static void o_h(void){ o_hash_h(out, in); }
static double best(void (*f)(void)){ double b = 1e30; for (int w = 0; w < 3000; w++) f();
  for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { g_g(); o_g(); } }
#else
  if (perf_counter_open()) return 2;
#endif
  for (unsigned i = 0; i < sizeof in; i++) in[i] = (uint8_t)(i * 131 + 7);
  struct { const char *n; void (*g)(void), (*o)(void); double kg, ke, kd; } rows[] = {
    {"shake256 32 -> N/4 (cbd seed)", g_seed, o_seed, RETRIES, 0, 0},
    {"hash_f  (pk, POLYBYTES -> 32)", g_f, o_f, 1, 1, 0},
    {"hash_g  (POLYBYTES -> N/4)",    g_g, o_g, 0, 1, 1},
    {"hash_h  (N/8+32 -> 32+N/4)",    g_h, o_h, 0, 1, 1} };
  double s[3] = {0, 0, 0};
  printf("NTRU+%d hash layer, per call (%s), GT permutation on both sides\n", NTRUPLUS_N, UNIT);
  for (unsigned i = 0; i < 4; i++){ double x = best(rows[i].g), y = best(rows[i].o);
    printf("  %-32s GT %8.1f  Official %8.1f  %+8.1f\n", rows[i].n, x, y, x - y);
    s[0] += rows[i].kg * (x - y); s[1] += rows[i].ke * (x - y); s[2] += rows[i].kd * (x - y); }
  printf("  weighted by calls: keygen %+.0f  encaps %+.0f  decaps %+.0f %s\n", s[0], s[1], s[2], UNIT);
  return 0; }
