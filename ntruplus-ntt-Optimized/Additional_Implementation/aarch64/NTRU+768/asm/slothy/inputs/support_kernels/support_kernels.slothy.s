.text
.align 2

.global poly_sub
.global _poly_sub
poly_sub:
_poly_sub:
	mov x8, #1536

.align 2
_support_loop_sub:
	/*
	 * Live-in: x0=dst, x1=src1, x2=src2, x8=public byte counter.
	 * Live-out: dst/src pointers advance by one 192-byte stripe.
	 * Range: int16 coefficient lanes; output is src1 - src2.
	 * Reserved physical registers: x9-x30 and sp.
	 */
slothy_start_support_poly_sub_loop:
	ld1 {v0.8h, v1.8h, v2.8h, v3.8h}, [x1], #64
	ld1 {v4.8h, v5.8h, v6.8h, v7.8h}, [x1], #64
	ld1 {v8.8h, v9.8h, v10.8h, v11.8h}, [x1], #64

	ld1 {v12.8h, v13.8h, v14.8h, v15.8h}, [x2], #64
	ld1 {v16.8h, v17.8h, v18.8h, v19.8h}, [x2], #64
	ld1 {v20.8h, v21.8h, v22.8h, v23.8h}, [x2], #64

	sub v0.8h,  v0.8h,  v12.8h
	sub v1.8h,  v1.8h,  v13.8h
	sub v2.8h,  v2.8h,  v14.8h
	sub v3.8h,  v3.8h,  v15.8h
	st1 {v0.8h, v1.8h}, [x0], #32
	sub v4.8h,  v4.8h,  v16.8h
	sub v5.8h,  v5.8h,  v17.8h
	st1 {v2.8h, v3.8h}, [x0], #32
	sub v6.8h,  v6.8h,  v18.8h
	sub v7.8h,  v7.8h,  v19.8h
	st1 {v4.8h, v5.8h}, [x0], #32
	sub v8.8h,  v8.8h,  v20.8h
	sub v9.8h,  v9.8h,  v21.8h
	st1 {v6.8h, v7.8h}, [x0], #32
	sub v10.8h, v10.8h, v22.8h
	sub v11.8h, v11.8h, v23.8h
	st1 {v8.8h,  v9.8h},  [x0], #32
	st1 {v10.8h, v11.8h}, [x0], #32
slothy_end_support_poly_sub_loop:
	subs x8, x8, #192
	b.ne _support_loop_sub
	ret

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
slothy_start_support_poly_triple_loop:
	ld1 {v1.8h, v2.8h, v3.8h, v4.8h}, [x1], #64
	ld1 {v5.8h, v6.8h, v7.8h, v8.8h}, [x1], #64
	ld1 {v9.8h, v10.8h, v11.8h, v12.8h}, [x1], #64

	mul v1.8h,  v1.8h,  v0.8h
	mul v2.8h,  v2.8h,  v0.8h
	st1 {v1.8h, v2.8h}, [x0], #32
	mul v3.8h,  v3.8h,  v0.8h
	mul v4.8h,  v4.8h,  v0.8h
	st1 {v3.8h, v4.8h}, [x0], #32

	mul v5.8h,  v5.8h,  v0.8h
	mul v6.8h,  v6.8h,  v0.8h
	st1 {v5.8h, v6.8h}, [x0], #32
	mul v7.8h,  v7.8h,  v0.8h
	mul v8.8h,  v8.8h,  v0.8h
	st1 {v7.8h, v8.8h}, [x0], #32

	mul v9.8h,  v9.8h,  v0.8h
	mul v10.8h, v10.8h, v0.8h
	st1 {v9.8h, v10.8h}, [x0], #32
	mul v11.8h, v11.8h, v0.8h
	mul v12.8h, v12.8h, v0.8h
	st1 {v11.8h, v12.8h}, [x0], #32
slothy_end_support_poly_triple_loop:
	subs x8, x8, #192
	b.ne _support_loop_triple
	ret

.global poly_crepmod3
.global _poly_crepmod3
poly_crepmod3:
_poly_crepmod3:
	movi v0.8h, #3
	movi v1.16b, #0x55
	mov x8, #1536

.align 2
_support_loop_crepmod3:
	/*
	 * Live-in: x0=dst, x1=src, x8=public byte counter, v0=3, v1=0x5555.
	 * Live-out: dst/src pointers advance by one 64-byte stripe.
	 * Range: int16 coefficient lanes; output is centered representative mod 3.
	 * Reserved physical registers: x9-x30 and sp.
	 */
