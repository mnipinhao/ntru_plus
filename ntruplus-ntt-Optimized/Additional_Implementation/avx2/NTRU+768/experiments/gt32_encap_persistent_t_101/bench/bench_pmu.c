#define _GNU_SOURCE
#include <linux/perf_event.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include "candidate.h"
#include "internal.h"

enum { SAMPLES = 20 };
typedef void (*bench_fn)(void);
static volatile uint64_t sink;
static _Alignas(64) int16_t front[768], m[768], t[768], h[768], out[768];
static _Alignas(64) uint8_t wire[1152], pk[1152], coins[96], ct[1152], ss[32];

static void f0(void){ ntruplus768_ntt_m_avx2(out,front); sink+=(uint16_t)out[0]; }
static void f1(void){ gt101_ntt_t_avx2(out,front); sink+=(uint16_t)out[0]; }
static void p0(void){ ntruplus768_pack_m_lazy10788_avx2(wire,m); sink+=wire[0]; }
static void p1(void){ gt101_pack_t_avx2(wire,t); sink+=wire[0]; }
static void b0(void){ ntruplus768_basemul_general_m_avx2(out,h,m); sink+=(uint16_t)out[0]; }
static void b1(void){ gt101_basemul_general_m_t_avx2(out,h,t); sink+=(uint16_t)out[0]; }
static void e0(void){ sink+=(uint64_t)ntruplus768_enc_derand_impl(ct,ss,pk,coins)+ct[0]+ss[0]; }
static void e1(void){ sink+=(uint64_t)gt101_encap_t(ct,ss,pk,coins)+ct[0]+ss[0]; }

static int perf_open(uint64_t config)
{
  struct perf_event_attr a;
  memset(&a,0,sizeof a); a.type=PERF_TYPE_HARDWARE; a.size=sizeof a;
  a.config=config; a.disabled=1; a.exclude_kernel=1; a.exclude_hv=1;
  return (int)syscall(SYS_perf_event_open,&a,0,-1,-1,0UL);
}
static double measure(bench_fn f,unsigned n,int fd)
{
  uint64_t v=0; ioctl(fd,PERF_EVENT_IOC_RESET,0); ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
  for(unsigned i=0;i<n;i++)f();
  ioctl(fd,PERF_EVENT_IOC_DISABLE,0);
  if(read(fd,&v,sizeof v)!=(ssize_t)sizeof v)return 0;
  return (double)v/n;
}
static int cmp(const void *a,const void *b)
{ double x=*(const double *)a,y=*(const double *)b; return (x>y)-(x<y); }
static double median(double x[SAMPLES])
{ double y[SAMPLES]; memcpy(y,x,sizeof y); qsort(y,SAMPLES,sizeof y[0],cmp); return .5*(y[9]+y[10]); }
static void metric(const char *region,bench_fn control,bench_fn candidate,unsigned n,
                   const char *name,int fd)
{
  double a[SAMPLES],b[SAMPLES],d[SAMPLES]; unsigned wins=0;
  for(unsigned i=0;i<SAMPLES;i++){
    if(i&1){b[i]=measure(candidate,n,fd);a[i]=measure(control,n,fd);}
    else {a[i]=measure(control,n,fd);b[i]=measure(candidate,n,fd);}
    d[i]=b[i]-a[i]; wins+=(d[i]<0);
  }
  printf("region=%s metric=%s control=%.3f candidate=%.3f delta=%.3f wins=%u/%u\n",
         region,name,median(a),median(b),median(d),wins,SAMPLES);
}
static uint64_t rng=UINT64_C(0x10155aa55aa55aa5);
static uint32_t rnd(void){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;return (uint32_t)rng;}
static void init(void)
{
  _Alignas(64) int16_t coeff[768];
  for(int i=0;i<768;i++){coeff[i]=(int16_t)((int)(rnd()%3457)-1728);h[i]=(int16_t)((int)(rnd()%3457)-1728);}
  ntruplus768_ntt_frontend_avx2(front,coeff); ntruplus768_ntt_m_avx2(m,front); gt101_ntt_t_avx2(t,front);
  for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;pk[3*i]=x;pk[3*i+1]=(uint8_t)((x>>8)|(y<<4));pk[3*i+2]=(uint8_t)(y>>4);}
  for(size_t i=0;i<sizeof coins;i++)coins[i]=(uint8_t)rnd();
}
int main(void)
{
  cpu_set_t set; CPU_ZERO(&set); CPU_SET(1,&set);
  if(sched_setaffinity(0,sizeof set,&set))return 2;
  init();
  for(unsigned i=0;i<100;i++){f0();f1();p0();p1();b0();b1();e0();e1();}
  int cycles=perf_open(PERF_COUNT_HW_CPU_CYCLES),ins=perf_open(PERF_COUNT_HW_INSTRUCTIONS);
  if(cycles<0||ins<0){perror("perf_event_open");return 3;}
  struct item {const char *name;bench_fn a,b;unsigned n;} items[]={
    {"forward",f0,f1,4096},{"pack",p0,p1,4096},{"b3",b0,b1,4096},{"encap",e0,e1,256}
  };
  for(unsigned i=0;i<sizeof items/sizeof items[0];i++){
    metric(items[i].name,items[i].a,items[i].b,items[i].n,"core_cycles",cycles);
    metric(items[i].name,items[i].a,items[i].b,items[i].n,"instructions",ins);
  }
  close(cycles);close(ins);printf("sink=%llu\n",(unsigned long long)sink);return 0;
}
