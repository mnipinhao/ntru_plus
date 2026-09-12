	.arch armv8-a
	.file	"gt864_p9_tobytes_full.c"
	.text
	.section	.text.p9_input_once_top_full,"ax",@progbits
	.align	2
	.p2align 5,,15
	.type	p9_input_once_top_full, %function
p9_input_once_top_full:
.LFB3918:
	.cfi_startproc
	stp	d8, d9, [sp, -64]!
	.cfi_def_cfa_offset 64
	.cfi_offset 72, -64
	.cfi_offset 73, -56
	add	x2, x1, 144
	stp	d10, d11, [sp, 16]
	stp	d12, d13, [sp, 32]
	stp	d14, d15, [sp, 48]
	.cfi_offset 74, -48
	.cfi_offset 75, -40
	.cfi_offset 76, -32
	.cfi_offset 77, -24
	.cfi_offset 78, -16
	.cfi_offset 79, -8
#APP
// 24 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	movi	v30.4s, 0
	mov	v29.16b, v30.16b
	mov	v18.16b, v30.16b
	mov	v26.16b, v30.16b
	mov	v27.16b, v30.16b
	mov	v19.16b, v30.16b
	mov	v28.16b, v30.16b
	mov	v24.16b, v30.16b
	mov	v25.16b, v30.16b
	ins	v29.h[4], v31.h[3]
	ins	v18.h[4], v31.h[6]
	ins	v26.h[4], v31.h[0]
	ins	v27.h[4], v31.h[4]
	ins	v19.h[4], v31.h[7]
	ins	v28.h[4], v31.h[1]
	ins	v24.h[4], v31.h[5]
	ins	v25.h[4], v31.h[2]
	add	x2, x1, 160
#APP
// 42 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	ins	v29.h[5], v31.h[3]
	ins	v18.h[5], v31.h[6]
	ins	v26.h[5], v31.h[0]
	ins	v27.h[5], v31.h[4]
	ins	v19.h[5], v31.h[7]
	ins	v28.h[5], v31.h[1]
	ins	v24.h[5], v31.h[5]
	ins	v25.h[5], v31.h[2]
	add	x2, x1, 176
#APP
// 52 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	ins	v29.h[6], v31.h[3]
	ins	v18.h[6], v31.h[6]
	ins	v26.h[6], v31.h[0]
	ins	v27.h[6], v31.h[4]
	ins	v19.h[6], v31.h[7]
	ins	v28.h[6], v31.h[1]
	ins	v24.h[6], v31.h[5]
	ins	v25.h[6], v31.h[2]
	add	x2, x1, 576
#APP
// 62 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	ins	v29.h[7], v31.h[3]
	ins	v18.h[7], v31.h[6]
	ins	v26.h[7], v31.h[0]
	ins	v27.h[7], v31.h[4]
	ins	v19.h[7], v31.h[7]
	ins	v28.h[7], v31.h[1]
	ins	v24.h[7], v31.h[5]
	ins	v25.h[7], v31.h[2]
	add	x2, x1, 272
#APP
// 72 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	mov	v20.16b, v30.16b
	mov	v21.16b, v30.16b
	ins	v29.h[0], v31.h[5]
	ins	v26.h[0], v31.h[2]
	ins	v27.h[0], v31.h[6]
	ins	v28.h[0], v31.h[3]
	ins	v24.h[0], v31.h[7]
	ins	v25.h[0], v31.h[4]
	ins	v20.h[0], v31.h[0]
	ins	v21.h[0], v31.h[1]
	add	x2, x1, 672
#APP
// 84 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	ins	v29.h[1], v31.h[5]
	ins	v26.h[1], v31.h[2]
	ins	v27.h[1], v31.h[6]
	ins	v20.h[1], v31.h[0]
	ins	v28.h[1], v31.h[3]
	ins	v24.h[1], v31.h[7]
	ins	v21.h[1], v31.h[1]
	ins	v25.h[1], v31.h[4]
	add	x2, x1, 688
#APP
// 94 "gt864_p9_tobytes_full.c" 1
	ldr q31, [x2]
// 0 "" 2
#NO_APP
	ins	v29.h[2], v31.h[5]
	ins	v26.h[2], v31.h[2]
	ins	v27.h[2], v31.h[6]
	ins	v20.h[2], v31.h[0]
	ins	v28.h[2], v31.h[3]
	ins	v24.h[2], v31.h[7]
	ins	v21.h[2], v31.h[1]
	ins	v25.h[2], v31.h[4]
	add	x2, x1, 704
#APP
// 104 "gt864_p9_tobytes_full.c" 1
	ldr q22, [x2]
