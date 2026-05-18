.text

.macro BARRETT_REDUCE out, in, tmp1, tmp2
    mov \tmp1, #19412
    mul \tmp1, \in, \tmp1
    mov \tmp2, #1
    lsl \tmp2, \tmp2, #25
    add \tmp1, \tmp1, \tmp2
    asr \tmp1, \tmp1, #26
    mov \tmp2, #3457
    msub \out, \tmp1, \tmp2, \in
.endm

.macro MONTGOMERY_REDUCE_MUL out, a, b, tmp1, tmp2, tmp3
    mul \tmp1, \a, \b
    sxth \tmp2, \tmp1
    mov \tmp3, #12929
    mul \tmp2, \tmp2, \tmp3
    sxth \tmp2, \tmp2
    mov \tmp3, #3457
    msub \tmp1, \tmp2, \tmp3, \tmp1
    asr \out, \tmp1, #16
.endm

.global ntt32_radix2_asm
.global _ntt32_radix2_asm
ntt32_radix2_asm:
_ntt32_radix2_asm:
    out       .req x0
    in        .req x1
    i         .req x2
    table     .req x3

    /*
     * Reference-shape ASM kernel:
     *   1. gather input into bitreversed order
     *   2. run iterative CT butterflies with len = 2,4,8,16,32
     *
     * This first version is intentionally scalar.  It fixes the ABI and
     * arithmetic schedule before the kernel is repacked into NEON vectors.
     */
    adr table, gt32_bitrev
    mov i, #0

Lgt32_bitrev_loop:
    add x17, in, i, lsl #1
    ldrsh w4, [x17]
    BARRETT_REDUCE w4, w4, w13, w14

    ldrb w5, [table, i]
    add x17, out, x5, lsl #1
    strh w4, [x17]

    add i, i, #1
    cmp i, #32
    b.ne Lgt32_bitrev_loop

    adr table, gt32_omega32_powers
    mov w2, #2      // len
    mov w4, #16     // step = 32 / len

Lgt32_len_loop:
    ldrsh w8, [table, w4, uxtw #1] // root = omega32^step
    lsr w5, w2, #1                 // half = len / 2
    mov w6, #0                     // start

Lgt32_start_loop:
    mov w7, #0xff6d
    sxth w7, w7                    // w = NTRUPLUS_R, Montgomery form of 1
    mov w9, #0                     // j

Lgt32_j_loop:
    add w10, w6, w9                // lo = start + j
    add w14, w10, w5               // hi = lo + half

    add x17, out, w10, uxtw #1
    ldrsh w11, [x17]               // u
    add x17, out, w14, uxtw #1
    ldrsh w12, [x17]               // high input

    MONTGOMERY_REDUCE_MUL w12, w12, w7, w13, w15, w16

    add w13, w11, w12
    sub w15, w11, w12
    BARRETT_REDUCE w13, w13, w16, w17
    BARRETT_REDUCE w15, w15, w16, w17

    add x17, out, w10, uxtw #1
    strh w13, [x17]
    add x17, out, w14, uxtw #1
    strh w15, [x17]

    MONTGOMERY_REDUCE_MUL w7, w7, w8, w13, w15, w16

    add w9, w9, #1
    cmp w9, w5
    b.ne Lgt32_j_loop

    add w6, w6, w2
    cmp w6, #32
    b.lt Lgt32_start_loop

    lsl w2, w2, #1
    lsr w4, w4, #1
    cmp w2, #64
    b.ne Lgt32_len_loop

    .unreq out
    .unreq in
    .unreq i
    .unreq table
    ret

.align 4
gt32_bitrev:
    .byte 0, 16, 8, 24, 4, 20, 12, 28
    .byte 2, 18, 10, 26, 6, 22, 14, 30
    .byte 1, 17, 9, 25, 5, 21, 13, 29
    .byte 3, 19, 11, 27, 7, 23, 15, 31

.align 4
gt32_omega32_powers:
    .hword -147, 484, -794, 874, 109, 864, -446, -554
    .hword 366, -429, -1339, 11, -1118, 177, 1181, 1591
    .hword 147, -484, 794, -874, -109, -864, 446, 554
    .hword -366, 429, 1339, -11, 1118, -177, -1181, -1591
