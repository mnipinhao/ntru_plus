#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
void tobytes_full_asm(uint8_t*, const int16_t*);
void tobytes_p86_full(uint8_t*, const int16_t*);
int  tobytes_compare_asm(const uint8_t*, const int16_t*);
int  tobytes_compare_p86(const uint8_t*, const int16_t*);
int  frombytes_asm(int16_t*, const uint8_t*);
int  frombytes_p86(int16_t*, const uint8_t*);
static int16_t in[NTRUPLUS_N], o1[NTRUPLUS_N+32], o2[NTRUPLUS_N+32];
static uint8_t buf[NTRUPLUS_POLYBYTES+64], bad_[NTRUPLUS_POLYBYTES+64];
int main(void){
  int bad=0;
  for(int t=0;t<300;t++){
    for(int i=0;i<NTRUPLUS_N;i++) in[i]=(int16_t)(((i+t*7919)*2654435761u)%6913)-3456;
    tobytes_full_asm(buf,in);
    if(tobytes_compare_asm(buf,in)||tobytes_compare_p86(buf,in)){printf("  compare 誤報 @t=%d\n",t);bad++;}
    memcpy(bad_,buf,sizeof buf); bad_[(t*37)%NTRUPLUS_POLYBYTES]^=1u<<(t%8);
    if(!tobytes_compare_asm(bad_,in)||!tobytes_compare_p86(bad_,in)){printf("  compare 漏報 @t=%d\n",t);bad++;}
    memset(o1,0x5A,sizeof o1); memset(o2,0x5A,sizeof o2);
    int r1=frombytes_asm(o1,buf), r2=frombytes_p86(o2,buf);
    if(r1!=r2||memcmp(o1,o2,sizeof o1)){printf("  frombytes 不一致 @t=%d (r %d/%d)\n",t,r1,r2);bad++;}
    for(int i=0;i<NTRUPLUS_POLYBYTES;i++) buf[i]=(uint8_t)((i*t)*2654435761u>>13);
    r1=frombytes_asm(o1,buf); r2=frombytes_p86(o2,buf);
    if(r1!=r2){printf("  frombytes 範圍旗標不一致 @t=%d (%d/%d)\n",t,r1,r2);bad++;}
    if(bad>4)break;
  }
  printf(bad?"  %d 個問題\n":"  300 組: compare 正確/漏報、frombytes 值與範圍旗標全部一致\n",bad);
  return 0;}
