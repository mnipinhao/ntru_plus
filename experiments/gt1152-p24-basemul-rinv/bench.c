#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "poly.h"
void basemul_rinv_asm(int16_t*, const int16_t*, const int16_t*);
static int fd; static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)_exit(3);return v;}
static int16_t a[NTRUPLUS_N], b[NTRUPLUS_N], o[NTRUPLUS_N];
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint64_t s=1;
    for(int i=0;i<NTRUPLUS_N;i++){s^=s<<13;s^=s>>7;s^=s<<17;a[i]=(int16_t)(s%4096);
                                  s^=s<<13;s^=s>>7;s^=s<<17;b[i]=(int16_t)(s%4096);}
    for(int i=0;i<200;i++) basemul_rinv_asm(o,a,b);
    const int R=20000; uint64_t t=rd();
    for(int i=0;i<R;i++) basemul_rinv_asm(o,a,b);
    printf("basemul_rinv: %7.1f cycles   (floor 2376, official basemul_scale 2551)\n",(double)(rd()-t)/R);
    return 0;
}
