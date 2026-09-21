#include "poly.h"

#include <arm_neon.h>

/*
 * NTRU+1152 sampling and elementwise leaves, NEON.
 *
 * Replaces the plain C from the milestone-1 tree, which the P12 profile measured at
 * 1246 cycles per poly_cbd1 against the official's 491, and 3277 per
 * poly_sotp_decode against 508.  After the codec work these were 32% of the
 * remaining gap.
 *
 * The old code was bit-serial with a carried dependency:
 *
 *     for (j = 0; j < 8; j++) { r[8*i+j] = (t1 & 1) - (t2 & 1);
 *                               t1 >>= 1; t2 >>= 1; }
 *
 * The obvious vectorisation -- extract bit plane j across sixteen bytes at once
 * -- is wrong for this layout: output coefficient 8i+j needs byte i's bits
 * consecutive, so bit planes would have to be interleaved eight ways, and NEON
 * stops at ST4.
 *
 * Broadcasting the other way avoids that entirely.  Duplicate one byte across
 * eight lanes and test it against {1,2,4,...,128}: that yields exactly the
 * eight consecutive output coefficients of byte i, with no interleave at all.
 */

static const uint16_t bitmask[8] = {1, 2, 4, 8, 16, 32, 64, 128};

/* One byte's eight bits, as eight 0/1 lanes in output order. */
static inline uint16x8_t bits_of(uint8_t b, uint16x8_t mask, uint16x8_t one)
{
    return vandq_u16(vtstq_u16(vdupq_n_u16(b), mask), one);
}

void poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N / 4])
{
    const uint16x8_t mask = vld1q_u16(bitmask);
    const uint16x8_t one = vdupq_n_u16(1);

    for (int i = 0; i < NTRUPLUS_N / 8; i++) {
        uint16x8_t s1 = bits_of(buf[i], mask, one);
        uint16x8_t s2 = bits_of(buf[i + NTRUPLUS_N / 8], mask, one);
        vst1q_s16(r->coeffs + 8 * i,
                  vsubq_s16(vreinterpretq_s16_u16(s1),
                            vreinterpretq_s16_u16(s2)));
    }
}

void poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N / 8],
                      const uint8_t buf[NTRUPLUS_N / 4])
{
    uint8_t tmp[NTRUPLUS_N / 4];
    int i = 0;

    for (; i + 16 <= NTRUPLUS_N / 8; i += 16)
        vst1q_u8(tmp + i, veorq_u8(vld1q_u8(buf + i), vld1q_u8(msg + i)));
    for (; i < NTRUPLUS_N / 8; i++)
        tmp[i] = (uint8_t)(buf[i] ^ msg[i]);
    for (; i + 16 <= NTRUPLUS_N / 4; i += 16)
        vst1q_u8(tmp + i, vld1q_u8(buf + i));
    for (; i < NTRUPLUS_N / 4; i++)
        tmp[i] = buf[i];

    poly_cbd1(r, tmp);
}

/*
 * NTRU+1152 poly_sotp_decode, two bits per coefficient.
 *
 * P21 measured the P13 version at 1343 cycles against the official's 508.  The
 * cause was one horizontal `vaddvq_u16` per output byte, 144 of them: it packed
 * eight 0/1 lanes into a byte by multiplying by {1,2,...,128} and reducing.
 *
 * The reference's message is just
 *
 *     msg[i] = packLSB(a[8i..8i+7]) ^ buf[144+i] ^ buf[i]
 *
 * so no bit-plane expansion is needed at all.  Following the official's cbd.s,
 * the coefficients are carried as a+1 in two-bit fields, four to a byte, which
 * lets a buf byte be consumed directly -- its even bits with `& 0x55` and its
 * odd bits with `>>1 & 0x55` -- and makes the failure test fall out of the same
 * packing: with f = a + 1 + b2 = t4 + 1, bit 0 of (f ^ (f >> 1)) is f0 ^ f1,
 * which is 1 exactly when f is 1 or 2, that is when t4 is 0 or 1.
 *
 * Coefficients outside {-1,0,1} would overflow a two-bit field.  They cannot be
 * silently wrong: the reference fails on any of them anyway, because t4 = a + b2
 * read as uint16 then exceeds 1 whichever way b2 falls.  A saturating narrow
 * keeps that property, and the running maximum below reports it, so this is the
 * reference's behaviour rather than a precondition.
 */
int poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *pa,
                     const uint8_t buf[NTRUPLUS_N / 4])
{
    const int16_t *a = pa->coeffs;
    const uint8x16_t m55 = vdupq_n_u8(0x55);
    const uint8x16_t one = vdupq_n_u8(1);
    uint8x16_t ok = vdupq_n_u8(0xFF);      /* AND-accumulated validity     */
    uint8x16_t hi = vdupq_n_u8(0);         /* max field, catches non-ternary */

    for (int g = 0; g < NTRUPLUS_N / 128; g++) {
        const int16_t *p = a + 128 * g;
        uint8x16_t w[8];

        /* 128 coefficients to 8 byte vectors, saturating, then a + 1. */
        for (int k = 0; k < 8; k++) {
            int8x16_t n = vcombine_s8(vqmovn_s16(vld1q_s16(p + 16 * k)),
                                      vqmovn_s16(vld1q_s16(p + 16 * k + 8)));
            w[k] = vaddq_u8(vreinterpretq_u8_s8(n), one);
            hi = vmaxq_u8(hi, w[k]);
        }

        /* Eight-way de-interleave: three uzp levels leave g[j][l] = a[8l+j]+1,
         * the plane index arriving bit-reversed, which the pairing below undoes. */
        uint8x16_t t0[8], t1[8];
        for (int k = 0; k < 4; k++) {
            t0[k]     = vuzp1q_u8(w[2 * k], w[2 * k + 1]);
            t0[k + 4] = vuzp2q_u8(w[2 * k], w[2 * k + 1]);
        }
        for (int k = 0; k < 2; k++) {
            t1[k]     = vuzp1q_u8(t0[2 * k],     t0[2 * k + 1]);
            t1[k + 2] = vuzp2q_u8(t0[2 * k],     t0[2 * k + 1]);
            t1[k + 4] = vuzp1q_u8(t0[2 * k + 4], t0[2 * k + 5]);
            t1[k + 6] = vuzp2q_u8(t0[2 * k + 4], t0[2 * k + 5]);
        }
        uint8x16_t q[8];
        for (int k = 0; k < 4; k++) {
            q[k]     = vuzp1q_u8(t1[2 * k], t1[2 * k + 1]);
            q[k + 4] = vuzp2q_u8(t1[2 * k], t1[2 * k + 1]);
        }
        /* The three uzp levels leave the planes in the order 0,2,1,3,4,6,5,7:
         * q[k][l] = a[8l + plane[k]] + 1.  Simulated symbolically rather than
         * assumed, so the pairing below is read off that order directly. */
        uint8x16_t ev = vorrq_u8(vorrq_u8(q[0], vshlq_n_u8(q[1], 2)),
                                 vorrq_u8(vshlq_n_u8(q[4], 4), vshlq_n_u8(q[5], 6)));
        uint8x16_t od = vorrq_u8(vorrq_u8(q[2], vshlq_n_u8(q[3], 2)),
                                 vorrq_u8(vshlq_n_u8(q[6], 4), vshlq_n_u8(q[7], 6)));

        uint8x16_t b1 = vld1q_u8(buf + 16 * g);
        uint8x16_t b2 = vld1q_u8(buf + NTRUPLUS_N / 8 + 16 * g);

        uint8x16_t fe = vaddq_u8(ev, vandq_u8(b2, m55));
        uint8x16_t fo = vaddq_u8(od, vandq_u8(vshrq_n_u8(b2, 1), m55));

        /* valid field <=> bit 0 of (f ^ f>>1) */
        uint8x16_t ve = veorq_u8(fe, vshrq_n_u8(fe, 1));
        uint8x16_t vo = veorq_u8(fo, vshrq_n_u8(fo, 1));
        ok = vandq_u8(ok, vandq_u8(ve, vo));

        /* message bit = t4 & 1 = complement of field bit 0 */
        uint8x16_t bits = veorq_u8(vandq_u8(fe, m55),
                                   vshlq_n_u8(vandq_u8(fo, m55), 1));
        vst1q_u8(msg + 16 * g, veorq_u8(vmvnq_u8(bits), b1));
    }

    uint32_t bad = vmaxvq_u8(vbicq_u8(m55, ok)) | (vmaxvq_u8(hi) > 2);
    uint32_t r = bad != 0;
    uint8x16_t mask = vdupq_n_u8((uint8_t)(r - 1));

    for (int i = 0; i < NTRUPLUS_N / 8; i += 16)
        vst1q_u8(msg + i, vandq_u8(vld1q_u8(msg + i), mask));

    return (int)r;
}

void poly_sub(poly *r, const poly *a, const poly *b)
{
    for (int i = 0; i < NTRUPLUS_N; i += 8)
        vst1q_s16(r->coeffs + i, vsubq_s16(vld1q_s16(a->coeffs + i),
                                           vld1q_s16(b->coeffs + i)));
}

void poly_triple(poly *r, const poly *a)
{
    for (int i = 0; i < NTRUPLUS_N; i += 8)
        vst1q_s16(r->coeffs + i, vmulq_n_s16(vld1q_s16(a->coeffs + i), 3));
}
