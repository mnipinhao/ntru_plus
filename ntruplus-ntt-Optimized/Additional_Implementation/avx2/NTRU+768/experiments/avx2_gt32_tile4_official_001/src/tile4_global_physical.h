#ifndef TILE4_GLOBAL_PHYSICAL_H
#define TILE4_GLOBAL_PHYSICAL_H

#include <stdint.h>

#define GT32_GLOBAL_PHYSICAL_WORDS 768

typedef struct __attribute__((aligned(32))) {
	int16_t frontend[GT32_GLOBAL_PHYSICAL_WORDS];
	int16_t forward_a[GT32_GLOBAL_PHYSICAL_WORDS];
	int16_t forward_b[GT32_GLOBAL_PHYSICAL_WORDS];
	int16_t product[GT32_GLOBAL_PHYSICAL_WORDS];
	int16_t inverse_rows[GT32_GLOBAL_PHYSICAL_WORDS];
} gt32_global_physical_scratch_t;

/*
 * Private coefficient-domain polynomial multiplication.
 *
 * Inputs use the small coefficient contract consumed by N5.  The internal
 * ABI is Forward-global-M -> B3-M -> inverse-global-AoS.  The output is the
 * same coefficient-domain representative as the qualified T9 path.
 * Scratch must be 32-byte aligned and may not alias out/a/b.
 */
void gt32_global_physical_polymul_private(
	int16_t out[GT32_GLOBAL_PHYSICAL_WORDS],
	const int16_t a[GT32_GLOBAL_PHYSICAL_WORDS],
	const int16_t b[GT32_GLOBAL_PHYSICAL_WORDS],
	gt32_global_physical_scratch_t *scratch);

#endif
