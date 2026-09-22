#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
#include "poly.h"
int ntruplus768_officialopt_serialize_compare(const uint8_t *, const poly *);
static uint32_t rng=17;
static uint32_t next(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static void require(int ok){if(!ok){fputs("serialize compare FAILED\n",stderr);exit(1);}}
int main(void){
    poly p, saved;
    uint8_t wire[1152+64], copy[sizeof wire];
    for(int k=0;k<10003;k++){
        for(int i=0;i<768;i++) p.coeffs[i]=(int16_t)next();
        if(k==0) memset(&p,0,sizeof p);
        saved=p;
        memset(wire,0xa5,sizeof wire);
        uint8_t *w=wire+1;
        poly_tobytes(w,&p); memcpy(copy,wire,sizeof wire);
        require(ntruplus768_officialopt_serialize_compare(w,&p)==0);
        require(!memcmp(&p,&saved,sizeof p)&&!memcmp(wire,copy,sizeof wire));
        w[k%1152]^=1u<<(k%8);
        require(ntruplus768_officialopt_serialize_compare(w,&p)==1);
    }
    size_t page=(size_t)sysconf(_SC_PAGESIZE);
    uint8_t *g=mmap(NULL,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    require(g!=MAP_FAILED);require(mprotect(g+page,page,PROT_READ|PROT_WRITE)==0);
    uint8_t *w=g+2*page-1152;
    poly_tobytes(w,&p);
    require(mprotect(g+page,page,PROT_READ)==0);
    require(ntruplus768_officialopt_serialize_compare(w,&p)==0);
    require(munmap(g,page*3)==0);
    puts("serialize-compare: 10003 signed-word cases, every byte mismatch, immutability, unaligned wire, final guard page PASS");
}
