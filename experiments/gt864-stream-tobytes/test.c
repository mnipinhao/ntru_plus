#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "poly.h"
void stream_tobytes(uint8_t *,const poly *);
void p3b12_candidate_tobytes(uint8_t *,const poly *);
static uint32_t s=1;
static uint32_t rnd(void){s^=s<<13;s^=s>>17;s^=s<<5;return s;}
void randombytes(unsigned char *p,size_t n){while(n--)*p++=rnd();}
int main(void){poly a;uint8_t b[1296],c[1296+32];
 for(int t=0;t<1536;++t){
    for(int j=0;j<864;++j)a.coeffs[j]=(int16_t)rnd();
    if(t<864){memset(&a,0,sizeof a);a.coeffs[t]=1234;}
    memset(c,0xa5,sizeof c);p3b12_candidate_tobytes(b,&a);stream_tobytes(c+16,&a);
    if(memcmp(b,c+16,1296)){printf("byte mismatch %d\n",t);return 1;}
    for(int j=0;j<16;++j)if(c[j]!=0xa5||c[1312+j]!=0xa5)return 1;
 }
 puts("PASS all 864 impulses and random full-int16 vectors, output canaries");
}
