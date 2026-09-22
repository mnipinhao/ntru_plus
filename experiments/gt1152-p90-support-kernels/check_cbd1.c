#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "poly.h"
void poly_cbd1(poly*, const uint8_t*);
void n_cbd1(poly*, const uint8_t*);
static uint8_t buf[NTRUPLUS_N/4]; static poly a,b;
int main(void){
  int bad=0;
  for(int t=0;t<500;t++){
    for(size_t i=0;i<sizeof buf;i++) buf[i]=(uint8_t)(((i+t*7919)*2654435761u)>>19);
    memset(&a,0x5A,sizeof a); memset(&b,0x5A,sizeof b);
    poly_cbd1(&a,buf); n_cbd1(&b,buf);
    if(memcmp(&a,&b,sizeof a)){ if(!bad) for(int i=0;i<NTRUPLUS_N;i++) if(a.coeffs[i]!=b.coeffs[i]){printf("  首個不同 i=%d: %d vs %d\n",i,a.coeffs[i],b.coeffs[i]);break;} bad++; }
  }
  printf(bad?"  %d/500 組不符\n":"  500 組隨機 buf 全部一致\n",bad); return 0;}
