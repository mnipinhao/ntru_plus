#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
void invntt16_tail_asm(int16_t*, const int16_t*, long, const int16_t*, const int16_t*);
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
static int16_t out[2048], scratch[2048];
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    for(int i=0;i<2048;i++) scratch[i]=(int16_t)((i*29)%3457-1728);
    for(int i=0;i<200;i++) invntt16_tail_asm(out,scratch,0,0,0);
    const int R=20000; uint64_t a=rd();
    for(int i=0;i<R;i++) invntt16_tail_asm(out,scratch,0,0,0);
    printf("invntt16_tail_asm (C): %.1f cycles per call\n",(double)(rd()-a)/R);
    printf("poly_invntt_ternary total (profile): 7433   official invntt+crepmod3: 6299\n");
    return 0;
}
