/* Same scratch in: the new kernel must write the identical values, only at
 * group-offset lane instead of group-offset 3*lane.  If that holds, the body
 * and its tables really are untouched and all that moved is the placement. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
void invntt16_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
void invntt16_lane_asm(int16_t*,const int16_t*,long,const int16_t*,const int16_t*);
static uint64_t st=0x243f6a8885a308d3ull;
static int16_t rnd(void){st^=st<<13;st^=st>>7;st^=st<<17;return (int16_t)((st>>33)%5235)-2617;}
int main(void){
    static int16_t in[128],a[896],b[896];
    long bad=0,checked=0;
    for(int trial=0;trial<2000;trial++){
        for(int i=0;i<128;i++) in[i]=rnd();
        memset(a,0,sizeof a); memset(b,0,sizeof b);
        invntt16_asm(a,in,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
        invntt16_lane_asm(b,in,0,&invntt16_constants[0][0],&invntt16_main_constants[0][0]);
        for(int g=0;g<32;g++) for(int l=0;l<4;l++,checked++)
            if(a[27*g+3*l]!=b[27*g+l]){
                if(!bad) printf("  首個不符 group %d lane %d: 舊 %d 新 %d\n",g,l,a[27*g+3*l],b[27*g+l]);
                bad++;
            }
    }
    printf("  %ld/%ld 個輸出相符 (%ld 次隨機輸入)\n",checked-bad,checked,2000L);
    return bad!=0;
}
