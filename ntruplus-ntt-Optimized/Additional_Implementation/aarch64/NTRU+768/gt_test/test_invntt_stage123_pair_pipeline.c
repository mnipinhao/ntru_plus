#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_rminus1_stage123_pair_pipeline(poly *r, const poly *a);
int poly_invntt_rminus1_stage123_pair_pipeline_abi_sentinel(poly *r,
                                                            const poly *a);

static uint32_t state = 0x789abcdeu;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void fill_case(poly *a, int id)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (id == 0) {
            a->coeffs[i] = 0;
        } else if (id == 1) {
            a->coeffs[i] = (int16_t)((i % 3) - 1);
        } else if (id == 2) {
            a->coeffs[i] = (int16_t)((i & 1) ? 1 : -1);
        } else {
            a->coeffs[i] = (int16_t)((int)(next_u32() % 7u) - 3);
        }
    }
}

int main(void)
{
    poly a, b, antt, bntt, product, want, got, inplace;
    uint64_t abi_mask = 0;
    int mismatches = 0;

    for (int t = 0; t < 516; t++) {
        fill_case(&a, t < 3 ? t : 3);
        fill_case(&b, t < 3 ? 2 - t : 3);
        poly_ntt(&antt, &a);
        poly_ntt(&bntt, &b);
        poly_basemul_rminus1(&product, &antt, &bntt);
        poly_invntt_from_rminus1(&want, &product);
        poly_invntt_rminus1_stage123_pair_pipeline(&got, &product);
        abi_mask |= (uint64_t)
            poly_invntt_rminus1_stage123_pair_pipeline_abi_sentinel(&got,
                                                                    &product);
        inplace = product;
        poly_invntt_rminus1_stage123_pair_pipeline(&inplace, &inplace);

        for (int i = 0; i < NTRUPLUS_N; i++) {
            if (want.coeffs[i] != got.coeffs[i] ||
                want.coeffs[i] != inplace.coeffs[i]) {
                if (mismatches < 8) {
                    printf("mismatch[%d]: want=%d got=%d inplace=%d\n", i,
                           want.coeffs[i], got.coeffs[i], inplace.coeffs[i]);
                }
                mismatches++;
            }
        }
    }

    printf("invntt_stage123_pair_pipeline_mismatches=%d\n", mismatches);
    printf("invntt_stage123_pair_pipeline_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}
