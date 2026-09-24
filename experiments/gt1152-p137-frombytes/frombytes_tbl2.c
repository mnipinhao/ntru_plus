/* P137 candidate A: NTRU+1152 frombytes with the first transpose level and
 * the byte expansion done by two-register tbl.
 *
 * Lane k of pair p is the twelve-byte block at pair_wire[p][k]; coefficient i
 * of a block is the halfword at byte s_i = floor(3i/2), low twelve bits for
 * even i, top twelve for odd i.  Per pair:
 *
 *   - 8 loads, one per block;
 *   - 8 tbl2, one per (block 2j, block 2j+1) and half: 32-bit units
 *     [c_i(b2j) c_i(b2j+1)] for i = 0..3 or 4..7;
 *   - 8 trn1/trn2 .4s and 8 trn1/trn2 .2d: vector for c_i = lane k block k;
 *   - one and or ushr per vector, the same for every lane;
 *   - running umax, 8 stores.
 *
 * 40 SIMD ops a pair against the production decoder's 48 (24 trn + 16
 * unfold + 8 umax); two-register tbl costs one trn on both M2 and A76
 * (ubench_tbl.c).  The one block whose 16-byte load would pass byte 1728
 * (pair 17, lane 7, offset 1716) loads the 16 bytes ending there, with its
 * indices shifted by four. */
#include <arm_neon.h>
#include <stdint.h>
#include "codec_pairs.h"

#define Q 3457
#define POLYBYTES 1728

static const uint8_t idx_lo[16] __attribute__((aligned(16))) =
    {0, 1, 16, 17,  1, 2, 17, 18,  3, 4, 19, 20,  4, 5, 20, 21};
static const uint8_t idx_hi[16] __attribute__((aligned(16))) =
    {6, 7, 22, 23,  7, 8, 23, 24,  9, 10, 25, 26,  10, 11, 26, 27};
/* the second block loaded four bytes early */
static const uint8_t idx_lo_end[16] __attribute__((aligned(16))) =
    {0, 1, 20, 21,  1, 2, 21, 22,  3, 4, 23, 24,  4, 5, 24, 25};
static const uint8_t idx_hi_end[16] __attribute__((aligned(16))) =
    {6, 7, 26, 27,  7, 8, 27, 28,  9, 10, 29, 30,  10, 11, 30, 31};

#define U32(x) vreinterpretq_u32_u8(x)
#define U64(x) vreinterpretq_u64_u32(x)
#define U16(x) vreinterpretq_u16_u64(x)

static inline uint16x8_t decode_pair(int16_t *a, const uint8_t *in, const unsigned short *w,
                                     uint8x16_t il, uint8x16_t ih, uint8x16_t il7, uint8x16_t ih7,
                                     int last)
{
    uint8x16x2_t r[4];
    uint32x4_t xl[4], xh[4];
    int16_t *b = a + 32 * 9;

    for (int j = 0; j < 4; j++) {
        r[j].val[0] = vld1q_u8(in + w[2 * j]);
        r[j].val[1] = vld1q_u8(in + w[2 * j + 1]);
    }
    if (last) r[3].val[1] = vld1q_u8(in + POLYBYTES - 16);
    for (int j = 0; j < 4; j++) {
        int e = last && j == 3;
        xl[j] = U32(vqtbl2q_u8(r[j], e ? il7 : il));
        xh[j] = U32(vqtbl2q_u8(r[j], e ? ih7 : ih));
    }
    /* [c_i b0b1 | c_i b2b3 | c_i+2 b0b1 | c_i+2 b2b3] and the same for b4..b7 */
    uint64x2_t l02a = U64(vtrn1q_u32(xl[0], xl[1])), l13a = U64(vtrn2q_u32(xl[0], xl[1]));
    uint64x2_t l02b = U64(vtrn1q_u32(xl[2], xl[3])), l13b = U64(vtrn2q_u32(xl[2], xl[3]));
    uint64x2_t h02a = U64(vtrn1q_u32(xh[0], xh[1])), h13a = U64(vtrn2q_u32(xh[0], xh[1]));
    uint64x2_t h02b = U64(vtrn1q_u32(xh[2], xh[3])), h13b = U64(vtrn2q_u32(xh[2], xh[3]));
    const uint16x8_t m12 = vdupq_n_u16(0x0fff);
    uint16x8_t c0 = vandq_u16(U16(vtrn1q_u64(l02a, l02b)), m12);
    uint16x8_t c2 = vandq_u16(U16(vtrn2q_u64(l02a, l02b)), m12);
    uint16x8_t c1 = vshrq_n_u16(U16(vtrn1q_u64(l13a, l13b)), 4);
    uint16x8_t c3 = vshrq_n_u16(U16(vtrn2q_u64(l13a, l13b)), 4);
    uint16x8_t c4 = vandq_u16(U16(vtrn1q_u64(h02a, h02b)), m12);
    uint16x8_t c6 = vandq_u16(U16(vtrn2q_u64(h02a, h02b)), m12);
    uint16x8_t c5 = vshrq_n_u16(U16(vtrn1q_u64(h13a, h13b)), 4);
    uint16x8_t c7 = vshrq_n_u16(U16(vtrn2q_u64(h13a, h13b)), 4);

    vst1q_u16((uint16_t *)a,      c0); vst1q_u16((uint16_t *)a +  8, c1);
    vst1q_u16((uint16_t *)a + 16, c2); vst1q_u16((uint16_t *)a + 24, c3);
    vst1q_u16((uint16_t *)b,      c4); vst1q_u16((uint16_t *)b +  8, c5);
    vst1q_u16((uint16_t *)b + 16, c6); vst1q_u16((uint16_t *)b + 24, c7);
    return vmaxq_u16(vmaxq_u16(vmaxq_u16(c0, c1), vmaxq_u16(c2, c3)),
                     vmaxq_u16(vmaxq_u16(c4, c5), vmaxq_u16(c6, c7)));
}

int frombytes_tbl2(int16_t out[1152], const uint8_t in[POLYBYTES])
{
    const uint8x16_t il = vld1q_u8(idx_lo), ih = vld1q_u8(idx_hi);
    const uint8x16_t il7 = vld1q_u8(idx_lo_end), ih7 = vld1q_u8(idx_hi_end);
    uint16x8_t hi = vdupq_n_u16(0);

#pragma GCC unroll 17
    for (int p = 0; p < CODEC_PAIRS - 1; p++)
        hi = vmaxq_u16(hi, decode_pair(out + 32 * pair_group[p], in, pair_wire[p], il, ih, il7, ih7, 0));
    hi = vmaxq_u16(hi, decode_pair(out + 32 * pair_group[CODEC_PAIRS - 1], in, pair_wire[CODEC_PAIRS - 1],
                                   il, ih, il7, ih7, 1));
    return vmaxvq_u16(hi) >= Q;
}
