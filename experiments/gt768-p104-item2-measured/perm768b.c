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
    o_poly_tobytes(buf,&nat);
    poly_frombytes_encap(&g,buf);
    /* a 12-byte block holds 8 consecutive natural coefficients */
    puts("  輸出向量 -> (區塊, 元素) 每 lane");
    for(int v=0; v<10; v++){
        printf("  v%-3d ",v);
        for(int l=0;l<8;l++){ int c=g.coeffs[8*v+l]; printf("(%2d,%d)",c/8,c%8); }
        printf("\n");
    }
    /* does each vector use one element position per 4-lane half? */
    int half_uniform=1, blocks_consecutive=1;
    for(int v=0; v<NTRUPLUS_N/8; v++)
      for(int h=0;h<2;h++){
        int e0=g.coeffs[8*v+4*h]%8, b0=g.coeffs[8*v+4*h]/8;
        for(int l=1;l<4;l++){
            int c=g.coeffs[8*v+4*h+l];
            if(c%8!=e0) half_uniform=0;
            if(c/8!=b0+l) blocks_consecutive=0;
        }
      }
    printf("\n  每個 4-lane 半區元素位置一致: %s\n", half_uniform?"是":"否");
    printf("  每個 4-lane 半區區塊連續: %s\n", blocks_consecutive?"是":"否");
    return 0;
}
