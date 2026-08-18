#include "d4_aos_f32x3_ref.h"
#include <stdio.h>
#include <string.h>
static unsigned s=1;static int r(void){s=1664525*s+1013904223;return (int)(s>>16);}static int go(d4aos_f32x3_state*a){d4aos_f32x3_state x,y;d4aos_f32x3_ref_inverse_checkpoint_stage0(&x,a);gt_d4aos_f32x3_invntt32_stage0_asm(&y,a);return memcmp(&x,&y,sizeof x)==0;}int main(void){d4aos_f32x3_state a;for(int i=0;i<768;i++){memset(&a,0,sizeof a);a.lane[i]=1;if(!go(&a))return 1;}for(int n=0;n<10000;n++){for(int i=0;i<768;i++)a.lane[i]=(int16_t)(r()%3457);if(!go(&a))return 1;}puts("f32x3-stage0-asm=passed basis=768 random=10000");}
