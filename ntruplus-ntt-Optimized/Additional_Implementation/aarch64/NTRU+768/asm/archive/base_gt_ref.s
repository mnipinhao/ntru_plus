.text
.align 2

/*
 * GT row-bitrev scalar-reference base operations.
 *
 * This is deliberately not optimized.  It preserves the KEM ABI while using
 * the GT layout contract:
 *
 *   coeff[branch*384 + 4*physical_j + lane]
 *
 * The lambda table is gt_rowbitrev_lambda[branch][physical_j] in physical
 * row-bitrev block order.  These constants are Montgomery-form because the
 * scalar basemul/baseinv helpers from ntt.c consume Montgomery zeta/lambda
 * values.  Do not use stock zetas_mul here; stock asm/stock/base.s is packed for
 * the KPQC coefficient-major NTT layout, not this GT block-major layout.
 */

.global poly_basemul
.global _poly_basemul
poly_basemul:
_poly_basemul:
	stp x29, x30, [sp, #-64]!
	mov x29, sp
	stp x19, x20, [sp, #16]
	stp x21, x22, [sp, #32]
	str x23, [sp, #48]

	mov x19, x0
	mov x20, x1
	mov x21, x2
	adrp x22, _gt_rowbitrev_lambda@PAGE
	add x22, x22, _gt_rowbitrev_lambda@PAGEOFF
	mov w23, #192

Lgt_basemul_loop:
	mov x0, x19
	mov x1, x20
	mov x2, x21
	ldrsh w3, [x22]
	bl _basemul

	add x19, x19, #8
	add x20, x20, #8
	add x21, x21, #8
	add x22, x22, #2
	subs w23, w23, #1
	b.ne Lgt_basemul_loop

	ldr x23, [sp, #48]
	ldp x21, x22, [sp, #32]
	ldp x19, x20, [sp, #16]
	ldp x29, x30, [sp], #64
	ret

.global poly_basemul_add
.global _poly_basemul_add
poly_basemul_add:
_poly_basemul_add:
	stp x29, x30, [sp, #-80]!
	mov x29, sp
	stp x19, x20, [sp, #16]
	stp x21, x22, [sp, #32]
	stp x23, x24, [sp, #48]

	mov x19, x0
	mov x20, x1
	mov x21, x2
	mov x22, x3
	adrp x23, _gt_rowbitrev_lambda@PAGE
	add x23, x23, _gt_rowbitrev_lambda@PAGEOFF
	mov w24, #192

Lgt_basemul_add_loop:
	mov x0, x19
	mov x1, x20
	mov x2, x21
	mov x3, x22
	ldrsh w4, [x23]
	bl _basemul_add

	add x19, x19, #8
	add x20, x20, #8
	add x21, x21, #8
	add x22, x22, #8
	add x23, x23, #2
	subs w24, w24, #1
	b.ne Lgt_basemul_add_loop

	ldp x23, x24, [sp, #48]
	ldp x21, x22, [sp, #32]
	ldp x19, x20, [sp, #16]
	ldp x29, x30, [sp], #80
	ret

.global poly_baseinv
.global _poly_baseinv
poly_baseinv:
_poly_baseinv:
	stp x29, x30, [sp, #-80]!
	mov x29, sp
	stp x19, x20, [sp, #16]
	stp x21, x22, [sp, #32]
	stp x23, x24, [sp, #48]

	mov x19, x0
	mov x20, x1
	adrp x21, _gt_rowbitrev_lambda@PAGE
	add x21, x21, _gt_rowbitrev_lambda@PAGEOFF
	mov w22, #192
	mov x23, x0

Lgt_baseinv_loop:
	mov x0, x19
	mov x1, x20
	ldrsh w2, [x21]
	bl _baseinv
	cbnz w0, Lgt_baseinv_fail

	add x19, x19, #8
	add x20, x20, #8
	add x21, x21, #2
	subs w22, w22, #1
	b.ne Lgt_baseinv_loop

	mov w0, #0
	b Lgt_baseinv_done

Lgt_baseinv_fail:
	mov x0, x23
	mov w24, #96

Lgt_baseinv_zero_loop:
	stp xzr, xzr, [x0], #16
	subs w24, w24, #1
	b.ne Lgt_baseinv_zero_loop
	mov w0, #1

Lgt_baseinv_done:
	ldp x23, x24, [sp, #48]
	ldp x21, x22, [sp, #32]
	ldp x19, x20, [sp, #16]
	ldp x29, x30, [sp], #80
	ret
