#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

extern const uint8_t gt_kpqc_block_to_gt_block[NTRUPLUS_N / 4];
uint64_t gt_canonical_pack_abi_sentinel(uint8_t *out, const poly *in);
uint64_t gt_canonical_unpack_abi_sentinel(poly *out, const uint8_t *in);

struct guarded_bytes {
    uint8_t before[32];
    uint8_t data[NTRUPLUS_POLYBYTES];
    uint8_t after[32];
};

struct guarded_poly {
    uint8_t before[32];
    poly data;
    uint8_t after[32];
};

static uint16_t canonical_u12(int16_t value)
{
    return (uint16_t)(value + ((value >> 15) & NTRUPLUS_Q));
}

static void pack_u12(uint8_t *out, const uint16_t *values)
{
    for (size_t i = 0; i < NTRUPLUS_N / 2; i++) {
        const uint16_t a = values[2 * i] & 0x0fff;
        const uint16_t b = values[2 * i + 1] & 0x0fff;
        out[3 * i] = (uint8_t)a;
        out[3 * i + 1] = (uint8_t)((a >> 8) | (b << 4));
        out[3 * i + 2] = (uint8_t)(b >> 4);
    }
}

static unsigned guard_mismatches(const uint8_t *guard, size_t size, uint8_t want)
{
    unsigned mismatches = 0;
    for (size_t i = 0; i < size; i++)
        mismatches += guard[i] != want;
    return mismatches;
}

static void canonical_to_gt(poly *out, const int16_t *canonical)
{
    for (size_t block = 0; block < NTRUPLUS_N / 4; block++) {
        const size_t physical = gt_kpqc_block_to_gt_block[block];
        for (size_t lane = 0; lane < 4; lane++)
            out->coeffs[4 * physical + lane] = canonical[4 * block + lane];
    }
}

int main(void)
{
    struct guarded_bytes packed;
    struct guarded_poly decoded;
    int16_t canonical[NTRUPLUS_N];
    uint16_t u12[NTRUPLUS_N];
    uint8_t want[NTRUPLUS_POLYBYTES];
    poly input;
    uint64_t pack_abi = 0;
    uint64_t unpack_abi = 0;
    unsigned pack_mismatches = 0;
    unsigned unpack_mismatches = 0;
    unsigned guard_errors = 0;

    for (int value = -NTRUPLUS_Q; value < NTRUPLUS_Q; value++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++) {
            canonical[i] = (int16_t)value;
            u12[i] = canonical_u12((int16_t)value);
        }
        canonical_to_gt(&input, canonical);
        memset(&packed, 0xa5, sizeof packed);
        pack_u12(want, u12);
        poly_tobytes_gt_canonical(packed.data, &input);
        pack_mismatches += memcmp(want, packed.data, sizeof want) != 0;
        guard_errors += guard_mismatches(packed.before, sizeof packed.before, 0xa5);
        guard_errors += guard_mismatches(packed.after, sizeof packed.after, 0xa5);
    }

    for (size_t i = 0; i < NTRUPLUS_N; i++) {
        static const int16_t critical[] = {
            -NTRUPLUS_Q, -NTRUPLUS_Q + 1, -1737, -1728, -1,
            0, 1, 1728, 1737, NTRUPLUS_Q - 1
        };
        canonical[i] = critical[i % (sizeof critical / sizeof critical[0])];
        u12[i] = canonical_u12(canonical[i]);
    }
    canonical_to_gt(&input, canonical);
    memset(&packed, 0xa5, sizeof packed);
    pack_u12(want, u12);
    poly_tobytes_gt_canonical(packed.data, &input);
    pack_mismatches += memcmp(want, packed.data, sizeof want) != 0;
    guard_errors += guard_mismatches(packed.before, sizeof packed.before, 0xa5);
    guard_errors += guard_mismatches(packed.after, sizeof packed.after, 0xa5);

    for (unsigned value = 0; value < 4096; value++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            u12[i] = (uint16_t)value;
        pack_u12(packed.data, u12);
        memset(&decoded, 0x5a, sizeof decoded);
        poly_frombytes_gt_canonical(&decoded.data, packed.data);
        for (size_t block = 0; block < NTRUPLUS_N / 4; block++) {
            const size_t physical = gt_kpqc_block_to_gt_block[block];
            for (size_t lane = 0; lane < 4; lane++)
                unpack_mismatches +=
                    decoded.data.coeffs[4 * physical + lane] != (int16_t)value;
        }
        guard_errors += guard_mismatches(decoded.before, sizeof decoded.before, 0x5a);
        guard_errors += guard_mismatches(decoded.after, sizeof decoded.after, 0x5a);
    }

    memset(&packed, 0, sizeof packed);
    memset(&decoded, 0, sizeof decoded);
    pack_abi = gt_canonical_pack_abi_sentinel(packed.data, &input);
    unpack_abi = gt_canonical_unpack_abi_sentinel(&decoded.data, packed.data);

    printf("canonical_pack_boundary_mismatches=%u\n", pack_mismatches);
    printf("canonical_unpack_u12_mismatches=%u\n", unpack_mismatches);
    printf("canonical_pack_guard_mismatches=%u\n", guard_errors);
    printf("canonical_pack_abi_mask=0x%llx\n", (unsigned long long)pack_abi);
    printf("canonical_unpack_abi_mask=0x%llx\n", (unsigned long long)unpack_abi);
    return pack_mismatches == 0 && unpack_mismatches == 0 &&
                   guard_errors == 0 && pack_abi == 0 && unpack_abi == 0
               ? 0
               : 1;
}
