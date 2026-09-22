#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "layout.h"
#include "params.h"
#include "poly.h"
void poly_tobytes_keygen_cq(uint8_t*, const gt_cq_poly*);
void poly_tobytes_decap(uint8_t*, const poly*);
int  o_poly_frombytes(poly*, const uint8_t*);
int main(void){
    static gt_cq_poly cq; static poly nat; static uint8_t buf[NTRUPLUS_POLYBYTES];
    for(int i=0;i<NTRUPLUS_N;i++) cq.storage.coeffs[i]=(int16_t)i;
    poly_tobytes_keygen_cq(buf,&cq);
    o_poly_frombytes(&nat,buf);
    static int seen[NTRUPLUS_N]; int bad=0;
    for(int i=0;i<NTRUPLUS_N;i++){int v=nat.coeffs[i];
        if(v<0||v>=NTRUPLUS_N||seen[v]++) bad++;}
    printf("  natural[j] = cq[pi(j)] 是置換: %s\n", bad?"否":"是");
    printf("  pi 的前 32 項:\n   ");
    for(int i=0;i<32;i++) printf("%4d",nat.coeffs[i]);
    printf("\n  (區塊, 元素) 每 8 個自然係數 = 一個 12-byte 區塊:\n");
    for(int b=0;b<6;b++){ printf("   blk%-2d ",b);
        for(int l=0;l<8;l++){int c=nat.coeffs[8*b+l]; printf("(%2d,%d)",c/8,c%8);} printf("\n"); }
    /* is the CQ source of each natural block a fixed element across 8 blocks? */
    int half_uniform=1, consec=1;
    for(int b=0;b<NTRUPLUS_N/8;b++) for(int h=0;h<2;h++){
        int e0=nat.coeffs[8*b+4*h]%8, s0=nat.coeffs[8*b+4*h]/8;
        for(int l=1;l<4;l++){int c=nat.coeffs[8*b+4*h+l];
            if(c%8!=e0) half_uniform=0;
            if(c/8!=s0+l) consec=0;}
    }
    printf("  每 4-lane 半區元素一致: %s, 來源區塊連續: %s\n",
           half_uniform?"是":"否", consec?"是":"否");
    /* identity check against the plain serializer */
    static poly p; static uint8_t b2[NTRUPLUS_POLYBYTES];
    for(int i=0;i<NTRUPLUS_N;i++) p.coeffs[i]=(int16_t)i;
    poly_tobytes_decap(b2,&p);
    printf("  tobytes_decap 是自然順序: %s\n", memcmp(b2,buf,sizeof buf)?"否":"是");
    return 0;
}
