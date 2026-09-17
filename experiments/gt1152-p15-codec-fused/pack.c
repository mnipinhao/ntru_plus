#include "pack_asm.h"
#include "fuse_perm.h"

#include <arm_neon.h>

#define Q 3457
#define BARRETT_V 19412

/*
 * NTRU+1152 serialization, fused.
 *
 * P12 replaced the scalar gather with lane-indexed LD4/ST4 and got tobytes to
 * 2367 cycles.  P14 then measured the parts: the permutation is 780 net and the
 * 12-bit pack 461, so 1402 of that 2367 was real work and roughly 950 was the
 * natural-order scratch array being written and read back.
 *
 * This removes the scratch.  A leaf is four coefficients, which is two 12-bit
 * pairs, which is exactly six contiguous wire bytes at offset 6L -- so a whole
 * Good-Thomas group can go from int16 to wire bytes without ever materialising
 * natural order.  Load four component vectors, reduce, build the six byte
 * planes, and scatter with lane-indexed ST3.
 *
 * P14 also asked whether the permutation itself could be replaced by cheap
 * offsets.  It cannot: the scatter addresses are not a uniform stride (only
 * some groups are), the lane scramble takes nine distinct patterns, and there
 * is no closed form -- `leaf = base + A*row + B*col mod 144` has no solution.
 * What the permutation *can* do is stop costing a separate pass, which is this.
 */

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

#define PUT(k)                                                     \
    do {                                                           \
        uint8_t *p = out + off[k];                                 \
        vst3_lane_u8(p,     lo, k);                                \
        vst3_lane_u8(p + 3, hi, k);                                \
    } while (0)

static inline void serialize(uint8_t out[NTRUPLUS1152_POLYBYTES],
                             const int16_t in[NTRUPLUS1152_N], int full)
{
    for (int g = 0; g < 36; g++) {
        const uint16_t *off = leaf_wire_offset[g];
        int16x8_t r0 = vld1q_s16(in + 32 * g);
        int16x8_t r1 = vld1q_s16(in + 32 * g + 8);
        int16x8_t r2 = vld1q_s16(in + 32 * g + 16);
        int16x8_t r3 = vld1q_s16(in + 32 * g + 24);

        if (full) {
            r0 = barrett_reduce(r0); r1 = barrett_reduce(r1);
            r2 = barrett_reduce(r2); r3 = barrett_reduce(r3);
        }
        uint16x8_t c0 = canonical(r0), c1 = canonical(r1);
        uint16x8_t c2 = canonical(r2), c3 = canonical(r3);

        uint8x8x3_t lo = {{
            vmovn_u16(c0),
            vmovn_u16(vorrq_u16(vshrq_n_u16(c0, 8), vshlq_n_u16(c1, 4))),
            vmovn_u16(vshrq_n_u16(c1, 4))}};
        uint8x8x3_t hi = {{
            vmovn_u16(c2),
            vmovn_u16(vorrq_u16(vshrq_n_u16(c2, 8), vshlq_n_u16(c3, 4))),
            vmovn_u16(vshrq_n_u16(c3, 4))}};

        PUT(0); PUT(1); PUT(2); PUT(3); PUT(4); PUT(5); PUT(6); PUT(7);
    }
}

void tobytes_full_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                      const int16_t in[NTRUPLUS1152_N])
{ serialize(out, in, 1); }

void tobytes_small_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                       const int16_t in[NTRUPLUS1152_N])
{ serialize(out, in, 0); }

int tobytes_compare_asm(const uint8_t expected[NTRUPLUS1152_POLYBYTES],
                        const int16_t in[NTRUPLUS1152_N])
{
    uint8_t bytes[NTRUPLUS1152_POLYBYTES];
    uint8x16_t acc = vdupq_n_u8(0);

    serialize(bytes, in, 1);
    for (int i = 0; i < NTRUPLUS1152_POLYBYTES; i += 16)
        acc = vorrq_u8(acc, veorq_u8(vld1q_u8(bytes + i), vld1q_u8(expected + i)));
    return vmaxvq_u8(acc) != 0;
}

#define GET(k)                                                     \
    do {                                                           \
        const uint8_t *p = in + off[k];                            \
        lo = vld3_lane_u8(p,     lo, k);                           \
        hi = vld3_lane_u8(p + 3, hi, k);                            \
    } while (0)

int frombytes_asm(int16_t out[NTRUPLUS1152_N],
                  const uint8_t in[NTRUPLUS1152_POLYBYTES])
{
    const uint16x8_t q = vdupq_n_u16(Q);
    const uint16x8_t mask = vdupq_n_u16(0x0FFF);
    uint16x8_t bad = vdupq_n_u16(0);

    for (int g = 0; g < 36; g++) {
        const uint16_t *off = leaf_wire_offset[g];
        uint8x8x3_t lo = {{vdup_n_u8(0), vdup_n_u8(0), vdup_n_u8(0)}};
        uint8x8x3_t hi = lo;

        GET(0); GET(1); GET(2); GET(3); GET(4); GET(5); GET(6); GET(7);

        uint16x8_t b0 = vmovl_u8(lo.val[0]), b1 = vmovl_u8(lo.val[1]);
        uint16x8_t b2 = vmovl_u8(lo.val[2]), b3 = vmovl_u8(hi.val[0]);
        uint16x8_t b4 = vmovl_u8(hi.val[1]), b5 = vmovl_u8(hi.val[2]);

        uint16x8_t c0 = vandq_u16(vorrq_u16(b0, vshlq_n_u16(b1, 8)), mask);
        uint16x8_t c1 = vandq_u16(vorrq_u16(vshrq_n_u16(b1, 4),
                                            vshlq_n_u16(b2, 4)), mask);
        uint16x8_t c2 = vandq_u16(vorrq_u16(b3, vshlq_n_u16(b4, 8)), mask);
        uint16x8_t c3 = vandq_u16(vorrq_u16(vshrq_n_u16(b4, 4),
                                            vshlq_n_u16(b5, 4)), mask);

        bad = vorrq_u16(bad, vcgeq_u16(c0, q));
        bad = vorrq_u16(bad, vcgeq_u16(c1, q));
        bad = vorrq_u16(bad, vcgeq_u16(c2, q));
        bad = vorrq_u16(bad, vcgeq_u16(c3, q));

        vst1q_s16(out + 32 * g,      vreinterpretq_s16_u16(c0));
        vst1q_s16(out + 32 * g + 8,  vreinterpretq_s16_u16(c1));
        vst1q_s16(out + 32 * g + 16, vreinterpretq_s16_u16(c2));
        vst1q_s16(out + 32 * g + 24, vreinterpretq_s16_u16(c3));
    }
    return vmaxvq_u16(bad) != 0;
}
