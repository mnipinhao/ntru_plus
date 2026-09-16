.text
.macro WRAP name, core
.global _\name
_\name:
    stp x29, x30, [sp, #-80]!
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    bl _\core
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    ldp x29, x30, [sp], #80
    ret
.endm
WRAP test_binv_num, binv_num_fused_tile
WRAP test_binv_finish, binv_finish_nocenter_tile
