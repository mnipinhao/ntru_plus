#define _GNU_SOURCE
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/syscall.h>
#include <unistd.h>
enum{PK=1296,SK=2624,CT=1296,SS=32,N=864}; typedef struct{int16_t c[N];}poly;
typedef int(*keyfn)(uint8_t*,uint8_t*); typedef int(*encfn)(uint8_t*,uint8_t*,const uint8_t*); typedef int(*decfn)(uint8_t*,const uint8_t*,const uint8_t*); typedef int(*invfn)(poly*,const poly*); typedef void(*unary)(poly*,const poly*); typedef void(*bytesfn)(uint8_t*,const int16_t*);
struct api{keyfn key;encfn enc;decfn dec;invfn inv;unary ntt;bytesfn full,small;}; struct counts{uint64_t n,v[3];}; static int fd; static uint64_t state=864; static volatile unsigned sink;
void randombytes(uint8_t*out,size_t n){while(n--){state^=state<<13;state^=state>>7;state^=state<<17;*out++=state;}}
static void*must(void*h,const char*n){void*p=dlsym(h,n);if(!p){fprintf(stderr,"missing %s: %s\n",n,dlerror());exit(2);}return p;}
static struct api load(const char*p){void*h=dlopen(p,RTLD_NOW|RTLD_LOCAL);if(!h){puts(dlerror());exit(2);}return(struct api){must(h,"crypto_kem_keypair"),must(h,"crypto_kem_enc"),must(h,"crypto_kem_dec"),must(h,"gt864_native_poly_baseinv"),must(h,"gt_d1_poly_ntt"),must(h,"gt864_fr0_tobytes_full"),must(h,"gt864_fr0_tobytes_small")};}
static int event(uint64_t c,int g){struct perf_event_attr a={0};a.size=sizeof a;a.type=PERF_TYPE_HARDWARE;a.config=c;a.exclude_kernel=1;a.exclude_hv=1;a.disabled=g<0;a.read_format=PERF_FORMAT_GROUP;return syscall(__NR_perf_event_open,&a,0,-1,g,0);} static struct counts tick(void){struct counts c;if(read(fd,&c,sizeof c)!=sizeof c||c.n!=3)exit(3);return c;}
static int modeq(const poly*a,const poly*b){for(int i=0;i<N;i++)if((a->c[i]-b->c[i])%3457)return 0;return 1;} static uint8_t pk[2][PK],sk[2][SK],ct[2][CT],ss[2][SS];
static void setup(struct api a,int v,uint64_t seed){state=seed;if(a.key(pk[v],sk[v]))exit(4);state=seed+1;if(a.enc(ct[v],ss[v],pk[v]))exit(4);uint8_t out[SS];if(a.dec(out,ct[v],sk[v])||memcmp(out,ss[v],SS))exit(4);}
int main(int argc,char**argv){if(argc!=4)return 2;struct api a[2]={load(argv[1]),load(argv[2])};int reverse=atoi(argv[3]);
 for(int t=0;t<24;t++){setup(a[0],0,100+t);setup(a[1],1,100+t);if(memcmp(pk[0],pk[1],PK)||memcmp(sk[0],sk[1],SK)||memcmp(ct[0],ct[1],CT)||memcmp(ss[0],ss[1],SS))return 5;uint8_t bad[CT],o0[SS],o1[SS];memcpy(bad,ct[0],CT);bad[11+37*t]^=128;if(a[0].dec(o0,bad,sk[0])!=a[1].dec(o1,bad,sk[1])||memcmp(o0,o1,SS))return 6;}
 poly input,out[2],zero={0};for(int attempts=0;;attempts++){state=0x123400+attempts;randombytes((uint8_t*)&input,sizeof input);for(int i=0;i<N;i++)input.c[i]=3*((uint16_t)input.c[i]%3-1);input.c[0]++;a[0].ntt(&input,&input);if(!a[0].inv(&out[0],&input))break;if(attempts==999)return 7;} if(a[1].inv(&out[1],&input)||!modeq(&out[0],&out[1]))return 8;if(a[0].inv(&out[0],&zero)!=1||a[1].inv(&out[1],&zero)!=1)return 9; puts("correctness=pass valid=24 tampered=24 baseinv_modq=pass failure=pass");
 fd=event(PERF_COUNT_HW_CPU_CYCLES,-1);int fi=event(PERF_COUNT_HW_INSTRUCTIONS,fd),fb=event(PERF_COUNT_HW_BRANCH_INSTRUCTIONS,fd);if(fd<0||fi<0||fb<0)return 3;ioctl(fd,PERF_EVENT_IOC_ENABLE,PERF_IOC_FLAG_GROUP);const char*names[]={"keygen","encaps","decaps"};
 for(int op=0;op<3;op++)for(int sample=-5;sample<31;sample++)for(int pos=0;pos<2;pos++){int v=pos^reverse,n=op?20:4;setup(a[v],v,0x9911);struct counts x=tick();for(int k=0;k<n;k++){state=0x880000+k*0x9e3779b1ULL;int r=op==0?a[v].key(pk[v],sk[v]):op==1?a[v].enc(ct[v],ss[v],pk[v]):a[v].dec(ss[v],ct[v],sk[v]);if(r)exit(11);sink+=ss[v][0];}struct counts y=tick();if(sample>=0)printf("full,%s,%s,%.3f,%.3f,%.3f\n",names[op],v?"candidate":"baseline",(double)(y.v[0]-x.v[0])/n,(double)(y.v[1]-x.v[1])/n,(double)(y.v[2]-x.v[2])/n);}
 for(int op=0;op<2;op++)for(int sample=-5;sample<31;sample++)for(int pos=0;pos<2;pos++){int v=pos^reverse,n=32;struct counts x=tick();for(int k=0;k<n;k++)sink+=a[v].inv(&out[v],op?&zero:&input);struct counts y=tick();if(sample>=0)printf("component,%s,%s,%.3f,%.3f,%.3f\n",op?"baseinv_failure":"baseinv_success",v?"candidate":"baseline",(double)(y.v[0]-x.v[0])/n,(double)(y.v[1]-x.v[1])/n,(double)(y.v[2]-x.v[2])/n);}
}
