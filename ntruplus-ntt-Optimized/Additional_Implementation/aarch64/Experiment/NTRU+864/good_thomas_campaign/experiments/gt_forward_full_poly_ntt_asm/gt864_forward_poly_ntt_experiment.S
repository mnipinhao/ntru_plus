/*
 * M5O Experiment-only full Forward composition.
 *
 * x0: 864-int16 FR-0 output
 * x1: 864-int16 natural-order input
 * Contract: x0 and x1 are disjoint.  The fixed stack object is the
 * 896-int16 P8-plus-tail buffer passed between the two frozen kernels.
 */
.text
.p2align 2
.global gt864_forward_poly_ntt_experiment
.global _gt864_forward_poly_ntt_experiment
gt864_forward_poly_ntt_experiment:
_gt864_forward_poly_ntt_experiment:
    stp x29, x30, [sp, #-32]!
    stp x19, x20, [sp, #16]
    mov x29, sp
    mov x19, x0
    mov x20, x1

    sub sp, sp, #1792
    mov x0, sp
    mov x1, x20
    bl gt864_top_split_ld3

    mov x0, x19
    mov x1, sp
    bl gt864_forward_six_bank_pass2
    add sp, sp, #1792

    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #32
    ret
