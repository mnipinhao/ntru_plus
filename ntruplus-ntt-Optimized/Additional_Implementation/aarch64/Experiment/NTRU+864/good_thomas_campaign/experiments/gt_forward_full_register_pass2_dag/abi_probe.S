.text
.p2align 2
.global gt864_m5r_abi_probe
.global _gt864_m5r_abi_probe
gt864_m5r_abi_probe:
_gt864_m5r_abi_probe:
    stp x29, x30, [sp, #-96]!
    stp x19, x20, [sp, #16]
    str x21, [sp, #32]
    stp d8, d9, [sp, #40]
    stp d10, d11, [sp, #56]
    stp d12, d13, [sp, #72]
    str d14, [sp, #88]
    sub sp, sp, #16
    str d15, [sp]
    mov x29, sp
    mov x19, x0
    mov x20, x1
    mov x21, x2

    mov x3, #0x108
    fmov d8, x3
    mov x3, #0x109
    fmov d9, x3
    mov x3, #0x10a
    fmov d10, x3
    mov x3, #0x10b
    fmov d11, x3
    mov x3, #0x10c
    fmov d12, x3
    mov x3, #0x10d
    fmov d13, x3
    mov x3, #0x10e
    fmov d14, x3
    mov x3, #0x10f
    fmov d15, x3

    mov x0, x19
    mov x1, x20
    bl gt864_forward_poly_ntt_full_register

    stp d8, d9, [x21, #0]
    stp d10, d11, [x21, #16]
    stp d12, d13, [x21, #32]
    stp d14, d15, [x21, #48]

    ldr d15, [sp]
    add sp, sp, #16
    ldr d14, [sp, #88]
    ldp d12, d13, [sp, #72]
    ldp d10, d11, [sp, #56]
    ldp d8, d9, [sp, #40]
    ldr x21, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret
