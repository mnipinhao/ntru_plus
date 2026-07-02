/*
 * Benchmark-only split producer for the rminus1 stage123-scratch experiment.
 *
 * ABI:
 *   x0 = int16_t *stage123_scratch
 *   x1 = const poly *a
 *   x2 = const poly *b
 *
 * This is intentionally not a direct-store production kernel.  It preserves
 * the historical benchmark shape by composing:
 *
 *   poly_basemul_rminus1(tmp, a, b)
 *   gt_rminus1_block_major_to_stage123_stripe_scratch(stage123_scratch, tmp)
 */

.text
.align 2

#include "../common.inc"

.global C_SYM(poly_basemul_rminus1_to_stage123scratch)
C_SYM(poly_basemul_rminus1_to_stage123scratch):
	stp x29, x30, [sp, #-16]!
	mov x29, sp
	stp x19, x20, [sp, #-16]!
	mov x19, x0
	sub sp, sp, #1536

	mov x0, sp
	bl C_SYM(poly_basemul_rminus1)

	mov x0, x19
	mov x1, sp
	bl C_SYM(gt_rminus1_block_major_to_stage123_stripe_scratch)

	add sp, sp, #1536
	ldp x19, x20, [sp], #16
	ldp x29, x30, [sp], #16
	ret
