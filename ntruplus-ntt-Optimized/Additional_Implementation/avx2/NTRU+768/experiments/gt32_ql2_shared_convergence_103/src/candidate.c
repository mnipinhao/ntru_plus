#include <stddef.h>
#include <stdint.h>
#include "candidate.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

typedef struct __attribute__((aligned(64))) {
  int16_t h[NTRUPLUS_N];
  int16_t r[NTRUPLUS_N];
  int16_t m[NTRUPLUS_N];
  int16_t c[NTRUPLUS_N];
} gt103_scratch;

static void forward_m(int16_t *out,int16_t *frontend,const int16_t *in)
{
  ntruplus768_ntt_frontend_avx2(frontend,in);
  ntruplus768_ntt_m_avx2(out,frontend);
}

static void forward_ql2(int16_t *out,int16_t *frontend,const int16_t *in)
{
  ntruplus768_ntt_frontend_avx2(frontend,in);
  gt103_ntt_ql2_avx2(out,frontend);
}

int gt103_encap_ql2(uint8_t *ct,uint8_t *ss,const uint8_t *pk,
                    const uint8_t *coins)
{
  uint8_t msg[HASH_H_INBYTES];
  uint8_t buf[HASH_H_OUTBYTES];
  gt103_scratch scratch;
  if(ntruplus768_unpack_m_avx2(scratch.h,pk)!=0){
    for(size_t i=0;i<NTRUPLUS_CIPHERTEXTBYTES;i++)ct[i]=0;
    secure_clear(ss,NTRUPLUS_SSBYTES);
    return 1;
  }
  for(size_t i=0;i<NTRUPLUS_N/8;i++)msg[i]=coins[i];
  hash_f(msg+NTRUPLUS_N/8,pk);
  hash_h(buf,msg);
  poly_cbd1((poly *)(void *)scratch.m,buf+NTRUPLUS_SYMBYTES);
  forward_m(scratch.r,scratch.c,scratch.m);
  ntruplus768_pack_m_lazy10788_avx2(ct,scratch.r);
  hash_g(ct,ct);
  poly_sotp_encode((poly *)(void *)scratch.m,msg,ct);
  forward_ql2(scratch.m,scratch.c,scratch.m);
  gt103_basemul_general_ql2_avx2(scratch.c,scratch.h,scratch.r);
  gt103_pack_ql2_sum_avx2(ct,scratch.c,scratch.m);
  for(size_t i=0;i<NTRUPLUS_SSBYTES;i++)ss[i]=buf[i];
  secure_clear(msg,sizeof msg);
  secure_clear(buf,sizeof buf);
  secure_clear(scratch.r,sizeof scratch.r);
  secure_clear(scratch.m,sizeof scratch.m);
  return 0;
}

typedef void (*ntt_core_fn)(int16_t *,const int16_t *);
typedef void (*b3_fn)(int16_t *,const int16_t *,const int16_t *);
typedef void (*pack_sum_fn)(uint8_t *,const int16_t *,const int16_t *);

/* Causal control: both modes execute the same caller bytes and indirect call
 * sites.  This is attribution-only; it is not a production ABI candidate. */
static __attribute__((noinline)) int encap_matched(
    uint8_t *ct,uint8_t *ss,const uint8_t *pk,const uint8_t *coins,
    ntt_core_fn ntt,b3_fn b3,pack_sum_fn pack)
{
  uint8_t msg[HASH_H_INBYTES],buf[HASH_H_OUTBYTES];
  gt103_scratch scratch;
  if(ntruplus768_unpack_m_avx2(scratch.h,pk)!=0){
    for(size_t i=0;i<NTRUPLUS_CIPHERTEXTBYTES;i++)ct[i]=0;
    secure_clear(ss,NTRUPLUS_SSBYTES);return 1;
  }
  for(size_t i=0;i<NTRUPLUS_N/8;i++)msg[i]=coins[i];
  hash_f(msg+NTRUPLUS_N/8,pk);hash_h(buf,msg);
  poly_cbd1((poly *)(void *)scratch.m,buf+NTRUPLUS_SYMBYTES);
  forward_m(scratch.r,scratch.c,scratch.m);
  ntruplus768_pack_m_lazy10788_avx2(ct,scratch.r);hash_g(ct,ct);
  poly_sotp_encode((poly *)(void *)scratch.m,msg,ct);
  ntruplus768_ntt_frontend_avx2(scratch.c,scratch.m);
  ntt(scratch.m,scratch.c);
  b3(scratch.c,scratch.h,scratch.r);
  pack(ct,scratch.c,scratch.m);
  for(size_t i=0;i<NTRUPLUS_SSBYTES;i++)ss[i]=buf[i];
  secure_clear(msg,sizeof msg);secure_clear(buf,sizeof buf);
  secure_clear(scratch.r,sizeof scratch.r);secure_clear(scratch.m,sizeof scratch.m);
  return 0;
}

int gt103_encap_matched_control(uint8_t *ct,uint8_t *ss,const uint8_t *pk,const uint8_t *coins)
{return encap_matched(ct,ss,pk,coins,ntruplus768_ntt_m_avx2,ntruplus768_basemul_general_m_avx2,ntruplus768_pack_m_sum_highrange12699_avx2);}
int gt103_encap_matched_candidate(uint8_t *ct,uint8_t *ss,const uint8_t *pk,const uint8_t *coins)
{return encap_matched(ct,ss,pk,coins,gt103_ntt_ql2_avx2,gt103_basemul_general_ql2_avx2,gt103_pack_ql2_sum_avx2);}
