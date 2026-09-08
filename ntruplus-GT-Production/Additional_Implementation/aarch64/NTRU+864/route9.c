#include "route9.h"
#include "p3b1_tables.h"
#include <arm_neon.h>
#include <stddef.h>

void p3b1_current_f2o(int16_t *out, const int16_t *in)
{ for (size_t i=0;i<P3B1_N;i++) out[i]=in[p3b1_map[i]]; }
void p3b1_current_o2f(int16_t *out, const int16_t *in)
{ for (size_t i=0;i<P3B1_N;i++) out[p3b1_map[i]]=in[i]; }

void p3b1_factor_f2o(int16_t *out, const int16_t *in)
{
    for (size_t leaf=0;leaf<144;leaf++) {
        size_t g=leaf/8,l=leaf%8,s=p3b1_leaf[leaf];
        for (size_t top=0;top<2;top++) for(size_t c=0;c<3;c++)
            out[432*top+24*g+8*c+l]=in[432*top+s+8*c];
    }
}
void p3b1_factor_o2f(int16_t *out, const int16_t *in)
{
    for (size_t leaf=0;leaf<144;leaf++) {
        size_t g=leaf/8,l=leaf%8,s=p3b1_leaf[leaf];
        for (size_t top=0;top<2;top++) for(size_t c=0;c<3;c++)
            out[432*top+s+8*c]=in[432*top+24*g+8*c+l];
    }
}

static inline uint8x16_t lookup3(uint8x16x4_t b0, uint8x16x4_t b1,
                                 uint8x16_t b2, const uint8_t idx[3][16])
{
    uint8x16_t x=vqtbl4q_u8(b0,vld1q_u8(idx[0]));
    x=vorrq_u8(x,vqtbl4q_u8(b1,vld1q_u8(idx[1])));
    return vorrq_u8(x,vqtbl1q_u8(b2,vld1q_u8(idx[2])));
}

__attribute__((noinline))
static void r9b_fwd(int16_t *out,const int16_t *in)
{
    uint8x16x4_t a,b; uint8x16_t c;
    a.val[0]=vreinterpretq_u8_s16(vld1q_s16(in+0*24));
    a.val[1]=vreinterpretq_u8_s16(vld1q_s16(in+1*24));
    a.val[2]=vreinterpretq_u8_s16(vld1q_s16(in+2*24));
    a.val[3]=vreinterpretq_u8_s16(vld1q_s16(in+3*24));
    b.val[0]=vreinterpretq_u8_s16(vld1q_s16(in+4*24));
    b.val[1]=vreinterpretq_u8_s16(vld1q_s16(in+5*24));
    b.val[2]=vreinterpretq_u8_s16(vld1q_s16(in+6*24));
    b.val[3]=vreinterpretq_u8_s16(vld1q_s16(in+7*24));
    c=vreinterpretq_u8_s16(vld1q_s16(in+8*24));
    for(int j=0;j<9;j++) vst1q_u8((uint8_t*)(out+48*j),lookup3(a,b,c,p3b1_b_fwd[j]));
}
__attribute__((noinline))
static void r9b_rev(int16_t *out,const int16_t *in)
{
    uint8x16x4_t a,b; uint8x16_t c;
    a.val[0]=vreinterpretq_u8_s16(vld1q_s16(in+0*48));
    a.val[1]=vreinterpretq_u8_s16(vld1q_s16(in+1*48));
    a.val[2]=vreinterpretq_u8_s16(vld1q_s16(in+2*48));
    a.val[3]=vreinterpretq_u8_s16(vld1q_s16(in+3*48));
    b.val[0]=vreinterpretq_u8_s16(vld1q_s16(in+4*48));
    b.val[1]=vreinterpretq_u8_s16(vld1q_s16(in+5*48));
    b.val[2]=vreinterpretq_u8_s16(vld1q_s16(in+6*48));
    b.val[3]=vreinterpretq_u8_s16(vld1q_s16(in+7*48));
    c=vreinterpretq_u8_s16(vld1q_s16(in+8*48));
    for(int s=0;s<9;s++) vst1q_u8((uint8_t*)(out+24*s),lookup3(a,b,c,p3b1_b_rev[s]));
}

static inline void transpose8(int16x8_t r0,int16x8_t r1,int16x8_t r2,int16x8_t r3,
 int16x8_t r4,int16x8_t r5,int16x8_t r6,int16x8_t r7,int16x8_t t[8])
{
    int16x8_t a0=vtrn1q_s16(r0,r1),a1=vtrn2q_s16(r0,r1),a2=vtrn1q_s16(r2,r3),a3=vtrn2q_s16(r2,r3);
    int16x8_t a4=vtrn1q_s16(r4,r5),a5=vtrn2q_s16(r4,r5),a6=vtrn1q_s16(r6,r7),a7=vtrn2q_s16(r6,r7);
    int32x4_t b0=vtrn1q_s32(vreinterpretq_s32_s16(a0),vreinterpretq_s32_s16(a2));
    int32x4_t b1=vtrn1q_s32(vreinterpretq_s32_s16(a1),vreinterpretq_s32_s16(a3));
    int32x4_t b2=vtrn2q_s32(vreinterpretq_s32_s16(a0),vreinterpretq_s32_s16(a2));
    int32x4_t b3=vtrn2q_s32(vreinterpretq_s32_s16(a1),vreinterpretq_s32_s16(a3));
    int32x4_t b4=vtrn1q_s32(vreinterpretq_s32_s16(a4),vreinterpretq_s32_s16(a6));
    int32x4_t b5=vtrn1q_s32(vreinterpretq_s32_s16(a5),vreinterpretq_s32_s16(a7));
    int32x4_t b6=vtrn2q_s32(vreinterpretq_s32_s16(a4),vreinterpretq_s32_s16(a6));
    int32x4_t b7=vtrn2q_s32(vreinterpretq_s32_s16(a5),vreinterpretq_s32_s16(a7));
#define TD(i,x,y,hi) t[i]=vreinterpretq_s16_s64(hi##q_s64(vreinterpretq_s64_s32(x),vreinterpretq_s64_s32(y)))
    TD(0,b0,b4,vtrn1); TD(1,b1,b5,vtrn1); TD(2,b2,b6,vtrn1); TD(3,b3,b7,vtrn1);
    TD(4,b0,b4,vtrn2); TD(5,b1,b5,vtrn2); TD(6,b2,b6,vtrn2); TD(7,b3,b7,vtrn2);
#undef TD
}

