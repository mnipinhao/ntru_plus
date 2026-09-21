#ifdef __APPLE__
.section __TEXT,__text,regular,pure_instructions
#else
.section .text.poly_sub,"ax",%progbits
#endif

.global poly_sub
.global _poly_sub
poly_sub:
_poly_sub:
    dst       .req x0
    src1      .req x1
    src2      .req x2
    counter   .req x8

    mov counter, #1536

    # v8-v15 are callee-saved; use v0-v7 and v16-v31 only.
.align 2
_loop_sub:
    ld1 {v0.8h - v3.8h},  [src1], #64
    ld1 {v4.8h - v7.8h},  [src1], #64
    ld1 {v16.8h - v19.8h}, [src1], #64

    ld1 {v20.8h - v23.8h}, [src2], #64
    ld1 {v24.8h - v27.8h}, [src2], #64
    ld1 {v28.8h - v31.8h}, [src2], #64

    sub v0.8h,  v0.8h,  v20.8h
    sub v1.8h,  v1.8h,  v21.8h
    sub v2.8h,  v2.8h,  v22.8h
    sub v3.8h,  v3.8h,  v23.8h
    st1 {v0.8h, v1.8h}, [dst], #32
    sub v4.8h,  v4.8h,  v24.8h
    sub v5.8h,  v5.8h,  v25.8h
    st1 {v2.8h, v3.8h}, [dst], #32
    sub v6.8h,  v6.8h,  v26.8h
    sub v7.8h,  v7.8h,  v27.8h
    st1 {v4.8h, v5.8h}, [dst], #32
    sub v16.8h, v16.8h, v28.8h
    sub v17.8h, v17.8h, v29.8h
    st1 {v6.8h, v7.8h}, [dst], #32
    sub v18.8h, v18.8h, v30.8h
    sub v19.8h, v19.8h, v31.8h
    st1 {v16.8h, v17.8h}, [dst], #32
    st1 {v18.8h, v19.8h}, [dst], #32

    subs counter, counter, #192
    b.ne _loop_sub

    .unreq dst
    .unreq src1
    .unreq src2
    .unreq counter

    ret


.text
.align 2
.global poly_triple
.global _poly_triple
poly_triple:
_poly_triple:
 movi v0.8h, #3
 mov x8, #1536

.align 2
_support_loop_triple:
 /*
	 * Live-in: x0=dst, x1=src, x8=public byte counter, v0=3.
	 * Live-out: dst/src pointers advance by one 192-byte stripe.
	 * Range: int16 coefficient lanes; output is 3 * src.
	 * Reserved physical registers: x9-x30 and sp.
	 */
        ld1 {v19.8H, v20.8H, v21.8H, v22.8H}, [x1], #64
        ld1 {v25.8H, v26.8H, v27.8H, v28.8H}, [x1], #64
        ld1 {v6.8H, v7.8H, v8.8H, v9.8H}, [x1], #64
        mul v3.8H, v20.8H, v0.8H
        mul v2.8H, v19.8H, v0.8H
        mul v14.8H, v22.8H, v0.8H
        mul v13.8H, v21.8H, v0.8H
        st1 {v2.8H, v3.8H}, [x0], #32
        mul v30.8H, v27.8H, v0.8H
        mul v23.8H, v25.8H, v0.8H
        st1 {v13.8H, v14.8H}, [x0], #32
        mul v24.8H, v26.8H, v0.8H
        mul v31.8H, v28.8H, v0.8H
        mul v20.8H, v6.8H, v0.8H
        st1 {v23.8H, v24.8H}, [x0], #32
        mul v22.8H, v8.8H, v0.8H
        st1 {v30.8H, v31.8H}, [x0], #32
        mul v23.8H, v9.8H, v0.8H
        mul v21.8H, v7.8H, v0.8H
        st1 {v20.8H, v21.8H}, [x0], #32
        st1 {v22.8H, v23.8H}, [x0], #32

 subs x8, x8, #192
 b.ne _support_loop_triple
 ret
