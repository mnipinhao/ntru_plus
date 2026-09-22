/* Does P29 still fit today's production inverse9 and scratch layout?
 *
 * Production: poly_invntt_ternary.  P29: the same twelve packed_i9 calls the
 * driver issues, then three p28_paired_i16, then p29_tail_direct and
 * p29_main_route.  The route reads Q-bases (0,16,64) for top0 and (32,48,80)
 * for top1, which are exactly the six 256-byte P8 blocks, so the pairing has to
 * be (block0,block2), (block1,block3), (block4,block5). */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "params.h"
#include "poly.h"
#include "inverse_tables.h"
#include "inverse16_tables.h"
void poly_invntt_ternary(poly*, const poly*);
void packed_i9(int16_t*, int16_t*, const int16_t*, const int16_t*);
void p28_paired_i16(int16_t*, int16_t*, long, const int16_t*, const int16_t*);
void p29_tail_direct(int16_t*, const int16_t*, long, const int16_t*, const int16_t*);
void p29_main_route(int16_t*, const int16_t*);

/* byte offsets, copied from inverse.S's unrolled dispatch */
static const int I9_O[12]={0,128,512,640,1024,1152,8,136,520,648,1032,1160};
static const int I9_T[12]={1536,1664,1538,1666,1540,1668,1542,1670,1544,1672,1546,1674};
static const int I9_I[12]={0,48,16,64,32,80,864,912,880,928,896,944};
static const int I9_Z[12]={0,288,0,288,0,288,576,864,576,864,576,864};

static void p29_inverse(poly *out, const poly *in, int pa, int pb, int pc){
    static int16_t scratch[896];
    /* padding is NOT cleared in production: the driver's clear writes to
     * sp + 1536 while the scratch has been caller-owned in x25 since P80.
     * Fill it with garbage and see whether either side notices. */
    for(int i=0;i<896;i++) scratch[i]=(int16_t)(0x5a5a ^ (i*2654435761u));
    uint8_t *S=(uint8_t*)scratch; const uint8_t *IN=(const uint8_t*)in->coeffs;
    const uint8_t *Z=(const uint8_t*)&invntt9_constants[0][0][0][0][0];
    for(int i=0;i<12;i++)
        packed_i9((int16_t*)(S+I9_O[i]),(int16_t*)(S+I9_T[i]),
                  (const int16_t*)(IN+I9_I[i]),(const int16_t*)(Z+I9_Z[i]));
    const int B[6]={0,256,512,768,1024,1280};
    const int pr[3][2]={{0,2},{1,3},{4,5}};
    int sel[3]={pa,pb,pc};
    for(int k=0;k<3;k++)
        p28_paired_i16((int16_t*)(S+B[pr[sel[k]][0]]),(int16_t*)(S+B[pr[sel[k]][1]]),0,
                       &invntt16_constants[0][0],&invntt16_main_constants[0][0]);
    p29_tail_direct(out->coeffs,(const int16_t*)(S+1536),0,
                    &invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
    p29_main_route(out->coeffs,(const int16_t*)S);
}
static uint64_t st=0x243f6a8885a308d3ull;
static int16_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return (int16_t)((st>>33)%5235)-2617;}
static void fill(poly *p, int mode, int k){
    for(int i=0;i<NTRUPLUS_N;i++){
        switch(mode){
          case 0: p->coeffs[i]=rnd(); break;
          case 1: p->coeffs[i]= (i+k)%2 ?  2617 : -2617; break;   /* the stated bound */
          case 2: p->coeffs[i]= 0; break;
          case 3: p->coeffs[i]= (i==k%NTRUPLUS_N) ? 2617 : 0; break;  /* unit vectors */
          case 4: p->coeffs[i]= (int16_t)(((i*2654435761u)>>k)%5235)-2617; break;
        }
    }
}
int main(void){
    static poly in,a,b;
    long cases=0, bad=0;
    for(int mode=0;mode<5;mode++){
        int reps = (mode==0||mode==4) ? 2000 : (mode==3 ? 864 : 4);
        for(int k=0;k<reps;k++){
            fill(&in,mode,k);
            poly_invntt_ternary(&a,&in);
            memset(&b,0,sizeof b);
            p29_inverse(&b,&in,0,1,2);
            for(int i=0;i<NTRUPLUS_N;i++) if(a.coeffs[i]!=b.coeffs[i]) bad++;
            cases++;
            /* in place, the way kem.c calls it */
            poly c=in; poly_invntt_ternary(&c,&c);
            poly d=in; p29_inverse(&d,&d,0,1,2);
            for(int i=0;i<NTRUPLUS_N;i++) if(c.coeffs[i]!=d.coeffs[i]) bad++;
            cases++;
        }
    }
    printf("  %ld 個案例 (隨機/邊界/零/單位向量/別名), 不符係數 %ld\n",cases,bad);
    /* ternary range */
    fill(&in,0,0); p29_inverse(&b,&in,0,1,2);
    int rng=1; for(int i=0;i<NTRUPLUS_N;i++) if(b.coeffs[i]<-1||b.coeffs[i]>1) rng=0;
    printf("  輸出全在 {-1,0,1}: %s\n", rng?"是":"否");
    return bad!=0;
}
