#include "api.h"
#include "poly.h"
#include "scaled_tables.h"
#include "gt864_fr0_basemul_tables.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
void fr0_inverse_scaled(poly*,const poly*);
int probe_inverse(int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*,const int16_t*);
static uint32_t state=2911;
static uint32_t rnd(void){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
static void check(int x,const char *m){if(!x){fprintf(stderr,"FAIL %s\n",m);exit(1);}}
static int mod(int64_t x){int r=x%3457;return r<0?r+3457:r;}
struct guarded{uint64_t pre;poly p;uint64_t post;};
static int invoke(poly*out,const poly*in){return probe_inverse(out->coeffs,in->coeffs,
 &gt864_inverse9_twist_barrett[0][0][0][0][0],&gt864_inverse16_stage_barrett[0][0],
 &gt864_inverse16_main_scale_barrett[0][0][0],&gt864_inverse16_tail_scale_barrett[0][0][0]);}
int main(void){
    struct guarded input={.pre=123,.post=321},out={.pre=456,.post=654},alias;
    poly ref,a,b,product;
    for(int t=0;t<256;t++){
        for(int i=0;i<864;i++)input.p.coeffs[i]=(int)(rnd()%4995)-2497;
        if(t<4)for(int i=0;i<864;i++)input.p.coeffs[i]=(int[]){0,2497,-2497,1}[t];
        fr0_inverse_scaled(&ref,&input.p);
        check(invoke(&out.p,&input.p)==0,"Inverse ABI/scratch wipe");
        check(!memcmp(&out.p,&ref,sizeof ref),"Inverse reference equality");
        alias=input;check(invoke(&alias.p,&alias.p)==0,"Inverse alias ABI/scratch");
        check(!memcmp(&alias.p,&ref,sizeof ref),"Inverse alias equality");
        check(input.pre==123&&input.post==321&&out.pre==456&&out.post==654&&alias.pre==123&&alias.post==321,"canaries");
        for(int i=0;i<864;i++){a.coeffs[i]=rnd()%4096;b.coeffs[i]=rnd()%4096;}
        gt864_basemul_rinv_asm(product.coeffs,a.coeffs,b.coeffs,&gt864_fr0_zetas_mul[0][0]);
        for(int j=0;j<36;j++)for(int l=0;l<8;l++){
            int k=24*j+l;int64_t x=a.coeffs[k],y=a.coeffs[k+8],z=a.coeffs[k+16];
            int64_t u=b.coeffs[k],v=b.coeffs[k+8],w=b.coeffs[k+16];
            int root=mod((int64_t)gt864_fr0_zetas_mul[j][l]*2775);
            int64_t expected[3]={x*u+root*(y*w+z*v),x*v+y*u+root*z*w,x*w+y*v+z*u};
            for(int c=0;c<3;c++){
                check(mod(product.coeffs[k+8*c])==mod(expected[c]*2775),"independent cubic R^-1 identity");
                check(abs(product.coeffs[k+8*c])<=2497,"BaseMul output range");
            }
        }
        alias.p=a;gt864_basemul_rinv_asm(alias.p.coeffs,alias.p.coeffs,b.coeffs,&gt864_fr0_zetas_mul[0][0]);
        check(!memcmp(&alias.p,&product,sizeof product),"BaseMul exact alias");
        fr0_inverse_scaled(&ref,&product);
        check(!invoke(&out.p,&product)&&!memcmp(&out.p,&ref,sizeof ref),"BaseMul R^-1 -> Inverse");
    }
    puts("PASS Inverse 256 inputs + 256 BaseMul R^-1 chains; alias/canaries/AAPCS/1792-byte scratch wipe");
}
