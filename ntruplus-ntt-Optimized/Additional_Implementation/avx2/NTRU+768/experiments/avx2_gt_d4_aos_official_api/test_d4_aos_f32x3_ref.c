#include "d4_aos_f32x3_ref.h"
#include <stdio.h>
#include <string.h>
static unsigned s=3;static int r(void){s=1664525*s+1013904223;return (int)(s>>16);}int main(void){d4aos_coeff_poly a,x,y;d4aos_ntt_poly d,f;for(int n=0;n<10000;n++){for(int i=0;i<768;i++)a.coeff[i]=(int16_t)(r()%3457);d4aos_ref_forward(&d,&a);d4aos_f32x3_ref_forward(&f,&a);if(memcmp(&d,&f,sizeof d)){puts("f");return 1;}d4aos_f32x3_ref_inverse(&x,&f);d4aos_ref_inverse(&y,&d);if(memcmp(&x,&y,sizeof x)){puts("i");return 1;}}puts("f32x3-ref=passed rounds=10000");}
