#define _GNU_SOURCE
#include "cluster_tbl_frombytes.h"
#include "p3b20_tables.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <unistd.h>
static uint32_t rng=1;static uint32_t next_u32(void){rng=rng*1664525u+1013904223u;return rng;}
static void oracle(int16_t out[864],const uint8_t in[1296]){for(int p=0;p<432;p++){uint16_t a=(uint16_t)(in[3*p]|((uint16_t)in[3*p+1]<<8))&4095,b=(uint16_t)((in[3*p+1]>>4)|((uint16_t)in[3*p+2]<<4));out[p3b20_map[2*p]]=(int16_t)a;out[p3b20_map[2*p+1]]=(int16_t)b;}}
static void cmp(const int16_t*a,const int16_t*b,int t){for(int i=0;i<864;i++)if(a[i]!=b[i]){fprintf(stderr,"fail test=%d coeff=%d expected=%d actual=%d\n",t,i,a[i],b[i]);exit(1);}}
int main(void){uint8_t in[1296];int16_t e[864],a[864];for(int t=0;t<256;t++){for(int i=0;i<1296;i++)in[i]=(uint8_t)next_u32();oracle(e,in);gt864_fr0_cluster_tbl_frombytes(a,in);cmp(e,a,t);}long ps=sysconf(_SC_PAGESIZE);if(ps<=0)return 2;size_t page=(size_t)ps;uint8_t*x=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0),*y=mmap(NULL,3*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);if(x==MAP_FAILED||y==MAP_FAILED)return 2;if(mprotect(x,page,PROT_NONE)||mprotect(x+2*page,page,PROT_NONE)||mprotect(y,page,PROT_NONE)||mprotect(y+2*page,page,PROT_NONE))return 2;for(int edge=0;edge<2;edge++){uint8_t*ip=x+page+(edge?page-1296:0);int16_t*op=(int16_t*)(y+page+(edge?page-1728:0));for(int i=0;i<1296;i++)ip[i]=(uint8_t)i;oracle(e,ip);gt864_fr0_cluster_tbl_frombytes(op,ip);cmp(e,op,256+edge);}munmap(x,3*page);munmap(y,3*page);puts("p3b20_correctness=pass cases=256 guarded_edges=2");return 0;}
