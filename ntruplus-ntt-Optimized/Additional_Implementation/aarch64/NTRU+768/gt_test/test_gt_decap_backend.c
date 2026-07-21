#include <inttypes.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "gt/decap_backend.h"
#include "ntt.h"
#include "params.h"
#include "poly.h"

extern const uint8_t gt_kpqc_block_to_gt_block[NTRUPLUS_N / 4];

uint64_t gt_decap_verify_pointwise_abi_sentinel(poly *dst, const poly *a,
                                                 const poly *b);

static uint32_t state = 1;

static uint32_t next_u32(void)
{
    state = state * 1664525U + 1013904223U;
    return state;
}

static int16_t centered(uint32_t value)
{
    value %= NTRUPLUS_Q;
    return value > NTRUPLUS_Q / 2
               ? (int16_t)(value - NTRUPLUS_Q)
               : (int16_t)value;
}

static void decode_block(int16_t dst[4], const uint8_t src[6])
{
    dst[0] = (int16_t)((src[0] | ((uint16_t)src[1] << 8)) & 0x0fff);
    dst[1] = (int16_t)(((src[1] >> 4) | ((uint16_t)src[2] << 4)) & 0x0fff);
    dst[2] = (int16_t)((src[3] | ((uint16_t)src[4] << 8)) & 0x0fff);
    dst[3] = (int16_t)(((src[4] >> 4) | ((uint16_t)src[5] << 4)) & 0x0fff);
}

static uint16_t canonical_u12(int16_t value)
{
    return (uint16_t)(value + ((value >> 15) & NTRUPLUS_Q));
}

static void encode_block(uint8_t dst[6], const int16_t src[4])
{
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

static void scalar_oracle(uint8_t out[NTRUPLUS_POLYBYTES],
                          const poly *c_minus_m2,
                          const uint8_t hinv_bytes[NTRUPLUS_POLYBYTES])
{
    size_t canonical_block;

    for (canonical_block = 0; canonical_block < NTRUPLUS_N / 4;
         canonical_block++) {
        const size_t gt_block = gt_kpqc_block_to_gt_block[canonical_block];
        const size_t branch = gt_block / 96;
        const size_t physical = gt_block % 96;
        const int16_t *a = &c_minus_m2->coeffs[4 * gt_block];
        int16_t b[4];
        int16_t product[4];

        decode_block(b, &hinv_bytes[6 * canonical_block]);
        basemul(product, a, b, gt_rowbitrev_lambda[branch][physical]);
        encode_block(&out[6 * canonical_block], product);
    }
}

int main(void)
{
    uint8_t hinv_bytes[NTRUPLUS_POLYBYTES];
    uint8_t expected[NTRUPLUS_POLYBYTES];
    uint8_t actual[NTRUPLUS_POLYBYTES];
    poly c_minus_m2;
    poly hinv;
    poly qsoa_a;
    poly qsoa_b;
    poly qsoa_r;
    uint64_t abi_mask;
    unsigned mismatches = 0;
    unsigned test;

    for (test = 0; test < 1000; test++) {
        size_t i;

        for (i = 0; i < NTRUPLUS_N; i++) {
            c_minus_m2.coeffs[i] = centered(next_u32());
            hinv.coeffs[i] = centered(next_u32());
        }
        poly_tobytes_gt_canonical_ref(hinv_bytes, &hinv);
        scalar_oracle(expected, &c_minus_m2, hinv_bytes);
        gt_decap_verify_to_bytes(actual, &c_minus_m2, hinv_bytes);
        if (memcmp(expected, actual, sizeof expected) != 0) {
            size_t offset = 0;
            while (offset < sizeof expected &&
                   expected[offset] == actual[offset])
                offset++;
            fprintf(stderr,
                    "test=%u byte=%zu expected=%u actual=%u\n",
                    test, offset, expected[offset], actual[offset]);
            mismatches++;
            break;
        }
    }

    for (size_t i = 0; i < NTRUPLUS_N; i++) {
        qsoa_a.coeffs[i] = centered(next_u32());
        qsoa_b.coeffs[i] = centered(next_u32());
    }
    abi_mask = gt_decap_verify_pointwise_abi_sentinel(
        &qsoa_r, &qsoa_a, &qsoa_b);

    printf("decap_backend_mismatches=%u abi_mask=0x%" PRIx64 "\n",
           mismatches, abi_mask);
    return mismatches != 0 || abi_mask != 0;
}
