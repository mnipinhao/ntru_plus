/*
 * Benchmark-only fused GT baseinv prepare and HIER_K8 group formation.
 *
 * ABI:
 *   x0 = numerator output, 24 block-major blocks of 32 int16 coefficients
 *   x1 = denominator output, 24 vectors of 8 int16 coefficients
 *   x2 = c01 output, 8 vectors of 8 int16 coefficients
 *   x3 = group-product output, 8 vectors of 8 int16 coefficients
 *   x4 = block-major input, 24 blocks of 32 int16 coefficients
 *   x5 = lambda input, 24 vectors of 8 int16 coefficients
 *   x6 = scaled-R constants, 8 int16 coefficients
 *
 * Each loop iteration prepares three denominator vectors and forms
 *   c01 = d0 * d1
 *   group_product = c01 * d2
 * while d0/d1/c01 remain in v8/v9/v10. This removes the C prepare-call and
 * stack round-trip at the prepare -> HIER_K8 boundary.
 */

.text
.align 2

#include "../support/common.inc"

.macro fqmul_keep dst, lhs, rhs
	smull v12.4s, \lhs\().4h, \rhs\().4h
	smull2 v13.4s, \lhs\().8h, \rhs\().8h
	uzp1 v14.8h, v12.8h, v13.8h
	mul v14.8h, v14.8h, v1.h[2]
	smlal v12.4s, v14.4h, v1.h[0]
	smlal2 v13.4s, v14.8h, v1.h[0]
	uzp2 \dst\().8h, v12.8h, v13.8h
.endm

/*
 * Compiler-validated baseinv_8_prepare schedule. The denominator is returned
 * in v4; the four numerator vectors are stored in block-major order. v8-v15
 * are deliberately untouched so the enclosing group keeps d0/d1/c01 live.
 */
