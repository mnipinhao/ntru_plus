#include "gt864_frombytes.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
static void put(uint8_t*b,int i,unsigned x){int j=3*(i/2);if(!(i&1)){b[j]=x;b[j+1]=(b[j+1]&240)|(x>>8);}else{b[j+1]=(b[j+1]&15)|(x<<4);b[j+2]=x>>4;}}
int main(void){uint8_t b[1296];poly p;
 for(unsigned x=0;x<4096;x++){
  memset(b,0,sizeof b);for(int i=0;i<864;i++)put(b,i,x);
  if(gt864_fr0_frombytes_checked(&p,b)!=(x>=3457))return 1;
  for(int i=0;i<864;i++)if(p.coeffs[i]!=(int)x)return 2;
 }
 for(int i=0;i<864;i++){
  memset(b,0,sizeof b);put(b,i,3456);if(gt864_fr0_frombytes_checked(&p,b))return 3;
  put(b,i,3457);if(!gt864_fr0_frombytes_checked(&p,b))return 4;
 }
 puts("PASS checked decoder: all 4096 uniform values; q-1/q at every 864 wire positions");return 0;
}
