#include "pack_asm.h"
#include "codec_pairs.h"

#include <arm_neon.h>

#define Q 3457
#define BARRETT_V 19412        /* ((1<<26) + Q/2) / Q */

/*
 * NTRU+1152 canonical serialization, permutation performed in registers.
 *
 * Replaces the P12 codec, which the P17 profile measured at 2185 cycles
 * per frombytes against the official's 509, and 2368 per tobytes against 1147.
 * P17 named the cause: that codec materialises a natural-order uint16 array and
 * runs two passes over memory, where NTRU+864's serializer -- the component
 * that made 864 beat its official before any hash work -- never materialises
 * natural order at all.  It permutes inside the register file with trn/uzp/tbl
 * and stores wire bytes directly.
 *
 * The tiling that makes this possible at 1152 is measured in generate_pairs.py
 * and holds exhaustively: the 36 Good-Thomas groups pair up as (g, g+9), and
 * for every pair and every lane k the two leaves are consecutive, the first
 * even.  A leaf is four coefficients, so a pair's lane is eight consecutive
 * natural coefficients, which the 12-bit format stores as exactly twelve
 * contiguous bytes at 6*m.  With m even those 144 blocks tile the 1728-byte
 * output with no overlap and no gap, so every store is independent.
 *
 * Per pair: eight loads, an 8x8 transpose (24 trn), and eight twelve-byte
 * stores.  No scratch array and no second pass.
 *
 * Degree-4 is what makes this cheaper than 864's version rather than dearer.
 * 864's three-coefficient leaves are 4.5 wire bytes, never aligned, which is
 * why its pack_full_top needs 54 tbl and 24 ext to route them; four
 * coefficients land on a 12-byte boundary every time.
 */

/* Wire order inside one lane's twelve bytes: the four 24-bit little-endian
 * pairs (c0|c1<<12), (c2|c3<<12), (c4|c5<<12), (c6|c7<<12). */
static const uint8_t pack_idx[16] = {
    0, 1, 2,  4, 5, 6,  8, 9, 10,  12, 13, 14,  255, 255, 255, 255
};
/*
 * The decode reads each twelve-byte block as eight 16-bit windows rather than
 * four 24-bit ones.  Lanes 0..3 take bytes (3j, 3j+1), whose low twelve bits
 * are the even coefficient; lanes 4..7 take bytes (3m+1, 3m+2), which hold the
 * odd coefficient shifted up by four.  One `ushl` with a per-lane count then
 * fixes both halves at once, so the separate `ushr` and `uzp1` the 24-bit form
 * needed collapse into a single instruction.
 */
static const uint8_t unpack_idx[16] = {
    0, 1,  3, 4,  6, 7,  9, 10,    1, 2,  4, 5,  7, 8,  10, 11
};
static const int16_t unpack_shift[8] = {0, 0, 0, 0, -4, -4, -4, -4};

/*
 * The 8x8 int16 transpose, three trn levels.  A transpose is an involution, so
 * the same network serves both directions.
 */
#define S32(x) vreinterpretq_s32_s16(x)
#define S16_32(x) vreinterpretq_s16_s32(x)
#define S64(x) vreinterpretq_s64_s16(x)
#define S16_64(x) vreinterpretq_s16_s64(x)