.macro prepare_one
	ldr q0, [x5], #16
	ld4 {v24.8h-v27.8h}, [x4], #64
	mov v29.16b, v0.16b
	smull v16.4s, v27.4h, v27.4h
	smull2 v31.4s, v27.8h, v27.8h
	neg v7.8h, v27.8h
	smull2 v18.4s, v26.8h, v26.8h
	smull v4.4s, v26.4h, v26.4h
	uzp1 v6.8h, v16.8h, v31.8h
	shl v7.8h, v7.8h, #1
	neg v20.8h, v26.8h
	mov v30.16b, v26.16b
	mul v6.8h, v6.8h, v1.h[2]
	smlal2 v18.4s, v25.8h, v7.8h
	smlal v4.4s, v25.4h, v7.4h
	shl v20.8h, v20.8h, #1
	smlal v16.4s, v6.4h, v1.h[0]
	smlal2 v31.4s, v6.8h, v1.h[0]
	uzp1 v5.8h, v4.8h, v18.8h
	mov v22.16b, v25.16b
	mov v21.16b, v27.16b
	uzp2 v31.8h, v16.8h, v31.8h
	mul v5.8h, v5.8h, v1.h[2]
	mov v23.16b, v24.16b
	smull v19.4s, v31.4h, v0.4h
	smull2 v31.4s, v31.8h, v0.8h
	smlal v4.4s, v5.4h, v1.h[0]
	smlal2 v18.4s, v5.8h, v1.h[0]
	smlal v19.4s, v25.4h, v25.4h
	smlal2 v31.4s, v25.8h, v25.8h
	uzp2 v18.8h, v4.8h, v18.8h
	smlal v19.4s, v24.4h, v20.4h
	smlal2 v31.4s, v24.8h, v20.8h
	smull v17.4s, v18.4h, v0.4h
	smull2 v18.4s, v18.8h, v0.8h
	uzp1 v3.8h, v19.8h, v31.8h
	smlal v17.4s, v24.4h, v24.4h
	smlal2 v18.4s, v24.8h, v24.8h
	mul v3.8h, v3.8h, v1.h[2]
	uzp1 v28.8h, v17.8h, v18.8h
	smlal v19.4s, v3.4h, v1.h[0]
	smlal2 v31.4s, v3.8h, v1.h[0]
	mul v28.8h, v28.8h, v1.h[2]
	uzp2 v31.8h, v19.8h, v31.8h
	smlal v17.4s, v28.4h, v1.h[0]
	smlal2 v18.4s, v28.8h, v1.h[0]
	smull v0.4s, v31.4h, v0.4h
	smull2 v29.4s, v31.8h, v29.8h
	neg v7.8h, v31.8h
	uzp2 v18.8h, v17.8h, v18.8h
	uzp1 v2.8h, v0.8h, v29.8h
	smull v16.4s, v24.4h, v18.4h
	smull2 v28.4s, v24.8h, v18.8h
	mul v2.8h, v2.8h, v1.h[2]
	smull v5.4s, v18.4h, v18.4h
	smull2 v4.4s, v18.8h, v18.8h
	smull2 v30.4s, v30.8h, v18.8h
	smlal v0.4s, v2.4h, v1.h[0]
	smlal2 v29.4s, v2.8h, v1.h[0]
	smlal2 v30.4s, v23.8h, v31.8h
	uzp2 v29.8h, v0.8h, v29.8h
	smlal v16.4s, v26.4h, v29.4h
	smlal2 v28.4s, v26.8h, v29.8h
	smull v17.4s, v27.4h, v29.4h
	smull v26.4s, v26.4h, v18.4h
	smlal v5.4s, v7.4h, v29.4h
	smlal2 v4.4s, v7.8h, v29.8h
	smlal v17.4s, v25.4h, v18.4h
	smlal v26.4s, v24.4h, v31.4h
	smull2 v29.4s, v21.8h, v29.8h
	smull v25.4s, v25.4h, v31.4h
	smull2 v31.4s, v22.8h, v31.8h
	uzp1 v6.8h, v5.8h, v4.8h
	smlal2 v29.4s, v22.8h, v18.8h
	smlal v25.4s, v27.4h, v18.4h
	smlal2 v31.4s, v21.8h, v18.8h
	uzp1 v3.8h, v16.8h, v28.8h
	uzp1 v2.8h, v17.8h, v29.8h
	uzp1 v0.8h, v26.8h, v30.8h
	uzp1 v19.8h, v25.8h, v31.8h
	mul v6.8h, v6.8h, v1.h[2]
	mul v3.8h, v3.8h, v1.h[2]
	mul v2.8h, v2.8h, v1.h[2]
	mul v0.8h, v0.8h, v1.h[2]
	mul v19.8h, v19.8h, v1.h[2]
	smlal v5.4s, v6.4h, v1.h[0]
	smlal2 v4.4s, v6.8h, v1.h[0]
	smlal v16.4s, v3.4h, v1.h[0]
	smlal2 v28.4s, v3.8h, v1.h[0]
	smlal v17.4s, v2.4h, v1.h[0]
	smlal2 v29.4s, v2.8h, v1.h[0]
	smlal v26.4s, v0.4h, v1.h[0]
	smlal2 v30.4s, v0.8h, v1.h[0]
	smlal v25.4s, v19.4h, v1.h[0]
	smlal2 v31.4s, v19.8h, v1.h[0]
	uzp2 v4.8h, v5.8h, v4.8h
	uzp2 v28.8h, v16.8h, v28.8h
	uzp2 v29.8h, v17.8h, v29.8h
	uzp2 v30.8h, v26.8h, v30.8h
	uzp2 v31.8h, v25.8h, v31.8h
	st4 {v28.8h-v31.8h}, [x0], #64
.endm

/*
 * Two-block prepare derived from the KPQC-final poly_baseinv_1 schedule.
 * GT uses ld4/st4 because its block-major memory contract interleaves the four
 * quartic coefficients. The two resulting denominators are reduced in v19/v20
 * and their c01 product is left in v1 before the numerator tail overwrites the
 * determinant temporaries.
 */
