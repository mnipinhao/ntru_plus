/* The lane-store variant must be bit-identical, every slot, not just the 128
 * it writes: a stray store would show up in the untouched remainder. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_st1_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
static uint64_t st=0x243f6a8885a308d3ull;
static int16_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return (int16_t)((st>>33)%5235)-2617;}
int main(void){
    static int16_t in[128],a[1024],b[1024];
    for(int trial=0;trial<5000;trial++){
        for(int i=0;i<128;i++) in[i]=rnd();
        memset(a,0x5a,sizeof a); memset(b,0x5a,sizeof b);
        invntt16_asm(a,in,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
        invntt16_st1_asm(b,in,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
        if(memcmp(a,b,sizeof a)){
            for(int p=0;p<1024;p++) if(a[p]!=b[p]){printf("  第 %d 次, 位置 %d: %d vs %d\n",trial,p,a[p],b[p]);break;}
            return 1;
        }
    }
    puts("  5000 次隨機輸入, 1024 個 halfword 全部位元相同");
    return 0;
}
