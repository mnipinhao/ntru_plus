#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
void tobytes_full_asm(uint8_t*, const int16_t*);
void tobytes_small_asm(uint8_t*, const int16_t*);
int  tobytes_compare_asm(const uint8_t*, const int16_t*);
void p87_tobytes_full(uint8_t*, const int16_t*);
void p87_tobytes_small(uint8_t*, const int16_t*);
int  p87_tobytes_compare(const uint8_t*, const int16_t*);
static int16_t in[NTRUPLUS_N];
static uint8_t r1[NTRUPLUS_POLYBYTES+64], r2[NTRUPLUS_POLYBYTES+64], bad_[NTRUPLUS_POLYBYTES+64];
int main(void){
  int bad=0;
  for(int t=0;t<400;t++){
    /* full: any signed int16 */
    for(int i=0;i<NTRUPLUS_N;i++) in[i]=(int16_t)(((i+t*7919)*2654435761u)%65536);
    memset(r1,0xAA,sizeof r1); memset(r2,0xAA,sizeof r2);
    tobytes_full_asm(r1,in); p87_tobytes_full(r2,in);
    if(memcmp(r1,r2,sizeof r1)){printf("  FULL mismatch @t=%d\n",t); if(++bad>3)break; continue;}
    if(tobytes_compare_asm(r1,in)||p87_tobytes_compare(r1,in)){printf("  compare 誤報 @t=%d\n",t);bad++;}
    memcpy(bad_,r1,sizeof r1); bad_[(t*37)%NTRUPLUS_POLYBYTES]^=1u<<(t%8);
    if(!tobytes_compare_asm(bad_,in)||!p87_tobytes_compare(bad_,in)){printf("  compare 漏報 @t=%d\n",t);bad++;}
    /* small: strictly inside (-3457,3457) */
    for(int i=0;i<NTRUPLUS_N;i++) in[i]=(int16_t)(((i+t*104729)*2246822519u)%6913)-3456;
    memset(r1,0xAA,sizeof r1); memset(r2,0xAA,sizeof r2);
    tobytes_small_asm(r1,in); p87_tobytes_small(r2,in);
    if(memcmp(r1,r2,sizeof r1)){printf("  SMALL mismatch @t=%d\n",t); if(++bad>3)break;}
    if(bad>3)break;
  }
  printf(bad?"  %d 個問題\n":"  400 組: full / small / compare(含漏報偵測) 全部與組語版一致，無越界\n",bad);
  return 0;}
