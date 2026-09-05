#define _GNU_SOURCE
#include "byte_boundary.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#ifdef __linux__
#include <linux/perf_event.h>
#endif
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <unistd.h>
typedef void (*to_fn)(uint8_t*,const int16_t*);
typedef void (*from_fn)(int16_t*,const uint8_t*);
static to_fn tf[4]={current_to,r9_to,c1_to,c2_to};
static from_fn ff[4]={current_from,r9_from,c1_from,c2_from};
#ifdef __linux__
static const char *names[4]={"current","r9","c1","c2"};
#endif
static int16_t input[864],ref[864],output[864];
static uint8_t bytes[1296],actual[1296];
static uint32_t rng=1;
static uint32_t next(void){rng=rng*1664525+1013904223;return rng;}
static void check(void){
 for(int t=0;t<128;t++){
  for(int i=0;i<864;i++)input[i]=t==0?i:t==1?-32768:t==2?32767:(int16_t)next();
  current_to(bytes,input);
  for(int v=1;v<4;v++){tf[v](actual,input);if(memcmp(bytes,actual,1296)){fprintf(stderr,"to fail t=%d v=%d\n",t,v);for(int i=0;i<1296;i++)if(bytes[i]!=actual[i]){fprintf(stderr,"byte=%d expected=%u actual=%u\n",i,bytes[i],actual[i]);break;}exit(1);}}
  current_from(ref,bytes);
  for(int v=1;v<4;v++){ff[v](output,bytes);if(memcmp(ref,output,sizeof ref)){fprintf(stderr,"from fail t=%d v=%d\n",t,v);exit(1);}}
  for(int i=0;i<864;i++)if(ref[i]!=((input[i]%3457+3457)%3457)){fprintf(stderr,"roundtrip fail\n");exit(1);}
  for(int i=0;i<1296;i++)bytes[i]=next();
  current_from(ref,bytes);
  for(int v=1;v<4;v++){ff[v](output,bytes);if(memcmp(ref,output,sizeof ref)){fprintf(stderr,"arbitrary bytes fail v=%d\n",v);exit(1);}}
 }
 /* Guarded end boundaries detect over-read and over-write, including last 12 bytes. */
 size_t page=sysconf(_SC_PAGESIZE);
 uint8_t *a=mmap(0,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 uint8_t *b=mmap(0,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
 if(a==MAP_FAILED||b==MAP_FAILED)exit(2);
 mprotect(a, page,PROT_NONE);mprotect(a+2*page,page,PROT_NONE);
 mprotect(b, page,PROT_NONE);mprotect(b+2*page,page,PROT_NONE);
 for(int edge=0;edge<2;edge++){
  int16_t *coeff=(int16_t*)(a+page+(edge?page-1728:0));
  uint8_t *enc=b+page+(edge?page-1296:0);
  for(int i=0;i<864;i++)coeff[i]=i-432;
  for(int v=0;v<4;v++){tf[v](enc,coeff);ff[v](coeff,enc);}
 }
 munmap(a,3*page);munmap(b,3*page);
 puts("correctness=pass random=128 arbitrary_bytes=128 guarded_edges=2");
}
#ifdef __linux__
static int openp(uint64_t config,int group){
 struct perf_event_attr p={0};p.size=sizeof p;p.type=PERF_TYPE_HARDWARE;p.config=config;p.disabled=group<0;p.exclude_kernel=1;p.exclude_hv=1;p.read_format=PERF_FORMAT_GROUP;
 return syscall(__NR_perf_event_open,&p,0,-1,group,0);
}
static volatile uint64_t sink;
int main(int argc,char **argv){
 check();if(argc==1)return 0;
 int fd=openp(PERF_COUNT_HW_CPU_CYCLES,-1),fi=openp(PERF_COUNT_HW_INSTRUCTIONS,fd),fb=openp(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);
 if(fd<0||fi<0||fb<0){perror("perf");return 2;}
 for(int i=0;i<864;i++)input[i]=(int16_t)next();
 current_to(bytes,input);
 int reverse=atoi(argv[1]);
 for(int rep=0;rep<41;rep++)for(int pos=0;pos<10;pos++){
  int op=reverse?9-pos:pos;
  struct {uint64_t n,v[3];}d;
  ioctl(fd,PERF_EVENT_IOC_RESET,PERF_IOC_FLAG_GROUP);ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
  for(int k=0;k<200;k++){
   if(op<4)tf[op](actual,input);
   else if(op<8)ff[op-4](output,bytes);
   else if(op==8)norm_only(output,input);
   else pack_only(actual,ref);
  }
  ioctl(fd,PERF_EVENT_IOC_DISABLE,PERF_IOC_FLAG_GROUP);
  if(read(fd,&d,sizeof d)!=(ssize_t)sizeof d||d.n!=3)return 2;
  sink+=actual[0]+output[0];
  printf("sample,%s_%s,%.3f,%.3f,%.3f\n",op<4?"to":op<8?"from":"isolated",op<8?names[op%4]:op==8?"norm":"pack",d.v[0]/200.0,d.v[1]/200.0,d.v[2]/200.0);
 }
 return 0;
}
#else
int main(void){check();return 0;}
#endif
