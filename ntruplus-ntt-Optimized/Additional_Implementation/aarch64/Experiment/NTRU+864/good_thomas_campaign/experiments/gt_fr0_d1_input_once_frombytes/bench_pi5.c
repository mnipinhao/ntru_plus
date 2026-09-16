#define _GNU_SOURCE
#include "input_once_frombytes.h"
#include "p3b11_tables.h"

#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>

void p3b11_baseline_c1_from(int16_t out[864], const uint8_t in[1296]);
typedef void (*from_fn)(int16_t *, const uint8_t *);
static from_fn functions[2]={p3b11_baseline_c1_from,gt864_fr0_input_once_frombytes};
static const char *names[2]={"c1","input_once"};
static uint8_t input[1296] __attribute__((aligned(16)));
static int16_t expected[864] __attribute__((aligned(16)));
static int16_t actual[864] __attribute__((aligned(16)));
static volatile uint64_t sink;
static uint32_t rng=1;
static uint32_t next_u32(void){rng=rng*1664525u+1013904223u;return rng;}

static uint16_t coefficient(const uint8_t *in,int index)
{
    int pair=index/2;
    return (index&1)==0?(uint16_t)(in[3*pair]|((uint16_t)(in[3*pair+1]&15)<<8)):
        (uint16_t)((in[3*pair+1]>>4)|((uint16_t)in[3*pair+2]<<4));
}
static void oracle(void)
{
    for(int i=0;i<864;i++)expected[p3b11_forward_map[i]]=(int16_t)coefficient(input,i);
}
static void check(void)
{
    for(int test=0;test<128;test++) {
        for(int i=0;i<1296;i++)input[i]=test==0?(uint8_t)i:
            test==1?0:test==2?255:(uint8_t)next_u32();
        oracle();
        for(int v=0;v<2;v++) {
            memset(actual,0xa5,sizeof actual);functions[v](actual,input);
            if(memcmp(expected,actual,sizeof actual)) {
                fprintf(stderr,"correctness fail test=%d variant=%s\n",test,names[v]);
                exit(1);
            }
        }
    }
    puts("p3b11_pi_correctness=pass cases=128 coefficients=864");
}
static int open_counter(uint64_t config,int group)
{
    struct perf_event_attr event={0};event.size=sizeof event;
    event.type=PERF_TYPE_HARDWARE;event.config=config;event.disabled=group<0;
    event.exclude_kernel=1;event.exclude_hv=1;event.read_format=PERF_FORMAT_GROUP;
    return (int)syscall(__NR_perf_event_open,&event,0,-1,group,0);
}
int main(int argc,char **argv)
{
    check();if(argc==1)return 0;int reverse=atoi(argv[1]);
    int cycles=open_counter(PERF_COUNT_HW_CPU_CYCLES,-1);
    int instructions=open_counter(PERF_COUNT_HW_INSTRUCTIONS,cycles);
    int branches=open_counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,cycles);
    if(cycles<0||instructions<0||branches<0){perror("perf_event_open");return 2;}
    for(int i=0;i<1296;i++)input[i]=(uint8_t)next_u32();
    for(int repetition=0;repetition<41;repetition++)for(int position=0;position<2;position++) {
        int variant=reverse?1-position:position;
        struct {uint64_t count,value[3];} result;
        ioctl(cycles,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);
        ioctl(cycles,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
        for(int iteration=0;iteration<400;iteration++)functions[variant](actual,input);
        ioctl(cycles,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);
        if(read(cycles,&result,sizeof result)!=(ssize_t)sizeof result||result.count!=3)return 2;
        sink+=(uint16_t)actual[repetition%864];
        printf("sample,from_%s,%.3f,%.3f,%.3f\n",names[variant],
               result.value[0]/400.0,result.value[1]/400.0,result.value[2]/400.0);
    }
    return 0;
}
