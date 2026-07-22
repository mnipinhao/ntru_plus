#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_basemul_add_encap_direct32_q31_tobytes_contract(
    poly *r, const poly *a, const poly *b, const poly *c);
void poly_basemul_add_encap_direct32_q31_pair_u2(
    poly *r, const poly *a, const poly *b, const poly *c);
void poly_basemul_add_encap_direct32_q31_pair_slothy(
    poly *r, const poly *a, const poly *b, const poly *c);
uint64_t q31_pair_slothy_abi_sentinel(
    poly *r, const poly *a, const poly *b, const poly *c);

static uint32_t state = 0x13579bdfu;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void fill(poly *p, int test)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (test == 0)
            p->coeffs[i] = 0;
        else if (test == 1)
            p->coeffs[i] = (int16_t)((i & 1) ? 1728 : -1728);
        else
            p->coeffs[i] = (int16_t)((int)(next_u32() % 3457u) - 1728);
    }
}

int main(void)
{
    poly a, b, c, want, u2, slothy;
    int mismatches = 0;
    uint64_t abi_mask;

    for (int test = 0; test < 1002; test++) {
        fill(&a, test);
        fill(&b, test);
        fill(&c, test);
        poly_basemul_add_encap_direct32_q31_tobytes_contract(
            &want, &a, &b, &c);
        poly_basemul_add_encap_direct32_q31_pair_u2(&u2, &a, &b, &c);
        poly_basemul_add_encap_direct32_q31_pair_slothy(
            &slothy, &a, &b, &c);
        for (int i = 0; i < NTRUPLUS_N; i++) {
            if (want.coeffs[i] != u2.coeffs[i] ||
                want.coeffs[i] != slothy.coeffs[i]) {
                if (mismatches < 8)
                    printf("mismatch[%d]: want=%d u2=%d slothy=%d\n", i,
                           want.coeffs[i], u2.coeffs[i], slothy.coeffs[i]);
                mismatches++;
            }
        }
    }
    fill(&a, 2);
    fill(&b, 2);
    fill(&c, 2);
    abi_mask = q31_pair_slothy_abi_sentinel(&slothy, &a, &b, &c);
    printf("q31_pair_pipeline_mismatches=%d\n", mismatches);
    printf("q31_pair_slothy_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}
