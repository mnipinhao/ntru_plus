#if defined(__clang__)
#  define PAIR_UNROLL _Pragma("clang loop unroll(full)")
#elif defined(__GNUC__)
#  define PAIR_UNROLL _Pragma("GCC unroll 18")
#else
#  define PAIR_UNROLL
#endif
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

/*
 * The twelve wire bytes of a block are built without a table.  Four
 * coefficients become three halfwords with shift-insert alone,
 *
 *   h0 = c0 | c1 << 12,  h1 = c1 >> 4 | c2 << 8,  h2 = c2 >> 8 | c3 << 4,
 *
 * and the operands are lane-aligned before the transpose, where lane j of
 * vector i already holds coefficient i of block j.  This is the shape the
 * official serializer uses, and it costs ten instructions a pair against the
 * twenty-four the previous widen-and-`tbl` encoding needed on top of its
 * transpose.  P86 measured 129.2 -> 98.0 ns for the reduced path and
 * 92.9 -> 65.4 for the already-reduced one.
 */
/*
 * The decode runs the same fold backwards: three halfwords carry four
 * coefficients, and ushr/sli/and recover them, so the table lookup and the
 * per-lane shift vector the 24-bit form needed both disappear.
 */

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

/* ---- reduction to canonical [0, q) ---- */

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
 * Reduce and make canonical in four instructions a vector rather than five:
 * a rounding multiply-high and a multiply-subtract land in (-q, q), then a
 * sign mask and a second multiply-subtract add q back where it is negative.
 */
static inline int16x8_t reduce_canon(int16x8_t a)
{
    int16x8_t t = vqrdmulhq_n_s16(a, 9);          /* round(2^15/q) = 9 */
    a = vmlsq_n_s16(a, t, (int16_t)Q);
    int16x8_t m = vreinterpretq_s16_u16(vcltq_s16(a, vdupq_n_s16(0)));
    return vmlsq_n_s16(a, m, (int16_t)Q);
}

/* four lane-aligned coefficients -> three halfwords */
static inline void fold4(uint16x8_t o[3], int16x8_t c0, int16x8_t c1,
                         int16x8_t c2, int16x8_t c3)
{
    uint16x8_t u0 = vreinterpretq_u16_s16(c0), u1 = vreinterpretq_u16_s16(c1);
    uint16x8_t u2 = vreinterpretq_u16_s16(c2), u3 = vreinterpretq_u16_s16(c3);
    o[0] = vsliq_n_u16(u0, u1, 12);
    o[1] = vsliq_n_u16(vshrq_n_u16(u1, 4), u2, 8);
    o[2] = vsliq_n_u16(vshrq_n_u16(u2, 8), u3, 4);
}

/* and back again */
static inline void unfold4(int16x8_t *c0, int16x8_t *c1, int16x8_t *c2,
                           int16x8_t *c3, uint16x8_t h0, uint16x8_t h1,
                           uint16x8_t h2)
{
    const uint16x8_t m12 = vdupq_n_u16(0x0FFF);
    *c0 = vreinterpretq_s16_u16(vandq_u16(h0, m12));
    *c1 = vreinterpretq_s16_u16(vandq_u16(vsliq_n_u16(vshrq_n_u16(h0,12), h1, 4), m12));
    *c2 = vreinterpretq_s16_u16(vandq_u16(vsliq_n_u16(vshrq_n_u16(h1, 8), h2, 8), m12));
    *c3 = vreinterpretq_s16_u16(vshrq_n_u16(h2, 4));
}

/*
 * One pair's eight vectors, lane-aligned rather than transposed: vector i
 * holds coefficient i of every block, which is the order `fold4` consumes.
 * The four consecutive coefficients of a block live in v[0], v[4], v[1],
 * v[5] and the next four in v[2], v[6], v[3], v[7].
 */
static inline void load_pair(int16x8_t v[8], const int16_t *gt, int p, int full)
{
    const int16_t *a = gt + 32 * pair_group[p];
    const int16_t *b = a + 32 * 9;

    v[0] = vld1q_s16(a);      v[1] = vld1q_s16(a + 16);
    v[2] = vld1q_s16(b);      v[3] = vld1q_s16(b + 16);
    v[4] = vld1q_s16(a + 8);  v[5] = vld1q_s16(a + 24);
    v[6] = vld1q_s16(b + 8);  v[7] = vld1q_s16(b + 24);

    if (full) for (int i = 0; i < 8; i++) v[i] = reduce_canon(v[i]);
    else      for (int i = 0; i < 8; i++) v[i] = canonical(v[i]);
}

/* the six halfword streams of a pair, gathered so lane k is block k's bytes */
static inline void fold_pair(int16x8_t g[8], int16x8_t v[8])
{
    uint16x8_t e[6];
    fold4(e,     v[0], v[4], v[1], v[5]);
    fold4(e + 3, v[2], v[6], v[3], v[7]);
    for (int i = 0; i < 6; i++) g[i] = vreinterpretq_s16_u16(e[i]);
    g[6] = g[7] = vdupq_n_s16(0);
    transpose8(g);
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
#pragma GCC unroll 18
    for (int p = 0; p < CODEC_PAIRS; p++) {
        const unsigned short *w = pair_wire[p];
        int16x8_t v[8], g[8];

        load_pair(v, in, p, full);
        fold_pair(g, v);
        for (int k = 0; k < 8; k++)
            store12(out + w[k], vreinterpretq_u8_s16(g[k]));
    }
}

