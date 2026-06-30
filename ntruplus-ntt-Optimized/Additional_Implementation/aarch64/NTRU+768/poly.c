#include "poly.h"
#include <arm_neon.h>

static const int16_t consts[] __attribute__((aligned(16))) = {
    0x0d81, 0x4bd4, 0xcd7f, 0xff6d, 0xfa8f, 0xf9dd, 0xc5d5, 0x0000
};

static inline int16x8_t fqmul_neon(int16x8_t x, int16x8_t y, int16x8_t con)
{
    int32x4_t l, h;
    int16x8_t t;

    l  = vmull_s16(vget_low_s16(x), vget_low_s16(y));
    h  = vmull_high_s16(x, y);

    t  = vuzp1q_s16(vreinterpretq_s16_s32(l), vreinterpretq_s16_s32(h));
    t  = vmulq_laneq_s16(t, con, 2);

    l  = vmlal_lane_s16(l, vget_low_s16(t), vget_low_s16(con), 0);
    h  = vmlal_high_lane_s16(h, t, vget_low_s16(con), 0);

    return vuzp2q_s16(vreinterpretq_s16_s32(l), vreinterpretq_s16_s32(h));
}

static inline int16x8_t fqinv_neon(int16x8_t a, int16x8_t con)
{
    int16x8_t t, t16, t128, t145, t691, u;

    t = fqmul_neon(a, a, con);       // 2
    t = fqmul_neon(t, t, con);       // 4
    t = fqmul_neon(t, t, con);       // 8
    t16 = fqmul_neon(t, t, con);     // 16

    t = fqmul_neon(t16, t16, con);   // 32
    t = fqmul_neon(t, t, con);       // 64
    t128 = fqmul_neon(t, t, con);    // 128

    t = fqmul_neon(t128, t16, con);  // 144
    t145 = fqmul_neon(t, a, con);    // 145
    t = fqmul_neon(t145, t128, con); // 273
    t = fqmul_neon(t, t, con);       // 546
    t691 = fqmul_neon(t, t145, con); // 691

    t = fqmul_neon(t691, t691, con); // 1382
    t = fqmul_neon(t, t, con);       // 2764
    t = fqmul_neon(t, t691, con);    // 3455

    u = vqrdmulhq_laneq_s16(t, con, 6);
    t = vmulq_laneq_s16(t, con, 5);
    t = vmlsq_laneq_s16(t, u, con, 0);

    return t;
}

static inline int poly_fqinv_batch(int16x8_t r[24], int16x8_t con)
{
    int16x8_t c[24];
    int16x8_t inv;

    c[0] = r[0];

    for (int i = 1; i < 24; i++)
        c[i] = fqmul_neon(c[i - 1], r[i], con);

    if (!vminvq_u16(vreinterpretq_u16_s16(c[23]))) return 1;

    inv = fqinv_neon(c[23], con);

    for (int i = 23; i > 0; i--)
    {
        int16x8_t ri = r[i];
        r[i] = fqmul_neon(c[i - 1], inv, con);
        inv  = fqmul_neon(inv, ri, con);
    }

    r[0] = inv;

    return 0;
}

extern void poly_baseinv_1(poly *r, int16x8_t* den, const poly* a);

static inline void poly_baseinv_2(poly *r, int16x8_t *den, int16x8_t con)
{
    int16_t *rp = r->coeffs;

    for (int i = 0; i < 24; i++)
    {
        int16x8_t pden = den[i];
        int16x8_t mden = vnegq_s16(pden);

        int offset = i * 32;

        int16x8_t r0 = vld1q_s16(rp + offset +  0);
        int16x8_t r1 = vld1q_s16(rp + offset +  8);
        int16x8_t r2 = vld1q_s16(rp + offset + 16);
        int16x8_t r3 = vld1q_s16(rp + offset + 24);

        r0 = fqmul_neon(r0, pden, con);
        r1 = fqmul_neon(r1, mden, con);
        r2 = fqmul_neon(r2, pden, con);
        r3 = fqmul_neon(r3, mden, con);

        vst1q_s16(rp + offset +  0, r0);
        vst1q_s16(rp + offset +  8, r1);
        vst1q_s16(rp + offset + 16, r2);
        vst1q_s16(rp + offset + 24, r3);
    }
}

int poly_baseinv(poly *r, const poly *a)
{
    int16x8_t con = vld1q_s16(consts);
    int16x8_t den[24] __attribute((aligned(16)));

    poly_baseinv_1(r, den, a);

    if(poly_fqinv_batch(den, con))
    {
        for (int i = 0; i < NTRUPLUS_N; i++)
            r->coeffs[i] = 0;
        
        return 1;
    } 
    poly_baseinv_2(r, den, con);

    return 0;
}
