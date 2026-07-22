/*
 * Benchmark-only complete GT HIER_K8 scaled base inverse.
 *
 * ABI:
 *   x0 = poly *r
 *   x1 = const poly *a
 *   w0 = 0 on success, 1 when any denominator product is zero
 *
 * The prepare phase reuses the existing Slothy-scheduled prepare2 kernel.
 * This entrypoint then performs the fixed 8-way batch inversion and all eight
 * three-denominator recoveries in assembly before calling the production
 * finish kernel. Production dispatch is intentionally unchanged.
 */

.text
.align 2

#include "../support/common.inc"

.equ HIER_K8_DEN_BYTES, 384
.equ HIER_K8_C01_BYTES, 128
.equ HIER_K8_GROUP_BYTES, 128
.equ HIER_K8_LOCAL_BYTES, 640
.equ HIER_K8_C01_OFFSET, HIER_K8_DEN_BYTES
.equ HIER_K8_GROUP_OFFSET, HIER_K8_DEN_BYTES + HIER_K8_C01_BYTES

.macro fqmul dst, lhs, rhs
	smull v16.4s, \lhs\().4h, \rhs\().4h
	smull2 v17.4s, \lhs\().8h, \rhs\().8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 \dst\().8h, v16.8h, v17.8h
.endm

.macro batch_back index, prefix
	ldr q2, [x23, #(16 * \index)]
	fqmul v3, \prefix, v0
	fqmul v0, v0, v2
	str q3, [x23, #(16 * \index)]
.endm

.global C_SYM(poly_baseinv_scaled_r_hier_k8_full_asm_candidate)
#ifndef __APPLE__
.type C_SYM(poly_baseinv_scaled_r_hier_k8_full_asm_candidate), %function
#endif
C_SYM(poly_baseinv_scaled_r_hier_k8_full_asm_candidate):
	stp x30, x19, [sp, #-16]!
	stp x20, x21, [sp, #-16]!
	stp x22, x23, [sp, #-16]!
	stp d8, d9, [sp, #-16]!
	stp d10, d11, [sp, #-16]!
	stp d12, d13, [sp, #-16]!
	stp d14, d15, [sp, #-16]!
	sub sp, sp, #HIER_K8_LOCAL_BYTES

	mov x19, x0
	mov x20, x1
	mov x21, sp
	add x22, sp, #HIER_K8_C01_OFFSET
	add x23, sp, #HIER_K8_GROUP_OFFSET

	/* Prepare 24 quartic blocks and form eight three-block products. */
	mov x0, x19
	mov x1, x21
	mov x2, x22
	mov x3, x23
	mov x4, x20
	LOAD_ADDR_PAGE(x5, gt_rowbitrev_lambda)
	LOAD_ADDR_OFF(x5, gt_rowbitrev_lambda)
	adr x6, Lhier_k8_scaled_r_consts
	bl C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm)

	/* Prefix products c0..c6 stay in q8..q14 across gt_fqinv15_asm. */
	ldr q1, Lhier_k8_scaled_r_consts
	ldr q8, [x23, #0]
	ldr q2, [x23, #16]
	fqmul v9, v8, v2
	ldr q2, [x23, #32]
	fqmul v10, v9, v2
	ldr q2, [x23, #48]
	fqmul v11, v10, v2
	ldr q2, [x23, #64]
	fqmul v12, v11, v2
	ldr q2, [x23, #80]
	fqmul v13, v12, v2
	ldr q2, [x23, #96]
	fqmul v14, v13, v2
	ldr q2, [x23, #112]
	fqmul v0, v14, v2

	/* Match vminvq_u16(): any zero lane makes the complete batch fail. */
	uminv h2, v0.8h
	umov w8, v2.h[0]
	cbz w8, Lhier_k8_failure

	bl C_SYM(gt_fqinv15_asm)
	ldr q1, Lhier_k8_scaled_r_consts

	/* Recover the inverse of each of the eight group products. */
	batch_back 7, v14
	batch_back 6, v13
	batch_back 5, v12
	batch_back 4, v11
	batch_back 3, v10
	batch_back 2, v9
	batch_back 1, v8
	str q0, [x23, #0]

	/* Recover d0^-1, d1^-1, d2^-1 for each three-denominator group. */
	mov x4, x21
	mov x5, x22
	mov x6, x23
	mov w7, #8
Lhier_k8_recover_group:
	ldp q2, q3, [x4]
	ldr q4, [x4, #32]
	ldr q5, [x5], #16
	ldr q6, [x6], #16

	fqmul v7, v5, v6
	fqmul v6, v6, v4
	fqmul v5, v2, v6
	fqmul v6, v6, v3

	stp q6, q5, [x4]
	str q7, [x4, #32]
	add x4, x4, #48
	subs w7, w7, #1
	b.ne Lhier_k8_recover_group

	mov x0, x19
	mov x1, x21
	bl C_SYM(baseinv_batch_finish24_n1_asm)
	mov w0, wzr
	b Lhier_k8_return

Lhier_k8_failure:
	mov x0, x19
	mov w1, wzr
	mov x2, #1536
	bl C_SYM(memset)
	mov w0, #1

Lhier_k8_return:
	add sp, sp, #HIER_K8_LOCAL_BYTES
	ldp d14, d15, [sp], #16
	ldp d12, d13, [sp], #16
	ldp d10, d11, [sp], #16
	ldp d8, d9, [sp], #16
	ldp x22, x23, [sp], #16
	ldp x20, x21, [sp], #16
	ldp x30, x19, [sp], #16
	ret
#ifndef __APPLE__
.size C_SYM(poly_baseinv_scaled_r_hier_k8_full_asm_candidate), \
	.-C_SYM(poly_baseinv_scaled_r_hier_k8_full_asm_candidate)
#endif

.p2align 4
Lhier_k8_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0