#define SETLANE(k,w,j) vsetq_lane_s16(vgetq_lane_s16((j),(k)),(w),(k))
__attribute__((noinline))
static void r9a_fwd(int16_t *out,const int16_t *in)
{
    int16x8_t j0=vld1q_s16(in+8*24),j1=vld1q_s16(in+7*24),j2=vld1q_s16(in+6*24),j3=vld1q_s16(in+5*24);
    int16x8_t j4=vld1q_s16(in+4*24),j5=vld1q_s16(in+3*24),j6=vld1q_s16(in+2*24),j7=vld1q_s16(in+1*24),j8=vld1q_s16(in);
    int16x8_t t[8],w[9];
    transpose8(j0,vextq_s16(j1,j1,7),vextq_s16(j2,j2,6),vextq_s16(j3,j3,5),
               vextq_s16(j4,j4,4),vextq_s16(j5,j5,3),vextq_s16(j6,j6,2),vextq_s16(j7,j7,1),t);
    w[0]=SETLANE(0,t[0],j8);
    for(int k=1;k<7;k++) w[k]=vbslq_s16(vld1q_u16(p3b1_prefix[k-1]),t[k-1],t[k]);
    w[1]=SETLANE(1,w[1],j8); w[2]=SETLANE(2,w[2],j8); w[3]=SETLANE(3,w[3],j8);
    w[4]=SETLANE(4,w[4],j8); w[5]=SETLANE(5,w[5],j8); w[6]=SETLANE(6,w[6],j8);
    w[7]=SETLANE(7,t[6],j8); w[8]=t[7];
    static const uint8_t p[9]={0,3,6,1,4,7,2,5,8};
    for(int k=0;k<9;k++) vst1q_u8((uint8_t*)(out+48*p[k]),vqtbl1q_u8(vreinterpretq_u8_s16(w[k]),vld1q_u8(p3b1_a_fwd[k])));
}

__attribute__((noinline))
static void r9a_rev(int16_t *out,const int16_t *in)
{
    static const uint8_t p[9]={0,3,6,1,4,7,2,5,8}; int16x8_t w[9],t[8],r[8],j8=vdupq_n_s16(0);
    for(int k=0;k<9;k++) w[k]=vreinterpretq_s16_u8(vqtbl1q_u8(vreinterpretq_u8_s16(vld1q_s16(in+48*p[k])),vld1q_u8(p3b1_a_rev[k])));
    j8=SETLANE(0,j8,w[0]); j8=SETLANE(1,j8,w[1]); j8=SETLANE(2,j8,w[2]); j8=SETLANE(3,j8,w[3]);
    j8=SETLANE(4,j8,w[4]); j8=SETLANE(5,j8,w[5]); j8=SETLANE(6,j8,w[6]); j8=SETLANE(7,j8,w[7]);
    for(int k=0;k<7;k++) t[k]=vbslq_s16(vld1q_u16(p3b1_prefix[k]),w[k+1],w[k]);
    t[7]=w[8]; transpose8(t[0],t[1],t[2],t[3],t[4],t[5],t[6],t[7],r);
    vst1q_s16(out+8*24,r[0]); vst1q_s16(out+7*24,vextq_s16(r[1],r[1],1));
    vst1q_s16(out+6*24,vextq_s16(r[2],r[2],2)); vst1q_s16(out+5*24,vextq_s16(r[3],r[3],3));
    vst1q_s16(out+4*24,vextq_s16(r[4],r[4],4)); vst1q_s16(out+3*24,vextq_s16(r[5],r[5],5));
    vst1q_s16(out+2*24,vextq_s16(r[6],r[6],6)); vst1q_s16(out+1*24,vextq_s16(r[7],r[7],7)); vst1q_s16(out,j8);
}
#undef SETLANE

#define WRAP(name,core) void name(int16_t *out,const int16_t *in){for(int top=0;top<2;top++)for(int c=0;c<3;c++)for(int p=0;p<2;p++)core(out+432*top+24*p+8*c,in+432*top+216*p+8*c);}
WRAP(p3b1_r9a_f2o,r9a_fwd) WRAP(p3b1_r9b_f2o,r9b_fwd)
#undef WRAP
#define WRAP(name,core) void name(int16_t *out,const int16_t *in){for(int top=0;top<2;top++)for(int c=0;c<3;c++)for(int p=0;p<2;p++)core(out+432*top+216*p+8*c,in+432*top+24*p+8*c);}
WRAP(p3b1_r9a_o2f,r9a_rev) WRAP(p3b1_r9b_o2f,r9b_rev)
#undef WRAP
