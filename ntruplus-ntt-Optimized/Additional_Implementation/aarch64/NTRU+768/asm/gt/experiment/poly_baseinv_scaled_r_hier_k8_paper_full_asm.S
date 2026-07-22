/*
 * Benchmark-only complete GT paper-HIER_K8 scaled base inverse.
 *
 * The prepare phase is the existing Slothy prepare2 kernel. The denominator
 * path is the balanced paper tree 8 -> 4 -> 2 -> 1 -> 2 -> 4 -> 8. Group
 * inverses are consumed immediately by two-group outer recovery, so they are
 * not stored and loaded through the group scratch array after fqinv15.
 */

.text
.align 2

#include "../support/common.inc"

.equ PAPER_K8_DEN_BYTES, 384
.equ PAPER_K8_C01_BYTES, 128
.equ PAPER_K8_GROUP_BYTES, 128
.equ PAPER_K8_LOCAL_BYTES, 640
.equ PAPER_K8_C01_OFFSET, PAPER_K8_DEN_BYTES
.equ PAPER_K8_GROUP_OFFSET, PAPER_K8_DEN_BYTES + PAPER_K8_C01_BYTES

.macro fqmul dst, lhs, rhs
	smull v16.4s, \lhs\().4h, \rhs\().4h
	smull2 v17.4s, \lhs\().8h, \rhs\().8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 \dst\().8h, v16.8h, v17.8h
.endm

.macro fqmul2 d0, l0, r0, d1, l1, r1
	smull v16.4s, \l0\().4h, \r0\().4h
	smull2 v17.4s, \l0\().8h, \r0\().8h
	smull v18.4s, \l1\().4h, \r1\().4h
	smull2 v19.4s, \l1\().8h, \r1\().8h
	uzp1 v20.8h, v16.8h, v17.8h
	uzp1 v21.8h, v18.8h, v19.8h
	mul v20.8h, v20.8h, v1.h[2]
	mul v21.8h, v21.8h, v1.h[2]
	smlal v16.4s, v20.4h, v1.h[0]
	smlal2 v17.4s, v20.8h, v1.h[0]
	smlal v18.4s, v21.4h, v1.h[0]
	smlal2 v19.4s, v21.8h, v1.h[0]
	uzp2 \d0\().8h, v16.8h, v17.8h
	uzp2 \d1\().8h, v18.8h, v19.8h
.endm

.macro fqmul4 d0, l0, r0, d1, l1, r1, d2, l2, r2, d3, l3, r3
	smull v16.4s, \l0\().4h, \r0\().4h
	smull2 v17.4s, \l0\().8h, \r0\().8h
	smull v18.4s, \l1\().4h, \r1\().4h
	smull2 v19.4s, \l1\().8h, \r1\().8h
	smull v20.4s, \l2\().4h, \r2\().4h
	smull2 v21.4s, \l2\().8h, \r2\().8h
	smull v22.4s, \l3\().4h, \r3\().4h
	smull2 v23.4s, \l3\().8h, \r3\().8h
	uzp1 v24.8h, v16.8h, v17.8h
	uzp1 v25.8h, v18.8h, v19.8h
	uzp1 v26.8h, v20.8h, v21.8h
	uzp1 v27.8h, v22.8h, v23.8h
	mul v24.8h, v24.8h, v1.h[2]
	mul v25.8h, v25.8h, v1.h[2]
	mul v26.8h, v26.8h, v1.h[2]
	mul v27.8h, v27.8h, v1.h[2]
	smlal v16.4s, v24.4h, v1.h[0]
	smlal2 v17.4s, v24.8h, v1.h[0]
	smlal v18.4s, v25.4h, v1.h[0]
	smlal2 v19.4s, v25.8h, v1.h[0]
	smlal v20.4s, v26.4h, v1.h[0]
	smlal2 v21.4s, v26.8h, v1.h[0]
	smlal v22.4s, v27.4h, v1.h[0]
	smlal2 v23.4s, v27.8h, v1.h[0]
	uzp2 \d0\().8h, v16.8h, v17.8h
	uzp2 \d1\().8h, v18.8h, v19.8h
	uzp2 \d2\().8h, v20.8h, v21.8h
	uzp2 \d3\().8h, v22.8h, v23.8h
.endm

