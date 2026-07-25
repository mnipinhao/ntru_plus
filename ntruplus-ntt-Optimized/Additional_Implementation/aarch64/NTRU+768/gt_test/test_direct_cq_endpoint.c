#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

typedef struct { int16_t coeffs[NTRUPLUS_N]; } bpq_poly;
typedef struct { int16_t coeffs[NTRUPLUS_N]; } cq_poly;

void gt_experiment_poly_ntt_to_cq(cq_poly *r, const poly *a);
uint64_t gt_experiment_poly_ntt_to_cq_abi_sentinel(cq_poly *r,
                                                    const poly *a);

static const uint8_t slot_for_k32[32] = {
    3, 7, 1, 0, 6, 2, 5, 4,
    8, 9, 10, 11, 12, 13, 14, 15,
    16, 17, 18, 19, 20, 21, 22, 23,
    24, 25, 26, 27, 28, 29, 30, 31,
};

static uint32_t rng_state = 0x43514e54u;

static uint32_t next_u32(void)
{
    rng_state = rng_state * 1664525u + 1013904223u;
    return rng_state;
}

static void fill_case(poly *a, int id)
{
    const int bound = 3 * (NTRUPLUS_Q - 1);
    const int span = 2 * bound + 1;

    for (int i = 0; i < NTRUPLUS_N; i++) {
        switch (id) {
        case 0: a->coeffs[i] = 0; break;
        case 1: a->coeffs[i] = (int16_t)((i % 17) - 8); break;
        case 2: a->coeffs[i] = (int16_t)(NTRUPLUS_Q - 1 - (i % 31)); break;
        case 3: a->coeffs[i] = (int16_t)(bound - (i % 61)); break;
        default:
            a->coeffs[i] =
                (int16_t)((int)(next_u32() % (uint32_t)span) - bound);
            break;
        }
    }
}

static void blockmajor_to_bpq(bpq_poly *out, const poly *in)
{
    for (int row = 0; row < 3; row++) {
        for (int k32 = 0; k32 < 32; k32++) {
            const int physical_j = (32 * row + 3 * k32) % 96;
            const int slot = 32 * row + slot_for_k32[k32];
            memcpy(&out->coeffs[8 * slot], &in->coeffs[4 * physical_j], 8);
            memcpy(&out->coeffs[8 * slot + 4],
                   &in->coeffs[384 + 4 * physical_j], 8);
        }
    }
}

static void bpq_to_cq(cq_poly *out, const bpq_poly *in)
{
    static const uint8_t cq_lane_quartic[8] = {
        0, 2, 4, 6, 1, 3, 5, 7,
    };

    for (int group = 0; group < 24; group++) {
        for (int lane = 0; lane < 8; lane++) {
            for (int coefficient = 0; coefficient < 4; coefficient++) {
                const int quartic = cq_lane_quartic[lane];
                out->coeffs[32 * group + 8 * coefficient + lane] =
                    in->coeffs[32 * group + 4 * quartic + coefficient];
            }
        }
    }
}

static int compare(const char *name, const cq_poly *want, const cq_poly *got)
{
    static int print_budget = 24;
    int mismatches = 0;
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (want->coeffs[i] != got->coeffs[i]) {
            if (print_budget > 0) {
                printf("%s mismatch[%d]: want=%d got=%d\n", name, i,
                       want->coeffs[i], got->coeffs[i]);
                print_budget--;
            }
            mismatches++;
        }
    }
    return mismatches;
}

int main(void)
{
    poly input, blockmajor, inplace;
    bpq_poly bpq;
    cq_poly want, got, got_inplace, sentinel;
    uint64_t abi_mask = 0;
    int mismatches = 0;

    for (int test = 0; test < 1000; test++) {
        fill_case(&input, test < 4 ? test : 4);
        poly_ntt(&blockmajor, &input);
        blockmajor_to_bpq(&bpq, &blockmajor);
        bpq_to_cq(&want, &bpq);

        gt_experiment_poly_ntt_to_cq(&got, &input);
        mismatches += compare("direct", &want, &got);

        inplace = input;
        gt_experiment_poly_ntt_to_cq(&got_inplace, &inplace);
        mismatches += compare("inplace", &want, &got_inplace);

        abi_mask |=
            gt_experiment_poly_ntt_to_cq_abi_sentinel(&sentinel, &input);
        mismatches += compare("sentinel", &want, &sentinel);
    }

    printf("direct_cq_endpoint_mismatches=%d\n", mismatches);
    printf("direct_cq_endpoint_abi_mask=0x%llx\n",
           (unsigned long long)abi_mask);
    return mismatches == 0 && abi_mask == 0 ? 0 : 1;
}
