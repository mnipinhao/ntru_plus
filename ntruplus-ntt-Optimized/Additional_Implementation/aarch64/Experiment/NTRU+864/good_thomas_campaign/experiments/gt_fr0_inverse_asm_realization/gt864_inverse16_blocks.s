/*
 * Stackless packed-top inverse NTT16 blocks.
 *
 * State indices 0..15 use v0-v7,v16-v23.  v8-v15 are untouched.
 * v24-v27 are widening Montgomery scratch, v28 is butterfly/recombine
 * scratch, v29 is the current public constant, and v30/v31 are q/-qinv.
 */

.text
.p2align 2

.macro FQMUL dst, src
    smull   v24.4s, \src\().4h, v29.4h
    smull2  v25.4s, \src\().8h, v29.8h
    uzp1    v26.8h, v24.8h, v25.8h
    mul     v26.8h, v26.8h, v31.8h
    smlal   v24.4s, v26.4h, v30.4h
    smlal2  v25.4s, v26.8h, v30.8h
    uzp2    \dst\().8h, v24.8h, v25.8h
.endm

.macro LOAD_CONST offset
    ldr     h29, [x3, #\offset]
    dup     v29.8h, v29.h[0]
.endm

.macro B2 left, right, offset
    mov     v28.16b, \left\().16b
    LOAD_CONST \offset
    FQMUL   \right, \right
    add     \left\().8h, v28.8h, \right\().8h
    sub     \right\().8h, v28.8h, \right\().8h
.endm

.macro INTT16
    B2 v0,  v1,  0
    B2 v2,  v3,  0
    B2 v4,  v5,  0
    B2 v6,  v7,  0
    B2 v16, v17, 0
    B2 v18, v19, 0
    B2 v20, v21, 0
    B2 v22, v23, 0

    B2 v0,  v2,  16
    B2 v1,  v3,  18
    B2 v4,  v6,  16
    B2 v5,  v7,  18
    B2 v16, v18, 16
    B2 v17, v19, 18
    B2 v20, v22, 16
    B2 v21, v23, 18

    B2 v0,  v4,  32
    B2 v1,  v5,  34
    B2 v2,  v6,  36
    B2 v3,  v7,  38
    B2 v16, v20, 32
    B2 v17, v21, 34
    B2 v18, v22, 36
    B2 v19, v23, 38

    B2 v0,  v16, 48
    B2 v1,  v17, 50
    B2 v2,  v18, 52
    B2 v3,  v19, 54
    B2 v4,  v20, 56
    B2 v5,  v21, 58
    B2 v6,  v22, 60
    B2 v7,  v23, 62
.endm

.macro LOAD_MAIN reg, offset
    ldr     d\reg, [x1, #\offset]
    ldr     d24, [x2, #\offset]
    ins     v\reg\().d[1], v24.d[0]
.endm

/* lowoff and scaleoff are byte offsets. */
.macro FINISH_MAIN reg, lowoff, scaleoff
    ldr     q29, [x4, #\scaleoff]
    FQMUL   v\reg, v\reg
    mov     v28.16b, v\reg\().16b
    ext     v\reg\().16b, v\reg\().16b, v\reg\().16b, #8
    sub     v\reg\().8h, v\reg\().8h, v28.8h
    mov     w8, #1665
    dup     v29.8h, w8
    FQMUL   v\reg, v\reg
    umov    w9, v\reg\().h[0]
    strh    w9, [x0, #(\lowoff + 864)]
    umov    w9, v\reg\().h[1]
    strh    w9, [x0, #(\lowoff + 870)]
    umov    w9, v\reg\().h[2]
    strh    w9, [x0, #(\lowoff + 876)]
    umov    w9, v\reg\().h[3]
    strh    w9, [x0, #(\lowoff + 882)]
    mov     w8, #64503              /* alpha*R = -1033 */
    dup     v29.8h, w8
    FQMUL   v\reg, v\reg
    sub     v\reg\().8h, v28.8h, v\reg\().8h
    umov    w9, v\reg\().h[0]
    strh    w9, [x0, #\lowoff]
    umov    w9, v\reg\().h[1]
    strh    w9, [x0, #(\lowoff + 6)]
    umov    w9, v\reg\().h[2]
    strh    w9, [x0, #(\lowoff + 12)]
    umov    w9, v\reg\().h[3]
    strh    w9, [x0, #(\lowoff + 18)]
.endm

.global gt864_inverse16_main_block_asm
.global _gt864_inverse16_main_block_asm
gt864_inverse16_main_block_asm:
_gt864_inverse16_main_block_asm:
    mov     w8, #3457
    dup     v30.8h, w8
    mov     w8, #52607
    dup     v31.8h, w8

    /* Natural columns are loaded into public bit-reversed state positions. */
    LOAD_MAIN 0,   0
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

    FINISH_MAIN 0,   0,   0
    FINISH_MAIN 1,   54,  16
    FINISH_MAIN 2,   108, 32
    FINISH_MAIN 3,   162, 48
    FINISH_MAIN 4,   216, 64
    FINISH_MAIN 5,   270, 80
    FINISH_MAIN 6,   324, 96
    FINISH_MAIN 7,   378, 112
    FINISH_MAIN 16,  432, 128
    FINISH_MAIN 17,  486, 144
    FINISH_MAIN 18,  540, 160
    FINISH_MAIN 19,  594, 176
    FINISH_MAIN 20,  648, 192
    FINISH_MAIN 21,  702, 208
    FINISH_MAIN 22,  756, 224
    FINISH_MAIN 23,  810, 240
    ret

.macro LOAD_TAIL reg, offset
    ldr     q\reg, [x1, #\offset]
.endm

.macro FINISH_TAIL reg, lowoff, scaleoff
    ldr     q29, [x4, #\scaleoff]
    FQMUL   v\reg, v\reg
    mov     v28.16b, v\reg\().16b
    ext     v\reg\().16b, v\reg\().16b, v\reg\().16b, #6
    sub     v\reg\().8h, v\reg\().8h, v28.8h
    mov     w8, #1665
    dup     v29.8h, w8
    FQMUL   v\reg, v\reg
    umov    w9, v\reg\().h[0]
    strh    w9, [x0, #(\lowoff + 864)]
    umov    w9, v\reg\().h[1]
    strh    w9, [x0, #(\lowoff + 866)]
    umov    w9, v\reg\().h[2]
    strh    w9, [x0, #(\lowoff + 868)]
    mov     w8, #64503
    dup     v29.8h, w8
    FQMUL   v\reg, v\reg
    sub     v\reg\().8h, v28.8h, v\reg\().8h
    umov    w9, v\reg\().h[0]
    strh    w9, [x0, #\lowoff]
    umov    w9, v\reg\().h[1]
    strh    w9, [x0, #(\lowoff + 2)]
    umov    w9, v\reg\().h[2]
    strh    w9, [x0, #(\lowoff + 4)]
.endm

.global gt864_inverse16_tail_block_asm
.global _gt864_inverse16_tail_block_asm
gt864_inverse16_tail_block_asm:
_gt864_inverse16_tail_block_asm:
    mov     w8, #3457
    dup     v30.8h, w8
    mov     w8, #52607
    dup     v31.8h, w8

    LOAD_TAIL 0,   0
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

    FINISH_TAIL 0,   0,   0
    FINISH_TAIL 1,   54,  16
    FINISH_TAIL 2,   108, 32
    FINISH_TAIL 3,   162, 48
    FINISH_TAIL 4,   216, 64
    FINISH_TAIL 5,   270, 80
    FINISH_TAIL 6,   324, 96
    FINISH_TAIL 7,   378, 112
    FINISH_TAIL 16,  432, 128
    FINISH_TAIL 17,  486, 144
    FINISH_TAIL 18,  540, 160
    FINISH_TAIL 19,  594, 176
    FINISH_TAIL 20,  648, 192
    FINISH_TAIL 21,  702, 208
    FINISH_TAIL 22,  756, 224
    FINISH_TAIL 23,  810, 240
    ret
