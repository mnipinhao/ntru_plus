/* Test-only AAPCS wrapper: eight pointer arguments, all-32-vector internal core. */
.text
.macro WRAP name, core
.global _\name
_\name:
    stp x29, x30, [sp, #-80]!
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    mov x9, x7
    mov x7, x6
    mov x6, x5
    bl _\core
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    ldp x29, x30, [sp], #80
    ret
.endm
WRAP test_small, pair_merge_small
WRAP test_full, pair_merge_full
