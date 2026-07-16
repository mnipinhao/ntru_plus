#ifndef NTRUPLUS_GT_BASEMUL_SOA_H
#define NTRUPLUS_GT_BASEMUL_SOA_H

#include <stdint.h>

#include "gt_ntt_avx2.h"

#define GT_SOA_BATCHES 12
#define GT_SOA_LANES 16

extern const int16_t gt_soa_lambda[GT_SOA_BATCHES][GT_SOA_LANES];
extern const int16_t gt_soa_lambda_qinv[GT_SOA_BATCHES][GT_SOA_LANES];

/*
 * Multiply 192 independent quartics in the candidate 16-block SoA layout.
 * The three arrays must not overlap.  Inputs satisfy |coefficient| <= q and
 * output is a normal-domain representative in [-(q-1),q-1].
 */
void gt_basemul_soa_avx2(int16_t out[restrict GT_NTT_N],
	const int16_t a[restrict GT_NTT_N],
	const int16_t b[restrict GT_NTT_N]);

#endif
