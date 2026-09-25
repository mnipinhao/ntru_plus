/* P139: AAPCS64 wrappers for the NTRU+768 internal entry points that clobber d8-d15 (their ABI mask
 * in test_abi is non-zero; the KEM reaches them through kem_api.S for the same reason). */
#ifdef __APPLE__
#define SYM(s) _##s
#else
#define SYM(s) s
#endif
.macro WRAP name, target
.text
.p2align 2
.global SYM(\name)
SYM(\name):
    stp x29, x30, [sp, #-80]!
    mov x29, sp
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    bl SYM(\target)
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    ldp x29, x30, [sp], #80
    ret
.endm
WRAP w_poly_cbd1, poly_cbd1
WRAP w_poly_sotp_encode, poly_sotp_encode
WRAP w_poly_sotp_decode, poly_sotp_decode
WRAP w_poly_triple, poly_triple
#if defined(__linux__) && defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
