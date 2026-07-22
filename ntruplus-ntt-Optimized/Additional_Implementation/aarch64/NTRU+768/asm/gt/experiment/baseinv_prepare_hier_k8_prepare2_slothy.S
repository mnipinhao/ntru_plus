/*
 * Benchmark-only wrapper for the Slothy-scheduled HIERK8 prepare2 group.
 * The included region processes one group of three quartic blocks and advances
 * x0-x5 according to experiments/baseinv_hier_k8/slothy_prepare2 contracts.
 */

.text
.align 2

#include "../support/common.inc"

.global C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm)
#ifndef __APPLE__
.type C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm), %function
#endif
C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm):
	sub sp, sp, #64
	stp d8, d9, [sp, #0]
	stp d10, d11, [sp, #16]
	stp d12, d13, [sp, #32]
	stp d14, d15, [sp, #48]

	ldr q0, [x6]
	mov x7, #8

Lprepare_hier_k8_prepare2_slothy_group_loop:
#include "../../../experiments/baseinv_hier_k8/slothy_prepare2/prepare2_group.opt.region.inc"
	subs x7, x7, #1
	b.ne Lprepare_hier_k8_prepare2_slothy_group_loop

	ldp d8, d9, [sp, #0]
	ldp d10, d11, [sp, #16]
	ldp d12, d13, [sp, #32]
	ldp d14, d15, [sp, #48]
	add sp, sp, #64
	ret
#ifndef __APPLE__
.size C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm), \
	.-C_SYM(baseinv_prepare_hier_k8_group_products_prepare2_slothy_asm)
#endif
