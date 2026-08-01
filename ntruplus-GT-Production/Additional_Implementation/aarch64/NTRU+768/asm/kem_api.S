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
#ifdef __APPLE__
.section __TEXT,__text,regular,pure_instructions
#else
.section .text.\public_name,"ax",%progbits
#endif
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
    /* P0-B: x0 is the public return value; clear every caller-saved lane. */
    movi v0.16b, #0
    stp q0, q0, [sp, #0]
    stp q0, q0, [sp, #32]
    str q0, [sp, #64]
    add sp, sp, #80
    mov x1, xzr
    mov x2, xzr
    mov x3, xzr
    mov x4, xzr
    mov x5, xzr
    mov x6, xzr
    mov x7, xzr
    mov x8, xzr
    mov x9, xzr
    mov x10, xzr
    mov x11, xzr
    mov x12, xzr
    mov x13, xzr
    mov x14, xzr
    mov x15, xzr
    mov x16, xzr
    mov x17, xzr
    movi v1.16b, #0
    movi v2.16b, #0
    movi v3.16b, #0
    movi v4.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    movi v7.16b, #0
    ins v8.d[1], xzr
    ins v9.d[1], xzr
    ins v10.d[1], xzr
    ins v11.d[1], xzr
    ins v12.d[1], xzr
    ins v13.d[1], xzr
    ins v14.d[1], xzr
    ins v15.d[1], xzr
    movi v16.16b, #0
    movi v17.16b, #0
    movi v18.16b, #0
    movi v19.16b, #0
    movi v20.16b, #0
    movi v21.16b, #0
    movi v22.16b, #0
    movi v23.16b, #0
    movi v24.16b, #0
    movi v25.16b, #0
    movi v26.16b, #0
    movi v27.16b, #0
    movi v28.16b, #0
    movi v29.16b, #0
    movi v30.16b, #0
    movi v31.16b, #0
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
