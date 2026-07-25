#ifndef NTRUPLUS_GT_BASEMUL_SOA_H
#define NTRUPLUS_GT_BASEMUL_SOA_H

#include <stdint.h>

#include "gt_ntt_avx2.h"

#define GT_SOA_BATCHES 12
#define GT_SOA_LANES 16

extern const int16_t gt_soa_lambda[GT_SOA_BATCHES][GT_SOA_LANES];
extern const int16_t gt_soa_lambda_qinv[GT_SOA_BATCHES][GT_SOA_LANES];
extern const int16_t gt_native_lambda[GT_SOA_BATCHES][GT_SOA_LANES];
extern const int16_t gt_native_lambda_qinv[GT_SOA_BATCHES][GT_SOA_LANES];

/*
 * Multiply 192 independent quartics in the candidate 16-block SoA layout.
 * The three arrays must not overlap.  Inputs satisfy |coefficient| <= q and
 * output is a normal-domain representative in [-(q-1),q-1].
 */
void gt_basemul_soa_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

/*
 * Multiply the same quartics directly in fused Stage345 native layout.
 * The arrays must not overlap.  One input satisfies |coefficient| <= q and
 * the other |coefficient| <= 8*(q-1); either orientation is valid.  This
 * keeps every raw product below q*2^15.  Output remains in native layout and
 * is a normal-domain representative in [-(q-1),q-1].
 */
void gt_basemul_native_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

#if defined(GT_HAVE_AVX2_ASM)
/* Zero-spill scheduled variants with the same arithmetic and range contract. */
void gt_basemul_soa_asm_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

void gt_basemul_native_asm_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

/*
 * Matching experimental variants retain product*R^-1 (mod q).  A three-
 * instruction centered checkpoint maps the proven pre-finalizer interval
 * [-4*(q-1),4*(q-1)] into [-2359,2359], so the existing inverse butterfly
 * range remains valid.  Consume only with the R^-1-aware inverse entry.
 */
void gt_basemul_soa_rminus1_asm_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

void gt_basemul_native_rminus1_asm_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

/*
 * More aggressive matching candidate: c0 keeps its raw <=2*(q-1) value;
 * c1..c3 use the centered checkpoint.  The inverse c0 stream reaches at
 * most 8*(q-1)=27648 before its existing packed Barrett checkpoint.
 */
void gt_basemul_soa_rminus1_c0lazy_asm_avx2(
	int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

void gt_basemul_native_rminus1_c0lazy_asm_avx2(
	int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);
#endif

#endif
