#include "poly.h"

#define Q 3457

/*
 * NTRU+1152 elementwise and natural-order support leaves, transcribed from
 * Reference_Implementation/NTRU+1152/poly.c.
 *
 * These are order-agnostic (ref_poly_sub, ref_poly_triple) or natural-order
 * (ref_poly_cbd1, poly_sotp_*), and the natural-order ones sit either before the
 * forward transform or after the fused inverse, so the Good-Thomas layout does
 * not reach them.
 */

void ref_poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N / 4])
{
    for (int i = 0; i < NTRUPLUS_N / 8; i++) {
        uint8_t t1 = buf[i];
        uint8_t t2 = buf[i + NTRUPLUS_N / 8];

        for (int j = 0; j < 8; j++) {
            r->coeffs[8 * i + j] = (int16_t)((t1 & 0x1) - (t2 & 0x1));
            t1 >>= 1;
            t2 >>= 1;
        }
    }
}

void ref_poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N / 8],
                      const uint8_t buf[NTRUPLUS_N / 4])
{
    uint8_t tmp[NTRUPLUS_N / 4];

    for (int i = 0; i < NTRUPLUS_N / 8; i++)
        tmp[i] = (uint8_t)(buf[i] ^ msg[i]);
    for (int i = NTRUPLUS_N / 8; i < NTRUPLUS_N / 4; i++)
        tmp[i] = buf[i];

    ref_poly_cbd1(r, tmp);
}

int ref_poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *a,
                     const uint8_t buf[NTRUPLUS_N / 4])
{
    uint32_t r = 0;
    uint8_t mask;

    for (int i = 0; i < NTRUPLUS_N / 8; i++) {
        uint8_t t1 = buf[i];
        uint8_t t2 = buf[i + NTRUPLUS_N / 8];
        uint8_t t3 = 0;

        for (int j = 0; j < 8; j++) {
            uint16_t t4 = (uint16_t)(t2 & 0x1);

            t4 = (uint16_t)(t4 + a->coeffs[8 * i + j]);
            r |= t4;
            t4 = (uint16_t)((t4 ^ t1) & 0x1);
            t3 ^= (uint8_t)(t4 << j);
            t1 >>= 1;
            t2 >>= 1;
        }
        msg[i] = t3;
    }

    r = r >> 1;
    r = (-(uint32_t)r) >> 31;
    mask = (uint8_t)(r - 1);

    for (int i = 0; i < NTRUPLUS_N / 8; i++)
        msg[i] &= mask;

    return (int)r;
}

void ref_poly_sub(poly *r, const poly *a, const poly *b)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        r->coeffs[i] = (int16_t)(a->coeffs[i] - b->coeffs[i]);
}

void ref_poly_triple(poly *r, const poly *a)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        r->coeffs[i] = (int16_t)(3 * a->coeffs[i]);
}
