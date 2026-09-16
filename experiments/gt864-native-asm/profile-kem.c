#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#define N 21
static const char*names[N]={"Forward","BaseInv","BaseMul_R0","BaseMul_Rinv","BaseMulAdd","Inverse","ToBytes_full","ToBytes_small","FromBytes_checked","CBD","SOTP_encode","SOTP_decode","Triple","Sub","Crepmod3","hash_f","hash_g","hash_h","SHAKE_sampling","RNG","cleanup"};
static int fd,active;static uint64_t totals[N],calls[N],rng;static double overhead;
void randombytes(uint8_t*p,size_t n){while(n--){rng^=rng<<13;rng^=rng>>7;rng^=rng<<17;*p++=rng;}}
static uint64_t tick(void){uint64_t x;if(read(fd,&x,8)!=8)exit(3);return x;}
__attribute__((noinline)) uint64_t prof_start(void){return active?tick():0;}
__attribute__((noinline)) void prof_end(int i,uint64_t t){if(active){uint64_t e=tick();totals[i]+=e-t;calls[i]++;}}
typedef int(*keyfn)(uint8_t*,uint8_t*);typedef int(*encfn)(uint8_t*,uint8_t*,const uint8_t*);typedef int(*decfn)(uint8_t*,const uint8_t*,const uint8_t*);
struct api{keyfn key;encfn enc;decfn dec;};
static struct api load(const char*s){void*h=dlopen(s,RTLD_NOW|RTLD_LOCAL);if(!h){puts(dlerror());exit(2);}return(struct api){(keyfn)dlsym(h,"crypto_kem_keypair"),(encfn)dlsym(h,"crypto_kem_enc"),(decfn)dlsym(h,"crypto_kem_dec")};}
static uint8_t pk[1296],sk[2624],ct[1296],ss[32];
static void setup(struct api a){rng=0xb6123001;if(a.key(pk,sk))exit(4);rng=0xb6123002;if(a.enc(ct,ss,pk))exit(4);uint8_t out[32];if(a.dec(out,ct,sk)||memcmp(out,ss,32))exit(4);}
static void invoke(struct api a,int op,int k){rng=0xb6000000ULL+(uint64_t)k*0x9e3779b1ULL;int x=op==0?a.key(pk,sk):op==1?a.enc(ct,ss,pk):a.dec(ss,ct,sk);if(x)exit(4);}
static int cmp(const void*a,const void*b){uint64_t x=*(const uint64_t*)a,y=*(const uint64_t*)b;return(x>y)-(x<y);}
int main(int argc,char**argv){if(argc!=2)return 2;char path[80];snprintf(path,sizeof path,"./%s.so",argv[1]);struct api plain=load(path);snprintf(path,sizeof path,"./%s-prof.so",argv[1]);struct api prof=load(path);
 struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;a.config=PERF_COUNT_HW_CPU_CYCLES;a.exclude_kernel=1;a.exclude_hv=1;fd=syscall(__NR_perf_event_open,&a,0,-1,-1,0);if(fd<0){perror("perf");return 3;}
 uint64_t samples[1001];active=1;for(int j=0;j<1001;j++){uint64_t t=prof_start();prof_end(0,t);samples[j]=totals[0];totals[0]=calls[0]=0;}qsort(samples,1001,sizeof(uint64_t),cmp);overhead=samples[500];printf("overhead,%.3f\n",overhead);
 uint8_t saved[1296+2624+1296+32];active=0;setup(plain);memcpy(saved,pk,1296);memcpy(saved+1296,sk,2624);memcpy(saved+3920,ct,1296);memcpy(saved+5216,ss,32);active=1;setup(prof);if(memcmp(saved,pk,1296)||memcmp(saved+1296,sk,2624)||memcmp(saved+3920,ct,1296)||memcmp(saved+5216,ss,32))return 5;puts("instrumentation_equivalence=pass");
 const char*ops[]={"keygen","encaps","decaps"};
 for(int op=0;op<3;op++)for(int sample=-3;sample<21;sample++){
  active=0;setup(prof);memset(totals,0,sizeof totals);memset(calls,0,sizeof calls);active=1;int n=op==0?4:20;
  for(int k=0;k<n;k++)invoke(prof,op,k);active=0;
  if(sample>=0)for(int i=0;i<N;i++)if(calls[i])printf("profile,%s,%s,%s,%.3f,%.3f,%.3f\n",ops[op],argv[1],names[i],(double)totals[i]/n,((double)totals[i]-overhead*calls[i])/n,(double)calls[i]/n);
 }
}