slothy_start_support_poly_crepmod3_loop:
	ld1 {v2.8h, v3.8h, v4.8h, v5.8h}, [x1], #64

	sqdmulh v6.8h, v2.8h, v1.8h
	sqdmulh v7.8h, v3.8h, v1.8h
	sqdmulh v8.8h, v4.8h, v1.8h
	sqdmulh v9.8h, v5.8h, v1.8h

	srshr v6.8h, v6.8h, #1
	srshr v7.8h, v7.8h, #1
	srshr v8.8h, v8.8h, #1
	srshr v9.8h, v9.8h, #1

	mls v2.8h, v6.8h, v0.8h
	mls v3.8h, v7.8h, v0.8h
	mls v4.8h, v8.8h, v0.8h
	mls v5.8h, v9.8h, v0.8h

	st1 {v2.8h, v3.8h, v4.8h, v5.8h}, [x0], #64
slothy_end_support_poly_crepmod3_loop:
	subs x8, x8, #64
	b.ne _support_loop_crepmod3
	ret

.global poly_frombytes
.global _poly_frombytes
poly_frombytes:
_poly_frombytes:
	adr x2, support_const_mask_0fff
	ldr q0, [x2]
	mov x8, #1536

.align 2
_support_loop_frombytes:
	/*
	 * Live-in: x0=dst, x1=src bytes, x8=public byte counter, v0=0x0fff mask.
	 * Live-out: dst advances by 128 bytes, src advances by 96 bytes.
	 * Range: packed 12-bit coefficients unpack to masked int16 lanes.
	 * Reserved physical registers: x9-x30 and sp.
	 */
slothy_start_support_poly_frombytes_loop:
	ld1 {v1.8h, v2.8h, v3.8h}, [x1], #48
	ld1 {v4.8h, v5.8h, v6.8h}, [x1], #48

	trn1 v7.2d,  v1.2d, v4.2d
	trn2 v8.2d,  v1.2d, v4.2d
	trn1 v9.2d,  v2.2d, v5.2d
	trn2 v10.2d, v2.2d, v5.2d
	trn1 v11.2d, v3.2d, v6.2d
	trn2 v12.2d, v3.2d, v6.2d

	trn1 v13.4s, v7.4s, v10.4s
	trn2 v14.4s, v7.4s, v10.4s
	trn1 v15.4s, v8.4s, v11.4s
	trn2 v16.4s, v8.4s, v11.4s
	trn1 v17.4s, v9.4s, v12.4s
	trn2 v18.4s, v9.4s, v12.4s

	trn1 v19.8h, v13.8h, v16.8h
	trn2 v20.8h, v13.8h, v16.8h
	trn1 v21.8h, v14.8h, v17.8h
	trn2 v22.8h, v14.8h, v17.8h
	trn1 v23.8h, v15.8h, v18.8h
	trn2 v24.8h, v15.8h, v18.8h

	ushr v25.8h, v19.8h, #12
	shl  v26.8h, v20.8h, #4
	ushr v27.8h, v20.8h, #8
	shl  v28.8h, v21.8h, #8
	ushr v29.8h, v21.8h, #4

	ushr v30.8h, v22.8h, #12
	shl  v31.8h, v23.8h, #4
	ushr v1.8h,  v23.8h, #8
	shl  v2.8h,  v24.8h, #8
	ushr v3.8h,  v24.8h, #4

	eor v4.16b, v25.16b, v26.16b
	eor v5.16b, v27.16b, v28.16b
	eor v6.16b, v30.16b, v31.16b
	eor v7.16b, v1.16b,  v2.16b

	and v8.16b,  v19.16b, v0.16b
	and v9.16b,  v4.16b,  v0.16b
	and v10.16b, v5.16b,  v0.16b
	and v11.16b, v29.16b, v0.16b
	and v12.16b, v22.16b, v0.16b
	and v13.16b, v6.16b,  v0.16b
	and v14.16b, v7.16b,  v0.16b
	and v15.16b, v3.16b,  v0.16b

	st1 {v8.8h, v9.8h, v10.8h, v11.8h}, [x0], #64
	st1 {v12.8h, v13.8h, v14.8h, v15.8h}, [x0], #64
slothy_end_support_poly_frombytes_loop:
	subs x8, x8, #128
	b.ne _support_loop_frombytes
	ret

