#include <stdio.h>
#include <stdint.h>
#include <time.h>
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static volatile unsigned sink;
static uint64_t wit(long it){uint64_t x=0,t0=nsec();
 for(long i=0;i<it;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 sink+=(unsigned)x; return nsec()-t0;}
int main(void){
  struct timespec s={2,0}; nanosleep(&s,0);          /* let the core go idle */
  uint64_t t0=nsec();
  for(int i=0;i<200;i++){ uint64_t d=wit(50000);
    double ms=(double)(nsec()-t0)/1e6, mhz=500000.0/(double)d*1000.0;
    if(i<6||i%10==0) printf("  %7.1f ms  %.0f MHz\n",ms,mhz); }
  return 0;}
