#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_basemul_rminus1_pair_u2(poly *r, const poly *a, const poly *b);
void poly_basemul_rminus1_pair_slothy(poly *r, const poly *a, const poly *b);
void rminus1_production_abi_safe(poly *r, const poly *a, const poly *b);
uint64_t rminus1_pair_u2_abi_sentinel(poly *r, const poly *a, const poly *b);
uint64_t rminus1_pair_slothy_abi_sentinel(poly *r, const poly *a,
                                         const poly *b);

static uint32_t rng_state = 0x4f12a9c3u;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    return rng_state;
}

static void fill_case(poly *a, poly *b, int test)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (test == 0) {
            a->coeffs[i] = 0;
            b->coeffs[i] = 0;
        } else if (test == 1) {
            a->coeffs[i] = (int16_t)(NTRUPLUS_Q - 1);
            b->coeffs[i] = (int16_t)(1 - NTRUPLUS_Q);
        } else if (test == 2) {
            a->coeffs[i] = (int16_t)((i & 1) ? 1728 : -1728);
            b->coeffs[i] = (int16_t)((i & 2) ? 1727 : -1727);
        } else {
            a->coeffs[i] = (int16_t)((int)(next_u32() % NTRUPLUS_Q) - 1728);
            b->coeffs[i] = (int16_t)((int)(next_u32() % NTRUPLUS_Q) - 1728);
        }
    }
}

static int compare(const poly *want, const poly *got)
{
    int mismatches = 0;
    for (int i = 0; i < NTRUPLUS_N; i++)
        mismatches += want->coeffs[i] != got->coeffs[i];
    return mismatches;
}

int main(void)
{
    poly a, b, production, u2, slothy, sentinel;
    uint64_t abi_mask = 0;
    int u2_mismatches = 0;
    int slothy_mismatches = 0;
    int sentinel_mismatches = 0;

    for (int test = 0; test < 1003; test++) {
        fill_case(&a, &b, test);
        rminus1_production_abi_safe(&production, &a, &b);
        poly_basemul_rminus1_pair_u2(&u2, &a, &b);
        poly_basemul_rminus1_pair_slothy(&slothy, &a, &b);
        u2_mismatches += compare(&production, &u2);
        slothy_mismatches += compare(&production, &slothy);

        abi_mask |= rminus1_pair_u2_abi_sentinel(&sentinel, &a, &b);
        sentinel_mismatches += compare(&production, &sentinel);
        abi_mask |= rminus1_pair_slothy_abi_sentinel(&sentinel, &a, &b);
        sentinel_mismatches += compare(&production, &sentinel);
    }

    printf("rminus1_pair_u2_mismatches=%d\n", u2_mismatches);
    printf("rminus1_pair_slothy_mismatches=%d\n", slothy_mismatches);
    printf("rminus1_pair_sentinel_mismatches=%d\n", sentinel_mismatches);
    printf("rminus1_pair_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    return u2_mismatches || slothy_mismatches || sentinel_mismatches ||
                   abi_mask
               ? 1
               : 0;
}
