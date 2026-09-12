#define _GNU_SOURCE
#include "p9_tobytes.h"
#include "p14_tobytes.h"
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

typedef void (*to_fn)(uint8_t *,const int16_t *);
static to_fn functions[4]={gt864_p9_tobytes_full_asm,gt864_p14_tobytes_full_asm,
                           gt864_p9_tobytes_small_asm,gt864_p14_tobytes_small_asm};
static const char *names[4]={"p9_full","p14_full","p9_small","p14_small"};
static int16_t input[864] __attribute__((aligned(16)));
static uint8_t expected[1296] __attribute__((aligned(16))),actual[1296] __attribute__((aligned(16)));
static volatile uint64_t sink;static uint32_t rng=1;
static uint32_t next_u32(void){rng=rng*1664525u+1013904223u;return rng;}
static void check(void){
 for(int mode=0;mode<2;mode++)for(int test=0;test<256;test++){
  for(int i=0;i<864;i++)input[i]=mode?(int16_t)((int)(next_u32()%6913)-3456):(int16_t)next_u32();
  functions[2*mode](expected,input);functions[2*mode+1](actual,input);
  if(memcmp(expected,actual,sizeof actual))exit(1);
 }
 puts("p14_pi_correctness=pass full=256 small=256");
}
static int open_counter(uint64_t config,int group){struct perf_event_attr e={0};e.size=sizeof e;e.type=PERF_TYPE_HARDWARE;e.config=config;e.disabled=group<0;e.exclude_kernel=1;e.exclude_hv=1;e.read_format=PERF_FORMAT_GROUP;return(int)syscall(__NR_perf_event_open,&e,0,-1,group,0);}
int main(int argc,char **argv){
 check();if(argc==1)return 0;int reverse=atoi(argv[1]);
 int cycles=open_counter(PERF_COUNT_HW_CPU_CYCLES,-1),instructions=open_counter(PERF_COUNT_HW_INSTRUCTIONS,cycles),branches=open_counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,cycles);if(cycles<0||instructions<0||branches<0)return 2;
 for(int mode=0;mode<2;mode++)for(int repetition=0;repetition<41;repetition++)for(int position=0;position<2;position++){
  int candidate=reverse?1-position:position,variant=2*mode+candidate;struct{uint64_t count,value[3];}result;
  ioctl(cycles,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);ioctl(cycles,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
  for(int iteration=0;iteration<400;iteration++)functions[variant](actual,input);
  ioctl(cycles,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);if(read(cycles,&result,sizeof result)!=(ssize_t)sizeof result||result.count!=3)return 2;
  sink+=actual[(mode*41+repetition)%1296];printf("sample,%s,%.3f,%.3f,%.3f\n",names[variant],result.value[0]/400.0,result.value[1]/400.0,result.value[2]/400.0);
 }
 return 0;
}
