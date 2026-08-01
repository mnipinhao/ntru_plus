/*
 * Benchmark-only 15-multiplication fqinv candidates.
 *
 * v0 = input a, v1 = constants, v0 = scaled inverse result.
 * Caller-saved vector registers only.
 */

.text
.align 2

#include "../support/common.inc"

.macro fqmul_p dst, lhs, rhs
	smull v16.4s, \lhs\().4h, \rhs\().4h
	smull2 v17.4s, \lhs\().8h, \rhs\().8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 \dst\().8h, v16.8h, v17.8h
.endm

.macro fqinv15_parallel_prefix
	mov v2.16b, v0.16b
	fqmul_p v0, v0, v0      // 2
	fqmul_p v0, v0, v0      // 4
	fqmul_p v0, v0, v0      // 8
	fqmul_p v3, v0, v0      // 16
.endm

.macro fqinv15_parallel_suffix
	fqmul_p v0, v5, v5      // 64
	fqmul_p v6, v0, v0      // 128
	fqmul_p v4, v6, v4      // 145
	fqmul_p v0, v4, v6      // 273
	fqmul_p v0, v0, v0      // 546
	fqmul_p v7, v0, v4      // 691
	fqmul_p v0, v7, v7      // 1382
	fqmul_p v0, v0, v0      // 2764
	fqmul_p v0, v0, v7      // 3455

	sqrdmulh v3.8h, v0.8h, v1.h[6]
	mul v0.8h, v0.8h, v1.h[5]
	mls v0.8h, v3.8h, v1.h[0]
	ret
.endm

.p2align 5
.global C_SYM(gt_fqinv15_parallel_source_asm)
C_SYM(gt_fqinv15_parallel_source_asm):
	fqinv15_parallel_prefix
	fqmul_p v4, v3, v2      // 17
	fqmul_p v5, v3, v3      // 32
	fqinv15_parallel_suffix

.p2align 5
.global C_SYM(gt_fqinv15_parallel_interleaved_asm)
C_SYM(gt_fqinv15_parallel_interleaved_asm):
	fqinv15_parallel_prefix

	// a^17 and a^32 are independent; use disjoint temporary triples.
	smull v16.4s, v3.4h, v2.4h
	smull v19.4s, v3.4h, v3.4h
	smull2 v17.4s, v3.8h, v2.8h
	smull2 v20.4s, v3.8h, v3.8h
	uzp1 v18.8h, v16.8h, v17.8h
	uzp1 v21.8h, v19.8h, v20.8h
	mul v18.8h, v18.8h, v1.h[2]
	mul v21.8h, v21.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal v19.4s, v21.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal2 v20.4s, v21.8h, v1.h[0]
	uzp2 v4.8h, v16.8h, v17.8h
	uzp2 v5.8h, v19.8h, v20.8h

	fqinv15_parallel_suffix
