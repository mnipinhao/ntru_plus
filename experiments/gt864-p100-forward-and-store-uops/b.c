#include <stdio.h>
#include <stdint.h>
#include <time.h>
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
#else
static inline uint64_t ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
#endif
void st_q1(void*,long); void st_q2(void*,long); void st_q3(void*,long); void st_q4(void*,long);
typedef void(*K)(void*,long);
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static _Alignas(64) uint8_t buf[2048];
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  K KS[4]={st_q1,st_q2,st_q3,st_q4};
  const char*NM[4]={"64 x str q          ","32 x st1 {2 regs}   ",
                    "21 x st1 {3 regs}+1 ","16 x st1 {4 regs}   "};
  const int NI[4]={64,64,64,64};      /* store instructions, ignoring the ADDs */
  const int NS[4]={64,32,22,16};      /* store *instructions* actually issued  */
  enum {R=201}; const long REP=2000;
  uint64_t wf=~0ull,best[4]={~0ull,~0ull,~0ull,~0ull};
  for(int w=0;w<300;w++){ for(int i=0;i<4;i++) KS[i](buf,REP); uint64_t d=witness(); if(d<wf) wf=d; }
  for(int r=0;r<R;r++) for(int i=0;i<4;i++){
    uint64_t x=ns(); KS[i](buf,REP); uint64_t dt=ns()-x;
    uint64_t d=witness(); if(d<wf) wf=d;
    if(dt<best[i]) best[i]=dt; }
  double gz=500000.0/(double)wf;
  printf("  時脈見證: %.3f GHz\n",gz);
  printf("  %-22s%10s%12s%12s\n","形式","store 指令","cyc/趟","cyc/store 指令");
  for(int i=0;i<4;i++){
    double c=(double)best[i]/REP*gz;
    printf("  %-22s%10d%12.1f%12.2f\n",NM[i],NS[i],c,c/NS[i]);
  }
  (void)NI; return 0;}
