#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include "candidate.h"
enum{S=20};typedef void(*fn)(void);static volatile uint64_t sink;
static _Alignas(64) int16_t h[768],r[768],m[768],p[768],scratch[768];static uint8_t w[1152];static uint64_t st=19;
static uint32_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return st;}
static void a(void){gt103_basemul_general_ql2_avx2(p,h,r);gt103_pack_ql2_sum_avx2(w,p,m);sink+=w[0];}
static void b(void){gt105_b3_ql2_virtual_pack_direct_avx2(scratch,h,r,m,w);sink+=w[0];}
static int op(uint64_t c){struct perf_event_attr x;memset(&x,0,sizeof x);x.type=PERF_TYPE_HARDWARE;x.size=sizeof x;x.config=c;x.disabled=1;x.exclude_kernel=1;x.exclude_hv=1;return syscall(SYS_perf_event_open,&x,0,-1,-1,0UL);}
static double one(fn f,int n,int d){uint64_t v;ioctl(d,PERF_EVENT_IOC_RESET,0);ioctl(d,PERF_EVENT_IOC_ENABLE,0);for(int i=0;i<n;i++)f();ioctl(d,PERF_EVENT_IOC_DISABLE,0);if(read(d,&v,8)!=8)return 0;return(double)v/n;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return(x>y)-(x<y);}static double med(double*x){double y[S];memcpy(y,x,sizeof y);qsort(y,S,sizeof(double),cmp);return.5*(y[9]+y[10]);}
static void metric(const char*n,int d){double x[S],y[S],z[S];for(int i=0;i<S;i++){if(i&1){y[i]=one(b,2048,d);x[i]=one(a,2048,d);}else{x[i]=one(a,2048,d);y[i]=one(b,2048,d);}z[i]=y[i]-x[i];}printf("metric=%s control=%.3f candidate=%.3f delta=%.3f\n",n,med(x),med(y),med(z));}
int main(void){cpu_set_t c;CPU_ZERO(&c);CPU_SET(1,&c);if(sched_setaffinity(0,sizeof c,&c))return 2;for(int i=0;i<768;i++){h[i]=(int16_t)((int)(rnd()%3457)-1728);r[i]=(int16_t)((int)(rnd()%3457)-1728);m[i]=(int16_t)((int)(rnd()%21577)-10788);}for(int i=0;i<100;i++){a();b();}int cy=op(PERF_COUNT_HW_CPU_CYCLES),in=op(PERF_COUNT_HW_INSTRUCTIONS),br=op(PERF_COUNT_HW_BRANCH_INSTRUCTIONS),bm=op(PERF_COUNT_HW_BRANCH_MISSES),cm=op(PERF_COUNT_HW_CACHE_MISSES);if(cy<0||in<0||br<0||bm<0||cm<0)return 3;metric("core_cycles",cy);metric("instructions",in);metric("branches",br);metric("branch_misses",bm);metric("cache_misses",cm);printf("sink=%llu\n",(unsigned long long)sink);}
