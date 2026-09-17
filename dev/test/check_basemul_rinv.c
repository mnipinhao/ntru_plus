/*
 * Differential for the SLOTHY-scheduled basemul_rinv against the shipped C,
 * which is the declared oracle for this kernel.
 *
 * The kernel's ABI differs from the C entry point: it takes the zeta table as a
 * fourth argument and advances all four pointers, so the shim below supplies
 * the table and restores the C signature.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "base_tables.h"

#define N 1152
#define Q 3457

void basemul_rinv_kernel(int16_t *out, const int16_t *a, const int16_t *b,
                         const int16_t *zetas);
void basemul_rinv_asm(int16_t *out, const int16_t *a, const int16_t *b);

static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
static int16_t a[N], b[N], o1[N], o2[N];
static uint64_t s = 0x2545F4914F6CDD1Dull;
static uint64_t rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}

static void kernel(int16_t *o, const int16_t *x, const int16_t *y)
{ basemul_rinv_kernel(o, x, y, &basemul_zetas[0][0]); }

int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);

    int exact=0, cong=0, worst=0;
    for(int t=0;t<4000;t++){
        for(int i=0;i<N;i++){
            if(t%3==0){ a[i]=(int16_t)(rnd()%4096); b[i]=(int16_t)(rnd()%4096); }
            else if(t%3==1){ a[i]=4095; b[i]=4095; }
            else { a[i]=(int16_t)((rnd()&1)?4095:0); b[i]=(int16_t)((rnd()&1)?4095:0); }
        }
        memset(o1,0x5A,sizeof o1); memset(o2,0xA5,sizeof o2);
        basemul_rinv_asm(o1,a,b);
        kernel(o2,a,b);
        for(int i=0;i<N;i++){
            if(o1[i]!=o2[i]){ exact++; if(((o1[i]-o2[i])%Q+Q)%Q) cong++; }
            int v = o2[i]<0 ? -o2[i] : o2[i];
            if(v>worst) worst=v;
        }
    }
    printf("4000 trials x 1152: not congruent %d, different representative %d, max |out| %d\n",
           cong, exact-cong, worst);
    if(cong || worst>1728) return 1;

    const int R=20000;
    for(int i=0;i<200;i++) basemul_rinv_asm(o1,a,b);
    uint64_t t0=rd(); for(int i=0;i<R;i++) basemul_rinv_asm(o1,a,b);
    double c=(double)(rd()-t0)/R;
    for(int i=0;i<200;i++) kernel(o2,a,b);
    t0=rd(); for(int i=0;i<R;i++) kernel(o2,a,b);
    double k=(double)(rd()-t0)/R;
    printf("  intrinsics C %7.1f   SLOTHY %7.1f   %+.1f    (floor 2376, official 2551)\n",
           c, k, k-c);
    return 0;
}
