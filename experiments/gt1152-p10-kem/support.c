#include "poly.h"

#include <arm_neon.h>

/*
 * NTRU+1152 sampling and elementwise leaves, NEON.
 *
 * Replaces the plain C from gt1152-p10-kem, which the P12 profile measured at
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
 * The decode keeps the reference's exact failure semantics: every t4 is folded
 * into one accumulator, the test is on bits above bit 0, and the message is
 * masked afterwards.  No lane exits early and no branch depends on coefficient
 * data.
 */
int poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *a,
                     const uint8_t buf[NTRUPLUS_N / 4])
{
    const uint16x8_t mask = vld1q_u16(bitmask);
    const uint16x8_t one = vdupq_n_u16(1);
    uint16x8_t racc = vdupq_n_u16(0);
    uint32_t r;
    uint8_t m;

    for (int i = 0; i < NTRUPLUS_N / 8; i++) {
        uint16x8_t b1 = bits_of(buf[i], mask, one);
        uint16x8_t b2 = bits_of(buf[i + NTRUPLUS_N / 8], mask, one);
        uint16x8_t av = vreinterpretq_u16_s16(vld1q_s16(a->coeffs + 8 * i));
        uint16x8_t t4 = vaddq_u16(b2, av);

        racc = vorrq_u16(racc, t4);
        msg[i] = (uint8_t)vaddvq_u16(
            vmulq_u16(vandq_u16(veorq_u16(t4, b1), one), mask));
    }

    /* Horizontal OR of the accumulator, then the reference's r>>1 test. */
    uint64x2_t w = vreinterpretq_u64_u16(racc);
    uint64_t red = vgetq_lane_u64(w, 0) | vgetq_lane_u64(w, 1);
    red |= red >> 32;
    red |= red >> 16;
    r = (uint32_t)(red & 0xFFFFu);

    r = r >> 1;
    r = (-(uint32_t)r) >> 31;
    m = (uint8_t)(r - 1);

    for (int i = 0; i < NTRUPLUS_N / 8; i += 16)
        vst1q_u8(msg + i, vandq_u8(vld1q_u8(msg + i), vdupq_n_u8(m)));

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
