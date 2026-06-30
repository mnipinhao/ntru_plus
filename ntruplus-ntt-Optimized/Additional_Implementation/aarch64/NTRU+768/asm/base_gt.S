.text
.align 2

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)@PAGE
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, C_SYM(sym)@PAGEOFF
#else
#define C_SYM(sym) sym
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, :lo12:C_SYM(sym)
#endif

.macro GT_STORE_TUPLE8 r0, r1, r2, r3
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[0], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[1], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[2], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[3], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[4], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[5], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[6], [x9]
	ldrh w9, [offsets], #2
	add x9, dst, x9
	st4 {\r0\().h, \r1\().h, \r2\().h, \r3\().h}[7], [x9]
.endm

/*
 * GT row-bitrev optimized poly_basemul.
 *
 * Layout:
 *   coeff[branch*384 + 4*physical_j + lane]
 *
 * This routine processes eight consecutive physical quartic blocks at a time:
 *   ld4 -> a0,a1,a2,a3 vectors for physical_j..physical_j+7
 *   ld4 -> b0,b1,b2,b3 vectors for physical_j..physical_j+7
 *
 * Constants:
 *   gt_rowbitrev_lambda[branch][physical_j] is Montgomery-form.  This kernel
 *   therefore uses the same Montgomery reduction arithmetic as stock base.s,
 *   but with the GT physical-order lambda table and GT block-major ld4/st4
 *   memory layout.  It intentionally does not use stock zetas_mul.
 */

.global poly_basemul
.global _poly_basemul
poly_basemul:
_poly_basemul:
	dst       .req x0
	src1      .req x1
	src2      .req x2
	const_ptr .req x3
	lambda    .req x4
	counter   .req x8
#ifdef GT_BASEMUL_STORE_TUPLE
	offsets   .req x6
#endif

	adr const_ptr, Lgt_base_consts
	ld1 {v0.8h}, [const_ptr]

	LOAD_ADDR_PAGE(lambda, gt_rowbitrev_lambda)
	LOAD_ADDR_OFF(lambda, gt_rowbitrev_lambda)

#ifdef GT_BASEMUL_STORE_TUPLE
	adr offsets, Lgt_block_to_tuple_store_offsets
#endif

	mov counter, #24

