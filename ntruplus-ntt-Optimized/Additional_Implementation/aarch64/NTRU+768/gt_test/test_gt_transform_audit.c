#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#ifndef GT_AUDIT_RANDOM_CASES
#define GT_AUDIT_RANDOM_CASES 10000
#endif

#ifndef GT_AUDIT_SPARSE_SCHOOLBOOK_CASES
#define GT_AUDIT_SPARSE_SCHOOLBOOK_CASES 10000
#endif

#ifndef GT_AUDIT_DENSE_SCHOOLBOOK_CASES
#define GT_AUDIT_DENSE_SCHOOLBOOK_CASES 256
#endif

void poly_basemul_gt_ref(poly *r, const poly *a, const poly *b);
uint64_t gt_audit_poly_ntt_abi_sentinel(poly *r, const poly *a);
uint64_t gt_audit_poly_invntt_abi_sentinel(poly *r, const poly *a);
uint64_t gt_audit_poly_invntt_rminus1_abi_sentinel(poly *r,
                                                   const poly *a);

static uint32_t random_state = 0x6d2b79f5u;
static uint64_t semantic_mismatch_count;
static uint64_t representation_mismatch_count;
static uint64_t representative_range_violation_count;
static int normal_inverse_max_abs;
static int rminus_inverse_max_abs;
static unsigned printed_mismatches;

static uint32_t next_u32(void)
{
    random_state = random_state * 1664525u + 1013904223u;
    return random_state;
}

static int16_t centered_modq(int64_t value)
{
    int64_t reduced = value % NTRUPLUS_Q;

    if (reduced < 0)
        reduced += NTRUPLUS_Q;
    if (reduced > NTRUPLUS_Q / 2)
        reduced -= NTRUPLUS_Q;
    return (int16_t)reduced;
}

static int same_modq(int16_t a, int16_t b)
{
    return centered_modq((int32_t)a - b) == 0;
}

static void note_mismatch(const char *label, unsigned case_idx, int coeff_idx,
                          int16_t got, int16_t want, int semantic)
{
    if (semantic)
        semantic_mismatch_count++;
    else
        representation_mismatch_count++;
    if (printed_mismatches < 24) {
        fprintf(stderr,
                "%s kind=%s case=%u coeff=%d got=%d want=%d "
                "delta_mod_q=%d\n",
                label, semantic ? "semantic" : "representative", case_idx,
                coeff_idx, got, want,
                centered_modq((int32_t)got - want));
        printed_mismatches++;
    }
}

static void compare_modq(const char *label, unsigned case_idx,
                         const poly *got, const poly *want)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (!same_modq(got->coeffs[i], want->coeffs[i]))
            note_mismatch(label, case_idx, i, got->coeffs[i], want->coeffs[i],
                          1);
    }
}

static void compare_exact(const char *label, unsigned case_idx,
                          const poly *got, const poly *want)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        if (got->coeffs[i] != want->coeffs[i]) {
            const int semantic =
                !same_modq(got->coeffs[i], want->coeffs[i]);

            note_mismatch(label, case_idx, i, got->coeffs[i], want->coeffs[i],
                          semantic);
        }
    }
}

static void check_centered_representatives(const char *label,
                                           unsigned case_idx,
                                           const poly *value, int *max_abs)
{
    for (int i = 0; i < NTRUPLUS_N; i++) {
        const int coeff = value->coeffs[i];
        const int magnitude = coeff < 0 ? -coeff : coeff;

        if (magnitude > *max_abs)
            *max_abs = magnitude;
        if (coeff < -(NTRUPLUS_Q / 2) || coeff > NTRUPLUS_Q / 2) {
            representative_range_violation_count++;
            if (printed_mismatches < 24) {
                fprintf(stderr,
                        "%s kind=range case=%u coeff=%d got=%d "
                        "allowed=[%d,%d]\n",
                        label, case_idx, i, coeff, -(NTRUPLUS_Q / 2),
                        NTRUPLUS_Q / 2);
                printed_mismatches++;
            }
        }
    }
}

static void fill_dense(poly *a)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        a->coeffs[i] = centered_modq(next_u32());
}

static void fill_sparse(poly *a, unsigned weight)
{
    memset(a, 0, sizeof(*a));
    for (unsigned i = 0; i < weight; i++) {
        unsigned pos = next_u32() % NTRUPLUS_N;
        int16_t value = (int16_t)(1 + next_u32() % 3u);

        if (next_u32() & 1u)
            value = (int16_t)-value;
        a->coeffs[pos] = centered_modq((int32_t)a->coeffs[pos] + value);
    }
}

