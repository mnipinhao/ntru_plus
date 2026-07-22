#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

#define RANDOM_CASES 4000
#define SENTINEL ((int16_t)0x5a5a)

typedef void (*unpack_fn)(poly *out, const uint8_t *in);

void poly_frombytes_gt_chunk0_u0(poly *out, const uint8_t *in);
void poly_frombytes_gt_chunk0_u1(poly *out, const uint8_t *in);
uint64_t gt_canonical_unpack_chunk_u0_abi_sentinel(poly *, const uint8_t *);
uint64_t gt_canonical_unpack_chunk_u1_abi_sentinel(poly *, const uint8_t *);

static const unsigned touched_byte_offsets[16] = {
    312, 288, 360, 336, 264, 240, 192, 216,
    72, 48, 0, 24, 168, 144, 96, 120,
};

struct guarded_poly {
    uint8_t before[32];
    poly value;
    uint8_t after[32];
};

struct candidate {
    const char *name;
    unpack_fn fn;
    uint64_t (*abi)(poly *, const uint8_t *);
    unsigned mismatches;
    unsigned untouched_mismatches;
    unsigned guard_mismatches;
    uint64_t abi_mask;
};

static uint64_t rng_state = 1;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (uint32_t)(rng_state >> 32);
}

static int is_touched(size_t coefficient)
{
    for (size_t block = 0; block < 16; block++) {
        const size_t first = touched_byte_offsets[block] / sizeof(int16_t);
        if (coefficient >= first && coefficient < first + 4)
            return 1;
    }
    return 0;
}

static void check_case(struct candidate *candidates, size_t count,
                       const uint8_t input[NTRUPLUS_POLYBYTES])
{
    poly reference;

    poly_frombytes_gt_canonical(&reference, input);
    for (size_t c = 0; c < count; c++) {
        struct guarded_poly got;
        memset(&got, 0xa5, sizeof got);
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            got.value.coeffs[i] = SENTINEL;
        candidates[c].fn(&got.value, input);
        for (size_t i = 0; i < NTRUPLUS_N; i++) {
            if (is_touched(i))
                candidates[c].mismatches +=
                    got.value.coeffs[i] != reference.coeffs[i];
            else
                candidates[c].untouched_mismatches +=
                    got.value.coeffs[i] != SENTINEL;
        }
        for (size_t i = 0; i < sizeof got.before; i++)
            candidates[c].guard_mismatches += got.before[i] != 0xa5;
        for (size_t i = 0; i < sizeof got.after; i++)
            candidates[c].guard_mismatches += got.after[i] != 0xa5;
    }
}

int main(void)
{
    struct candidate candidates[] = {
        {"u0", poly_frombytes_gt_chunk0_u0,
         gt_canonical_unpack_chunk_u0_abi_sentinel, 0, 0, 0, 0},
        {"u1", poly_frombytes_gt_chunk0_u1,
         gt_canonical_unpack_chunk_u1_abi_sentinel, 0, 0, 0, 0},
    };
    uint8_t input[NTRUPLUS_POLYBYTES];
    poly abi_output;
    int failed = 0;

    for (unsigned value = 0; value < 256; value++) {
        memset(input, value, sizeof input);
        check_case(candidates, 2, input);
    }
    for (unsigned test = 0; test < RANDOM_CASES; test++) {
        for (size_t i = 0; i < sizeof input; i++)
            input[i] = (uint8_t)next_u32();
        check_case(candidates, 2, input);
    }

    for (size_t c = 0; c < 2; c++) {
        memset(&abi_output, 0, sizeof abi_output);
        candidates[c].abi_mask = candidates[c].abi(&abi_output, input);
        printf("canonical_unpack_chunk_%s_mismatches=%u\n", candidates[c].name,
               candidates[c].mismatches);
        printf("canonical_unpack_chunk_%s_untouched_mismatches=%u\n",
               candidates[c].name, candidates[c].untouched_mismatches);
        printf("canonical_unpack_chunk_%s_guard_mismatches=%u\n",
               candidates[c].name, candidates[c].guard_mismatches);
        printf("canonical_unpack_chunk_%s_abi_mask=0x%llx\n",
               candidates[c].name, (unsigned long long)candidates[c].abi_mask);
        failed |= candidates[c].mismatches != 0;
        failed |= candidates[c].untouched_mismatches != 0;
        failed |= candidates[c].guard_mismatches != 0;
        failed |= candidates[c].abi_mask != 0;
    }
    return failed;
}
