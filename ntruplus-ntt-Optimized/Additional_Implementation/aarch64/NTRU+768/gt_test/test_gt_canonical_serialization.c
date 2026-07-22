#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

extern const uint8_t gt_kpqc_block_to_gt_block[NTRUPLUS_N / 4];

static uint16_t canonical_u12(int16_t value)
{
    return (uint16_t)(value + ((value >> 15) & NTRUPLUS_Q));
}

static void pack_standard(uint8_t out[NTRUPLUS_POLYBYTES],
                          const int16_t values[NTRUPLUS_N])
{
    for (size_t i = 0; i < NTRUPLUS_N / 2; i++) {
        const uint16_t t0 = canonical_u12(values[2 * i]);
        const uint16_t t1 = canonical_u12(values[2 * i + 1]);

        out[3 * i] = (uint8_t)t0;
        out[3 * i + 1] = (uint8_t)((t0 >> 8) | (t1 << 4));
        out[3 * i + 2] = (uint8_t)(t1 >> 4);
    }
}

static uint32_t next_random(uint32_t *state)
{
    *state = *state * 1664525u + 1013904223u;
    return *state;
}

int main(void)
{
    uint8_t seen[NTRUPLUS_N / 4] = {0};
    uint8_t want[NTRUPLUS_POLYBYTES];
    uint8_t got[NTRUPLUS_POLYBYTES];
    uint8_t reference[NTRUPLUS_POLYBYTES];
    int16_t canonical[NTRUPLUS_N];
    poly input;
    poly decoded;
    poly decoded_reference;
    uint32_t state = 1;
    unsigned mismatches = 0;
    unsigned pack_mismatches = 0;
    unsigned unpack_mismatches = 0;
    size_t first_pack_byte = NTRUPLUS_POLYBYTES;
    size_t first_unpack_coeff = NTRUPLUS_N;

    for (size_t block = 0; block < NTRUPLUS_N / 4; block++) {
        const unsigned physical = gt_kpqc_block_to_gt_block[block];

        mismatches += physical >= NTRUPLUS_N / 4;
        if (physical < NTRUPLUS_N / 4) {
            mismatches += seen[physical] != 0;
            seen[physical] = 1;
        }
    }

    for (unsigned trial = 0; trial < 1000; trial++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++) {
            const int16_t value =
                (int16_t)(next_random(&state) % NTRUPLUS_Q) - NTRUPLUS_Q / 2;
            canonical[i] = value;
        }
        for (size_t block = 0; block < NTRUPLUS_N / 4; block++) {
            const unsigned physical = gt_kpqc_block_to_gt_block[block];

            for (size_t lane = 0; lane < 4; lane++)
                input.coeffs[4 * physical + lane] = canonical[4 * block + lane];
        }

        pack_standard(want, canonical);
        poly_tobytes_gt_canonical_ref(reference, &input);
        poly_tobytes_gt_canonical(got, &input);
        if (trial == 0 && memcmp(reference, got, sizeof got) != 0) {
            printf("first_pack_reference:");
            for (size_t i = 0; i < 24; i++)
                printf(" %02x", reference[i]);
            printf("\nfirst_pack_asm:");
            for (size_t i = 0; i < 24; i++)
                printf(" %02x", got[i]);
            printf("\n");
        }
        mismatches += memcmp(want, reference, sizeof reference) != 0;
        for (size_t i = 0; i < sizeof got; i++) {
            if (reference[i] != got[i]) {
                pack_mismatches++;
                if (first_pack_byte == NTRUPLUS_POLYBYTES)
                    first_pack_byte = i;
            }
        }

        memset(&decoded, 0, sizeof decoded);
        memset(&decoded_reference, 0, sizeof decoded_reference);
        poly_frombytes_gt_canonical(&decoded, got);
        poly_frombytes_gt_canonical_ref(&decoded_reference, got);
        if (trial == 0 &&
            memcmp(&decoded, &decoded_reference, sizeof decoded) != 0) {
            printf("first_unpack_reference:");
            for (size_t i = 0; i < 16; i++)
                printf(" %04x", (uint16_t)decoded_reference.coeffs[i]);
            printf("\nfirst_unpack_asm:");
            for (size_t i = 0; i < 16; i++)
                printf(" %04x", (uint16_t)decoded.coeffs[i]);
            printf("\n");
        }
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            if (decoded.coeffs[i] != decoded_reference.coeffs[i]) {
                unpack_mismatches++;
                if (first_unpack_coeff == NTRUPLUS_N)
                    first_unpack_coeff = i;
            }
    }

    mismatches += pack_mismatches + unpack_mismatches;
    printf("gt_canonical_pack_mismatches=%u\n", pack_mismatches);
    if (pack_mismatches != 0)
        printf("gt_canonical_pack_first_byte=%zu\n", first_pack_byte);
    printf("gt_canonical_unpack_mismatches=%u\n", unpack_mismatches);
    if (unpack_mismatches != 0)
        printf("gt_canonical_unpack_first_coeff=%zu\n", first_unpack_coeff);
    printf("gt_canonical_serialization_mismatches=%u\n", mismatches);
    return mismatches == 0 ? 0 : 1;
}
