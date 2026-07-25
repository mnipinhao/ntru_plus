#ifndef NTRUPLUS_GT_NATIVE_PACK_H
#define NTRUPLUS_GT_NATIVE_PACK_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

#define GT_NATIVE_QUARTIC_SLOTS 192

extern const uint8_t
	gt_production_to_native_quartic[GT_NATIVE_QUARTIC_SLOTS];
extern const uint8_t
	gt_native_to_production_quartic[GT_NATIVE_QUARTIC_SLOTS];

/*
 * Canonicalize, permute, and serialize a normal-domain GTN16 polynomial
 * directly to the unchanged production WIRE12 format.  The wire traversal is
 * production-group, lane, sign, then quartic coefficient; this matches the
 * two-batch interleave in production pack.s.  The input may contain any
 * signed-int16 representatives.  Addresses and loop counts depend only on
 * public slot indices.
 */
void gt_poly_tobytes_native(uint8_t out[NTRUPLUS_POLYBYTES],
	const poly *native);

#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
/*
 * AVX2 implementation of the same contract.  It reconstructs each pair of
 * production WIRE12 lane vectors with fixed public shuffles, then reuses the
 * production canonicalize/pack network.
 */
void gt_poly_tobytes_native_asm_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const poly *native);

/*
 * Consumer-specialized entries with the same byte output.  The L3 entry
 * accepts |x| <= 10172 and uses the exact center10 reducer.  The centered
 * entry accepts -(q-1) <= x <= q-1 and only adds q to negative lanes.
 */
void gt_poly_tobytes_native_l3_asm_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const poly *native);
void gt_poly_tobytes_native_centered_asm_avx2(
	uint8_t out[NTRUPLUS_POLYBYTES], const poly *native);
#endif

/* Test-only exact scalar form of the production packed canonicalizer. */
uint16_t gt_native_pack_canonicalize_test(int16_t value);

#endif
