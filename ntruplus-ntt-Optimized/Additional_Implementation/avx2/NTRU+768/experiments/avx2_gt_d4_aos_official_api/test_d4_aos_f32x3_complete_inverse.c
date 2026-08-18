#include "d4_aos_f32x3_ref.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { LANES = 768, RANDOM_CASES = 10000, PRODUCT_CASES = 1000 };
static uint32_t random_word = 31;

static uint32_t next_random(void)
{
    random_word = 1664525U * random_word + 1013904223U;
    return random_word;
}

static int compare_output(
    const d4aos_coeff_poly *expected,
    const d4aos_coeff_poly *actual,
    const char *variant,
    const char *kind,
    int test_id)
{
    for (int index = 0; index < LANES; ++index) {
        if (expected->coeff[index] != actual->coeff[index] ||
            actual->coeff[index] < 0 || actual->coeff[index] >= D4AOS_Q) {
            fprintf(stderr,
                "inverse mismatch variant=%s kind=%s test=%d natural=%d "
                "expected=%d actual=%d\n",
                variant, kind, test_id, index,
                expected->coeff[index], actual->coeff[index]);
            return 0;
        }
    }
    return 1;
}

static int check_native(
    const d4aos_f32x3_state *input,
    const char *kind,
    int test_id,
    int check_alias)
{
    d4aos_coeff_poly expected;
    d4aos_coeff_poly y1;
    d4aos_coeff_poly y2;
    d4aos_f32x3_state post_l4;
    d4aos_f32x3_state post_dft3;
    d4aos_coeff_poly scalar_boundary;
    d4aos_f32x3_state alias;

    d4aos_f32x3_ref_inverse(
        &expected, (const d4aos_ntt_poly *)(const void *)input);
    gt_d4aos_f32x3_yang_invntt_avx2_asm(&y1, input);
    gt_d4aos_f32x3_yang_compact_invntt_avx2_asm(&y2, input);
    gt_d4aos_f32x3_invntt32_ct_merged_yang_asm(&post_l4, input);
    d4aos_f32x3_ref_inverse_dft3_barrett(&post_dft3, &post_l4);
    d4aos_f32x3_ref_inverse_terminal(&scalar_boundary, &post_dft3);

    if (!compare_output(&expected, &scalar_boundary, "scalar-terminal", kind, test_id) ||
        !compare_output(&expected, &y1, "Y1", kind, test_id) ||
        !compare_output(&expected, &y2, "Y2", kind, test_id)) {
        return 0;
    }

    if (check_alias) {
        alias = *input;
        gt_d4aos_f32x3_yang_invntt_avx2_asm(
            (d4aos_coeff_poly *)(void *)&alias, &alias);
        if (!compare_output(&expected, (const d4aos_coeff_poly *)(const void *)&alias,
                "Y1-alias", kind, test_id)) {
            return 0;
        }
        alias = *input;
        gt_d4aos_f32x3_yang_compact_invntt_avx2_asm(
            (d4aos_coeff_poly *)(void *)&alias, &alias);
        if (!compare_output(&expected, (const d4aos_coeff_poly *)(const void *)&alias,
                "Y2-alias", kind, test_id)) {
            return 0;
        }
    }
    return 1;
}

int main(void)
{
    d4aos_f32x3_state input;

    memset(&input, 0, sizeof(input));
    if (!check_native(&input, "zero", 0, 1)) {
        return 1;
    }
    for (int basis = 0; basis < LANES; ++basis) {
        memset(&input, 0, sizeof(input));
        input.lane[basis] = 1;
        if (!check_native(&input, "basis", basis, basis < 8)) {
            return 1;
        }
    }
    for (int lane = 0; lane < LANES; ++lane) {
        memset(&input, 0, sizeof(input));
        input.lane[lane] = D4AOS_Q;
        if (!check_native(&input, "q-representative", lane, lane < 8)) {
            return 1;
        }
    }
    for (int test_id = 0; test_id < RANDOM_CASES; ++test_id) {
        for (int lane = 0; lane < LANES; ++lane) {
            input.lane[lane] = (int16_t)(next_random() % D4AOS_Q);
        }
        if (!check_native(&input, "random", test_id, test_id < 16)) {
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
        if (!check_native((const d4aos_f32x3_state *)(const void *)&product,
                "forward-basemul", test_id, test_id < 8)) {
            return 1;
        }
    }
    puts("complete-inverse=passed Y1/Y2 basis=768 q=768 random=10000 "
         "products=1000 alias=passed range=passed natural-order=passed");
    return 0;
}
