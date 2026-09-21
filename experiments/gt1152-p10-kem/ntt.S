/* NTRU+1152 full Forward wrapper; preserves d8-d15 once.
 *
 * x0 out, x1 in, x2 scratch: 2304 bytes provided by the caller.  This leaf
 * allocates no memory of its own, so the transform of f, g and the recovered
 * message lies in a buffer the C caller can name and clear.  Before this it
 * allocated the frame itself and never cleared it -- the same gap NTRU+864's
 * ntt.S had, inherited with the port.
 * Ported from NTRU+864's ntt.S: scratch 1792 -> 2304 bytes and the tail
 * region moves from +1536 to +2048, following the eight-bank layout. */
.text
.p2align 2
.global ntt_asm
.global _ntt_asm
ntt_asm:
_ntt_asm:
    stp x29, x30, [sp, #-112]!   // 16 more than before: x21 holds the scratch
    stp x19, x20, [sp, #16]
    str x21, [sp, #96]
    stp d8, d9, [sp, #32]
    stp d10, d11, [sp, #48]
    stp d12, d13, [sp, #64]
    stp d14, d15, [sp, #80]
    mov x29, sp
    mov x19, x0
    mov x20, x1
    mov x21, x2                 // scratch, 2304 bytes, caller-owned
    mov x0, x21
    mov x1, x20
    bl ntt_top_asm
    add x0, x21, #2048
    mov x1, x0
    bl ntt_tail_asm
    mov x0, x19
    mov x1, x21
    bl ntt9_asm
    ldp d14, d15, [sp, #80]
    ldp d12, d13, [sp, #64]
    ldp d10, d11, [sp, #48]
    ldp d8, d9, [sp, #32]
    ldr x21, [sp, #96]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #112
    ret

#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
