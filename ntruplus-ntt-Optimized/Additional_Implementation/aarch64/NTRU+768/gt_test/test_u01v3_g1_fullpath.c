#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

void poly_ntt_u01v3_g1(poly *r, const poly *a);
void poly_ntt_u01v3_g1_s2(poly *r, const poly *a);
int poly_ntt_u01v3_g1_abi_sentinel(poly *r, const poly *a);
int poly_ntt_u01v3_g1_s2_abi_sentinel(poly *r, const poly *a);

static uint32_t state = 0x9e3779b9u;

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
    poly input, want, g1, g1_inplace, combo, combo_inplace, sentinel;
    uint64_t g1_abi = 0, combo_abi = 0;
    int mismatches = 0;
    for (int t = 0; t < 260; t++) {
        fill_case(&input, t < 4 ? t : 4);
        poly_ntt(&want, &input);
        poly_ntt_u01v3_g1(&g1, &input);
        g1_inplace = input;
        poly_ntt_u01v3_g1(&g1_inplace, &g1_inplace);
        poly_ntt_u01v3_g1_s2(&combo, &input);
        combo_inplace = input;
        poly_ntt_u01v3_g1_s2(&combo_inplace, &combo_inplace);
        g1_abi |= (uint64_t)poly_ntt_u01v3_g1_abi_sentinel(&sentinel, &input);
        mismatches += compare("g1", &want, &g1);
        mismatches += compare("g1_inplace", &want, &g1_inplace);
        mismatches += compare("g1_s2", &want, &combo);
        mismatches += compare("g1_s2_inplace", &want, &combo_inplace);
        mismatches += compare("g1_sentinel", &want, &sentinel);
        combo_abi |= (uint64_t)poly_ntt_u01v3_g1_s2_abi_sentinel(&sentinel, &input);
        mismatches += compare("g1_s2_sentinel", &want, &sentinel);
    }
    printf("u01v3_g1_abi_mask=0x%llx\n", (unsigned long long)g1_abi);
    printf("u01v3_g1_s2_abi_mask=0x%llx\n", (unsigned long long)combo_abi);
    printf("u01v3_g1_fullpath_mismatches=%d\n", mismatches);
    return mismatches == 0 && g1_abi == 0 && combo_abi == 0 ? 0 : 1;
}
