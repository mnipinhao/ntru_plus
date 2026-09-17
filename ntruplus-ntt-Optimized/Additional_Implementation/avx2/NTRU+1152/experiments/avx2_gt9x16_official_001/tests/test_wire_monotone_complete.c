#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "poly.h"

#define N 1152
#define BYTES 1728
#define Q 3457
void ntruplus1152_exp001_top_split_small(int16_t out[N], const int16_t in[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(int16_t state[N]);
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t state[N]);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress(uint8_t out[BYTES], const uint8_t pk[BYTES], const int16_t r[N], const int16_t m[N], int16_t scratch[N]);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(uint8_t out[BYTES], const uint8_t pk[BYTES], const int16_t r[N], const int16_t m[N], int16_t scratch[N]);
static uint64_t state = UINT64_C(0x57495245454e4335);
static uint32_t rnd(void) { state ^= state << 13; state ^= state >> 7; state ^= state << 17; return (uint32_t)(state >> 16); }
static void encode12(uint8_t out[BYTES], const uint16_t in[N]) {
  int i; memset(out, 0, BYTES);
  for (i = 0; i < N; ++i) { unsigned bit=12U*i, byte=bit>>3, shift=bit&7U; uint32_t x=(uint32_t)in[i]<<shift;
    out[byte]|=(uint8_t)x; if(byte+1<BYTES)out[byte+1]|=(uint8_t)(x>>8); if(byte+2<BYTES)out[byte+2]|=(uint8_t)(x>>16); }
}
int main(void) {
  _Alignas(32) int16_t rc[N],mc[N],rn[N],mn[N],rw[N],mw[N],sn[N],sw[N];
  _Alignas(32) uint16_t h[N];
  _Alignas(32) uint8_t pk[BYTES],a[BYTES],b[BYTES],expected[BYTES];
  poly hp,rp,mp,cp; int trial,i;
  for(trial=0;trial<120;++trial){
    for(i=0;i<N;++i){rc[i]=(int16_t)((int)(rnd()%3)-1);mc[i]=(int16_t)((int)(rnd()%3)-1);h[i]=(uint16_t)(rnd()%Q);}
    encode12(pk,h); ntruplus1152_exp001_top_split_small(rn,rc);memcpy(rw,rn,sizeof rn);ntruplus1152_exp001_top_split_small(mn,mc);memcpy(mw,mn,sizeof mn);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(rn);ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1_lazy_reduce(mn);
    ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(rw);ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(mw);
    if(ntruplus1152_exp001_encap_h4_m3b_exact_egress(a,pk,rn,mn,sn)||ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(b,pk,rw,mw,sw)||memcmp(a,b,BYTES)){fprintf(stderr,"wire complete mismatch trial=%d\n",trial);return 1;}
    if(poly_frombytes(&hp,pk)){return 1;} memcpy(rp.coeffs,rc,sizeof rc);memcpy(mp.coeffs,mc,sizeof mc);poly_ntt(&rp);poly_ntt(&mp);poly_basemul(&cp,&hp,&rp);poly_add(&cp,&cp,&mp);poly_tobytes(expected,&cp);
    if(memcmp(a,expected,BYTES)){fprintf(stderr,"Official mismatch trial=%d\n",trial);return 1;}
  }
  memset(pk,0xff,sizeof pk); if(!ntruplus1152_exp001_encap_h4_m3b_exact_egress(a,pk,rn,mn,sn)||!ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(b,pk,rw,mw,sw)){fputs("invalid PK accepted\n",stderr);return 1;}
  puts("wire-monotone complete island: ok"); return 0;
}
