#ifndef GT32_LATE_SOA_065_H
#define GT32_LATE_SOA_065_H

#include <stdint.h>

#define LATE065_WORDS 768

typedef struct {
	int16_t frontend[LATE065_WORDS];
	int16_t operand_a[LATE065_WORDS];
	int16_t operand_b[LATE065_WORDS];
	int16_t product[LATE065_WORDS];
	int16_t inverse_rows[LATE065_WORDS];
} late065_scratch;

/*
 * Complete coefficient-input -> coefficient-output polynomial chains.
 *
 * Inputs must satisfy the selected raw N5 frontend contract [-3,4].  Output
 * may alias either coefficient input because both inputs are dead before the
 * common inverse tail starts.  Scratch must be 32-byte aligned and disjoint
 * from input/output storage.  The three profiles have identical public scale,
 * coefficient order, and modulo-q semantics.
 */
void late065_chain_c0(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS],
	late065_scratch *scratch);
void late065_chain_c1(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS],
	late065_scratch *scratch);
void late065_chain_l0(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS],
	late065_scratch *scratch);

void late_full_inverse_i2_asm(int16_t out[LATE065_WORDS],
	const int16_t in[LATE065_WORDS]);
void late_soa_full_basemul_i2_fused_asm(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS]);

void gt32_tile4_frontend_wide_raw_asm(int16_t *, const int16_t *);
void gt32_tile4_forward_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_forward_all_bm_soa_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_c3center_late_aos_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_attr_basemul_i1_stage01_fused_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_attr_inverse_i1_cross3_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_tail_t9_isolated_private_asm(
	int16_t *, const int16_t *);

#endif
