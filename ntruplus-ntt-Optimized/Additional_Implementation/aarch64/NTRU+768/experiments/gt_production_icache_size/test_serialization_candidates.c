#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"
#ifdef GT_SERIALIZATION_TEST_RELEASE_LAYOUT
#include "internal/keygen.h"
#define BASELINE_GENERIC_PACK poly_tobytes
#else
#include "gt/keygen_cq.h"
#define BASELINE_GENERIC_PACK poly_tobytes_gt_canonical
#endif

#define RANDOM_CASES 2000

void poly_tobytes_shared_compact_candidate(uint8_t *, const poly *);
void gt_keygen_tobytes_cq_shared_candidate(uint8_t *, const gt_cq_poly *);
uint64_t abi_poly_tobytes_shared_compact_candidate(void *, void *, void *, void *);
uint64_t abi_gt_keygen_tobytes_cq_shared_candidate(void *, void *, void *, void *);

struct guarded_bytes {
    uint8_t before[32];
    uint8_t data[NTRUPLUS_POLYBYTES];
    uint8_t after[32];
};

static uint32_t rng_state = 1;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    return rng_state;
}

static unsigned guard_mismatches(const struct guarded_bytes *value)
{
    unsigned mismatches = 0;
    for (size_t i = 0; i < sizeof value->before; i++)
        mismatches += value->before[i] != 0xa5;
    for (size_t i = 0; i < sizeof value->after; i++)
        mismatches += value->after[i] != 0xa5;
    return mismatches;
}

int main(void)
{
    poly generic_input;
    gt_cq_poly cq_input;
    uint8_t reference[NTRUPLUS_POLYBYTES];
    struct guarded_bytes candidate;
    unsigned generic_mismatches = 0;
    unsigned keygen_mismatches = 0;
    unsigned generic_guard = 0;
    unsigned keygen_guard = 0;

    for (int value = -NTRUPLUS_Q; value < NTRUPLUS_Q; value++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++) {
            generic_input.coeffs[i] = (int16_t)value;
            cq_input.storage.coeffs[i] = (int16_t)value;
        }
        BASELINE_GENERIC_PACK(reference, &generic_input);
        memset(&candidate, 0xa5, sizeof candidate);
        poly_tobytes_shared_compact_candidate(candidate.data, &generic_input);
        generic_mismatches +=
            memcmp(reference, candidate.data, sizeof reference) != 0;
        generic_guard += guard_mismatches(&candidate);

        gt_keygen_tobytes_cq(reference, &cq_input);
        memset(&candidate, 0xa5, sizeof candidate);
        gt_keygen_tobytes_cq_shared_candidate(candidate.data, &cq_input);
        keygen_mismatches +=
            memcmp(reference, candidate.data, sizeof reference) != 0;
        keygen_guard += guard_mismatches(&candidate);
    }

    for (unsigned test = 0; test < RANDOM_CASES; test++) {
        for (size_t i = 0; i < NTRUPLUS_N; i++) {
            int16_t value =
                (int16_t)(next_u32() % (2 * NTRUPLUS_Q)) - NTRUPLUS_Q;
            generic_input.coeffs[i] = value;
            cq_input.storage.coeffs[i] = value;
        }
        BASELINE_GENERIC_PACK(reference, &generic_input);
        memset(&candidate, 0xa5, sizeof candidate);
        poly_tobytes_shared_compact_candidate(candidate.data, &generic_input);
        generic_mismatches +=
            memcmp(reference, candidate.data, sizeof reference) != 0;
        generic_guard += guard_mismatches(&candidate);

        gt_keygen_tobytes_cq(reference, &cq_input);
        memset(&candidate, 0xa5, sizeof candidate);
        gt_keygen_tobytes_cq_shared_candidate(candidate.data, &cq_input);
        keygen_mismatches +=
            memcmp(reference, candidate.data, sizeof reference) != 0;
        keygen_guard += guard_mismatches(&candidate);
    }

    memset(&candidate, 0, sizeof candidate);
    uint64_t generic_abi = abi_poly_tobytes_shared_compact_candidate(
        candidate.data, &generic_input, 0, 0);
    uint64_t keygen_abi = abi_gt_keygen_tobytes_cq_shared_candidate(
        candidate.data, &cq_input, 0, 0);

    printf("shared_generic_pack_mismatches=%u\n", generic_mismatches);
    printf("shared_generic_pack_guard_mismatches=%u\n", generic_guard);
    printf("shared_generic_pack_abi_mask=0x%llx\n",
           (unsigned long long)generic_abi);
    printf("shared_keygen_pack_mismatches=%u\n", keygen_mismatches);
    printf("shared_keygen_pack_guard_mismatches=%u\n", keygen_guard);
    printf("shared_keygen_pack_abi_mask=0x%llx\n",
           (unsigned long long)keygen_abi);

    return generic_mismatches != 0 || keygen_mismatches != 0 ||
           generic_guard != 0 || keygen_guard != 0 ||
           generic_abi != 0 || keygen_abi != 0;
}
