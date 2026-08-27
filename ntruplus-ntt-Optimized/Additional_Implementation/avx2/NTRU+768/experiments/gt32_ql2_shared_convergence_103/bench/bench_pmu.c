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

enum{S=20};typedef void(*fn)(void);static volatile uint64_t sink;
static _Alignas(64) int16_t coeff[768],front[768],m[768],q[768],h[768],r[768],out[768];
static _Alignas(64) uint8_t wire[1152],pk[1152],coins[96],ct[1152],ss[32];
static uint64_t rs=UINT64_C(0x10355aa55aa55aa5);static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
static void f0(void){ntruplus768_ntt_m_avx2(out,front);sink+=(uint16_t)out[0];}static void f1(void){gt103_ntt_ql2_avx2(out,front);sink+=(uint16_t)out[0];}
static void b0(void){ntruplus768_basemul_general_m_avx2(out,h,r);sink+=(uint16_t)out[0];}static void b1(void){gt103_basemul_general_ql2_avx2(out,h,r);sink+=(uint16_t)out[0];}
static void q0(void){ntruplus768_pack_m_sum_highrange12699_avx2(wire,m,m);sink+=wire[0];}static void q1(void){gt103_pack_ql2_sum_avx2(wire,q,q);sink+=wire[0];}
static void i0(void){ntruplus768_ntt_frontend_avx2(front,coeff);ntruplus768_ntt_m_avx2(m,front);ntruplus768_basemul_general_m_avx2(out,h,r);ntruplus768_pack_m_sum_highrange12699_avx2(wire,out,m);sink+=wire[0];}
static void i1(void){ntruplus768_ntt_frontend_avx2(front,coeff);gt103_ntt_ql2_avx2(q,front);gt103_basemul_general_ql2_avx2(out,h,r);gt103_pack_ql2_sum_avx2(wire,out,q);sink+=wire[0];}
static void e0(void){sink+=ntruplus768_enc_derand_impl(ct,ss,pk,coins)+ct[0]+ss[0];}static void e1(void){sink+=gt103_encap_ql2(ct,ss,pk,coins)+ct[0]+ss[0];}
static void x0(void){sink+=gt103_encap_matched_control(ct,ss,pk,coins)+ct[0]+ss[0];}static void x1(void){sink+=gt103_encap_matched_candidate(ct,ss,pk,coins)+ct[0]+ss[0];}
static int openp(uint64_t c){struct perf_event_attr a;memset(&a,0,sizeof a);a.type=PERF_TYPE_HARDWARE;a.size=sizeof a;a.config=c;a.disabled=1;a.exclude_kernel=1;a.exclude_hv=1;return syscall(SYS_perf_event_open,&a,0,-1,-1,0UL);}
static double one(fn f,unsigned n,int fd){uint64_t v;ioctl(fd,PERF_EVENT_IOC_RESET,0);ioctl(fd,PERF_EVENT_IOC_ENABLE,0);for(unsigned i=0;i<n;i++)f();ioctl(fd,PERF_EVENT_IOC_DISABLE,0);if(read(fd,&v,8)!=8)return 0;return(double)v/n;}
static int cmp(const void*a,const void*b){double x=*(double*)a,y=*(double*)b;return(x>y)-(x<y);}static double med(double*x){double y[S];memcpy(y,x,sizeof y);qsort(y,S,sizeof(double),cmp);return.5*(y[9]+y[10]);}
static void metric(const char*n,fn a,fn b,unsigned it,const char*m,int fd){double x[S],y[S],d[S];unsigned w=0;for(int s=0;s<S;s++){if(s&1){y[s]=one(b,it,fd);x[s]=one(a,it,fd);}else{x[s]=one(a,it,fd);y[s]=one(b,it,fd);}d[s]=y[s]-x[s];w+=d[s]<0;}printf("region=%s metric=%s control=%.3f candidate=%.3f delta=%.3f wins=%u/%u\n",n,m,med(x),med(y),med(d),w,S);}
static void init(void){for(int j=0;j<768;j++){coeff[j]=(int16_t)((int)(rnd()%3457)-1728);h[j]=(int16_t)((int)(rnd()%3457)-1728);r[j]=(int16_t)((int)(rnd()%3457)-1728);}ntruplus768_ntt_frontend_avx2(front,coeff);ntruplus768_ntt_m_avx2(m,front);gt103_ntt_ql2_avx2(q,front);for(int j=0;j<384;j++){uint16_t x=rnd()%3457,y=rnd()%3457;pk[3*j]=x;pk[3*j+1]=(uint8_t)((x>>8)|(y<<4));pk[3*j+2]=(uint8_t)(y>>4);}for(int j=0;j<96;j++)coins[j]=(uint8_t)rnd();}
int main(void){cpu_set_t s;CPU_ZERO(&s);CPU_SET(1,&s);if(sched_setaffinity(0,sizeof s,&s))return 2;init();for(int j=0;j<100;j++){f0();f1();b0();b1();q0();q1();i0();i1();e0();e1();x0();x1();}int cyc=openp(PERF_COUNT_HW_CPU_CYCLES),ins=openp(PERF_COUNT_HW_INSTRUCTIONS);if(cyc<0||ins<0){perror("perf_event_open");return 3;}struct X{const char*n;fn a,b;unsigned it;}x[]={{"forward",f0,f1,4096},{"b3",b0,b1,4096},{"q24",q0,q1,4096},{"island",i0,i1,2048},{"encap",e0,e1,256},{"encap_matched",x0,x1,256}};for(unsigned j=0;j<sizeof x/sizeof*x;j++){metric(x[j].n,x[j].a,x[j].b,x[j].it,"core_cycles",cyc);metric(x[j].n,x[j].a,x[j].b,x[j].it,"instructions",ins);}close(cyc);close(ins);printf("sink=%llu\n",(unsigned long long)sink);}