static inline void transpose8(int16x8_t v[8])
{
    int16x8_t a0 = vtrn1q_s16(v[0], v[1]), a1 = vtrn2q_s16(v[0], v[1]);
    int16x8_t a2 = vtrn1q_s16(v[2], v[3]), a3 = vtrn2q_s16(v[2], v[3]);
    int16x8_t a4 = vtrn1q_s16(v[4], v[5]), a5 = vtrn2q_s16(v[4], v[5]);
    int16x8_t a6 = vtrn1q_s16(v[6], v[7]), a7 = vtrn2q_s16(v[6], v[7]);

    int16x8_t b0 = S16_32(vtrn1q_s32(S32(a0), S32(a2)));
    int16x8_t b2 = S16_32(vtrn2q_s32(S32(a0), S32(a2)));
    int16x8_t b1 = S16_32(vtrn1q_s32(S32(a1), S32(a3)));
    int16x8_t b3 = S16_32(vtrn2q_s32(S32(a1), S32(a3)));
    int16x8_t b4 = S16_32(vtrn1q_s32(S32(a4), S32(a6)));
    int16x8_t b6 = S16_32(vtrn2q_s32(S32(a4), S32(a6)));
    int16x8_t b5 = S16_32(vtrn1q_s32(S32(a5), S32(a7)));
    int16x8_t b7 = S16_32(vtrn2q_s32(S32(a5), S32(a7)));

    v[0] = S16_64(vtrn1q_s64(S64(b0), S64(b4)));
    v[4] = S16_64(vtrn2q_s64(S64(b0), S64(b4)));
    v[1] = S16_64(vtrn1q_s64(S64(b1), S64(b5)));
    v[5] = S16_64(vtrn2q_s64(S64(b1), S64(b5)));
    v[2] = S16_64(vtrn1q_s64(S64(b2), S64(b6)));
    v[6] = S16_64(vtrn2q_s64(S64(b2), S64(b6)));
    v[3] = S16_64(vtrn1q_s64(S64(b3), S64(b7)));
    v[7] = S16_64(vtrn2q_s64(S64(b3), S64(b7)));
}

/* ---- reduction to canonical [0, q), unchanged from P12 ---- */

static inline int16x8_t barrett_reduce(int16x8_t a)
{
    int16x8_t t = vqdmulhq_n_s16(a, BARRETT_V);
    t = vrshrq_n_s16(t, 11);
    return vmlsq_n_s16(a, t, (int16_t)Q);
}

/*
 * Canonical in two instructions rather than three.  Every input is in (-q, q),
 * so a + q is in (0, 2q) and never wraps 16 bits; read unsigned, a negative a
 * is huge and a + q is the small correct one, a non-negative a is the small one
 * itself, so an unsigned minimum picks the right representative either way.
 */
static inline int16x8_t canonical(int16x8_t a)
{
    uint16x8_t u = vreinterpretq_u16_s16(a);
    return vreinterpretq_s16_u16(vminq_u16(u, vaddq_u16(u, vdupq_n_u16(Q))));
}

/*
 * Load one pair's eight vectors already ordered for the transpose: the rows
 * must be (c0, c2) of the first group, (c0, c2) of the second, then (c1, c3)
 * of each, so that a transposed lane reads out as the four even coefficients
 * followed by the four odd ones -- exactly the operand order the 12-bit
 * encoding wants, at no cost.
 */
static inline void load_pair(int16x8_t v[8], const int16_t *gt, int p, int full)
{
    const int16_t *a = gt + 32 * pair_group[p];
    const int16_t *b = a + 32 * 9;

    v[0] = vld1q_s16(a);      v[1] = vld1q_s16(a + 16);
    v[2] = vld1q_s16(b);      v[3] = vld1q_s16(b + 16);
    v[4] = vld1q_s16(a + 8);  v[5] = vld1q_s16(a + 24);
    v[6] = vld1q_s16(b + 8);  v[7] = vld1q_s16(b + 24);

    if (full)
        for (int i = 0; i < 8; i++) v[i] = barrett_reduce(v[i]);
    for (int i = 0; i < 8; i++) v[i] = canonical(v[i]);
    transpose8(v);
}

/* One lane's eight canonical coefficients as twelve wire bytes in lanes 0..11. */
static inline uint8x16_t encode_lane(int16x8_t u, uint8x16_t idx)
{
    uint16x8_t x = vreinterpretq_u16_s16(u);
    uint32x4_t y = vmovl_u16(vget_low_u16(x));       /* even coefficients   */
    y = vmlal_high_n_u16(y, x, 4096);                /* += odd << 12        */
    return vqtbl1q_u8(vreinterpretq_u8_u32(y), idx);
}

static inline void store12(uint8_t *out, uint8x16_t b)
{
    vst1_u8(out, vget_low_u8(b));
    vst1q_lane_u32((uint32_t *)(void *)(out + 8), vreinterpretq_u32_u8(b), 2);
}

static inline uint8x16_t load12(const uint8_t *in)
{
    uint8x16_t b = vcombine_u8(vld1_u8(in), vdup_n_u8(0));
    return vreinterpretq_u8_u32(
        vld1q_lane_u32((const uint32_t *)(const void *)(in + 8),
                       vreinterpretq_u32_u8(b), 2));
}

