/* P115: can the GT inverse consume Official's fused decode+basemul product, given only a fixed relayout? */
#include <stdio.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
#include "test/reference/poly_reference.h"
int main(void){
  static uint8_t bytes[NTRUPLUS_POLYBYTES], ct[NTRUPLUS_POLYBYTES], fb[NTRUPLUS_POLYBYTES];
  poly t,q,g; int map[NTRUPLUS_N]; /* map[gt_pos] = qsoa_pos */
  for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(int16_t)(i+1);
  poly_tobytes_encap(bytes,&t);           /* canonical bytes whose GT decode is t */
  if(poly_frombytes_decap(&q,bytes)){puts("decap decode fail");return 1;}
  int inv[NTRUPLUS_N+2]; for(int i=0;i<NTRUPLUS_N+2;i++) inv[i]=-1;
  for(int i=0;i<NTRUPLUS_N;i++){int v=q.coeffs[i]; if(v<1||v>NTRUPLUS_N||inv[v]>=0){printf("qsoa value %d at %d not a permutation\n",v,i);return 1;} inv[v]=i;}
  for(int i=0;i<NTRUPLUS_N;i++) map[i]=inv[i+1];
  /* granularity: do 4-coeff GT blocks come from 4 consecutive-in-something QSoA slots? */
  int blk8=0,pairs=0; for(int b=0;b<NTRUPLUS_N/4;b++){int d=map[4*b+1]-map[4*b]; if(map[4*b+2]-map[4*b+1]==d&&map[4*b+3]-map[4*b+2]==d) blk8++;}
  printf("GT 4-coeff blocks with constant QSoA stride: %d / %d (stride of block0 = %d)\n",blk8,NTRUPLUS_N/4,map[1]-map[0]);
  printf("first GT blocks -> QSoA pos:"); for(int b=0;b<6;b++) printf(" [%d %d %d %d]",map[4*b],map[4*b+1],map[4*b+2],map[4*b+3]); puts("");
  printf("GT pos 384.. -> :"); for(int b=96;b<99;b++) printf(" [%d %d %d %d]",map[4*b],map[4*b+1],map[4*b+2],map[4*b+3]); puts("");
  (void)pairs;
  /* the real test */
  for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(int16_t)((i*2654435761u+17)%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
  int tot=0;
  for(int trial=0;trial<64;trial++){
    for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(int16_t)(((i+trial*977)*40503u+99+trial)%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
    poly a,c,b,f,m;
    poly_frombytes_basemul_decap_scale(&a,&c,ct,fb);
    for(int i=0;i<NTRUPLUS_N;i++) g.coeffs[i]=a.coeffs[map[i]];   /* Official product, relaid out to block-major */
    poly_invntt_decap_scale(&a); poly_crepmod3(&a,&a);
    poly_invntt(&m,&g); poly_crepmod3(&m,&m);
    poly_frombytes_encap(&c,ct); poly_frombytes_encap(&f,fb); poly_basemul(&b,&c,&f);
    int dm=0,bad=0; for(int i=0;i<NTRUPLUS_N;i++){ int x=(g.coeffs[i]-b.coeffs[i])%NTRUPLUS_Q; dm+= x!=0; bad+=a.coeffs[i]!=m.coeffs[i]; }
    if(trial<2) printf("trial %d: products differ mod q at %d slots; GT-inv(Official product) vs Official chain: %d mismatches\n",trial,dm,bad);
    tot+=bad;}
  printf("64 trials total mismatches: %d\n",tot); return tot!=0;}
