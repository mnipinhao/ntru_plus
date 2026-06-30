/*
 * Opt-in wrapper for the Slothy-generated GT add32 finalizer microkernel.
 *
 * ABI:
 *   x0 = destination block-major output, 32 int16 coefficients
 *   x1 = raw R^-1 product in SoA vectors: raw0[8], raw1[8], raw2[8], raw3[8]
 *   x2 = addend in SoA vectors: c0[8], c1[8], c2[8], c3[8]
 *
 * Output:
 *   dst[4*j + k] = Mont(c_k[j] * R + raw_k[j] * R^2)
 *
 * This file is not production-wired.  It is a benchmarkable extraction of the
 * real Slothy region from base_gt_add32_rminus1_finalize.n1.opt.S.
 */

.text
.align 2

.global base_gt_add32_finalize8_n1_opt
.global _base_gt_add32_finalize8_n1_opt
base_gt_add32_finalize8_n1_opt:
_base_gt_add32_finalize8_n1_opt:
	ldr q16, [x1, #0]
	ldr q25, [x1, #16]
	ldr q20, [x1, #32]
	ldr q8,  [x1, #48]
	ldr q0,  [x2, #0]
	ldr q6,  [x2, #16]
	ldr q18, [x2, #32]
	ldr q31, [x2, #48]
	adr x3, Ladd32_finalize_consts
	ldr q13, [x3]

	smull2 v24.4s, v20.8h, v13.h[7]
	smlal2 v24.4s, v18.8h, v13.h[3]
	smull v12.4s, v16.4h, v13.h[7]
	smull v15.4s, v8.4h, v13.h[7]
	smull v11.4s, v20.4h, v13.h[7]
	smlal v11.4s, v18.4h, v13.h[3]
	smull2 v28.4s, v16.8h, v13.h[7]
	smull v2.4s, v25.4h, v13.h[7]
	smlal v12.4s, v0.4h, v13.h[3]
	uzp1 v10.8h, v11.8h, v24.8h
	smull2 v4.4s, v8.8h, v13.h[7]
	smull2 v1.4s, v25.8h, v13.h[7]
	mul v14.8h, v10.8h, v13.h[2]
	smlal v15.4s, v31.4h, v13.h[3]
	smlal2 v28.4s, v0.8h, v13.h[3]
	smlal2 v4.4s, v31.8h, v13.h[3]
	smlal2 v24.4s, v14.8h, v13.h[0]
	smlal2 v1.4s, v6.8h, v13.h[3]
	smlal v2.4s, v6.4h, v13.h[3]
	uzp1 v23.8h, v12.8h, v28.8h
	smlal v11.4s, v14.4h, v13.h[0]
	uzp1 v9.8h, v15.8h, v4.8h
	mul v29.8h, v23.8h, v13.h[2]
	mul v17.8h, v9.8h, v13.h[2]
	uzp1 v3.8h, v2.8h, v1.8h
	uzp2 v11.8h, v11.8h, v24.8h
	mul v27.8h, v3.8h, v13.h[2]
	smlal2 v28.4s, v29.8h, v13.h[0]
	smlal v12.4s, v29.4h, v13.h[0]
	smlal2 v4.4s, v17.8h, v13.h[0]
	smlal v2.4s, v27.4h, v13.h[0]
	smlal v15.4s, v17.4h, v13.h[0]
	smlal2 v1.4s, v27.8h, v13.h[0]
	uzp2 v9.8h, v12.8h, v28.8h
	uzp2 v12.8h, v15.8h, v4.8h
	uzp2 v10.8h, v2.8h, v1.8h
	st4 {v9.8h, v10.8h, v11.8h, v12.8h}, [x0]
	ret

.align 4
Ladd32_finalize_consts:
	.hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d
	.hword 0xfa8f, 0xf9dd, 0xc5d5, 0x0363
