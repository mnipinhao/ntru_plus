#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <arm_neon.h>
#include <pthread.h>
#include <sys/qos.h>
#include "scatter.h"
#define N 1152
#define G 36
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
static int16_t out[N+64], seed[N];
__attribute__((noinline)) static void A(int16_t *o,const int16_t *s){
  for(int g=0;g<G;g++){
    int16x8_t v0=vld1q_s16(s+g*32),v1=vld1q_s16(s+g*32+8),v2=vld1q_s16(s+g*32+16),v3=vld1q_s16(s+g*32+24);
    v0=vaddq_s16(v0,v3);v1=vaddq_s16(v1,v0);v2=vaddq_s16(v2,v1);v3=vaddq_s16(v3,v2);
    vst1q_s16(o+g*32,v0);vst1q_s16(o+g*32+8,v1);vst1q_s16(o+g*32+16,v2);vst1q_s16(o+g*32+24,v3);}}
__attribute__((noinline)) static void B(int16_t *o,const int16_t *s){
  for(int g=0;g<G;g++){const unsigned short*w=scatter[g];
    int16x8_t v0=vld1q_s16(s+g*32),v1=vld1q_s16(s+g*32+8),v2=vld1q_s16(s+g*32+16),v3=vld1q_s16(s+g*32+24);
    v0=vaddq_s16(v0,v3);v1=vaddq_s16(v1,v0);v2=vaddq_s16(v2,v1);v3=vaddq_s16(v3,v2);
    int16x8_t a0=vtrn1q_s16(v0,v1),a1=vtrn2q_s16(v0,v1),a2=vtrn1q_s16(v2,v3),a3=vtrn2q_s16(v2,v3);
    int32x4_t b0=vtrn1q_s32(vreinterpretq_s32_s16(a0),vreinterpretq_s32_s16(a2));
    int32x4_t b1=vtrn2q_s32(vreinterpretq_s32_s16(a0),vreinterpretq_s32_s16(a2));
    int32x4_t b2=vtrn1q_s32(vreinterpretq_s32_s16(a1),vreinterpretq_s32_s16(a3));
    int32x4_t b3=vtrn2q_s32(vreinterpretq_s32_s16(a1),vreinterpretq_s32_s16(a3));
    vst1_s16(o+w[0],vget_low_s16(vreinterpretq_s16_s32(b0)));
    vst1_s16(o+w[2],vget_low_s16(vreinterpretq_s16_s32(b1)));
    vst1_s16(o+w[1],vget_low_s16(vreinterpretq_s16_s32(b2)));
    vst1_s16(o+w[3],vget_low_s16(vreinterpretq_s16_s32(b3)));
    vst1_s16(o+w[4],vget_high_s16(vreinterpretq_s16_s32(b0)));
    vst1_s16(o+w[6],vget_high_s16(vreinterpretq_s16_s32(b1)));
    vst1_s16(o+w[5],vget_high_s16(vreinterpretq_s16_s32(b2)));
    vst1_s16(o+w[7],vget_high_s16(vreinterpretq_s16_s32(b3)));}}
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=nsec();
 for(long i=0;i<50000;i++) __asm__ volatile("add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=nsec()-t0; sink+=(unsigned)x; return d?d:1;}
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(int i=0;i<N;i++) seed[i]=(int16_t)(i*2654435761u);
  const long M=20000; volatile long ck=0;
  uint64_t wf=~0ull,best[2]={~0ull,~0ull}; int acc[2]={0,0};
  uint64_t t0=nsec(); int st=0;
  for(int w=0;w<4000;w++){
    for(long k=0;k<M;k++){A(out,seed); ck+=out[k%N]; B(out,seed); ck+=out[k%N];}
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && nsec()-t0>3000000000ull) break; }
  for(int r=0;r<41;r++){
    uint64_t a=nsec(); for(long k=0;k<M;k++){A(out,seed); ck+=out[k%N];} uint64_t d0=nsec()-a;
    uint64_t w0=witness(); if(w0<wf) wf=w0;
    if(w0*98<=wf*100){acc[0]++; if(d0<best[0]) best[0]=d0;}
    a=nsec(); for(long k=0;k<M;k++){B(out,seed); ck+=out[k%N];} uint64_t d1=nsec()-a;
    uint64_t w1=witness(); if(w1<wf) wf=w1;
    if(w1*98<=wf*100){acc[1]++; if(d1<best[1]) best[1]=d1;} }
  double a=(double)best[0]/M,b=(double)best[1]/M;
  printf("  A 連續 str q                %6.1f ns   (%d/41)\n",a,acc[0]);
  printf("  B 轉置 + 散射 64-bit store  %6.1f ns   (%d/41)\n",b,acc[1]);
  printf("  轉換端多付                  %+6.1f ns    vs 打包器可回收 51.1 ns\n",b-a);
  printf("  (ck=%ld)\n",ck); return 0;}
