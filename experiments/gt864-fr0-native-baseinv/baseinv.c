/* BINV-FR0-0: conservative, default-off FR0-native inverse.
 * Public ABI: same poly pointer shape, centered R0 output; alias-safe.
 * Internal arithmetic is R1. Each tile is [a0 lanes][a1 lanes][a2 lanes].
 * No conversion to the stock polynomial layout occurs.
 */
#include <arm_neon.h>
#include <stdint.h>
#include "poly.h"
#include "gt864_fr0_basemul_tables.h"

static inline int16x8_t center(int16x8_t a)
{
    int16x8_t q=vdupq_n_s16(3457);
    a=vmlsq_s16(a,vqrdmulhq_s16(a,vdupq_n_s16(9)),q);
    a=vaddq_s16(a,vandq_s16(vshrq_n_s16(a,15),q));
    return vsubq_s16(a,vandq_s16(vreinterpretq_s16_u16(
        vcgtq_s16(a,vdupq_n_s16(1728))),q));
}

/* a,b centered; signed REDC bound <=1774 before centering.
 * -q^-1 mod 2^16 = -12929. Product + t*q fits signed int32.
 */
static inline int16x8_t mm_pre(int16x8_t a,int16x8_t b,int16x8_t bqi)
{
    int16x8_t t=vmulq_s16(a,bqi),q=vdupq_n_s16(3457);
    int32x4_t lo=vmull_s16(vget_low_s16(a),vget_low_s16(b));
    int32x4_t hi=vmull_high_s16(a,b);
    lo=vmlal_s16(lo,vget_low_s16(t),vget_low_s16(q));
    hi=vmlal_high_s16(hi,t,q);
    int16x8_t result=vuzp2q_s16(vreinterpretq_s16_s32(lo),vreinterpretq_s16_s32(hi));
#ifdef FR0_LAZY
    return result; /* |inputs|<=4000 => |result|<2000; see proof.py */
#else
    return center(result);
#endif
}
static inline int16x8_t mm(int16x8_t a,int16x8_t b)
{ return mm_pre(a,b,vmulq_s16(b,vdupq_n_s16(-12929))); }
static inline int16x8_t add(int16x8_t a,int16x8_t b)
{
#ifdef FR0_LAZY
    return vaddq_s16(a,b);
#else
    return center(vaddq_s16(a,b));
#endif
}
static inline int16x8_t sub(int16x8_t a,int16x8_t b)
{
#ifdef FR0_LAZY
    return vsubq_s16(a,b);
#else
    return center(vsubq_s16(a,b));
#endif
}
static int16x8_t inverse(int16x8_t x)
{
    int16x8_t r=vdupq_n_s16(-147); /* 1 in R1 */
    /* Fixed public exponent q-2. No input-dependent exponent path. */
    for(int bit=11;bit>=0;--bit){
        r=mm(r,r);
        if ((3455u>>bit)&1u) r=mm(r,x);
    }
    return r;
}

int fr0_native_baseinv(poly *out,const poly *in)
{
    int16x8_t den[36],prefix[36];
    const int16x8_t r2=vdupq_n_s16(867);
    for(int j=0;j<36;++j){
        int16x8_t a=mm(center(vld1q_s16(in->coeffs+24*j)),r2);
        int16x8_t b=mm(center(vld1q_s16(in->coeffs+24*j+8)),r2);
        int16x8_t c=mm(center(vld1q_s16(in->coeffs+24*j+16)),r2);
        /* Existing D1 zetas are z*R in this exact FR0 lane ordering. */
        int16x8_t z=vld1q_s16(gt864_fr0_zetas_mul[j]);
        int16x8_t b0=sub(mm(a,a),mm(z,mm(b,c)));
        int16x8_t b1=sub(mm(z,mm(c,c)),mm(a,b));
        int16x8_t b2=sub(mm(b,b),mm(a,c));
        den[j]=add(mm(a,b0),mm(z,add(mm(b,b2),mm(c,b1))));
        vst1q_s16(out->coeffs+24*j,b0);
        vst1q_s16(out->coeffs+24*j+8,b1);
        vst1q_s16(out->coeffs+24*j+16,b2);
    }
    /* Three independent 12-vector chains. All live products remain R1. */
    prefix[0]=den[0];prefix[12]=den[12];prefix[24]=den[24];
    for(int i=1;i<12;++i){
        prefix[i]=mm(prefix[i-1],den[i]);
        prefix[12+i]=mm(prefix[11+i],den[12+i]);
        prefix[24+i]=mm(prefix[23+i],den[24+i]);
    }
    int16x8_t x=prefix[11],y=prefix[23],z=prefix[35];
    uint16x8_t zero=vorrq_u16(vceqq_s16(x,vdupq_n_s16(0)),
        vorrq_u16(vceqq_s16(y,vdupq_n_s16(0)),vceqq_s16(z,vdupq_n_s16(0))));
    /* Same caller-visible noninvertible decision as the existing API. */
    if(vmaxvq_u16(zero)){
        for(int j=0;j<864;j+=8)vst1q_s16(out->coeffs+j,vdupq_n_s16(0));
        return 1;
    }
    int16x8_t xy=mm(x,y),inv=inverse(mm(xy,z));
    int16x8_t invxy=mm(inv,z);
    int16x8_t i0=mm(invxy,y),i1=mm(invxy,x),i2=mm(inv,xy);
    for(int i=11;i>0;--i){
        x=den[i];y=den[12+i];z=den[24+i];
        den[i]=mm(prefix[i-1],i0);den[12+i]=mm(prefix[11+i],i1);
        den[24+i]=mm(prefix[23+i],i2);
        i0=mm(i0,x);i1=mm(i1,y);i2=mm(i2,z);
    }
    den[0]=i0;den[12]=i1;den[24]=i2;
    for(int j=0;j<36;++j){
        /* Convert inverse denominator R1 -> R0 once. Numerators are R1:
         * REDC(R1 numerator * R0 inverse denominator) gives R0 output.
         * Reuse d*(-q^-1) across all three component products. */
        int16x8_t d=mm(den[j],vdupq_n_s16(1));
        int16x8_t dqi=vmulq_s16(d,vdupq_n_s16(-12929));
        for(int c=0;c<3;++c){
            int16_t *p=out->coeffs+24*j+8*c;
            vst1q_s16(p,center(mm_pre(vld1q_s16(p),d,dqi)));
        }
    }
    return 0;
}