Lgt_basemul_loop:
	ld1 {v1.8h}, [lambda], #16

	ld4 {v4.8h, v5.8h, v6.8h, v7.8h}, [src1], #64
	ld4 {v8.8h, v9.8h, v10.8h, v11.8h}, [src2], #64

	smull   v12.4s, v5.4h, v11.4h // a1*b3
	smull2  v13.4s, v5.8h, v11.8h // a1*b3
	smull   v14.4s, v6.4h, v11.4h // a2*b3
	smull2  v15.4s, v6.8h, v11.8h // a2*b3
	smull   v16.4s, v7.4h, v11.4h // a3*b3
	smull2  v17.4s, v7.8h, v11.8h // a3*b3

	smlal   v12.4s, v6.4h, v10.4h // a2*b2
	smlal2  v13.4s, v6.8h, v10.8h // a2*b2
	smlal   v14.4s, v7.4h, v10.4h // a3*b2
	smlal2  v15.4s, v7.8h, v10.8h // a3*b2

	smlal   v12.4s, v7.4h, v9.4h  // a3*b1
	smlal2  v13.4s, v7.8h, v9.8h  // a3*b1

	uzp1    v20.8h, v16.8h, v17.8h
	uzp1    v19.8h, v14.8h, v15.8h
	uzp1    v18.8h, v12.8h, v13.8h

	mul     v20.8h, v20.8h, v0.h[2]
	mul     v19.8h, v19.8h, v0.h[2]
	mul     v18.8h, v18.8h, v0.h[2]

	smlal   v16.4s, v20.4h, v0.h[0]
	smlal2  v17.4s, v20.8h, v0.h[0]
	smlal   v14.4s, v19.4h, v0.h[0]
	smlal2  v15.4s, v19.8h, v0.h[0]
	smlal   v12.4s, v18.4h, v0.h[0]
	smlal2  v13.4s, v18.8h, v0.h[0]

	uzp2    v30.8h, v16.8h, v17.8h
	uzp2    v29.8h, v14.8h, v15.8h
	uzp2    v28.8h, v12.8h, v13.8h

	smull   v18.4s, v7.4h, v8.4h  // a3*b0
	smull2  v19.4s, v7.8h, v8.8h  // a3*b0
	smull   v16.4s, v30.4h, v1.4h // lambda*(a3*b3)
	smull2  v17.4s, v30.8h, v1.8h // lambda*(a3*b3)
	smull   v14.4s, v29.4h, v1.4h // lambda*(a2*b3 + a3*b2)
	smull2  v15.4s, v29.8h, v1.8h // lambda*(a2*b3 + a3*b2)
	smull   v12.4s, v28.4h, v1.4h // lambda*(a1*b3 + a2*b2 + a3*b1)
	smull2  v13.4s, v28.8h, v1.8h // lambda*(a1*b3 + a2*b2 + a3*b1)

	smlal   v18.4s, v4.4h, v11.4h // a0*b3
	smlal2  v19.4s, v4.8h, v11.8h // a0*b3
	smlal   v16.4s, v4.4h, v10.4h // a0*b2
	smlal2  v17.4s, v4.8h, v10.8h // a0*b2
	smlal   v14.4s, v4.4h, v9.4h  // a0*b1
	smlal2  v15.4s, v4.8h, v9.8h  // a0*b1
	smlal   v12.4s, v4.4h, v8.4h  // a0*b0
	smlal2  v13.4s, v4.8h, v8.8h  // a0*b0

	smlal   v18.4s, v5.4h, v10.4h // a1*b2
	smlal2  v19.4s, v5.8h, v10.8h // a1*b2
	smlal   v16.4s, v5.4h, v9.4h  // a1*b1
	smlal2  v17.4s, v5.8h, v9.8h  // a1*b1
	smlal   v14.4s, v5.4h, v8.4h  // a1*b0
	smlal2  v15.4s, v5.8h, v8.8h  // a1*b0

	smlal   v18.4s, v6.4h, v9.4h  // a2*b1
	smlal2  v19.4s, v6.8h, v9.8h  // a2*b1
	smlal   v16.4s, v6.4h, v8.4h  // a2*b0
	smlal2  v17.4s, v6.8h, v8.8h  // a2*b0

	uzp1    v23.8h, v18.8h, v19.8h
	uzp1    v22.8h, v16.8h, v17.8h
	uzp1    v21.8h, v14.8h, v15.8h
	uzp1    v20.8h, v12.8h, v13.8h

	mul     v23.8h, v23.8h, v0.h[2]
	mul     v22.8h, v22.8h, v0.h[2]
	mul     v21.8h, v21.8h, v0.h[2]
	mul     v20.8h, v20.8h, v0.h[2]

	smlal   v18.4s, v23.4h, v0.h[0]
	smlal   v16.4s, v22.4h, v0.h[0]
	smlal   v14.4s, v21.4h, v0.h[0]
	smlal   v12.4s, v20.4h, v0.h[0]

	smlal2  v19.4s, v23.8h, v0.h[0]
	smlal2  v17.4s, v22.8h, v0.h[0]
	smlal2  v15.4s, v21.8h, v0.h[0]
	smlal2  v13.4s, v20.8h, v0.h[0]

	uzp2    v7.8h, v18.8h, v19.8h
	uzp2    v6.8h, v16.8h, v17.8h
	uzp2    v5.8h, v14.8h, v15.8h
	uzp2    v4.8h, v12.8h, v13.8h

#ifdef GT_BASEMUL_STORE_RMINUS1
#ifdef GT_BASEMUL_ACCUM_RMINUS1
	ld4 {v8.8h, v9.8h, v10.8h, v11.8h}, [dst]
	add  v4.8h,  v4.8h,  v8.8h
	add  v5.8h,  v5.8h,  v9.8h
	add  v6.8h,  v6.8h, v10.8h
	add  v7.8h,  v7.8h, v11.8h
#endif
#ifdef GT_BASEMUL_STORE_TUPLE
	GT_STORE_TUPLE8 v4, v5, v6, v7
#else
	st4 {v4.8h, v5.8h, v6.8h, v7.8h}, [dst], #64
#endif
#else
	mul v11.8h, v7.8h, v0.h[3]
	mul v10.8h, v6.8h, v0.h[3]
	mul  v9.8h, v5.8h, v0.h[3]
	mul  v8.8h, v4.8h, v0.h[3]

	sqrdmulh v7.8h, v7.8h, v0.h[4]
	sqrdmulh v6.8h, v6.8h, v0.h[4]
	sqrdmulh v5.8h, v5.8h, v0.h[4]
	sqrdmulh v4.8h, v4.8h, v0.h[4]

	mls v11.8h, v7.8h, v0.h[0]
	mls v10.8h, v6.8h, v0.h[0]
	mls  v9.8h, v5.8h, v0.h[0]
	mls  v8.8h, v4.8h, v0.h[0]

	sqdmulh v15.8h, v11.8h, v0.h[1]
	sqdmulh v14.8h, v10.8h, v0.h[1]
	sqdmulh v13.8h,  v9.8h, v0.h[1]
	sqdmulh v12.8h,  v8.8h, v0.h[1]

	srshr v15.8h, v15.8h, #11
	srshr v14.8h, v14.8h, #11
	srshr v13.8h, v13.8h, #11
	srshr v12.8h, v12.8h, #11

	mls v11.8h, v15.8h, v0.h[0]
	mls v10.8h, v14.8h, v0.h[0]
	mls  v9.8h, v13.8h, v0.h[0]
	mls  v8.8h, v12.8h, v0.h[0]