void u_tobytes_full_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                      const int16_t in[NTRUPLUS1152_N])
{
    tobytes(out, in, 1);
}

void u_tobytes_small_asm(uint8_t out[NTRUPLUS1152_POLYBYTES],
                       const int16_t in[NTRUPLUS1152_N])
{
    tobytes(out, in, 0);
}

/*
 * Compare without serializing to a buffer first: the twelve bytes are already
 * in a register when they are produced, so they are folded straight into the
 * accumulator.  Every block is visited and no branch depends on the data.
 */
int u_tobytes_compare_asm(const uint8_t expected[NTRUPLUS1152_POLYBYTES],
                        const int16_t in[NTRUPLUS1152_N])
{
    uint8x16_t acc = vdupq_n_u8(0);

    for (int p = 0; p < CODEC_PAIRS; p++) {
        const unsigned short *w = pair_wire[p];
        int16x8_t v[8], g[8];

        load_pair(v, in, p, 1);
        fold_pair(g, v);
        for (int k = 0; k < 8; k++)
            acc = vorrq_u8(acc, veorq_u8(vreinterpretq_u8_s16(g[k]),
                                         load12(expected + w[k])));
    }
    return vmaxvq_u8(acc) != 0;
}

/*
 * Decode.  Each block's twelve bytes are fetched whole and the eight blocks of
 * a pair are transposed so that lane k of the six halfword streams is block k;
 * `unfold4` then recovers the coefficients without a table.
 *
 * The plain 16-byte load reads four bytes past a block, which the transpose
 * discards.  Only the final block, at offset 1716, would read past the
 * 1728-byte input, so that one takes the two-load path.
 */
int u_frombytes_asm(int16_t out[NTRUPLUS1152_N],
                  const uint8_t in[NTRUPLUS1152_POLYBYTES])
{
    uint16x8_t hi = vdupq_n_u16(0);

    for (int p = 0; p < CODEC_PAIRS; p++) {
        const unsigned short *w = pair_wire[p];
        int16_t *a = out + 32 * pair_group[p];
        int16_t *b = a + 32 * 9;
        int16x8_t g[8], v[8];

        /* The wire offsets and the group index are compile-time constants once
         * p is; unrolled, the eight LDRH of pair_wire[p] and the LDRB of
         * pair_group[p] disappear and every address becomes an immediate.  The
         * short load is peeled so the k loop carries no test at all. */
        for (int k = 0; k < 7; k++)
            g[k] = vreinterpretq_s16_u8(vld1q_u8(in + w[k]));
        g[7] = (p == CODEC_PAIRS - 1)
             ? vreinterpretq_s16_u8(load12(in + w[7]))
             : vreinterpretq_s16_u8(vld1q_u8(in + w[7]));
        transpose8(g);

        unfold4(&v[0], &v[4], &v[1], &v[5], vreinterpretq_u16_s16(g[0]),
                vreinterpretq_u16_s16(g[1]), vreinterpretq_u16_s16(g[2]));
        unfold4(&v[2], &v[6], &v[3], &v[7], vreinterpretq_u16_s16(g[3]),
                vreinterpretq_u16_s16(g[4]), vreinterpretq_u16_s16(g[5]));

        /* One running maximum rather than a compare per lane: some coefficient
         * is out of range exactly when the maximum is.  Written as an explicit
         * tree, not a loop: as a loop gcc keeps v[] as a stack array and spills
         * all eight vectors, then reloads them one at a time to fold them, so
         * every coefficient made three trips through memory instead of one. */
        {
            uint16x8_t m0 = vmaxq_u16(vreinterpretq_u16_s16(v[0]),
                                      vreinterpretq_u16_s16(v[1]));
            uint16x8_t m1 = vmaxq_u16(vreinterpretq_u16_s16(v[2]),
                                      vreinterpretq_u16_s16(v[3]));
            uint16x8_t m2 = vmaxq_u16(vreinterpretq_u16_s16(v[4]),
                                      vreinterpretq_u16_s16(v[5]));
            uint16x8_t m3 = vmaxq_u16(vreinterpretq_u16_s16(v[6]),
                                      vreinterpretq_u16_s16(v[7]));
            hi = vmaxq_u16(hi, vmaxq_u16(vmaxq_u16(m0, m1), vmaxq_u16(m2, m3)));
        }

        vst1q_s16(a,      v[0]); vst1q_s16(a +  8, v[4]);
        vst1q_s16(a + 16, v[1]); vst1q_s16(a + 24, v[5]);
        vst1q_s16(b,      v[2]); vst1q_s16(b +  8, v[6]);
        vst1q_s16(b + 16, v[3]); vst1q_s16(b + 24, v[7]);
    }
    return vmaxvq_u16(hi) >= Q;
}
