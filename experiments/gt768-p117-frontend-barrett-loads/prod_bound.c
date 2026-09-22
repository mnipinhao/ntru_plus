/* P117: how large can Official's first decap product get?  Extreme canonical ct/f, then random. */
#include <stdio.h>
#include <stdlib.h>
#include "params.h"
#include "poly.h"
#include "decap_verify.h"
static unsigned rng=99; static unsigned rnd(void){rng=rng*1103515245u+12345u; return rng>>8;}
static int run(const poly*a,const poly*b){ static unsigned char ct[NTRUPLUS_POLYBYTES],fb[NTRUPLUS_POLYBYTES]; poly m,c;
  poly_tobytes_encap(ct,a); poly_tobytes_encap(fb,b); if(poly_frombytes_basemul_decap_scale(&m,&c,ct,fb)) return -1;
  int mx=0; for(int i=0;i<NTRUPLUS_N;i++){int v=abs(m.coeffs[i]); if(v>mx) mx=v;} return mx; }
int main(void){ poly a,b; int best=0;
  int pats[6]={0,1,2,3,4,5};
  for(int pa=0;pa<6;pa++) for(int pb=0;pb<6;pb++){
    for(int i=0;i<NTRUPLUS_N;i++){ int s[6]={NTRUPLUS_Q-1,(i&1)*(NTRUPLUS_Q-1),((i>>2)&1)*(NTRUPLUS_Q-1),1728,1729,(i%3)*1728};
      a.coeffs[i]=(short)s[pats[pa]]; b.coeffs[i]=(short)s[pats[pb]]; }
    int v=run(&a,&b); if(v>best) best=v; }
  printf("structured extremes: max |product| = %d\n",best);
  for(int t=0;t<200000;t++){ for(int i=0;i<NTRUPLUS_N;i++){ a.coeffs[i]=(short)(rnd()&1? NTRUPLUS_Q-1-(rnd()%8): rnd()%NTRUPLUS_Q); b.coeffs[i]=(short)(rnd()%NTRUPLUS_Q);} int v=run(&a,&b); if(v>best){best=v;} }
  printf("after 200k skewed random: max |product| = %d\n",best); return 0;}