/*
 * Reduce x^(i+j) directly with x^768 = x^384 - 1.  For degree at most 1534:
 *   k < 768:        x^k
 *   768 <= k<1152: x^(k-384) - x^(k-768)
 *   k >= 1152:    -x^(k-1152)
 */
static void schoolbook_mul(poly *r, const poly *a, const poly *b)
{
    int64_t accum[NTRUPLUS_N] = {0};

    for (int i = 0; i < NTRUPLUS_N; i++) {
        for (int j = 0; j < NTRUPLUS_N; j++) {
            const int k = i + j;
            const int64_t product = (int64_t)a->coeffs[i] * b->coeffs[j];

            if (k < NTRUPLUS_N) {
                accum[k] += product;
            } else if (k < 3 * NTRUPLUS_N / 2) {
                accum[k - NTRUPLUS_N / 2] += product;
                accum[k - NTRUPLUS_N] -= product;
            } else {
                accum[k - 3 * NTRUPLUS_N / 2] -= product;
            }
        }
    }

    for (int i = 0; i < NTRUPLUS_N; i++)
        r->coeffs[i] = centered_modq(accum[i]);
}

static void full_product(poly *out, poly *fa, poly *fb, poly *fp,
                         const poly *a, const poly *b)
{
    poly_ntt(fa, a);
    poly_ntt(fb, b);
    poly_basemul_normal(fp, fa, fb);
    poly_invntt_normal(out, fp);
}

static void check_transform_case(const char *label, unsigned case_idx,
                                 const poly *a, const poly *b,
                                 int check_schoolbook)
{
    poly fa, fb, fa_ref, fb_ref, base, base_ref;
    poly roundtrip, inverse_ref, product, product_ref;
    poly rminus_base, rminus_product, inplace;

    poly_ntt(&fa, a);
    poly_ntt(&fb, b);
    ntt_gt_rowbitrevlayout(fa_ref.coeffs, a->coeffs);
    ntt_gt_rowbitrevlayout(fb_ref.coeffs, b->coeffs);
    compare_modq("forward_layout_a", case_idx, &fa, &fa_ref);
    compare_modq("forward_layout_b", case_idx, &fb, &fb_ref);

    inplace = *a;
    poly_ntt(&inplace, &inplace);
    compare_exact("forward_inplace", case_idx, &inplace, &fa);

    poly_invntt_normal(&roundtrip, &fa);
    compare_modq("normal_roundtrip", case_idx, &roundtrip, a);
    check_centered_representatives("normal_inverse_range", case_idx,
                                   &roundtrip, &normal_inverse_max_abs);
    invntt_gt_rowbitrevlayout_exact(inverse_ref.coeffs, fa.coeffs);
    compare_exact("normal_inverse_exact", case_idx, &roundtrip, &inverse_ref);

    inplace = fa;
    poly_invntt_normal(&inplace, &inplace);
    compare_exact("inverse_inplace", case_idx, &inplace, &roundtrip);

    poly_basemul_normal(&base, &fa, &fb);
    poly_basemul_gt_ref(&base_ref, &fa, &fb);
    compare_modq("base_layout", case_idx, &base, &base_ref);
    poly_invntt_normal(&product, &base);

    poly_basemul(&rminus_base, &fa, &fb);
    poly_invntt(&rminus_product, &rminus_base);
    compare_exact("rminus1_pair", case_idx, &rminus_product, &product);
    check_centered_representatives("rminus_inverse_range", case_idx,
                                   &rminus_product, &rminus_inverse_max_abs);

    if (check_schoolbook) {
        schoolbook_mul(&product_ref, a, b);
        compare_modq(label, case_idx, &product, &product_ref);
    }
}

static void check_boundaries(void)
{
    static const char *const labels[] = {
        "zero", "unit", "max_canonical_positive", "max_canonical_negative",
        "alternating_signs", "near_q", "structured_sparse"
    };
    poly cases[7];
    poly unit;

    memset(cases, 0, sizeof(cases));
    memset(&unit, 0, sizeof(unit));
    unit.coeffs[0] = 1;
    cases[1] = unit;

    for (int i = 0; i < NTRUPLUS_N; i++) {
        cases[2].coeffs[i] = NTRUPLUS_Q / 2;
        cases[3].coeffs[i] = (int16_t)-(NTRUPLUS_Q / 2);
        cases[4].coeffs[i] = (i & 1) ? (int16_t)-(NTRUPLUS_Q / 2)
                                           : (int16_t)(NTRUPLUS_Q / 2);
        cases[5].coeffs[i] = (i & 1) ? (int16_t)(1 - NTRUPLUS_Q)
                                           : (int16_t)(NTRUPLUS_Q - 1);
    }
    cases[6].coeffs[0] = 1;
    cases[6].coeffs[1] = -1;
    cases[6].coeffs[383] = 3;
    cases[6].coeffs[384] = -3;
    cases[6].coeffs[767] = 2;

    for (unsigned i = 0; i < sizeof(cases) / sizeof(cases[0]); i++)
        check_transform_case(labels[i], i, &cases[i], &unit, 1);
}

