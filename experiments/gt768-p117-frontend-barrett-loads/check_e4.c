/* P117: E4 vs E3 on real chains, and on synthetic inputs at Official's product bound. */
#include <stdio.h>
#include <stdlib.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
int e3_poly_frombytes_basemul_decap_scale(poly*,poly*,const unsigned char*,const unsigned char*);
void e3_poly_invntt(poly*,const poly*);
void e4_poly_invntt(poly*,const poly*);
static unsigned rng=31337; static unsigned rnd(void){rng=rng*1103515245u+12345u; return rng>>8;}
int main(void){ static unsigned char ct[NTRUPLUS_POLYBYTES],fb[NTRUPLUS_POLYBYTES]; poly t,c,p,a,b,o; long bad=0,bado=0;
 for(int trial=0;trial<3000;trial++){
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()&1? NTRUPLUS_Q-1-(rnd()%4): rnd()%NTRUPLUS_Q); poly_tobytes_encap(ct,&t);
   for(int i=0;i<NTRUPLUS_N;i++) t.coeffs[i]=(short)(rnd()%NTRUPLUS_Q); poly_tobytes_encap(fb,&t);
   poly_frombytes_basemul_decap_scale(&o,&c,ct,fb); poly_invntt_decap_scale(&o); poly_crepmod3(&o,&o);
   e3_poly_frombytes_basemul_decap_scale(&p,&c,ct,fb); e4_poly_invntt(&b,&p);
   for(int i=0;i<NTRUPLUS_N;i++) bado+=o.coeffs[i]!=b.coeffs[i]; }
 printf("E4 chain vs Official chain, 3000 skewed ct: %ld mismatches\n",bado);
 /* synthetic |x|<=2458: E4 is proved; any E3 disagreement is an E3 error */
 long e3wrong=0,e4truth=0,e3truth=0; int polys=0;
 for(int trial=0;trial<2000;trial++){
   for(int i=0;i<NTRUPLUS_N;i++){ int mode=trial%4; int v= mode==0? ((rnd()&1)?2458:-2458) : mode==1? 2458 : mode==2? ((i/4)&1?2458:-2458) : (int)(rnd()%4917)-2458; p.coeffs[i]=(short)v; }
   e3_poly_invntt(&a,&p); e4_poly_invntt(&b,&p);
   { poly q; for(int g=0;g<24;g++) for(int l=0;l<8;l++) for(int k=0;k<4;k++) q.coeffs[32*g+8*k+l]=p.coeffs[32*g+4*l+k];
     poly_invntt_decap_scale(&q); poly_crepmod3(&q,&q); for(int i=0;i<NTRUPLUS_N;i++){ e4truth+=q.coeffs[i]!=b.coeffs[i]; e3truth+=q.coeffs[i]!=a.coeffs[i]; } }
   int d=0; for(int i=0;i<NTRUPLUS_N;i++) d+=a.coeffs[i]!=b.coeffs[i]; e3wrong+=d; polys+=d>0; }
 printf("synthetic |x|<=2458 (2000 polys): E3 differs from proved E4 in %d polys, %ld coefficients\n",polys,e3wrong);
 printf("vs Official inverse on the same inputs: E4 %ld, E3 %ld coefficient mismatches\n",e4truth,e3truth);
 return bado!=0; }
