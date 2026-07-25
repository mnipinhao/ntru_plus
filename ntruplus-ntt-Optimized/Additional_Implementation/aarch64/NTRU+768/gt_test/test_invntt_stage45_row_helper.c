#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_rminus1_stage45_row_helper(poly *r, const poly *a);
int poly_invntt_rminus1_stage45_row_helper_abi_sentinel(poly *r,
                                                        const poly *a);

static uint32_t state = 0x45a11e5du;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void fill_case(poly *a, int id)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        switch (id) {
        case 0:
            a->coeffs[i] = 0;
            break;
        case 1:
            a->coeffs[i] = (int16_t)((i % 3) - 1);
            break;
        case 2:
            a->coeffs[i] = (int16_t)((i & 1) ? 1 : -1);
            break;
        default:
            a->coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
            break;
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
    poly a, b, antt, bntt, product, production, candidate, inplace, sentinel;
    uint64_t abi_mask = 0;
    int mismatches = 0;

    for (int t = 0; t < 1024; t++) {
        fill_case(&a, t < 3 ? t : 3);
        fill_case(&b, t < 3 ? 2 - t : 3);
        poly_ntt(&antt, &a);
        poly_ntt(&bntt, &b);
        poly_basemul_rminus1(&product, &antt, &bntt);

        poly_invntt_from_rminus1(&production, &product);
        poly_invntt_rminus1_stage45_row_helper(&candidate, &product);
        inplace = product;
        poly_invntt_rminus1_stage45_row_helper(&inplace, &inplace);
        abi_mask |=
            (uint64_t)poly_invntt_rminus1_stage45_row_helper_abi_sentinel(
                &sentinel, &product);

        mismatches += compare(&production, &candidate);
        mismatches += compare(&production, &inplace);
        mismatches += compare(&production, &sentinel);
    }

    printf("invntt_stage45_row_helper_mismatches=%d\n", mismatches);
    printf("invntt_stage45_row_helper_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}
