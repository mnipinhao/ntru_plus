#define _GNU_SOURCE
#include "input_once_tobytes.h"
#include "p3b6_tables.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static uint32_t rng = 1;
static uint32_t next_u32(void) { rng=rng*1664525u+1013904223u; return rng; }
static int16_t canon(int16_t x) { int32_t r=x%3457; return (int16_t)(r<0?r+3457:r); }

static void oracle(uint8_t out[1296],const int16_t in[864])
{
    for(int pair=0;pair<432;pair++) {
        uint16_t a=(uint16_t)canon(in[p3b6_map[2*pair]]);
        uint16_t b=(uint16_t)canon(in[p3b6_map[2*pair+1]]);
        out[3*pair]=(uint8_t)a;
        out[3*pair+1]=(uint8_t)((a>>8)|(b<<4));
        out[3*pair+2]=(uint8_t)(b>>4);
    }
}

static void compare(const uint8_t expected[1296],const uint8_t actual[1296],int test)
{
    for(int i=0;i<1296;i++) if(expected[i]!=actual[i]) {
        fprintf(stderr,"fail test=%d byte=%d expected=%u actual=%u\n",
                test,i,expected[i],actual[i]);
        exit(1);
    }
}

int main(void)
{
    int16_t input[864]; uint8_t expected[1296],actual[1296];
    for(int test=0;test<256;test++) {
        for(int i=0;i<864;i++) input[i]=test==0?(int16_t)i:
            test==1?INT16_MIN:test==2?INT16_MAX:(int16_t)next_u32();
        oracle(expected,input); gt864_fr0_input_once_tobytes(actual,input);
        compare(expected,actual,test);
    }
    long ps=sysconf(_SC_PAGESIZE); if(ps<=0)return 2; size_t page=(size_t)ps;
    uint8_t *a=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    uint8_t *b=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    if(a==MAP_FAILED||b==MAP_FAILED)return 2;
    if(mprotect(a,page,PROT_NONE)||mprotect(a+2*page,page,PROT_NONE)||
       mprotect(b,page,PROT_NONE)||mprotect(b+2*page,page,PROT_NONE))return 2;
    for(int edge=0;edge<2;edge++) {
        int16_t *in=(int16_t*)(a+page+(edge?page-1728:0));
        uint8_t *out=b+page+(edge?page-1296:0);
        for(int i=0;i<864;i++)in[i]=(int16_t)(i-432);
        oracle(expected,in);gt864_fr0_input_once_tobytes(out,in);
        compare(expected,out,256+edge);
    }
    munmap(a,3*page);munmap(b,3*page);
    puts("p3b6_correctness=pass cases=256 guarded_edges=2 bytes=1296");
    return 0;
}
