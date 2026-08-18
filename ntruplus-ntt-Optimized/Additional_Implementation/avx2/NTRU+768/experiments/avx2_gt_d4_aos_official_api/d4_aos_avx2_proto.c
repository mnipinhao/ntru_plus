#include "d4_aos_avx2_proto.h"
#include <immintrin.h>
#include <string.h>

enum { Q=3457, R=3310, QINV=-12929, ROWS=96, VECS=48 };
static __m256i fw[VECS][ROWS], iv[ROWS][VECS], zeta[VECS];
static __m256i pick[4], lane_mask[4];
static int ready;
static int modq(int64_t x){ x%=Q; return (int)(x<0?x+Q:x); }
static int power(int a,int e){int r=1;while(e){if(e&1)r=modq((int64_t)r*a);a=modq((int64_t)a*a);e>>=1;}return r;}
static int mont(int a){int x=modq((int64_t)a*R);return x>Q/2?x-Q:x;}
static int k_of(int k3,int k32){return (32*k3+3*k32)%ROWS;}
static __m256i canon(__m256i x){
 const __m256i q=_mm256_set1_epi16(Q), z=_mm256_setzero_si256();
 x=_mm256_add_epi16(x,_mm256_and_si256(_mm256_cmpgt_epi16(z,x),q));
 x=_mm256_sub_epi16(x,_mm256_and_si256(_mm256_cmpgt_epi16(x,_mm256_set1_epi16(Q-1)),q));
 return x;
}
/* Montgomery reduction of 16 signed 16-bit products, with b in R-domain. */
static __m256i mmul(__m256i a,__m256i b){
 const __m256i qi=_mm256_set1_epi16(QINV),q=_mm256_set1_epi16(Q),one=_mm256_set1_epi16(1),z=_mm256_setzero_si256();
 __m256i pl=_mm256_mullo_epi16(a,b),ph=_mm256_mulhi_epi16(a,b);
 __m256i t=_mm256_mullo_epi16(pl,qi),tl=_mm256_mullo_epi16(t,q),th=_mm256_mulhi_epi16(t,q);
 (void)tl;
 return canon(_mm256_add_epi16(_mm256_add_epi16(ph,th),_mm256_andnot_si256(_mm256_cmpeq_epi16(pl,z),one)));
}
static __m256i addq(__m256i a,__m256i b){return canon(_mm256_add_epi16(a,b));}
static __m256i subq(__m256i a,__m256i b){return canon(_mm256_sub_epi16(a,b));}
static void init(void){
 if(ready)return;
 for(int i=0;i<4;i++){
  int8_t p[32]; int16_t m[16];
  for(int l=0;l<32;l++)p[l]=(int8_t)(8*((l&15)/8)+2*i+(l&1));
  for(int l=0;l<16;l++)m[l]=((l&3)==i)?-1:0;
  pick[i]=_mm256_loadu_si256((const __m256i*)p); lane_mask[i]=_mm256_loadu_si256((const __m256i*)m);
 }
 for(int k3=0;k3<3;k3++)for(int pair=0;pair<16;pair++){
  int v=16*k3+pair; int16_t zm[16];
  for(int i=0;i<ROWS;i++){int16_t a[16],b[16];for(int br=0;br<2;br++)for(int u=0;u<2;u++)for(int c=0;c<4;c++){int k=k_of(k3,2*pair+u),g=modq((int64_t)(br?2:22)*power(641,k));a[8*br+4*u+c]=(int16_t)mont(power(g,i));b[8*br+4*u+c]=(int16_t)mont(power(g,Q-1-i));}fw[v][i]=_mm256_loadu_si256((const __m256i*)a);iv[i][v]=_mm256_loadu_si256((const __m256i*)b);}
  for(int br=0;br<2;br++)for(int u=0;u<2;u++)for(int c=0;c<4;c++){int k=k_of(k3,2*pair+u);zm[8*br+4*u+c]=(int16_t)mont(modq((int64_t)(br?2:22)*power(641,k)));}
  zeta[v]=_mm256_loadu_si256((const __m256i*)zm);
 }
 ready=1;
}
void gt_d4aos_ntt_avx2_proto(d4aos_ntt_poly *out,const d4aos_coeff_poly *in){
 const __m256i alpha0=_mm256_set1_epi16((int16_t)mont(2735)),alpha1=_mm256_set1_epi16((int16_t)mont(723)); init();
 for(int v=0;v<VECS;v++){__m256i acc=_mm256_setzero_si256();for(int i=0;i<ROWS;i++){__m128i a=_mm_loadl_epi64((const __m128i*)&in->coeff[4*i]),b=_mm_loadl_epi64((const __m128i*)&in->coeff[384+4*i]);__m256i aa=_mm256_broadcastq_epi64(a),bb=_mm256_broadcastq_epi64(b),u0=addq(aa,mmul(bb,alpha0)),u1=addq(aa,mmul(bb,alpha1));__m256i t0=mmul(u0,fw[v][i]),t1=mmul(u1,fw[v][i]);acc=addq(acc,_mm256_permute2x128_si256(t0,t1,0x30));}_mm256_store_si256((__m256i*)&out->lane[16*v],acc);}
}
void gt_d4aos_basemul_avx2_proto(d4aos_ntt_poly *out,const d4aos_ntt_poly *a,const d4aos_ntt_poly *b){
 init();for(int v=0;v<VECS;v++){__m256i x=_mm256_load_si256((const __m256i*)&a->lane[16*v]),y=_mm256_load_si256((const __m256i*)&b->lane[16*v]),yr=mmul(y,_mm256_set1_epi16((int16_t)modq((int64_t)R*R))),acc=_mm256_setzero_si256();for(int i=0;i<4;i++)for(int j=0;j<4;j++){__m256i p=mmul(_mm256_shuffle_epi8(x,pick[i]),_mm256_shuffle_epi8(yr,pick[j]));if(i+j>=4)p=mmul(p,zeta[v]);acc=addq(acc,_mm256_and_si256(p,lane_mask[(i+j)&3]));}_mm256_store_si256((__m256i*)&out->lane[16*v],acc);}}
void gt_d4aos_invntt_avx2_proto(d4aos_coeff_poly *out,const d4aos_ntt_poly *in){
 const __m256i inv96=_mm256_set1_epi16((int16_t)mont(3421)),dinv=_mm256_set1_epi16((int16_t)mont(power(modq(2735-723),Q-2))),alpha=_mm256_set1_epi16((int16_t)mont(2735));init();
 for(int i=0;i<ROWS;i++){__m256i acc=_mm256_setzero_si256();for(int v=0;v<VECS;v++)acc=addq(acc,mmul(_mm256_load_si256((const __m256i*)&in->lane[16*v]),iv[i][v]));acc=mmul(acc,inv96);__m256i sw=_mm256_permute4x64_epi64(acc,_MM_SHUFFLE(2,3,0,1));acc=addq(acc,sw);__m128i b0=_mm256_castsi256_si128(acc),b1=_mm256_extracti128_si256(acc,1);__m256i u0=_mm256_broadcastsi128_si256(b0),u1=_mm256_broadcastsi128_si256(b1),hi=mmul(subq(u0,u1),dinv),lo=subq(u0,mmul(hi,alpha));__m128i l=_mm256_castsi256_si128(lo),h=_mm256_castsi256_si128(hi);_mm_storel_epi64((__m128i*)&out->coeff[4*i],l);_mm_storel_epi64((__m128i*)&out->coeff[384+4*i],h);}
}
