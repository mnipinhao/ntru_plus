/* Build the free layout from a known natural array, repack, compare.
 * Free main: block i = 2c + (j>=4) at 128 halfwords, vector t at 8t,
 * lane = 4h + (j%4).  Free tail: c-block at 32 halfwords, group g at g. */
#include <stdio.h>
#include <string.h>
#include <stdint.h>
void repack_tbl_asm(int16_t*,const int16_t*,const int16_t*);
void repack_asm(int16_t*,const int16_t*,const int16_t*);
int main(void){
    static int16_t nat[864], got[864], main_[768], tail[96];
    for(int i=0;i<864;i++) nat[i]=(int16_t)(i+1);
    for(int h=0;h<2;h++) for(int t=0;t<16;t++) for(int j=0;j<9;j++) for(int c=0;c<3;c++){
        int g=t+16*h, v=nat[27*g+3*j+c];
        if(j==8) tail[32*c+g]=v;
        else     main_[128*(2*c+(j>=4))+8*t+4*h+(j%4)]=v;
    }
    memset(got,0,sizeof got);
    repack_asm(got,main_,tail);
    int bad=0; for(int i=0;i<864;i++) if(got[i]!=nat[i]){ if(!bad)
        printf("  第一個不符 位置 %d: 得 %d 應為 %d\n",i,got[i],nat[i]); bad++; }
    printf("  %d/864 還原正確\n",864-bad);
    return bad!=0;
}
