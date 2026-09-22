#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include "internal.h"
#include "poly.h"

void ntruplus768_exp001_basemul_eager_m(int16_t *,const int16_t *,const int16_t *);
/* Exported only in the research object; copied fixed constants, not an oracle. */
extern const int16_t ntruplus768_exp001_eager_lambda[192];
enum { N=768,Q=3457 };
typedef struct __attribute__((aligned(64))) { int16_t pre[32],v[N],post[32]; } guarded;
static guarded h,r,c,d;
static _Alignas(64) int16_t input[N],work[N],oldh[N],oldr[N],alias[N];
static uint64_t seed=768;
static uint32_t rnd(void) {seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return (uint32_t)seed;}
static int mod(int64_t x) {x%=Q;return (int)(x<0?x+Q:x);}
static void check(int yes,const char *s) {if(!yes){fprintf(stderr,"FAIL %s\n",s);exit(1);}}
int main(void) {
    for(int t=0;t<10003;t++) {
        memset(&c,0x5a,sizeof c);memset(&d,0x5a,sizeof d);
        for(int i=0;i<N;i++) {
            h.v[i]=t<2?(t?Q-1:0):(int16_t)(rnd()%Q);
            input[i]=t<1536?(i==t/2?(t%2?-1:1):0):
                     t==1536?0:t==1537?(i%2?-1:1):(int16_t)((int)(rnd()%3)-1);
        }
        ntruplus768_ntt_frontend_avx2(work,input);
        ntruplus768_ntt_m_avx2(r.v,work);
        /* Include conservative-bound extremes without relying on reachability. */
        if(t>=9999) for(int i=0;i<N;i++) r.v[i]=(i+t)%2?15592:-15592;
        memcpy(oldh,h.v,sizeof oldh);memcpy(oldr,r.v,sizeof oldr);
        ntruplus768_basemul_general_m_avx2(c.v,h.v,r.v);
        ntruplus768_exp001_basemul_eager_m(d.v,h.v,r.v);
        check(!memcmp(&c,&d,sizeof c),"raw exact and output canaries");
        check(!memcmp(h.v,oldh,sizeof oldh)&&!memcmp(r.v,oldr,sizeof oldr),"immutability");
        for(int b=0;b<12;b++) for(int l=0;l<16;l++) {
            /* lambda table holds lambda*R; inverse(R) mod q = 2775. */
            int lam=mod((int64_t)ntruplus768_exp001_eager_lambda[b*16+l]*2775);
            check(mod((int64_t)867*2775*2775)==1,"Montgomery domain oracle");
            for(int j=0;j<4;j++) {
                int64_t sum=0;
                for(int a=0;a<4;a++) for(int z=0;z<4;z++) if((a+z)%4==j)
                    sum+=(int64_t)h.v[b*64+a*16+l]*r.v[b*64+z*16+l]*(a+z>=4?lam:1);
                check(mod(sum)==mod(d.v[b*64+j*16+l]),"independent quartic convolution");
            }
        }
        if(t<40) {
            memcpy(alias,h.v,sizeof alias);
            ntruplus768_exp001_basemul_eager_m(alias,alias,r.v);
            check(!memcmp(alias,c.v,sizeof alias),"out=h alias");
            memcpy(alias,r.v,sizeof alias);
            ntruplus768_exp001_basemul_eager_m(alias,h.v,alias);
            check(!memcmp(alias,c.v,sizeof alias),"out=r alias");
        }
    }
    long page_signed=sysconf(_SC_PAGESIZE);
    check(page_signed>0,"page size");
    size_t page=(size_t)page_signed;
    void *regions[3];int16_t *ends[3];
    for(int j=0;j<3;j++) {
        regions[j]=mmap(NULL,2*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        check(regions[j]!=MAP_FAILED,"mmap");
        check(!mprotect((char*)regions[j]+page,page,PROT_NONE),"guard");
        ends[j]=(int16_t*)((char*)regions[j]+page-sizeof input);
    }
    memcpy(ends[0],h.v,sizeof input);memcpy(ends[1],r.v,sizeof input);
    ntruplus768_exp001_basemul_eager_m(ends[2],ends[0],ends[1]);
    check(!memcmp(ends[2],c.v,sizeof input),"guard-page tails");
    for(int j=0;j<3;j++) munmap(regions[j],2*page);
    puts("PASS 10003 raw/quartic cases, signed impulses, bounds, alias, canary, immutable, guard-page");
}