.macro prepare_two_and_c01
	ld1 {v1.8h, v2.8h}, [x5], #32
	ld4 {v3.8h-v6.8h}, [x4], #64
	ld4 {v7.8h-v10.8h}, [x4], #64

	neg v26.8h, v6.8h
	neg v30.8h, v10.8h
	neg v27.8h, v5.8h
	neg v31.8h, v9.8h
	shl v26.8h, v26.8h, #1
	shl v30.8h, v30.8h, #1
	shl v27.8h, v27.8h, #1
	shl v31.8h, v31.8h, #1

	smull v11.4s, v5.4h, v5.4h
	smull2 v12.4s, v5.8h, v5.8h
	smull v13.4s, v9.4h, v9.4h
	smull2 v14.4s, v9.8h, v9.8h
	smull v15.4s, v6.4h, v6.4h
	smull2 v16.4s, v6.8h, v6.8h
	smull v17.4s, v10.4h, v10.4h
	smull2 v18.4s, v10.8h, v10.8h
	smlal v11.4s, v4.4h, v26.4h
	smlal2 v12.4s, v4.8h, v26.8h
	smlal v13.4s, v8.4h, v30.4h
	smlal2 v14.4s, v8.8h, v30.8h

	uzp1 v21.8h, v15.8h, v16.8h
	uzp1 v22.8h, v17.8h, v18.8h
	uzp1 v19.8h, v11.8h, v12.8h
	uzp1 v20.8h, v13.8h, v14.8h
	mul v21.8h, v21.8h, v0.h[2]
	mul v22.8h, v22.8h, v0.h[2]
	mul v19.8h, v19.8h, v0.h[2]
	mul v20.8h, v20.8h, v0.h[2]
	smlal v15.4s, v21.4h, v0.h[0]
	smlal2 v16.4s, v21.8h, v0.h[0]
	smlal v17.4s, v22.4h, v0.h[0]
	smlal2 v18.4s, v22.8h, v0.h[0]
	smlal v11.4s, v19.4h, v0.h[0]
	smlal2 v12.4s, v19.8h, v0.h[0]
	smlal v13.4s, v20.4h, v0.h[0]
	smlal2 v14.4s, v20.8h, v0.h[0]

	uzp2 v25.8h, v15.8h, v16.8h
	uzp2 v29.8h, v17.8h, v18.8h
	uzp2 v24.8h, v11.8h, v12.8h
	uzp2 v28.8h, v13.8h, v14.8h
	smull v15.4s, v25.4h, v1.4h
	smull2 v16.4s, v25.8h, v1.8h
	smull v17.4s, v29.4h, v2.4h
	smull2 v18.4s, v29.8h, v2.8h
	smull v11.4s, v24.4h, v1.4h
	smull2 v12.4s, v24.8h, v1.8h
	smull v13.4s, v28.4h, v2.4h
	smull2 v14.4s, v28.8h, v2.8h
	smlal v15.4s, v4.4h, v4.4h
	smlal2 v16.4s, v4.8h, v4.8h
	smlal v17.4s, v8.4h, v8.4h
	smlal2 v18.4s, v8.8h, v8.8h
	smlal v11.4s, v3.4h, v3.4h
	smlal2 v12.4s, v3.8h, v3.8h
	smlal v13.4s, v7.4h, v7.4h
	smlal2 v14.4s, v7.8h, v7.8h
	smlal v15.4s, v3.4h, v27.4h
	smlal2 v16.4s, v3.8h, v27.8h
	smlal v17.4s, v7.4h, v31.4h
	smlal2 v18.4s, v7.8h, v31.8h

	uzp1 v19.8h, v11.8h, v12.8h
	uzp1 v20.8h, v13.8h, v14.8h
	uzp1 v21.8h, v15.8h, v16.8h
	uzp1 v22.8h, v17.8h, v18.8h
	mul v19.8h, v19.8h, v0.h[2]
	mul v20.8h, v20.8h, v0.h[2]
	mul v21.8h, v21.8h, v0.h[2]
	mul v22.8h, v22.8h, v0.h[2]
	smlal v11.4s, v19.4h, v0.h[0]
	smlal2 v12.4s, v19.8h, v0.h[0]
	smlal v13.4s, v20.4h, v0.h[0]
	smlal2 v14.4s, v20.8h, v0.h[0]
	smlal v15.4s, v21.4h, v0.h[0]
	smlal2 v16.4s, v21.8h, v0.h[0]
	smlal v17.4s, v22.4h, v0.h[0]
	smlal2 v18.4s, v22.8h, v0.h[0]

	uzp2 v24.8h, v11.8h, v12.8h
	uzp2 v28.8h, v13.8h, v14.8h
	uzp2 v25.8h, v15.8h, v16.8h
	uzp2 v29.8h, v17.8h, v18.8h
	smull v11.4s, v25.4h, v1.4h
	smull2 v12.4s, v25.8h, v1.8h
	smull v13.4s, v29.4h, v2.4h
	smull2 v14.4s, v29.8h, v2.8h
	uzp1 v19.8h, v11.8h, v12.8h
	uzp1 v20.8h, v13.8h, v14.8h
	mul v19.8h, v19.8h, v0.h[2]
	mul v20.8h, v20.8h, v0.h[2]
	smlal v11.4s, v19.4h, v0.h[0]
	smlal2 v12.4s, v19.8h, v0.h[0]
	smlal v13.4s, v20.4h, v0.h[0]
	smlal2 v14.4s, v20.8h, v0.h[0]
	uzp2 v26.8h, v11.8h, v12.8h
	uzp2 v30.8h, v13.8h, v14.8h
	neg v27.8h, v25.8h
	neg v31.8h, v29.8h

	smull v11.4s, v24.4h, v24.4h
	smull2 v12.4s, v24.8h, v24.8h
	smull v13.4s, v28.4h, v28.4h
	smull2 v14.4s, v28.8h, v28.8h
	smlal v11.4s, v27.4h, v26.4h
	smlal2 v12.4s, v27.8h, v26.8h
	smlal v13.4s, v31.4h, v30.4h
	smlal2 v14.4s, v31.8h, v30.8h
	uzp1 v19.8h, v11.8h, v12.8h
	uzp1 v20.8h, v13.8h, v14.8h
	mul v19.8h, v19.8h, v0.h[2]
	mul v20.8h, v20.8h, v0.h[2]
	smlal v11.4s, v19.4h, v0.h[0]
	smlal2 v12.4s, v19.8h, v0.h[0]
	smlal v13.4s, v20.4h, v0.h[0]
	smlal2 v14.4s, v20.8h, v0.h[0]
	uzp2 v19.8h, v11.8h, v12.8h
	uzp2 v20.8h, v13.8h, v14.8h
	stp q19, q20, [x1], #32

	/* c01 = MontgomeryReduce(den0 * den1); v1/v2 are now dead. */
	smull v11.4s, v19.4h, v20.4h
	smull2 v12.4s, v19.8h, v20.8h
	uzp1 v1.8h, v11.8h, v12.8h
	mul v1.8h, v1.8h, v0.h[2]
	smlal v11.4s, v1.4h, v0.h[0]
	smlal2 v12.4s, v1.8h, v0.h[0]
	uzp2 v1.8h, v11.8h, v12.8h

	/* Numerator for the first block. */
	smull v11.4s, v3.4h, v24.4h
	smull2 v12.4s, v3.8h, v24.8h
	smull v13.4s, v6.4h, v26.4h
	smull2 v14.4s, v6.8h, v26.8h
	smull v15.4s, v5.4h, v24.4h
	smull2 v16.4s, v5.8h, v24.8h
	smull v17.4s, v4.4h, v25.4h
	smull2 v18.4s, v4.8h, v25.8h
	smlal v11.4s, v5.4h, v26.4h
	smlal2 v12.4s, v5.8h, v26.8h
	smlal v13.4s, v4.4h, v24.4h
	smlal2 v14.4s, v4.8h, v24.8h
	smlal v15.4s, v3.4h, v25.4h
	smlal2 v16.4s, v3.8h, v25.8h
	smlal v17.4s, v6.4h, v24.4h
	smlal2 v18.4s, v6.8h, v24.8h
	uzp1 v19.8h, v11.8h, v12.8h
	uzp1 v20.8h, v13.8h, v14.8h
	uzp1 v21.8h, v15.8h, v16.8h
	uzp1 v22.8h, v17.8h, v18.8h
	mul v19.8h, v19.8h, v0.h[2]
	mul v20.8h, v20.8h, v0.h[2]
	mul v21.8h, v21.8h, v0.h[2]
	mul v22.8h, v22.8h, v0.h[2]
	smlal v11.4s, v19.4h, v0.h[0]
	smlal2 v12.4s, v19.8h, v0.h[0]
	smlal v13.4s, v20.4h, v0.h[0]
	smlal2 v14.4s, v20.8h, v0.h[0]
	smlal v15.4s, v21.4h, v0.h[0]
	smlal2 v16.4s, v21.8h, v0.h[0]
	smlal v17.4s, v22.4h, v0.h[0]
	smlal2 v18.4s, v22.8h, v0.h[0]
	uzp2 v11.8h, v11.8h, v12.8h
	uzp2 v12.8h, v13.8h, v14.8h
	uzp2 v13.8h, v15.8h, v16.8h
	uzp2 v14.8h, v17.8h, v18.8h
	st4 {v11.8h-v14.8h}, [x0], #64

	/* Numerator for the second block. */
	smull v11.4s, v7.4h, v28.4h
	smull2 v12.4s, v7.8h, v28.8h
	smull v13.4s, v10.4h, v30.4h
	smull2 v14.4s, v10.8h, v30.8h
	smull v15.4s, v9.4h, v28.4h
	smull2 v16.4s, v9.8h, v28.8h
	smull v17.4s, v8.4h, v29.4h
	smull2 v18.4s, v8.8h, v29.8h
	smlal v11.4s, v9.4h, v30.4h
	smlal2 v12.4s, v9.8h, v30.8h
	smlal v13.4s, v8.4h, v28.4h
	smlal2 v14.4s, v8.8h, v28.8h
	smlal v15.4s, v7.4h, v29.4h
	smlal2 v16.4s, v7.8h, v29.8h
	smlal v17.4s, v10.4h, v28.4h
	smlal2 v18.4s, v10.8h, v28.8h
	uzp1 v19.8h, v11.8h, v12.8h
	uzp1 v20.8h, v13.8h, v14.8h
	uzp1 v21.8h, v15.8h, v16.8h
	uzp1 v22.8h, v17.8h, v18.8h
	mul v19.8h, v19.8h, v0.h[2]
	mul v20.8h, v20.8h, v0.h[2]
	mul v21.8h, v21.8h, v0.h[2]
	mul v22.8h, v22.8h, v0.h[2]
	smlal v11.4s, v19.4h, v0.h[0]
	smlal2 v12.4s, v19.8h, v0.h[0]
	smlal v13.4s, v20.4h, v0.h[0]
	smlal2 v14.4s, v20.8h, v0.h[0]
	smlal v15.4s, v21.4h, v0.h[0]
	smlal2 v16.4s, v21.8h, v0.h[0]
	smlal v17.4s, v22.4h, v0.h[0]
	smlal2 v18.4s, v22.8h, v0.h[0]
	uzp2 v11.8h, v11.8h, v12.8h
	uzp2 v12.8h, v13.8h, v14.8h
	uzp2 v13.8h, v15.8h, v16.8h
	uzp2 v14.8h, v17.8h, v18.8h
	st4 {v11.8h-v14.8h}, [x0], #64
