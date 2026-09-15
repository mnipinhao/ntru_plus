#define _GNU_SOURCE
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include "gt864_native_scaled_tables.h"
#include "gt864_p13b_composite_tables.h"

typedef void (*lazyfn)(int16_t *, const int16_t *, const void *, const int16_t *, const int16_t *);
typedef void (*prefixfn)(int16_t *, const int16_t *, const int16_t *);
typedef void (*terminalfn)(int16_t *, const int16_t *, const int16_t *);
struct counts { uint64_t n, v[3]; };
static int fd;
static volatile unsigned sink;
static uint32_t state;
static _Alignas(16) int16_t source[768], work[2][768], output[2][864];
void randombytes(uint8_t *out, size_t n) { while (n--) *out++ = (uint8_t)(state = state * 1664525u + 1013904223u); }

static void *must(void *h, const char *name) {
  void *p = dlsym(h, name); if (!p) { fprintf(stderr, "%s\n", dlerror()); exit(2); } return p;
}
static int event(uint64_t config, int group) {
  struct perf_event_attr a = {0}; a.size=sizeof a; a.type=PERF_TYPE_HARDWARE; a.config=config;
  a.exclude_kernel=a.exclude_hv=1; a.disabled=group<0; a.read_format=PERF_FORMAT_GROUP;
  return syscall(__NR_perf_event_open,&a,0,-1,group,0);
}
static struct counts tick(void) { struct counts c; if(read(fd,&c,sizeof c)!=sizeof c||c.n!=3)exit(3);return c; }
static void fill(unsigned seed) {
  state=seed; for(unsigned i=0;i<768;i++){state^=state<<13;state^=state>>17;state^=state<<5;source[i]=(int16_t)((int)(state%5235)-2617);}
}
static void baseline(lazyfn f) {
  memcpy(work[0],source,sizeof source); memset(output[0],0,sizeof output[0]);
  for(unsigned g=0;g<6;g++){unsigned c=g/2,h=g%2;f(output[0]+c+12*h,work[0]+128*g,0,&gt864_inverse16_stage_barrett[0][0],&gt864_p13b_main[0][0]);}
}
static void candidate(prefixfn p, terminalfn t) {
  memcpy(work[1],source,sizeof source); memset(output[1],0,sizeof output[1]);
  for(unsigned g=0;g<6;g++)p(work[1]+128*g,work[1]+128*g,&gt864_inverse16_stage_barrett[0][0]);
  t(output[1],work[1],&gt864_p13b_main[0][0]);
}
int main(int argc,char **argv){
  if(argc!=3)return 2; void *b=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL),*c=dlopen(argv[2],RTLD_NOW|RTLD_LOCAL);
  if(!b||!c){fprintf(stderr,"%s\n",dlerror());return 2;} lazyfn f=must(b,"lazy_i16");prefixfn p=must(c,"p32_i16_prefix");terminalfn t=must(c,"p32_i16_terminal6");
  fill(864);baseline(f);candidate(p,t);if(memcmp(output[0],output[1],sizeof output[0]))return 4;puts("correctness=pass");
  fd=event(PERF_COUNT_HW_CPU_CYCLES,-1);int fi=event(PERF_COUNT_HW_INSTRUCTIONS,fd),fb=event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);if(fd<0||fi<0||fb<0)return 3;ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);
  for(int sample=-10;sample<91;sample++){fill(0x320000u+(unsigned)(sample+10));for(int pos=0;pos<2;pos++){int which=pos^(sample&1);struct counts a=tick();for(int k=0;k<32;k++){if(which)candidate(p,t);else baseline(f);sink+=(unsigned)output[which][k];}struct counts z=tick();if(sample>=0)printf("main_i16,%s,%.3f,%.3f,%.3f\n",which?"candidate":"baseline",(double)(z.v[0]-a.v[0])/32,(double)(z.v[1]-a.v[1])/32,(double)(z.v[2]-a.v[2])/32);}}
}
