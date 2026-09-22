#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include "decode_aligned_mapping.h"
int ntruplus768_unpack_m_avx2(int16_t *,const uint8_t *);
int ntruplus768_unpack3_m_avx2(int16_t *,int16_t *,int16_t *,const uint8_t *,const uint8_t *);
int ntruplus768_exp_aligned_decode(int16_t *,const uint8_t *);
int ntruplus768_exp_aligned_decode3(int16_t *,int16_t *,int16_t *,const uint8_t *,const uint8_t *);
#define CHECK(x) do {if(!(x)){fprintf(stderr,"FAIL line %d\n",__LINE__);abort();}}while(0)
static uint64_t state=768;
static uint32_t rng(void){state^=state<<13;state^=state>>7;state^=state<<17;return (uint32_t)state;}
static void encode(uint8_t *b,const uint16_t *v){
    for(int i=0;i<384;i++){uint32_t x=v[2*i]|((uint32_t)v[2*i+1]<<12);b[3*i]=(uint8_t)x;b[3*i+1]=(uint8_t)(x>>8);b[3*i+2]=(uint8_t)(x>>16);}
}
static void check(const uint8_t *in,int shift){
    uint8_t saved[1152];memcpy(saved,in,1152);
    _Alignas(32) uint8_t a[1600],b[1600];uint16_t expected[768];int invalid=0;
    memset(a,0xa5,sizeof a);memset(b,0xa5,sizeof b);
    for(int i=0;i<768;i++){
        int offset=3*(i/2);uint32_t x=(uint32_t)in[offset]|((uint32_t)in[offset+1]<<8)|((uint32_t)in[offset+2]<<16);
        uint16_t v=(uint16_t)((x>>(12*(i%2)))&4095);expected[wire_to_m[i]]=v;invalid|=v>=3457;
    }
    int off=32+shift;
    CHECK(ntruplus768_unpack_m_avx2((int16_t *)(void *)(a+off),in)==invalid);
    CHECK(ntruplus768_exp_aligned_decode((int16_t *)(void *)(b+off),in)==invalid);
    CHECK(!memcmp(a,b,sizeof a));CHECK(!memcmp(b+off,expected,1536));CHECK(!memcmp(saved,in,1152));
    for(int i=0;i<off;i++)CHECK(b[i]==0xa5);
    for(int i=off+1536;i<1600;i++)CHECK(b[i]==0xa5);
}
static void triple(void){
    uint8_t ct[1152]={0},sk[2304]={0},saved[3456];
    _Alignas(32) int16_t a[3][768],b[3][768];
    for(int target=-1;target<3;target++)for(int position=0;position<768;position++){
        memset(ct,0,sizeof ct);memset(sk,0,sizeof sk);
        if(target>=0){uint8_t *p=target?sk+1152*(target-1):ct;int o=3*(position/2);uint32_t x=4095u<<(12*(position%2));p[o]=(uint8_t)x;p[o+1]=(uint8_t)(x>>8);p[o+2]=(uint8_t)(x>>16);}
        memcpy(saved,ct,1152);memcpy(saved+1152,sk,2304);
        int x=ntruplus768_unpack3_m_avx2(a[0],a[1],a[2],ct,sk);
        int y=ntruplus768_exp_aligned_decode3(b[0],b[1],b[2],ct,sk);
        CHECK(x==y && y==(target>=0));CHECK(!memcmp(a,b,sizeof a));
        CHECK(!memcmp(saved,ct,1152)&&!memcmp(saved+1152,sk,2304));
    }
}
static uint8_t *guarded(size_t *page){
    *page=(size_t)sysconf(_SC_PAGESIZE);
    uint8_t *p=mmap(NULL,3*(*page),PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    CHECK(p!=MAP_FAILED);CHECK(!mprotect(p+*page,*page,PROT_READ|PROT_WRITE));return p;
}
int main(void){
    uint16_t v[768]={0};uint8_t storage[1184],*in=storage;
    const uint16_t edges[]={1,2048,3456,3457,4095};
    for(int i=0;i<768;i++)for(unsigned j=0;j<sizeof edges/sizeof edges[0];j++){
        v[i]=edges[j];encode(in,v);check(in,0);v[i]=0;
    }
    for(int t=0;t<10003;t++){
        for(int i=0;i<768;i++)v[i]=(uint16_t)(rng()%(t%2?3457u:4096u));
        in=storage+(t%32);encode(in,v);check(in,2*(t%16));
    }
    triple();
    size_t pi,po;uint8_t *ip=guarded(&pi),*op=guarded(&po);
    for(int side=0;side<2;side++){
        in=ip+pi+(side?pi-1152:0);uint8_t *out=op+po+(side?po-1536:0);
        memset(in,0,1152);CHECK(!ntruplus768_exp_aligned_decode((int16_t *)(void *)out,in));
        for(int i=0;i<1536;i++)CHECK(out[i]==0);
    }
    CHECK(!munmap(ip,3*pi));CHECK(!munmap(op,3*po));
    puts("PASS decoder: 3840 position cases, 10003 random, triple invalid coverage, unaligned buffers, canary, immutability, guard pages");
    return 0;
}
