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
 * Caller-saved vector registers only: v0-v7 and v16-v21.
 *
 * The 15-multiplication exponent DAG and instruction order were scheduled for
 * Cortex-A76 with fixed-register Slothy scheduling.
 */

.text
.p2align 5

#include "../support/common.inc"

.global C_SYM(gt_fqinv15_asm)
C_SYM(gt_fqinv15_asm):
	smull v16.4s, v0.4h, v0.4h
	orr v2.16b, v0.16b, v0.16b
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v0.4h
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v0.4h
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v0.8h
	smull v16.4s, v0.4h, v0.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v3.8h, v16.8h, v17.8h
	smull v19.4s, v3.4h, v3.4h
	smull2 v20.4s, v3.8h, v3.8h
	smull v16.4s, v3.4h, v2.4h
	smull2 v17.4s, v3.8h, v2.8h
	uzp1 v21.8h, v19.8h, v20.8h
	mul v21.8h, v21.8h, v1.h[2]
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v19.4s, v21.4h, v1.h[0]
	smlal2 v20.4s, v21.8h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v5.8h, v19.8h, v20.8h
	uzp2 v4.8h, v16.8h, v17.8h
	smull v16.4s, v5.4h, v5.4h
	smull2 v17.4s, v5.8h, v5.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v0.8h
	smull v16.4s, v0.4h, v0.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v6.8h, v16.8h, v17.8h
	smull2 v17.4s, v6.8h, v4.8h
	smull v16.4s, v6.4h, v4.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v4.8h, v16.8h, v17.8h
	smull v16.4s, v4.4h, v6.4h
	smull2 v17.4s, v4.8h, v6.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v0.4h
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v4.8h
	smull v16.4s, v0.4h, v4.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v7.8h, v16.8h, v17.8h
	smull v16.4s, v7.4h, v7.4h
	smull2 v17.4s, v7.8h, v7.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v0.8h
	smull v16.4s, v0.4h, v0.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v7.4h
	smull2 v17.4s, v0.8h, v7.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	sqrdmulh v3.8h, v0.8h, v1.h[6]
	mul v0.8h, v0.8h, v1.h[5]
	mls v0.8h, v3.8h, v1.h[0]
	ret
