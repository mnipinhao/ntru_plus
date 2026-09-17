#define _GNU_SOURCE
#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include "cpucycles.h"
#define N 768
#define SAMPLES 31
#define ITERS 2048
void gt103_basemul_general_ql2_avx2(int16_t*,const int16_t*,const int16_t*);
void gt135_basemul_general_ql2_native_e0(int16_t*,const int16_t*,const int16_t*);
static _Alignas(64) int16_t a[N],b[N],aq[N],bq[N],out[N];static volatile uint64_t sink;static uint64_t rs=135;
static uint32_t rnd(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return(uint32_t)rs;}
static void cvt(int16_t*o,const int16_t*x){static const int l[4][4]={{0,1,8,9},{2,3,10,11},{4,5,12,13},{6,7,14,15}};for(int g=0;g<12;g++)for(int r=0;r<4;r++)for(int k=0;k<4;k++)for(int c=0;c<4;c++)o[g*64+r*16+4*k+c]=x[g*64+c*16+l[r][k]];}
static int cmp(const void*x,const void*y){double a=*(const double*)x,b=*(const double*)y;return(a>b)-(a<b);}static double med(double*x){qsort(x,SAMPLES,sizeof*x,cmp);return x[SAMPLES/2];}
int main(int argc,char**argv){int flip=argc>1?atoi(argv[1]):0;cpu_set_t set;CPU_ZERO(&set);CPU_SET(1,&set);sched_setaffinity(0,sizeof set,&set);for(int i=0;i<N;i++){a[i]=(int16_t)((int)(rnd()%3457)-1728);b[i]=(int16_t)((int)(rnd()%3457)-1728);}cvt(aq,a);cvt(bq,b);double ca[SAMPLES],cb[SAMPLES];
 for(int s=0;s<SAMPLES;s++){int first=(s+flip)&1;for(int side=0;side<2;side++){int candidate=first?1-side:side;uint64_t x=cpucycles();for(int z=0;z<ITERS;z++){if(candidate)gt135_basemul_general_ql2_native_e0(out,aq,bq);else gt103_basemul_general_ql2_avx2(out,a,b);sink+=(uint16_t)out[z%N];}uint64_t y=cpucycles();(candidate?cb:ca)[s]=(double)(y-x)/ITERS;}}
 double x=med(ca),y=med(cb);printf("{\"control\":%.6f,\"candidate\":%.6f,\"delta\":%.6f,\"sink\":%llu}\n",x,y,y-x,(unsigned long long)sink);return 0;}
