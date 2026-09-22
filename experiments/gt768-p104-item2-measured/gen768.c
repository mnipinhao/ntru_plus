#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "layout.h"
#include "params.h"
#include "poly.h"
int poly_frombytes_encap(poly*, const uint8_t*);
void o_poly_tobytes(uint8_t*, const poly*);
int main(void){
    static poly nat,g; static uint8_t buf[NTRUPLUS_POLYBYTES];
    for(int i=0;i<NTRUPLUS_N;i++) nat.coeffs[i]=(int16_t)i;
    o_poly_tobytes(buf,&nat); poly_frombytes_encap(&g,buf);
    /* each 4-lane half is element e of blocks 4q..4q+3 */
    printf("/* Generated from the shipped poly_frombytes_encap: output vector v\n"
           " * takes lanes 0-3 from element half_elem[v][0] of the four 12-byte\n"
           " * blocks starting at byte 48*half_quad[v][0], and lanes 4-7 likewise\n"
           " * from half [1].  Derived, not invented. */\n");
    printf("static const unsigned char half_quad[%d][2] = {\n", NTRUPLUS_N/8);
    for(int v=0; v<NTRUPLUS_N/8; v++){
        int q0=g.coeffs[8*v]/8/4, q1=g.coeffs[8*v+4]/8/4;
        printf("%s{%2d,%2d},", v%8?" ":"    ", q0,q1);
        if(v%8==7) printf("\n");
    }
    printf("};\nstatic const unsigned char half_elem[%d][2] = {\n", NTRUPLUS_N/8);
    for(int v=0; v<NTRUPLUS_N/8; v++){
        printf("%s{%d,%d},", v%8?" ":"    ", g.coeffs[8*v]%8, g.coeffs[8*v+4]%8);
        if(v%8==7) printf("\n");
    }
    printf("};\n");
    /* sanity: every (quad, element) used exactly once */
    static int used[24][8]; int bad=0;
    for(int v=0; v<NTRUPLUS_N/8; v++) for(int h=0;h<2;h++){
        int c=g.coeffs[8*v+4*h]; if(used[c/8/4][c%8]++) bad++;
    }
    fprintf(stderr,"  24x8 個 (quad, element) 各用一次: %s\n", bad?"否":"是");
    return 0;
}
