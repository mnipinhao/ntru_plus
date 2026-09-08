/*
 * Stackless packed-top inverse NTT16 blocks.
 *
 * State indices 0..15 use v24,v1-v7,v16-v23.  v8-v15 are untouched.
 * v25-v28 are grouped Barrett quotients/saved values, v29 is destructive
 * scratch, v0 is a four-pair or vector public constant, and v31 is q.
 * v0 is required because halfword vector-by-element encodings use v0-v15.
 */

.text
.p2align 2

.macro B2X4 l0, r0, l1, r1, l2, r2, l3, r3, offset
    ldr     q0, [x3, #\offset]
    sqrdmulh v25.8h, \r0\().8h, v0.h[1]
    sqrdmulh v26.8h, \r1\().8h, v0.h[3]
    sqrdmulh v27.8h, \r2\().8h, v0.h[5]
    sqrdmulh v28.8h, \r3\().8h, v0.h[7]
    mul     \r0\().8h, \r0\().8h, v0.h[0]
    mul     \r1\().8h, \r1\().8h, v0.h[2]
    mul     \r2\().8h, \r2\().8h, v0.h[4]
    mul     \r3\().8h, \r3\().8h, v0.h[6]
    mls     \r0\().8h, v25.8h, v31.8h
    mls     \r1\().8h, v26.8h, v31.8h
    mls     \r2\().8h, v27.8h, v31.8h
    mls     \r3\().8h, v28.8h, v31.8h
    mov     v29.16b, \l0\().16b
    add     \l0\().8h, \l0\().8h, \r0\().8h
    sub     \r0\().8h, v29.8h, \r0\().8h
    mov     v29.16b, \l1\().16b
    add     \l1\().8h, \l1\().8h, \r1\().8h
    sub     \r1\().8h, v29.8h, \r1\().8h
    mov     v29.16b, \l2\().16b
    add     \l2\().8h, \l2\().8h, \r2\().8h
    sub     \r2\().8h, v29.8h, \r2\().8h
    mov     v29.16b, \l3\().16b
    add     \l3\().8h, \l3\().8h, \r3\().8h
    sub     \r3\().8h, v29.8h, \r3\().8h
.endm

.macro INTT16
    B2X4 v24, v1, v2, v3, v4, v5, v6, v7, 0
    B2X4 v16, v17, v18, v19, v20, v21, v22, v23, 16

    B2X4 v24, v2, v1, v3, v4, v6, v5, v7, 32
    B2X4 v16, v18, v17, v19, v20, v22, v21, v23, 48

    B2X4 v24, v4, v1, v5, v2, v6, v3, v7, 64
    B2X4 v16, v20, v17, v21, v18, v22, v19, v23, 80

    B2X4 v24, v16, v1, v17, v2, v18, v3, v19, 96
    B2X4 v4, v20, v5, v21, v6, v22, v7, v23, 112
.endm

.macro LOAD_MAIN reg, offset
    ldr     d\reg, [x1, #\offset]
    ldr     d30, [x2, #\offset]
    ins     v\reg\().d[1], v30.d[0]
.endm

.macro SCALE4 r0, r1, r2, r3, o0, o1, o2, o3
    ldr     q0, [x4, #(\o0 + 16)]
    sqrdmulh v25.8h, \r0\().8h, v0.8h
    ldr     q0, [x4, #(\o1 + 16)]
    sqrdmulh v26.8h, \r1\().8h, v0.8h
    ldr     q0, [x4, #(\o2 + 16)]
    sqrdmulh v27.8h, \r2\().8h, v0.8h
    ldr     q0, [x4, #(\o3 + 16)]
    sqrdmulh v28.8h, \r3\().8h, v0.8h
    ldr     q0, [x4, #\o0]
    mul     \r0\().8h, \r0\().8h, v0.8h
    ldr     q0, [x4, #\o1]
    mul     \r1\().8h, \r1\().8h, v0.8h
    ldr     q0, [x4, #\o2]
    mul     \r2\().8h, \r2\().8h, v0.8h
    ldr     q0, [x4, #\o3]
    mul     \r3\().8h, \r3\().8h, v0.8h
    mls     \r0\().8h, v25.8h, v31.8h
    mls     \r1\().8h, v26.8h, v31.8h
    mls     \r2\().8h, v27.8h, v31.8h
    mls     \r3\().8h, v28.8h, v31.8h
.endm

.macro LOAD_FIXED_PAIR low, high
    mov     w8, #((\low) & 0xffff)
    dup     v0.8h, w8
    mov     w8, #((\high) & 0xffff)
    dup     v30.8h, w8
.endm

/* Finish two states together; low offsets are bytes in natural output. */
.macro FINISH_MAIN2 r0, low0, r1, low1
    mov     v25.16b, \r0\().16b
    mov     v26.16b, \r1\().16b
    ext     \r0\().16b, \r0\().16b, \r0\().16b, #8
    ext     \r1\().16b, \r1\().16b, \r1\().16b, #8
    sub     \r0\().8h, \r0\().8h, v25.8h
    sub     \r1\().8h, \r1\().8h, v26.8h
    LOAD_FIXED_PAIR -1634, -15488 /* (beta-alpha)^-1 */
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    umov    w9, \r0\().h[0]
    strh    w9, [x0, #(\low0 + 864)]
    umov    w9, \r0\().h[1]
    strh    w9, [x0, #(\low0 + 870)]
    umov    w9, \r0\().h[2]
    strh    w9, [x0, #(\low0 + 876)]
    umov    w9, \r0\().h[3]
    strh    w9, [x0, #(\low0 + 882)]
    umov    w9, \r1\().h[0]
    strh    w9, [x0, #(\low1 + 864)]
    umov    w9, \r1\().h[1]
    strh    w9, [x0, #(\low1 + 870)]
    umov    w9, \r1\().h[2]
    strh    w9, [x0, #(\low1 + 876)]
    umov    w9, \r1\().h[3]
    strh    w9, [x0, #(\low1 + 882)]
    LOAD_FIXED_PAIR -722, -6844 /* alpha */
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    sub     \r0\().8h, v25.8h, \r0\().8h
    sub     \r1\().8h, v26.8h, \r1\().8h
    umov    w9, \r0\().h[0]
    strh    w9, [x0, #\low0]
    umov    w9, \r0\().h[1]
    strh    w9, [x0, #(\low0 + 6)]
    umov    w9, \r0\().h[2]
    strh    w9, [x0, #(\low0 + 12)]
    umov    w9, \r0\().h[3]
    strh    w9, [x0, #(\low0 + 18)]
    umov    w9, \r1\().h[0]
    strh    w9, [x0, #\low1]
    umov    w9, \r1\().h[1]
    strh    w9, [x0, #(\low1 + 6)]
    umov    w9, \r1\().h[2]
    strh    w9, [x0, #(\low1 + 12)]
    umov    w9, \r1\().h[3]
    strh    w9, [x0, #(\low1 + 18)]
.endm

.global gt864_inverse16_main_block_asm
.global _gt864_inverse16_main_block_asm
gt864_inverse16_main_block_asm:
_gt864_inverse16_main_block_asm:
    mov     w8, #3457
    dup     v31.8h, w8

    /* Natural columns are loaded into public bit-reversed state positions. */
    LOAD_MAIN 24,  0
    LOAD_MAIN 16, 16
    LOAD_MAIN 4,  32
    LOAD_MAIN 20, 48
    LOAD_MAIN 2,  64
    LOAD_MAIN 18, 80
    LOAD_MAIN 6,  96
    LOAD_MAIN 22, 112
    LOAD_MAIN 1,  128
    LOAD_MAIN 17, 144
    LOAD_MAIN 5,  160
    LOAD_MAIN 21, 176
    LOAD_MAIN 3,  192
    LOAD_MAIN 19, 208
    LOAD_MAIN 7,  224
    LOAD_MAIN 23, 240

    INTT16

    SCALE4 v24, v1, v2, v3, 0, 32, 64, 96
    FINISH_MAIN2 v24, 0, v1, 54
    FINISH_MAIN2 v2, 108, v3, 162
    SCALE4 v4, v5, v6, v7, 128, 160, 192, 224
    FINISH_MAIN2 v4, 216, v5, 270
    FINISH_MAIN2 v6, 324, v7, 378
    SCALE4 v16, v17, v18, v19, 256, 288, 320, 352
    FINISH_MAIN2 v16, 432, v17, 486
    FINISH_MAIN2 v18, 540, v19, 594
    SCALE4 v20, v21, v22, v23, 384, 416, 448, 480
    FINISH_MAIN2 v20, 648, v21, 702
    FINISH_MAIN2 v22, 756, v23, 810
    ret

.macro LOAD_TAIL reg, offset
    ldr     q\reg, [x1, #\offset]
.endm

.macro FINISH_TAIL2 r0, low0, r1, low1
    mov     v25.16b, \r0\().16b
    mov     v26.16b, \r1\().16b
    ext     \r0\().16b, \r0\().16b, \r0\().16b, #6
    ext     \r1\().16b, \r1\().16b, \r1\().16b, #6
    sub     \r0\().8h, \r0\().8h, v25.8h
    sub     \r1\().8h, \r1\().8h, v26.8h
    LOAD_FIXED_PAIR -1634, -15488
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    umov    w9, \r0\().h[0]
    strh    w9, [x0, #(\low0 + 864)]
    umov    w9, \r0\().h[1]
    strh    w9, [x0, #(\low0 + 866)]
    umov    w9, \r0\().h[2]
    strh    w9, [x0, #(\low0 + 868)]
    umov    w9, \r1\().h[0]
    strh    w9, [x0, #(\low1 + 864)]
    umov    w9, \r1\().h[1]
    strh    w9, [x0, #(\low1 + 866)]
    umov    w9, \r1\().h[2]
    strh    w9, [x0, #(\low1 + 868)]
    LOAD_FIXED_PAIR -722, -6844
    sqrdmulh v27.8h, \r0\().8h, v30.8h
    sqrdmulh v28.8h, \r1\().8h, v30.8h
    mul     \r0\().8h, \r0\().8h, v0.8h
    mul     \r1\().8h, \r1\().8h, v0.8h
    mls     \r0\().8h, v27.8h, v31.8h
    mls     \r1\().8h, v28.8h, v31.8h
    sub     \r0\().8h, v25.8h, \r0\().8h
    sub     \r1\().8h, v26.8h, \r1\().8h
    umov    w9, \r0\().h[0]
    strh    w9, [x0, #\low0]
    umov    w9, \r0\().h[1]
    strh    w9, [x0, #(\low0 + 2)]
    umov    w9, \r0\().h[2]
    strh    w9, [x0, #(\low0 + 4)]
    umov    w9, \r1\().h[0]
    strh    w9, [x0, #\low1]
    umov    w9, \r1\().h[1]
    strh    w9, [x0, #(\low1 + 2)]
    umov    w9, \r1\().h[2]
    strh    w9, [x0, #(\low1 + 4)]
.endm

.global gt864_inverse16_tail_block_asm
.global _gt864_inverse16_tail_block_asm
gt864_inverse16_tail_block_asm:
_gt864_inverse16_tail_block_asm:
    mov     w8, #3457
    dup     v31.8h, w8

    LOAD_TAIL 24,  0
    LOAD_TAIL 16, 16
    LOAD_TAIL 4,  32
    LOAD_TAIL 20, 48
    LOAD_TAIL 2,  64
    LOAD_TAIL 18, 80
    LOAD_TAIL 6,  96
    LOAD_TAIL 22, 112
    LOAD_TAIL 1,  128
    LOAD_TAIL 17, 144
    LOAD_TAIL 5,  160
    LOAD_TAIL 21, 176
    LOAD_TAIL 3,  192
    LOAD_TAIL 19, 208
    LOAD_TAIL 7,  224
    LOAD_TAIL 23, 240

    INTT16

    SCALE4 v24, v1, v2, v3, 0, 32, 64, 96
    FINISH_TAIL2 v24, 0, v1, 54
    FINISH_TAIL2 v2, 108, v3, 162
    SCALE4 v4, v5, v6, v7, 128, 160, 192, 224
    FINISH_TAIL2 v4, 216, v5, 270
    FINISH_TAIL2 v6, 324, v7, 378
    SCALE4 v16, v17, v18, v19, 256, 288, 320, 352
    FINISH_TAIL2 v16, 432, v17, 486
    FINISH_TAIL2 v18, 540, v19, 594
    SCALE4 v20, v21, v22, v23, 384, 416, 448, 480
    FINISH_TAIL2 v20, 648, v21, 702
    FINISH_TAIL2 v22, 756, v23, 810
    ret