.endm

.global C_SYM(baseinv_prepare_hier_k8_group_products_asm)
#ifndef __APPLE__
.type C_SYM(baseinv_prepare_hier_k8_group_products_asm), %function
#endif
C_SYM(baseinv_prepare_hier_k8_group_products_asm):
	sub sp, sp, #64
	stp d8, d9, [sp, #0]
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	ldr q1, [x6]
	mov x7, #8

Lprepare_hier_k8_group_loop:
	prepare_one
	mov v8.16b, v4.16b

	prepare_one
	mov v9.16b, v4.16b
	fqmul_keep v10, v8, v9

	prepare_one
	fqmul_keep v11, v10, v4

	stp q8, q9, [x1], #32
	str q4, [x1], #16
	str q10, [x2], #16
	str q11, [x3], #16

	subs x7, x7, #1
	b.ne Lprepare_hier_k8_group_loop

	ldp d8, d9, [sp, #0]
	ldp d10, d11, [sp, #16]
	ldp d12, d13, [sp, #32]
	ldp d14, d15, [sp, #48]
	add sp, sp, #64
	ret
#ifndef __APPLE__
.size C_SYM(baseinv_prepare_hier_k8_group_products_asm), \
	.-C_SYM(baseinv_prepare_hier_k8_group_products_asm)
#endif

.global C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_asm)
#ifndef __APPLE__
.type C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_asm), %function
#endif
C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_asm):
	sub sp, sp, #64
	stp d8, d9, [sp, #0]
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	ldr q0, [x6]
	mov x7, #8

Lprepare_hier_k8_prepare2_group_loop:
slothy_start_baseinv_prepare2_group_baseline:
	prepare_two_and_c01
	mov v10.16b, v1.16b
	mov v1.16b, v0.16b

	prepare_one
	fqmul_keep v11, v10, v4

	str q4, [x1], #16
	str q10, [x2], #16
	str q11, [x3], #16
	mov v0.16b, v1.16b
slothy_end_baseinv_prepare2_group_baseline:

	subs x7, x7, #1
	b.ne Lprepare_hier_k8_prepare2_group_loop

	ldp d8, d9, [sp, #0]
	ldp d10, d11, [sp, #16]
	ldp d12, d13, [sp, #32]
	ldp d14, d15, [sp, #48]
	add sp, sp, #64
	ret
#ifndef __APPLE__
.size C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_asm), \
	.-C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_asm)
#endif
