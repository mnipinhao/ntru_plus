#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "fips202.h"
static int fd; static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)_exit(3);return v;}
static uint8_t msg[176], data[177], out[320], st[200];
void ntruplus_keccak_f1600_x1_aarch64(uint64_t*, const uint64_t*);
extern const uint64_t *dummy;
static const uint64_t RC[24]={
0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,
0x000000000000008aULL,0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,
0x000000008000808bULL,0x800000000000008bULL,0x8000000000008089ULL,0x8000000000008003ULL,
0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,0x800000008000000aULL,
0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};
static void gen_h(void){ data[0]=0x02; memcpy(data+1,msg,176); shake256(out,320,data,177); }
static void perm5(void){ for(int i=0;i<5;i++) ntruplus_keccak_f1600_x1_aarch64((uint64_t*)st,RC); }
static double bench(void(*f)(void)){
    for(int i=0;i<300;i++) f();
    const int R=20000; uint64_t a=rd();
    for(int i=0;i<R;i++) f();
    return (double)(rd()-a)/R;
}
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint64_t s=1; for(int i=0;i<176;i++){s^=s<<13;s^=s>>7;s^=s<<17;msg[i]=(uint8_t)s;}
    double gh=bench(gen_h), p5=bench(perm5);
    printf("  hash_h, generic sponge          %8.1f  (5 permutations)\n", gh);
    printf("  5 bare assembly permutations    %8.1f\n", p5);
    printf("  sponge overhead above the core  %8.1f  (%.0f per permutation)\n", gh-p5, (gh-p5)/5);
    printf("\n  for reference, fused hash_g is 13765 for 16 permutations = %.0f each\n", 13765.0/16);
    return 0;
}
