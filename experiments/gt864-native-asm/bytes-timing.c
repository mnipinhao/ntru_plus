#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
typedef void(*bytesfn)(uint8_t*,const int16_t*);
static uint64_t rng=864;static volatile unsigned sink;
void randombytes(uint8_t*out,size_t n){while(n--){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;*out++=rng;}}
static bytesfn load(const char*path,const char*name){void*h=dlopen(path,RTLD_NOW|RTLD_LOCAL);if(!h){puts(dlerror());exit(2);}bytesfn f=(bytesfn)dlsym(h,name);if(!f){puts(dlerror());exit(2);}return f;}
static int event(uint64_t config,int group){struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;a.config=config;a.exclude_kernel=1;a.exclude_hv=1;a.disabled=group<0;a.read_format=PERF_FORMAT_GROUP;return syscall(__NR_perf_event_open,&a,0,-1,group,0);}
struct counts{uint64_t n,v[3];};
static struct counts readc(int fd){struct counts c;if(read(fd,&c,sizeof c)!=sizeof c||c.n!=3)exit(3);return c;}
int main(int argc,char**argv){
 if(argc!=6)return 2;
 bytesfn f[2]={load(argv[1],argv[2]),load(argv[3],argv[4])};int reverse=atoi(argv[5]);
 int16_t in[864] __attribute__((aligned(16)));uint8_t out[2][1296];
 /* Identical legal D1-range input for both implementations; entire public call. */
 for(int i=0;i<864;i++){uint16_t x;randombytes((uint8_t*)&x,2);in[i]=(int)(x%6047)-3023;}
 f[0](out[0],in);f[1](out[1],in);if(memcmp(out[0],out[1],1296))return 4;
 int fd=event(PERF_COUNT_HW_CPU_CYCLES,-1),fi=event(PERF_COUNT_HW_INSTRUCTIONS,fd),fb=event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);
 if(fd<0||fi<0||fb<0){perror("perf");return 3;}ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
 for(int sample=-5;sample<41;sample++)for(int pos=0;pos<2;pos++){
  int v=pos^reverse,n=128;struct counts x=readc(fd);
  for(int k=0;k<n;k++){f[v](out[v],in);sink+=out[v][k%1296];}
  struct counts y=readc(fd);if(sample>=0)printf("bytes,complete,%s,%.3f,%.3f,%.3f\n",v?"candidate":"baseline",(double)(y.v[0]-x.v[0])/n,(double)(y.v[1]-x.v[1])/n,(double)(y.v[2]-x.v[2])/n);
 }
}
