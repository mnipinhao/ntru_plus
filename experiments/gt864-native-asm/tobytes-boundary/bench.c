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
typedef void(*tofn)(uint8_t*,const int16_t*);
typedef int(*fromfn)(int16_t*,const uint8_t*);
static int fd,active;static uint64_t last,total[8],calls[8],rng=864;
static volatile unsigned sink;
struct counts{uint64_t n,v[3];};
static struct counts tick(void){struct counts x;if(read(fd,&x,sizeof x)!=sizeof x||x.n!=3)exit(3);return x;}
void randombytes(uint8_t*p,size_t n){while(n--){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;*p++=rng;}}
void stage_mark(int id){if(!active)return;uint64_t t=tick().v[0];if(id){total[id]+=t-last;calls[id]++;}last=t;}
static int event(uint64_t config,int group){struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;a.config=config;a.exclude_kernel=1;a.exclude_hv=1;a.disabled=group<0;a.read_format=PERF_FORMAT_GROUP;return syscall(__NR_perf_event_open,&a,0,-1,group,0);}
static void*openlib(const char*p){void*h=dlopen(p,RTLD_NOW|RTLD_LOCAL);if(!h){puts(dlerror());exit(2);}return h;}
static void*sym(void*h,const char*s){void*f=dlsym(h,s);if(!f){puts(s);exit(2);}return f;}
int main(int argc,char**argv){if(argc!=4)return 2;int reverse=atoi(argv[3]);
 void*h[2]={openlib(argv[1]),openlib(argv[2])},*hp[2]={openlib("./official-prof.so"),openlib("./gt-prof.so")};
 fromfn from[2]={(fromfn)sym(h[0],"poly_frombytes"),(fromfn)sym(h[1],"gt864_fr0_frombytes_checked")};
 fd=event(PERF_COUNT_HW_CPU_CYCLES,-1);int fi=event(PERF_COUNT_HW_INSTRUCTIONS,fd),fb=event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);if(fd<0||fi<0||fb<0){perror("PMU");return 3;}ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
 uint8_t wire[1296],out[1298];int16_t in[2][864],saved[2][864];
 for(int i=0;i<432;i++){uint16_t a,b;randombytes((uint8_t*)&a,2);randombytes((uint8_t*)&b,2);a%=3457;b%=3457;wire[3*i]=a;wire[3*i+1]=(a>>8)|((b&15)<<4);wire[3*i+2]=b>>4;}
 for(int mode=0;mode<2;mode++){
  tofn clean[2]={(tofn)sym(h[0],"poly_tobytes"),(tofn)sym(h[1],mode?"gt864_fr0_tobytes_small":"gt864_fr0_tobytes_full")};
  tofn prof[2]={(tofn)sym(hp[0],"poly_tobytes"),(tofn)sym(hp[1],mode?"gt864_fr0_tobytes_small":"gt864_fr0_tobytes_full")};
  for(int v=0;v<2;v++){if(from[v](in[v],wire))return 4;for(int i=0;i<864;i++)in[v][i]=mode?(in[v][i]>1728?in[v][i]-3457:in[v][i]):in[v][i]+3457;}
  memcpy(saved,in,sizeof in);
  for(int v=0;v<2;v++)for(int marked=0;marked<2;marked++){memset(out,0xa5,sizeof out);active=marked;(marked?prof[v]:clean[v])(out+1,in[v]);if(memcmp(out+1,wire,1296)||out[0]!=0xa5||out[1297]!=0xa5||memcmp(saved,in,sizeof in))return 5;}
  active=0;printf("correctness,%s,clean-and-profile-pass\n",mode?"small":"full");
  for(int sample=-5;sample<41;sample++)for(int pos=0;pos<2;pos++){int v=pos^reverse,n=128;struct counts a=tick();for(int k=0;k<n;k++){clean[v](out+1,in[v]);sink+=out[1];}struct counts z=tick();if(sample>=0)printf("full,%s,%s,%.3f,%.3f,%.3f\n",mode?"small":"full",v?"gt":"official",(double)(z.v[0]-a.v[0])/n,(double)(z.v[1]-a.v[1])/n,(double)(z.v[2]-a.v[2])/n);}
  for(int sample=-3;sample<21;sample++)for(int pos=0;pos<2;pos++){int v=pos^reverse,n=16;memset(total,0,sizeof total);memset(calls,0,sizeof calls);active=1;for(int k=0;k<n;k++)prof[v](out+1,in[v]);active=0;if(sample>=0)for(int i=1;i<8;i++)if(calls[i])printf("stage,%s,%s,%d,%.3f,%.3f\n",mode?"small":"full",v?"gt":"official",i,(double)total[i]/n,(double)calls[i]/n);}
 }
}
