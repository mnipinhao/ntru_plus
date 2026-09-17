#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "poly.h"
#include "gt9x16_forward.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = {"bytes", "words", 0};
const long long sizes[] = {NTRUPLUS_POLYBYTES, NTRUPLUS_N};

#define TIMINGS 32
#define BANKS (TIMINGS + 1)
#define PREFIX "wire_monotone_shared_abi_"

void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(int16_t *);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t *);
void ntruplus1152_exp001_direct_serializer_natural(uint8_t *, const int16_t *);
void ntruplus1152_exp001_direct_serializer_wire(uint8_t *, const int16_t *);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress(uint8_t *, const uint8_t *, const int16_t *, const int16_t *, int16_t *);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(uint8_t *, const uint8_t *, const int16_t *, const int16_t *, int16_t *);

static uint8_t *pk, *ct[2], *hash_bytes[2];
static poly *encoded_h, *r_coeff, *m_coeff;
static int16_t *r_work[2], *m_work[2], *scratch[2];
static long long cycles[TIMINGS + 1];
static volatile unsigned int sink;
void preallocate(void) {}
void allocate(void) {
  int v;
  pk=(uint8_t*)alignedcalloc(BANKS*NTRUPLUS_POLYBYTES);
  encoded_h=(poly*)alignedcalloc(BANKS*sizeof *encoded_h);
  r_coeff=(poly*)alignedcalloc(BANKS*sizeof *r_coeff);
  m_coeff=(poly*)alignedcalloc(BANKS*sizeof *m_coeff);
  for(v=0;v<2;++v){ct[v]=(uint8_t*)alignedcalloc(BANKS*NTRUPLUS_POLYBYTES);hash_bytes[v]=(uint8_t*)alignedcalloc(BANKS*NTRUPLUS_POLYBYTES);r_work[v]=(int16_t*)alignedcalloc(BANKS*NTRUPLUS_N*sizeof(int16_t));m_work[v]=(int16_t*)alignedcalloc(BANKS*NTRUPLUS_N*sizeof(int16_t));scratch[v]=(int16_t*)alignedcalloc(BANKS*NTRUPLUS_N*sizeof(int16_t));}
}
#define WS(base,i) ((base)+(i)*NTRUPLUS_N)
#define BS(base,i) ((base)+(i)*NTRUPLUS_POLYBYTES)
static void reset_inputs(void){int b,j;for(b=0;b<BANKS;++b){for(j=0;j<NTRUPLUS_N;++j){encoded_h[b].coeffs[j]=(int16_t)(((unsigned)j*619U+(unsigned)b*37U+11U)%3457U);r_coeff[b].coeffs[j]=(int16_t)((int)(((unsigned)j*43U+(unsigned)b*19U)%3U)-1);m_coeff[b].coeffs[j]=(int16_t)((int)(((unsigned)j*71U+(unsigned)b*23U)%3U)-1);}poly_tobytes(BS(pk,b),encoded_h+b);}}
static int run_variant(int v,int b){int16_t *r=WS(r_work[v],b),*m=WS(m_work[v],b);ntruplus1152_exp001_top_split_small(r,r_coeff[b].coeffs);ntruplus1152_exp001_top_split_small(m,m_coeff[b].coeffs);if(v==0){ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(r);ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(m);ntruplus1152_exp001_direct_serializer_natural(BS(hash_bytes[v],b),r);return ntruplus1152_exp001_encap_h4_m3b_exact_egress(BS(ct[v],b),BS(pk,b),r,m,WS(scratch[v],b));}ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(r);ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(m);ntruplus1152_exp001_direct_serializer_wire(BS(hash_bytes[v],b),r);return ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(BS(ct[v],b),BS(pk,b),r,m,WS(scratch[v],b));}
static int __attribute__((noinline,aligned(32))) control(int b){return run_variant(0,b);}
static int __attribute__((noinline,aligned(32))) candidate(int b){return run_variant(1,b);}
static void preflight(void){poly h,r,m,c;uint8_t expected_ct[NTRUPLUS_POLYBYTES],expected_hash[NTRUPLUS_POLYBYTES];int cr,wr;reset_inputs();if(poly_frombytes(&h,pk)){fputs("wire preflight: Official PK reject\n",stderr);abort();}r=r_coeff[0];m=m_coeff[0];poly_ntt(&r);poly_ntt(&m);poly_tobytes(expected_hash,&r);poly_basemul(&c,&h,&r);poly_add(&c,&c,&m);poly_tobytes(expected_ct,&c);cr=control(0);wr=candidate(0);if(cr||wr||memcmp(ct[0],expected_ct,NTRUPLUS_POLYBYTES)||memcmp(ct[1],expected_ct,NTRUPLUS_POLYBYTES)||memcmp(hash_bytes[0],expected_hash,NTRUPLUS_POLYBYTES)||memcmp(hash_bytes[1],expected_hash,NTRUPLUS_POLYBYTES)){fprintf(stderr,"wire preflight: cr=%d wr=%d ct0=%d ct1=%d hash0=%d hash1=%d\n",cr,wr,memcmp(ct[0],expected_ct,NTRUPLUS_POLYBYTES),memcmp(ct[1],expected_ct,NTRUPLUS_POLYBYTES),memcmp(hash_bytes[0],expected_hash,NTRUPLUS_POLYBYTES),memcmp(hash_bytes[1],expected_hash,NTRUPLUS_POLYBYTES));abort();}}
#define ENTRY(v,p) do{for(i=0;i<=TIMINGS;++i){cycles[i]=cpucycles();sink|=(unsigned)(v?candidate(i):control(i));}for(i=0;i<TIMINGS;++i)cycles[i]=cycles[i+1]-cycles[i];{char label[96];snprintf(label,sizeof label,PREFIX "%s_pos%d_cycles",v?"candidate":"control",p);printentry(-1,label,cycles,TIMINGS);}}while(0)
void measure(void){static const int order[2][4]={{0,1,1,0},{1,0,0,1}};int i,l,r,p;preflight();printf("wire_monotone_shared_abi_runtime_addresses %p %p\n",(void*)control,(void*)candidate);for(l=0;l<LOOPS;++l)for(r=0;r<2;++r){reset_inputs();for(p=0;p<4;++p)ENTRY(order[r][p],p);}}
