#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "internal.h"
#include "poly.h"

enum { BANKS=16, BLOCKS=32 };
void ntruplus768_exp001_encap_live_b3_pack(uint8_t *,const int16_t *,
                                             const int16_t *,const int16_t *);
int ntruplus768_exp001_enc_derand_live_b3_pack(uint8_t *,uint8_t *,
                                                const uint8_t *,const uint8_t *);

typedef struct __attribute__((aligned(64))) {
    int16_t h[NTRUPLUS_N],r[NTRUPLUS_N],m[NTRUPLUS_N],c[NTRUPLUS_N];
    int16_t work[NTRUPLUS_N];
    uint8_t rb[NTRUPLUS_CIPHERTEXTBYTES],cb[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t ss[NTRUPLUS_SSBYTES];
} state;

static state states[2][BANKS];
static _Alignas(64) int16_t rin[BANKS][NTRUPLUS_N],min[BANKS][NTRUPLUS_N];
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t coins[BANKS][NTRUPLUS_N/8];
static uint64_t seed=UINT64_C(0x28a738c149e3);
static volatile uint64_t sink;
static uint32_t rnd(void) {
    seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return (uint32_t)seed;
}
static void forward(int16_t *out,int16_t *work,const int16_t *in) {
    ntruplus768_ntt_frontend_avx2(work,in);
    ntruplus768_ntt_m_avx2(out,work);
}
static void run(int variant,int region,int bank) {
    state *s=&states[variant][bank];
    if(region!=0) {
        if(ntruplus768_unpack_m_avx2(s->h,pk[bank])) abort();
        forward(s->r,s->work,rin[bank]);
        ntruplus768_pack_m_lazy10788_avx2(s->rb,s->r);
        forward(s->m,s->work,min[bank]);
    }
    if(variant) ntruplus768_exp001_encap_live_b3_pack(s->cb,s->h,s->r,s->m);
    else {
        ntruplus768_basemul_general_m_avx2(s->c,s->h,s->r);
        poly_add((poly *)(void *)s->c,(const poly *)(const void *)s->c,
                 (const poly *)(const void *)s->m);
        ntruplus768_pack_m_highrange12699_avx2(s->cb,s->c);
    }
    sink += s->cb[(bank+region)%NTRUPLUS_CIPHERTEXTBYTES];
}
int main(void) {
    for(int b=0;b<BANKS;b++) {
        int16_t h[NTRUPLUS_N];
        for(int i=0;i<NTRUPLUS_N;i++) {
            rin[b][i]=(int16_t)((int)(rnd()%3)-1);
            min[b][i]=(int16_t)((int)(rnd()%3)-1);
            h[i]=(int16_t)(rnd()%3457);
        }
        for(int i=0;i<NTRUPLUS_N;i+=2) {
            int a=h[i],c=h[i+1],k=3*i/2;
            pk[b][k]=(uint8_t)a;
            pk[b][k+1]=(uint8_t)((a>>8)|((c&15)<<4));
            pk[b][k+2]=(uint8_t)(c>>4);
        }
        for(size_t i=0;i<sizeof coins[b];i++) coins[b][i]=(uint8_t)rnd();
        for(int v=0;v<2;v++) {
            if(ntruplus768_unpack_m_avx2(states[v][b].h,pk[b])) abort();
            forward(states[v][b].r,states[v][b].work,rin[b]);
            forward(states[v][b].m,states[v][b].work,min[b]);
        }
        for(int v=0;v<2;v++) run(v,0,b);
        if(memcmp(states[0][b].cb,states[1][b].cb,sizeof states[0][b].cb)) abort();
        for(int v=0;v<2;v++) run(v,1,b);
        if(memcmp(states[0][b].cb,states[1][b].cb,sizeof states[0][b].cb) ||
           memcmp(states[0][b].rb,states[1][b].rb,sizeof states[0][b].rb)) abort();
    }
    fprintf(stderr,"preflight=pass cpucycles=%s\n",cpucycles_implementation());
    puts("region,variant,block,slot,cycles");
    for(int region=0;region<2;region++) for(int block=0;block<BLOCKS;block++) {
        const int order[4]={block&1?1:0,block&1?0:1,block&1?0:1,block&1?1:0};
        for(int slot=0;slot<4;slot++) {
            int variant=order[slot],bank=(block+slot)%BANKS;
            long long begin=cpucycles();
            run(variant,region,bank);
            long long end=cpucycles();
            printf("%d,%d,%d,%d,%lld\n",region,variant,block,slot,end-begin);
        }
    }
    return sink==UINT64_C(0xbadbeef)?1:0;
}
