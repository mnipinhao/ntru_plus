/* P137: throughput of tbl with 1..4 table registers (and trn1 for scale):
 * 16 independent ops per block, 2^20 blocks; reports cycles (A76 PMU) or ns
 * (M2) per op. */
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
#define R16(x) x x x x x x x x x x x x x x x x
#define OPS(op) \
  "1:\n" \
  op("v16") op("v17") op("v18") op("v19") op("v20") op("v21") op("v22") op("v23") \
  op("v24") op("v25") op("v26") op("v27") op("v28") op("v29") op("v30") op("v31") \
  "subs %x0, %x0, #1\n b.ne 1b\n"
#define T1(d) "tbl " d ".16b, {v0.16b}, v8.16b\n"
#define T2(d) "tbl " d ".16b, {v0.16b, v1.16b}, v8.16b\n"
#define T3(d) "tbl " d ".16b, {v0.16b, v1.16b, v2.16b}, v8.16b\n"
#define T4(d) "tbl " d ".16b, {v0.16b, v1.16b, v2.16b, v3.16b}, v8.16b\n"
#define TR(d) "trn1 " d ".8h, v0.8h, v1.8h\n"
#define RUN(name, op) static void name(uint64_t n){ __asm__ volatile(OPS(op) : "+r"(n) :: "v16","v17","v18","v19","v20","v21","v22","v23","v24","v25","v26","v27","v28","v29","v30","v31","cc"); }
RUN(r1, T1) RUN(r2, T2) RUN(r3, T3) RUN(r4, T4) RUN(rt, TR)
static double t(void (*f)(uint64_t)){ const uint64_t N = 1u << 20; double b = 1e30;
  for (int k = 0; k < 20; k++){
#ifdef __APPLE__
    uint64_t t0 = now(); f(N); double d = (double)(now() - t0);
#else
    perf_counter_start(); f(N); double d = (double)perf_counter_stop();
#endif
    d /= (double)(N * 16); if (d < b) b = d; }
  return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); while (now() - t1 < 3000000000ull) r1(1000); }
#else
  if (perf_counter_open()) return 2;
#endif
  double tr = t(rt);
  printf("per op (%s): trn1 %.3f  tbl1 %.3f  tbl2 %.3f  tbl3 %.3f  tbl4 %.3f   (relative to trn1: %.2f %.2f %.2f %.2f)\n", UNIT,
         tr, t(r1), t(r2), t(r3), t(r4), t(r1)/tr, t(r2)/tr, t(r3)/tr, t(r4)/tr);
  return 0; }
