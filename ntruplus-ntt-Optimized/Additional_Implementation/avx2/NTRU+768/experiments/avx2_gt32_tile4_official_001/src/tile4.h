#ifndef NTRUPLUS_GT32_TILE4_H
#define NTRUPLUS_GT32_TILE4_H

#include <stdint.h>

#define GT32_TILE4_Q 3457
#define GT32_TILE4_WORDS 128
#define GT32_TILE4_TILES 6
#define GT32_TILE4_POLY_WORDS (GT32_TILE4_WORDS * GT32_TILE4_TILES)

/* Native quartic multiplication: TILE4 e=0 x e=0 -> TILE4 e=-1. */
void gt32_tile4_basemul_b0(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_basemul_b1(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Register-transpose assembly candidate.  Distinct buffers are required. */
void gt32_tile4_basemul_b2_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* General NTT ABI: TILE4 e=0 x e=0 -> TILE4 e=0, distinct buffers. */
void gt32_tile4_basemul_general_b2_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);
/* Decap-only bridge: TILE4 e=0 x e=0 -> private coefficient planes e=-1. */
void gt32_tile4_basemul_scale_soa_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS],
	const int16_t b[GT32_TILE4_POLY_WORDS]);

void gt32_tile4_frontend_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_intrinsic(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Low-level frontend requires disjoint input/output regions. */
void gt32_tile4_frontend_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Raw top split requires every input coefficient to be in [-3,4]. */
void gt32_tile4_frontend_raw_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_fixed_raw_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_frontend_wide_raw_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

/*
 * One tile is one (k3, branch) and four quartic coefficients:
 *   vector = Q / 4, lane = 4 * (Q % 4) + coefficient.
 * Input Q is natural order; forward output Q is bit-reversed frequency order.
 */
void gt32_tile4_forward_tile_ref(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_inverse_tile_ref(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_forward_all_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* D2a oracle: private coefficient planes e=-1 -> same private layout e=-1. */
void gt32_tile4_inverse_soa_private_ref(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_soa_private_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_soa_private_parallel_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

void gt32_tile4_forward_tile_asm(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_inverse_tile_asm(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS]);
void gt32_tile4_forward_all_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_all_serial_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_all_parallel_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_all_pair_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_inverse_all_pair_asm(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

/* Full coefficient-order input -> TILE4 bit-reversed frequency output. */
void gt32_tile4_forward_full_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_candidate(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
/* Small-input-only combined candidate; supports out == in. */
void gt32_tile4_forward_full_fixed_pair_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_fixed_pair_wide_load_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_wide_raw_pair_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_wide_raw_pair_align32_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);
void gt32_tile4_forward_full_wide_raw_pair_align64_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

#endif
