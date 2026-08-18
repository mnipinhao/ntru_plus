#include "d4_aos_f32x3_ref.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { LANES = 768, RANDOM_CASES = 10000, PRODUCT_CASES = 1000 };
static uint32_t random_word = 23;

typedef struct {
    uint64_t before[4];
    d4aos_f32x3_state state;
    uint64_t after[4];
} guarded_state __attribute__((aligned(32)));

static uint32_t next_random(void)
{
    random_word = 1664525U * random_word + 1013904223U;
    return random_word;
}

static int check_boundary(
    const d4aos_f32x3_state *input,
    const char *kind,
    int test_id)
{
    d4aos_f32x3_state expected;
    guarded_state actual;
    d4aos_f32x3_state in_place;

    d4aos_f32x3_ref_inverse_dft3_barrett(&expected, input);
    for (int index = 0; index < 4; ++index) {
        actual.before[index] = UINT64_C(0x83a7f15c29d640be) ^ (uint64_t)index;
        actual.after[index] = UINT64_C(0x4d90b2e7613acf85) ^ (uint64_t)index;
    }
    gt_d4aos_f32x3_idft3_barrett_probe_asm(&actual.state, input);
    in_place = *input;
    gt_d4aos_f32x3_idft3_barrett_probe_asm(&in_place, &in_place);

    for (int index = 0; index < LANES; ++index) {
        if (actual.state.lane[index] != expected.lane[index] ||
            in_place.lane[index] != expected.lane[index] ||
            actual.state.lane[index] < 0 || actual.state.lane[index] > D4AOS_Q) {
            const int vector = index / 16;
            const int lane = index % 16;
            fprintf(stderr,
                "DFT3 mismatch kind=%s test=%d t=%d row=%d lane=%d branch=%d "
                "u=%d coefficient=%d expected=%d actual=%d omega=-886 qinv=13706 "
                "raw=D0[0,10368],D1D2[-5368,5368] reduced=[0,3457]\n",
                kind, test_id, vector % 16, vector / 16, lane, lane / 8,
                lane % 8 / 4, lane % 4, expected.lane[index],
                actual.state.lane[index]);
            return 0;
        }
    }
    for (int index = 0; index < 4; ++index) {
        if (actual.before[index] !=
                (UINT64_C(0x83a7f15c29d640be) ^ (uint64_t)index) ||
            actual.after[index] !=
                (UINT64_C(0x4d90b2e7613acf85) ^ (uint64_t)index)) {
            fprintf(stderr, "DFT3 canary mismatch kind=%s test=%d\n", kind, test_id);
            return 0;
        }
    }
    return 1;
}

int main(void)
{
    d4aos_f32x3_state input;

    memset(&input, 0, sizeof(input));
    if (!check_boundary(&input, "zero", 0)) {
        return 1;
    }
    for (int basis = 0; basis < LANES; ++basis) {
        memset(&input, 0, sizeof(input));
        input.lane[basis] = 1;
        if (!check_boundary(&input, "basis-monomial", basis)) {
            return 1;
        }
    }
    for (int boundary = 0; boundary < 3; ++boundary) {
        const int16_t value = (int16_t)(boundary == 0 ? 0 :
            (boundary == 1 ? 1 : D4AOS_Q - 1));
        for (int lane = 0; lane < LANES; ++lane) {
            input.lane[lane] = value;
        }
        if (!check_boundary(&input, "boundary", boundary)) {
            return 1;
        }
    }
    for (int test_id = 0; test_id < RANDOM_CASES; ++test_id) {
        for (int lane = 0; lane < LANES; ++lane) {
            input.lane[lane] = (int16_t)(next_random() % D4AOS_Q);
        }
        if (!check_boundary(&input, "random-post-l4", test_id)) {
            return 1;
        }
    }
    for (int test_id = 0; test_id < PRODUCT_CASES; ++test_id) {
        d4aos_coeff_poly left;
        d4aos_coeff_poly right;
        d4aos_ntt_poly left_ntt;
        d4aos_ntt_poly right_ntt;
        d4aos_ntt_poly product;

        for (int lane = 0; lane < LANES; ++lane) {
            left.coeff[lane] = (int16_t)(next_random() % D4AOS_Q);
            right.coeff[lane] = (int16_t)(next_random() % D4AOS_Q);
        }
        d4aos_f32x3_ref_forward(&left_ntt, &left);
        d4aos_f32x3_ref_forward(&right_ntt, &right);
        d4aos_ref_basemul(&product, &left_ntt, &right_ntt);
        gt_d4aos_f32x3_invntt32_ct_merged_yang_asm(
            &input, (const d4aos_f32x3_state *)(const void *)&product);
        if (!check_boundary(&input, "forward-basemul-post-l4", test_id)) {
            return 1;
        }
    }
    puts("compact-dft3=passed basis=768 random=10000 products=1000 "
         "range=passed scale=R0 inplace=passed");
    return 0;
}
