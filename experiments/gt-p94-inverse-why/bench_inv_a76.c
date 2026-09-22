#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include "params.h"
#include "poly.h"
void poly_invntt_ternary(poly*, const poly*);
void o_poly_invntt_scale(poly*);
void o_poly_crepmod3(poly*);
static inline uint64_t nsec(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);
 return (uint64_t)t.tv_sec*1000000000ull+(uint64_t)t.tv_nsec;}
static volatile unsigned sink; static poly a,b;
int main(void){
  for(int i=0;i<NTRUPLUS_N;i++) a.coeffs[i]=(int16_t)((i*2654435761u)%3457)-1728;
  for(int w=0;w<20000;w++){poly_invntt_ternary(&b,&a); b=a; o_poly_invntt_scale(&b); o_poly_crepmod3(&b); sink+=b.coeffs[0];}
  uint64_t g=~0ull,o=~0ull,c=~0ull;
  for(int r=0;r<41;r++){
    uint64_t t=nsec(); for(int k=0;k<20000;k++){poly_invntt_ternary(&b,&a); sink+=b.coeffs[0];} uint64_t d=nsec()-t; if(d<g)g=d;
    t=nsec(); for(int k=0;k<20000;k++){b=a; o_poly_invntt_scale(&b); o_poly_crepmod3(&b); sink+=b.coeffs[0];} d=nsec()-t; if(d<o)o=d;
    t=nsec(); for(int k=0;k<20000;k++){b=a; sink+=b.coeffs[0];} d=nsec()-t; if(d<c)c=d; }
  double G=(double)g/20000,O=(double)o/20000,C=(double)c/20000;
  printf("  GT invntt_ternary        %7.1f ns\n",G);
  printf("  Official invntt+crepmod3 %7.1f ns  (扣複製 %.1f 後 %7.1f)\n",O,C,O-C);
  printf("  → GT / Official = %.2fx\n",G/(O-C));
  return 0;}
