#include "pack_asm.h"
#include "codec_perm.h"

#include <arm_neon.h>

#define Q 3457
#define BARRETT_V 19412        /* ((1<<26) + Q/2) / Q */

/*
 * NTRU+1152 canonical serialization, NEON.
 *
 * Replaces the plain-C codec from gt1152-p09-pack, which the P11 profile
 * measured at 4205 cycles per frombytes against the official's 505, and 6189
 * per Full tobytes against 1148.  That gap was 70% of the whole GT deficit.
 *
 * The cause was a gather.  The old code indexed the coefficient array through
 * a permutation table, one coefficient at a time, and AArch64 NEON has no
 * gather -- so every permuted access was a scalar load, 1152 of them.
 *
 * The fix uses the right primitive.  A Good-Thomas group is 32 contiguous
 * int16: four components by eight lanes, at GT[32g .. 32g+31].  In natural
 * order a leaf is four *contiguous* coefficients.  So
 *
 *     LD4 {v0.h, v1.h, v2.h, v3.h}[k], [leaf]
 *
 * reads one leaf's four components straight into lane k of the four component
 * vectors, and ST4 does the reverse.  Eight of those move a whole group, with
 * no transpose and no TBL.  That is the degree-4 alignment advantage measured
 * in gt1152-p03-gt-layout made concrete: four int16 is exactly one lane-indexed
 * LD4/ST4, where NTRU+864's three would need LD3/ST3 and still not align for
 * packing.
 *
 * The 12-bit codec itself is then sequential over natural order, exactly as the
 * official lane does it.
 */

/* ---- 12-bit wire codec, natural order, three bytes per two coefficients ---- */

static inline void pack_natural(uint8_t out[NTRUPLUS1152_POLYBYTES],
                                const uint16_t nat[NTRUPLUS1152_N])
{
    /* 16 lanes at a time: 32 canonical coefficients become 48 bytes. */
    for (int i = 0; i < NTRUPLUS1152_N / 2; i += 16) {
        uint16x8_t a0 = vld1q_u16(nat + 2 * i);
        uint16x8_t a1 = vld1q_u16(nat + 2 * i + 8);
        uint16x8_t a2 = vld1q_u16(nat + 2 * i + 16);
        uint16x8_t a3 = vld1q_u16(nat + 2 * i + 24);

        /* even lanes are t0, odd lanes are t1 */
        uint16x8_t t0 = vuzp1q_u16(a0, a1);
        uint16x8_t t1 = vuzp2q_u16(a0, a1);
        uint16x8_t t2 = vuzp1q_u16(a2, a3);
        uint16x8_t t3 = vuzp2q_u16(a2, a3);

        uint8x16_t b0 = vuzp1q_u8(vreinterpretq_u8_u16(t0),
                                  vreinterpretq_u8_u16(t2));
        /* b1 = (t0 >> 8) | (t1 << 4) */
        uint16x8_t lo = vorrq_u16(vshrq_n_u16(t0, 8), vshlq_n_u16(t1, 4));
        uint16x8_t hi = vorrq_u16(vshrq_n_u16(t2, 8), vshlq_n_u16(t3, 4));
        uint8x16_t b1 = vuzp1q_u8(vreinterpretq_u8_u16(lo),
                                  vreinterpretq_u8_u16(hi));
        /* b2 = t1 >> 4 */
        uint16x8_t s0 = vshrq_n_u16(t1, 4);
        uint16x8_t s1 = vshrq_n_u16(t3, 4);
        uint8x16_t b2 = vuzp1q_u8(vreinterpretq_u8_u16(s0),
                                  vreinterpretq_u8_u16(s1));

        uint8x16x3_t triple = {{b0, b1, b2}};
        vst3q_u8(out + 3 * i, triple);
    }
}

static inline uint32_t unpack_natural(uint16_t nat[NTRUPLUS1152_N],
                                      const uint8_t in[NTRUPLUS1152_POLYBYTES])
{
    const uint16x8_t q = vdupq_n_u16(Q);
    const uint16x8_t mask = vdupq_n_u16(0x0FFF);
    uint16x8_t bad = vdupq_n_u16(0);

    for (int i = 0; i < NTRUPLUS1152_N / 2; i += 16) {
        uint8x16x3_t triple = vld3q_u8(in + 3 * i);
        uint8x16_t b0 = triple.val[0], b1 = triple.val[1], b2 = triple.val[2];

        uint16x8_t b0l = vmovl_u8(vget_low_u8(b0));
        uint16x8_t b0h = vmovl_high_u8(b0);
        uint16x8_t b1l = vmovl_u8(vget_low_u8(b1));
        uint16x8_t b1h = vmovl_high_u8(b1);
        uint16x8_t b2l = vmovl_u8(vget_low_u8(b2));
        uint16x8_t b2h = vmovl_high_u8(b2);

        uint16x8_t t0l = vandq_u16(vorrq_u16(b0l, vshlq_n_u16(b1l, 8)), mask);
        uint16x8_t t0h = vandq_u16(vorrq_u16(b0h, vshlq_n_u16(b1h, 8)), mask);
        uint16x8_t t1l = vandq_u16(vorrq_u16(vshrq_n_u16(b1l, 4),
                                             vshlq_n_u16(b2l, 4)), mask);
        uint16x8_t t1h = vandq_u16(vorrq_u16(vshrq_n_u16(b1h, 4),
                                             vshlq_n_u16(b2h, 4)), mask);

        /* Canonical rejection, branch-free and with no early exit. */
        bad = vorrq_u16(bad, vcgeq_u16(t0l, q));
        bad = vorrq_u16(bad, vcgeq_u16(t0h, q));
        bad = vorrq_u16(bad, vcgeq_u16(t1l, q));
        bad = vorrq_u16(bad, vcgeq_u16(t1h, q));

        vst1q_u16(nat + 2 * i,      vzip1q_u16(t0l, t1l));
        vst1q_u16(nat + 2 * i + 8,  vzip2q_u16(t0l, t1l));
        vst1q_u16(nat + 2 * i + 16, vzip1q_u16(t0h, t1h));
        vst1q_u16(nat + 2 * i + 24, vzip2q_u16(t0h, t1h));
    }
    return vmaxvq_u16(bad) != 0;
}

