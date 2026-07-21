#include <stddef.h>
#include <stdint.h>

#include "params.h"
#include "poly.h"

/*
 * KPQC block i uses lambda +/-zetas[96 + i/2].  Each value occurs exactly
 * once in gt_rowbitrev_lambda, so this table is the unique canonical-block to
 * GT-physical-block permutation.  Coefficients inside each quartic block keep
 * their X^0, X^1, X^2, X^3 order.
 */
const uint8_t gt_kpqc_block_to_gt_block[NTRUPLUS_N / 4] = {
     39,  36,  45,  42,  33,  30,  24,  27,   9,   6,   0,   3,  21,  18,  12,  15,
     87,  84,  93,  90,  81,  78,  72,  75,  57,  54,  48,  51,  69,  66,  60,  63,
     16,  19,  22,  25,  28,  31,  34,  37,  40,  43,  46,  49,  52,  55,  58,  61,
     88,  91,  94,   1,   4,   7,  10,  13,  76,  79,  82,  85,  70,  73,  67,  64,
     50,  53,  47,  44,  35,  32,  41,  38,  74,  77,  71,  68,  59,  56,  65,  62,
      2,   5,  95,  92,  83,  80,  89,  86,  26,  29,  23,  20,  11,   8,  17,  14,
    142, 145, 139, 136, 154, 157, 151, 148, 130, 133, 127, 124, 115, 112, 121, 118,
    178, 181, 175, 172, 163, 160, 169, 166, 106, 109, 103, 100, 187, 184,  97, 190,
    167, 164, 173, 170, 161, 158, 152, 155, 137, 134, 128, 131, 149, 146, 140, 143,
    119, 116, 125, 122, 113, 110, 104, 107, 185, 182, 176, 179, 101,  98, 188, 191,
    144, 147, 150, 153, 156, 159, 162, 165, 168, 171, 174, 177, 180, 183, 186, 189,
    120, 123, 126, 129, 132, 135, 138, 141, 108, 111, 114, 117, 102, 105,  99,  96,
};

static uint16_t canonical_u12(int16_t value)
{
    return (uint16_t)(value + ((value >> 15) & NTRUPLUS_Q));
}

void poly_tobytes_gt_canonical_ref(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a)
{
    for (size_t block = 0; block < NTRUPLUS_N / 4; block++) {
        const int16_t *src = &a->coeffs[4 * gt_kpqc_block_to_gt_block[block]];
        uint8_t *dst = &r[6 * block];
        const uint16_t t0 = canonical_u12(src[0]);
        const uint16_t t1 = canonical_u12(src[1]);
        const uint16_t t2 = canonical_u12(src[2]);
        const uint16_t t3 = canonical_u12(src[3]);

        dst[0] = (uint8_t)t0;
        dst[1] = (uint8_t)((t0 >> 8) | (t1 << 4));
        dst[2] = (uint8_t)(t1 >> 4);
        dst[3] = (uint8_t)t2;
        dst[4] = (uint8_t)((t2 >> 8) | (t3 << 4));
        dst[5] = (uint8_t)(t3 >> 4);
    }
}

void poly_frombytes_gt_canonical_ref(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES])
{
    for (size_t block = 0; block < NTRUPLUS_N / 4; block++) {
        int16_t *dst = &r->coeffs[4 * gt_kpqc_block_to_gt_block[block]];
        const uint8_t *src = &a[6 * block];

        dst[0] = (int16_t)((src[0] | ((uint16_t)src[1] << 8)) & 0x0fff);
        dst[1] = (int16_t)(((src[1] >> 4) | ((uint16_t)src[2] << 4)) & 0x0fff);
        dst[2] = (int16_t)((src[3] | ((uint16_t)src[4] << 8)) & 0x0fff);
        dst[3] = (int16_t)(((src[4] >> 4) | ((uint16_t)src[5] << 4)) & 0x0fff);
    }
}

/*
 * The production AArch64 build provides strong assembly definitions.  These
 * weak wrappers keep the portable oracle usable by host-side tests.
 */
__attribute__((weak))
void poly_tobytes_gt_canonical(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a)
{
    poly_tobytes_gt_canonical_ref(r, a);
}

#ifndef GT_PRODUCTION_USE_CANONICAL_UNPACK_U1
__attribute__((weak))
void poly_frombytes_gt_canonical(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES])
{
    poly_frombytes_gt_canonical_ref(r, a);
}
#endif
