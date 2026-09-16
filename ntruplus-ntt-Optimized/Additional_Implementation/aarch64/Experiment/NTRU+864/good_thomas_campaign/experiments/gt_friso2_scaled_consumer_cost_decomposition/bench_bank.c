#if !defined(__linux__)
#error "bench_bank requires Linux perf_event_open"
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <asm/unistd.h>
#include <errno.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include "bank_offsets.h"
#define N 864
#define P8 896
#define Q 3457
#define NINPUTS 64
#define NTESTS 61
#define NITERATIONS 40000
#define NWARMUP 200
typedef void (*kernel_fn)(int16_t *, const int16_t *);
struct counts { uint64_t cycles,instructions; };
struct variant { char code; const char *name; kernel_fn fn; };
extern void gt864_top_split_ld3(int16_t *,const int16_t *);
extern void gt864_forward_six_bank_pass2_all_one_mul_b3(int16_t *,const int16_t *);
extern void gt864_forward_six_bank_pass2_cf5b(int16_t *,const int16_t *);
extern void gt864_forward_noop(int16_t *,const int16_t *);
#define DECL(c) extern void gt864_cf5c_base_##c(int16_t*,const int16_t*); extern void gt864_cf5c_cand_##c(int16_t*,const int16_t*)
DECL(t0c1); DECL(t0c2); DECL(t1c1); DECL(t1c2);
static const kernel_fn bases[4]={gt864_cf5c_base_t0c1,gt864_cf5c_base_t0c2,gt864_cf5c_base_t1c1,gt864_cf5c_base_t1c2};
static const kernel_fn cands[4]={gt864_cf5c_cand_t0c1,gt864_cf5c_cand_t0c2,gt864_cf5c_cand_t1c1,gt864_cf5c_cand_t1c2};
static int16_t natural[NINPUTS][N] __attribute__((aligned(64)));
static int16_t p8[NINPUTS][P8] __attribute__((aligned(64)));
static int16_t output[N] __attribute__((aligned(64)));
static volatile uint64_t sink; static int leader_fd=-1,member_fd=-1; static uint32_t rng=0xcf5c864u;
static uint32_t rnd(void){uint32_t x=rng;x^=x<<13;x^=x>>17;x^=x<<5;return rng=x;}
static void prepare(int which){
    for(int k=0;k<NINPUTS;k++){
        int16_t bref[N],cref[N],iso[N];
        for(int i=0;i<N;i++) natural[k][i]=(int16_t)((int)(rnd()%Q)-1728);
        gt864_top_split_ld3(p8[k],natural[k]);
        gt864_forward_six_bank_pass2_all_one_mul_b3(bref,p8[k]);
        gt864_forward_six_bank_pass2_cf5b(cref,p8[k]);
        memset(iso,0x55,sizeof(iso)); bases[which](iso,p8[k]);
        for(int i=0;i<144;i++){unsigned at=gt864_cf5c_bank_indices[which][i];if(iso[at]!=bref[at]){fprintf(stderr,"base mismatch case=%d input=%d index=%u\n",which,k,at);exit(1);}}
        memset(iso,0x55,sizeof(iso)); cands[which](iso,p8[k]);
        for(int i=0;i<144;i++){unsigned at=gt864_cf5c_bank_indices[which][i];if(iso[at]!=cref[at]){fprintf(stderr,"cand mismatch case=%d input=%d index=%u\n",which,k,at);exit(1);}}
    }
    printf("correctness,status=pass,case=%d,base=64x144,candidate=64x144\n",which);
}
static int perf_open(uint64_t config,int group){struct perf_event_attr p;memset(&p,0,sizeof(p));p.type=PERF_TYPE_HARDWARE;p.size=sizeof(p);p.config=config;p.disabled=group==-1;p.exclude_kernel=1;p.exclude_hv=1;p.read_format=PERF_FORMAT_GROUP;return(int)syscall(__NR_perf_event_open,&p,0,-1,group,0);}
static struct counts measure(const struct variant*v){struct{uint64_t nr,value[2];}d={0,{0,0}};ioctl(leader_fd,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);ioctl(leader_fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);for(int i=0;i<NITERATIONS;i++)v->fn(output,p8[i&63]);ioctl(leader_fd,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);if(read(leader_fd,&d,sizeof(d))!=(ssize_t)sizeof(d)||d.nr!=2){perror("perf read");exit(2);}sink+=(uint16_t)output[(unsigned)v->code%N];return(struct counts){d.value[0],d.value[1]};}
int main(int argc,char**argv){if(argc!=3){fprintf(stderr,"usage: %s CASE BCN|NCB\n",argv[0]);return 2;}int which=atoi(argv[1]);if(which<0||which>3||strlen(argv[2])!=3)return 2;prepare(which);const struct variant vs[]={{'B',"baseline",bases[which]},{'C',"candidate",cands[which]},{'N',"noop",gt864_forward_noop}};leader_fd=perf_open(PERF_COUNT_HW_CPU_CYCLES,-1);member_fd=perf_open(PERF_COUNT_HW_INSTRUCTIONS,leader_fd);if(leader_fd<0||member_fd<0){fprintf(stderr,"perf_event_open: %s\n",strerror(errno));return 2;}for(int v=0;v<3;v++)for(int i=0;i<NWARMUP;i++)vs[v].fn(output,p8[i&63]);for(int s=0;s<NTESTS;s++)for(int pos=0;pos<3;pos++){const struct variant*v=NULL;for(int j=0;j<3;j++)if(vs[j].code==argv[2][pos])v=&vs[j];if(!v)return 2;struct counts c=measure(v);printf("sample,case=%d,order=%s,index=%d,variant=%s,cycles=%.6f,instructions=%.6f\n",which,argv[2],s,v->name,(double)c.cycles/NITERATIONS,(double)c.instructions/NITERATIONS);}printf("meta,sink=%"PRIu64"\n",sink);return 0;}
