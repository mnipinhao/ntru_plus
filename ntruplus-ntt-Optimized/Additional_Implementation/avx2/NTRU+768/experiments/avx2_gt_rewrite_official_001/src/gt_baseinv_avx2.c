#include "gt_backend.h"

#include <immintrin.h>
#include <stddef.h>
#include <string.h>

#include "gt_avx2_arith.h"
#include "gt_generated_tables.h"

enum {
    GT_QINV = 12929,
    GT_RINV = -682,
    GT_RINV_QINV = 29782,
};

static inline __m256i montgomery_mul(__m256i a, __m256i b)
{
    const __m256i q = _mm256_set1_epi16(NTRUPLUS_Q);
    const __m256i qinv = _mm256_set1_epi16(GT_QINV);
    const __m256i low = _mm256_mullo_epi16(a, b);
    const __m256i high = _mm256_mulhi_epi16(a, b);
    const __m256i correction = _mm256_mulhi_epi16(
        _mm256_mullo_epi16(low, qinv), q);
    return _mm256_sub_epi16(high, correction);
}

static inline __m256i montgomery_mul_fixed(__m256i a, __m256i factor,
                                           __m256i factor_qinv)
{
    const __m256i q = _mm256_set1_epi16(NTRUPLUS_Q);
    const __m256i high = _mm256_mulhi_epi16(a, factor);
    const __m256i correction = _mm256_mulhi_epi16(
        _mm256_mullo_epi16(a, factor_qinv), q);
    return _mm256_sub_epi16(high, correction);
}

static inline __m256i montgomery_square(__m256i a)
{
    return montgomery_mul(a, a);
}

static __m256i field_inverse(__m256i r)
{
    const __m256i qinv = _mm256_set1_epi16(GT_QINV);
    const __m256i rinv = _mm256_set1_epi16(GT_RINV);
    const __m256i rinv_qinv = _mm256_set1_epi16(GT_RINV_QINV);
    const __m256i r_qinv = _mm256_mullo_epi16(r, qinv);
    __m256i t1 = montgomery_square(r);
    __m256i t1_qinv = _mm256_mullo_epi16(t1, qinv);
    __m256i t2 = montgomery_square(t1);
    t2 = montgomery_square(t2);
    __m256i t3 = montgomery_square(t2);
    t1 = montgomery_mul_fixed(t2, t1, t1_qinv);
    t1_qinv = _mm256_mullo_epi16(t1, qinv);
    t2 = montgomery_mul_fixed(t3, t1, t1_qinv);
    t2 = montgomery_square(t2);
    t2 = montgomery_mul_fixed(t2, r, r_qinv);
    t1 = montgomery_mul_fixed(t2, t1, t1_qinv);
    for (unsigned i = 0; i < 6; ++i)
        t2 = montgomery_square(t2);
    const __m256i t2_qinv = _mm256_mullo_epi16(t2, qinv);
    t2 = montgomery_mul_fixed(t1, t2, t2_qinv);
    return montgomery_mul_fixed(t2, rinv, rinv_qinv);
}

static int batch_inverse(__m256i determinant[12])
{
    const __m256i qinv = _mm256_set1_epi16(GT_QINV);
    const __m256i zero = _mm256_setzero_si256();
    __m256i prefix[12];
    __m256i operand_qinv[12];
    prefix[0] = determinant[0];
    for (size_t i = 1; i < 12; ++i) {
        operand_qinv[i] = _mm256_mullo_epi16(determinant[i], qinv);
        prefix[i] = montgomery_mul_fixed(prefix[i - 1], determinant[i],
                                         operand_qinv[i]);
    }
    const __m256i zero_mask = _mm256_cmpeq_epi16(prefix[11], zero);
    const int failure = !_mm256_testz_si256(zero_mask, zero_mask);

    /* Inverting zero produces zero under this fixed addition chain.  Always
     * run the recovery loop so the failure result does not alter the address
     * trace or loop structure. */
    __m256i inverse = field_inverse(prefix[11]);
    for (size_t i = 11; i > 0; --i) {
        const __m256i inverse_qinv = _mm256_mullo_epi16(inverse, qinv);
        const __m256i operand = determinant[i];
        determinant[i] = montgomery_mul_fixed(prefix[i - 1], inverse,
                                              inverse_qinv);
        inverse = montgomery_mul_fixed(inverse, operand, operand_qinv[i]);
    }
    determinant[0] = inverse;
    return failure;
}

