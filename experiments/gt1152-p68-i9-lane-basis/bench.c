#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <stdlib.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
#include "invntt9_lane_tables.h"
void invntt_ternary_asm(int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*);
void invntt_ternary_p68_asm(int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*);
static int cmp(const void*a,const void*b){double x=*(const double*)a,y=*(const double*)b;return x<y?-1:x>y;}
static double ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec*1e9+t.tv_nsec;}
#define N 2000
int main(void){
  static int16_t in[1152],out[1152]; double s[64];
  for(int i=0;i<1152;i++) in[i]=(int16_t)((i*2654435761u)%3457)-1728;
  for(int v=0;v<2;v++){
    for(int r=0;r<64;r++){
      double t0=ns();
      for(int k=0;k<N;k++){
        if(v==0) invntt_ternary_asm(out,in,&invntt9_constants[0][0][0][0][0],&invntt16_constants[0][0],&invntt16_main_constants[0][0],&invntt16_tail_constants[0][0]);
        else     invntt_ternary_p68_asm(out,in,&invntt9_constants_lane[0][0][0][0],&invntt16_constants[0][0],&invntt16_main_constants[0][0],&invntt16_tail_constants[0][0]);
      }
      s[r]=(ns()-t0)/N;
    }
    qsort(s,64,sizeof(double),cmp);
    printf("  %-12s median %7.2f ns   min %7.2f ns\n", v?"P68":"production", s[32], s[0]);
  }
  return 0;}
