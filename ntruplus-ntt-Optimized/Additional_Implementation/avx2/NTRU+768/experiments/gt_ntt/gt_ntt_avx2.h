#ifndef NTRUPLUS_GT_NTT_AVX2_H
#define NTRUPLUS_GT_NTT_AVX2_H

#include <stdint.h>

#define GT_NTT_N 768
#define GT_NTT_Q 3457

/* Prototype forward NTT; output matches ntt_gt_rowbitrevlayout(). */
void gt_ntt_avx2(int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);

/*
 * Convert between the verified row-bitrev block-major representation and the
 * candidate 16-block SoA representation:
 *   batch = 4*k3 + Q/8, lane = 8*branch + Q%8.
 */
void gt_ntt_rowbitrev_to_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
void gt_ntt_soa_to_rowbitrev(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);

/* Exposed only so the prototype tests can verify representation boundaries. */
typedef struct __attribute__((aligned(32))) {
	int16_t row01[32][16];
	int16_t row2[32][8];
} gt_frontend_scratch;

typedef struct __attribute__((aligned(32))) {
	int16_t row01[32][16];
	int16_t row2_packed[16][16];
} gt_stage2_scratch;

#if defined(GT_HAVE_AVX2_ASM)
/*
 * Full forward wrappers below own private aligned semantic scratch, so every
 * one of them preserves the public out==in contract.
 */
/* Hybrid prototype: intrinsic frontend/stage12, hand-scheduled ASM stage345. */
void gt_ntt_avx2_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
/* Hand-scheduled frontend/stage12, with the same ASM stage345 consumer. */
void gt_ntt_avx2_frontend_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
/* Stripe-first producer removes the frontend scratch. */
void gt_ntt_avx2_frontend_direct_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_direct_interleaved_asm_soa(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_direct_queued_store_asm_soa(
	int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_half_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_remapped_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_half_remapped_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_resident_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_frontend_queued_store_asm_soa(int16_t out[GT_NTT_N],
	const int16_t in[GT_NTT_N]);
/* Standalone low-level entries below have boundary-specific alias contracts. */
void gt_ntt_avx2_frontend_asm(gt_frontend_scratch *scratch,
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_stage12_asm(gt_stage2_scratch *out,
	const gt_frontend_scratch *in);
void gt_ntt_avx2_frontend_stage12_asm(gt_stage2_scratch *out,
	const int16_t in[GT_NTT_N]);
/* Low-level zero-handoff entry: out and in must not overlap. */
void gt_ntt_avx2_frontend_stage12_direct_asm(gt_stage2_scratch *out,
	const int16_t in[GT_NTT_N]);
/* Low-level half-handoff entry: out and in must not overlap. */
void gt_ntt_avx2_frontend_stage12_half_asm(gt_stage2_scratch *out,
	const int16_t in[GT_NTT_N]);
/*
 * Low-level Stage345 entries are not in-place: scratch must be 32-byte
 * aligned, and its full 1536-byte region must not overlap the 1536-byte out
 * region.  The public wrappers above remain out==in safe because they pass a
 * private stage2 scratch to these consumers.
 */
void gt_ntt_avx2_stage345_soa_asm(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch);
void gt_ntt_avx2_stage345_soa_interleaved_asm(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch);
void gt_ntt_avx2_stage345_soa_remapped_asm(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch);
void gt_ntt_avx2_stage345_soa_resident_asm(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch);
void gt_ntt_avx2_stage345_soa_queued_store_asm(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch);
void gt_ntt_avx2_barrett_packed_asm(int16_t out[16],
	const int16_t in[16]);
#endif

void gt_ntt_avx2_frontend(gt_frontend_scratch *scratch,
	const int16_t in[GT_NTT_N]);
void gt_ntt_avx2_stage12(gt_stage2_scratch *out,
	const gt_frontend_scratch *in);
void gt_ntt_avx2_stage345(gt_stage2_scratch *scratch);
void gt_ntt_avx2_scatter(int16_t out[GT_NTT_N],
	const gt_stage2_scratch *scratch);

void gt_ntt_avx2_montgomery_test(int16_t out[16],
	const int16_t a[16], const int16_t b[16]);
void gt_ntt_avx2_barrett_test(int16_t out[16], const int16_t a[16]);

#endif
