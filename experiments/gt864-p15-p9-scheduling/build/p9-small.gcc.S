	.arch armv8-a
	.file	"gt864_p9_tobytes_small.c"
	.text
	.section	.text.p9_input_once_top_small,"ax",@progbits
	.align	2
	.p2align 5,,15
	.type	p9_input_once_top_small, %function
p9_input_once_top_small:
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
// 25 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	movi	v31.4s, 0
	mov	v25.16b, v31.16b
	mov	v21.16b, v31.16b
	mov	v26.16b, v31.16b
	mov	v27.16b, v31.16b
	mov	v22.16b, v31.16b
	mov	v28.16b, v31.16b
	mov	v29.16b, v31.16b
	mov	v30.16b, v31.16b
	ins	v25.h[4], v24.h[3]
	ins	v21.h[4], v24.h[6]
	ins	v26.h[4], v24.h[0]
	ins	v27.h[4], v24.h[4]
	ins	v22.h[4], v24.h[7]
	ins	v28.h[4], v24.h[1]
	ins	v29.h[4], v24.h[5]
	ins	v30.h[4], v24.h[2]
	add	x2, x1, 160
#APP
// 43 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	ins	v25.h[5], v24.h[3]
	ins	v21.h[5], v24.h[6]
	ins	v26.h[5], v24.h[0]
	ins	v27.h[5], v24.h[4]
	ins	v22.h[5], v24.h[7]
	ins	v28.h[5], v24.h[1]
	ins	v29.h[5], v24.h[5]
	ins	v30.h[5], v24.h[2]
	add	x2, x1, 176
#APP
// 53 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	ins	v25.h[6], v24.h[3]
	ins	v21.h[6], v24.h[6]
	ins	v26.h[6], v24.h[0]
	ins	v27.h[6], v24.h[4]
	ins	v22.h[6], v24.h[7]
	ins	v28.h[6], v24.h[1]
	ins	v29.h[6], v24.h[5]
	ins	v30.h[6], v24.h[2]
	add	x2, x1, 576
#APP
// 63 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	ins	v25.h[7], v24.h[3]
	ins	v21.h[7], v24.h[6]
	ins	v26.h[7], v24.h[0]
	ins	v27.h[7], v24.h[4]
	ins	v22.h[7], v24.h[7]
	ins	v28.h[7], v24.h[1]
	ins	v29.h[7], v24.h[5]
	ins	v30.h[7], v24.h[2]
	add	x2, x1, 272
#APP
// 73 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	mov	v19.16b, v31.16b
	mov	v20.16b, v31.16b
	ins	v25.h[0], v24.h[5]
	ins	v26.h[0], v24.h[2]
	ins	v27.h[0], v24.h[6]
	ins	v28.h[0], v24.h[3]
	ins	v29.h[0], v24.h[7]
	ins	v30.h[0], v24.h[4]
	ins	v19.h[0], v24.h[0]
	ins	v20.h[0], v24.h[1]
	add	x2, x1, 672
#APP
// 85 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	ins	v25.h[1], v24.h[5]
	ins	v26.h[1], v24.h[2]
	ins	v27.h[1], v24.h[6]
	ins	v19.h[1], v24.h[0]
	ins	v28.h[1], v24.h[3]
	ins	v29.h[1], v24.h[7]
	ins	v20.h[1], v24.h[1]
	ins	v30.h[1], v24.h[4]
	add	x2, x1, 688
#APP
// 95 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	ins	v25.h[2], v24.h[5]
	ins	v26.h[2], v24.h[2]
	ins	v27.h[2], v24.h[6]
	ins	v19.h[2], v24.h[0]
	ins	v28.h[2], v24.h[3]
	ins	v29.h[2], v24.h[7]
	ins	v20.h[2], v24.h[1]
	ins	v30.h[2], v24.h[4]
	add	x2, x1, 704
#APP
// 105 "gt864_p9_tobytes_small.c" 1
	ldr q24, [x2]
