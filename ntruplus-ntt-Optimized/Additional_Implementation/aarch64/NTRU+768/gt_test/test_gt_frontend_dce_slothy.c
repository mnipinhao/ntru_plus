#include <stdint.h>
#include <stdio.h>

#include "params.h"
#include "poly.h"

void poly_ntt_frontend_dce_slothy_fixed(poly *r, const poly *a);
void poly_ntt_frontend_dce_slothy_rename(poly *r, const poly *a);
int poly_ntt_frontend_dce_slothy_fixed_abi_sentinel(poly *r, const poly *a);
int poly_ntt_frontend_dce_slothy_rename_abi_sentinel(poly *r, const poly *a);

static uint32_t state = 0x18dce123u;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void fill_case(poly *a, int id)
{
    const int bound = 3 * (NTRUPLUS_Q - 1);
    const int span = 2 * bound + 1;

    for (int i = 0; i < NTRUPLUS_N; i++) {
        switch (id) {
        case 0: a->coeffs[i] = 0; break;
        case 1: a->coeffs[i] = (int16_t)(i % 17); break;
        case 2: a->coeffs[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 31)); break;
        case 3: a->coeffs[i] = (int16_t)(bound - (i % 61)); break;
        default:
            a->coeffs[i] = (int16_t)((int)(next_u32() % (uint32_t)span) - bound);
            break;
        }
    }
}

static int compare(const char *name, const poly *want, const poly *got)
{
    int mismatches = 0;

    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (want->coeffs[i] != got->coeffs[i]) {
            if (mismatches < 8)
                printf("%s mismatch[%d]: want=%d got=%d\n", name, i,
                       want->coeffs[i], got->coeffs[i]);
            mismatches++;
        }
    }
    return mismatches;
}

int main(void)
{
    poly input, want, fixed, rename, inplace, sentinel;
    uint64_t fixed_abi = 0;
    uint64_t rename_abi = 0;
    int mismatches = 0;

    for (int test = 0; test < 1000; test++) {
        fill_case(&input, test < 4 ? test : 4);
        poly_ntt(&want, &input);
        poly_ntt_frontend_dce_slothy_fixed(&fixed, &input);
        poly_ntt_frontend_dce_slothy_rename(&rename, &input);
        mismatches += compare("fixed", &want, &fixed);
        mismatches += compare("rename", &want, &rename);

        inplace = input;
        poly_ntt_frontend_dce_slothy_fixed(&inplace, &inplace);
        mismatches += compare("fixed_inplace", &want, &inplace);
        inplace = input;
        poly_ntt_frontend_dce_slothy_rename(&inplace, &inplace);
        mismatches += compare("rename_inplace", &want, &inplace);

        fixed_abi |= (uint64_t)poly_ntt_frontend_dce_slothy_fixed_abi_sentinel(
            &sentinel, &input);
        mismatches += compare("fixed_sentinel", &want, &sentinel);
        rename_abi |= (uint64_t)poly_ntt_frontend_dce_slothy_rename_abi_sentinel(
            &sentinel, &input);
        mismatches += compare("rename_sentinel", &want, &sentinel);
    }

    printf("frontend_dce_fixed_abi_mask=0x%llx\n",
           (unsigned long long)fixed_abi);
    printf("frontend_dce_rename_abi_mask=0x%llx\n",
           (unsigned long long)rename_abi);
    printf("frontend_dce_slothy_mismatches=%d\n", mismatches);
    return mismatches == 0 && fixed_abi == 0 && rename_abi == 0 ? 0 : 1;
}
