/* A76 cycle gate: production vs P68, same binary, interleaved rounds. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
#include "invntt9_lane_tables.h"
void invntt_ternary_asm(int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*);
void invntt_ternary_p68_asm(int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*);
static int fd;
static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)exit(3);return v;}
static int cmp(const void*a,const void*b){uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b;return(x>y)-(x<y);}
#define R 201
#define N 200
int main(void){
  struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;
  a.config=PERF_COUNT_HW_CPU_CYCLES;a.exclude_kernel=1;a.exclude_hv=1;
  fd=syscall(__NR_perf_event_open,&a,0,-1,-1,0);if(fd<0){perror("perf");return 3;}
  static int16_t in[1152],out[1152];
  for(int i=0;i<1152;i++) in[i]=(int16_t)((i*2654435761u)%3457)-1728;
  static uint64_t s[2][R];
  uint64_t ov; {uint64_t t=rd();ov=rd()-t;}
  for(int r=0;r<R;r++) for(int v=0;v<2;v++){
    uint64_t t0=rd();
    for(int k=0;k<N;k++){
      if(v==0) invntt_ternary_asm(out,in,&invntt9_constants[0][0][0][0][0],&invntt16_constants[0][0],&invntt16_main_constants[0][0],&invntt16_tail_constants[0][0]);
      else     invntt_ternary_p68_asm(out,in,&invntt9_constants_lane[0][0][0][0],&invntt16_constants[0][0],&invntt16_main_constants[0][0],&invntt16_tail_constants[0][0]);
    }
    s[v][r]=(rd()-t0-ov)/N;
  }
  for(int v=0;v<2;v++) qsort(s[v],R,sizeof(uint64_t),cmp);
  printf("  production  median %6llu cycles   min %6llu\n",(unsigned long long)s[0][R/2],(unsigned long long)s[0][0]);
  printf("  P68         median %6llu cycles   min %6llu\n",(unsigned long long)s[1][R/2],(unsigned long long)s[1][0]);
  double d=100.0*((double)s[1][R/2]-(double)s[0][R/2])/(double)s[0][R/2];
  printf("  delta       %+.2f%% (median)\n",d);
  return 0;}