/* ---- reduction to canonical [0, q) ---- */

static inline int16x8_t barrett_reduce(int16x8_t a)
{
    int16x8_t t = vqdmulhq_n_s16(a, BARRETT_V);
    t = vrshrq_n_s16(t, 11);
    return vmlsq_n_s16(a, t, (int16_t)Q);
}

static inline uint16x8_t canonical(int16x8_t a)
{
    return vreinterpretq_u16_s16(
        vaddq_s16(a, vandq_s16(vshrq_n_s16(a, 15), vdupq_n_s16(Q))));
}

/* ---- the permutation, one lane-indexed LD4/ST4 per leaf ---- */

#define GATHER_LANE(k)                                                    \
    v = vld4q_lane_s16((const int16_t *)((const uint8_t *)nat + off[k]), v, k)

static inline void natural_to_gt(int16_t gt[NTRUPLUS1152_N],
                                 const uint16_t nat[NTRUPLUS1152_N])
{
    for (int g = 0; g < CODEC_GROUPS; g++) {
        const uint16_t *off = leaf_byte_offset[g];
        int16x8x4_t v;
        v.val[0] = vdupq_n_s16(0); v.val[1] = v.val[0];
        v.val[2] = v.val[0];       v.val[3] = v.val[0];
        GATHER_LANE(0); GATHER_LANE(1); GATHER_LANE(2); GATHER_LANE(3);
        GATHER_LANE(4); GATHER_LANE(5); GATHER_LANE(6); GATHER_LANE(7);
        vst1q_s16(gt + 32 * g,      v.val[0]);
        vst1q_s16(gt + 32 * g + 8,  v.val[1]);
        vst1q_s16(gt + 32 * g + 16, v.val[2]);
        vst1q_s16(gt + 32 * g + 24, v.val[3]);
    }
}

#define SCATTER_LANE(k)                                                   \
    vst4q_lane_s16((int16_t *)((uint8_t *)nat + off[k]), v, k)

/*
 * Reduction is folded into the scatter rather than run as its own pass over the
 * scratch.  Three passes became two; the coefficients are already in registers
 * when they arrive, so reducing there is free of extra traffic.
 */
static inline void gt_to_natural(uint16_t nat[NTRUPLUS1152_N],
                                 const int16_t gt[NTRUPLUS1152_N], int full)
{
    for (int g = 0; g < CODEC_GROUPS; g++) {
        const uint16_t *off = leaf_byte_offset[g];
        int16x8x4_t v;
        v.val[0] = vld1q_s16(gt + 32 * g);
        v.val[1] = vld1q_s16(gt + 32 * g + 8);
        v.val[2] = vld1q_s16(gt + 32 * g + 16);
        v.val[3] = vld1q_s16(gt + 32 * g + 24);
        if (full)
            for (int c = 0; c < 4; c++) v.val[c] = barrett_reduce(v.val[c]);
        for (int c = 0; c < 4; c++)
            v.val[c] = vreinterpretq_s16_u16(canonical(v.val[c]));
        SCATTER_LANE(0); SCATTER_LANE(1); SCATTER_LANE(2); SCATTER_LANE(3);
        SCATTER_LANE(4); SCATTER_LANE(5); SCATTER_LANE(6); SCATTER_LANE(7);
    }
}

/* ---- public entry points ---- */

void tobytes_full_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                      const int16_t in[NTRUPLUS1152_N])
{
    uint16_t nat[NTRUPLUS1152_N];

    gt_to_natural(nat, in, 1);
    pack_natural(out, nat);
}

void tobytes_small_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                       const int16_t in[NTRUPLUS1152_N])
{
    uint16_t nat[NTRUPLUS1152_N];

    gt_to_natural(nat, in, 0);
    pack_natural(out, nat);
}

int tobytes_compare_asm(const uint8_t expected[NTRUPLUS1152_POLYBYTES],
                        const int16_t in[NTRUPLUS1152_N])
{
    uint8_t bytes[NTRUPLUS1152_POLYBYTES];
    uint8x16_t acc = vdupq_n_u8(0);

    tobytes_full_asm(bytes, in);
    for (int i = 0; i < NTRUPLUS1152_POLYBYTES; i += 16)
        acc = vorrq_u8(acc, veorq_u8(vld1q_u8(bytes + i), vld1q_u8(expected + i)));
    return vmaxvq_u8(acc) != 0;
}

int frombytes_asm(int16_t out[NTRUPLUS1152_N],
                  const uint8_t in[NTRUPLUS1152_POLYBYTES])
{
    uint16_t nat[NTRUPLUS1152_N];
    uint32_t bad = unpack_natural(nat, in);

    natural_to_gt(out, nat);
    return (int)bad;
}
