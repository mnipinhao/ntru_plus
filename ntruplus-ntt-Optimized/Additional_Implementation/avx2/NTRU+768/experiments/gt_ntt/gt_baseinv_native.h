#ifndef NTRUPLUS_GT_BASEINV_NATIVE_H
#define NTRUPLUS_GT_BASEINV_NATIVE_H

#include <stdint.h>

#include "gt_forward_lazy_bounds.h"
#include "gt_ntt_avx2.h"

/*
 * Invert 192 independent quartics in GTN16 native layout.
 *
 * The centered control accepts representatives in [-3080,3079].  The
 * center-on-load candidate accepts GTN-L8 representatives satisfying
 * |a[i]| <= 8*(q-1).  It applies the exact packed center10 checkpoint while
 * each coefficient vector is first resident in a YMM register; no standalone
 * 768-coefficient normalization or layout pass is performed.
 *
 * Both entries support out == in, leave the input untouched otherwise, return
 * zero on success, and return one with an all-zero output if any quartic is
 * non-invertible.  Successful output is GTN16 normal-domain data with
 * |out[i]| <= q-1.
 */
int gt_baseinv_native_centered_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);

int gt_baseinv_native_center_on_load_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);

/*
 * GTN-L3 is the zero-normalization contract used by the delayed-center
 * Forward.  Its generic envelope is |a[i]| <= 3*(q-1)=10368; the actual
 * producer bounds are 10172 in row01 batches and 9992 in row2 batches.
 * Every initial a_i*a_j product is therefore below q*2^15, so the centered
 * arithmetic body is reused without executing any center10 instruction.
 */
static inline int gt_baseinv_native_l3_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	return gt_baseinv_native_centered_avx2(out, in);
}

#if defined(GT_HAVE_AVX2_ASM)
/*
 * Scheduled prepare-ASM variants with the same external contracts.  The
 * determinant batch inversion and final scaling remain shared with the
 * intrinsic oracle.
 */
int gt_baseinv_native_centered_asm_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);

int gt_baseinv_native_center_on_load_asm_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);

static inline int gt_baseinv_native_l3_asm_avx2(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N])
{
	return gt_baseinv_native_centered_asm_avx2(out, in);
}
#endif

/* Test-only visibility for exhaustive validation of the fused checkpoint. */
void gt_baseinv_center_l8_test_avx2(int16_t out[16],
	const int16_t in[16]);

#endif
