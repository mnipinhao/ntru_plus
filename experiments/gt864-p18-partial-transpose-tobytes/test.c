#define _GNU_SOURCE
#include "p18_tobytes.h"
#include "p18_map.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static uint32_t rng = 1;
static uint32_t next_u32(void) { rng = rng * 1664525u + 1013904223u; return rng; }
static int16_t canon(int16_t x) { int32_t r=x%3457; return (int16_t)(r<0?r+3457:r); }
static void oracle(uint8_t out[1296], const int16_t in[864]) {
  for (int pair=0; pair<432; pair++) {
    uint16_t a=(uint16_t)canon(in[p18_map[2*pair]]);
    uint16_t b=(uint16_t)canon(in[p18_map[2*pair+1]]);
    out[3*pair]=(uint8_t)a;
    out[3*pair+1]=(uint8_t)((a>>8)|(b<<4));
    out[3*pair+2]=(uint8_t)(b>>4);
  }
}
static void compare(const uint8_t *a,const uint8_t *b,const char *mode,int test) {
  for(int i=0;i<1296;i++) if(a[i]!=b[i]) {
    fprintf(stderr,"P18 fail %s test=%d byte=%d %u!=%u\n",mode,test,i,a[i],b[i]); exit(1);
  }
}
static void fill(int16_t in[864],int small,int test) {
  static const int16_t fe[]={INT16_MIN,INT16_MAX,-3457,-3456,-1,0,1,3456,3457};
  static const int16_t se[]={-3456,-1,0,1,3456};
  for(int i=0;i<864;i++) in[i]=test==0?(small?se[i%5]:fe[i%9]):
      (small?(int16_t)((int)(next_u32()%6913)-3456):(int16_t)next_u32());
}
int main(void) {
  _Alignas(16) int16_t in[864]; uint8_t expected[1296],actual[1296];
  for(int small=0;small<2;small++) for(int test=0;test<513;test++) {
    fill(in,small,test); oracle(expected,in);
    if(small) gt864_p18_tobytes_small_asm(actual,in);
    else gt864_p18_tobytes_full_asm(actual,in);
    compare(expected,actual,small?"small":"full",test);
  }
  long ps=sysconf(_SC_PAGESIZE); if(ps<=0)return 2; size_t page=(size_t)ps;
  uint8_t *a=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  uint8_t *b=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
  if(a==MAP_FAILED||b==MAP_FAILED)return 2;
  if(mprotect(a,page,PROT_NONE)||mprotect(a+2*page,page,PROT_NONE)||
     mprotect(b,page,PROT_NONE)||mprotect(b+2*page,page,PROT_NONE))return 2;
  for(int edge=0;edge<2;edge++) {
    int16_t *ip=(int16_t *)(a+page+(edge?page-1728:0));
    uint8_t *op=b+page+(edge?page-1296:0);
    for(int i=0;i<864;i++)ip[i]=(int16_t)(i-432);
    oracle(expected,ip); gt864_p18_tobytes_full_asm(op,ip); compare(expected,op,"guard",edge);
  }
  puts("p18_correctness=pass full=513 small=513 guarded_edges=2");
  return 0;
}
