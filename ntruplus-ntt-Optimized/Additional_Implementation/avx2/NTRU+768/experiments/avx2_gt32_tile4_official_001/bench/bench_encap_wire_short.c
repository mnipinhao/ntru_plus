#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "cpucycles.h"
#include "poly.h"

enum { N=768, Q=3457, BYTES=1152, BANKS=16, REPS=32 };
void ntruplus768_ntt_frontend_avx2(int16_t *,const int16_t *);
void ntruplus768_ntt_m_avx2(int16_t *,const int16_t *);
void ntruplus768_wire_research_forward(int16_t *,const int16_t *);
int ntruplus768_unpack_m_avx2(int16_t *,const uint8_t *);
int ntruplus768_wire_research_decode(int16_t *,const uint8_t *);
void ntruplus768_pack_m_lazy10788_avx2(uint8_t *,const int16_t *);
void ntruplus768_wire_research_pack(uint8_t *,const int16_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *,const int16_t *,const int16_t *);
void ntruplus768_wire_research_muladd_1(int16_t *,const int16_t *,const int16_t *,const int16_t *);
void ntruplus768_wire_research_muladd_2(int16_t *,const int16_t *,const int16_t *,const int16_t *);
void ntruplus768_wire_research_control_basemul_general_m_avx2(int16_t *,
    const int16_t *,const int16_t *,const int16_t *);

typedef struct __attribute__((aligned(64))) {
    int16_t h[N],r[N],m[N],c[N],work[N];
    uint8_t rb[BYTES],cb[BYTES];
} state;
static state states[4][BANKS];
static _Alignas(64) int16_t r_input[BANKS][N],m_input[BANKS][N];
static _Alignas(64) uint8_t pk[BANKS][BYTES];
static volatile uint64_t sink;
static uint64_t seed=UINT64_C(0x5a91b76812f0);
static uint32_t rnd(void) { seed^=seed<<13;seed^=seed>>7;seed^=seed<<17;return (uint32_t)seed; }

static int operation(int variant,int region,int bank) {
    state *s=&states[variant][bank];
    const int16_t *r=r_input[bank],*m=m_input[bank];
    if(region==0 || region==2) {
        ntruplus768_ntt_frontend_avx2(s->work,r);
        if(variant==0 || variant==3) ntruplus768_ntt_m_avx2(s->r,s->work);
        else ntruplus768_wire_research_forward(s->r,s->work);
    }
    if(region==1 || region==2) {
        ntruplus768_ntt_frontend_avx2(s->work,m);
        if(variant==0 || variant==3) ntruplus768_ntt_m_avx2(s->m,s->work);
        else ntruplus768_wire_research_forward(s->m,s->work);
    }
    if(region==3) {
        ntruplus768_ntt_frontend_avx2(s->work,r);
        if(variant==0 || variant==3) { ntruplus768_ntt_m_avx2(s->r,s->work);
                        ntruplus768_pack_m_lazy10788_avx2(s->rb,s->r); }
        else { ntruplus768_wire_research_forward(s->r,s->work);
               ntruplus768_wire_research_pack(s->rb,s->r); }
    }
    if(region==4) {
        if(variant==0 || variant==3) {
            if(ntruplus768_unpack_m_avx2(s->h,pk[bank])) return 1;
            ntruplus768_ntt_frontend_avx2(s->work,r);
            ntruplus768_ntt_m_avx2(s->r,s->work);
            ntruplus768_pack_m_lazy10788_avx2(s->rb,s->r);
            ntruplus768_ntt_frontend_avx2(s->work,m);
            ntruplus768_ntt_m_avx2(s->m,s->work);
            if(variant==3)
                ntruplus768_wire_research_control_basemul_general_m_avx2(
                    s->c,s->h,s->r,s->m);
            else {
                ntruplus768_basemul_general_m_avx2(s->c,s->h,s->r);
                poly_add((poly *)(void *)s->c,(const poly *)(const void *)s->c,
                         (const poly *)(const void *)s->m);
            }
            ntruplus768_pack_m_lazy10788_avx2(s->cb,s->c);
        } else {
            if(ntruplus768_wire_research_decode(s->h,pk[bank])) return 1;
            ntruplus768_ntt_frontend_avx2(s->work,r);
            ntruplus768_wire_research_forward(s->r,s->work);
            ntruplus768_wire_research_pack(s->rb,s->r);
            ntruplus768_ntt_frontend_avx2(s->work,m);
            ntruplus768_wire_research_forward(s->m,s->work);
            if(variant==1) ntruplus768_wire_research_muladd_1(s->c,s->h,s->r,s->m);
            else ntruplus768_wire_research_muladd_2(s->c,s->h,s->r,s->m);
            ntruplus768_wire_research_pack(s->cb,s->c);
        }
    }
    return 0;
}

int main(void) {
    for(int b=0;b<BANKS;b++) {
        int16_t h[N];
        for(int i=0;i<N;i++) {
            r_input[b][i]=(int16_t)((int)(rnd()%3)-1);
            m_input[b][i]=(int16_t)((int)(rnd()%3)-1);
            h[i]=(int16_t)(rnd()%Q);
        }
        for(int i=0;i<N;i+=2) {
            int a=h[i],c=h[i+1],k=3*i/2;
            pk[b][k]=(uint8_t)a; pk[b][k+1]=(uint8_t)((a>>8)|((c&15)<<4));
            pk[b][k+2]=(uint8_t)(c>>4);
        }
    }
    for(int b=0;b<BANKS;b++) {
        for(int v=0;v<4;v++) if(operation(v,4,b)) abort();
        if(memcmp(states[0][b].rb,states[1][b].rb,BYTES) ||
           memcmp(states[0][b].cb,states[1][b].cb,BYTES) ||
           memcmp(states[0][b].rb,states[2][b].rb,BYTES) ||
           memcmp(states[0][b].cb,states[2][b].cb,BYTES) ||
           memcmp(states[0][b].rb,states[3][b].rb,BYTES) ||
           memcmp(states[0][b].cb,states[3][b].cb,BYTES)) abort();
    }
    fprintf(stderr,"preflight=pass cpucycles=%s\n",cpucycles_implementation());
    puts("region,variant,block,slot,cycles");
    for(int region=0;region<5;region++) {
        for(int block=0;block<REPS;block++) {
            int order[8]={0,1,2,3,3,2,1,0};
            if(block&1) { int reversed[8]={3,2,1,0,0,1,2,3};memcpy(order,reversed,sizeof order); }
            for(int slot=0;slot<8;slot++) {
                int v=order[slot],bank=(block+slot)%BANKS;
                long long begin=cpucycles();
                int rc=operation(v,region,bank);
                long long end=cpucycles();
                if(rc) abort();
                sink+=(uint16_t)states[v][bank].r[0]+states[v][bank].rb[0];
                printf("%d,%d,%d,%d,%lld\n",region,v,block,slot,end-begin);
            }
        }
    }
    return sink==UINT64_C(0xdeadbeef)?1:0;
}
