#define _GNU_SOURCE
#include "pair_wait_tobytes.h"
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
void gt864_fr0_input_once_tobytes(uint8_t out[1296],const int16_t fr0[864]);
typedef void(*fn)(uint8_t*,const int16_t*);static fn f[2]={gt864_fr0_input_once_tobytes,gt864_fr0_pair_wait_tobytes};static const char*n[2]={"p3b6","pair_wait"};static int16_t in[864]__attribute__((aligned(16)));static uint8_t e[1296]__attribute__((aligned(16))),a[1296]__attribute__((aligned(16)));static volatile uint64_t sink;static uint32_t rng=1;static uint32_t next_u32(void){rng=rng*1664525u+1013904223u;return rng;}
static void check(void){for(int t=0;t<128;t++){for(int i=0;i<864;i++)in[i]=(int16_t)next_u32();f[0](e,in);f[1](a,in);if(memcmp(e,a,sizeof a))exit(1);}puts("p3b15_pi_correctness=pass cases=128");}
static int counter(uint64_t c,int g){struct perf_event_attr e={0};e.size=sizeof e;e.type=PERF_TYPE_HARDWARE;e.config=c;e.disabled=g<0;e.exclude_kernel=1;e.exclude_hv=1;e.read_format=PERF_FORMAT_GROUP;return(int)syscall(__NR_perf_event_open,&e,0,-1,g,0);}
int main(int argc,char**argv){check();if(argc==1)return 0;int rev=atoi(argv[1]),cy=counter(PERF_COUNT_HW_CPU_CYCLES,-1),ins=counter(PERF_COUNT_HW_INSTRUCTIONS,cy),br=counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,cy);if(cy<0||ins<0||br<0)return 2;for(int i=0;i<864;i++)in[i]=(int16_t)next_u32();for(int r=0;r<41;r++)for(int p=0;p<2;p++){int v=rev?1-p:p;struct{uint64_t count,value[3];}z;ioctl(cy,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);ioctl(cy,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);for(int j=0;j<400;j++)f[v](a,in);ioctl(cy,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);if(read(cy,&z,sizeof z)!=(ssize_t)sizeof z||z.count!=3)return 2;sink+=a[r%1296];printf("sample,to_%s,%.3f,%.3f,%.3f\n",n[v],z.value[0]/400.0,z.value[1]/400.0,z.value[2]/400.0);}return 0;}
