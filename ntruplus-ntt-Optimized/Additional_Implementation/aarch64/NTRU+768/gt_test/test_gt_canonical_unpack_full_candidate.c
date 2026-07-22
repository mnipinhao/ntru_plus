#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

#define RANDOM_CASES 4000

void poly_frombytes_gt_canonical_u1(poly *out, const uint8_t *in);
uint64_t gt_canonical_unpack_full_u1_abi_sentinel(poly *, const uint8_t *);

struct guarded_poly {
    uint8_t before[32];
    poly value;
    uint8_t after[32];
};

static uint64_t rng_state = 1;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(rng_state >> 32);
}

static void check_case(const uint8_t input[NTRUPLUS_POLYBYTES],
                       unsigned *mismatches, unsigned *guard_mismatches)
{
    poly reference;
    struct guarded_poly got;

    poly_frombytes_gt_canonical(&reference, input);
    memset(&got, 0xa5, sizeof got);
    poly_frombytes_gt_canonical_u1(&got.value, input);
    *mismatches += memcmp(&got.value, &reference, sizeof reference) != 0;
    for (size_t i = 0; i < sizeof got.before; i++)
        *guard_mismatches += got.before[i] != 0xa5;
    for (size_t i = 0; i < sizeof got.after; i++)
        *guard_mismatches += got.after[i] != 0xa5;
}

int main(void)
{
    uint8_t input[NTRUPLUS_POLYBYTES];
    poly abi_output;
    unsigned mismatches = 0;
    unsigned guard_mismatches = 0;
    uint64_t abi_mask;

    for (unsigned value = 0; value < 256; value++) {
        memset(input, value, sizeof input);
        check_case(input, &mismatches, &guard_mismatches);
    }
    for (unsigned test = 0; test < RANDOM_CASES; test++) {
        for (size_t i = 0; i < sizeof input; i++)
            input[i] = (uint8_t)next_u32();
        check_case(input, &mismatches, &guard_mismatches);
    }
    memset(&abi_output, 0, sizeof abi_output);
    abi_mask = gt_canonical_unpack_full_u1_abi_sentinel(&abi_output, input);
    printf("canonical_unpack_full_u1_mismatches=%u\n", mismatches);
    printf("canonical_unpack_full_u1_guard_mismatches=%u\n", guard_mismatches);
    printf("canonical_unpack_full_u1_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    return mismatches != 0 || guard_mismatches != 0 || abi_mask != 0;
}
