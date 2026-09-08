#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "poly.h"
void fr0_basemul_for_inverse(int16_t *,const int16_t *,const int16_t *);
void fr0_inverse_scaled(poly *,const poly *);
void gt_d1_poly_basemul(poly *,const poly *,const poly *);
void gt_d1_poly_invntt(poly *,const poly *);
static uint32_t s=123;
static uint32_t rnd(void){s^=s<<13;s^=s>>17;s^=s<<5;return s;}
static int mod(int64_t a){int v=a%3457;return v<0?v+3457:v;}
void randombytes(unsigned char *p,size_t n){while(n--)*p++=rnd();}
int main(void){poly a,b,c,d,x,y;
 for(int t=0;t<512;++t){
  for(int j=0;j<864;++j){a.coeffs[j]=rnd()&4095;b.coeffs[j]=rnd()&4095;
   if(t<4){a.coeffs[j]=(t&1)?4095:0;b.coeffs[j]=(t&2)?4095:0;}}
  gt_d1_poly_basemul(&c,&a,&b);fr0_basemul_for_inverse(d.coeffs,a.coeffs,b.coeffs);
  for(int j=0;j<864;++j)if(mod((int64_t)d.coeffs[j]*65536)!=mod(c.coeffs[j])||d.coeffs[j]<-2497||d.coeffs[j]>2497)return 1;
  gt_d1_poly_invntt(&x,&c);fr0_inverse_scaled(&y,&d);
  if(memcmp(&x,&y,sizeof x)){printf("inverse mismatch %d\n",t);return 1;}
 }
 puts("PASS 512 FromBytes-range products; exact R^-1 relation; centered inverse equality");
}
