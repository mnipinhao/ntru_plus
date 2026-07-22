#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

#define RANDOM_CASES 2000

typedef void (*full_pack_fn)(uint8_t *out, const poly *in);

void poly_tobytes_gt_canonical_p1(uint8_t *out, const poly *in);
void poly_tobytes_gt_canonical_p2(uint8_t *out, const poly *in);
void poly_tobytes_gt_canonical_p3(uint8_t *out, const poly *in);
void poly_tobytes_gt_canonical_cross_chunk(uint8_t *out, const poly *in);
void poly_tobytes_gt_canonical_compact(uint8_t *out, const poly *in);

uint64_t gt_canonical_full_p1_abi_sentinel(uint8_t *out, const poly *in);
uint64_t gt_canonical_full_p2_abi_sentinel(uint8_t *out, const poly *in);
uint64_t gt_canonical_full_p3_abi_sentinel(uint8_t *out, const poly *in);
uint64_t gt_canonical_full_cross_chunk_abi_sentinel(uint8_t *out,
                                                    const poly *in);
uint64_t gt_canonical_full_compact_abi_sentinel(uint8_t *out,
                                                const poly *in);

struct guarded_bytes {
    uint8_t before[32];
    uint8_t data[NTRUPLUS_POLYBYTES];
    uint8_t after[32];
};

struct candidate {
    const char *name;
    full_pack_fn pack;
    uint64_t (*abi)(uint8_t *, const poly *);
    unsigned mismatches;
    unsigned guard_mismatches;
    uint64_t abi_mask;
};

static uint32_t rng_state = 1;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    return rng_state;
}

static void check_case(struct candidate *candidates, size_t count,
                       const poly *input)
{
    uint8_t reference[NTRUPLUS_POLYBYTES];
    struct guarded_bytes got;

    poly_tobytes_gt_canonical(reference, input);
    for (size_t c = 0; c < count; c++) {
        memset(&got, 0xa5, sizeof got);
        candidates[c].pack(got.data, input);
        candidates[c].mismatches +=
            memcmp(reference, got.data, sizeof reference) != 0;
        for (size_t i = 0; i < sizeof got.before; i++)
            candidates[c].guard_mismatches += got.before[i] != 0xa5;
        for (size_t i = 0; i < sizeof got.after; i++)
            candidates[c].guard_mismatches += got.after[i] != 0xa5;
    }
}

int main(void)
{
    struct candidate candidates[] = {
        {"p1", poly_tobytes_gt_canonical_p1,
         gt_canonical_full_p1_abi_sentinel, 0, 0, 0},
        {"p2", poly_tobytes_gt_canonical_p2,
         gt_canonical_full_p2_abi_sentinel, 0, 0, 0},
        {"p3", poly_tobytes_gt_canonical_p3,
         gt_canonical_full_p3_abi_sentinel, 0, 0, 0},
        {"cross_chunk", poly_tobytes_gt_canonical_cross_chunk,
         gt_canonical_full_cross_chunk_abi_sentinel, 0, 0, 0},
        {"compact", poly_tobytes_gt_canonical_compact,
         gt_canonical_full_compact_abi_sentinel, 0, 0, 0},
    };
    const size_t candidate_count = sizeof candidates / sizeof candidates[0];
    struct guarded_bytes abi_out;
    poly input;
    int failed = 0;

    for (int value = -NTRUPLUS_Q; value < NTRUPLUS_Q; value++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            input.coeffs[i] = (int16_t)value;
        check_case(candidates, candidate_count, &input);
    }
    for (unsigned test = 0; test < RANDOM_CASES; test++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++)
            input.coeffs[i] =
                (int16_t)(next_u32() % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q;
        check_case(candidates, candidate_count, &input);
    }

    for (size_t c = 0; c < candidate_count; c++) {
        memset(&abi_out, 0, sizeof abi_out);
        candidates[c].abi_mask = candidates[c].abi(abi_out.data, &input);
        printf("canonical_full_%s_mismatches=%u\n", candidates[c].name,
               candidates[c].mismatches);
        printf("canonical_full_%s_guard_mismatches=%u\n", candidates[c].name,
               candidates[c].guard_mismatches);
        printf("canonical_full_%s_abi_mask=0x%llx\n", candidates[c].name,
               (unsigned long long)candidates[c].abi_mask);
        failed |= candidates[c].mismatches != 0;
        failed |= candidates[c].guard_mismatches != 0;
        failed |= candidates[c].abi_mask != 0;
    }
    return failed;
}
