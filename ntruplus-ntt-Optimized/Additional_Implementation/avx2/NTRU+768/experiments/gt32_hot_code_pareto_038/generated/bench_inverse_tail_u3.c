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
#include <x86intrin.h>

void ntruplus768_invntt_tail_avx2(int16_t *, const int16_t *);
void gt32_invntt_tail_u3_avx2(int16_t *, const int16_t *);
enum { WORDS=768, SAMPLES=20 };
typedef void (*bench_fn)(void);
static _Alignas(64) int16_t input[WORDS], control_out[WORDS], candidate_out[WORDS];
static volatile uint64_t sink;
static void control(void){ntruplus768_invntt_tail_avx2(control_out,input);sink+=(uint16_t)control_out[0];}
static void candidate(void){gt32_invntt_tail_u3_avx2(candidate_out,input);sink+=(uint16_t)candidate_out[0];}
static uint64_t start_tsc(void){_mm_lfence();return __rdtsc();}
static uint64_t stop_tsc(void){unsigned x;uint64_t t=__rdtscp(&x);_mm_lfence();return t;}
static double measure_tsc(bench_fn f,unsigned n){uint64_t a=start_tsc();for(unsigned i=0;i<n;i++)f();return(double)(stop_tsc()-a)/n;}
static int perf_open(uint64_t config){struct perf_event_attr a;memset(&a,0,sizeof a);a.type=PERF_TYPE_HARDWARE;a.size=sizeof a;a.config=config;a.disabled=1;a.exclude_kernel=1;a.exclude_hv=1;return(int)syscall(SYS_perf_event_open,&a,0,-1,-1,0UL);}
static double measure_perf(bench_fn f,unsigned n,int fd){uint64_t x=0;ioctl(fd,PERF_EVENT_IOC_RESET,0);ioctl(fd,PERF_EVENT_IOC_ENABLE,0);for(unsigned i=0;i<n;i++)f();ioctl(fd,PERF_EVENT_IOC_DISABLE,0);if(read(fd,&x,sizeof x)!=(ssize_t)sizeof x)return 0;return(double)x/n;}
static int cmpd(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return(x>y)-(x<y);}
static double median(double x[SAMPLES]){double y[SAMPLES];memcpy(y,x,sizeof y);qsort(y,SAMPLES,sizeof y[0],cmpd);return.5*(y[9]+y[10]);}
static void metric(const char*n,int fd,unsigned it){double a[SAMPLES],b[SAMPLES],d[SAMPLES];unsigned w=0;for(unsigned i=0;i<SAMPLES;i++){if(i&1){b[i]=fd<0?measure_tsc(candidate,it):measure_perf(candidate,it,fd);a[i]=fd<0?measure_tsc(control,it):measure_perf(control,it,fd);}else{a[i]=fd<0?measure_tsc(control,it):measure_perf(control,it,fd);b[i]=fd<0?measure_tsc(candidate,it):measure_perf(candidate,it,fd);}d[i]=b[i]-a[i];w+=d[i]<0;}printf("metric=%s control=%.3f candidate=%.3f delta=%.3f wins=%u/%u\n",n,median(a),median(b),median(d),w,SAMPLES);}
static int correctness(void){uint32_t s=1;for(unsigned trial=0;trial<1000;trial++){for(unsigned i=0;i<WORDS;i++){s=s*1664525u+1013904223u;input[i]=(int16_t)((int)(s%3823)-1911);}ntruplus768_invntt_tail_avx2(control_out,input);gt32_invntt_tail_u3_avx2(candidate_out,input);if(memcmp(control_out,candidate_out,sizeof control_out)){fprintf(stderr,"mismatch trial=%u\n",trial);return 0;}}return 1;}
int main(int argc,char**argv){unsigned it=argc>1?(unsigned)strtoul(argv[1],0,0):4000,cpu=argc>2?(unsigned)strtoul(argv[2],0,0):1;cpu_set_t set;CPU_ZERO(&set);CPU_SET(cpu,&set);if(sched_setaffinity(0,sizeof set,&set))return 2;if(!correctness())return 1;for(unsigned i=0;i<100;i++){control();candidate();}int cyc=perf_open(PERF_COUNT_HW_CPU_CYCLES),ins=perf_open(PERF_COUNT_HW_INSTRUCTIONS);printf("iterations=%u cpu=%u correctness=pass\n",it,cpu);metric("tsc",-1,it);metric("core_cycles",cyc,it);metric("instructions",ins,it);if(cyc>=0)close(cyc);if(ins>=0)close(ins);printf("sink=%llu\n",(unsigned long long)sink);return 0;}
