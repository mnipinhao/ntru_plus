#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#define N 1152
int poly_sotp_decode(uint8_t*, const int16_t*, const uint8_t*);
int old_sotp_decode(uint8_t*, const int16_t*, const uint8_t*);
static int fd; static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)_exit(3);return v;}
static int16_t a[N]; static uint8_t buf[N/4], m1[N/8], m2[N/8];
static volatile int sink;
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint64_t s=1; for(size_t i=0;i<N/4;i++){s^=s<<13;s^=s>>7;s^=s<<17;buf[i]=(uint8_t)s;}
    for(int i=0;i<N;i++){s^=s<<13;s^=s>>7;s^=s<<17;
        a[i]=(int16_t)((int)(s&1)-((buf[N/8+i/8]>>(i%8))&1));}
    int r1=old_sotp_decode(m1,a,buf), r2=poly_sotp_decode(m2,a,buf);
    printf("agreement: %s (rc %d/%d)\n", (r1==r2 && !memcmp(m1,m2,N/8))?"pass":"FAIL", r1, r2);
    const int R=50000;
    for(int i=0;i<200;i++) sink=old_sotp_decode(m1,a,buf);
    uint64_t t=rd(); for(int i=0;i<R;i++) sink=old_sotp_decode(m1,a,buf);
    double o=(double)(rd()-t)/R;
    for(int i=0;i<200;i++) sink=poly_sotp_decode(m2,a,buf);
    t=rd(); for(int i=0;i<R;i++) sink=poly_sotp_decode(m2,a,buf);
    double n=(double)(rd()-t)/R;
    printf("  P13 (horizontal reduction)  %7.1f\n  P23 (two-bit fields)        %7.1f\n  official                     508\n", o, n);
    return 0;
}
