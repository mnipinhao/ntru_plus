#ifndef GT32_TILE4_PREPARED_FIXED_B3_H
#define GT32_TILE4_PREPARED_FIXED_B3_H

#include <stdint.h>

#include "tile4.h"

#define GT32_PREPARED_FIXED_B3_MATRIX_WORDS (12 * 4 * 4 * 16)

typedef struct __attribute__((aligned(64))) {
	int16_t row_packets[GT32_PREPARED_FIXED_B3_MATRIX_WORDS];
} gt32_prepared_fixed_b3_general_e1;

void gt32_prepare_fixed_b3_general_e1(
	gt32_prepared_fixed_b3_general_e1 *matrix,
	const int16_t fixed[GT32_TILE4_POLY_WORDS]);

void gt32_tile4_basemul_general_fixed_soa_e1_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t dynamic[GT32_TILE4_POLY_WORDS],
	const gt32_prepared_fixed_b3_general_e1 *matrix);

#endif