int gt_poly_baseinv(poly *r, const poly *a)
{
    __m256i determinant[12] __attribute__((aligned(32)));
    const __m256i qinv = _mm256_set1_epi16(GT_QINV);

    for (size_t batch = 0; batch < 12; ++batch) {
        const size_t base = 64 * batch;
        const __m256i alpha = _mm256_loadu_si256(
            (const __m256i *)&gt_alpha_montgomery[16 * batch]);
        const __m256i alpha_qinv = _mm256_loadu_si256(
            (const __m256i *)&gt_alpha_montgomery_qinv[16 * batch]);
        const __m256i a0 = _mm256_load_si256((const __m256i *)&a->coeffs[base]);
        const __m256i a1 = _mm256_load_si256((const __m256i *)&a->coeffs[base + 16]);
        const __m256i a2 = _mm256_load_si256((const __m256i *)&a->coeffs[base + 32]);
        const __m256i a3 = _mm256_load_si256((const __m256i *)&a->coeffs[base + 48]);
        __m256i cross = montgomery_mul(a1, a3);
        __m256i t0 = _mm256_sub_epi16(montgomery_square(a2),
                                      _mm256_add_epi16(cross, cross));
        t0 = _mm256_add_epi16(montgomery_square(a0),
                              montgomery_mul_fixed(t0, alpha, alpha_qinv));
        cross = montgomery_mul(a0, a2);
        __m256i t1 = _mm256_add_epi16(montgomery_square(a1),
            montgomery_mul_fixed(montgomery_square(a3), alpha, alpha_qinv));
        t1 = _mm256_sub_epi16(t1, _mm256_add_epi16(cross, cross));
        const __m256i t2 = montgomery_mul_fixed(t1, alpha, alpha_qinv);
        determinant[batch] = _mm256_sub_epi16(
            montgomery_square(t0), montgomery_mul(t1, t2));

        _mm256_store_si256((__m256i *)&r->coeffs[base],
            _mm256_add_epi16(montgomery_mul(a0, t0), montgomery_mul(a2, t2)));
        _mm256_store_si256((__m256i *)&r->coeffs[base + 16],
            _mm256_add_epi16(montgomery_mul(a3, t2), montgomery_mul(a1, t0)));
        _mm256_store_si256((__m256i *)&r->coeffs[base + 32],
            _mm256_add_epi16(montgomery_mul(a2, t0), montgomery_mul(a0, t1)));
        _mm256_store_si256((__m256i *)&r->coeffs[base + 48],
            _mm256_add_epi16(montgomery_mul(a1, t1), montgomery_mul(a3, t0)));
    }

    const int failure = batch_inverse(determinant);
    const __m256i success_mask = _mm256_set1_epi16((short)(failure - 1));
    for (size_t batch = 0; batch < 12; ++batch) {
        const size_t base = 64 * batch;
        const __m256i scale = determinant[batch];
        const __m256i scale_qinv = _mm256_mullo_epi16(scale, qinv);
        __m256i r0 = montgomery_mul_fixed(
            _mm256_load_si256((const __m256i *)&r->coeffs[base]), scale, scale_qinv);
        __m256i r1 = montgomery_mul_fixed(
            _mm256_load_si256((const __m256i *)&r->coeffs[base + 16]), scale, scale_qinv);
        __m256i r2 = montgomery_mul_fixed(
            _mm256_load_si256((const __m256i *)&r->coeffs[base + 32]), scale, scale_qinv);
        __m256i r3 = montgomery_mul_fixed(
            _mm256_load_si256((const __m256i *)&r->coeffs[base + 48]), scale, scale_qinv);
        r1 = _mm256_sub_epi16(_mm256_setzero_si256(), r1);
        r3 = _mm256_sub_epi16(_mm256_setzero_si256(), r3);
        _mm256_store_si256((__m256i *)&r->coeffs[base],
            _mm256_and_si256(gt_center16_twice(r0), success_mask));
        _mm256_store_si256((__m256i *)&r->coeffs[base + 16],
            _mm256_and_si256(gt_center16_twice(r1), success_mask));
        _mm256_store_si256((__m256i *)&r->coeffs[base + 32],
            _mm256_and_si256(gt_center16_twice(r2), success_mask));
        _mm256_store_si256((__m256i *)&r->coeffs[base + 48],
            _mm256_and_si256(gt_center16_twice(r3), success_mask));
    }
    return failure;
}
