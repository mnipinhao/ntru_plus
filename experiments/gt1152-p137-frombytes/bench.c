/* P137: production frombytes_asm, candidate A (C and asm) and SUPERCOP's Official
 * poly_frombytes (renamed o_poly_frombytes), same binary. */
#include <stdio.h>
#include <stdint.h>
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
int frombytes_asm(int16_t out[1152], const uint8_t in[1728]);
int frombytes_tbl2(int16_t out[1152], const uint8_t in[1728]);
int frombytes_tbl2_asm(int16_t out[1152], const uint8_t in[1728]);
int o_poly_frombytes(int16_t out[1152], const uint8_t in[1728]);
static uint8_t in[1728]; static int16_t r[1152] __attribute__((aligned(16))); static volatile int sink;
static void f_prod(void){ sink += frombytes_asm(r, in); }
static void f_tbl2(void){ sink += frombytes_tbl2(r, in); }
static void f_tasm(void){ sink += frombytes_tbl2_asm(r, in); }
static void f_off(void){ sink += o_poly_frombytes(r, in); }
static double best(void (*f)(void)){ double b = 1e30; for (int w = 0; w < 5000; w++) f();
  for (int k = 0; k < 400; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) { f_prod(); f_tbl2(); f_tasm(); f_off(); } }
#else
  if (perf_counter_open()) return 2;
#endif
  uint32_t s = 7; for (int k = 0; k < 576; k++){ int c[2]; for (int j = 0; j < 2; j++){ s ^= s << 13; s ^= s >> 17; s ^= s << 5; c[j] = s % 3457; }
    in[3*k] = c[0]; in[3*k+1] = (c[0] >> 8) | (c[1] << 4); in[3*k+2] = c[1] >> 4; }
  for (int i = 0; i < 3; i++) printf("frombytes  production %.1f  candidate A (C) %.1f  candidate A (asm) %.1f  Official %.1f %s\n", best(f_prod), best(f_tbl2), best(f_tasm), best(f_off), UNIT);
  return 0; }
