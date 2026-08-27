#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "candidate.h"
#include "internal.h"
#include "poly.h"

static uint64_t state=UINT64_C(0x103c0ffee1234567);
static uint32_t rnd(void){state^=state<<13;state^=state>>7;state^=state<<17;return (uint32_t)state;}

static void m_to_ql2(int16_t *out,const int16_t *in)
{
  for(int g=0;g<12;g++){
    const __m256i *p=(const __m256i *)(const void *)(in+64*g);
    __m256i a=_mm256_loadu_si256(p+0),b=_mm256_loadu_si256(p+1);
    __m256i c=_mm256_loadu_si256(p+2),d=_mm256_loadu_si256(p+3);
    __m256i w0=_mm256_unpacklo_epi16(a,b),w1=_mm256_unpackhi_epi16(a,b);
    __m256i w2=_mm256_unpacklo_epi16(c,d),w3=_mm256_unpackhi_epi16(c,d);
    __m256i *q=(__m256i *)(void *)(out+64*g);
    _mm256_storeu_si256(q+0,_mm256_unpacklo_epi32(w0,w2));
    _mm256_storeu_si256(q+1,_mm256_unpackhi_epi32(w0,w2));
    _mm256_storeu_si256(q+2,_mm256_unpacklo_epi32(w1,w3));
    _mm256_storeu_si256(q+3,_mm256_unpackhi_epi32(w1,w3));
  }
}

static int edges(const int16_t *a,const int16_t *b)
{
  _Alignas(64) int16_t fa[768],fb[768],ma[768],mb[768],qa[768],qb[768],ref[768],p0[768],p1[768];
  _Alignas(64) uint8_t w0[1152],w1[1152];
  ntruplus768_ntt_frontend_avx2(fa,a);ntruplus768_ntt_m_avx2(ma,fa);gt103_ntt_ql2_avx2(qa,fa);
  m_to_ql2(ref,ma);if(memcmp(ref,qa,sizeof ref))return 1;
  ntruplus768_ntt_frontend_avx2(fb,b);ntruplus768_ntt_m_avx2(mb,fb);gt103_ntt_ql2_avx2(qb,fb);
  ntruplus768_basemul_general_m_avx2(p0,ma,mb);gt103_basemul_general_ql2_avx2(p1,ma,mb);
  m_to_ql2(ref,p0);if(memcmp(ref,p1,sizeof ref))return 2;
  ntruplus768_pack_m_sum_highrange12699_avx2(w0,p0,ma);
  gt103_pack_ql2_sum_avx2(w1,p1,qa);if(memcmp(w0,w1,sizeof w0)){
    for(int i=0,n=0;i<1152&&n<12;i++)if(w0[i]!=w1[i]){printf("wire[%d]=%u/%u ",i,w0[i],w1[i]);n++;}
    putchar('\n');return 3;
  }
  return 0;
}

static void pairpk(uint8_t *p)
{for(int i=0;i<384;i++){uint16_t x=rnd()%3457,y=rnd()%3457;p[3*i]=x;p[3*i+1]=(uint8_t)((x>>8)|(y<<4));p[3*i+2]=(uint8_t)(y>>4);}}

int main(void)
{
  _Alignas(64) int16_t a[768],b[768];
  memset(b,0,sizeof b);b[0]=1;
  for(int i=0;i<768;i++){memset(a,0,sizeof a);a[i]=1;int e=edges(a,b);if(e){printf("impulse=%d edge=%d\n",i,e);return 1;}}
  for(int pattern=0;pattern<4;pattern++){
    for(int i=0;i<768;i++){
      a[i]=(pattern==0)?1728:(pattern==1)?-1728:(pattern==2)?((i&1)?1728:-1728):(int16_t)(i%3457-1728);
      b[i]=(pattern==3)?(int16_t)(1728-i%3457):a[i];
    }
    int e=edges(a,b);if(e){printf("pattern=%d edge=%d\n",pattern,e);return 1;}
  }
  for(int k=0;k<1000;k++){
    for(int i=0;i<768;i++){a[i]=(int16_t)((int)(rnd()%3457)-1728);b[i]=(int16_t)((int)(rnd()%3457)-1728);}
    int e=edges(a,b);if(e){printf("random=%d edge=%d\n",k,e);return 1;}
  }
  uint8_t pk[1152],coins[96],c0[1152],c1[1152],s0[32],s1[32];
  for(int k=0;k<1000;k++){
    pairpk(pk);for(size_t i=0;i<sizeof coins;i++)coins[i]=(uint8_t)rnd();
    int r0=ntruplus768_enc_derand_impl(c0,s0,pk,coins),r1=gt103_encap_ql2(c1,s1,pk,coins);
    if(r0!=r1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0)){printf("encap=%d\n",k);return 1;}
    r0=gt103_encap_matched_control(c0,s0,pk,coins);r1=gt103_encap_matched_candidate(c1,s1,pk,coins);
    if(r0!=r1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0)){printf("matched=%d\n",k);return 1;}
  }
  memset(pk,0,sizeof pk);pk[0]=0x81;pk[1]=0x0d;
  int r0=ntruplus768_enc_derand_impl(c0,s0,pk,coins),r1=gt103_encap_ql2(c1,s1,pk,coins);
  if(r0!=1||r1!=1||memcmp(c0,c1,sizeof c0)||memcmp(s0,s1,sizeof s0))return 1;
  puts("PASS impulses=768 patterns=4 random=1000 encap=1000 noncanonical=1 Forward/B3/QL2-add-Q24 exact");
  return 0;
}
