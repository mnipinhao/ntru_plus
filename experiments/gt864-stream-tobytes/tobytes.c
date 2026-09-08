#include <arm_neon.h>
#include <stdint.h>
#include "poly.h"
#include "p3b1_tables.h"
/* Routing output is immediately normalized and packed as pairs of wire
 * coefficients. ST3 lane writes each pair's three bytes at a nine-byte
 * stride. No output-byte merge and no full coefficient array. */
static inline uint16x8_t norm(int16x8_t a){
    int16x8_t q=vdupq_n_s16(3457);
    a=vmlsq_s16(a,vqrdmulhq_s16(a,vdupq_n_s16(9)),q);
    return vreinterpretq_u16_s16(vaddq_s16(a,vandq_s16(vshrq_n_s16(a,15),q)));
}
static inline void emit(uint8_t *out,int16x8_t x,int16x8_t y){
    uint16x8_t a=norm(x),b=norm(y);
    uint8x8x3_t bytes={{vmovn_u16(a),
        vmovn_u16(vorrq_u16(vshrq_n_u16(a,8),vshlq_n_u16(b,4))),
        vmovn_u16(vshrq_n_u16(b,4))}};
    vst3_lane_u8(out+0*9,bytes,0);vst3_lane_u8(out+1*9,bytes,1);
    vst3_lane_u8(out+2*9,bytes,2);vst3_lane_u8(out+3*9,bytes,3);
    vst3_lane_u8(out+4*9,bytes,4);vst3_lane_u8(out+5*9,bytes,5);
    vst3_lane_u8(out+6*9,bytes,6);vst3_lane_u8(out+7*9,bytes,7);
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
static inline void route(int16x8_t output[9],const int16_t *in)
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
#define ROUTE_OUT(k) output[p[k]]=vreinterpretq_s16_u8(vqtbl1q_u8(vreinterpretq_u8_s16(w[k]),vld1q_u8(p3b1_a_fwd[k])));
    ROUTE_OUT(0) ROUTE_OUT(1) ROUTE_OUT(2) ROUTE_OUT(3) ROUTE_OUT(4)
    ROUTE_OUT(5) ROUTE_OUT(6) ROUTE_OUT(7) ROUTE_OUT(8)
#undef ROUTE_OUT
}

__attribute__((noinline))
static void pair(uint8_t *out,const int16_t *a,const int16_t *b){
    int16x8_t x[9],y[9];
    route(x,a);route(y,b);
    emit(out+72*0,x[0],y[0]);emit(out+72*1,x[1],y[1]);emit(out+72*2,x[2],y[2]);
    emit(out+72*3,x[3],y[3]);emit(out+72*4,x[4],y[4]);emit(out+72*5,x[5],y[5]);
    emit(out+72*6,x[6],y[6]);emit(out+72*7,x[7],y[7]);emit(out+72*8,x[8],y[8]);
}
void stream_tobytes(uint8_t *out,const poly *in){
    for(int top=0;top<2;++top){
        const int16_t *p=in->coeffs+432*top;
        uint8_t *o=out+648*top;
        pair(o,p,p+8);             /* p0:c0,c1 */
        pair(o+3,p+16,p+216);      /* p0:c2,p1:c0 */
        pair(o+6,p+224,p+232);     /* p1:c1,c2 */
    }
}
