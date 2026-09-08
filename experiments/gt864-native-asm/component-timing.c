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
typedef struct{int16_t c[864];} poly;
typedef void(*unary)(poly*,const poly*);
typedef void(*binary)(poly*,const poly*,const poly*);
typedef int(*invfn)(poly*,const poly*);
struct api{invfn inv;unary inverse;binary mul;};
static uint64_t rng=864;static volatile unsigned sink;
void randombytes(uint8_t*out,size_t n){while(n--){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;*out++=rng;}}
static void*sym(void*h,const char*n){void*p=dlsym(h,n);if(!p){fprintf(stderr,"missing %s\n",n);exit(2);}return p;}
static struct api load(const char*path,int native){void*h=dlopen(path,RTLD_NOW|RTLD_LOCAL);if(!h){puts(dlerror());exit(2);}return(struct api){sym(h,native?"bench_baseinv":"gt_d1_poly_baseinv"),sym(h,native?"fr0_inverse_scaled":"gt_d1_poly_invntt"),sym(h,native?"fr0_basemul_for_inverse":"gt_d1_poly_basemul")};}
static int event(uint64_t config,int group){struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;a.config=config;a.exclude_kernel=1;a.exclude_hv=1;a.disabled=group<0;a.read_format=PERF_FORMAT_GROUP;return syscall(__NR_perf_event_open,&a,0,-1,group,0);}
struct counts{uint64_t n,v[3];};
static struct counts readc(int fd){struct counts c;if(read(fd,&c,sizeof c)!=sizeof c||c.n!=3)exit(3);return c;}
int main(int argc,char**argv){if(argc!=5)return 2;int reverse=atoi(argv[4]);
 struct api f[2]={load(argv[1],atoi(argv[3])),load(argv[2],1)};
 poly a,b,one={0},zero={0},p[2],out;
 for(int j=0;j<36;j++)for(int l=0;l<8;l++)one.c[24*j+l]=1;
 randombytes((uint8_t*)&a,sizeof a);randombytes((uint8_t*)&b,sizeof b);
 for(int i=0;i<864;i++){a.c[i]=(uint16_t)a.c[i]&4095;b.c[i]=(uint16_t)b.c[i]&4095;}
 for(int v=0;v<2;v++)f[v].mul(&p[v],&a,&b);
 int fd=event(PERF_COUNT_HW_CPU_CYCLES,-1),fi=event(PERF_COUNT_HW_INSTRUCTIONS,fd),fb=event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);
 if(fd<0||fi<0||fb<0){perror("perf");return 3;}ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
 const char*names[]={"baseinv_success","baseinv_failure","basemul_scale_specific","inverse_scale_specific","basemul_inverse"};
 for(int op=0;op<5;op++)for(int sample=-5;sample<41;sample++)for(int pos=0;pos<2;pos++){
  int v=pos^reverse,n=32;struct counts x=readc(fd);
  for(int k=0;k<n;k++){
   if(op<2)sink+=f[v].inv(&out,op?&zero:&one);
   if(op==2)f[v].mul(&out,&a,&b);
   if(op==3)f[v].inverse(&out,&p[v]);
   if(op==4){f[v].mul(&p[v],&a,&b);f[v].inverse(&out,&p[v]);}
   sink+=(uint16_t)out.c[0];
  }
  struct counts y=readc(fd);if(sample>=0)printf("component,%s,%s,%.3f,%.3f,%.3f\n",names[op],v?"candidate":"baseline",(double)(y.v[0]-x.v[0])/n,(double)(y.v[1]-x.v[1])/n,(double)(y.v[2]-x.v[2])/n);
 }
}
