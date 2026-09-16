.text
.align 2

.macro LOAD_CANARY reg, imm16
    movz \reg, #\imm16
    movk \reg, #\imm16, lsl #16
    movk \reg, #\imm16, lsl #32
    movk \reg, #\imm16, lsl #48
.endm

.macro CHECK_X reg, imm16, bit
    LOAD_CANARY x9, \imm16
    cmp \reg, x9
    mov x10, #(1 << \bit)
    csel x10, x10, xzr, ne
    orr x0, x0, x10
.endm

.macro CHECK_D operand, imm16, bit
    umov x9, \operand
    LOAD_CANARY x10, \imm16
    cmp x9, x10
    mov x11, #(1 << \bit)
    csel x11, x11, xzr, ne
    orr x0, x0, x11
.endm

.macro ABI_SENTINEL name, target
.global \name
.type \name, %function
\name:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #176
    stp x19, x20, [sp, #0]
    stp x21, x22, [sp, #16]
    stp x23, x24, [sp, #32]
    stp x25, x26, [sp, #48]
    stp x27, x28, [sp, #64]
    stp d8, d9, [sp, #80]
    stp d10, d11, [sp, #96]
    stp d12, d13, [sp, #112]
    stp d14, d15, [sp, #128]
    stp x0, x1, [sp, #144]
    stp x2, x3, [sp, #160]
    LOAD_CANARY x19, 0x1919
    LOAD_CANARY x20, 0x2020
    LOAD_CANARY x21, 0x2121
    LOAD_CANARY x22, 0x2222
    LOAD_CANARY x23, 0x2323
    LOAD_CANARY x24, 0x2424
    LOAD_CANARY x25, 0x2525
    LOAD_CANARY x26, 0x2626
    LOAD_CANARY x27, 0x2727
    LOAD_CANARY x28, 0x2828
    LOAD_CANARY x9, 0xd8d8
    fmov d8, x9
    LOAD_CANARY x9, 0xd9d9
    fmov d9, x9
    LOAD_CANARY x9, 0xdada
    fmov d10, x9
    LOAD_CANARY x9, 0xdbdb
    fmov d11, x9
    LOAD_CANARY x9, 0xdcdc
    fmov d12, x9
    LOAD_CANARY x9, 0xdddd
    fmov d13, x9
    LOAD_CANARY x9, 0xdede
    fmov d14, x9
    LOAD_CANARY x9, 0xdfdf
    fmov d15, x9
    ldp x0, x1, [sp, #144]
    ldp x2, x3, [sp, #160]
    bl \target
    mov x0, xzr
    CHECK_X x19, 0x1919, 0
    CHECK_X x20, 0x2020, 1
    CHECK_X x21, 0x2121, 2
    CHECK_X x22, 0x2222, 3
    CHECK_X x23, 0x2323, 4
    CHECK_X x24, 0x2424, 5
    CHECK_X x25, 0x2525, 6
    CHECK_X x26, 0x2626, 7
    CHECK_X x27, 0x2727, 8
    CHECK_X x28, 0x2828, 9
    CHECK_D v8.d[0], 0xd8d8, 10
    CHECK_D v9.d[0], 0xd9d9, 11
    CHECK_D v10.d[0], 0xdada, 12
    CHECK_D v11.d[0], 0xdbdb, 13
    CHECK_D v12.d[0], 0xdcdc, 14
    CHECK_D v13.d[0], 0xdddd, 15
    CHECK_D v14.d[0], 0xdede, 16
    CHECK_D v15.d[0], 0xdfdf, 17
    ldp d14, d15, [sp, #128]
    ldp d12, d13, [sp, #112]
    ldp d10, d11, [sp, #96]
    ldp d8, d9, [sp, #80]
    ldp x27, x28, [sp, #64]
    ldp x25, x26, [sp, #48]
    ldp x23, x24, [sp, #32]
    ldp x21, x22, [sp, #16]
    ldp x19, x20, [sp, #0]
    add sp, sp, #176
    ldp x29, x30, [sp], #16
    ret
.size \name, .-\name
.endm

ABI_SENTINEL abi_crypto_kem_keypair, crypto_kem_keypair
ABI_SENTINEL abi_crypto_kem_enc, crypto_kem_enc
ABI_SENTINEL abi_crypto_kem_dec, crypto_kem_dec
ABI_SENTINEL abi_gt_forward, gt864_forward_poly_ntt_p41_k1_kem_only
ABI_SENTINEL abi_gt_baseinv, gt864_native_poly_baseinv
ABI_SENTINEL abi_gt_basemul_inverse, gt864_native_basemul_for_inverse
ABI_SENTINEL abi_gt_inverse_ternary, gt864_native_inverse_ternary
ABI_SENTINEL abi_gt_frombytes_checked, gt864_fr0_frombytes_checked
ABI_SENTINEL abi_gt_tobytes_full, gt864_fr0_tobytes_full
ABI_SENTINEL abi_gt_tobytes_small, gt864_fr0_tobytes_small
ABI_SENTINEL abi_gt_tobytes_compare, gt864_fr0_tobytes_full_compare
