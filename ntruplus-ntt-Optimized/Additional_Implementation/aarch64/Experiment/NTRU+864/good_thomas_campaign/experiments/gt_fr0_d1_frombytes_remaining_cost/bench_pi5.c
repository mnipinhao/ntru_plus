#define _GNU_SOURCE
#include "input_once_frombytes.h"
#include "p3b11_tables.h"
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
void stock_from(int16_t*out,const uint8_t*in);
void stock_shuffle(int16_t*out,const int16_t*in);
static void official_from(int16_t*out,const uint8_t*in){stock_from(out,in);stock_shuffle(out,out);}
typedef void(*fn)(int16_t*,const uint8_t*);static fn f[2]={official_from,gt864_fr0_input_once_frombytes};static const char*n[2]={"official_api","p3b11"};static uint8_t bytes[1296]__attribute__((aligned(16)));static int16_t a[864]__attribute__((aligned(16))),b[864]__attribute__((aligned(16)));static volatile uint64_t sink;static uint32_t rng=1;static uint32_t next_u32(void){rng=rng*1664525u+1013904223u;return rng;}
static void check(void){for(int t=0;t<256;t++){for(int i=0;i<1296;i++)bytes[i]=(uint8_t)next_u32();stock_from(a,bytes);gt864_fr0_input_once_frombytes(b,bytes);for(int i=0;i<864;i++)if(b[p3b11_forward_map[i]]!=a[i]){fprintf(stderr,"fail t=%d serialized=%d fr0=%u stock=%d candidate=%d\n",t,i,p3b11_forward_map[i],a[i],b[p3b11_forward_map[i]]);exit(1);}}puts("p3b17_correctness=pass cases=256 arbitrary_bytes exact_raw_to_FR0_map");}
static int counter(uint64_t c,int g){struct perf_event_attr e={0};e.size=sizeof e;e.type=PERF_TYPE_HARDWARE;e.config=c;e.disabled=g<0;e.exclude_kernel=1;e.exclude_hv=1;e.read_format=PERF_FORMAT_GROUP;return(int)syscall(__NR_perf_event_open,&e,0,-1,g,0);}
int main(int argc,char**argv){check();if(argc==1)return 0;int rev=atoi(argv[1]),cy=counter(PERF_COUNT_HW_CPU_CYCLES,-1),ins=counter(PERF_COUNT_HW_INSTRUCTIONS,cy),br=counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,cy);if(cy<0||ins<0||br<0)return 2;for(int r=0;r<41;r++)for(int p=0;p<2;p++){int v=rev?1-p:p;struct{uint64_t count,value[3];}z;ioctl(cy,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);ioctl(cy,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);for(int j=0;j<400;j++)f[v](b,bytes);ioctl(cy,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);if(read(cy,&z,sizeof z)!=(ssize_t)sizeof z||z.count!=3)return 2;sink+=(uint16_t)b[r%864];printf("sample,from_%s,%.3f,%.3f,%.3f\n",n[v],z.value[0]/400.0,z.value[1]/400.0,z.value[2]/400.0);}return 0;}
