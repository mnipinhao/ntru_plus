/* All eighteen hash calls in ONE process: three sets, two sides, three calls.
 *
 * The earlier comparison ran each set in its own binary, so the per-set spread
 * could have been code layout rather than code.  Here everything shares a
 * process, an i-cache and a round-robin schedule. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t ns(void){return clock_gettime_nsec_np(CLOCK_UPTIME_RAW);}
#define DECL(p) void p##hash_f(uint8_t*,const uint8_t*); \
                void p##hash_g(uint8_t*,const uint8_t*); \
                void p##hash_h(uint8_t*,const uint8_t*);
DECL(g768_) DECL(g864_) DECL(g1152_) DECL(o768_) DECL(o864_) DECL(o1152_)
static volatile unsigned sink;
static uint64_t witness(void){uint64_t x=0,t0=ns();
 for(long i=0;i<50000;i++) __asm__ volatile(
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
  "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n":"+r"(x));
 uint64_t d=ns()-t0; sink+=(unsigned)x; return d?d:1;}
static uint8_t pk[2048], msg[512], out[1024];
typedef void (*H)(uint8_t*, const uint8_t*);
typedef struct { const char *name; H f; const uint8_t *in; int perms; } Case;
static Case C_[] = {
 {"768  hash_f GT",       g768_hash_f,  pk,  9}, {"768  hash_f Off",  o768_hash_f,  pk,  9},
 {"768  hash_g GT",       g768_hash_g,  pk, 10}, {"768  hash_g Off",  o768_hash_g,  pk, 10},
 {"768  hash_h GT",       g768_hash_h,  msg, 2}, {"768  hash_h Off",  o768_hash_h,  msg, 2},
 {"864  hash_f GT",       g864_hash_f,  pk, 10}, {"864  hash_f Off",  o864_hash_f,  pk, 10},
 {"864  hash_g GT",       g864_hash_g,  pk, 11}, {"864  hash_g Off",  o864_hash_g,  pk, 11},
 {"864  hash_h GT",       g864_hash_h,  msg, 3}, {"864  hash_h Off",  o864_hash_h,  msg, 3},
 {"1152 hash_f GT",      g1152_hash_f,  pk, 13}, {"1152 hash_f Off", o1152_hash_f,  pk, 13},
 {"1152 hash_g GT",      g1152_hash_g,  pk, 15}, {"1152 hash_g Off", o1152_hash_g,  pk, 15},
 {"1152 hash_h GT",      g1152_hash_h,  msg, 4}, {"1152 hash_h Off", o1152_hash_h,  msg, 4},
};
#define NC ((int)(sizeof C_/sizeof*C_))
#define N 2000
static int which;
static int run(void){ C_[which].f(out, C_[which].in); return out[0]; }
int main(void){
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE,0);
  for(size_t i=0;i<sizeof pk;i++)  pk[i]=(uint8_t)(i*211u);
  for(size_t i=0;i<sizeof msg;i++) msg[i]=(uint8_t)(i*167u);
  static uint64_t best[NC]; for(int i=0;i<NC;i++) best[i]=~0ull;
  uint64_t wf=~0ull,t0=ns(); int st=0;
  for(int w=0;w<4000;w++){ for(which=0;which<NC;which++) for(int k=0;k<N;k++) sink+=run();
    uint64_t d=witness(); if(d<wf){wf=d;st=0;} else st++;
    if(st>=5 && ns()-t0>4000000000ull) break; }
  enum {R=301};
  for(int r=0;r<R;r++) for(which=0;which<NC;which++){
    uint64_t x=ns(); for(int k=0;k<N;k++) sink+=run();
    uint64_t dt=ns()-x, d=witness(); if(d<wf) wf=d;
    if(dt<best[which]) best[which]=dt; }
  double gz=500000.0/(double)wf;
  printf("  時脈見證 %.3f GHz   裸置換 158.33 ns\n\n",gz);
  printf("  %-18s%9s%9s%12s\n","","ns","置換","ns/置換");
  for(int i=0;i<NC;i++){ double t=(double)best[i]/N;
    printf("  %-18s%9.1f%9d%12.1f\n",C_[i].name,t,C_[i].perms,t/C_[i].perms); }
  printf("\n  %-10s%10s%10s%9s%12s\n","set","GT/置換","Off/置換","比","GT 包裝");
  const int base[3]={0,6,12}; const char*nm[3]={"768","864","1152"};
  for(int s=0;s<3;s++){
    double gt=0,of=0; int p=0;
    for(int k=0;k<3;k++){ int i=base[s]+2*k;
      gt+=(double)best[i]/N; of+=(double)best[i+1]/N; p+=C_[i].perms; }
    printf("  %-10s%10.1f%10.1f%9.3f%+12.1f\n",nm[s],gt/p,of/p,gt/of,gt/p-158.33);
  }
  return 0;}
