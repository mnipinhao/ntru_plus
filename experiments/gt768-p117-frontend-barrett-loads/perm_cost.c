/* P117: throughput cost of permutes/stores inside a SIMD-saturated loop (16 independent adds). */
#include <stdio.h>
#include <time.h>
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline unsigned long long now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#define GHZ 3.497
#else
#include "perf_counter.h"
#endif
#define N 20000000L
static short buf[4096] __attribute__((aligned(64)));
#define ADDS "add v0.8h,v0.8h,v16.8h\n add v1.8h,v1.8h,v16.8h\n add v2.8h,v2.8h,v16.8h\n add v3.8h,v3.8h,v16.8h\n add v4.8h,v4.8h,v16.8h\n add v5.8h,v5.8h,v16.8h\n add v6.8h,v6.8h,v16.8h\n add v7.8h,v7.8h,v16.8h\n add v8.8h,v8.8h,v16.8h\n add v9.8h,v9.8h,v16.8h\n add v10.8h,v10.8h,v16.8h\n add v11.8h,v11.8h,v16.8h\n add v12.8h,v12.8h,v16.8h\n add v13.8h,v13.8h,v16.8h\n add v14.8h,v14.8h,v16.8h\n add v15.8h,v15.8h,v16.8h\n"
#define CL "memory","cc","v0","v1","v2","v3","v4","v5","v6","v7","v8","v9","v10","v11","v12","v13","v14","v15","v20","v21","v22","v23","v24","v25","v26","v27"
#define LOOP(body) __asm__ volatile("1:\n" ADDS body " subs %0,%0,#1\n b.ne 1b":"+r"(n),"+r"(p)::CL)
static double run(int v){ double best=1e30;
 for(int r=0;r<5;r++){ long n=N; short*p=buf;
#ifdef __APPLE__
  unsigned long long t=now();
#else
  perf_counter_start();
#endif
  switch(v){
  case 0: LOOP(""); break;
  case 1: LOOP("st4 {v20.8h-v23.8h},[%1]\n"); break;
  case 2: LOOP("st1 {v20.8h-v23.8h},[%1]\n"); break;
  case 3: LOOP("zip1 v24.8h,v20.8h,v21.8h\n zip2 v25.8h,v20.8h,v21.8h\n zip1 v26.8h,v22.8h,v23.8h\n zip2 v27.8h,v22.8h,v23.8h\n"); break;
  case 4: LOOP("tbl v24.16b,{v20.16b},v17.16b\n tbl v25.16b,{v21.16b},v17.16b\n tbl v26.16b,{v22.16b},v17.16b\n tbl v27.16b,{v23.16b},v17.16b\n"); break;
  case 5: LOOP("tbl v24.16b,{v20.16b,v21.16b},v17.16b\n tbl v25.16b,{v20.16b,v21.16b},v18.16b\n tbl v26.16b,{v22.16b,v23.16b},v17.16b\n tbl v27.16b,{v22.16b,v23.16b},v18.16b\n"); break;
  case 6: LOOP("uzp2 v24.8h,v20.8h,v21.8h\n uzp2 v25.8h,v20.8h,v21.8h\n uzp2 v26.8h,v22.8h,v23.8h\n uzp2 v27.8h,v22.8h,v23.8h\n"); break;
  case 7: LOOP("tbl v24.16b,{v20.16b-v23.16b},v17.16b\n tbl v25.16b,{v20.16b-v23.16b},v18.16b\n tbl v26.16b,{v20.16b-v23.16b},v17.16b\n tbl v27.16b,{v20.16b-v23.16b},v18.16b\n"); break;
  case 8: LOOP("tbl v24.16b,{v20.16b-v22.16b},v17.16b\n tbl v25.16b,{v20.16b-v22.16b},v18.16b\n tbl v26.16b,{v20.16b-v22.16b},v17.16b\n tbl v27.16b,{v20.16b-v22.16b},v18.16b\n"); break;
  }
#ifdef __APPLE__
  double c=(now()-t)*GHZ/N;
#else
  double c=(double)perf_counter_stop()/N;
#endif
  if(c<best) best=c; }
 return best; }
int main(void){
#ifdef __APPLE__
 pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#else
 if(perf_counter_open()) return 2;
#endif
 const char*nm[9]={"16 add (base)","+ st4 {4}.8h","+ st1 {4}.8h","+ 4 zip .8h","+ 4 tbl 1-reg","+ 4 tbl 2-reg","+ 4 uzp2 .8h","+ 4 tbl 4-reg","+ 4 tbl 3-reg"};
 double b=run(0); printf("%-16s %.2f cycles\n",nm[0],b);
 for(int v=1;v<9;v++){ double c=run(v); printf("%-16s %.2f cycles (+%.2f)\n",nm[v],c,c-b); } return 0; }
