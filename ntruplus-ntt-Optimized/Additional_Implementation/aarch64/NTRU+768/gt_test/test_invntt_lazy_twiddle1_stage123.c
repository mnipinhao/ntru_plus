#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123(poly *r, const poly *a);
int poly_invntt_rminus1_lazy_twiddle1_stage123_abi_sentinel(poly *r,
                                                            const poly *a);
void poly_invntt_rminus1_lazy_twiddle1_stage123_len16(poly *r, const poly *a);
int poly_invntt_rminus1_lazy_twiddle1_stage123_len16_abi_sentinel(
    poly *r, const poly *a);
void poly_invntt_rminus1_post_branchfold_slothy(poly *r, const poly *a);
int poly_invntt_rminus1_post_branchfold_slothy_abi_sentinel(poly *r,
                                                            const poly *a);

static uint32_t state = 0x1a2b3c4du;

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

static int compare(const char *name, const poly *want, const poly *got)
{
    int mismatches = 0;
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (want->coeffs[i] != got->coeffs[i]) {
            if (mismatches < 8) {
                printf("%s mismatch[%d]: want=%d got=%d\n", name, i,
                       want->coeffs[i], got->coeffs[i]);
            }
            mismatches++;
        }
    }
    return mismatches;
}

int main(void)
{
    poly a, b, antt, bntt, product, want, got, inplace, len16, post, sentinel;
    uint64_t abi_mask = 0, len16_abi_mask = 0, post_abi_mask = 0;
    int mismatches = 0;

    for (int t = 0; t < 516; t++) {
        fill_case(&a, t < 3 ? t : 3);
        fill_case(&b, t < 3 ? 2 - t : 3);
        poly_ntt(&antt, &a);
        poly_ntt(&bntt, &b);
        poly_basemul_rminus1(&product, &antt, &bntt);

        poly_invntt_from_rminus1(&want, &product);
        poly_invntt_rminus1_lazy_twiddle1_stage123(&got, &product);
        inplace = product;
        poly_invntt_rminus1_lazy_twiddle1_stage123(&inplace, &inplace);
        abi_mask |= (uint64_t)
            poly_invntt_rminus1_lazy_twiddle1_stage123_abi_sentinel(
                &sentinel, &product);

        mismatches += compare("lazy", &want, &got);
        mismatches += compare("lazy_inplace", &want, &inplace);
        mismatches += compare("lazy_sentinel", &want, &sentinel);
        poly_invntt_rminus1_lazy_twiddle1_stage123_len16(&len16, &product);
        mismatches += compare("lazy_len16", &want, &len16);
        len16_abi_mask |= (uint64_t)
            poly_invntt_rminus1_lazy_twiddle1_stage123_len16_abi_sentinel(
                &sentinel, &product);
        mismatches += compare("lazy_len16_sentinel", &want, &sentinel);
        poly_invntt_rminus1_post_branchfold_slothy(&post, &product);
        mismatches += compare("post_slothy", &want, &post);
        post_abi_mask |= (uint64_t)
            poly_invntt_rminus1_post_branchfold_slothy_abi_sentinel(
                &sentinel, &product);
        mismatches += compare("post_slothy_sentinel", &want, &sentinel);
    }

    printf("invntt_lazy_twiddle1_stage123_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    printf("invntt_lazy_twiddle1_stage123_mismatches=%d\n", mismatches);
    printf("invntt_lazy_twiddle1_stage123_len16_abi_mask=0x%llx\n",
           (unsigned long long)len16_abi_mask);
    printf("invntt_post_branchfold_slothy_abi_mask=0x%llx\n",
           (unsigned long long)post_abi_mask);
    return mismatches == 0 && abi_mask == 0 && len16_abi_mask == 0 &&
                   post_abi_mask == 0
               ? 0
               : 1;
}
