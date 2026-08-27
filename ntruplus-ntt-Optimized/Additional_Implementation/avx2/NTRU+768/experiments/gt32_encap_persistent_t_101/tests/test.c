#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "candidate.h"
#include "internal.h"

static uint64_t state=UINT64_C(0x101c0ffee1234567);
static uint32_t rnd(void){state^=state<<13;state^=state>>7;state^=state<<17;return (uint32_t)state;}

static void t_to_m(int16_t *out,const int16_t *in)
{
  const __m256i mask=_mm256_setr_epi8(0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15,
                                      0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15);
  for(int g=0;g<12;g++){
    const __m256i *p=(const __m256i *)(const void *)(in+64*g);
    __m256i a=_mm256_shuffle_epi8(_mm256_loadu_si256(p+0),mask);
    __m256i b=_mm256_shuffle_epi8(_mm256_loadu_si256(p+1),mask);
    __m256i c=_mm256_shuffle_epi8(_mm256_loadu_si256(p+2),mask);
    __m256i d=_mm256_shuffle_epi8(_mm256_loadu_si256(p+3),mask);
    __m256i x0=_mm256_unpacklo_epi32(a,c),x1=_mm256_unpackhi_epi32(a,c);
    __m256i x2=_mm256_unpacklo_epi32(b,d),x3=_mm256_unpackhi_epi32(b,d);
    __m256i *q=(__m256i *)(void *)(out+64*g);
    _mm256_storeu_si256(q+0,_mm256_unpacklo_epi64(x0,x2));
    _mm256_storeu_si256(q+1,_mm256_unpackhi_epi64(x0,x2));
    _mm256_storeu_si256(q+2,_mm256_unpacklo_epi64(x1,x3));
    _mm256_storeu_si256(q+3,_mm256_unpackhi_epi64(x1,x3));
  }
}

static int one(const int16_t *a,const int16_t *b)
{
  _Alignas(64) int16_t f[768],m[768],t[768],tm[768],hm[768],p0[768],p1[768];
  _Alignas(64) uint8_t w0[1152],w1[1152];
  ntruplus768_ntt_frontend_avx2(f,a); ntruplus768_ntt_m_avx2(m,f);
  gt101_ntt_t_avx2(t,f); t_to_m(tm,t);
  if(memcmp(m,tm,sizeof m)) return 1;
  ntruplus768_pack_m_lazy10788_avx2(w0,m); gt101_pack_t_avx2(w1,t);
  if(memcmp(w0,w1,sizeof w0)) {
    for(int i=0,n=0;i<1152&&n<12;i++)if(w0[i]!=w1[i]){printf("wire[%d]=%u/%u ",i,w0[i],w1[i]);n++;}
    putchar('\n'); return 2;
  }
  ntruplus768_ntt_frontend_avx2(f,b); ntruplus768_ntt_m_avx2(hm,f);
  ntruplus768_basemul_general_m_avx2(p0,hm,m);
  gt101_basemul_general_m_t_avx2(p1,hm,t);
  if(memcmp(p0,p1,sizeof p0)) return 3;
  return 0;
}

int main(void)
{
  _Alignas(64) int16_t a[768],b[768];
  memset(a,0,sizeof a);memset(b,0,sizeof b);b[0]=1;
  for(int i=0;i<768;i++){memset(a,0,sizeof a);a[i]=1;int r=one(a,b);if(r){printf("impulse %d edge %d\n",i,r);return 1;}}
  for(int k=0;k<1000;k++){
    for(int i=0;i<768;i++){a[i]=(int16_t)((int)(rnd()%3457)-1728);b[i]=(int16_t)((int)(rnd()%3457)-1728);}
    int r=one(a,b);if(r){printf("random %d edge %d\n",k,r);return 1;}
  }
  uint8_t pk[1152]={0},coins[96],c0[1152],c1[1152],s0[32],s1[32];
  for(int k=0;k<1000;k++){
    for(size_t i=0;i<sizeof pk;i++)pk[i]=(uint8_t)rnd();
    /* Canonical pairs, encoded directly. */
    for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;pk[3*i]=x;pk[3*i+1]=(uint8_t)((x>>8)|(y<<4));pk[3*i+2]=(uint8_t)(y>>4);}
    for(size_t i=0;i<sizeof coins;i++)coins[i]=(uint8_t)rnd();
    int r0=ntruplus768_enc_derand_impl(c0,s0,pk,coins),r1=gt101_encap_t(c1,s1,pk,coins);
    if(r0!=r1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0)){printf("encap %d\n",k);return 1;}
  }
  memset(pk,0,sizeof pk);pk[0]=0x81;pk[1]=0x0d;
  int r0=ntruplus768_enc_derand_impl(c0,s0,pk,coins),r1=gt101_encap_t(c1,s1,pk,coins);
  if(r0!=1||r1!=1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0))return 1;
  puts("PASS impulses=768 random=1000 encap=1000 noncanonical=1 raw_M/WIRE12/product exact");
  return 0;
}