/* Recover two adjacent three-denominator groups from two live group inverses. */
.macro recover_group_pair denoff, c01off, group_inv0, group_inv1
	ldp q2, q3, [x21, #\denoff]
	ldr q4, [x21, #(\denoff + 32)]
	ldp q5, q6, [x21, #(\denoff + 48)]
	ldr q7, [x21, #(\denoff + 80)]
	ldp q8, q9, [x22, #\c01off]

	fqmul4 v10, v8, \group_inv0, v11, \group_inv0, v4, \
	         v12, v9, \group_inv1, v13, \group_inv1, v7
	fqmul4 v2, v2, v11, v3, v11, v3, \
	         v5, v5, v13, v6, v13, v6

	stp q3, q2, [x21, #\denoff]
	str q10, [x21, #(\denoff + 32)]
	stp q6, q5, [x21, #(\denoff + 48)]
	str q12, [x21, #(\denoff + 80)]
.endm

.global C_SYM(poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate)
#ifndef __APPLE__
.type C_SYM(poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate), %function
#endif
C_SYM(poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate):
	stp x30, x19, [sp, #-16]!
	stp x20, x21, [sp, #-16]!
	stp x22, x23, [sp, #-16]!
	stp d8, d9, [sp, #-16]!
	stp d10, d11, [sp, #-16]!
	stp d12, d13, [sp, #-16]!
	stp d14, d15, [sp, #-16]!
	sub sp, sp, #PAPER_K8_LOCAL_BYTES

	mov x19, x0
	mov x20, x1
	mov x21, sp
	add x22, sp, #PAPER_K8_C01_OFFSET
	add x23, sp, #PAPER_K8_GROUP_OFFSET

	/* Prepare numerators, 24 denominators, c01[8], and group[8]. */
	mov x0, x19
	mov x1, x21
	mov x2, x22
	mov x3, x23
	mov x4, x20
	LOAD_ADDR_PAGE(x5, gt_rowbitrev_lambda)
	LOAD_ADDR_OFF(x5, gt_rowbitrev_lambda)
	adr x6, Lpaper_k8_scaled_r_consts
	bl C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm)

	ldr q1, Lpaper_k8_scaled_r_consts

	/* Balanced forward tree: 8 -> 4 -> 2 -> 1. */
	ldp q2, q3, [x23]
	ldp q4, q5, [x23, #32]
	ldp q6, q7, [x23, #64]
	ldp q14, q15, [x23, #96]
	fqmul4 v8, v2, v3, v9, v4, v5, \
	         v10, v6, v7, v11, v14, v15
	fqmul2 v12, v8, v9, v13, v10, v11
	fqmul v0, v12, v13

	uminv h2, v0.8h
	umov w8, v2.h[0]
	cbz w8, Lpaper_k8_failure

	bl C_SYM(gt_fqinv15_asm)
	ldr q1, Lpaper_k8_scaled_r_consts

	/* Balanced backward tree: 1 -> 2 -> 4. */
	fqmul2 v2, v0, v13, v3, v0, v12
	fqmul4 v4, v2, v9, v5, v2, v8, \
	         v6, v3, v11, v7, v3, v10

	/* Recover all group inverses while l4_inv[0..3] remain live. */
	ldp q2, q3, [x23]
	ldp q8, q9, [x23, #32]
	fqmul4 v12, v3, v4, v13, v2, v4, \
	         v14, v9, v5, v15, v8, v5
	ldp q2, q3, [x23, #64]
	ldp q8, q9, [x23, #96]
	fqmul4 v28, v3, v6, v29, v2, v6, \
	         v30, v9, v7, v31, v8, v7

	/* Consume group inverses in two-group windows without memory round trips. */
	recover_group_pair 0, 0, v12, v13
	recover_group_pair 96, 32, v14, v15
	recover_group_pair 192, 64, v28, v29
	recover_group_pair 288, 96, v30, v31

	mov x0, x19
	mov x1, x21
	bl C_SYM(baseinv_batch_finish24_n1_asm)
	mov w0, wzr
	b Lpaper_k8_return

Lpaper_k8_failure:
	mov x0, x19
	mov w1, wzr
	mov x2, #1536
	bl C_SYM(memset)
	mov w0, #1

Lpaper_k8_return:
	add sp, sp, #PAPER_K8_LOCAL_BYTES
	ldp d14, d15, [sp], #16
	ldp d12, d13, [sp], #16
	ldp d10, d11, [sp], #16
	ldp d8, d9, [sp], #16
	ldp x22, x23, [sp], #16
	ldp x20, x21, [sp], #16
	ldp x30, x19, [sp], #16
	ret
#ifndef __APPLE__
.size C_SYM(poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate), \
	.-C_SYM(poly_baseinv_scaled_r_hier_k8_paper_full_asm_candidate)
#endif

.p2align 4
Lpaper_k8_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0
