/* NTRU+864 decapsulation arithmetic chain: forward, R^-1 product, fused
 * inverse-to-ternary. Correctness probe only; not a timing harness. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "poly.h"
#include "inverse.h"
int main(int argc,char**argv){
    static poly a,b,A,B,m,out;
    if(argc!=2){fprintf(stderr,"usage: probe864 <2x864 values>\n");return 2;}
    char*p=argv[1];
    for(int i=0;i<864;i++){ a.coeffs[i]=(int16_t)strtol(p,&p,10); if(*p==',')p++; }
    for(int i=0;i<864;i++){ b.coeffs[i]=(int16_t)strtol(p,&p,10); if(*p==',')p++; }
    poly_ntt(&A,&a); poly_ntt(&B,&b);
    poly_basemul_rinv(m.coeffs,A.coeffs,B.coeffs);
    poly_invntt_ternary(&out,&m);
    for(int i=0;i<864;i++) printf("%d%c",out.coeffs[i],i==863?'\n':',');
    return 0;
}
