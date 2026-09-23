/* A76: throughput of smull/smlal, and whether zip/trn issue alongside them. */
#include <stdio.h>
#include <stdint.h>
#include "perf_counter.h"
#define S8(op) op " v16.4s, v0.4h, v1.4h\n" op " v17.4s, v0.4h, v1.4h\n" op " v18.4s, v0.4h, v1.4h\n" op " v19.4s, v0.4h, v1.4h\n" \
               op " v20.4s, v0.4h, v1.4h\n" op " v21.4s, v0.4h, v1.4h\n" op " v22.4s, v0.4h, v1.4h\n" op " v23.4s, v0.4h, v1.4h\n"
#define Z8 "zip1 v24.4s, v2.4s, v3.4s\nzip1 v25.4s, v2.4s, v3.4s\nzip1 v26.4s, v2.4s, v3.4s\nzip1 v27.4s, v2.4s, v3.4s\n" \
           "zip2 v28.4s, v2.4s, v3.4s\nzip2 v29.4s, v2.4s, v3.4s\nzip2 v30.4s, v2.4s, v3.4s\nzip2 v31.4s, v2.4s, v3.4s\n"
#define CL "v16","v17","v18","v19","v20","v21","v22","v23","v24","v25","v26","v27","v28","v29","v30","v31"
#define B(name, body) static double name(void){ perf_counter_start(); for(int i=0;i<100000;i++) __asm__ volatile(body ::: CL); return perf_counter_stop()/100000.0; }
B(t_smull, S8("smull") S8("smull"))
B(t_smlal, S8("smlal") S8("smlal"))
B(t_zip, Z8 Z8)
B(t_mix, S8("smull") S8("smull") Z8 Z8)
int main(void){ if(perf_counter_open()) return 2; t_mix();
  printf("16 smull %.1f  16 smlal %.1f  16 zip %.1f  16 smull + 16 zip %.1f cycles\n", t_smull(), t_smlal(), t_zip(), t_mix()); }
