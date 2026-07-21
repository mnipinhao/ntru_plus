.text
.p2align 2

/* Returns bit 0 for x19-x28 damage and bit 1 for d8-d15 damage. */
.global gt_decap_verify_pointwise_abi_sentinel
.global _gt_decap_verify_pointwise_abi_sentinel
gt_decap_verify_pointwise_abi_sentinel:
_gt_decap_verify_pointwise_abi_sentinel:
    adrp x3, gt_decap_verify_pointwise
    add x3, x3, :lo12:gt_decap_verify_pointwise

.Ldecap_verify_canonical_abi_sentinel_common:
    sub sp, sp, #160
    stp x29, x30, [sp, #0]
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    stp x25, x26, [sp, #64]
    stp x27, x28, [sp, #80]
    stp d8, d9, [sp, #96]
    stp d10, d11, [sp, #112]
    stp d12, d13, [sp, #128]
    stp d14, d15, [sp, #144]

    mov x19, #0x119
    mov x20, #0x120
    mov x21, #0x121
    mov x22, #0x122
    mov x23, #0x123
    mov x24, #0x124
    mov x25, #0x125
    mov x26, #0x126
    mov x27, #0x127
    mov x28, #0x128
    mov x9, #0x208
    dup v8.2d, x9
    mov x9, #0x209
    dup v9.2d, x9
    mov x9, #0x210
    dup v10.2d, x9
    mov x9, #0x211
    dup v11.2d, x9
    mov x9, #0x212
    dup v12.2d, x9
    mov x9, #0x213
    dup v13.2d, x9
    mov x9, #0x214
    dup v14.2d, x9
    mov x9, #0x215
    dup v15.2d, x9

    blr x3

    mov x0, #0
    cmp x19, #0x119
    cset w9, ne
    orr x0, x0, x9
    cmp x20, #0x120
    cset w9, ne
    orr x0, x0, x9
    cmp x21, #0x121
    cset w9, ne
    orr x0, x0, x9
    cmp x22, #0x122
    cset w9, ne
    orr x0, x0, x9
    cmp x23, #0x123
    cset w9, ne
    orr x0, x0, x9
    cmp x24, #0x124
    cset w9, ne
    orr x0, x0, x9
    cmp x25, #0x125
    cset w9, ne
    orr x0, x0, x9
    cmp x26, #0x126
    cset w9, ne
    orr x0, x0, x9
    cmp x27, #0x127
    cset w9, ne
    orr x0, x0, x9
    cmp x28, #0x128
    cset w9, ne
    orr x0, x0, x9

    mov x9, #0x208
    fmov x10, d8
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x209
    fmov x10, d9
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x210
    fmov x10, d10
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x211
    fmov x10, d11
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x212
    fmov x10, d12
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x213
    fmov x10, d13
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x214
    fmov x10, d14
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1
    mov x9, #0x215
    fmov x10, d15
    cmp x10, x9
    cset w10, ne
    orr x0, x0, x10, lsl #1

    ldp x19, x20, [sp, #16]
    ldp x21, x22, [sp, #32]
    ldp x23, x24, [sp, #48]
    ldp x25, x26, [sp, #64]
    ldp x27, x28, [sp, #80]
    ldp d8, d9, [sp, #96]
    ldp d10, d11, [sp, #112]
    ldp d12, d13, [sp, #128]
    ldp d14, d15, [sp, #144]
    ldp x29, x30, [sp, #0]
    add sp, sp, #160
    ret
