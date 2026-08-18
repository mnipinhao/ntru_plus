#include "d4_aos_avx2_proto.h"
#include <stdio.h>
#include <string.h>
static unsigned s=7; static int rnd(void){s=1664525U*s+1013904223U;return (int)(s>>16);}
static void fill(d4aos_coeff_poly *a){for(int i=0;i<768;i++)a->coeff[i]=(int16_t)(rnd()%3457);}
static int eq(const void*a,const void*b){return memcmp(a,b,1536)==0;}
int main(void){d4aos_coeff_poly a,ri,rp;d4aos_ntt_poly fa,fb,fp,bi,bp;
 for(int n=0;n<32;n++){fill(&a);d4aos_ref_forward(&fa,&a);gt_d4aos_ntt_avx2_proto(&fp,&a);if(!eq(&fa,&fp)){for(int i=0;i<768;i++)if(fa.lane[i]!=fp.lane[i]){printf("forward n=%d lane=%d ref=%d got=%d\n",n,i,fa.lane[i],fp.lane[i]);break;}return 1;}d4aos_ref_inverse(&ri,&fa);gt_d4aos_invntt_avx2_proto(&rp,&fa);if(!eq(&ri,&rp)){puts("inverse");return 1;}fill(&a);d4aos_ref_forward(&fa,&a);fill(&a);d4aos_ref_forward(&fb,&a);d4aos_ref_basemul(&bi,&fa,&fb);gt_d4aos_basemul_avx2_proto(&bp,&fa,&fb);if(!eq(&bi,&bp)){for(int i=0;i<768;i++)if(bi.lane[i]!=bp.lane[i]){printf("basemul n=%d lane=%d ref=%d got=%d\n",n,i,bi.lane[i],bp.lane[i]);break;}return 1;}}
 puts("d4aos-avx2-proto=passed rounds=32");return 0;
}