.global poly_tobytes
.global _poly_tobytes
poly_tobytes:
_poly_tobytes:
	adr x2, support_const_q
	ldr q0, [x2]
	mov x8, #1536

.align 2
_support_loop_tobytes:
	/*
	 * Live-in: x0=dst bytes, x1=src coefficients, x8=public byte counter, v0=q.
	 * Live-out: v1..v6 hold packed byte vectors for the two original stores;
	 * src advances by 128 bytes, and dst advances after the stores below.
	 * Range: int16 coefficients are conditionally lifted by q then packed.
	 * Reserved physical registers: x9-x30 and sp.
	 */
slothy_start_support_poly_tobytes_loop:
	ld1 {v1.8h, v2.8h, v3.8h, v4.8h}, [x1], #64
	ld1 {v5.8h, v6.8h, v7.8h, v8.8h}, [x1], #64

	sshr v9.8h,  v1.8h, #15
	sshr v10.8h, v2.8h, #15
	sshr v11.8h, v3.8h, #15
	sshr v12.8h, v4.8h, #15
	sshr v13.8h, v5.8h, #15
	sshr v14.8h, v6.8h, #15
	sshr v15.8h, v7.8h, #15
	sshr v16.8h, v8.8h, #15

	and v17.16b, v9.16b,  v0.16b
	and v18.16b, v10.16b, v0.16b
	and v19.16b, v11.16b, v0.16b
	and v20.16b, v12.16b, v0.16b
	and v21.16b, v13.16b, v0.16b
	and v22.16b, v14.16b, v0.16b
	and v23.16b, v15.16b, v0.16b
	and v24.16b, v16.16b, v0.16b

	add v25.8h, v1.8h, v17.8h
	add v26.8h, v2.8h, v18.8h
	add v27.8h, v3.8h, v19.8h
	add v28.8h, v4.8h, v20.8h
	add v29.8h, v5.8h, v21.8h
	add v30.8h, v6.8h, v22.8h
	add v31.8h, v7.8h, v23.8h
	add v1.8h,  v8.8h, v24.8h

	ushr v2.8h, v26.8h, #4
	ushr v3.8h, v27.8h, #8
	ushr v4.8h, v30.8h, #4
	ushr v5.8h, v31.8h, #8

	shl v6.8h,  v26.8h, #12
	shl v7.8h,  v27.8h, #8
	shl v8.8h,  v28.8h, #4
	shl v9.8h,  v30.8h, #12
	shl v10.8h, v31.8h, #8
	shl v11.8h, v1.8h,  #4

	eor v12.16b, v25.16b, v6.16b
	eor v13.16b, v2.16b,  v7.16b
	eor v14.16b, v3.16b,  v8.16b
	eor v15.16b, v29.16b, v9.16b
	eor v16.16b, v4.16b,  v10.16b
	eor v17.16b, v5.16b,  v11.16b

	trn1 v18.8h, v12.8h, v13.8h
	trn1 v19.8h, v14.8h, v15.8h
	trn1 v20.8h, v16.8h, v17.8h
	trn2 v21.8h, v12.8h, v13.8h
	trn2 v22.8h, v14.8h, v15.8h
	trn2 v23.8h, v16.8h, v17.8h

	trn1 v24.4s, v18.4s, v19.4s
	trn1 v25.4s, v20.4s, v21.4s
	trn1 v26.4s, v22.4s, v23.4s
	trn2 v27.4s, v18.4s, v19.4s
	trn2 v28.4s, v20.4s, v21.4s
	trn2 v29.4s, v22.4s, v23.4s

	trn1 v1.2d, v24.2d, v25.2d
	trn1 v2.2d, v26.2d, v27.2d
	trn1 v3.2d, v28.2d, v29.2d
	trn2 v4.2d, v24.2d, v25.2d
	trn2 v5.2d, v26.2d, v27.2d
	trn2 v6.2d, v28.2d, v29.2d

slothy_end_support_poly_tobytes_loop:
	st1 {v1.8h, v2.8h, v3.8h}, [x0], #48
	st1 {v4.8h, v5.8h, v6.8h}, [x0], #48
	subs x8, x8, #128
	b.ne _support_loop_tobytes
	ret

.align 4
support_const_mask_0fff:
	.hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
	.hword 0x0fff, 0x0fff, 0x0fff, 0x0fff

.align 4
support_const_q:
	.hword 3457, 3457, 3457, 3457
	.hword 3457, 3457, 3457, 3457
