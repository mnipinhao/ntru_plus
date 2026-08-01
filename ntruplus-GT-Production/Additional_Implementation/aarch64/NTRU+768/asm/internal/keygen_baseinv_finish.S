/* Production keygen baseinv finish: CQ output for mixed basemul. */

.text
.align 2

/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

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

#endif

.macro fqmul4 d0, l0, r0, d1, l1, r1, d2, l2, r2, d3, l3, r3
	smull v16.4s, \l0\().4h, \r0\().4h
	smull2 v17.4s, \l0\().8h, \r0\().8h
	smull v18.4s, \l1\().4h, \r1\().4h
	smull2 v19.4s, \l1\().8h, \r1\().8h
	smull v20.4s, \l2\().4h, \r2\().4h
	smull2 v21.4s, \l2\().8h, \r2\().8h
	smull v22.4s, \l3\().4h, \r3\().4h
	smull2 v23.4s, \l3\().8h, \r3\().8h
	uzp1 v24.8h, v16.8h, v17.8h
	uzp1 v25.8h, v18.8h, v19.8h
	uzp1 v26.8h, v20.8h, v21.8h
	uzp1 v27.8h, v22.8h, v23.8h
	mul v24.8h, v24.8h, v1.h[2]
	mul v25.8h, v25.8h, v1.h[2]
	mul v26.8h, v26.8h, v1.h[2]
	mul v27.8h, v27.8h, v1.h[2]
	smlal v16.4s, v24.4h, v1.h[0]
	smlal2 v17.4s, v24.8h, v1.h[0]
	smlal v18.4s, v25.4h, v1.h[0]
	smlal2 v19.4s, v25.8h, v1.h[0]
	smlal v20.4s, v26.4h, v1.h[0]
	smlal2 v21.4s, v26.8h, v1.h[0]
	smlal v22.4s, v27.4h, v1.h[0]
	smlal2 v23.4s, v27.8h, v1.h[0]
	uzp2 \d0\().8h, v16.8h, v17.8h
	uzp2 \d1\().8h, v18.8h, v19.8h
	uzp2 \d2\().8h, v20.8h, v21.8h
	uzp2 \d3\().8h, v22.8h, v23.8h
.endm

/* x0=CQ output, x1=CQ numerator scratch, x2=inverted denominators. */
.global C_SYM(gt_keygen_baseinv_cq_finish)
#ifndef __APPLE__
.type C_SYM(gt_keygen_baseinv_cq_finish), %function
#endif
C_SYM(gt_keygen_baseinv_cq_finish):
	ldr q1, Lbpq_finish_scaled_r_consts
	mov w3, #24

Lbpq_finish_cq_loop:
	ldp q2, q3, [x1], #32
	ldp q4, q5, [x1], #32
	ldr q6, [x2], #16
	neg v7.8h, v6.8h

	fqmul4 v28, v2, v6, v29, v3, v7, \
	         v30, v4, v6, v31, v5, v7

	stp q28, q29, [x0], #32
	stp q30, q31, [x0], #32
	subs w3, w3, #1
	b.ne Lbpq_finish_cq_loop
	/* P0-B: output is committed; erase secret vector temporaries. */
	movi v1.16b, #0
	movi v2.16b, #0
	movi v3.16b, #0
	movi v4.16b, #0
	movi v5.16b, #0
	movi v6.16b, #0
	movi v7.16b, #0
	movi v16.16b, #0
	movi v17.16b, #0
	movi v18.16b, #0
	movi v19.16b, #0
	movi v20.16b, #0
	movi v21.16b, #0
	movi v22.16b, #0
	movi v23.16b, #0
	movi v24.16b, #0
	movi v25.16b, #0
	movi v26.16b, #0
	movi v27.16b, #0
	movi v28.16b, #0
	movi v29.16b, #0
	movi v30.16b, #0
	movi v31.16b, #0
	ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_baseinv_cq_finish), \
	.-C_SYM(gt_keygen_baseinv_cq_finish)
#endif

.p2align 4
Lbpq_finish_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0
