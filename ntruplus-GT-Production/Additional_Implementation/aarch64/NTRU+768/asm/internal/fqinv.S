/*
 * GT batch baseinv scalar-field inversion core.
 *
 * ABI:
 *   v0 = input vector a
 *   v1 = constants vector:
 *        h[0] = q, h[2] = qinv, h[5]/h[6] = final scale/precompute
 *   returns v0 = a^{-1} in the same Montgomery/scaled representation as the
 *                existing C Neon fqinv_neon().
 *
 * Caller-saved vector registers only: v0-v7 and v16-v18.
 */

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

.macro fqmul dst, lhs, rhs
	smull v16.4s, \lhs\().4h, \rhs\().4h
	smull2 v17.4s, \lhs\().8h, \rhs\().8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 \dst\().8h, v16.8h, v17.8h
.endm

.global C_SYM(gt_fqinv15_asm)
C_SYM(gt_fqinv15_asm):
	mov v2.16b, v0.16b

	fqmul v0, v0, v0      // 2
	fqmul v0, v0, v0      // 4
	fqmul v0, v0, v0      // 8
	fqmul v3, v0, v0      // 16

	fqmul v0, v3, v3      // 32
	fqmul v0, v0, v0      // 64
	fqmul v4, v0, v0      // 128

	fqmul v0, v4, v3      // 144
	fqmul v5, v0, v2      // 145
	fqmul v0, v5, v4      // 273
	fqmul v0, v0, v0      // 546
	fqmul v6, v0, v5      // 691

	fqmul v0, v6, v6      // 1382
	fqmul v0, v0, v0      // 2764
	fqmul v0, v0, v6      // 3455

	sqrdmulh v7.8h, v0.8h, v1.h[6]
	mul v0.8h, v0.8h, v1.h[5]
	mls v0.8h, v7.8h, v1.h[0]
	ret
