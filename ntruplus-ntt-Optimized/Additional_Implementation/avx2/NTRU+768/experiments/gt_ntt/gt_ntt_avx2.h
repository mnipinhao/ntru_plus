#ifndef NTRUPLUS_GT_NTT_AVX2_H
#define NTRUPLUS_GT_NTT_AVX2_H

#include <stdint.h>

#define GT_NTT_N 768
#define GT_NTT_Q 3457

/* Prototype forward NTT; output matches ntt_gt_rowbitrevlayout(). */
void gt_ntt_avx2(int16_t out[GT_NTT_N], const int16_t in[GT_NTT_N]);

/* Exposed only so the prototype tests can verify representation boundaries. */
typedef struct __attribute__((aligned(32))) {
	int16_t row01[32][16];
	int16_t row2[32][8];
} gt_frontend_scratch;

typedef struct __attribute__((aligned(32))) {
	int16_t row01[32][16];
	int16_t row2_packed[16][16];
} gt_stage2_scratch;

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