// 0 "" 2
#NO_APP
	ins	v25.h[3], v24.h[5]
	adrp	x2, .LC1
	ins	v26.h[3], v24.h[2]
	adrp	x9, .LC2
	ldr	q23, [x2, #:lo12:.LC1]
	add	x8, x0, 56
	ins	v27.h[3], v24.h[6]
	add	x7, x0, 164
	cmlt	v5.8h, v25.8h, #0
	add	x6, x0, 272
	cmlt	v6.8h, v26.8h, #0
	add	x2, x0, 512
	ins	v29.h[3], v24.h[7]
	add	x5, x0, 380
	cmlt	v18.8h, v27.8h, #0
	add	x4, x0, 488
	and	v5.16b, v5.16b, v23.16b
	add	x3, x0, 596
	and	v6.16b, v6.16b, v23.16b
	ins	v30.h[3], v24.h[4]
	ins	v28.h[3], v24.h[3]
	add	v5.8h, v5.8h, v25.8h
	add	v6.8h, v6.8h, v26.8h
	and	v25.16b, v18.16b, v23.16b
	cmlt	v26.8h, v29.8h, #0
	uzp2	v7.8h, v5.8h, v5.8h
	cmlt	v4.8h, v28.8h, #0
	add	v25.8h, v25.8h, v27.8h
	cmlt	v18.8h, v30.8h, #0
	and	v27.16b, v26.16b, v23.16b
	and	v4.16b, v4.16b, v23.16b
	uzp1	v26.8h, v5.8h, v5.8h
	shl	v3.8h, v7.8h, 12
	add	v29.8h, v27.8h, v29.8h
	and	v18.16b, v18.16b, v23.16b
	uzp2	v27.8h, v6.8h, v6.8h
	orr	v8.16b, v26.16b, v3.16b
	add	v28.8h, v4.8h, v28.8h
	add	v18.8h, v18.8h, v30.8h
	shl	v26.8h, v27.8h, 12
	uzp2	v30.8h, v25.8h, v25.8h
	uzp1	v6.8h, v6.8h, v6.8h
	uzp2	v3.8h, v28.8h, v28.8h
	uzp1	v25.8h, v25.8h, v25.8h
	ushr	v9.8h, v7.8h, 4
	orr	v10.16b, v6.16b, v26.16b
	shl	v26.8h, v30.8h, 12
	uzp2	v6.8h, v29.8h, v29.8h
	ins	v19.h[3], v24.h[0]
	ins	v20.h[3], v24.h[1]
	ldr	q24, [x9, #:lo12:.LC2]
	orr	v12.16b, v25.16b, v26.16b
	uzp2	v7.8h, v18.8h, v18.8h
	shl	v26.8h, v3.8h, 12
	ushr	v11.8h, v27.8h, 4
	uzp1	v28.8h, v28.8h, v28.8h
	shl	v27.8h, v6.8h, 12
	tbl	v25.16b, {v8.16b - v9.16b}, v24.16b
	ushr	v13.8h, v30.8h, 4
	uzp1	v29.8h, v29.8h, v29.8h
	orr	v14.16b, v28.16b, v26.16b
	uzp1	v18.8h, v18.8h, v18.8h
	str	d25, [x0, 48]
	tbl	v26.16b, {v10.16b - v11.16b}, v24.16b
	st1	{v25.s}[2], [x8]
	shl	v28.8h, v7.8h, 12
	ushr	v15.8h, v3.8h, 4
	orr	v16.16b, v29.16b, v27.16b
	ushr	v17.8h, v6.8h, 4
	str	d26, [x0, 156]
	tbl	v27.16b, {v12.16b - v13.16b}, v24.16b
	st1	{v26.s}[2], [x7]
	orr	v4.16b, v18.16b, v28.16b
	ushr	v5.8h, v7.8h, 4
	tbl	v28.16b, {v14.16b - v15.16b}, v24.16b
	tbl	v29.16b, {v16.16b - v17.16b}, v24.16b
	str	d27, [x0, 264]
	st1	{v27.s}[2], [x6]
	tbl	v30.16b, {v4.16b - v5.16b}, v24.16b
	str	d28, [x2, -140]
	st1	{v28.s}[2], [x5]
	str	d29, [x0, 480]
	st1	{v29.s}[2], [x4]
	str	d30, [x2, 76]
	st1	{v30.s}[2], [x3]
	add	x3, x1, 96
#APP
// 121 "gt864_p9_tobytes_small.c" 1
	ldr q18, [x3]
// 0 "" 2
#NO_APP
	mov	v27.16b, v31.16b
	mov	v28.16b, v31.16b
	mov	v29.16b, v31.16b
	mov	v25.16b, v31.16b
	mov	v30.16b, v31.16b
	mov	v26.16b, v31.16b
	ins	v19.h[4], v18.h[6]
	ins	v20.h[4], v18.h[7]
	ins	v27.h[4], v18.h[2]
	ins	v28.h[4], v18.h[5]
	ins	v29.h[4], v18.h[3]
	ins	v25.h[0], v18.h[0]
	ins	v30.h[4], v18.h[4]
	ins	v26.h[0], v18.h[1]
	add	x3, x1, 112
#APP
// 137 "gt864_p9_tobytes_small.c" 1
	ldr q18, [x3]
// 0 "" 2
#NO_APP
	ins	v27.h[5], v18.h[2]
	ins	v28.h[5], v18.h[5]
	ins	v29.h[5], v18.h[3]
	ins	v19.h[5], v18.h[6]
	ins	v25.h[1], v18.h[0]
	ins	v30.h[5], v18.h[4]
	ins	v20.h[5], v18.h[7]
	ins	v26.h[1], v18.h[1]
	add	x3, x1, 128
#APP
// 147 "gt864_p9_tobytes_small.c" 1
	ldr q18, [x3]
// 0 "" 2
#NO_APP
	ins	v27.h[6], v18.h[2]
	ins	v28.h[6], v18.h[5]
	ins	v29.h[6], v18.h[3]
	ins	v19.h[6], v18.h[6]
	ins	v25.h[2], v18.h[0]
	ins	v30.h[6], v18.h[4]
	ins	v20.h[6], v18.h[7]
	ins	v26.h[2], v18.h[1]
	add	x3, x1, 528
#APP
// 157 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[7], v16.h[6]
	add	x4, x0, 308
	ins	v20.h[7], v16.h[7]
	add	x3, x0, 524
	ins	v27.h[7], v16.h[2]
	ins	v28.h[7], v16.h[5]
	cmlt	v17.8h, v19.8h, #0
	cmlt	v18.8h, v20.8h, #0
	ins	v29.h[7], v16.h[3]
	ins	v25.h[3], v16.h[0]
	and	v17.16b, v17.16b, v23.16b
	and	v18.16b, v18.16b, v23.16b
	ins	v30.h[7], v16.h[4]
	ins	v26.h[3], v16.h[1]
	add	v19.8h, v17.8h, v19.8h
	add	v20.8h, v18.8h, v20.8h
	uzp2	v17.8h, v19.8h, v19.8h
	uzp2	v18.8h, v20.8h, v20.8h
	uzp1	v19.8h, v19.8h, v19.8h
	uzp1	v20.8h, v20.8h, v20.8h
	shl	v11.8h, v17.8h, 12
	shl	v16.8h, v18.8h, 12
	ushr	v13.8h, v17.8h, 4
	ushr	v15.8h, v18.8h, 4
	orr	v12.16b, v19.16b, v11.16b
	orr	v14.16b, v20.16b, v16.16b
	tbl	v19.16b, {v12.16b - v13.16b}, v24.16b
	tbl	v20.16b, {v14.16b - v15.16b}, v24.16b
	str	d19, [x2, -212]
	st1	{v19.s}[2], [x4]
	str	d20, [x2, 4]
	st1	{v20.s}[2], [x3]
	add	x3, x1, 224
#APP
// 169 "gt864_p9_tobytes_small.c" 1
	ldr q20, [x3]
// 0 "" 2
#NO_APP
	mov	v18.16b, v31.16b
	mov	v7.16b, v31.16b
	mov	v16.16b, v31.16b
	mov	v17.16b, v31.16b
	ins	v27.h[0], v20.h[4]
	ins	v28.h[0], v20.h[7]
	ins	v29.h[0], v20.h[5]
	ins	v30.h[0], v20.h[6]
	ins	v18.h[6], v20.h[1]
	ins	v7.h[6], v20.h[2]
	ins	v16.h[6], v20.h[0]
	ins	v17.h[6], v20.h[3]
	add	x3, x1, 624
#APP
// 183 "gt864_p9_tobytes_small.c" 1
	ldr q20, [x3]
// 0 "" 2
#NO_APP
	ins	v27.h[1], v20.h[4]
	ins	v28.h[1], v20.h[7]
	ins	v18.h[7], v20.h[1]
	ins	v29.h[1], v20.h[5]
	ins	v7.h[7], v20.h[2]
	ins	v30.h[1], v20.h[6]
	ins	v16.h[7], v20.h[0]
	ins	v17.h[7], v20.h[3]
	add	x3, x1, 320
#APP
// 193 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v21.h[0], v15.h[0]
	ins	v22.h[0], v15.h[1]
	mov	v19.16b, v31.16b
	ins	v18.h[0], v15.h[3]
	mov	v20.16b, v21.16b
	mov	v21.16b, v22.16b
	mov	v22.16b, v31.16b
	ins	v7.h[0], v15.h[4]
	ins	v16.h[0], v15.h[2]
	ins	v17.h[0], v15.h[5]
	ins	v19.h[4], v15.h[6]
	ins	v22.h[4], v15.h[7]
	add	x3, x1, 720
#APP
// 205 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[5], v15.h[6]
	ins	v20.h[1], v15.h[0]
	ins	v18.h[1], v15.h[3]
	ins	v22.h[5], v15.h[7]
	ins	v21.h[1], v15.h[1]
	ins	v7.h[1], v15.h[4]
	ins	v16.h[1], v15.h[2]
	ins	v17.h[1], v15.h[5]
	add	x3, x1, 736
#APP
// 215 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[6], v15.h[6]
	ins	v20.h[2], v15.h[0]
	ins	v18.h[2], v15.h[3]
	ins	v22.h[6], v15.h[7]
	ins	v21.h[2], v15.h[1]
	ins	v7.h[2], v15.h[4]
	ins	v16.h[2], v15.h[2]
	ins	v17.h[2], v15.h[5]
	add	x3, x1, 752
#APP
// 225 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v20.h[3], v15.h[0]
	add	x4, x0, 128
	ins	v21.h[3], v15.h[1]
	add	x3, x0, 344
	ins	v19.h[7], v15.h[6]
	ins	v18.h[3], v15.h[3]
	cmlt	v5.8h, v20.8h, #0
	cmlt	v6.8h, v21.8h, #0
	ins	v22.h[7], v15.h[7]
	ins	v7.h[3], v15.h[4]
	and	v5.16b, v5.16b, v23.16b
	and	v6.16b, v6.16b, v23.16b
	ins	v16.h[3], v15.h[2]
	ins	v17.h[3], v15.h[5]
	add	v20.8h, v5.8h, v20.8h
	add	v21.8h, v6.8h, v21.8h
	uzp2	v14.8h, v20.8h, v20.8h
	uzp2	v15.8h, v21.8h, v21.8h
	uzp1	v20.8h, v20.8h, v20.8h
	uzp1	v21.8h, v21.8h, v21.8h
	shl	v12.8h, v14.8h, 12
	shl	v13.8h, v15.8h, 12
	ushr	v3.8h, v14.8h, 4
	ushr	v1.8h, v15.8h, 4
	orr	v2.16b, v20.16b, v12.16b
	orr	v0.16b, v21.16b, v13.16b
	tbl	v2.16b, {v2.16b - v3.16b}, v24.16b
	tbl	v0.16b, {v0.16b - v1.16b}, v24.16b
	str	d2, [x0, 120]
	st1	{v2.s}[2], [x4]
	str	d0, [x0, 336]
	st1	{v0.s}[2], [x3]
	add	x3, x1, 192
#APP
// 237 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v16.h[4], v15.h[0]
	mov	v12.16b, v7.16b
	mov	v21.16b, v31.16b
	mov	v7.16b, v31.16b
	mov	v13.16b, v16.16b
	mov	v20.16b, v31.16b
	mov	v16.16b, v31.16b
	ins	v18.h[4], v15.h[1]
	ins	v12.h[4], v15.h[2]
	ins	v17.h[4], v15.h[3]
	ins	v7.h[6], v15.h[4]
	ins	v16.h[6], v15.h[7]
	ins	v21.h[6], v15.h[5]
	ins	v20.h[6], v15.h[6]
	add	x3, x1, 208
#APP
// 251 "gt864_p9_tobytes_small.c" 1
	ldr q14, [x3]
// 0 "" 2
#NO_APP
	ins	v18.h[5], v14.h[1]
	add	x6, x0, 200
	ins	v12.h[5], v14.h[2]
	add	x5, x0, 416
	ins	v13.h[5], v14.h[0]
	add	x4, x0, 560
	ins	v17.h[5], v14.h[3]
	add	x3, x0, 632
	cmlt	v5.8h, v18.8h, #0
	cmlt	v6.8h, v12.8h, #0
	cmlt	v15.8h, v13.8h, #0
	cmlt	v9.8h, v17.8h, #0
	and	v5.16b, v5.16b, v23.16b
	and	v6.16b, v6.16b, v23.16b
	and	v15.16b, v15.16b, v23.16b
	and	v9.16b, v9.16b, v23.16b
	add	v18.8h, v5.8h, v18.8h
	add	v6.8h, v6.8h, v12.8h
	add	v15.8h, v15.8h, v13.8h
	add	v17.8h, v9.8h, v17.8h
	uzp2	v12.8h, v18.8h, v18.8h
	uzp2	v13.8h, v6.8h, v6.8h
	uzp1	v18.8h, v18.8h, v18.8h
	uzp2	v5.8h, v15.8h, v15.8h
	shl	v9.8h, v12.8h, 12
	uzp1	v6.8h, v6.8h, v6.8h
	uzp2	v4.8h, v17.8h, v17.8h
	uzp1	v15.8h, v15.8h, v15.8h
	orr	v10.16b, v18.16b, v9.16b
	shl	v18.8h, v13.8h, 12
	ushr	v11.8h, v12.8h, 4
	ushr	v3.8h, v13.8h, 4
	uzp1	v17.8h, v17.8h, v17.8h
	orr	v2.16b, v6.16b, v18.16b
	shl	v18.8h, v5.8h, 12
	tbl	v11.16b, {v10.16b - v11.16b}, v24.16b
	ushr	v9.8h, v5.8h, 4
	ushr	v13.8h, v4.8h, 4
	orr	v8.16b, v15.16b, v18.16b
	shl	v18.8h, v4.8h, 12
	str	d11, [x0, 192]
	tbl	v15.16b, {v2.16b - v3.16b}, v24.16b
	st1	{v11.s}[2], [x6]
	ins	v7.h[7], v14.h[4]
	ins	v16.h[7], v14.h[7]
	orr	v12.16b, v17.16b, v18.16b
	tbl	v18.16b, {v8.16b - v9.16b}, v24.16b
	str	d15, [x0, 408]
	ins	v21.h[7], v14.h[5]
	st1	{v15.s}[2], [x5]
	ins	v20.h[7], v14.h[6]
	tbl	v12.16b, {v12.16b - v13.16b}, v24.16b
	str	d18, [x0, 552]
	st1	{v18.s}[2], [x4]
	str	d12, [x0, 624]
	st1	{v12.s}[2], [x3]
#APP
// 265 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x1]
// 0 "" 2
#NO_APP
	mov	v17.16b, v31.16b
	mov	v5.16b, v31.16b
	mov	v6.16b, v31.16b
	mov	v18.16b, v31.16b
	ins	v7.h[0], v15.h[0]
	ins	v16.h[0], v15.h[3]
	ins	v21.h[0], v15.h[1]
	ins	v20.h[0], v15.h[2]
	ins	v17.h[0], v15.h[6]
	ins	v5.h[0], v15.h[4]
	ins	v6.h[0], v15.h[7]
	ins	v18.h[0], v15.h[5]
	add	x3, x1, 16
#APP
// 279 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v7.h[1], v15.h[0]
	ins	v16.h[1], v15.h[3]
	ins	v17.h[1], v15.h[6]
	ins	v21.h[1], v15.h[1]
	ins	v5.h[1], v15.h[4]
	ins	v6.h[1], v15.h[7]
	ins	v20.h[1], v15.h[2]
	ins	v18.h[1], v15.h[5]
	add	x3, x1, 32
#APP
// 289 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v7.h[2], v15.h[0]
	ins	v16.h[2], v15.h[3]
	ins	v17.h[2], v15.h[6]
	ins	v21.h[2], v15.h[1]
	ins	v5.h[2], v15.h[4]
	ins	v6.h[2], v15.h[7]
	ins	v20.h[2], v15.h[2]
	ins	v18.h[2], v15.h[5]
	add	x3, x1, 432
#APP
// 299 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v7.h[3], v15.h[0]
	ins	v16.h[3], v15.h[3]
	ins	v17.h[3], v15.h[6]
	ins	v21.h[3], v15.h[1]
	ins	v5.h[3], v15.h[4]
	ins	v6.h[3], v15.h[7]
	ins	v20.h[3], v15.h[2]
	ins	v18.h[3], v15.h[5]
	add	x3, x1, 448
#APP
// 309 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v7.h[4], v15.h[0]
	ins	v16.h[4], v15.h[3]
	ins	v17.h[4], v15.h[6]
	ins	v21.h[4], v15.h[1]
	ins	v5.h[4], v15.h[4]
	ins	v6.h[4], v15.h[7]
	ins	v20.h[4], v15.h[2]
	ins	v18.h[4], v15.h[5]
	add	x3, x1, 464
#APP
// 319 "gt864_p9_tobytes_small.c" 1
	ldr q3, [x3]
// 0 "" 2
#NO_APP
	ins	v7.h[5], v3.h[0]
	mov	x3, x0
	ins	v16.h[5], v3.h[3]
	add	x6, x0, 80
	ins	v21.h[5], v3.h[1]
	add	x5, x0, 224
	ins	v20.h[5], v3.h[2]
	add	x4, x0, 440
	cmlt	v4.8h, v7.8h, #0
	cmlt	v14.8h, v16.8h, #0
	cmlt	v15.8h, v21.8h, #0
	cmlt	v13.8h, v20.8h, #0
	and	v4.16b, v4.16b, v23.16b
	and	v14.16b, v14.16b, v23.16b
	and	v15.16b, v15.16b, v23.16b
	ins	v17.h[5], v3.h[6]
	add	v7.8h, v4.8h, v7.8h
	add	v16.8h, v14.8h, v16.8h
	and	v14.16b, v13.16b, v23.16b
	add	v21.8h, v15.8h, v21.8h
	uzp2	v13.8h, v7.8h, v7.8h
	uzp2	v2.8h, v16.8h, v16.8h
	uzp1	v7.8h, v7.8h, v7.8h
	uzp2	v4.8h, v21.8h, v21.8h
	shl	v12.8h, v13.8h, 12
	add	v20.8h, v14.8h, v20.8h
	uzp1	v16.8h, v16.8h, v16.8h
	uzp1	v21.8h, v21.8h, v21.8h
	orr	v0.16b, v7.16b, v12.16b
	shl	v7.8h, v2.8h, 12
	uzp2	v12.8h, v20.8h, v20.8h
	ushr	v1.8h, v13.8h, 4
	uzp1	v20.8h, v20.8h, v20.8h
	orr	v10.16b, v16.16b, v7.16b
	shl	v16.8h, v4.8h, 12
	ushr	v11.8h, v2.8h, 4
	ushr	v15.8h, v4.8h, 4
	tbl	v0.16b, {v0.16b - v1.16b}, v24.16b
	orr	v14.16b, v21.16b, v16.16b
	shl	v21.8h, v12.8h, 12
	tbl	v10.16b, {v10.16b - v11.16b}, v24.16b
	ushr	v9.8h, v12.8h, 4
	str	d0, [x3], 8
	tbl	v14.16b, {v14.16b - v15.16b}, v24.16b
	st1	{v0.s}[2], [x3]
	orr	v8.16b, v20.16b, v21.16b
	ins	v5.h[5], v3.h[4]
	str	d10, [x0, 72]
	ins	v6.h[5], v3.h[7]
	st1	{v10.s}[2], [x6]
	ins	v18.h[5], v3.h[5]
	str	d14, [x0, 216]
	tbl	v8.16b, {v8.16b - v9.16b}, v24.16b
	st1	{v14.s}[2], [x5]
	str	d8, [x0, 432]
	st1	{v8.s}[2], [x4]
	add	x3, x1, 240
#APP
// 333 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	mov	v7.16b, v31.16b
	mov	v12.16b, v31.16b
	mov	v20.16b, v31.16b
	mov	v21.16b, v31.16b
	ins	v17.h[6], v16.h[2]
	ins	v5.h[6], v16.h[0]
	ins	v6.h[6], v16.h[3]
	ins	v18.h[6], v16.h[1]
	ins	v7.h[6], v16.h[5]
	ins	v12.h[6], v16.h[6]
	ins	v20.h[6], v16.h[7]
	ins	v21.h[6], v16.h[4]
	add	x3, x1, 256
#APP
// 347 "gt864_p9_tobytes_small.c" 1
	ldr q11, [x3]
// 0 "" 2
#NO_APP
	mov	v16.16b, v5.16b
	add	x5, x0, 152
	ins	v17.h[7], v11.h[2]
	add	x4, x0, 296
	ins	v18.h[7], v11.h[1]
	add	x3, x0, 368
	ins	v6.h[7], v11.h[3]
	ins	v16.h[7], v11.h[0]
	cmlt	v15.8h, v17.8h, #0
	mov	v10.16b, v17.16b
	mov	v13.16b, v18.16b
	cmlt	v14.8h, v16.8h, #0
	and	v15.16b, v15.16b, v23.16b
	mov	v18.16b, v12.16b
	cmlt	v12.8h, v6.8h, #0
	and	v14.16b, v14.16b, v23.16b
	add	v15.8h, v15.8h, v10.8h
	mov	v17.16b, v7.16b
	and	v12.16b, v12.16b, v23.16b
	add	v14.8h, v14.8h, v16.8h
	cmlt	v16.8h, v13.8h, #0
	uzp2	v10.8h, v15.8h, v15.8h
	add	v6.8h, v12.8h, v6.8h
	uzp2	v7.8h, v14.8h, v14.8h
	and	v16.16b, v16.16b, v23.16b
	shl	v12.8h, v10.8h, 12
	uzp1	v15.8h, v15.8h, v15.8h
	uzp1	v14.8h, v14.8h, v14.8h
	add	v16.8h, v16.8h, v13.8h
	shl	v13.8h, v7.8h, 12
	orr	v8.16b, v15.16b, v12.16b
	uzp2	v15.8h, v6.8h, v6.8h
	uzp2	v12.8h, v16.8h, v16.8h
	ushr	v9.8h, v10.8h, 4
	orr	v4.16b, v14.16b, v13.16b
	uzp1	v6.8h, v6.8h, v6.8h
	shl	v14.8h, v15.8h, 12
	tbl	v13.16b, {v8.16b - v9.16b}, v24.16b
	uzp1	v16.8h, v16.8h, v16.8h
	ushr	v5.8h, v7.8h, 4
	shl	v9.8h, v12.8h, 12
	orr	v2.16b, v6.16b, v14.16b
	str	d13, [x0, 144]
	ushr	v3.8h, v15.8h, 4
	st1	{v13.s}[2], [x5]
	tbl	v14.16b, {v4.16b - v5.16b}, v24.16b
	ins	v17.h[7], v11.h[5]
	ins	v18.h[7], v11.h[6]
	ins	v20.h[7], v11.h[7]
	ins	v21.h[7], v11.h[4]
	str	d14, [x0, 288]
	orr	v10.16b, v16.16b, v9.16b
	st1	{v14.s}[2], [x4]
	ushr	v11.8h, v12.8h, 4
	tbl	v15.16b, {v2.16b - v3.16b}, v24.16b
	tbl	v16.16b, {v10.16b - v11.16b}, v24.16b
	str	d15, [x0, 360]
	st1	{v15.s}[2], [x3]
	str	d16, [x0, 504]
	st1	{v16.s}[2], [x2]
	add	x3, x1, 48
#APP
// 361 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	mov	v5.16b, v31.16b
	mov	v6.16b, v31.16b
	mov	v7.16b, v31.16b
	mov	v16.16b, v31.16b
	ins	v17.h[0], v15.h[1]
	ins	v18.h[0], v15.h[2]
	ins	v20.h[0], v15.h[3]
	ins	v21.h[0], v15.h[0]
	ins	v5.h[0], v15.h[4]
	ins	v6.h[0], v15.h[7]
	ins	v7.h[0], v15.h[5]
	ins	v16.h[0], v15.h[6]
	add	x3, x1, 64
#APP
// 375 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[1], v15.h[1]
	ins	v5.h[1], v15.h[4]
	ins	v6.h[1], v15.h[7]
	ins	v18.h[1], v15.h[2]
	ins	v7.h[1], v15.h[5]
	ins	v20.h[1], v15.h[3]
	ins	v16.h[1], v15.h[6]
	ins	v21.h[1], v15.h[0]
	add	x3, x1, 80
#APP
// 385 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[2], v15.h[1]
	ins	v5.h[2], v15.h[4]
	ins	v6.h[2], v15.h[7]
	ins	v18.h[2], v15.h[2]
	ins	v7.h[2], v15.h[5]
	ins	v20.h[2], v15.h[3]
	ins	v16.h[2], v15.h[6]
	ins	v21.h[2], v15.h[0]
	add	x3, x1, 288
#APP
// 395 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[2], v15.h[6]
	ins	v5.h[6], v15.h[0]
	ins	v6.h[6], v15.h[3]
	ins	v22.h[2], v15.h[7]
	ins	v7.h[6], v15.h[1]
	ins	v25.h[6], v15.h[4]
	ins	v16.h[6], v15.h[2]
	ins	v26.h[6], v15.h[5]
	add	x3, x1, 304
#APP
// 405 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[3], v15.h[6]
	ins	v5.h[7], v15.h[0]
	ins	v6.h[7], v15.h[3]
	ins	v22.h[3], v15.h[7]
	ins	v7.h[7], v15.h[1]
	ins	v25.h[7], v15.h[4]
	ins	v16.h[7], v15.h[2]
	ins	v26.h[7], v15.h[5]
	add	x3, x1, 480
#APP
// 415 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[3], v15.h[1]
	ins	v5.h[3], v15.h[4]
	ins	v6.h[3], v15.h[7]
	ins	v18.h[3], v15.h[2]
	ins	v7.h[3], v15.h[5]
	ins	v20.h[3], v15.h[3]
	ins	v16.h[3], v15.h[6]
	ins	v21.h[3], v15.h[0]
	add	x3, x1, 496
#APP
// 425 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[4], v15.h[1]
	ins	v5.h[4], v15.h[4]
	ins	v6.h[4], v15.h[7]
	ins	v18.h[4], v15.h[2]
	ins	v7.h[4], v15.h[5]
	ins	v20.h[4], v15.h[3]
	ins	v16.h[4], v15.h[6]
	ins	v21.h[4], v15.h[0]
	add	x3, x1, 512
#APP
// 435 "gt864_p9_tobytes_small.c" 1
	ldr q11, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[5], v11.h[1]
	add	x10, x0, 44
	ins	v5.h[5], v11.h[4]
	add	x9, x0, 116
	ins	v6.h[5], v11.h[7]
	add	x8, x0, 188
	ins	v18.h[5], v11.h[2]
	add	x7, x0, 260
	cmlt	v9.8h, v17.8h, #0
	add	x6, x0, 332
	cmlt	v10.8h, v5.8h, #0
	add	x5, x0, 476
	cmlt	v14.8h, v6.8h, #0
	add	x4, x0, 548
	ins	v20.h[5], v11.h[3]
	add	x3, x0, 584
	and	v9.16b, v9.16b, v23.16b
	ins	v7.h[5], v11.h[5]
	and	v14.16b, v14.16b, v23.16b
	and	v10.16b, v10.16b, v23.16b
	cmlt	v15.8h, v18.8h, #0
	add	v17.8h, v9.8h, v17.8h
	add	v8.8h, v14.8h, v6.8h
	ins	v16.h[5], v11.h[6]
	ins	v21.h[5], v11.h[0]
	uzp2	v9.8h, v17.8h, v17.8h
	and	v15.16b, v15.16b, v23.16b
	add	v10.8h, v10.8h, v5.8h
	cmlt	v11.8h, v7.8h, #0
	cmlt	v14.8h, v20.8h, #0
	add	v6.8h, v15.8h, v18.8h
	uzp2	v5.8h, v10.8h, v10.8h
	shl	v4.8h, v9.8h, 12
	and	v14.16b, v14.16b, v23.16b
	cmlt	v18.8h, v21.8h, #0
	and	v11.16b, v11.16b, v23.16b
	cmlt	v15.8h, v16.8h, #0
	uzp1	v17.8h, v17.8h, v17.8h
	uzp1	v10.8h, v10.8h, v10.8h
	add	v11.8h, v11.8h, v7.8h
	and	v15.16b, v15.16b, v23.16b
	add	v7.8h, v14.8h, v20.8h
	orr	v12.16b, v17.16b, v4.16b
	and	v20.16b, v18.16b, v23.16b
	uzp2	v17.8h, v8.8h, v8.8h
	shl	v4.8h, v5.8h, 12
	uzp1	v14.8h, v8.8h, v8.8h
	add	v20.8h, v20.8h, v21.8h
	add	v8.8h, v15.8h, v16.8h
	uzp2	v21.8h, v11.8h, v11.8h
	orr	v15.16b, v10.16b, v4.16b
	shl	v10.8h, v17.8h, 12
	uzp2	v18.8h, v6.8h, v6.8h
	ushr	v13.8h, v9.8h, 4
	ushr	v16.8h, v5.8h, 4
	orr	v0.16b, v14.16b, v10.16b
	ushr	v1.8h, v17.8h, 4
	uzp2	v10.8h, v7.8h, v7.8h
	shl	v17.8h, v21.8h, 12
	uzp1	v11.8h, v11.8h, v11.8h
	tbl	v12.16b, {v12.16b - v13.16b}, v24.16b
	tbl	v15.16b, {v15.16b - v16.16b}, v24.16b
	shl	v14.8h, v18.8h, 12
	uzp1	v6.8h, v6.8h, v6.8h
	orr	v4.16b, v11.16b, v17.16b
	uzp1	v9.8h, v7.8h, v7.8h
	str	d12, [x0, 36]
	uzp2	v17.8h, v8.8h, v8.8h
	st1	{v12.s}[2], [x10]
	shl	v16.8h, v10.8h, 12
	str	d15, [x0, 108]
	orr	v2.16b, v6.16b, v14.16b
	st1	{v15.s}[2], [x9]
	tbl	v14.16b, {v0.16b - v1.16b}, v24.16b
	ushr	v3.8h, v18.8h, 4
	uzp2	v18.8h, v20.8h, v20.8h
	orr	v6.16b, v9.16b, v16.16b
	ushr	v5.8h, v21.8h, 4
	str	d14, [x0, 180]
	shl	v9.8h, v17.8h, 12
	st1	{v14.s}[2], [x8]
	uzp1	v8.8h, v8.8h, v8.8h
	tbl	v15.16b, {v2.16b - v3.16b}, v24.16b
	shl	v14.8h, v18.8h, 12
	uzp1	v11.8h, v20.8h, v20.8h
	ushr	v7.8h, v10.8h, 4
	ushr	v13.8h, v17.8h, 4
	str	d15, [x0, 252]
	tbl	v16.16b, {v4.16b - v5.16b}, v24.16b
	st1	{v15.s}[2], [x7]
	orr	v12.16b, v8.16b, v9.16b
	ushr	v21.8h, v18.8h, 4
	tbl	v17.16b, {v6.16b - v7.16b}, v24.16b
	orr	v20.16b, v11.16b, v14.16b
	str	d16, [x2, -188]
	tbl	v18.16b, {v12.16b - v13.16b}, v24.16b
	st1	{v16.s}[2], [x6]
	str	d17, [x2, -44]
	tbl	v20.16b, {v20.16b - v21.16b}, v24.16b
	st1	{v17.s}[2], [x5]
	str	d18, [x2, 28]
	st1	{v18.s}[2], [x4]
	str	d20, [x0, 576]
	st1	{v20.s}[2], [x3]
	add	x3, x1, 544
#APP
// 453 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v22.h[0], v16.h[3]
	ins	v25.h[4], v16.h[0]
	ins	v26.h[4], v16.h[1]
	mov	v21.16b, v31.16b
	mov	v17.16b, v22.16b
	mov	v18.16b, v25.16b
	mov	v20.16b, v26.16b
	mov	v25.16b, v31.16b
	mov	v22.16b, v31.16b
	mov	v26.16b, v31.16b
	ins	v19.h[0], v16.h[2]
	ins	v21.h[0], v16.h[5]
	ins	v25.h[0], v16.h[6]
	ins	v22.h[0], v16.h[4]
	ins	v26.h[0], v16.h[7]
	add	x3, x1, 560
#APP
// 467 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[1], v15.h[2]
	add	x6, x0, 32
	ins	v17.h[1], v15.h[3]
	add	x5, x0, 248
	ins	v18.h[5], v15.h[0]
	add	x4, x0, 404
	ins	v20.h[5], v15.h[1]
	add	x3, x0, 620
	ins	v21.h[1], v15.h[5]
	mov	v14.16b, v17.16b
	cmlt	v17.8h, v19.8h, #0
	mov	v13.16b, v18.16b
	cmlt	v12.8h, v20.8h, #0
	cmlt	v18.8h, v14.8h, #0
	and	v17.16b, v17.16b, v23.16b
	cmlt	v16.8h, v13.8h, #0
	ins	v25.h[1], v15.h[6]
	and	v18.16b, v18.16b, v23.16b
	add	v19.8h, v17.8h, v19.8h
	and	v16.16b, v16.16b, v23.16b
	ins	v22.h[1], v15.h[4]
	add	v18.8h, v18.8h, v14.8h
	uzp2	v11.8h, v19.8h, v19.8h
	and	v14.16b, v12.16b, v23.16b
	add	v17.8h, v16.8h, v13.8h
	uzp1	v19.8h, v19.8h, v19.8h
	uzp2	v16.8h, v18.8h, v18.8h
	add	v20.8h, v14.8h, v20.8h
	shl	v13.8h, v11.8h, 12
	uzp2	v14.8h, v17.8h, v17.8h
	uzp1	v18.8h, v18.8h, v18.8h
	shl	v10.8h, v16.8h, 12
	orr	v4.16b, v19.16b, v13.16b
	uzp2	v19.8h, v20.8h, v20.8h
	ushr	v5.8h, v11.8h, 4
	uzp1	v17.8h, v17.8h, v17.8h
	shl	v11.8h, v14.8h, 12
	orr	v2.16b, v18.16b, v10.16b
	uzp1	v20.8h, v20.8h, v20.8h
	shl	v18.8h, v19.8h, 12
	ushr	v3.8h, v16.8h, 4
	tbl	v4.16b, {v4.16b - v5.16b}, v24.16b
	orr	v6.16b, v17.16b, v11.16b
	ushr	v7.8h, v14.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v24.16b
	orr	v12.16b, v20.16b, v18.16b
	str	d4, [x0, 24]
	ushr	v13.8h, v19.8h, 4
	st1	{v4.s}[2], [x6]
	tbl	v6.16b, {v6.16b - v7.16b}, v24.16b
	ins	v26.h[1], v15.h[7]
	str	d2, [x0, 240]
	st1	{v2.s}[2], [x5]
	tbl	v20.16b, {v12.16b - v13.16b}, v24.16b
	str	d6, [x2, -116]
	st1	{v6.s}[2], [x4]
	str	d20, [x2, 100]
	st1	{v20.s}[2], [x3]
	add	x3, x1, 336
#APP
// 481 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	mov	v17.16b, v31.16b
	mov	v18.16b, v31.16b
	mov	v19.16b, v31.16b
	mov	v20.16b, v31.16b
	ins	v21.h[2], v16.h[1]
	ins	v25.h[2], v16.h[2]
	ins	v22.h[2], v16.h[0]
	ins	v26.h[2], v16.h[3]
	ins	v17.h[2], v16.h[7]
	ins	v18.h[2], v16.h[4]
	ins	v19.h[2], v16.h[5]
	ins	v20.h[2], v16.h[6]
	add	x3, x1, 352
#APP
// 495 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[3], v16.h[7]
	ins	v21.h[3], v16.h[1]
	ins	v18.h[3], v16.h[4]
	ins	v25.h[3], v16.h[2]
	ins	v19.h[3], v16.h[5]
	ins	v22.h[3], v16.h[0]
	ins	v26.h[3], v16.h[3]
	ins	v20.h[3], v16.h[6]
	add	x3, x1, 368
#APP
// 505 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[4], v16.h[7]
	ins	v21.h[4], v16.h[1]
	ins	v18.h[4], v16.h[4]
	ins	v25.h[4], v16.h[2]
	ins	v19.h[4], v16.h[5]
	ins	v22.h[4], v16.h[0]
	ins	v26.h[4], v16.h[3]
	ins	v20.h[4], v16.h[6]
	add	x3, x1, 768
#APP
// 515 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[5], v16.h[7]
	ins	v21.h[5], v16.h[1]
	ins	v18.h[5], v16.h[4]
	ins	v25.h[5], v16.h[2]
	ins	v19.h[5], v16.h[5]
	ins	v22.h[5], v16.h[0]
	ins	v26.h[5], v16.h[3]
	ins	v20.h[5], v16.h[6]
	add	x3, x1, 784
#APP
// 525 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[6], v16.h[7]
	ins	v21.h[6], v16.h[1]
	ins	v18.h[6], v16.h[4]
	ins	v25.h[6], v16.h[2]
	ins	v19.h[6], v16.h[5]
	ins	v22.h[6], v16.h[0]
	ins	v26.h[6], v16.h[3]
	ins	v20.h[6], v16.h[6]
	add	x3, x1, 800
#APP
// 535 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v21.h[7], v15.h[1]
	add	x6, x0, 104
	ins	v25.h[7], v15.h[2]
	add	x5, x0, 320
	ins	v22.h[7], v15.h[0]
	add	x4, x0, 464
	ins	v26.h[7], v15.h[3]
	add	x3, x0, 536
	cmlt	v7.8h, v21.8h, #0
	cmlt	v16.8h, v25.8h, #0
	cmlt	v14.8h, v22.8h, #0
	cmlt	v13.8h, v26.8h, #0
	and	v7.16b, v7.16b, v23.16b
	and	v16.16b, v16.16b, v23.16b
	and	v14.16b, v14.16b, v23.16b
	ins	v17.h[7], v15.h[7]
	add	v21.8h, v7.8h, v21.8h
	add	v25.8h, v16.8h, v25.8h
	and	v16.16b, v13.16b, v23.16b
	add	v22.8h, v14.8h, v22.8h
	uzp2	v11.8h, v21.8h, v21.8h
	uzp2	v14.8h, v25.8h, v25.8h
	add	v26.8h, v16.8h, v26.8h
	uzp1	v21.8h, v21.8h, v21.8h
	shl	v13.8h, v11.8h, 12
	uzp2	v16.8h, v22.8h, v22.8h
	uzp1	v25.8h, v25.8h, v25.8h
	shl	v10.8h, v14.8h, 12
	orr	v2.16b, v21.16b, v13.16b
	uzp2	v21.8h, v26.8h, v26.8h
	ushr	v3.8h, v11.8h, 4
	uzp1	v22.8h, v22.8h, v22.8h
	shl	v11.8h, v16.8h, 12
	orr	v4.16b, v25.16b, v10.16b
	uzp1	v26.8h, v26.8h, v26.8h
	shl	v25.8h, v21.8h, 12
	ushr	v5.8h, v14.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v24.16b
	orr	v0.16b, v22.16b, v11.16b
	ushr	v1.8h, v16.8h, 4
	tbl	v4.16b, {v4.16b - v5.16b}, v24.16b
	ushr	v13.8h, v21.8h, 4
	str	d2, [x0, 96]
	orr	v12.16b, v26.16b, v25.16b
	st1	{v2.s}[2], [x6]
	tbl	v0.16b, {v0.16b - v1.16b}, v24.16b
	mov	v21.16b, v19.16b
	str	d4, [x0, 312]
	ins	v18.h[7], v15.h[4]
	st1	{v4.s}[2], [x5]
	tbl	v26.16b, {v12.16b - v13.16b}, v24.16b
	ins	v20.h[7], v15.h[6]
	str	d0, [x0, 456]
	ins	v21.h[7], v15.h[5]
	st1	{v0.s}[2], [x4]
	str	d26, [x0, 528]
	st1	{v26.s}[2], [x3]
	add	x3, x1, 592
#APP
// 549 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	mov	v19.16b, v31.16b
	mov	v22.16b, v31.16b
	mov	v25.16b, v31.16b
	mov	v26.16b, v31.16b
	ins	v17.h[0], v16.h[3]
	ins	v18.h[0], v16.h[0]
	ins	v21.h[0], v16.h[1]
	ins	v20.h[0], v16.h[2]
	ins	v19.h[0], v16.h[6]
	ins	v22.h[0], v16.h[4]
	ins	v25.h[0], v16.h[7]
	ins	v26.h[0], v16.h[5]
	add	x3, x1, 608
#APP
// 563 "gt864_p9_tobytes_small.c" 1
	ldr q15, [x3]
// 0 "" 2
#NO_APP
	ins	v17.h[1], v15.h[3]
	add	x6, x0, 68
	ins	v18.h[1], v15.h[0]
	add	x5, x0, 176
	ins	v21.h[1], v15.h[1]
	add	x4, x0, 392
	ins	v20.h[1], v15.h[2]
	add	x3, x0, 608
	mov	v12.16b, v17.16b
	cmlt	v17.8h, v17.8h, #0
	mov	v14.16b, v18.16b
	cmlt	v18.8h, v18.8h, #0
	cmlt	v13.8h, v20.8h, #0
	and	v17.16b, v17.16b, v23.16b
	cmlt	v16.8h, v21.8h, #0
	and	v18.16b, v18.16b, v23.16b
	ins	v19.h[1], v15.h[6]
	add	v17.8h, v17.8h, v12.8h
	and	v16.16b, v16.16b, v23.16b
	add	v18.8h, v18.8h, v14.8h
	and	v14.16b, v13.16b, v23.16b
	uzp2	v10.8h, v17.8h, v17.8h
	add	v16.8h, v16.8h, v21.8h
	uzp2	v11.8h, v18.8h, v18.8h
	add	v21.8h, v14.8h, v20.8h
	uzp1	v17.8h, v17.8h, v17.8h
	shl	v14.8h, v10.8h, 12
	uzp2	v20.8h, v16.8h, v16.8h
	uzp1	v18.8h, v18.8h, v18.8h
	uzp1	v16.8h, v16.8h, v16.8h
	orr	v4.16b, v17.16b, v14.16b
	shl	v14.8h, v11.8h, 12
	uzp2	v17.8h, v21.8h, v21.8h
	ushr	v5.8h, v10.8h, 4
	uzp1	v21.8h, v21.8h, v21.8h
	orr	v2.16b, v18.16b, v14.16b
	shl	v14.8h, v20.8h, 12
	shl	v18.8h, v17.8h, 12
	ushr	v3.8h, v11.8h, 4
	tbl	v4.16b, {v4.16b - v5.16b}, v24.16b
	orr	v6.16b, v16.16b, v14.16b
	ushr	v7.8h, v20.8h, 4
	tbl	v2.16b, {v2.16b - v3.16b}, v24.16b
	orr	v12.16b, v21.16b, v18.16b
	str	d4, [x0, 60]
	ushr	v13.8h, v17.8h, 4
	st1	{v4.s}[2], [x6]
	tbl	v6.16b, {v6.16b - v7.16b}, v24.16b
	ins	v22.h[1], v15.h[4]
	str	d2, [x0, 168]
	ins	v25.h[1], v15.h[7]
	st1	{v2.s}[2], [x5]
	tbl	v21.16b, {v12.16b - v13.16b}, v24.16b
	ins	v26.h[1], v15.h[5]
	str	d6, [x0, 384]
	st1	{v6.s}[2], [x4]
	str	d21, [x0, 600]
	st1	{v21.s}[2], [x3]
	add	x3, x1, 384
#APP
// 577 "gt864_p9_tobytes_small.c" 1
	ldr q18, [x3]
// 0 "" 2
#NO_APP
	mov	v20.16b, v31.16b
	mov	v17.16b, v31.16b
	mov	v21.16b, v31.16b
	ins	v19.h[2], v18.h[2]
	ins	v22.h[2], v18.h[0]
	ins	v25.h[2], v18.h[3]
	ins	v26.h[2], v18.h[1]
	ins	v20.h[2], v18.h[5]
	ins	v17.h[2], v18.h[6]
	ins	v21.h[2], v18.h[4]
	ins	v31.h[2], v18.h[7]
	add	x3, x1, 400
#APP
// 591 "gt864_p9_tobytes_small.c" 1
	ldr q18, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[3], v18.h[2]
	ins	v20.h[3], v18.h[5]
	ins	v22.h[3], v18.h[0]
	ins	v25.h[3], v18.h[3]
	ins	v17.h[3], v18.h[6]
	ins	v26.h[3], v18.h[1]
	ins	v21.h[3], v18.h[4]
	ins	v31.h[3], v18.h[7]
	add	x3, x1, 416
#APP
// 601 "gt864_p9_tobytes_small.c" 1
	ldr q18, [x3]
// 0 "" 2
#NO_APP
	ins	v19.h[4], v18.h[2]
	ins	v20.h[4], v18.h[5]
	ins	v22.h[4], v18.h[0]
	ins	v25.h[4], v18.h[3]
	ins	v17.h[4], v18.h[6]
	ins	v26.h[4], v18.h[1]
	ins	v21.h[4], v18.h[4]
	ins	v31.h[4], v18.h[7]
	add	x3, x1, 640
#APP
// 611 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v21.h[0], v16.h[0]
	ins	v27.h[2], v16.h[4]
	ins	v28.h[2], v16.h[7]
	ins	v20.h[0], v16.h[1]
	ins	v29.h[2], v16.h[5]
	ins	v17.h[0], v16.h[2]
	ins	v30.h[2], v16.h[6]
	mov	v18.16b, v21.16b
	ins	v31.h[0], v16.h[3]
	add	x3, x1, 656
#APP
// 621 "gt864_p9_tobytes_small.c" 1
	ldr q16, [x3]
// 0 "" 2
#NO_APP
	ins	v27.h[3], v16.h[4]
	add	x6, x0, 20
	ins	v28.h[3], v16.h[7]
	add	x5, x0, 92
	ins	v29.h[3], v16.h[5]
	add	x4, x0, 236
	ins	v30.h[3], v16.h[6]
	add	x3, x0, 452
	cmlt	v21.8h, v27.8h, #0
	cmlt	v14.8h, v28.8h, #0
	cmlt	v15.8h, v29.8h, #0
	ins	v20.h[1], v16.h[1]
	and	v21.16b, v21.16b, v23.16b
	and	v14.16b, v14.16b, v23.16b
	and	v15.16b, v15.16b, v23.16b
	ins	v17.h[1], v16.h[2]
	add	v21.8h, v21.8h, v27.8h
	cmlt	v27.8h, v30.8h, #0
	add	v14.8h, v14.8h, v28.8h
	add	v28.8h, v15.8h, v29.8h
	uzp2	v15.8h, v21.8h, v21.8h
	and	v29.16b, v27.16b, v23.16b
	uzp1	v21.8h, v21.8h, v21.8h
	uzp2	v27.8h, v14.8h, v14.8h
	uzp2	v13.8h, v28.8h, v28.8h
	add	v29.8h, v29.8h, v30.8h
	shl	v30.8h, v15.8h, 12
	uzp1	v14.8h, v14.8h, v14.8h
	ushr	v3.8h, v15.8h, 4
	uzp1	v28.8h, v28.8h, v28.8h
	orr	v2.16b, v21.16b, v30.16b
	uzp2	v30.8h, v29.8h, v29.8h
	shl	v21.8h, v27.8h, 12
	shl	v15.8h, v13.8h, 12
	uzp1	v29.8h, v29.8h, v29.8h
	ushr	v5.8h, v27.8h, 4
	orr	v4.16b, v14.16b, v21.16b
	shl	v21.8h, v30.8h, 12
	tbl	v2.16b, {v2.16b - v3.16b}, v24.16b
	orr	v6.16b, v28.16b, v15.16b
	ushr	v7.8h, v13.8h, 4
	orr	v0.16b, v29.16b, v21.16b
	tbl	v4.16b, {v4.16b - v5.16b}, v24.16b
	str	d2, [x0, 12]
	ushr	v1.8h, v30.8h, 4
	st1	{v2.s}[2], [x6]
	tbl	v6.16b, {v6.16b - v7.16b}, v24.16b
	mov	v21.16b, v18.16b
	ins	v31.h[1], v16.h[3]
	str	d4, [x0, 84]
	tbl	v0.16b, {v0.16b - v1.16b}, v24.16b
	st1	{v4.s}[2], [x5]
	str	d6, [x0, 228]
	ins	v21.h[1], v16.h[0]
	st1	{v6.s}[2], [x4]
	str	d0, [x2, -68]
	st1	{v0.s}[2], [x3]
	add	x3, x1, 816
#APP
// 635 "gt864_p9_tobytes_small.c" 1
	ldr q27, [x3]
// 0 "" 2
#NO_APP
	mov	v30.16b, v19.16b
	mov	v28.16b, v20.16b
	mov	v29.16b, v17.16b
	ins	v22.h[5], v27.h[0]
	ins	v30.h[5], v27.h[2]
	ins	v28.h[5], v27.h[5]
	ins	v25.h[5], v27.h[3]
	ins	v29.h[5], v27.h[6]
	ins	v26.h[5], v27.h[1]
	ins	v21.h[5], v27.h[4]
	ins	v31.h[5], v27.h[7]
	add	x3, x1, 832
#APP
// 645 "gt864_p9_tobytes_small.c" 1
	ldr q27, [x3]
// 0 "" 2
#NO_APP
	ins	v30.h[6], v27.h[2]
	ins	v28.h[6], v27.h[5]
	ins	v22.h[6], v27.h[0]
	ins	v25.h[6], v27.h[3]
	ins	v29.h[6], v27.h[6]
	ins	v26.h[6], v27.h[1]
	ins	v21.h[6], v27.h[4]
	ins	v31.h[6], v27.h[7]
	add	x1, x1, 848
#APP
// 655 "gt864_p9_tobytes_small.c" 1
	ldr q6, [x1]
// 0 "" 2
#NO_APP
	ins	v30.h[7], v6.h[2]
	add	x9, x0, 140
	ins	v28.h[7], v6.h[5]
	add	x8, x0, 212
	ins	v22.h[7], v6.h[0]
	add	x7, x0, 284
	ins	v25.h[7], v6.h[3]
	add	x6, x0, 356
	cmlt	v20.8h, v30.8h, #0
	add	x5, x0, 428
	cmlt	v18.8h, v28.8h, #0
	add	x4, x0, 500
	ins	v26.h[7], v6.h[1]
	add	x3, x0, 572
	ins	v29.h[7], v6.h[6]
	add	x1, x0, 644
	and	v20.16b, v20.16b, v23.16b
	cmlt	v27.8h, v22.8h, #0
	and	v18.16b, v18.16b, v23.16b
	cmlt	v19.8h, v25.8h, #0
	add	v5.8h, v20.8h, v30.8h
	ins	v21.h[7], v6.h[4]
	ins	v31.h[7], v6.h[7]
	add	v18.8h, v18.8h, v28.8h
	cmlt	v30.8h, v26.8h, #0
	and	v27.16b, v27.16b, v23.16b
	cmlt	v20.8h, v29.8h, #0
	and	v19.16b, v19.16b, v23.16b
	uzp2	v28.8h, v5.8h, v5.8h
	mov	v7.16b, v21.16b
	add	v27.8h, v27.8h, v22.8h
	and	v20.16b, v20.16b, v23.16b
	add	v19.8h, v19.8h, v25.8h
	and	v22.16b, v30.16b, v23.16b
	uzp2	v25.8h, v18.8h, v18.8h
	cmlt	v30.8h, v31.8h, #0
	cmlt	v21.8h, v21.8h, #0
	uzp2	v3.8h, v27.8h, v27.8h
	shl	v6.8h, v28.8h, 12
	add	v29.8h, v20.8h, v29.8h
	and	v30.16b, v30.16b, v23.16b
	uzp1	v5.8h, v5.8h, v5.8h
	and	v21.16b, v21.16b, v23.16b
	uzp1	v18.8h, v18.8h, v18.8h
	shl	v23.8h, v25.8h, 12
	add	v22.8h, v22.8h, v26.8h
	uzp2	v26.8h, v19.8h, v19.8h
	orr	v8.16b, v5.16b, v6.16b
	orr	v10.16b, v18.16b, v23.16b
	add	v21.8h, v21.8h, v7.8h
	add	v31.8h, v30.8h, v31.8h
	shl	v23.8h, v3.8h, 12
	uzp2	v30.8h, v29.8h, v29.8h
	ushr	v9.8h, v28.8h, 4
	uzp1	v27.8h, v27.8h, v27.8h
	uzp2	v28.8h, v22.8h, v22.8h
	uzp1	v20.8h, v29.8h, v29.8h
	uzp1	v19.8h, v19.8h, v19.8h
	shl	v29.8h, v26.8h, 12
	ushr	v11.8h, v25.8h, 4
	orr	v12.16b, v27.16b, v23.16b
	uzp2	v2.8h, v21.8h, v21.8h
	tbl	v23.16b, {v8.16b - v9.16b}, v24.16b
	shl	v18.8h, v30.8h, 12
	ushr	v13.8h, v3.8h, 4
	tbl	v25.16b, {v10.16b - v11.16b}, v24.16b
	orr	v14.16b, v19.16b, v29.16b
	str	d23, [x0, 132]
	uzp2	v11.8h, v31.8h, v31.8h
	st1	{v23.s}[2], [x9]
	shl	v27.8h, v28.8h, 12
	ushr	v15.8h, v26.8h, 4
	str	d25, [x0, 204]
	uzp1	v22.8h, v22.8h, v22.8h
	st1	{v25.s}[2], [x8]
	orr	v16.16b, v20.16b, v18.16b
	tbl	v26.16b, {v12.16b - v13.16b}, v24.16b
	ushr	v17.8h, v30.8h, 4
	uzp1	v21.8h, v21.8h, v21.8h
	shl	v20.8h, v2.8h, 12
	orr	v4.16b, v22.16b, v27.16b
	str	d26, [x2, -236]
	tbl	v27.16b, {v14.16b - v15.16b}, v24.16b
	st1	{v26.s}[2], [x7]
	shl	v29.8h, v11.8h, 12
	ushr	v5.8h, v28.8h, 4
	uzp1	v31.8h, v31.8h, v31.8h
	tbl	v28.16b, {v16.16b - v17.16b}, v24.16b
	str	d27, [x2, -164]
	orr	v6.16b, v21.16b, v20.16b
	st1	{v27.s}[2], [x6]
	ushr	v7.8h, v2.8h, 4
	orr	v18.16b, v31.16b, v29.16b
	ushr	v19.8h, v11.8h, 4
	str	d28, [x2, -92]
	tbl	v29.16b, {v4.16b - v5.16b}, v24.16b
	st1	{v28.s}[2], [x5]
	tbl	v30.16b, {v6.16b - v7.16b}, v24.16b
	tbl	v31.16b, {v18.16b - v19.16b}, v24.16b
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
	.size	p9_input_once_top_small, .-p9_input_once_top_small
	.section	.text.gt864_p9_input_once_small_inner,"ax",@progbits
	.align	2
	.p2align 5,,15
	.global	gt864_p9_input_once_small_inner
	.type	gt864_p9_input_once_small_inner, %function
gt864_p9_input_once_small_inner:
.LFB3919:
	.cfi_startproc
	stp	x29, x30, [sp, -16]!
	.cfi_def_cfa_offset 16
	.cfi_offset 29, -16
	.cfi_offset 30, -8
	mov	x12, x1
	mov	x29, sp
	bl	p9_input_once_top_small
	ldp	x29, x30, [sp], 16
	.cfi_restore 30
	.cfi_restore 29
	.cfi_def_cfa_offset 0
	add	x1, x12, 864
	add	x0, x0, 648
	b	p9_input_once_top_small
	.cfi_endproc
.LFE3919:
	.size	gt864_p9_input_once_small_inner, .-gt864_p9_input_once_small_inner
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
