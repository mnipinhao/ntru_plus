/* The packed tail must write the identical 96 halfwords at the identical
 * natural addresses.  Everything else in `out` must be untouched. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt_tail_direct_asm(int16_t*, const int16_t*, long, const int16_t*, const int16_t*);
void tail_packed_asm(int16_t*, const int16_t*, long, const int16_t*, const int16_t*);
static uint64_t st=0x243f6a8885a308d3ull;
static int16_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return (int16_t)((st>>33)%5235)-2617;}
int main(void){
    static int16_t scr[256], a[1024], b[1024];
    long bad=0, touched=0;
    for(int t=0;t<5000;t++){
        for(int i=0;i<256;i++) scr[i]=rnd();
        memset(a,0x5a,sizeof a); memset(b,0x5a,sizeof b);
        invntt_tail_direct_asm(a,scr,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
        tail_packed_asm(b,scr,0,&invntt16_constants[0][0],&invntt16_tail_constants[0][0]);
        if(memcmp(a,b,sizeof a)) bad++;
        if(t==0){ for(int i=0;i<1024;i++) if(a[i]!=(int16_t)0x5a5a) touched++; }
    }
    printf("  5000 組輸入, 全部 1024 個 halfword 不符 %ld  (該被寫到的位置 %ld 個)\n",bad,touched);
    return bad!=0;
}
