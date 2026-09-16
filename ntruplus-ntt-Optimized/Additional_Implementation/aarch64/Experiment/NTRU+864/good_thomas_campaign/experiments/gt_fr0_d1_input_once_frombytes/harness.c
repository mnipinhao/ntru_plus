#define _GNU_SOURCE
#include "input_once_frombytes.h"
#include "p3b11_tables.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static uint32_t rng = 1;
static uint32_t next_u32(void) { rng=rng*1664525u+1013904223u; return rng; }

static uint16_t coefficient(const uint8_t in[1296], int index)
{
    int pair=index/2;
    if((index&1)==0)
        return (uint16_t)(in[3*pair]|((uint16_t)(in[3*pair+1]&15)<<8));
    return (uint16_t)((in[3*pair+1]>>4)|((uint16_t)in[3*pair+2]<<4));
}

static void oracle(int16_t out[864],const uint8_t in[1296])
{
    for(int serialized=0;serialized<864;serialized++)
        out[p3b11_forward_map[serialized]]=(int16_t)coefficient(in,serialized);
}

static void compare(const int16_t expected[864],const int16_t actual[864],int test)
{
    for(int i=0;i<864;i++) if(expected[i]!=actual[i]) {
        fprintf(stderr,"fail test=%d coefficient=%d expected=%d actual=%d\n",
                test,i,expected[i],actual[i]);
        exit(1);
    }
}

int main(void)
{
    uint8_t input[1296]; int16_t expected[864],actual[864];
    for(int test=0;test<256;test++) {
        for(int i=0;i<1296;i++) input[i]=test==0?(uint8_t)i:
            test==1?0:test==2?255:(uint8_t)next_u32();
        oracle(expected,input); memset(actual,0xa5,sizeof actual);
        gt864_fr0_input_once_frombytes(actual,input);
        compare(expected,actual,test);
    }
    long ps=sysconf(_SC_PAGESIZE); if(ps<=0)return 2; size_t page=(size_t)ps;
    uint8_t *a=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    uint8_t *b=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(a==MAP_FAILED||b==MAP_FAILED)return 2;
    if(mprotect(a,page,PROT_NONE)||mprotect(a+2*page,page,PROT_NONE)||
       mprotect(b,page,PROT_NONE)||mprotect(b+2*page,page,PROT_NONE))return 2;
    for(int edge=0;edge<2;edge++) {
        uint8_t *in=a+page+(edge?page-1296:0);
        int16_t *out=(int16_t*)(b+page+(edge?page-1728:0));
        for(int i=0;i<1296;i++)in[i]=(uint8_t)(i*17+edge);
        oracle(expected,in);memset(out,0xa5,1728);
        gt864_fr0_input_once_frombytes(out,in);compare(expected,out,256+edge);
    }
    munmap(a,3*page);munmap(b,3*page);
    puts("p3b11_correctness=pass cases=256 guarded_edges=2 coefficients=864");
    return 0;
}
