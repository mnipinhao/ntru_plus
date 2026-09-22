/* Everything this round measured, in cycles.
 *
 * The clock witness is 500,000 dependent ADDs, one cycle each, so its own
 * duration IS the cycle length: freq = 500000 / witness_ns.  No PMU needed and
 * it works identically on both machines. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#ifdef __APPLE__
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
#else
static inline uint64_t ns(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
#endif
#include "inverse_tables.h"
#include "inverse16_tables.h"
typedef void (*I16)(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_st1_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_lane_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_strq_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_tail_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void crepmod3_ternary_asm(int16_t*);
void packed_i9(int16_t*,int16_t*,const int16_t*,const int16_t*);
void packed_i9_scatter(int16_t*,int16_t*,const int16_t*,const int16_t*);
void repack_hand_asm(int16_t*,const int16_t*,const int16_t*);
void repack_sched_asm(int16_t*,const int16_t*,const int16_t*);
void p28_paired_i16(int16_t*,int16_t*,long,const int16_t*,const int16_t*);
void p29_tail_direct(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void p29_main_route(int16_t*,const int16_t*);

static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}

static int16_t out[1024], scr[1024], mn[768], tl[96], in9[864];
static const int BASE[6]={0,12,1,13,2,14};
static const int SC[12]={0,64,256,320,512,576,4,68,260,324,516,580};
static const int TL[12]={768,832,769,833,770,834,771,835,772,836,773,837};
static const int IN[12]={0,24,8,32,16,40,432,456,440,464,448,472};
static const int TW[12]={0,144,0,144,0,144,288,432,288,432,288,432};

static int i16_x6(I16 k){ for(int i=0;i<6;i++)
    k(out+BASE[i],scr+128*i,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  return out[0]+out[431]; }
static int f_cur (void){ return i16_x6(invntt16_asm); }
static int f_st1 (void){ return i16_x6(invntt16_st1_asm); }
static int f_strd(void){ return i16_x6(invntt16_lane_asm); }
static int f_strq(void){ return i16_x6(invntt16_strq_asm); }
static int i9(void (*k)(int16_t*,int16_t*,const int16_t*,const int16_t*)){
  for(int i=0;i<12;i++) k(scr+SC[i],scr+TL[i],in9+IN[i],&invntt9_constants[0][0][0][0][0]+TW[i]);
  return scr[0]+scr[800]; }
static int f_i9  (void){ return i9(packed_i9); }
static int f_i9s (void){ return i9(packed_i9_scatter); }
static int f_rph (void){ repack_hand_asm(out,mn,tl);  return out[0]+out[863]; }
static int f_rps (void){ repack_sched_asm(out,mn,tl); return out[0]+out[863]; }
static int f_prod(void){
  for(int i=0;i<6;i++)
    invntt16_asm(out+BASE[i],scr+128*i,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  invntt16_tail_asm(out+24,scr+768,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
  crepmod3_ternary_asm(out); return out[0]+out[863]; }
static int f_p29 (void){
  for(int i=0;i<3;i++)
    p28_paired_i16(scr+256*i,scr+256*i+128,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
  p29_tail_direct(out,scr+768,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
  p29_main_route(out,scr); return out[0]+out[863]; }

typedef struct { const char *name; int (*f)(void); int calls; } Case;
static Case C_[] = {
  {"invntt16 x6  現行 (128 umov+128 strh)", f_cur, 6},
  {"invntt16 x6  128 st1 {v.h}[lane]",      f_st1, 6},
  {"invntt16 x6  32 str d  (P95)",          f_strd,6},
  {"invntt16 x6  16 str q  (無效, 見說明)", f_strq,6},
  {"packed_i9 x12  現行 (24 store)",        f_i9,  12},
  {"packed_i9 x12  P95 散射 (72 store)",    f_i9s, 12},
  {"repack  手寫",                          f_rph, 1},
  {"repack  Slothy 排程",                   f_rps, 1},
  {"main+tail+ternary  production",         f_prod,1},
  {"main+tail+ternary  P29",                f_p29, 1},
};
#define NC ((int)(sizeof C_/sizeof*C_))
#define N 2000
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
#endif
  for(int i=0;i<1024;i++) scr[i]=(int16_t)((i*2654435761u)%5235)-2617;
  for(int i=0;i<768;i++)  mn[i]=(int16_t)i;
  for(int i=0;i<96;i++)   tl[i]=(int16_t)i;
  for(int i=0;i<864;i++)  in9[i]=(int16_t)((i*2654435761u)%5235)-2617;
  static uint64_t best[NC], bw[NC];
  for(int i=0;i<NC;i++){ best[i]=~0ull; bw[i]=0; }
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(int i=0;i<NC;i++) for(int k=0;k<N;k++) sink+=C_[i].f();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>4000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++) for(int i=0;i<NC;i++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=C_[i].f();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[i]){ best[i]=dt; bw[i]=d; } }
  double ghz = 500000.0/(double)wf;                /* 500k dependent ADDs */
  printf("  時脈見證: %.3f GHz\n\n", ghz);
  printf("  %-38s %10s %10s %10s\n","","ns","cycles","cyc/call");
  for(int i=0;i<NC;i++){
    double t=(double)best[i]/N, c=t*ghz;
    printf("  %-38s %10.1f %10.0f %10.0f\n",C_[i].name,t,c,c/C_[i].calls);
  }
  return 0;}
