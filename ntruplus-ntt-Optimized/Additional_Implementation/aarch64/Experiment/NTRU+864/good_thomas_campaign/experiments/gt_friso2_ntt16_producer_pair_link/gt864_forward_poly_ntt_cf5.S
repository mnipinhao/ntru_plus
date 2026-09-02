/* M5U-CF5 linked correctness-only Forward wrapper; preserves d8-d15 once. */
.text
.p2align 2
.global gt864_forward_poly_ntt_cf5
.global _gt864_forward_poly_ntt_cf5
gt864_forward_poly_ntt_cf5:
_gt864_forward_poly_ntt_cf5:
    stp x29, x30, [sp, #-96]!
    stp x19, x20, [sp, #16]
    stp d8, d9, [sp, #32]
    stp d10, d11, [sp, #48]
    stp d12, d13, [sp, #64]
    stp d14, d15, [sp, #80]
    mov x29, sp
    mov x19, x0
    mov x20, x1
    sub sp, sp, #1792
    mov x0, sp
    mov x1, x20
    bl gt864_top_split_ld3
    mov x0, x19
    mov x1, sp
    bl gt864_forward_six_bank_pass2_cf5
    add sp, sp, #1792
    ldp d14, d15, [sp, #80]
    ldp d12, d13, [sp, #64]
    ldp d10, d11, [sp, #48]
    ldp d8, d9, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret
