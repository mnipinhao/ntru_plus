#ifndef GT32_TILE4_DUAL_TERMINAL_H
#define GT32_TILE4_DUAL_TERMINAL_H

#include <stdint.h>

#include "tile4.h"

#define GT32_SOTP_PLANE_BYTES (GT32_TILE4_POLY_WORDS / 8)

typedef struct {
	uint8_t neg[GT32_SOTP_PLANE_BYTES];
	uint8_t nz[GT32_SOTP_PLANE_BYTES];
} gt32_sotp_sidecar_t;

/* Benchmark-only: no coefficient-order ternary polynomial is produced. */
void gt32_tile4_inverse_terminal_n5_sidecar_asm(
	int16_t n5_frontend[GT32_TILE4_POLY_WORDS],
	const int16_t inverse_rows[GT32_TILE4_POLY_WORDS],
	gt32_sotp_sidecar_t *sidecar);
void gt32_tile4_inverse_terminal_n5_sidecar_b2_asm(
	int16_t n5_frontend[GT32_TILE4_POLY_WORDS],
	const int16_t inverse_rows[GT32_TILE4_POLY_WORDS],
	gt32_sotp_sidecar_t *sidecar);
void gt32_tile4_inverse_terminal_n5_sidecar_b4_asm(
	int16_t n5_frontend[GT32_TILE4_POLY_WORDS],
	const int16_t inverse_rows[GT32_TILE4_POLY_WORDS],
	gt32_sotp_sidecar_t *sidecar);

int gt32_sotp_decode_sidecar(uint8_t msg[GT32_SOTP_PLANE_BYTES],
	const gt32_sotp_sidecar_t *sidecar,
	const uint8_t buf[2 * GT32_SOTP_PLANE_BYTES]);

/* Benchmark-only extension of the production full-m crepmod3 ABI. */
void gt32_poly_crepmod3_sidecar_s1_asm(int16_t m[768],
	gt32_sotp_sidecar_t *sidecar);
void gt32_poly_crepmod3_sidecar_s2_asm(int16_t m[768],
	gt32_sotp_sidecar_t *sidecar);

#endif
