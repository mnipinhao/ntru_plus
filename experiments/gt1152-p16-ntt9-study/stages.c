#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
void ntt_asm(int16_t*, const int16_t*);
void ntt_top_asm(int16_t*, const int16_t*);
void ntt_tail_asm(int16_t*);
void ntt9_asm(int16_t*, const int16_t*);
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
static int16_t in[1152], out[1152];
static int16_t scratch[2048] __attribute__((aligned(16)));
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    for(int i=0;i<1152;i++) in[i]=(int16_t)((i*7)%8-3);
    uint64_t a,b; const int R=20000;
    for(int i=0;i<50;i++) ntt_asm(out,in);
    a=rd(); for(int i=0;i<R;i++) ntt_asm(out,in); b=rd();
    printf("ntt_asm      raw=%llu  per=%.1f  out[0..3]=%d %d %d %d\n",(unsigned long long)(b-a),(double)(b-a)/R,out[0],out[1],out[2],out[3]);
    for(int i=0;i<50;i++) ntt_top_asm(scratch,in);
    a=rd(); for(int i=0;i<R;i++) ntt_top_asm(scratch,in); b=rd();
    printf("ntt_top_asm  raw=%llu  per=%.1f  scr[0..3]=%d %d %d %d\n",(unsigned long long)(b-a),(double)(b-a)/R,scratch[0],scratch[1],scratch[2],scratch[3]);
    for(int i=0;i<50;i++) ntt_tail_asm(scratch+1024);
    a=rd(); for(int i=0;i<R;i++) ntt_tail_asm(scratch+1024); b=rd();
    printf("ntt_tail_asm raw=%llu  per=%.1f\n",(unsigned long long)(b-a),(double)(b-a)/R);
    for(int i=0;i<50;i++) ntt9_asm(out,scratch);
    a=rd(); for(int i=0;i<R;i++) ntt9_asm(out,scratch); b=rd();
    printf("ntt9_asm     raw=%llu  per=%.1f\n",(unsigned long long)(b-a),(double)(b-a)/R);
    return 0;
}
