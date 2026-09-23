/* 1152 poly_baseinv alone, GT against Official, on an input both can invert. */
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
void o_poly_ntt(poly *); int o_poly_baseinv(poly *, const poly *); void o_poly_triple(poly *); void o_poly_cbd1(poly *, const uint8_t *);
static poly fg, fo, r; static uint8_t buf[NTRUPLUS_N/4]; static volatile int sink;
static uint32_t s = 11; static uint32_t rnd(void){ s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
static void g(void){ sink += poly_baseinv(&r, &fg); } static void o(void){ sink += o_poly_baseinv(&r, &fo); }
static double best(void (*f)(void)){ double b = 1e30; for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#else
  if (perf_counter_open()) return 2;
#endif
  for (;;) { for (int i = 0; i < (int)sizeof buf; i++) buf[i] = rnd();
    poly t; poly_cbd1(&t, buf); poly_triple(&t, &t); t.coeffs[0] += 1; fo = t; poly_ntt(&fg, &t); o_poly_ntt(&fo);
    if (!poly_baseinv(&r, &fg) && !o_poly_baseinv(&r, &fo)) break; }
#ifdef __APPLE__
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { g(); o(); } }
#endif
  printf("baseinv  GT %.1f  Official %.1f %s\n", best(g), best(o), UNIT); return 0; }
