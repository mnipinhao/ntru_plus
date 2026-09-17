#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "poly.h"
int baseinv_asm(int16_t*, const int16_t*);
int ref_baseinv(int16_t*, const int16_t*);
static int fd; static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)_exit(3);return v;}
static int16_t a[NTRUPLUS_N], o1[NTRUPLUS_N], o2[NTRUPLUS_N];
static uint64_t s=0xC0FFEE123456789ull;
static uint64_t rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0); if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    int bad=0, inv=0, noninv=0, diffrep=0;
    for(int t=0;t<4000;t++){
        for(int i=0;i<NTRUPLUS_N;i++) a[i]=(int16_t)(rnd()%3457)-1728;
        if(t%3==1){ /* force one leaf non-invertible: zero a whole group lane */
            int g=(int)(rnd()%36), l=(int)(rnd()%8);
            for(int c=0;c<4;c++) a[32*g+8*c+l]=0;
        }
        memset(o1,0x5A,sizeof o1); memset(o2,0xA5,sizeof o2);
        int r1=ref_baseinv(o1,a), r2=baseinv_asm(o2,a);
        r1?noninv++:inv++;
        if(r1!=r2){ if(bad<3) printf("  rc mismatch t=%d %d/%d\n",t,r1,r2); bad++; continue; }
        int exact=0, cong=0;
        for(int i=0;i<NTRUPLUS_N;i++){
            if(o1[i]!=o2[i]){ exact++; if(((o1[i]-o2[i])%3457+3457)%3457) cong++; }
        }
        if(cong){ if(bad<3) printf("  NOT congruent t=%d: %d coefficients\n",t,cong); bad++; }
        else if(exact) diffrep++;
    }
    printf("4000 trials: real mismatches %d, congruent-but-different-representative %d  (invertible %d, non-invertible %d)\n", bad, diffrep, inv, noninv);
    if(bad) return 1;
    for(int i=0;i<NTRUPLUS_N;i++) a[i]=(int16_t)(rnd()%3457)-1728;
    const int R=5000;
    for(int i=0;i<100;i++) ref_baseinv(o1,a);
    uint64_t t0=rd(); for(int i=0;i<R;i++) ref_baseinv(o1,a); double ro=(double)(rd()-t0)/R;
    for(int i=0;i<100;i++) baseinv_asm(o2,a);
    t0=rd(); for(int i=0;i<R;i++) baseinv_asm(o2,a); double nn=(double)(rd()-t0)/R;
    printf("  serial baseline %7.1f   this variant %7.1f   %+.1f\n", ro, nn, nn-ro);
    return 0;
}
