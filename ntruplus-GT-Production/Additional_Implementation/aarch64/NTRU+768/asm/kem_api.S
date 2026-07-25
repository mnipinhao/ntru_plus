.text
.align 2

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif

/*
 * The selected leaf support kernels use a closed-world internal SIMD ABI.
 * Preserve the AAPCS64 d8-d15 lanes once at each public KEM boundary.
 */
.macro DEFINE_KEM_API_WRAPPER public_name, internal_name
.global C_SYM(\public_name)
#ifndef __APPLE__
.type C_SYM(\public_name), %function
#endif
C_SYM(\public_name):
    sub sp, sp, #80
    stp x29, x30, [sp, #0]
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    mov x29, sp
    bl C_SYM(\internal_name)
    ldp d14, d15, [sp, #64]
    ldp d12, d13, [sp, #48]
    ldp d10, d11, [sp, #32]
    ldp d8, d9, [sp, #16]
    ldp x29, x30, [sp, #0]
    add sp, sp, #80
    ret
#ifndef __APPLE__
.size C_SYM(\public_name), .-C_SYM(\public_name)
#endif
.endm

DEFINE_KEM_API_WRAPPER crypto_kem_keypair, crypto_kem_keypair_internal
DEFINE_KEM_API_WRAPPER crypto_kem_enc, crypto_kem_enc_internal
DEFINE_KEM_API_WRAPPER crypto_kem_dec, crypto_kem_dec_internal

#undef C_SYM
#ifdef __APPLE__
#undef C_SYM_1
#endif
