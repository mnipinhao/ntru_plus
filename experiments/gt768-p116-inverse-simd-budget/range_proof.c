/* P116: exhaustive bound on the post branch-merge sum y, over all int16 inputs x and every branchfold constant.
 * Per output vector the table holds 4 q: lo normal, lo precompute, hi normal, hi precompute (8 lanes each).
 * p = x*c - q*sqrdmulh(x,c'); y lane i<4 = p_lo[i]+p_lo[i+4], lane i>=4 = p_hi[i-4]+p_hi[i]. */
#include <stdio.h>
#include <stdint.h>
#include "branchfold_table.h"
static int16_t sat(int32_t v){return v>32767?32767:v<-32768?-32768:v;}
static int16_t sqrdmulh(int16_t a,int16_t b){return sat(((int32_t)a*b*2+32768)>>16);}
static int maxabs(short c,short cp){int m=0; for(int x=-32768;x<=32767;x++){int16_t t=sqrdmulh((int16_t)x,cp); int16_t p=(int16_t)((int16_t)(x*c)-(int16_t)(t*3457)); int a=p<0?-p:p; if(a>m)m=a;} return m;}
int main(void){ int nvec=(int)(sizeof BF/sizeof BF[0])/32, worst=0, worstp=0;
 for(int v=0;v<nvec;v++){ const short*T=BF+32*v; int m[2][8];
   for(int h=0;h<2;h++) for(int l=0;l<8;l++){ m[h][l]=maxabs(T[16*h+l],T[16*h+8+l]); if(m[h][l]>worstp) worstp=m[h][l]; }
   for(int h=0;h<2;h++) for(int l=0;l<4;l++){ int y=m[h][l]+m[h][l+4]; if(y>worst) worst=y; } }
 printf("%d output vectors: max|product| = %d, max|y| <= %d (Barrett centered for |y| < 29385: %s)\n",nvec,worstp,worst,worst<29385?"PROVED":"FAILS");
 return worst>=29385; }