// 0 "" 2
#NO_APP
	movi	v23.8h, 0x9
	adrp	x2, .LC1
	ins	v29.h[3], v22.h[5]
	adrp	x9, .LC2
	ldr	q31, [x2, #:lo12:.LC1]
	add	x8, x0, 56
	ins	v26.h[3], v22.h[2]
	add	x7, x0, 164
	sqrdmulh	v14.8h, v29.8h, v23.8h
	add	x6, x0, 272
	ins	v27.h[3], v22.h[6]
	add	x2, x0, 512
	ins	v28.h[3], v22.h[3]
	add	x5, x0, 380
	sqrdmulh	v15.8h, v26.8h, v23.8h
	add	x4, x0, 488
	mls	v29.8h, v14.8h, v31.8h
	add	x3, x0, 596
	ins	v24.h[3], v22.h[7]
	sqrdmulh	v13.8h, v27.8h, v23.8h
	mls	v26.8h, v15.8h, v31.8h
	cmlt	v15.8h, v29.8h, #0
	sqrdmulh	v14.8h, v28.8h, v23.8h
	mls	v27.8h, v13.8h, v31.8h
	ins	v25.h[3], v22.h[4]
	and	v15.16b, v15.16b, v31.16b
	mls	v28.8h, v14.8h, v31.8h
	cmlt	v12.8h, v26.8h, #0
	sqrdmulh	v14.8h, v24.8h, v23.8h
	add	v29.8h, v15.8h, v29.8h
	ins	v20.h[3], v22.h[0]
	ins	v21.h[3], v22.h[1]
	mls	v24.8h, v14.8h, v31.8h
	uzp2	v15.8h, v29.8h, v29.8h
	sqrdmulh	v22.8h, v25.8h, v23.8h
	and	v12.16b, v12.16b, v31.16b
	cmlt	v14.8h, v27.8h, #0
	cmlt	v13.8h, v28.8h, #0
	mls	v25.8h, v22.8h, v31.8h
	add	v12.8h, v12.8h, v26.8h
	uzp1	v29.8h, v29.8h, v29.8h
	shl	v26.8h, v15.8h, 12
	and	v13.16b, v13.16b, v31.16b
	and	v14.16b, v14.16b, v31.16b
	cmlt	v22.8h, v24.8h, #0
	orr	v4.16b, v29.16b, v26.16b
	add	v29.8h, v13.8h, v28.8h
	add	v14.8h, v14.8h, v27.8h
	uzp2	v13.8h, v12.8h, v12.8h
	and	v22.16b, v22.16b, v31.16b
	cmlt	v26.8h, v25.8h, #0
	ushr	v5.8h, v15.8h, 4
	uzp1	v27.8h, v12.8h, v12.8h
	add	v24.8h, v22.8h, v24.8h
	and	v26.16b, v26.16b, v31.16b
	uzp2	v15.8h, v14.8h, v14.8h
	shl	v22.8h, v13.8h, 12
	uzp1	v28.8h, v14.8h, v14.8h
	add	v25.8h, v26.8h, v25.8h
	shl	v14.8h, v15.8h, 12
	uzp2	v26.8h, v29.8h, v29.8h
	orr	v2.16b, v27.16b, v22.16b
	uzp2	v27.8h, v24.8h, v24.8h
	ldr	q22, [x9, #:lo12:.LC2]
	orr	v6.16b, v28.16b, v14.16b
	ushr	v3.8h, v13.8h, 4
	uzp2	v14.8h, v25.8h, v25.8h
	shl	v28.8h, v26.8h, 12
	uzp1	v29.8h, v29.8h, v29.8h
	uzp1	v24.8h, v24.8h, v24.8h
	shl	v13.8h, v27.8h, 12
	tbl	v4.16b, {v4.16b - v5.16b}, v22.16b
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	ushr	v7.8h, v15.8h, 4
	orr	v0.16b, v29.16b, v28.16b
	orr	v16.16b, v24.16b, v13.16b
	uzp1	v25.8h, v25.8h, v25.8h
	str	d4, [x0, 48]
	shl	v24.8h, v14.8h, 12
	st1	{v4.s}[2], [x8]
	ushr	v1.8h, v26.8h, 4
	str	d2, [x0, 156]
	tbl	v6.16b, {v6.16b - v7.16b}, v22.16b
	st1	{v2.s}[2], [x7]
	ushr	v17.8h, v27.8h, 4
	orr	v28.16b, v25.16b, v24.16b
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	ushr	v29.8h, v14.8h, 4
	str	d6, [x0, 264]
	tbl	v16.16b, {v16.16b - v17.16b}, v22.16b
	st1	{v6.s}[2], [x6]
	str	d0, [x2, -140]
	tbl	v28.16b, {v28.16b - v29.16b}, v22.16b
	st1	{v0.s}[2], [x5]
	str	d16, [x0, 480]
	st1	{v16.s}[2], [x4]
	str	d28, [x2, 76]
	st1	{v28.s}[2], [x3]
	add	x3, x1, 96
#APP
// 120 "gt864_p9_tobytes_full.c" 1
	ldr q17, [x3]
// 0 "" 2
#NO_APP
	mov	v26.16b, v30.16b
	mov	v27.16b, v30.16b
	mov	v28.16b, v30.16b
	mov	v24.16b, v30.16b
	mov	v29.16b, v30.16b
	mov	v25.16b, v30.16b
	ins	v20.h[4], v17.h[6]
	ins	v21.h[4], v17.h[7]
	ins	v26.h[4], v17.h[2]
	ins	v27.h[4], v17.h[5]
	ins	v28.h[4], v17.h[3]
	ins	v24.h[0], v17.h[0]
	ins	v29.h[4], v17.h[4]
	ins	v25.h[0], v17.h[1]
	add	x3, x1, 112
#APP
// 136 "gt864_p9_tobytes_full.c" 1
	ldr q17, [x3]
// 0 "" 2
#NO_APP
	ins	v26.h[5], v17.h[2]
	ins	v27.h[5], v17.h[5]
	ins	v28.h[5], v17.h[3]
	ins	v20.h[5], v17.h[6]
	ins	v24.h[1], v17.h[0]
	ins	v29.h[5], v17.h[4]
	ins	v21.h[5], v17.h[7]
	ins	v25.h[1], v17.h[1]
	add	x3, x1, 128
#APP
// 146 "gt864_p9_tobytes_full.c" 1
	ldr q17, [x3]
// 0 "" 2
#NO_APP
	ins	v26.h[6], v17.h[2]
	ins	v27.h[6], v17.h[5]
	ins	v28.h[6], v17.h[3]
	ins	v20.h[6], v17.h[6]
	ins	v24.h[2], v17.h[0]
	ins	v29.h[6], v17.h[4]
	ins	v21.h[6], v17.h[7]
	ins	v25.h[2], v17.h[1]
	add	x3, x1, 528
#APP
// 156 "gt864_p9_tobytes_full.c" 1
	ldr q11, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[7], v11.h[6]
	add	x4, x0, 308
	ins	v21.h[7], v11.h[7]
	add	x3, x0, 524
	ins	v26.h[7], v11.h[2]
	ins	v27.h[7], v11.h[5]
	sqrdmulh	v16.8h, v20.8h, v23.8h
	sqrdmulh	v17.8h, v21.8h, v23.8h
	ins	v28.h[7], v11.h[3]
	ins	v24.h[3], v11.h[0]
	mls	v20.8h, v16.8h, v31.8h
	mls	v21.8h, v17.8h, v31.8h
	ins	v29.h[7], v11.h[4]
	ins	v25.h[3], v11.h[1]
	cmlt	v16.8h, v20.8h, #0
	cmlt	v17.8h, v21.8h, #0
	and	v16.16b, v16.16b, v31.16b
	and	v17.16b, v17.16b, v31.16b
	add	v20.8h, v16.8h, v20.8h
	add	v21.8h, v17.8h, v21.8h
	uzp2	v16.8h, v20.8h, v20.8h
	uzp2	v17.8h, v21.8h, v21.8h
	uzp1	v20.8h, v20.8h, v20.8h
	uzp1	v21.8h, v21.8h, v21.8h
	shl	v10.8h, v16.8h, 12
	shl	v11.8h, v17.8h, 12
	ushr	v13.8h, v16.8h, 4
	ushr	v15.8h, v17.8h, 4
	orr	v12.16b, v20.16b, v10.16b
	orr	v14.16b, v21.16b, v11.16b
	tbl	v20.16b, {v12.16b - v13.16b}, v22.16b
	tbl	v21.16b, {v14.16b - v15.16b}, v22.16b
	str	d20, [x2, -212]
	st1	{v20.s}[2], [x4]
	str	d21, [x2, 4]
	st1	{v21.s}[2], [x3]
	add	x3, x1, 224
#APP
// 168 "gt864_p9_tobytes_full.c" 1
	ldr q21, [x3]
// 0 "" 2
#NO_APP
	mov	v16.16b, v30.16b
	mov	v6.16b, v30.16b
	mov	v7.16b, v30.16b
	mov	v17.16b, v30.16b
	ins	v26.h[0], v21.h[4]
	ins	v27.h[0], v21.h[7]
	ins	v28.h[0], v21.h[5]
	ins	v29.h[0], v21.h[6]
	ins	v16.h[6], v21.h[1]
	ins	v6.h[6], v21.h[2]
	ins	v7.h[6], v21.h[0]
	ins	v17.h[6], v21.h[3]
	add	x3, x1, 624
#APP
// 182 "gt864_p9_tobytes_full.c" 1
	ldr q21, [x3]
// 0 "" 2
#NO_APP
	ins	v26.h[1], v21.h[4]
	ins	v27.h[1], v21.h[7]
	ins	v16.h[7], v21.h[1]
	ins	v28.h[1], v21.h[5]
	ins	v6.h[7], v21.h[2]
	ins	v29.h[1], v21.h[6]
	ins	v7.h[7], v21.h[0]
	ins	v17.h[7], v21.h[3]
	add	x3, x1, 320
#APP
// 192 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	mov	v20.16b, v30.16b
	mov	v21.16b, v30.16b
	ins	v18.h[0], v15.h[0]
	ins	v16.h[0], v15.h[3]
	ins	v19.h[0], v15.h[1]
	ins	v6.h[0], v15.h[4]
	ins	v7.h[0], v15.h[2]
	ins	v17.h[0], v15.h[5]
	ins	v20.h[4], v15.h[6]
	ins	v21.h[4], v15.h[7]
	add	x3, x1, 720
#APP
// 204 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[5], v15.h[6]
	ins	v18.h[1], v15.h[0]
	ins	v16.h[1], v15.h[3]
	ins	v21.h[5], v15.h[7]
	ins	v19.h[1], v15.h[1]
	ins	v6.h[1], v15.h[4]
	ins	v7.h[1], v15.h[2]
	ins	v17.h[1], v15.h[5]
	add	x3, x1, 736
#APP
// 214 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[6], v15.h[6]
	ins	v18.h[2], v15.h[0]
	ins	v16.h[2], v15.h[3]
	ins	v21.h[6], v15.h[7]
	ins	v19.h[2], v15.h[1]
	ins	v6.h[2], v15.h[4]
	ins	v7.h[2], v15.h[2]
	ins	v17.h[2], v15.h[5]
	add	x3, x1, 752
#APP
// 224 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v18.h[3], v15.h[0]
	add	x4, x0, 128
	ins	v19.h[3], v15.h[1]
	add	x3, x0, 344
	ins	v20.h[7], v15.h[6]
	ins	v16.h[3], v15.h[3]
	sqrdmulh	v13.8h, v18.8h, v23.8h
	sqrdmulh	v14.8h, v19.8h, v23.8h
	ins	v21.h[7], v15.h[7]
	ins	v6.h[3], v15.h[4]
	mls	v18.8h, v13.8h, v31.8h
	mls	v19.8h, v14.8h, v31.8h
	ins	v7.h[3], v15.h[2]
	ins	v17.h[3], v15.h[5]
	cmlt	v4.8h, v18.8h, #0
	cmlt	v5.8h, v19.8h, #0
	and	v4.16b, v4.16b, v31.16b
	and	v5.16b, v5.16b, v31.16b
	add	v18.8h, v4.8h, v18.8h
	add	v19.8h, v5.8h, v19.8h
	uzp2	v14.8h, v18.8h, v18.8h
	uzp2	v15.8h, v19.8h, v19.8h
	uzp1	v18.8h, v18.8h, v18.8h
	uzp1	v19.8h, v19.8h, v19.8h
	shl	v12.8h, v14.8h, 12
	shl	v13.8h, v15.8h, 12
	ushr	v3.8h, v14.8h, 4
	ushr	v1.8h, v15.8h, 4
	orr	v2.16b, v18.16b, v12.16b
	orr	v0.16b, v19.16b, v13.16b
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	str	d2, [x0, 120]
	st1	{v2.s}[2], [x4]
	str	d0, [x0, 336]
	st1	{v0.s}[2], [x3]
	add	x3, x1, 192
#APP
// 236 "gt864_p9_tobytes_full.c" 1
	ldr q5, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[4], v5.h[1]
	ins	v17.h[4], v5.h[3]
	mov	v18.16b, v30.16b
	mov	v19.16b, v30.16b
	mov	v15.16b, v16.16b
	mov	v14.16b, v17.16b
	mov	v16.16b, v30.16b
	mov	v17.16b, v30.16b
	ins	v6.h[4], v5.h[2]
	ins	v7.h[4], v5.h[0]
	ins	v18.h[6], v5.h[7]
	ins	v17.h[6], v5.h[4]
	ins	v19.h[6], v5.h[5]
	ins	v16.h[6], v5.h[6]
	add	x3, x1, 208
#APP
// 250 "gt864_p9_tobytes_full.c" 1
	ldr q11, [x3]
// 0 "" 2
#NO_APP
	ins	v15.h[5], v11.h[1]
	add	x6, x0, 200
	ins	v6.h[5], v11.h[2]
	add	x5, x0, 416
	ins	v7.h[5], v11.h[0]
	add	x4, x0, 560
	ins	v14.h[5], v11.h[3]
	add	x3, x0, 632
	sqrdmulh	v9.8h, v15.8h, v23.8h
	sqrdmulh	v10.8h, v6.8h, v23.8h
	ins	v17.h[7], v11.h[4]
	ins	v18.h[7], v11.h[7]
	mls	v15.8h, v9.8h, v31.8h
	sqrdmulh	v9.8h, v7.8h, v23.8h
	mls	v6.8h, v10.8h, v31.8h
	sqrdmulh	v10.8h, v14.8h, v23.8h
	cmlt	v5.8h, v15.8h, #0
	mls	v7.8h, v9.8h, v31.8h
	cmlt	v4.8h, v6.8h, #0
	mls	v14.8h, v10.8h, v31.8h
	and	v5.16b, v5.16b, v31.16b
	cmlt	v10.8h, v7.8h, #0
	and	v4.16b, v4.16b, v31.16b
	ins	v19.h[7], v11.h[5]
	add	v5.8h, v5.8h, v15.8h
	ins	v16.h[7], v11.h[6]
	cmlt	v15.8h, v14.8h, #0
	and	v11.16b, v10.16b, v31.16b
	add	v6.8h, v4.8h, v6.8h
	uzp2	v10.8h, v5.8h, v5.8h
	and	v15.16b, v15.16b, v31.16b
	add	v11.8h, v11.8h, v7.8h
	uzp2	v9.8h, v6.8h, v6.8h
	shl	v8.8h, v10.8h, 12
	add	v15.8h, v15.8h, v14.8h
	uzp1	v5.8h, v5.8h, v5.8h
	uzp2	v14.8h, v11.8h, v11.8h
	shl	v7.8h, v9.8h, 12
	ushr	v13.8h, v10.8h, 4
	orr	v12.16b, v5.16b, v8.16b
	shl	v10.8h, v14.8h, 12
	uzp2	v8.8h, v15.8h, v15.8h
	uzp1	v6.8h, v6.8h, v6.8h
	uzp1	v11.8h, v11.8h, v11.8h
	uzp1	v15.8h, v15.8h, v15.8h
	ushr	v3.8h, v9.8h, 4
	orr	v2.16b, v6.16b, v7.16b
	orr	v4.16b, v11.16b, v10.16b
	shl	v11.8h, v8.8h, 12
	tbl	v12.16b, {v12.16b - v13.16b}, v22.16b
	ushr	v5.8h, v14.8h, 4
	tbl	v13.16b, {v2.16b - v3.16b}, v22.16b
	orr	v6.16b, v15.16b, v11.16b
	ushr	v7.8h, v8.8h, 4
	str	d12, [x0, 192]
	tbl	v14.16b, {v4.16b - v5.16b}, v22.16b
	st1	{v12.s}[2], [x6]
	str	d13, [x0, 408]
	st1	{v13.s}[2], [x5]
	tbl	v15.16b, {v6.16b - v7.16b}, v22.16b
	str	d14, [x0, 552]
	st1	{v14.s}[2], [x4]
	str	d15, [x0, 624]
	st1	{v15.s}[2], [x3]
#APP
// 264 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x1]
// 0 "" 2
#NO_APP
	mov	v4.16b, v30.16b
	mov	v5.16b, v30.16b
	mov	v6.16b, v30.16b
	mov	v7.16b, v30.16b
	ins	v17.h[0], v15.h[0]
	ins	v18.h[0], v15.h[3]
	ins	v19.h[0], v15.h[1]
	ins	v16.h[0], v15.h[2]
	ins	v4.h[0], v15.h[6]
	ins	v5.h[0], v15.h[4]
	ins	v6.h[0], v15.h[7]
	ins	v7.h[0], v15.h[5]
	add	x3, x1, 16
#APP
// 278 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[1], v15.h[0]
	ins	v18.h[1], v15.h[3]
	ins	v4.h[1], v15.h[6]
	ins	v19.h[1], v15.h[1]
	ins	v5.h[1], v15.h[4]
	ins	v6.h[1], v15.h[7]
	ins	v16.h[1], v15.h[2]
	ins	v7.h[1], v15.h[5]
	add	x3, x1, 32
#APP
// 288 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[2], v15.h[0]
	ins	v18.h[2], v15.h[3]
	ins	v4.h[2], v15.h[6]
	ins	v19.h[2], v15.h[1]
	ins	v5.h[2], v15.h[4]
	ins	v6.h[2], v15.h[7]
	ins	v16.h[2], v15.h[2]
	ins	v7.h[2], v15.h[5]
	add	x3, x1, 432
#APP
// 298 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[3], v15.h[0]
	ins	v18.h[3], v15.h[3]
	ins	v4.h[3], v15.h[6]
	ins	v19.h[3], v15.h[1]
	ins	v5.h[3], v15.h[4]
	ins	v6.h[3], v15.h[7]
	ins	v16.h[3], v15.h[2]
	ins	v7.h[3], v15.h[5]
	add	x3, x1, 448
#APP
// 308 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[4], v15.h[0]
	ins	v18.h[4], v15.h[3]
	ins	v4.h[4], v15.h[6]
	ins	v19.h[4], v15.h[1]
	ins	v5.h[4], v15.h[4]
	ins	v6.h[4], v15.h[7]
	ins	v16.h[4], v15.h[2]
	ins	v7.h[4], v15.h[5]
	add	x3, x1, 464
#APP
// 318 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[5], v15.h[0]
	mov	x3, x0
	ins	v18.h[5], v15.h[3]
	add	x6, x0, 80
	ins	v19.h[5], v15.h[1]
	add	x5, x0, 224
	ins	v16.h[5], v15.h[2]
	add	x4, x0, 440
	sqrdmulh	v12.8h, v17.8h, v23.8h
	sqrdmulh	v14.8h, v18.8h, v23.8h
	sqrdmulh	v13.8h, v19.8h, v23.8h
	ins	v4.h[5], v15.h[6]
	mls	v17.8h, v12.8h, v31.8h
	mls	v18.8h, v14.8h, v31.8h
	mls	v19.8h, v13.8h, v31.8h
	sqrdmulh	v14.8h, v16.8h, v23.8h
	cmlt	v0.8h, v17.8h, #0
	cmlt	v1.8h, v18.8h, #0
	cmlt	v9.8h, v19.8h, #0
	mls	v16.8h, v14.8h, v31.8h
	and	v0.16b, v0.16b, v31.16b
	and	v1.16b, v1.16b, v31.16b
	and	v9.16b, v9.16b, v31.16b
	cmlt	v14.8h, v16.8h, #0
	add	v17.8h, v0.8h, v17.8h
	add	v18.8h, v1.8h, v18.8h
	add	v9.8h, v9.8h, v19.8h
	and	v19.16b, v14.16b, v31.16b
	uzp2	v13.8h, v17.8h, v17.8h
	uzp2	v14.8h, v18.8h, v18.8h
	uzp2	v12.8h, v9.8h, v9.8h
	add	v19.8h, v19.8h, v16.8h
	uzp1	v17.8h, v17.8h, v17.8h
	uzp1	v16.8h, v9.8h, v9.8h
	shl	v9.8h, v13.8h, 12
	uzp1	v18.8h, v18.8h, v18.8h
	ushr	v3.8h, v13.8h, 4
	ushr	v11.8h, v14.8h, 4
	orr	v2.16b, v17.16b, v9.16b
	shl	v17.8h, v14.8h, 12
	ushr	v1.8h, v12.8h, 4
	ins	v5.h[5], v15.h[4]
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	orr	v10.16b, v18.16b, v17.16b
	uzp2	v18.8h, v19.8h, v19.8h
	shl	v17.8h, v12.8h, 12
	uzp1	v19.8h, v19.8h, v19.8h
	str	d2, [x3], 8
	tbl	v10.16b, {v10.16b - v11.16b}, v22.16b
	st1	{v2.s}[2], [x3]
	ushr	v9.8h, v18.8h, 4
	orr	v0.16b, v16.16b, v17.16b
	shl	v17.8h, v18.8h, 12
	ins	v6.h[5], v15.h[7]
	str	d10, [x0, 72]
	ins	v7.h[5], v15.h[5]
	st1	{v10.s}[2], [x6]
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	orr	v8.16b, v19.16b, v17.16b
	str	d0, [x0, 216]
	tbl	v8.16b, {v8.16b - v9.16b}, v22.16b
	st1	{v0.s}[2], [x5]
	str	d8, [x0, 432]
	st1	{v8.s}[2], [x4]
	add	x3, x1, 240
#APP
// 332 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	mov	v16.16b, v5.16b
	mov	v17.16b, v30.16b
	mov	v18.16b, v30.16b
	mov	v19.16b, v30.16b
	mov	v5.16b, v30.16b
	ins	v4.h[6], v15.h[2]
	ins	v16.h[6], v15.h[0]
	ins	v6.h[6], v15.h[3]
	ins	v7.h[6], v15.h[1]
	ins	v17.h[6], v15.h[5]
	ins	v18.h[6], v15.h[6]
	ins	v19.h[6], v15.h[7]
	ins	v5.h[6], v15.h[4]
	add	x3, x1, 256
#APP
// 346 "gt864_p9_tobytes_full.c" 1
	ldr q14, [x3]
// 0 "" 2
#NO_APP
	ins	v4.h[7], v14.h[2]
	add	x5, x0, 152
	ins	v16.h[7], v14.h[0]
	add	x4, x0, 296
	ins	v6.h[7], v14.h[3]
	add	x3, x0, 368
	ins	v7.h[7], v14.h[1]
	sqrdmulh	v11.8h, v4.8h, v23.8h
	sqrdmulh	v15.8h, v16.8h, v23.8h
	sqrdmulh	v10.8h, v6.8h, v23.8h
	ins	v17.h[7], v14.h[5]
	mls	v4.8h, v11.8h, v31.8h
	mls	v16.8h, v15.8h, v31.8h
	sqrdmulh	v15.8h, v7.8h, v23.8h
	mls	v6.8h, v10.8h, v31.8h
	ins	v18.h[7], v14.h[6]
	mov	v11.16b, v16.16b
	cmlt	v16.8h, v4.8h, #0
	mls	v7.8h, v15.8h, v31.8h
	cmlt	v10.8h, v6.8h, #0
	cmlt	v15.8h, v11.8h, #0
	and	v16.16b, v16.16b, v31.16b
	ins	v19.h[7], v14.h[7]
	ins	v5.h[7], v14.h[4]
	and	v15.16b, v15.16b, v31.16b
	add	v16.8h, v16.8h, v4.8h
	and	v10.16b, v10.16b, v31.16b
	cmlt	v14.8h, v7.8h, #0
	add	v15.8h, v15.8h, v11.8h
	uzp2	v11.8h, v16.8h, v16.8h
	add	v10.8h, v10.8h, v6.8h
	and	v14.16b, v14.16b, v31.16b
	uzp2	v9.8h, v15.8h, v15.8h
	shl	v6.8h, v11.8h, 12
	uzp1	v16.8h, v16.8h, v16.8h
	uzp2	v8.8h, v10.8h, v10.8h
	add	v14.8h, v14.8h, v7.8h
	uzp1	v15.8h, v15.8h, v15.8h
	orr	v12.16b, v16.16b, v6.16b
	shl	v16.8h, v9.8h, 12
	uzp2	v4.8h, v14.8h, v14.8h
	uzp1	v7.8h, v10.8h, v10.8h
	ushr	v13.8h, v11.8h, 4
	orr	v0.16b, v15.16b, v16.16b
	shl	v16.8h, v8.8h, 12
	uzp1	v14.8h, v14.8h, v14.8h
	ushr	v1.8h, v9.8h, 4
	tbl	v6.16b, {v12.16b - v13.16b}, v22.16b
	orr	v2.16b, v7.16b, v16.16b
	shl	v16.8h, v4.8h, 12
	ushr	v3.8h, v8.8h, 4
	tbl	v7.16b, {v0.16b - v1.16b}, v22.16b
	str	d6, [x0, 144]
	ushr	v11.8h, v4.8h, 4
	st1	{v6.s}[2], [x5]
	orr	v10.16b, v14.16b, v16.16b
	tbl	v15.16b, {v2.16b - v3.16b}, v22.16b
	str	d7, [x0, 288]
	st1	{v7.s}[2], [x4]
	tbl	v16.16b, {v10.16b - v11.16b}, v22.16b
	str	d15, [x0, 360]
	st1	{v15.s}[2], [x3]
	str	d16, [x0, 504]
	st1	{v16.s}[2], [x2]
	add	x3, x1, 48
#APP
// 360 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	mov	v6.16b, v30.16b
	mov	v7.16b, v30.16b
	mov	v16.16b, v30.16b
	mov	v4.16b, v30.16b
	ins	v17.h[0], v15.h[1]
	ins	v18.h[0], v15.h[2]
	ins	v19.h[0], v15.h[3]
	ins	v5.h[0], v15.h[0]
	ins	v6.h[0], v15.h[4]
	ins	v7.h[0], v15.h[7]
	ins	v16.h[0], v15.h[5]
	ins	v4.h[0], v15.h[6]
	add	x3, x1, 64
#APP
// 374 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[1], v15.h[1]
	ins	v6.h[1], v15.h[4]
	ins	v7.h[1], v15.h[7]
	ins	v18.h[1], v15.h[2]
	ins	v16.h[1], v15.h[5]
	ins	v19.h[1], v15.h[3]
	ins	v4.h[1], v15.h[6]
	ins	v5.h[1], v15.h[0]
	add	x3, x1, 80
#APP
// 384 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[2], v15.h[1]
	ins	v6.h[2], v15.h[4]
	ins	v7.h[2], v15.h[7]
	ins	v18.h[2], v15.h[2]
	ins	v16.h[2], v15.h[5]
	ins	v19.h[2], v15.h[3]
	ins	v4.h[2], v15.h[6]
	ins	v5.h[2], v15.h[0]
	add	x3, x1, 288
#APP
// 394 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[2], v15.h[6]
	ins	v6.h[6], v15.h[0]
	ins	v7.h[6], v15.h[3]
	ins	v21.h[2], v15.h[7]
	ins	v16.h[6], v15.h[1]
	ins	v24.h[6], v15.h[4]
	ins	v4.h[6], v15.h[2]
	ins	v25.h[6], v15.h[5]
	add	x3, x1, 304
#APP
// 404 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[3], v15.h[6]
	ins	v6.h[7], v15.h[0]
	ins	v7.h[7], v15.h[3]
	ins	v21.h[3], v15.h[7]
	ins	v16.h[7], v15.h[1]
	ins	v24.h[7], v15.h[4]
	ins	v4.h[7], v15.h[2]
	ins	v25.h[7], v15.h[5]
	add	x3, x1, 480
#APP
// 414 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[3], v15.h[1]
	ins	v6.h[3], v15.h[4]
	ins	v7.h[3], v15.h[7]
	ins	v18.h[3], v15.h[2]
	mov	v3.16b, v17.16b
	ins	v16.h[3], v15.h[5]
	ins	v19.h[3], v15.h[3]
	ins	v4.h[3], v15.h[6]
	ins	v5.h[3], v15.h[0]
	add	x3, x1, 496
#APP
// 424 "gt864_p9_tobytes_full.c" 1
	ldr q17, [x3]
// 0 "" 2
#NO_APP
	ins	v3.h[4], v17.h[1]
	ins	v6.h[4], v17.h[4]
	ins	v7.h[4], v17.h[7]
	ins	v18.h[4], v17.h[2]
	ins	v16.h[4], v17.h[5]
	ins	v19.h[4], v17.h[3]
	ins	v4.h[4], v17.h[6]
	ins	v5.h[4], v17.h[0]
	add	x3, x1, 512
#APP
// 434 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v3.h[5], v15.h[1]
	add	x10, x0, 44
	ins	v7.h[5], v15.h[7]
	add	x9, x0, 116
	ins	v6.h[5], v15.h[4]
	add	x8, x0, 188
	ins	v16.h[5], v15.h[5]
	add	x7, x0, 260
	sqrdmulh	v17.8h, v3.8h, v23.8h
	add	x6, x0, 332
	ins	v18.h[5], v15.h[2]
	add	x5, x0, 476
	sqrdmulh	v14.8h, v6.8h, v23.8h
	add	x4, x0, 548
	ins	v19.h[5], v15.h[3]
	add	x3, x0, 584
	mls	v3.8h, v17.8h, v31.8h
	sqrdmulh	v17.8h, v7.8h, v23.8h
	mls	v6.8h, v14.8h, v31.8h
	ins	v4.h[5], v15.h[6]
	sqrdmulh	v14.8h, v18.8h, v23.8h
	mls	v7.8h, v17.8h, v31.8h
	sqrdmulh	v17.8h, v16.8h, v23.8h
	cmlt	v9.8h, v3.8h, #0
	mls	v18.8h, v14.8h, v31.8h
	ins	v5.h[5], v15.h[0]
	mls	v16.8h, v17.8h, v31.8h
	sqrdmulh	v17.8h, v19.8h, v23.8h
	sqrdmulh	v15.8h, v4.8h, v23.8h
	and	v9.16b, v9.16b, v31.16b
	cmlt	v10.8h, v6.8h, #0
	mls	v19.8h, v17.8h, v31.8h
	mov	v17.16b, v4.16b
	add	v9.8h, v9.8h, v3.8h
	cmlt	v12.8h, v7.8h, #0
	cmlt	v13.8h, v18.8h, #0
	mls	v17.8h, v15.8h, v31.8h
	sqrdmulh	v15.8h, v5.8h, v23.8h
	uzp2	v11.8h, v9.8h, v9.8h
	and	v10.16b, v10.16b, v31.16b
	and	v12.16b, v12.16b, v31.16b
	mls	v5.8h, v15.8h, v31.8h
	and	v13.16b, v13.16b, v31.16b
	cmlt	v15.8h, v19.8h, #0
	cmlt	v14.8h, v16.8h, #0
	add	v10.8h, v10.8h, v6.8h
	add	v12.8h, v12.8h, v7.8h
	add	v13.8h, v13.8h, v18.8h
	shl	v7.8h, v11.8h, 12
	and	v18.16b, v15.16b, v31.16b
	uzp1	v9.8h, v9.8h, v9.8h
	and	v14.16b, v14.16b, v31.16b
	uzp2	v15.8h, v10.8h, v10.8h
	ushr	v1.8h, v11.8h, 4
	orr	v0.16b, v9.16b, v7.16b
	add	v14.8h, v14.8h, v16.8h
	cmlt	v8.8h, v17.8h, #0
	add	v16.8h, v18.8h, v19.8h
	cmlt	v18.8h, v5.8h, #0
	uzp2	v7.8h, v12.8h, v12.8h
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	and	v8.16b, v8.16b, v31.16b
	uzp2	v1.8h, v14.8h, v14.8h
	shl	v19.8h, v15.8h, 12
	uzp1	v10.8h, v10.8h, v10.8h
	str	d0, [x0, 36]
	and	v18.16b, v18.16b, v31.16b
	st1	{v0.s}[2], [x10]
	uzp2	v6.8h, v13.8h, v13.8h
	add	v17.8h, v8.8h, v17.8h
	ushr	v9.8h, v15.8h, 4
	add	v18.8h, v18.8h, v5.8h
	uzp2	v15.8h, v16.8h, v16.8h
	orr	v8.16b, v10.16b, v19.16b
	ushr	v5.8h, v7.8h, 4
	shl	v19.8h, v7.8h, 12
	uzp1	v12.8h, v12.8h, v12.8h
	shl	v7.8h, v1.8h, 12
	uzp1	v14.8h, v14.8h, v14.8h
	tbl	v8.16b, {v8.16b - v9.16b}, v22.16b
	orr	v4.16b, v12.16b, v19.16b
	uzp2	v9.8h, v17.8h, v17.8h
	orr	v2.16b, v14.16b, v7.16b
	shl	v19.8h, v6.8h, 12
	str	d8, [x0, 108]
	shl	v7.8h, v15.8h, 12
	st1	{v8.s}[2], [x9]
	uzp1	v13.8h, v13.8h, v13.8h
	uzp1	v16.8h, v16.8h, v16.8h
	uzp2	v14.8h, v18.8h, v18.8h
	uzp1	v17.8h, v17.8h, v17.8h
	orr	v10.16b, v13.16b, v19.16b
	orr	v12.16b, v16.16b, v7.16b
	ushr	v11.8h, v6.8h, 4
	shl	v16.8h, v9.8h, 12
	tbl	v19.16b, {v4.16b - v5.16b}, v22.16b
	ushr	v3.8h, v1.8h, 4
	tbl	v7.16b, {v10.16b - v11.16b}, v22.16b
	orr	v4.16b, v17.16b, v16.16b
	ushr	v13.8h, v15.8h, 4
	str	d19, [x0, 180]
	shl	v17.8h, v14.8h, 12
	st1	{v19.s}[2], [x8]
	uzp1	v8.8h, v18.8h, v18.8h
	str	d7, [x0, 252]
	tbl	v15.16b, {v2.16b - v3.16b}, v22.16b
	st1	{v7.s}[2], [x7]
	ushr	v5.8h, v9.8h, 4
	tbl	v16.16b, {v12.16b - v13.16b}, v22.16b
	orr	v18.16b, v8.16b, v17.16b
	ushr	v19.8h, v14.8h, 4
	str	d15, [x2, -188]
	tbl	v17.16b, {v4.16b - v5.16b}, v22.16b
	st1	{v15.s}[2], [x6]
	str	d16, [x2, -44]
	st1	{v16.s}[2], [x5]
	tbl	v18.16b, {v18.16b - v19.16b}, v22.16b
	str	d17, [x2, 28]
	st1	{v17.s}[2], [x4]
	str	d18, [x0, 576]
	st1	{v18.s}[2], [x3]
	add	x3, x1, 544
#APP
// 452 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[0], v15.h[2]
	ins	v21.h[0], v15.h[3]
	ins	v24.h[4], v15.h[0]
	mov	v19.16b, v30.16b
	mov	v18.16b, v20.16b
	mov	v16.16b, v21.16b
	mov	v17.16b, v24.16b
	mov	v20.16b, v30.16b
	mov	v21.16b, v30.16b
	mov	v24.16b, v30.16b
	ins	v25.h[4], v15.h[1]
	ins	v20.h[0], v15.h[5]
	ins	v21.h[0], v15.h[6]
	ins	v24.h[0], v15.h[4]
	ins	v19.h[0], v15.h[7]
	add	x3, x1, 560
#APP
// 466 "gt864_p9_tobytes_full.c" 1
	ldr q6, [x3]
// 0 "" 2
#NO_APP
	ins	v18.h[1], v6.h[2]
	add	x6, x0, 32
	ins	v16.h[1], v6.h[3]
	add	x5, x0, 248
	ins	v17.h[5], v6.h[0]
	add	x4, x0, 404
	ins	v25.h[5], v6.h[1]
	add	x3, x0, 620
	sqrdmulh	v14.8h, v18.8h, v23.8h
	sqrdmulh	v15.8h, v16.8h, v23.8h
	ins	v20.h[1], v6.h[5]
	ins	v21.h[1], v6.h[6]
	mls	v18.8h, v14.8h, v31.8h
	sqrdmulh	v14.8h, v17.8h, v23.8h
	mls	v16.8h, v15.8h, v31.8h
	sqrdmulh	v15.8h, v25.8h, v23.8h
	cmlt	v7.8h, v18.8h, #0
	mls	v17.8h, v14.8h, v31.8h
	ins	v24.h[1], v6.h[4]
	mls	v25.8h, v15.8h, v31.8h
	and	v7.16b, v7.16b, v31.16b
	cmlt	v15.8h, v16.8h, #0
	cmlt	v12.8h, v17.8h, #0
	cmlt	v14.8h, v25.8h, #0
	add	v18.8h, v7.8h, v18.8h
	and	v15.16b, v15.16b, v31.16b
	and	v12.16b, v12.16b, v31.16b
	ins	v19.h[1], v6.h[7]
	uzp2	v13.8h, v18.8h, v18.8h
	add	v16.8h, v15.8h, v16.8h
	add	v15.8h, v12.8h, v17.8h
	and	v17.16b, v14.16b, v31.16b
	shl	v12.8h, v13.8h, 12
	uzp2	v14.8h, v16.8h, v16.8h
	uzp1	v18.8h, v18.8h, v18.8h
	add	v25.8h, v17.8h, v25.8h
	uzp2	v17.8h, v15.8h, v15.8h
	uzp1	v16.8h, v16.8h, v16.8h
	orr	v2.16b, v18.16b, v12.16b
	uzp2	v18.8h, v25.8h, v25.8h
	shl	v12.8h, v14.8h, 12
	ushr	v3.8h, v13.8h, 4
	uzp1	v15.8h, v15.8h, v15.8h
	shl	v13.8h, v17.8h, 12
	orr	v4.16b, v16.16b, v12.16b
	uzp1	v25.8h, v25.8h, v25.8h
	shl	v16.8h, v18.8h, 12
	ushr	v5.8h, v14.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	orr	v0.16b, v15.16b, v13.16b
	ushr	v1.8h, v17.8h, 4
	tbl	v4.16b, {v4.16b - v5.16b}, v22.16b
	orr	v10.16b, v25.16b, v16.16b
	str	d2, [x0, 24]
	ushr	v11.8h, v18.8h, 4
	st1	{v2.s}[2], [x6]
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	str	d4, [x0, 240]
	st1	{v4.s}[2], [x5]
	tbl	v25.16b, {v10.16b - v11.16b}, v22.16b
	str	d0, [x2, -116]
	st1	{v0.s}[2], [x4]
	str	d25, [x2, 100]
	st1	{v25.s}[2], [x3]
	add	x3, x1, 336
#APP
// 480 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	mov	v16.16b, v30.16b
	mov	v17.16b, v30.16b
	mov	v18.16b, v30.16b
	mov	v25.16b, v30.16b
	ins	v20.h[2], v15.h[1]
	ins	v21.h[2], v15.h[2]
	ins	v24.h[2], v15.h[0]
	ins	v19.h[2], v15.h[3]
	ins	v16.h[2], v15.h[7]
	ins	v17.h[2], v15.h[4]
	ins	v18.h[2], v15.h[5]
	ins	v25.h[2], v15.h[6]
	add	x3, x1, 352
#APP
// 494 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[3], v15.h[7]
	ins	v20.h[3], v15.h[1]
	ins	v17.h[3], v15.h[4]
	ins	v21.h[3], v15.h[2]
	ins	v18.h[3], v15.h[5]
	ins	v24.h[3], v15.h[0]
	ins	v19.h[3], v15.h[3]
	ins	v25.h[3], v15.h[6]
	add	x3, x1, 368
#APP
// 504 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[4], v15.h[7]
	ins	v20.h[4], v15.h[1]
	ins	v17.h[4], v15.h[4]
	ins	v21.h[4], v15.h[2]
	ins	v18.h[4], v15.h[5]
	ins	v24.h[4], v15.h[0]
	ins	v19.h[4], v15.h[3]
	ins	v25.h[4], v15.h[6]
	add	x3, x1, 768
#APP
// 514 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[5], v15.h[7]
	ins	v20.h[5], v15.h[1]
	ins	v17.h[5], v15.h[4]
	ins	v21.h[5], v15.h[2]
	ins	v18.h[5], v15.h[5]
	ins	v24.h[5], v15.h[0]
	ins	v19.h[5], v15.h[3]
	ins	v25.h[5], v15.h[6]
	add	x3, x1, 784
#APP
// 524 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[6], v15.h[7]
	ins	v20.h[6], v15.h[1]
	ins	v17.h[6], v15.h[4]
	ins	v21.h[6], v15.h[2]
	ins	v18.h[6], v15.h[5]
	ins	v24.h[6], v15.h[0]
	ins	v19.h[6], v15.h[3]
	ins	v25.h[6], v15.h[6]
	add	x3, x1, 800
#APP
// 534 "gt864_p9_tobytes_full.c" 1
	ldr q7, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[7], v7.h[1]
	add	x6, x0, 104
	ins	v21.h[7], v7.h[2]
	add	x5, x0, 320
	ins	v24.h[7], v7.h[0]
	add	x4, x0, 464
	ins	v19.h[7], v7.h[3]
	add	x3, x0, 536
	sqrdmulh	v14.8h, v20.8h, v23.8h
	sqrdmulh	v15.8h, v21.8h, v23.8h
	ins	v16.h[7], v7.h[7]
	ins	v17.h[7], v7.h[4]
	mls	v20.8h, v14.8h, v31.8h
	sqrdmulh	v14.8h, v24.8h, v23.8h
	mls	v21.8h, v15.8h, v31.8h
	sqrdmulh	v15.8h, v19.8h, v23.8h
	cmlt	v6.8h, v20.8h, #0
	mls	v24.8h, v14.8h, v31.8h
	ins	v18.h[7], v7.h[5]
	mls	v19.8h, v15.8h, v31.8h
	and	v6.16b, v6.16b, v31.16b
	cmlt	v15.8h, v21.8h, #0
	cmlt	v13.8h, v24.8h, #0
	cmlt	v14.8h, v19.8h, #0
	add	v20.8h, v6.8h, v20.8h
	and	v15.16b, v15.16b, v31.16b
	and	v13.16b, v13.16b, v31.16b
	ins	v25.h[7], v7.h[6]
	uzp2	v12.8h, v20.8h, v20.8h
	add	v21.8h, v15.8h, v21.8h
	add	v15.8h, v13.8h, v24.8h
	and	v24.16b, v14.16b, v31.16b
	shl	v13.8h, v12.8h, 12
	uzp2	v14.8h, v21.8h, v21.8h
	uzp1	v20.8h, v20.8h, v20.8h
	add	v24.8h, v24.8h, v19.8h
	uzp1	v21.8h, v21.8h, v21.8h
	uzp2	v19.8h, v15.8h, v15.8h
	orr	v2.16b, v20.16b, v13.16b
	shl	v13.8h, v14.8h, 12
	uzp2	v20.8h, v24.8h, v24.8h
	uzp1	v15.8h, v15.8h, v15.8h
	ushr	v3.8h, v12.8h, 4
	orr	v4.16b, v21.16b, v13.16b
	shl	v13.8h, v19.8h, 12
	uzp1	v24.8h, v24.8h, v24.8h
	shl	v21.8h, v20.8h, 12
	ushr	v5.8h, v14.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	orr	v0.16b, v15.16b, v13.16b
	ushr	v1.8h, v19.8h, 4
	tbl	v4.16b, {v4.16b - v5.16b}, v22.16b
	orr	v10.16b, v24.16b, v21.16b
	str	d2, [x0, 96]
	ushr	v11.8h, v20.8h, 4
	st1	{v2.s}[2], [x6]
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	str	d4, [x0, 312]
	st1	{v4.s}[2], [x5]
	tbl	v24.16b, {v10.16b - v11.16b}, v22.16b
	str	d0, [x0, 456]
	st1	{v0.s}[2], [x4]
	str	d24, [x0, 528]
	st1	{v24.s}[2], [x3]
	add	x3, x1, 592
#APP
// 548 "gt864_p9_tobytes_full.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	mov	v19.16b, v30.16b
	mov	v20.16b, v30.16b
	mov	v21.16b, v30.16b
	mov	v24.16b, v30.16b
	ins	v16.h[0], v15.h[3]
	ins	v17.h[0], v15.h[0]
	ins	v18.h[0], v15.h[1]
	ins	v25.h[0], v15.h[2]
	ins	v19.h[0], v15.h[6]
	ins	v20.h[0], v15.h[4]
	ins	v21.h[0], v15.h[7]
	ins	v24.h[0], v15.h[5]
	add	x3, x1, 608
#APP
// 562 "gt864_p9_tobytes_full.c" 1
	ldr q7, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[1], v7.h[3]
	add	x6, x0, 68
	ins	v17.h[1], v7.h[0]
	add	x5, x0, 176
	ins	v18.h[1], v7.h[1]
	add	x4, x0, 392
	ins	v25.h[1], v7.h[2]
	add	x3, x0, 608
	sqrdmulh	v14.8h, v16.8h, v23.8h
	sqrdmulh	v15.8h, v17.8h, v23.8h
	sqrdmulh	v13.8h, v18.8h, v23.8h
	ins	v19.h[1], v7.h[6]
	mls	v16.8h, v14.8h, v31.8h
	mls	v17.8h, v15.8h, v31.8h
	mls	v18.8h, v13.8h, v31.8h
	ins	v20.h[1], v7.h[4]
	cmlt	v15.8h, v16.8h, #0
	mov	v14.16b, v17.16b
	sqrdmulh	v17.8h, v25.8h, v23.8h
	cmlt	v13.8h, v18.8h, #0
	and	v15.16b, v15.16b, v31.16b
	ins	v21.h[1], v7.h[7]
	mls	v25.8h, v17.8h, v31.8h
	cmlt	v17.8h, v14.8h, #0
	add	v16.8h, v15.8h, v16.8h
	and	v13.16b, v13.16b, v31.16b
	cmlt	v15.8h, v25.8h, #0
	and	v17.16b, v17.16b, v31.16b
	uzp2	v12.8h, v16.8h, v16.8h
	uzp1	v16.8h, v16.8h, v16.8h
	ins	v24.h[1], v7.h[5]
	add	v17.8h, v17.8h, v14.8h
	add	v14.8h, v13.8h, v18.8h
	and	v18.16b, v15.16b, v31.16b
	shl	v13.8h, v12.8h, 12
	uzp2	v15.8h, v17.8h, v17.8h
	uzp1	v17.8h, v17.8h, v17.8h
	add	v25.8h, v18.8h, v25.8h
	orr	v0.16b, v16.16b, v13.16b
	uzp2	v18.8h, v14.8h, v14.8h
	shl	v13.8h, v15.8h, 12
	uzp2	v16.8h, v25.8h, v25.8h
	uzp1	v14.8h, v14.8h, v14.8h
	ushr	v1.8h, v12.8h, 4
	orr	v2.16b, v17.16b, v13.16b
	shl	v13.8h, v18.8h, 12
	uzp1	v25.8h, v25.8h, v25.8h
	shl	v17.8h, v16.8h, 12
	ushr	v3.8h, v15.8h, 4
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	orr	v4.16b, v14.16b, v13.16b
	ushr	v5.8h, v18.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	orr	v10.16b, v25.16b, v17.16b
	str	d0, [x0, 60]
	ushr	v11.8h, v16.8h, 4
	st1	{v0.s}[2], [x6]
	tbl	v4.16b, {v4.16b - v5.16b}, v22.16b
	str	d2, [x0, 168]
	st1	{v2.s}[2], [x5]
	tbl	v25.16b, {v10.16b - v11.16b}, v22.16b
	str	d4, [x0, 384]
	st1	{v4.s}[2], [x4]
	str	d25, [x0, 600]
	st1	{v25.s}[2], [x3]
	add	x3, x1, 384
#APP
// 576 "gt864_p9_tobytes_full.c" 1
	ldr q25, [x3]
// 0 "" 2
#NO_APP
	mov	v18.16b, v30.16b
	mov	v17.16b, v30.16b
	mov	v15.16b, v30.16b
	ins	v19.h[2], v25.h[2]
	ins	v20.h[2], v25.h[0]
	ins	v21.h[2], v25.h[3]
	ins	v24.h[2], v25.h[1]
	ins	v18.h[2], v25.h[5]
	ins	v17.h[2], v25.h[6]
	ins	v15.h[2], v25.h[4]
	ins	v30.h[2], v25.h[7]
	add	x3, x1, 400
#APP
// 590 "gt864_p9_tobytes_full.c" 1
	ldr q25, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[3], v25.h[2]
	ins	v18.h[3], v25.h[5]
	ins	v20.h[3], v25.h[0]
	ins	v21.h[3], v25.h[3]
	ins	v17.h[3], v25.h[6]
	ins	v24.h[3], v25.h[1]
	ins	v15.h[3], v25.h[4]
	ins	v30.h[3], v25.h[7]
	add	x3, x1, 416
#APP
// 600 "gt864_p9_tobytes_full.c" 1
	ldr q25, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[4], v25.h[2]
	ins	v18.h[4], v25.h[5]
	ins	v20.h[4], v25.h[0]
	ins	v21.h[4], v25.h[3]
	ins	v17.h[4], v25.h[6]
	ins	v24.h[4], v25.h[1]
	ins	v15.h[4], v25.h[4]
	ins	v30.h[4], v25.h[7]
	add	x3, x1, 640
#APP
// 610 "gt864_p9_tobytes_full.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v29.h[2], v16.h[6]
	ins	v26.h[2], v16.h[4]
	ins	v27.h[2], v16.h[7]
	ins	v18.h[0], v16.h[1]
	mov	v25.16b, v29.16b
	mov	v29.16b, v15.16b
	ins	v28.h[2], v16.h[5]
	ins	v17.h[0], v16.h[2]
	ins	v30.h[0], v16.h[3]
	ins	v29.h[0], v16.h[0]
	add	x3, x1, 656
#APP
// 620 "gt864_p9_tobytes_full.c" 1
	ldr q7, [x3]
// 0 "" 2
#NO_APP
	ins	v26.h[3], v7.h[4]
	add	x6, x0, 20
	ins	v27.h[3], v7.h[7]
	add	x5, x0, 92
	ins	v28.h[3], v7.h[5]
	add	x4, x0, 236
	ins	v25.h[3], v7.h[6]
	add	x3, x0, 452
	sqrdmulh	v14.8h, v26.8h, v23.8h
	sqrdmulh	v15.8h, v27.8h, v23.8h
	sqrdmulh	v16.8h, v28.8h, v23.8h
	ins	v29.h[1], v7.h[0]
	mls	v26.8h, v14.8h, v31.8h
	mls	v27.8h, v15.8h, v31.8h
	sqrdmulh	v15.8h, v25.8h, v23.8h
	mls	v28.8h, v16.8h, v31.8h
	cmlt	v6.8h, v26.8h, #0
	cmlt	v16.8h, v27.8h, #0
	mls	v25.8h, v15.8h, v31.8h
	cmlt	v15.8h, v28.8h, #0
	and	v6.16b, v6.16b, v31.16b
	and	v16.16b, v16.16b, v31.16b
	cmlt	v14.8h, v25.8h, #0
	and	v15.16b, v15.16b, v31.16b
	add	v26.8h, v6.8h, v26.8h
	add	v27.8h, v16.8h, v27.8h
	and	v16.16b, v14.16b, v31.16b
	add	v28.8h, v15.8h, v28.8h
	uzp2	v12.8h, v26.8h, v26.8h
	uzp2	v13.8h, v27.8h, v27.8h
	add	v25.8h, v16.8h, v25.8h
	uzp1	v26.8h, v26.8h, v26.8h
	shl	v15.8h, v12.8h, 12
	uzp2	v16.8h, v28.8h, v28.8h
	uzp1	v27.8h, v27.8h, v27.8h
	shl	v11.8h, v13.8h, 12
	orr	v2.16b, v26.16b, v15.16b
	uzp2	v26.8h, v25.8h, v25.8h
	ushr	v3.8h, v12.8h, 4
	uzp1	v28.8h, v28.8h, v28.8h
	shl	v12.8h, v16.8h, 12
	orr	v0.16b, v27.16b, v11.16b
	uzp1	v25.8h, v25.8h, v25.8h
	shl	v27.8h, v26.8h, 12
	ushr	v1.8h, v13.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v22.16b
	orr	v4.16b, v28.16b, v12.16b
	ushr	v5.8h, v16.8h, 4
	orr	v14.16b, v25.16b, v27.16b
	tbl	v0.16b, {v0.16b - v1.16b}, v22.16b
	str	d2, [x0, 12]
	ushr	v15.8h, v26.8h, 4
	st1	{v2.s}[2], [x6]
	tbl	v4.16b, {v4.16b - v5.16b}, v22.16b
	mov	v27.16b, v17.16b
	ins	v18.h[1], v7.h[1]
	str	d0, [x0, 84]
	tbl	v26.16b, {v14.16b - v15.16b}, v22.16b
	st1	{v0.s}[2], [x5]
	mov	v28.16b, v29.16b
	str	d4, [x0, 228]
	ins	v27.h[1], v7.h[2]
	st1	{v4.s}[2], [x4]
	ins	v30.h[1], v7.h[3]
	str	d26, [x2, -68]
	st1	{v26.s}[2], [x3]
	add	x3, x1, 816
#APP
// 634 "gt864_p9_tobytes_full.c" 1
	ldr q29, [x3]
// 0 "" 2
#NO_APP
	mov	v26.16b, v18.16b
	ins	v19.h[5], v29.h[2]
	ins	v20.h[5], v29.h[0]
	ins	v21.h[5], v29.h[3]
	ins	v26.h[5], v29.h[5]
	ins	v27.h[5], v29.h[6]
	ins	v24.h[5], v29.h[1]
	ins	v28.h[5], v29.h[4]
	ins	v30.h[5], v29.h[7]
	add	x3, x1, 832
#APP
// 644 "gt864_p9_tobytes_full.c" 1
	ldr q25, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[6], v25.h[2]
	ins	v26.h[6], v25.h[5]
	ins	v20.h[6], v25.h[0]
	ins	v21.h[6], v25.h[3]
	ins	v27.h[6], v25.h[6]
	ins	v24.h[6], v25.h[1]
	ins	v28.h[6], v25.h[4]
	ins	v30.h[6], v25.h[7]
	add	x1, x1, 848
#APP
// 654 "gt864_p9_tobytes_full.c" 1
	ldr q29, [x1]
// 0 "" 2
#NO_APP
	ins	v19.h[7], v29.h[2]
	add	x9, x0, 140
	ins	v26.h[7], v29.h[5]
	add	x8, x0, 212
	ins	v20.h[7], v29.h[0]
	add	x7, x0, 284
	ins	v21.h[7], v29.h[3]
	add	x6, x0, 356
	sqrdmulh	v7.8h, v19.8h, v23.8h
	add	x5, x0, 428
	sqrdmulh	v18.8h, v26.8h, v23.8h
	add	x4, x0, 500
	ins	v27.h[7], v29.h[6]
	add	x3, x0, 572
	sqrdmulh	v25.8h, v20.8h, v23.8h
	add	x1, x0, 644
	mls	v19.8h, v7.8h, v31.8h
	mls	v26.8h, v18.8h, v31.8h
	ins	v28.h[7], v29.h[4]
	mls	v20.8h, v25.8h, v31.8h
	sqrdmulh	v18.8h, v21.8h, v23.8h
	sqrdmulh	v25.8h, v27.8h, v23.8h
	ins	v24.h[7], v29.h[1]
	cmlt	v7.8h, v19.8h, #0
	mls	v21.8h, v18.8h, v31.8h
	mls	v27.8h, v25.8h, v31.8h
	ins	v30.h[7], v29.h[7]
	cmlt	v25.8h, v20.8h, #0
	sqrdmulh	v29.8h, v24.8h, v23.8h
	sqrdmulh	v6.8h, v28.8h, v23.8h
	cmlt	v18.8h, v26.8h, #0
	and	v7.16b, v7.16b, v31.16b
	mls	v24.8h, v29.8h, v31.8h
	mls	v28.8h, v6.8h, v31.8h
	sqrdmulh	v29.8h, v30.8h, v23.8h
	add	v7.8h, v7.8h, v19.8h
	and	v18.16b, v18.16b, v31.16b
	and	v19.16b, v25.16b, v31.16b
	cmlt	v23.8h, v21.8h, #0
	cmlt	v25.8h, v27.8h, #0
	mls	v30.8h, v29.8h, v31.8h
	add	v18.8h, v18.8h, v26.8h
	and	v23.16b, v23.16b, v31.16b
	and	v29.16b, v25.16b, v31.16b
	cmlt	v26.8h, v24.8h, #0
	cmlt	v25.8h, v28.8h, #0
	uzp2	v6.8h, v7.8h, v7.8h
	add	v27.8h, v29.8h, v27.8h
	add	v19.8h, v19.8h, v20.8h
	add	v23.8h, v23.8h, v21.8h
	cmlt	v29.8h, v30.8h, #0
	uzp2	v21.8h, v18.8h, v18.8h
	and	v26.16b, v26.16b, v31.16b
	and	v25.16b, v25.16b, v31.16b
	uzp2	v20.8h, v19.8h, v19.8h
	shl	v5.8h, v6.8h, 12
	add	v26.8h, v26.8h, v24.8h
	and	v31.16b, v29.16b, v31.16b
	add	v25.8h, v25.8h, v28.8h
	shl	v29.8h, v21.8h, 12
	uzp2	v28.8h, v23.8h, v23.8h
	uzp1	v7.8h, v7.8h, v7.8h
	uzp1	v18.8h, v18.8h, v18.8h
	uzp1	v24.8h, v19.8h, v19.8h
	add	v30.8h, v31.8h, v30.8h
	orr	v8.16b, v7.16b, v5.16b
	orr	v10.16b, v18.16b, v29.16b
	uzp2	v31.8h, v27.8h, v27.8h
	shl	v7.8h, v20.8h, 12
	ushr	v9.8h, v6.8h, 4
	uzp1	v29.8h, v27.8h, v27.8h
	uzp2	v6.8h, v26.8h, v26.8h
	shl	v27.8h, v28.8h, 12
	uzp1	v23.8h, v23.8h, v23.8h
	ushr	v11.8h, v21.8h, 4
	orr	v12.16b, v24.16b, v7.16b
	shl	v21.8h, v31.8h, 12
	uzp2	v7.8h, v25.8h, v25.8h
	orr	v14.16b, v23.16b, v27.16b
	ushr	v13.8h, v20.8h, 4
	tbl	v23.16b, {v8.16b - v9.16b}, v22.16b
	tbl	v24.16b, {v10.16b - v11.16b}, v22.16b
	shl	v9.8h, v6.8h, 12
	uzp1	v26.8h, v26.8h, v26.8h
	uzp2	v11.8h, v30.8h, v30.8h
	ushr	v15.8h, v28.8h, 4
	str	d23, [x0, 132]
	orr	v16.16b, v29.16b, v21.16b
	st1	{v23.s}[2], [x9]
	orr	v4.16b, v26.16b, v9.16b
	str	d24, [x0, 204]
	tbl	v26.16b, {v12.16b - v13.16b}, v22.16b
	st1	{v24.s}[2], [x8]
	shl	v10.8h, v7.8h, 12
	ushr	v17.8h, v31.8h, 4
	uzp1	v25.8h, v25.8h, v25.8h
	tbl	v27.16b, {v14.16b - v15.16b}, v22.16b
	str	d26, [x2, -236]
	shl	v29.8h, v11.8h, 12
	st1	{v26.s}[2], [x7]
	uzp1	v30.8h, v30.8h, v30.8h
	ushr	v5.8h, v6.8h, 4
	orr	v18.16b, v25.16b, v10.16b
	str	d27, [x2, -164]
	tbl	v28.16b, {v16.16b - v17.16b}, v22.16b
	st1	{v27.s}[2], [x6]
	ushr	v19.8h, v7.8h, 4
	orr	v20.16b, v30.16b, v29.16b
	ushr	v21.8h, v11.8h, 4
	tbl	v29.16b, {v4.16b - v5.16b}, v22.16b
	str	d28, [x2, -92]
	tbl	v30.16b, {v18.16b - v19.16b}, v22.16b
	st1	{v28.s}[2], [x5]
	tbl	v31.16b, {v20.16b - v21.16b}, v22.16b
	str	d29, [x2, -20]
	st1	{v29.s}[2], [x4]
	str	d30, [x2, 52]
	st1	{v30.s}[2], [x3]
	str	d31, [x2, 124]
	st1	{v31.s}[2], [x1]
	ldp	d10, d11, [sp, 16]
	ldp	d12, d13, [sp, 32]
	ldp	d14, d15, [sp, 48]
	ldp	d8, d9, [sp], 64
	.cfi_restore 73
	.cfi_restore 72
	.cfi_restore 78
	.cfi_restore 79
	.cfi_restore 76
	.cfi_restore 77
	.cfi_restore 74
	.cfi_restore 75
	.cfi_def_cfa_offset 0
	ret
	.cfi_endproc
.LFE3918:
	.size	p9_input_once_top_full, .-p9_input_once_top_full
	.section	.text.gt864_p9_input_once_full_inner,"ax",@progbits
	.align	2
	.p2align 5,,15
	.global	gt864_p9_input_once_full_inner
	.type	gt864_p9_input_once_full_inner, %function
gt864_p9_input_once_full_inner:
.LFB3919:
	.cfi_startproc
	stp	x29, x30, [sp, -16]!
	.cfi_def_cfa_offset 16
	.cfi_offset 29, -16
	.cfi_offset 30, -8
	mov	x12, x1
	mov	x29, sp
	bl	p9_input_once_top_full
	ldp	x29, x30, [sp], 16
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa_offset 0
	add	x1, x12, 864
	add	x0, x0, 648
	b	p9_input_once_top_full
	.cfi_endproc
.LFE3919:
	.size	gt864_p9_input_once_full_inner, .-gt864_p9_input_once_full_inner
	.section	.rodata.cst16,"aM",@progbits,16
	.align	4
.LC1:
	.hword	3457
	.hword	3457
	.hword	3457
	.hword	3457
	.hword	3457
	.hword	3457
	.hword	3457
	.hword	3457
	.align	4
.LC2:
	.byte	0
	.byte	1
	.byte	16
	.byte	2
	.byte	3
	.byte	18
	.byte	4
	.byte	5
	.byte	20
	.byte	6
	.byte	7
	.byte	22
	.byte	-1
	.byte	-1
	.byte	-1
	.byte	-1
	.ident	"GCC: (Debian 14.2.0-19) 14.2.0"
	.section	.note.GNU-stack,"",@progbits
