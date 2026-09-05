#if !defined(__linux__)
#error Linux PMU required
#endif
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include "route9.h"
#include <asm/unistd.h>
#include <inttypes.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#define SAMPLES 41
#define OPS 8
typedef void (*route_fn)(int16_t *,const int16_t *);
struct count{uint64_t c,i,b;};
static int16_t fr0[P3B1_N],official[P3B1_N],out[P3B1_N];
static volatile uint64_t sink;static int leader,ifd,bfd;
static const char *names[OPS]={"f2o_current","f2o_factor","f2o_r9a","f2o_r9b","o2f_current","o2f_factor","o2f_r9a","o2f_r9b"};
static route_fn fn[OPS]={p3b1_current_f2o,p3b1_factor_f2o,p3b1_r9a_f2o,p3b1_r9b_f2o,p3b1_current_o2f,p3b1_factor_o2f,p3b1_r9a_o2f,p3b1_r9b_o2f};
static int openp(uint64_t config,int group){struct perf_event_attr p;memset(&p,0,sizeof p);p.type=PERF_TYPE_HARDWARE;p.size=sizeof p;p.config=config;p.disabled=group==-1;p.exclude_kernel=1;p.exclude_hv=1;p.read_format=PERF_FORMAT_GROUP;return syscall(__NR_perf_event_open,&p,0,-1,group,0);}
static struct count measure(int op){struct{uint64_t n,v[3];}d={0};const int16_t *in=op<4?fr0:official;ioctl(leader,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);ioctl(leader,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);for(int k=0;k<500;k++)fn[op](out,in);ioctl(leader,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);if(read(leader,&d,sizeof d)!=(ssize_t)sizeof d||d.n!=3)exit(2);sink+=(uint16_t)out[(op*97)%P3B1_N];return(struct count){d.v[0],d.v[1],d.v[2]};}
int main(int argc,char **argv){if(argc!=2||strlen(argv[1])!=OPS)return 2;for(int i=0;i<P3B1_N;i++)fr0[i]=(int16_t)(i*73+19);p3b1_current_f2o(official,fr0);leader=openp(PERF_COUNT_HW_CPU_CYCLES,-1);ifd=openp(PERF_COUNT_HW_INSTRUCTIONS,leader);bfd=openp(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,leader);if(leader<0||ifd<0||bfd<0)return 2;puts("correctness,status=prepared,D1-P3B1_ops=8");for(int s=0;s<SAMPLES;s++)for(int p=0;p<OPS;p++){int op=argv[1][p]-'0';if(op<0||op>=OPS)return 2;struct count x=measure(op);printf("sample,operation=%s,index=%d,position=%d,cycles=%.6f,instructions=%.6f,branches=%.6f\n",names[op],s,p,(double)x.c/500,(double)x.i/500,(double)x.b/500);}printf("meta,sink=%"PRIu64"\n",sink);return 0;}
