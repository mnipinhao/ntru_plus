/* Production keygen BPQ baseinv prepare, 24 groups. */

.text
.align 2

#include "../support/common.inc"

.global C_SYM(gt_keygen_baseinv_bpq_prepare)
#ifndef __APPLE__
.type C_SYM(gt_keygen_baseinv_bpq_prepare), %function
#endif
C_SYM(gt_keygen_baseinv_bpq_prepare):
	stp d8, d9, [sp, #-16]!
	stp d10, d11, [sp, #-16]!
	stp d12, d13, [sp, #-16]!
	stp d14, d15, [sp, #-16]!

	LOAD_ADDR_PAGE(x3, gt_keygen_bpq_lambda8)
	LOAD_ADDR_OFF(x3, gt_keygen_bpq_lambda8)
	ldr q0, Lbpq_prepare_scaled_r_consts
	mov w4, #24

Lbpq_prepare_slothy_loop:
#include "../../slothy/production/bpq_cq_keygen/prepare_group.n1.opt.inc"
	subs w4, w4, #1
	b.ne Lbpq_prepare_slothy_loop

	ldp d14, d15, [sp], #16
	ldp d12, d13, [sp], #16
	ldp d10, d11, [sp], #16
	ldp d8, d9, [sp], #16
	ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_baseinv_bpq_prepare), \
	.-C_SYM(gt_keygen_baseinv_bpq_prepare)
#endif

.p2align 4
Lbpq_prepare_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0
