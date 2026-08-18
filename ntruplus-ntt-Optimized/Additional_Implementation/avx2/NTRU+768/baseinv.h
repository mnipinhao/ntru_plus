#ifndef NTRUPLUS_GT_BASEINV_NATIVE_H
#define NTRUPLUS_GT_BASEINV_NATIVE_H

#include <stdint.h>

#include "ntt_bounds.h"
#include "ntt.h"

/* Invert 192 independent quartics in the selected P layout. */
int gt_baseinv_native_centered_avx2(
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

#endif