#ifdef GT_BASEMUL_STORE_TUPLE
	GT_STORE_TUPLE8 v8, v9, v10, v11
#else
	st4 {v8.8h, v9.8h, v10.8h, v11.8h}, [dst], #64
#endif
#endif

	subs counter, counter, #1
	b.ne Lgt_basemul_loop

	.unreq dst
	.unreq src1
	.unreq src2
	.unreq const_ptr
	.unreq lambda
	.unreq counter
#ifdef GT_BASEMUL_STORE_TUPLE
	.unreq offsets
#endif

	ret

.align 4
Lgt_base_consts:
	.hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d, 0xfa8f, 0xf9dd, 0xc5d5, 0x0363

.global poly_basemul_add
.global _poly_basemul_add
poly_basemul_add:
_poly_basemul_add:
	dst       .req x0
	src1      .req x1
	src2      .req x2
	src3      .req x3
	lambda    .req x4
	const_ptr .req x5
	counter   .req x8

	adr const_ptr, Lgt_base_consts
	ld1 {v0.8h}, [const_ptr]

	LOAD_ADDR_PAGE(lambda, gt_rowbitrev_lambda)
	LOAD_ADDR_OFF(lambda, gt_rowbitrev_lambda)

	mov counter, #24

Lgt_basemul_add_loop:
	ld1 {v1.8h}, [lambda], #16

	ld4 {v4.8h, v5.8h, v6.8h, v7.8h}, [src1], #64
	ld4 {v8.8h, v9.8h, v10.8h, v11.8h}, [src2], #64
	ld4 {v12.8h, v13.8h, v14.8h, v15.8h}, [src3], #64

	smull  v16.4s, v5.4h, v11.4h // a1*b3
	smull2 v17.4s, v5.8h, v11.8h // a1*b3
	smull  v18.4s, v6.4h, v11.4h // a2*b3
	smull2 v19.4s, v6.8h, v11.8h // a2*b3
	smull  v20.4s, v7.4h, v11.4h // a3*b3
	smull2 v21.4s, v7.8h, v11.8h // a3*b3

	smlal  v16.4s, v6.4h, v10.4h // a2*b2
	smlal2 v17.4s, v6.8h, v10.8h // a2*b2
	smlal  v18.4s, v7.4h, v10.4h // a3*b2
	smlal2 v19.4s, v7.8h, v10.8h // a3*b2

	smlal  v16.4s, v7.4h, v9.4h // a3*b1
	smlal2 v17.4s, v7.8h, v9.8h // a3*b1

	uzp1 v24.8h, v20.8h, v21.8h
	uzp1 v23.8h, v18.8h, v19.8h
	uzp1 v22.8h, v16.8h, v17.8h

	mul v24.8h, v24.8h, v0.h[2]
	mul v23.8h, v23.8h, v0.h[2]
	mul v22.8h, v22.8h, v0.h[2]

	smlal  v20.4s, v24.4h, v0.h[0]
	smlal2 v21.4s, v24.8h, v0.h[0]
	smlal  v18.4s, v23.4h, v0.h[0]
	smlal2 v19.4s, v23.8h, v0.h[0]
	smlal  v16.4s, v22.4h, v0.h[0]
	smlal2 v17.4s, v22.8h, v0.h[0]

	uzp2 v30.8h, v20.8h, v21.8h
	uzp2 v29.8h, v18.8h, v19.8h
	uzp2 v28.8h, v16.8h, v17.8h

	smull  v22.4s, v7.4h, v8.4h  // a3*b0
	smull2 v23.4s, v7.8h, v8.8h  // a3*b0
	smull  v20.4s, v30.4h, v1.4h // lambda*(a3*b3)
	smull2 v21.4s, v30.8h, v1.8h // lambda*(a3*b3)
	smull  v18.4s, v29.4h, v1.4h // lambda*(a2*b3 + a3*b2)
	smull2 v19.4s, v29.8h, v1.8h // lambda*(a2*b3 + a3*b2)
	smull  v16.4s, v28.4h, v1.4h // lambda*(a1*b3 + a2*b2 + a3*b1)
	smull2 v17.4s, v28.8h, v1.8h // lambda*(a1*b3 + a2*b2 + a3*b1)

	smlal  v22.4s, v4.4h, v11.4h // a0*b3
	smlal2 v23.4s, v4.8h, v11.8h // a0*b3
	smlal  v20.4s, v4.4h, v10.4h // a0*b2
	smlal2 v21.4s, v4.8h, v10.8h // a0*b2
	smlal  v18.4s, v4.4h, v9.4h  // a0*b1
	smlal2 v19.4s, v4.8h, v9.8h  // a0*b1
	smlal  v16.4s, v4.4h, v8.4h  // a0*b0
	smlal2 v17.4s, v4.8h, v8.8h  // a0*b0

	smlal  v22.4s, v5.4h, v10.4h // a1*b2
	smlal2 v23.4s, v5.8h, v10.8h // a1*b2
	smlal  v20.4s, v5.4h, v9.4h  // a1*b1
	smlal2 v21.4s, v5.8h, v9.8h  // a1*b1
	smlal  v18.4s, v5.4h, v8.4h  // a1*b0
	smlal2 v19.4s, v5.8h, v8.8h  // a1*b0

	smlal  v22.4s, v6.4h, v9.4h  // a2*b1
	smlal2 v23.4s, v6.8h, v9.8h  // a2*b1
	smlal  v20.4s, v6.4h, v8.4h  // a2*b0
	smlal2 v21.4s, v6.8h, v8.8h  // a2*b0

	uzp1 v24.8h, v16.8h, v17.8h
	uzp1 v25.8h, v18.8h, v19.8h
	uzp1 v26.8h, v20.8h, v21.8h
	uzp1 v27.8h, v22.8h, v23.8h

	mul v24.8h, v24.8h, v0.h[2]
	mul v25.8h, v25.8h, v0.h[2]
	mul v26.8h, v26.8h, v0.h[2]
	mul v27.8h, v27.8h, v0.h[2]

	smlal  v16.4s, v24.4h, v0.h[0]
	smlal2 v17.4s, v24.8h, v0.h[0]
	smlal  v18.4s, v25.4h, v0.h[0]
	smlal2 v19.4s, v25.8h, v0.h[0]
	smlal  v20.4s, v26.4h, v0.h[0]
	smlal2 v21.4s, v26.8h, v0.h[0]
	smlal  v22.4s, v27.4h, v0.h[0]
	smlal2 v23.4s, v27.8h, v0.h[0]

	uzp2 v4.8h, v16.8h, v17.8h
	uzp2 v5.8h, v18.8h, v19.8h
	uzp2 v6.8h, v20.8h, v21.8h
	uzp2 v7.8h, v22.8h, v23.8h

