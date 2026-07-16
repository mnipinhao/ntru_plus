#ifndef NTRUPLUS_GT_INVNTT_SOA_H
#define NTRUPLUS_GT_INVNTT_SOA_H

#include <stdint.h>

#include "gt_ntt_avx2.h"

/*
 * Consume the 16-block SoA NTT-domain representation directly.  The input is
 * in normal domain with |coefficient| <= q.  Output is congruent to the
 * canonical NTRU+768 coefficient representation.  out==in is supported.
 */
void gt_invntt_soa_avx2(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* Exact scratch-boundary oracle after inverse NTT32 and packed Barrett. */
void gt_invntt_soa_ntt32_intrinsic(int16_t rows[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* Exact in-place oracle for inverse DFT3 and its packed checkpoints. */
void gt_invntt_soa_dft3_intrinsic(int16_t rows[GT_NTT_N]);

/* Exact oracle for untwist, branch merge, normalization, and final stores. */
void gt_invntt_soa_postprocess_intrinsic(int16_t out[GT_NTT_N],
	const int16_t rows[GT_NTT_N]);

#if defined(GT_HAVE_AVX2_ASM)
/* Testable ASM region; rows must be 32-byte aligned and separate from in. */
void gt_invntt_soa_ntt32_asm(int16_t rows[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* In-place inverse DFT3 ASM region; rows must be 32-byte aligned. */
void gt_invntt_soa_dft3_asm(int16_t rows[GT_NTT_N]);

/* rows must be 32-byte aligned and must not overlap out. */
void gt_invntt_soa_postprocess_asm(int16_t out[GT_NTT_N],
	const int16_t rows[GT_NTT_N]);

/* Hybrid milestone: ASM inverse NTT32, intrinsic DFT3 and postprocess. */
void gt_invntt_soa_avx2_hybrid(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* Two-region hybrid: ASM inverse NTT32 and DFT3, intrinsic postprocess. */
void gt_invntt_soa_avx2_dft3_hybrid(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* Three separately callable ASM regions; the C wrapper owns row scratch. */
void gt_invntt_soa_avx2_postprocess_hybrid(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* Single ASM entry with one internal 1536-byte aligned row scratch. */
void gt_invntt_soa_avx2_fused_asm(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
#endif

#endif
