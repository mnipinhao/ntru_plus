/* Test-only scalar cores for public-wrapper control tests before Slothy RA.
 * Never link this file into the real assembly test or benchmark binary. */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static int16_t redc(int32_t x) {
    int16_t t=(int16_t)((uint32_t)x*(uint32_t)-12929);
    return (int16_t)((x+(int32_t)t*3457)/65536);
}
static int16_t mm(int16_t a,int16_t b){return redc((int32_t)a*b);}
static int16_t center(int x){x%=3457;if(x>1728)x-=3457;if(x< -1728)x+=3457;return x;}
void binv_num_tile(int16_t *out,const int16_t *in,const int16_t *z,int16_t *den){
    int16_t copy[24];memcpy(copy,in,sizeof copy);
    for(int l=0;l<8;l++){
        int16_t a=mm(copy[l],867),b=mm(copy[l+8],867),c=mm(copy[l+16],867);
        int16_t n0=mm(a,a)-mm(z[l],mm(b,c));
        int16_t n1=mm(z[l],mm(c,c))-mm(a,b);
        int16_t n2=mm(b,b)-mm(a,c);
        den[l]=mm(a,n0)+mm(z[l],mm(b,n2)+mm(c,n1));
        out[l]=n0;out[l+8]=n1;out[l+16]=n2;
    }
}
void binv_prefix3(int16_t*out,const int16_t*a,const int16_t*b){
    int16_t tmp[24];for(int i=0;i<24;i++)tmp[i]=mm(a[i],b[i]);memcpy(out,tmp,sizeof tmp);
}
void binv_inverse3(int16_t*out,const int16_t*in){
    int16_t tmp[24];
    for(int l=0;l<8;l++){
        int16_t x=in[l],y=in[l+8],z=in[l+16],xy=mm(x,y),xyz=mm(xy,z),r=-147;
        for(int bit=11;bit>=0;bit--){r=mm(r,r);if((3455>>bit)&1)r=mm(r,xyz);}
        int16_t rxy=mm(r,z);tmp[l]=mm(rxy,y);tmp[l+8]=mm(rxy,x);tmp[l+16]=mm(r,xy);
    }memcpy(out,tmp,sizeof tmp);
}
void binv_recover3(int16_t*out,const int16_t*p,int16_t*running,const int16_t*den){
    int16_t next[24],tmp[24];
    for(int i=0;i<24;i++){tmp[i]=mm(p[i],running[i]);next[i]=mm(running[i],den[i]);}
    memcpy(out,tmp,sizeof tmp);memcpy(running,next,sizeof next);
}
void binv_finish_tile(int16_t*out,const int16_t*den){
    for(int l=0;l<8;l++){int16_t d=mm(den[l],1);for(int c=0;c<3;c++)out[8*c+l]=center(mm(out[8*c+l],d));}
}
void bm_rinv_tile(int16_t*out,const int16_t*a,const int16_t*b,const int16_t*z){
    int16_t tmp[24];
    for(int l=0;l<8;l++){
        int16_t c0=redc(a[l+16]*(int32_t)b[l+8]+a[l+8]*(int32_t)b[l+16]);
        int16_t c1=redc(a[l+16]*(int32_t)b[l+16]);
        tmp[l]=redc(c0*(int32_t)z[l]+a[l]*(int32_t)b[l]);
        tmp[l+8]=redc(c1*(int32_t)z[l]+a[l]*(int32_t)b[l+8]+a[l+8]*(int32_t)b[l]);
        tmp[l+16]=redc(a[l+16]*(int32_t)b[l]+a[l+8]*(int32_t)b[l+8]+a[l]*(int32_t)b[l+16]);
    }memcpy(out,tmp,sizeof tmp);
}
void center32(int16_t*out){for(int i=0;i<32;i++)out[i]=center(out[i]);}
#ifdef ORACLE_INVERSE
#include "gt864_fr0_inverse_asm.h"
/* Test-only adapters reuse original executable assembly, not lazy candidates. */
void packed_i9(int16_t*out,int16_t*tail,const int16_t*in,const int16_t*twist){
    int16_t old[64];
    gt864_fr0_inverse9_block_asm(old,tail,in,(const int16_t(*)[2][8])twist);
    for(int col=0;col<8;col++)for(int half=0;half<2;half++)for(int l=0;l<4;l++)
        out[8*col+128*half+l]=old[8*col+4*half+l];
}
void lazy_i16(int16_t*out,const int16_t*in,const int16_t*unused,const int16_t*stage,const int16_t*scale){
    (void)unused;int16_t a[128]={0},b[128]={0};
    for(int col=0;col<16;col++)for(int l=0;l<4;l++){
        a[8*col+l]=in[8*col+l];b[8*col+l]=in[8*col+4+l];
    }
    gt864_inverse16_main_block_asm(out,a,b,(const int16_t(*)[16])stage,(const int16_t(*)[2][8])scale);
}
void lazy_itail(int16_t*out,const int16_t*in,const int16_t*unused,const int16_t*stage,const int16_t*scale){
    gt864_inverse16_tail_block_asm(out,in,unused,(const int16_t(*)[16])stage,(const int16_t(*)[2][8])scale);
}
#else
/* The BaseInv-only control test never exercises Inverse. */
void packed_i9(void){abort();}
void lazy_i16(void){abort();}
void lazy_itail(void){abort();}
#endif
