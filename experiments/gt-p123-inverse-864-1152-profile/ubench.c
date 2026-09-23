/* A76/M2 throughput of Q-form 16-bit ops: 8 independent chains, 1e7 iterations. */
#include <stdio.h>
#include <stdint.h>
#include <time.h>
static uint64_t ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1000000000ull+t.tv_nsec;}
#define R8(op) op" v0.8h,v0.8h,v31.8h\n" op" v1.8h,v1.8h,v31.8h\n" op" v2.8h,v2.8h,v31.8h\n" op" v3.8h,v3.8h,v31.8h\n" \
               op" v4.8h,v4.8h,v31.8h\n" op" v5.8h,v5.8h,v31.8h\n" op" v6.8h,v6.8h,v31.8h\n" op" v7.8h,v7.8h,v31.8h\n"
#define B(name, body) static double name(long n){uint64_t t=ns(); for(long i=0;i<n;i++) __asm__ volatile(body R8("add") ::: "v0","v1","v2","v3","v4","v5","v6","v7"); return (double)(ns()-t)/n;}
B(t_add,  R8("add"))
B(t_mul,  R8("mul"))
B(t_sqrd, R8("sqrdmulh"))
B(t_mls,  R8("mls"))
B(t_mix,  R8("mul") R8("add"))
B(t_ext,  R8("trn1"))
static double t_base(long n){uint64_t t=ns(); for(long i=0;i<n;i++) __asm__ volatile(R8("add") R8("add") ::: "v0","v1","v2","v3","v4","v5","v6","v7"); return (double)(ns()-t)/n;}
int main(void){ long n=10000000; t_base(n);
  double a=t_base(n)/2;  /* ns per 8 adds */
  printf("ns per 8 ops (minus 8 adds): add %.3f mul %.3f sqrdmulh %.3f mls %.3f  mul+add(16) %.3f trn1 %.3f   [8 adds = %.3f ns]\n",
   t_add(n)-a, t_mul(n)-a, t_sqrd(n)-a, t_mls(n)-a, t_mix(n)-a, t_ext(n)-a, a);
}
