/*
 * Production keygen balanced HIER_K8 tree for 24 CQ denominators.
 *
 * ABI:
 *   x0 = int16_t den[24][8]
 *   w0 = 0 on success, 1 if any denominator product is zero
 *
 * The input/output layout is the coefficient-Q scratch layout used by the
 * fixed Direct-CQ key-generation pipeline.
 */

.text
.align 2

/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)@PAGE
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, C_SYM(sym)@PAGEOFF
#else
#define C_SYM(sym) sym
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, :lo12:C_SYM(sym)
#endif

#endif

.equ BPQ_TREE_C01_OFFSET, 0
.equ BPQ_TREE_GROUP_OFFSET, 128
.equ BPQ_TREE_LOCAL_BYTES, 256

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

.macro form_group_pair denoff, scratchoff
	ldp q2, q3, [x19, #(\denoff)]
	ldr q4, [x19, #(\denoff + 32)]
	ldp q5, q6, [x19, #(\denoff + 48)]
	ldr q7, [x19, #(\denoff + 80)]
	fqmul2 v8, v2, v3, v9, v5, v6
	stp q8, q9, [sp, #(BPQ_TREE_C01_OFFSET + \scratchoff)]
	fqmul2 v10, v8, v4, v11, v9, v7
	stp q10, q11, [sp, #(BPQ_TREE_GROUP_OFFSET + \scratchoff)]
.endm

/* Recover two adjacent three-denominator groups from two group inverses. */
.macro recover_group_pair denoff, c01off, group_inv0, group_inv1
	ldp q2, q3, [x19, #(\denoff)]
	ldr q4, [x19, #(\denoff + 32)]
	ldp q5, q6, [x19, #(\denoff + 48)]
	ldr q7, [x19, #(\denoff + 80)]
	ldp q8, q9, [sp, #(BPQ_TREE_C01_OFFSET + \c01off)]

	fqmul4 v10, v8, \group_inv0, v11, \group_inv0, v4, \
	         v12, v9, \group_inv1, v13, \group_inv1, v7
	fqmul4 v2, v2, v11, v3, v11, v3, \
	         v5, v5, v13, v6, v13, v6

	stp q3, q2, [x19, #(\denoff)]
	str q10, [x19, #(\denoff + 32)]
	stp q6, q5, [x19, #(\denoff + 48)]
	str q12, [x19, #(\denoff + 80)]
.endm

.global C_SYM(gt_keygen_baseinv_hier_k8)
#ifndef __APPLE__
.type C_SYM(gt_keygen_baseinv_hier_k8), %function
#endif
C_SYM(gt_keygen_baseinv_hier_k8):
	stp x30, x19, [sp, #-16]!
	stp d8, d9, [sp, #-16]!
	stp d10, d11, [sp, #-16]!
	stp d12, d13, [sp, #-16]!
	stp d14, d15, [sp, #-16]!
	sub sp, sp, #BPQ_TREE_LOCAL_BYTES

	mov x19, x0
	ldr q1, Lbpq_tree_scaled_r_consts

	/* Form c01[8] and the eight three-denominator group products. */
	form_group_pair 0, 0
	form_group_pair 96, 32
	form_group_pair 192, 64
	form_group_pair 288, 96

	/* Balanced forward tree: 8 -> 4 -> 2 -> 1. */
	ldp q2, q3, [sp, #BPQ_TREE_GROUP_OFFSET]
	ldp q4, q5, [sp, #(BPQ_TREE_GROUP_OFFSET + 32)]
	ldp q6, q7, [sp, #(BPQ_TREE_GROUP_OFFSET + 64)]
	ldp q14, q15, [sp, #(BPQ_TREE_GROUP_OFFSET + 96)]
	fqmul4 v8, v2, v3, v9, v4, v5, \
	         v10, v6, v7, v11, v14, v15
	fqmul2 v12, v8, v9, v13, v10, v11
	fqmul v0, v12, v13

	uminv h2, v0.8h
	umov w8, v2.h[0]
	cbz w8, Lbpq_tree_failure

	bl C_SYM(gt_fqinv15_asm)
	ldr q1, Lbpq_tree_scaled_r_consts

	/* Balanced backward tree: 1 -> 2 -> 4 -> 8. */
	fqmul2 v2, v0, v13, v3, v0, v12
	fqmul4 v4, v2, v9, v5, v2, v8, \
	         v6, v3, v11, v7, v3, v10

	ldp q2, q3, [sp, #BPQ_TREE_GROUP_OFFSET]
	ldp q8, q9, [sp, #(BPQ_TREE_GROUP_OFFSET + 32)]
	fqmul4 v12, v3, v4, v13, v2, v4, \
	         v14, v9, v5, v15, v8, v5
	ldp q2, q3, [sp, #(BPQ_TREE_GROUP_OFFSET + 64)]
	ldp q8, q9, [sp, #(BPQ_TREE_GROUP_OFFSET + 96)]
	fqmul4 v28, v3, v6, v29, v2, v6, \
	         v30, v9, v7, v31, v8, v7

	recover_group_pair 0, 0, v12, v13
	recover_group_pair 96, 32, v14, v15
	recover_group_pair 192, 64, v28, v29
	recover_group_pair 288, 96, v30, v31

	mov w0, wzr
	b Lbpq_tree_return

Lbpq_tree_failure:
	mov w0, #1

Lbpq_tree_return:
	/* P0-B: restore first, then erase local scratch and saved images. */
	ldp d14, d15, [sp, #(BPQ_TREE_LOCAL_BYTES + 0)]
	ldp d12, d13, [sp, #(BPQ_TREE_LOCAL_BYTES + 16)]
	ldp d10, d11, [sp, #(BPQ_TREE_LOCAL_BYTES + 32)]
	ldp d8, d9, [sp, #(BPQ_TREE_LOCAL_BYTES + 48)]
	ldp x30, x19, [sp, #(BPQ_TREE_LOCAL_BYTES + 64)]
	movi v1.16b, #0
	mov x9, sp
	mov x10, #21
Lbpq_tree_clear:
	str q1, [x9], #16
	subs x10, x10, #1
	b.ne Lbpq_tree_clear
	add sp, sp, #(BPQ_TREE_LOCAL_BYTES + 80)
	ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_baseinv_hier_k8), \
	.-C_SYM(gt_keygen_baseinv_hier_k8)
#endif

.p2align 4
Lbpq_tree_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0
