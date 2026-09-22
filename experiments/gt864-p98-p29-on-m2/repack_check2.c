/* Corrected free layout: main block i = 2c + (j>=4), group g at halfword 4g;
 * tail c-block at 32 halfwords, group g at halfword g. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
void repack_asm(int16_t*,const int16_t*,const int16_t*);
int main(void){
    static int16_t nat[864], got[864], mn[768], tl[96];
    for(int i=0;i<864;i++) nat[i]=(int16_t)(i+1);
    for(int g=0;g<32;g++) for(int j=0;j<9;j++) for(int c=0;c<3;c++){
        int v=nat[27*g+3*j+c];
        if(j==8) tl[32*c+g]=v; else mn[128*(2*c+(j>=4))+4*g+(j%4)]=v;
    }
    memset(got,0,sizeof got);
    repack_asm(got,mn,tl);
    int bad=0; for(int i=0;i<864;i++) if(got[i]!=nat[i]){ if(!bad)
        printf("  第一個不符 位置 %d: 得 %d 應為 %d\n",i,got[i],nat[i]); bad++; }
    printf("  %d/864 還原正確\n",864-bad);
    return bad!=0;
}
