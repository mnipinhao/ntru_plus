#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include "../generated/pack_identity14_mapping.h"
void ntruplus768_pack_m_lazy10788_avx2(uint8_t*,const int16_t*);
void ntruplus768_exp001_pack_identity14(uint8_t*,const int16_t*);
static uint32_t rng=9183;
static uint32_t rnd(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return rng;}
static unsigned canon(int x){int v=x%3457;return (unsigned)(v<0?v+3457:v);}
static void check(int16_t *in,uint8_t*out){
    _Alignas(32) int16_t saved[768]; uint8_t old[1152],oracle[1152];
    memcpy(saved,in,sizeof saved);
    ntruplus768_pack_m_lazy10788_avx2(old,in);
    ntruplus768_exp001_pack_identity14(out,in);
    for(int i=0;i<768;i+=2){unsigned a=canon(in[id14_wire_to_m[i]]),b=canon(in[id14_wire_to_m[i+1]]);
        oracle[i*3/2]=(uint8_t)a;oracle[i*3/2+1]=(uint8_t)((a>>8)|(b<<4));oracle[i*3/2+2]=(uint8_t)(b>>4);}
    if(memcmp(old,out,1152)||memcmp(oracle,out,1152)||memcmp(saved,in,sizeof saved))abort();
}
int main(void){
    _Alignas(32) int16_t in[768];uint8_t storage[1216];
    for(unsigned t=0;t<65536+10003;t++){
        for(unsigned i=0;i<768;i++)in[i]=(int16_t)(t<65536?(uint16_t)(t+97u*i):(uint16_t)rnd());
        memset(storage,0x93,sizeof storage);check(in,storage+32);
        for(int i=0;i<32;i++)if(storage[i]!=0x93||storage[1184+i]!=0x93)abort();
    }
    long page=sysconf(_SC_PAGESIZE);if(page<=0)abort();size_t p=(size_t)page;
    uint8_t*a=mmap(NULL,2*p,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    uint8_t*b=mmap(NULL,2*p,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(a==MAP_FAILED||b==MAP_FAILED||mprotect(a+p,p,PROT_NONE)||mprotect(b+p,p,PROT_NONE))abort();
    int16_t*end=(int16_t*)(a+p-1536);memcpy(end,in,1536);check(end,b+p-1152);
    munmap(a,2*p);munmap(b,2*p);
    puts("PASS identity14: 65536 shifted signed-i16 sweeps + 10003 random vectors; scalar wire oracle, immutability, canary, guard ends");
    return 0;
}
