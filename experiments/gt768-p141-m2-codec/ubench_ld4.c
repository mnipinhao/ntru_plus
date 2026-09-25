/* P141: throughput of structured loads/stores against plain ones, and of each beside SIMD work.
 * 8 independent ops per loop iteration over a 4 KiB L1-resident buffer; per op, ns (M2) / cycles. */
#include <stdio.h>
#include <stdint.h>
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#define UNIT "ns"
#else
#include "perf_counter.h"
#define UNIT "cyc"
#endif
static uint16_t buf[4096] __attribute__((aligned(64)));
#define LOOP(body) "1:\n" body "subs %x[n], %x[n], #1\n b.ne 1b\n"
#define L8(op) op op op op op op op op
#define RUN(name, body, clob...) static void name(uint64_t n){ uint16_t *p = buf; \
  __asm__ volatile(LOOP(body) : [n]"+r"(n) : [p]"r"(p) : "memory", "cc", clob); }
RUN(r_ld4,  L8("ld4 {v0.8h, v1.8h, v2.8h, v3.8h}, [%[p]]\n"), "v0","v1","v2","v3")
RUN(r_ld1x4, L8("ld1 {v0.8h, v1.8h, v2.8h, v3.8h}, [%[p]]\n"), "v0","v1","v2","v3")
RUN(r_ldq4, L8("ldp q0, q1, [%[p]]\n ldp q2, q3, [%[p], #32]\n"), "v0","v1","v2","v3")
RUN(r_st4,  L8("st4 {v0.8h, v1.8h, v2.8h, v3.8h}, [%[p]]\n"), "v0","v1","v2","v3")
RUN(r_st1x4, L8("st1 {v0.8h, v1.8h, v2.8h, v3.8h}, [%[p]]\n"), "v0","v1","v2","v3")
/* the same structured load beside 8 independent SIMD adds: does it take SIMD slots? */
RUN(r_add8, L8("add v16.8h, v17.8h, v18.8h\n add v19.8h, v20.8h, v21.8h\n add v22.8h, v23.8h, v24.8h\n add v25.8h, v26.8h, v27.8h\n"), "v16","v19","v22","v25")
RUN(r_ld4add, L8("ld4 {v0.8h, v1.8h, v2.8h, v3.8h}, [%[p]]\n add v16.8h, v17.8h, v18.8h\n add v19.8h, v20.8h, v21.8h\n add v22.8h, v23.8h, v24.8h\n add v25.8h, v26.8h, v27.8h\n"), "v0","v1","v2","v3","v16","v19","v22","v25")
RUN(r_ld1add, L8("ld1 {v0.8h, v1.8h, v2.8h, v3.8h}, [%[p]]\n add v16.8h, v17.8h, v18.8h\n add v19.8h, v20.8h, v21.8h\n add v22.8h, v23.8h, v24.8h\n add v25.8h, v26.8h, v27.8h\n"), "v0","v1","v2","v3","v16","v19","v22","v25")
static double t(void (*f)(uint64_t)){ const uint64_t N = 1 << 18; double b = 1e30;
  for (int k = 0; k < 20; k++){
#ifdef __APPLE__
    uint64_t t0 = now(); f(N); double d = (double)(now() - t0);
#else
    perf_counter_start(); f(N); double d = (double)perf_counter_stop();
#endif
    d /= (double)(N * 8); if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) r_add8(1000); }
#else
  if (perf_counter_open()) return 2;
#endif
  double a = t(r_add8);
  printf("per iteration of 8 (%s): ld4 %.3f  ld1x4 %.3f  2x ldp q %.3f  st4 %.3f  st1x4 %.3f\n", UNIT, t(r_ld4), t(r_ld1x4), t(r_ldq4), t(r_st4), t(r_st1x4));
  printf("4 SIMD adds alone %.3f; with an ld4 %.3f; with an ld1x4 %.3f\n", a, t(r_ld4add), t(r_ld1add));
  return 0; }
