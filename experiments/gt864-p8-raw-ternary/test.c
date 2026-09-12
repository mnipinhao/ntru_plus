#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "gt864_native.h"
#include "gt864_native_scaled_tables.h"
int probe_inverse(int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*);
void gt864_crepmod3_raw(int16_t*);
static int ref(int x) { x%=3457;if(x>1728)x-=3457;if(x< -1728)x+=3457;x%=3;if(x>1)x-=3;if(x< -1)x+=3;return x; }
static uint32_t seed=864;
static uint32_t rnd(void){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;return seed;}
int main(void){
    struct {uint64_t left;poly p;uint64_t right;} box;
    for(int base=-4577;base<=4577;base+=864){
        box.left=0x123456789abcdefULL;box.right=0xfedcba987654321ULL;
        for(int i=0;i<864;i++)box.p.coeffs[i]=(base+i>4577?4577:base+i);
        gt864_crepmod3_raw(box.p.coeffs);
        for(int i=0;i<864;i++)if(box.p.coeffs[i]!=ref(base+i>4577?4577:base+i))return 1;
        if(box.left!=0x123456789abcdefULL||box.right!=0xfedcba987654321ULL)return 2;
    }
    poly in,old,out,alias;
    for(int trial=0;trial<1024;trial++){
        for(int i=0;i<864;i++)in.coeffs[i]=trial==0?2497:trial==1?-2497:(int)(rnd()%4995)-2497;
        gt864_native_inverse(&old,&in);poly_crepmod3(&old,&old);
        gt864_native_inverse_ternary(&out,&in);alias=in;gt864_native_inverse_ternary(&alias,&alias);
        if(memcmp(&old,&out,sizeof old)||memcmp(&old,&alias,sizeof old))return 3;
        if(probe_inverse(out.coeffs,in.coeffs,&gt864_inverse9_twist_barrett[0][0][0][0][0],
          &gt864_inverse16_stage_barrett[0][0],&gt864_inverse16_main_scale_barrett[0][0][0],
          &gt864_inverse16_tail_scale_barrett[0][0][0]))return 4;
        if(memcmp(&old,&out,sizeof old))return 5;
    }
    puts("PASS raw exhaustive 9155 values/canaries; 1024 complete inverse+conversion exact/alias/AAPCS/wipe cases");
    return 0;
}
