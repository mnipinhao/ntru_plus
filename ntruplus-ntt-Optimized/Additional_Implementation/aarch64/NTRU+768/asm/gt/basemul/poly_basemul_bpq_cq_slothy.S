/* Production keygen mixed BPQ x scaled-R CQ basemul, CQ output. */

.text
.arch armv8-a
.p2align 4

#include "../support/common.inc"

.global C_SYM(gt_keygen_basemul_bpq_cq_to_cq_scaled_r)
#ifndef __APPLE__
.type C_SYM(gt_keygen_basemul_bpq_cq_to_cq_scaled_r), %function
#endif
C_SYM(gt_keygen_basemul_bpq_cq_to_cq_scaled_r):
    stp d8, d9, [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    LOAD_ADDR_PAGE(x3, gt_keygen_bpq_lambda8)
    LOAD_ADDR_OFF(x3, gt_keygen_bpq_lambda8)
    adr x4, .Lbpq_cq_scaled_r_consts
    ldr q0, [x4]
    mov w4, #6

.Lmixed_bpq_cq_quad_loop:
#include "../../slothy/production/bpq_cq_keygen/basemul_quad4.n1.opt.inc"
    subs w4, w4, #1
    b.ne .Lmixed_bpq_cq_quad_loop

    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8, d9, [sp], #64
    ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_basemul_bpq_cq_to_cq_scaled_r), \
    .-C_SYM(gt_keygen_basemul_bpq_cq_to_cq_scaled_r)
#endif

.text
.p2align 4
.Lbpq_cq_scaled_r_consts:
    .hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0

#ifndef __APPLE__
.section .note.GNU-stack,"",%progbits
#endif
