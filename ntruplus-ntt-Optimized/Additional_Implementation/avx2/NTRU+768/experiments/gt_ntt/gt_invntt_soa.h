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

#endif