/* ---- public entry points ---- */

static inline void tobytes(uint8_t *out, const int16_t *in, int full)
{
    const uint8x16_t idx = vld1q_u8(pack_idx);

#pragma GCC unroll 18
    for (int p = 0; p < CODEC_PAIRS; p++) {
        const unsigned short *w = pair_wire[p];
        int16x8_t v[8];

        load_pair(v, in, p, full);
        for (int k = 0; k < 8; k++)
            store12(out + w[k], encode_lane(v[k], idx));
    }
}

void tobytes_full_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                      const int16_t in[NTRUPLUS1152_N])
{
    tobytes(out, in, 1);
}

void tobytes_small_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                       const int16_t in[NTRUPLUS1152_N])
{
    tobytes(out, in, 0);
}

/*
 * Compare without serializing to a buffer first: the twelve bytes are already
 * in a register when they are produced, so they are folded straight into the
 * accumulator.  Every block is visited and no branch depends on the data.
 */
int tobytes_compare_asm(const uint8_t expected[NTRUPLUS1152_POLYBYTES],
                        const int16_t in[NTRUPLUS1152_N])
{
    const uint8x16_t idx = vld1q_u8(pack_idx);
    uint8x16_t acc = vdupq_n_u8(0);

    for (int p = 0; p < CODEC_PAIRS; p++) {
        const unsigned short *w = pair_wire[p];
        int16x8_t v[8];

        load_pair(v, in, p, 1);
        for (int k = 0; k < 8; k++)
            acc = vorrq_u8(acc, veorq_u8(encode_lane(v[k], idx),
                                         load12(expected + w[k])));
    }
    return vmaxvq_u8(acc) != 0;
}

/*
 * One pair's eight twelve-byte blocks, decoded into transposed lanes.
 *
 * `safe` is a compile-time constant at both call sites.  With it clear the
 * block is fetched with a plain 16-byte load, four bytes wider than the block:
 * the table lookup only ever reads bytes 0..11, so the extra bytes are ignored,
 * and halving the loads is worth it.  Only the very last block, at offset 1716,
 * would read past the 1728-byte input; it lives at lane 7 of pair 17, so the
 * final pair takes the two-load path instead.
 */
static inline void unpack_pair(int16x8_t v[8], const uint8_t *in,
                               const unsigned short *w, uint8x16_t idx,
                               uint16x8_t *hi, int safe)
{
    const uint16x8_t m12 = vdupq_n_u16(0x0FFF);
    const int16x8_t sh = vld1q_s16(unpack_shift);

    for (int k = 0; k < 8; k++) {
        uint8x16_t raw = safe ? load12(in + w[k]) : vld1q_u8(in + w[k]);
        uint16x8_t win = vreinterpretq_u16_u8(vqtbl1q_u8(raw, idx));
        uint16x8_t u = vandq_u16(vshlq_u16(win, sh), m12);

        /* One running maximum rather than a compare and an or per lane: some
         * coefficient is out of range exactly when the maximum is. */
        *hi = vmaxq_u16(*hi, u);
        v[k] = vreinterpretq_s16_u16(u);
    }
    transpose8(v);
}

int frombytes_asm(int16_t out[NTRUPLUS1152_N],
                  const uint8_t in[NTRUPLUS1152_POLYBYTES])
{
    const uint8x16_t idx = vld1q_u8(unpack_idx);
    uint16x8_t hi = vdupq_n_u16(0);

    for (int p = 0; p < CODEC_PAIRS; p++) {
        int16_t *a = out + 32 * pair_group[p];
        int16_t *b = a + 32 * 9;
        int16x8_t v[8];

        if (p == CODEC_PAIRS - 1) unpack_pair(v, in, pair_wire[p], idx, &hi, 1);
        else                      unpack_pair(v, in, pair_wire[p], idx, &hi, 0);

        vst1q_s16(a,      v[0]); vst1q_s16(a +  8, v[4]);
        vst1q_s16(a + 16, v[1]); vst1q_s16(a + 24, v[5]);
        vst1q_s16(b,      v[2]); vst1q_s16(b +  8, v[6]);
        vst1q_s16(b + 16, v[3]); vst1q_s16(b + 24, v[7]);
    }
    return vmaxvq_u16(hi) >= Q;
}