#ifdef GT_BASEMUL_ADD32_RMINUS1_FINALIZE
	smull2 v24.4s, v6.8h, v0.h[7]
	smlal2 v24.4s, v14.8h, v0.h[3]
	smull  v11.4s, v4.4h, v0.h[7]
	smull  v21.4s, v7.4h, v0.h[7]
	smull  v10.4s, v6.4h, v0.h[7]
	smlal  v10.4s, v14.4h, v0.h[3]
	smull2 v26.4s, v4.8h, v0.h[7]
	smull  v17.4s, v5.4h, v0.h[7]
	smlal  v11.4s, v12.4h, v0.h[3]
	uzp1   v9.8h,  v10.8h, v24.8h
	smull2 v19.4s, v7.8h, v0.h[7]
	smull2 v16.4s, v5.8h, v0.h[7]
	mul    v20.8h, v9.8h,  v0.h[2]
	smlal  v21.4s, v15.4h, v0.h[3]
	smlal2 v26.4s, v12.8h, v0.h[3]
	smlal2 v19.4s, v15.8h, v0.h[3]
	smlal2 v24.4s, v20.8h, v0.h[0]
	smlal2 v16.4s, v13.8h, v0.h[3]
	smlal  v17.4s, v13.4h, v0.h[3]
	uzp1   v23.8h, v11.8h, v26.8h
	smlal  v10.4s, v20.4h, v0.h[0]
	uzp1   v8.8h,  v21.8h, v19.8h
	mul    v27.8h, v23.8h, v0.h[2]
	mul    v22.8h, v8.8h,  v0.h[2]
	uzp1   v18.8h, v17.8h, v16.8h
	uzp2   v10.8h, v10.8h, v24.8h
	mul    v25.8h, v18.8h, v0.h[2]
	smlal2 v26.4s, v27.8h, v0.h[0]
	smlal  v11.4s, v27.4h, v0.h[0]
	smlal2 v19.4s, v22.8h, v0.h[0]
	smlal  v17.4s, v25.4h, v0.h[0]
	smlal  v21.4s, v22.4h, v0.h[0]
	smlal2 v16.4s, v25.8h, v0.h[0]
	uzp2   v8.8h,  v11.8h, v26.8h
	uzp2   v11.8h, v21.8h, v19.8h
	uzp2   v9.8h,  v17.8h, v16.8h

	st4 {v8.8h, v9.8h, v10.8h, v11.8h}, [dst], #64
