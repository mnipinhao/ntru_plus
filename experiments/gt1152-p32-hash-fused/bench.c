#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "fips202.h"
#define PB 1728
void ntruplus_hash_f_fixed(uint8_t*, const uint8_t*);
void ntruplus_hash_g_fixed(uint8_t*, const uint8_t*);
static int fd; static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)_exit(3);return v;}
static uint8_t msg[PB], data[1+PB], o32[32], o288[288];
static void gen_f(void){ data[0]=0x00; memcpy(data+1,msg,PB); shake256(o32,32,data,PB+1); }
static void gen_g(void){ data[0]=0x01; memcpy(data+1,msg,PB); shake256(o288,288,data,PB+1); }
static void fix_f(void){ ntruplus_hash_f_fixed(o32,msg); }
static void fix_g(void){ ntruplus_hash_g_fixed(o288,msg); }
static double bench(void(*f)(void)){
    for(int i=0;i<200;i++) f();
    const int R=5000; uint64_t a=rd();
    for(int i=0;i<R;i++) f();
    return (double)(rd()-a)/R;
}
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint64_t s=1; for(int i=0;i<PB;i++){s^=s<<13;s^=s>>7;s^=s<<17;msg[i]=(uint8_t)s;}
    double gf=bench(gen_f), ff=bench(fix_f), gg=bench(gen_g), fg=bench(fix_g);
    printf("  %-26s %8.1f -> %8.1f   %+8.1f  (%.2fx)\n","hash_f (32 out)",gf,ff,ff-gf,gf/ff);
    printf("  %-26s %8.1f -> %8.1f   %+8.1f  (%.2fx)\n","hash_g (288 out)",gg,fg,fg-gg,gg/fg);
    return 0;
}
