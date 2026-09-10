#include "api.h"
#include "gt864_fr0_basemul_tables.h"
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>
extern int probe_baseinv(int16_t*,const int16_t*,const int16_t*);
static uint32_t state=864;
static uint32_t rnd(void){state^=state<<13;state^=state>>17;state^=state<<5;return state;}
static int mod(int64_t x){int r=x%3457;return r<0?r+3457:r;}
struct guarded {uint64_t before;int16_t v[864];uint64_t after;};
static void check(int x,const char *msg){if(!x){fprintf(stderr,"FAIL: %s\n",msg);exit(1);}}
int main(void){
    struct guarded in={.before=123,.after=456},out={.before=789,.after=987},alias;
    unsigned success=0,failure=0;
    for(int t=0;t<808;t++){
        for(int i=0;i<864;i++)in.v[i]=(int16_t)rnd();
        if(t<8)for(int i=0;i<864;i++)in.v[i]=(int16_t[]){0,1,-1,32767,-32768,3457,-3457,1728}[t];
        if(t>=8&&t<296){int leaf=t-8,j=leaf/8,l=leaf%8;in.v[24*j+l]=in.v[24*j+8+l]=in.v[24*j+16+l]=0;}
        int status=probe_baseinv(out.v,in.v,&gt864_fr0_zetas_mul[0][0]);
        check(status==0||status==1,"ABI or scratch erasure");
        if(t>=8&&t<296)check(status==1,"injected zero leaf not rejected");
        alias=in;int s2=probe_baseinv(alias.v,alias.v,&gt864_fr0_zetas_mul[0][0]);
        check(s2==status&&!memcmp(alias.v,out.v,sizeof out.v),"exact alias differential");
        check(in.before==123&&in.after==456&&out.before==789&&out.after==987&&alias.before==123&&alias.after==456,"buffer canary");
        if(status){failure++;for(int i=0;i<864;i++)check(out.v[i]==0,"failure output not zero");continue;}
        success++;
        for(int j=0;j<36;j++)for(int l=0;l<8;l++){
            int64_t a=in.v[24*j+l],b=in.v[24*j+8+l],c=in.v[24*j+16+l];
            int64_t x=out.v[24*j+l],y=out.v[24*j+8+l],w=out.v[24*j+16+l];
            int z=mod((int64_t)gt864_fr0_zetas_mul[j][l]*2775);
            /* The promoted no-centering finish deliberately returns raw R0
             * representatives.  The proved Keygen-only consumer contract is
             * [-1972,1972], not the former centered [-1728,1728] contract. */
            check(x>=-1972&&x<=1972&&y>=-1972&&y<=1972&&w>=-1972&&w<=1972,"no-centering range");
            check(mod(a*x+z*(b*w+c*y))==1&&!mod(a*y+b*x+z*c*w)&&!mod(a*w+b*y+c*x),"cubic inverse identity");
        }
    }
    printf("PASS BaseInv 808 cases (%u success / %u failure), all 288 zero-leaf positions, alias, canaries, AAPCS, scratch wipe\n",success,failure);
}