static void check_random_dense(void)
{
    poly a, b;

    for (unsigned i = 0; i < GT_AUDIT_RANDOM_CASES; i++) {
        fill_dense(&a);
        fill_dense(&b);
        check_transform_case("dense_schoolbook", i, &a, &b,
                             i < GT_AUDIT_DENSE_SCHOOLBOOK_CASES);
    }
}

static void check_random_sparse_schoolbook(void)
{
    poly a, b;
    poly fa, fb, fp, got, want;

    for (unsigned i = 0; i < GT_AUDIT_SPARSE_SCHOOLBOOK_CASES; i++) {
        fill_sparse(&a, 8);
        fill_sparse(&b, 8);
        full_product(&got, &fa, &fb, &fp, &a, &b);
        schoolbook_mul(&want, &a, &b);
        compare_modq("sparse_schoolbook", i, &got, &want);
    }
}

static uint64_t check_abi(void)
{
    poly a, b, fa, fb, base, rminus_base;
    poly direct, sentinel;
    uint64_t forward_mask;
    uint64_t normal_inverse_mask;
    uint64_t rminus_inverse_mask;

    fill_dense(&a);
    fill_dense(&b);

    poly_ntt(&direct, &a);
    forward_mask = gt_audit_poly_ntt_abi_sentinel(&sentinel, &a);
    compare_exact("abi_forward_output", 0, &sentinel, &direct);

    poly_ntt(&fa, &a);
    poly_ntt(&fb, &b);
    poly_basemul_normal(&base, &fa, &fb);
    poly_invntt_normal(&direct, &base);
    normal_inverse_mask = gt_audit_poly_invntt_abi_sentinel(&sentinel, &base);
    compare_exact("abi_normal_inverse_output", 0, &sentinel, &direct);

    poly_basemul(&rminus_base, &fa, &fb);
    poly_invntt(&direct, &rminus_base);
    rminus_inverse_mask =
        gt_audit_poly_invntt_rminus1_abi_sentinel(&sentinel, &rminus_base);
    compare_exact("abi_rminus_inverse_output", 0, &sentinel, &direct);

    printf("abi_forward_mask=0x%" PRIx64 "\n", forward_mask);
    printf("abi_normal_inverse_mask=0x%" PRIx64 "\n", normal_inverse_mask);
    printf("abi_rminus_inverse_mask=0x%" PRIx64 "\n", rminus_inverse_mask);
    return forward_mask | normal_inverse_mask | rminus_inverse_mask;
}

int main(void)
{
    uint64_t abi_mask;

    check_boundaries();
    check_random_dense();
    check_random_sparse_schoolbook();
    abi_mask = check_abi();

    printf("gt_transform_audit_random_cases=%d\n", GT_AUDIT_RANDOM_CASES);
    printf("gt_transform_audit_dense_schoolbook_cases=%d\n",
           GT_AUDIT_DENSE_SCHOOLBOOK_CASES);
    printf("gt_transform_audit_sparse_schoolbook_cases=%d\n",
           GT_AUDIT_SPARSE_SCHOOLBOOK_CASES);
    printf("gt_transform_audit_semantic_mismatches=%" PRIu64 "\n",
           semantic_mismatch_count);
    printf("gt_transform_audit_representative_mismatches=%" PRIu64 "\n",
           representation_mismatch_count);
    printf("gt_transform_audit_representative_range_violations=%" PRIu64
           "\n", representative_range_violation_count);
    printf("gt_transform_audit_normal_inverse_max_abs=%d\n",
           normal_inverse_max_abs);
    printf("gt_transform_audit_rminus_inverse_max_abs=%d\n",
           rminus_inverse_max_abs);
    printf("gt_transform_audit_abi_mask=0x%" PRIx64 "\n", abi_mask);

    return semantic_mismatch_count == 0 &&
                   representative_range_violation_count == 0 &&
                   abi_mask == 0
               ? 0
               : 1;
}
