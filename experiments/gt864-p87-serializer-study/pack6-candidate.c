/*
 * NTRU+864 serialization in six-vector groups.
 *
 * The existing packers route every twelve-byte block through `tbl`, because at
 * 864 a block's eight coefficients sit at *two* lanes of eight vectors and no
 * transpose can deliver one.  The same-lane run is six wire positions, nine
 * bytes, and that is the unit this uses instead.
 *
 * Eighteen groups of six vectors: lane j of a group is six consecutive wire
 * coefficients for every j, so 48 loaded coefficients yield eight runs with
 * nothing discarded, and the 144 runs tile the 1296-byte output exactly.
 *
 * Six coefficients are 72 bits, four and a half halfwords, which is what made
 * this look impossible.  They fold into *five* halfwords in seven instructions
 * and only nine bytes are stored; the fifth halfword's high byte is zero by
 * construction and is simply not written.
 */
#include <stdint.h>
#include <arm_neon.h>
#include "pack6.h"

#define Q 3457

/* Official's reduction: round-multiply-high and multiply-subtract to land in
 * (-q, q), then a sign mask and a second multiply-subtract to make it
 * canonical.  Four instructions a vector. */
static inline int16x8_t reduce_canon(int16x8_t a)
{
    int16x8_t t = vqrdmulhq_n_s16(a, 9);          /* round(2^15/q) = 9 */
    a = vmlsq_n_s16(a, t, (int16_t)Q);
    int16x8_t m = vreinterpretq_s16_u16(vcltq_s16(a, vdupq_n_s16(0)));
    return vmlsq_n_s16(a, m, (int16_t)Q);
}

/* Already inside (-q, q): a + q is in (0, 2q) and never wraps sixteen bits, so
 * an unsigned minimum picks the canonical representative in two instructions. */
static inline int16x8_t canon_only(int16x8_t a)
{
    uint16x8_t u = vreinterpretq_u16_s16(a);
    return vreinterpretq_s16_u16(vminq_u16(u, vaddq_u16(u, vdupq_n_u16(Q))));
}

/* six lane-aligned coefficients -> five halfwords, nine bytes of which are live */
static inline void fold6(uint16x8_t h[5], const int16x8_t c[6])
{
    uint16x8_t u0 = vreinterpretq_u16_s16(c[0]), u1 = vreinterpretq_u16_s16(c[1]);
    uint16x8_t u2 = vreinterpretq_u16_s16(c[2]), u3 = vreinterpretq_u16_s16(c[3]);
    uint16x8_t u4 = vreinterpretq_u16_s16(c[4]), u5 = vreinterpretq_u16_s16(c[5]);
    h[0] = vsliq_n_u16(u0, u1, 12);
    h[1] = vsliq_n_u16(vshrq_n_u16(u1, 4), u2, 8);
    h[2] = vsliq_n_u16(vshrq_n_u16(u2, 8), u3, 4);
    h[3] = vsliq_n_u16(u4, u5, 12);
    h[4] = vshrq_n_u16(u5, 4);            /* < 256, so its high byte is zero */
}

#define S32(x) vreinterpretq_s32_s16(x)
#define S16_32(x) vreinterpretq_s16_s32(x)
#define S64(x) vreinterpretq_s64_s16(x)
#define S16_64(x) vreinterpretq_s16_s64(x)

/* the usual three-level network; two rows are idle because only five of the
 * eight streams carry anything */
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

static inline void store9(uint8_t *out, uint8x16_t b)
{
    vst1_u8(out, vget_low_u8(b));
    vst1q_lane_u8(out + 8, b, 8);
}

static inline void group(int16x8_t g[8], const int16_t *in, int p, int full)
{
    const unsigned char *vi = pack6_vec[p];
    int16x8_t c[6];
    for (int i = 0; i < 6; i++) {
        int16x8_t x = vld1q_s16(in + 8 * vi[i]);
        c[i] = full ? reduce_canon(x) : canon_only(x);
    }
    uint16x8_t h[5];
    fold6(h, c);
    for (int i = 0; i < 5; i++) g[i] = vreinterpretq_s16_u16(h[i]);
    g[5] = g[6] = g[7] = vdupq_n_s16(0);
    transpose8(g);
}

static inline void tobytes6(uint8_t *out, const int16_t *in, int full)
{
#pragma GCC unroll 18
    for (int p = 0; p < PACK6_GROUPS; p++) {
        const unsigned short *w = pack6_off[p];
        int16x8_t g[8];
        group(g, in, p, full);
        for (int k = 0; k < 8; k++)
            store9(out + w[k], vreinterpretq_u8_s16(g[k]));
    }
}

void p87_tobytes_full(uint8_t *out, const int16_t *in)  { tobytes6(out, in, 1); }
void p87_tobytes_small(uint8_t *out, const int16_t *in) { tobytes6(out, in, 0); }

/*
 * Compare without materialising.  The nine live bytes of a run are fetched with
 * one 16-byte load and the seven bytes past them are masked off; `g[k]` is
 * already zero there, the fifth halfword's high byte included.  A byte load and
 * lane insert would be two instructions and a general-purpose round trip.
 *
 * The final run ends exactly at 1296, so it takes an eight-byte load and a
 * lane insert rather than reading past the buffer.
 */
static const uint8_t mask9[16] = {255,255,255,255,255,255,255,255,255,0,0,0,0,0,0,0};

int p87_tobytes_compare(const uint8_t *expected, const int16_t *in)
{
    const uint8x16_t m = vld1q_u8(mask9);
    uint8x16_t acc = vdupq_n_u8(0);

    for (int p = 0; p < PACK6_GROUPS; p++) {
        const unsigned short *w = pack6_off[p];
        int16x8_t g[8];
        group(g, in, p, 1);
        for (int k = 0; k < 8; k++) {
            uint8x16_t e;
            if (w[k] + 16 <= 1296) {
                e = vld1q_u8(expected + w[k]);
            } else {
                e = vcombine_u8(vld1_u8(expected + w[k]), vdup_n_u8(0));
                e = vsetq_lane_u8(expected[w[k] + 8], e, 8);
            }
            acc = vorrq_u8(acc, vandq_u8(veorq_u8(vreinterpretq_u8_s16(g[k]), e), m));
        }
    }
    return vmaxvq_u8(acc) != 0;
}
