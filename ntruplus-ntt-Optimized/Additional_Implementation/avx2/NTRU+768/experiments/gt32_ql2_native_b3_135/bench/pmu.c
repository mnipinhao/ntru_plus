#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdlib.h>
#define N 768
void gt103_basemul_general_ql2_avx2(int16_t*,const int16_t*,const int16_t*);
void gt135_basemul_general_ql2_native_e0(int16_t*,const int16_t*,const int16_t*);
static _Alignas(64) int16_t a[N],b[N],o[N];static volatile uint64_t sink;
int main(int argc,char**argv){int candidate=argc>1?atoi(argv[1]):0;cpu_set_t s;CPU_ZERO(&s);CPU_SET(1,&s);sched_setaffinity(0,sizeof s,&s);for(int i=0;i<N;i++){a[i]=(int16_t)(i%1700);b[i]=(int16_t)((i*7)%1700);}for(int z=0;z<200000;z++){if(candidate)gt135_basemul_general_ql2_native_e0(o,a,b);else gt103_basemul_general_ql2_avx2(o,a,b);sink+=(uint16_t)o[z%N];}return sink==UINT64_MAX;}