#else
	mul  v8.8h, v4.8h, v0.h[3]
	mul  v9.8h, v5.8h, v0.h[3]
	mul v10.8h, v6.8h, v0.h[3]
	mul v11.8h, v7.8h, v0.h[3]

	sqrdmulh v4.8h, v4.8h, v0.h[4]
	sqrdmulh v5.8h, v5.8h, v0.h[4]
	sqrdmulh v6.8h, v6.8h, v0.h[4]
	sqrdmulh v7.8h, v7.8h, v0.h[4]

	mls  v8.8h, v4.8h, v0.h[0]
	mls  v9.8h, v5.8h, v0.h[0]
	mls v10.8h, v6.8h, v0.h[0]
	mls v11.8h, v7.8h, v0.h[0]

	add  v8.8h,  v8.8h, v12.8h
	add  v9.8h,  v9.8h, v13.8h
	add v10.8h, v10.8h, v14.8h
	add v11.8h, v11.8h, v15.8h

	sqdmulh v12.8h,  v8.8h, v0.h[1]
	sqdmulh v13.8h,  v9.8h, v0.h[1]
	sqdmulh v14.8h, v10.8h, v0.h[1]
	sqdmulh v15.8h, v11.8h, v0.h[1]

	srshr v12.8h, v12.8h, #11
	srshr v13.8h, v13.8h, #11
	srshr v14.8h, v14.8h, #11
	srshr v15.8h, v15.8h, #11

	mls  v8.8h, v12.8h, v0.h[0]
	mls  v9.8h, v13.8h, v0.h[0]
	mls v10.8h, v14.8h, v0.h[0]
	mls v11.8h, v15.8h, v0.h[0]

	st4 {v8.8h, v9.8h, v10.8h, v11.8h}, [dst], #64
#endif

	subs counter, counter, #1
	b.ne Lgt_basemul_add_loop

	.unreq dst
	.unreq src1
	.unreq src2
	.unreq src3
	.unreq lambda
	.unreq const_ptr
	.unreq counter

	ret

#ifdef GT_BASEMUL_STORE_TUPLE
.align 4
Lgt_block_to_tuple_store_offsets:
	.hword    0,  600,  432,    8,  608,  440,   16,  616
	.hword  448,   24,  624,  456,   32,  632,  464,   40
	.hword  640,  472,   48,  648,  480,   56,  656,  488
	.hword   64,  664,  496,   72,  672,  504,   80,  680
	.hword  256,   88,  688,  264,   96,  696,  272,  104
	.hword  704,  280,  112,  712,  288,  120,  720,  296
	.hword  128,  728,  304,  136,  736,  312,  144,  744
	.hword  320,  152,  752,  328,  160,  760,  336,  168
	.hword  512,  344,  176,  520,  352,  184,  528,  360
	.hword  192,  536,  368,  200,  544,  376,  208,  552
	.hword  384,  216,  560,  392,  224,  568,  400,  232
	.hword  576,  408,  240,  584,  416,  248,  592,  424
	.hword  768, 1368, 1200,  776, 1376, 1208,  784, 1384
	.hword 1216,  792, 1392, 1224,  800, 1400, 1232,  808
	.hword 1408, 1240,  816, 1416, 1248,  824, 1424, 1256
	.hword  832, 1432, 1264,  840, 1440, 1272,  848, 1448
	.hword 1024,  856, 1456, 1032,  864, 1464, 1040,  872
	.hword 1472, 1048,  880, 1480, 1056,  888, 1488, 1064
	.hword  896, 1496, 1072,  904, 1504, 1080,  912, 1512
	.hword 1088,  920, 1520, 1096,  928, 1528, 1104,  936
	.hword 1280, 1112,  944, 1288, 1120,  952, 1296, 1128
	.hword  960, 1304, 1136,  968, 1312, 1144,  976, 1320
	.hword 1152,  984, 1328, 1160,  992, 1336, 1168, 1000
	.hword 1344, 1176, 1008, 1352, 1184, 1016, 1360, 1192
#endif
