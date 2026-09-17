#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "candidate.h"
#include "internal.h"
#include "symmetric.h"

static uint64_t state = UINT64_C(0x142d1eec7c0ffee1);
static uint32_t rnd(void){state^=state<<13;state^=state>>7;state^=state<<17;return (uint32_t)state;}
static void pairpk(uint8_t *p){for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;p[3*i]=(uint8_t)x;p[3*i+1]=(uint8_t)((x>>8)|(y<<4));p[3*i+2]=(uint8_t)(y>>4);}}

int main(void)
{
    _Alignas(64) int16_t coeff[768], front[768], m[768];
    uint8_t wire[1152], h0[192], h1[192];
    for(int k=0;k<1000;k++){
        for(int i=0;i<768;i++) coeff[i]=(int16_t)((int)(rnd()%3457)-1728);
        ntruplus768_ntt_frontend_avx2(front,coeff);
        ntruplus768_ntt_m_avx2(m,front);
        ntruplus768_pack_m_lazy10788_avx2(wire,m);
        hash_g(h0,wire);
        gt142_hash_g_from_m(h1,m);
        if(memcmp(h0,h1,sizeof h0)){printf("hash mismatch %d\n",k);return 1;}
    }
    uint8_t pk[1152],coins[96],c0[1152],c1[1152],s0[32],s1[32];
    for(int k=0;k<1000;k++){
        pairpk(pk);for(size_t i=0;i<sizeof coins;i++)coins[i]=(uint8_t)rnd();
        int r0=ntruplus768_enc_derand_impl(c0,s0,pk,coins);
        int r1=gt142_enc_derand(c1,s1,pk,coins);
        if(r0!=r1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0)){printf("encap mismatch %d\n",k);return 1;}
    }
    memset(pk,0,sizeof pk);pk[0]=0x81;pk[1]=0x0d;
    int r0=ntruplus768_enc_derand_impl(c0,s0,pk,coins);
    int r1=gt142_enc_derand(c1,s1,pk,coins);
    if(r0!=1||r1!=1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0))return 1;
    puts("PASS hash=1000 encap=1000 noncanonical=1 byte-exact");
    return 0;
}
