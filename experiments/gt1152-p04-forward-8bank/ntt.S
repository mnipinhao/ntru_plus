/* NTRU+1152 full Forward wrapper; preserves d8-d15 once.
 * Ported from NTRU+864's ntt.S: scratch 1792 -> 2304 bytes and the tail
 * region moves from +1536 to +2048, following the eight-bank layout. */
.text
.p2align 2
.global ntt_asm
.global _ntt_asm
ntt_asm:
_ntt_asm:
    stp x29, x30, [sp, #-96]!
    stp x19, x20, [sp, #16]
    stp d8, d9, [sp, #32]
    stp d10, d11, [sp, #48]
    stp d12, d13, [sp, #64]
    stp d14, d15, [sp, #80]
    mov x29, sp
    mov x19, x0
    mov x20, x1
    sub sp, sp, #2304
    mov x0, sp
    mov x1, x20
    bl ntt_top_asm
    add x0, sp, #2048
    mov x1, x0
    bl ntt_tail_asm
    mov x0, x19
    mov x1, sp
    bl ntt9_asm
    add sp, sp, #2304
    ldp d14, d15, [sp, #80]
    ldp d12, d13, [sp, #64]
    ldp d10, d11, [sp, #48]
    ldp d8, d9, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #96
    ret

#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
