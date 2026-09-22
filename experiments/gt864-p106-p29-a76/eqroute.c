/* the widened route must write the identical 864 halfwords */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
void invntt_route_asm(int16_t*, const int16_t*);
void route_wide_asm(int16_t*, const int16_t*);
static uint64_t st=0x243f6a8885a308d3ull;
static int16_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return (int16_t)((st>>33)%9155)-4577;}
int main(void){
    static int16_t scr[768], a[1024], b[1024]; long bad=0;
    for(int t=0;t<5000;t++){
        for(int i=0;i<768;i++) scr[i]=rnd();
        memset(a,0x5a,sizeof a); memset(b,0x5a,sizeof b);
        invntt_route_asm(a,scr); route_wide_asm(b,scr);
        if(memcmp(a,b,sizeof a)) bad++;
    }
    printf("  5000 組輸入, 1024 個 halfword 不符 %ld\n",bad);
    return bad!=0;}
