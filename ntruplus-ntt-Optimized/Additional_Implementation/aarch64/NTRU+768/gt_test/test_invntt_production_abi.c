#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123_len16(poly *r, const poly *a);
int poly_invntt_from_rminus1_production_abi_sentinel(poly *r,
                                                     const poly *a);

static uint32_t state = 0x71ab1a55u;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void fill_small(poly *a)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        a->coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
}

static int compare(const poly *a, const poly *b)
{
    int mismatches = 0;
    for (int i = 0; i < NTRUPLUS_N; i++)
        mismatches += a->coeffs[i] != b->coeffs[i];
    return mismatches;
}

int main(void)
{
    poly a, b, antt, bntt, product, production, oracle, sentinel;
    uint64_t abi_mask = 0;
    int mismatches = 0;

    for (int t = 0; t < 516; t++) {
        fill_small(&a);
        fill_small(&b);
        poly_ntt(&antt, &a);
        poly_ntt(&bntt, &b);
        poly_basemul_rminus1(&product, &antt, &bntt);
        poly_invntt_from_rminus1(&production, &product);
        poly_invntt_rminus1_lazy_twiddle1_stage123_len16(&oracle, &product);
        mismatches += compare(&production, &oracle);
        abi_mask |= (uint64_t)poly_invntt_from_rminus1_production_abi_sentinel(
            &sentinel, &product);
        mismatches += compare(&production, &sentinel);
    }

    printf("invntt_production_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    printf("invntt_production_mismatches=%d\n", mismatches);
    return abi_mask == 0 && mismatches == 0 ? 0 : 1;
}
