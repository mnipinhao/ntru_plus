/* NTRU+1152 decapsulation arithmetic chain. Correctness probe only. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "inverse.h"
#include "inverse_tables.h"
#include "inverse16_tables.h"
void ntt_asm(int16_t out[1152], const int16_t in[1152]);
void invntt_ternary_asm(int16_t*,const int16_t*,const int16_t*,const int16_t*,
                        const int16_t*,const int16_t*);
int main(int argc,char**argv){
    static int16_t a[1152],b[1152],A[1152],B[1152],m[1152],out[1152];
    if(argc!=2){fprintf(stderr,"usage: harness <2x1152>\n");return 2;}
    char*p=argv[1];
    for(int i=0;i<1152;i++){a[i]=(int16_t)strtol(p,&p,10); if(*p==',')p++;}
    for(int i=0;i<1152;i++){b[i]=(int16_t)strtol(p,&p,10); if(*p==',')p++;}
    ntt_asm(A,a); ntt_asm(B,b);
    basemul_rinv_asm(m,A,B);
    invntt_ternary_asm(out,m,&invntt9_constants[0][0][0][0][0],
        &invntt16_constants[0][0],&invntt16_main_constants[0][0],
        &invntt16_tail_constants[0][0]);
    for(int i=0;i<1152;i++) printf("%d%c",out[i],i==1151?'\n':',');
    return 0;
}
