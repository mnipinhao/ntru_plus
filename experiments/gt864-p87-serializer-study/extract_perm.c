#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
void tobytes_small_asm(uint8_t*, const int16_t*);
static int16_t in[NTRUPLUS_N];
static uint8_t out[NTRUPLUS_POLYBYTES+16];
int main(void){
  /* value = GT-layout index, so wire field j reveals which GT slot it came from */
  for(int i=0;i<NTRUPLUS_N;i++) in[i]=(int16_t)i;     /* indices < 3457, fit in 12 bits */
  memset(out,0,sizeof out);
  tobytes_small_asm(out,in);
  for(int j=0;j<NTRUPLUS_N;j++){
    int b=(j*3)/2; int v = (j&1) ? ((out[b]>>4)|(out[b+1]<<4)) : (out[b]|((out[b+1]&0xf)<<8));
    printf("%d\n", v & 0xFFF);
  }
  return 0;}
