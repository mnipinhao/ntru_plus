#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "poly.h"
unsigned long g_ph[4]; static int fd;
unsigned long pmu_read(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return (unsigned long)v;}
int baseinv_asm(int16_t*, const int16_t*);
static int16_t a[NTRUPLUS_N], o[NTRUPLUS_N];
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0); if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint64_t s=1; for(int i=0;i<NTRUPLUS_N;i++){s^=s<<13;s^=s>>7;s^=s<<17;a[i]=(int16_t)(s%3457)-1728;}
    for(int i=0;i<50;i++) baseinv_asm(o,a);
    g_ph[0]=g_ph[1]=g_ph[2]=0;
    const int R=5000; unsigned long t=pmu_read();
    for(int i=0;i<R;i++) baseinv_asm(o,a);
    double tot=(double)(pmu_read()-t)/R;
    printf("baseinv total       %7.1f cycles\n", tot);
    printf("  numerator loop    %7.1f  (%4.1f%%)\n", (double)g_ph[0]/R, 100.0*g_ph[0]/R/tot);
    printf("  prefix+inv+recover%7.1f  (%4.1f%%)   <- serial\n", (double)g_ph[1]/R, 100.0*g_ph[1]/R/tot);
    printf("  finish loop       %7.1f  (%4.1f%%)\n", (double)g_ph[2]/R, 100.0*g_ph[2]/R/tot);
    return 0;
}
