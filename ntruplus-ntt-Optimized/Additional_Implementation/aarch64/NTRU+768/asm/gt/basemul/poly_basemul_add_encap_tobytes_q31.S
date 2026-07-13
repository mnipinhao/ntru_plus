/*
 * GT encap-only poly_basemul_add direct32 Q31 byte-contract path.
 *
 * This is not a production replacement for poly_basemul_add.  It keeps the
 * current poly_basemul_add.n1.opt.inc register allocation through the
 * quartic product accumulator boundary, then replaces the product Montgomery
 * fold plus add32 finalizer with:
 *
 *   out = tobytes-contract reduce(P + c)
 *
 * The reducer uses the exhaustively-checked Q31 constant C=621199 for q=3457:
 *
 *   t = sqrdmulh_s32(x, C)
 *   y = x - t * q
 *
 * The output is byte-equivalent under poly_tobytes, not a general centered
 * representative contract.  Callers must consume the result immediately with
 * poly_tobytes in the encap ciphertext path.
 */

.text
.align 2

#include "../support/common.inc"

.global poly_basemul_add_encap_direct32_q31_tobytes_contract
.global _poly_basemul_add_encap_direct32_q31_tobytes_contract
poly_basemul_add_encap_direct32_q31_tobytes_contract:
_poly_basemul_add_encap_direct32_q31_tobytes_contract:
	LOAD_ADDR_PAGE(x4, gt_rowbitrev_lambda)
	LOAD_ADDR_OFF(x4, gt_rowbitrev_lambda)
	adr x5, Ldirect32_q31_consts
	ldr q11, [x5]
	mov x6, #24

Ldirect32_q31_loop:
	ld4 {v24.8H, v25.8H, v26.8H, v27.8H}, [x1], #64
	ld4 {v28.8H, v29.8H, v30.8H, v31.8H}, [x2], #64
	smull v1.4S, v27.4H, v31.4H
	ldr q16, [x4], #16
	smull2 v6.4S, v27.8H, v31.8H
	smull v15.4S, v25.4H, v31.4H
	ld4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x3], #64
	smull2 v23.4S, v25.8H, v31.8H
	smlal2 v23.4S, v26.8H, v30.8H
	smlal v15.4S, v26.4H, v30.4H
	uzp1 v4.8H, v1.8H, v6.8H
	smull v17.4S, v26.4H, v31.4H
	smull2 v10.4S, v26.8H, v31.8H
	smlal2 v23.4S, v27.8H, v29.8H
	smlal v17.4S, v27.4H, v30.4H
	smull v13.4S, v27.4H, v28.4H
	smull2 v14.4S, v27.8H, v28.8H
	smlal v15.4S, v27.4H, v29.4H
	smlal2 v10.4S, v27.8H, v30.8H
	mul v2.8H, v4.8H, v11.H[2]
	smlal v13.4S, v24.4H, v31.4H
	uzp1 v12.8H, v15.8H, v23.8H
	smlal2 v14.4S, v24.8H, v31.8H
	uzp1 v31.8H, v17.8H, v10.8H
	smlal v13.4S, v25.4H, v30.4H
	smlal2 v6.4S, v2.8H, v11.H[0]
	smlal v1.4S, v2.4H, v11.H[0]
	smlal2 v14.4S, v25.8H, v30.8H
	mul v5.8H, v31.8H, v11.H[2]
	uzp2 v27.8H, v1.8H, v6.8H
	smlal2 v14.4S, v26.8H, v29.8H
	smlal v13.4S, v26.4H, v29.4H
	smull v6.4S, v27.4H, v16.4H
	smull2 v3.4S, v27.8H, v16.8H
	smlal2 v3.4S, v24.8H, v30.8H
	smlal v6.4S, v24.4H, v30.4H
	smlal v6.4S, v25.4H, v29.4H
	smlal2 v3.4S, v25.8H, v29.8H
	smlal v17.4S, v5.4H, v11.H[0]
	smlal2 v10.4S, v5.8H, v11.H[0]
	mul v27.8H, v12.8H, v11.H[2]
	smlal2 v3.4S, v26.8H, v28.8H
	smlal v6.4S, v26.4H, v28.4H
	uzp2 v1.8H, v17.8H, v10.8H
	smull2 v9.4S, v1.8H, v16.8H
	smull v4.4S, v1.4H, v16.4H
	smlal2 v9.4S, v24.8H, v29.8H
	smlal v4.4S, v24.4H, v29.4H
	smlal v15.4S, v27.4H, v11.H[0]
	smlal2 v23.4S, v27.8H, v11.H[0]
	smlal2 v9.4S, v25.8H, v28.8H
	smlal v4.4S, v25.4H, v28.4H
	uzp2 v5.8H, v15.8H, v23.8H
	smull v31.4S, v5.4H, v16.4H
	smull2 v10.4S, v5.8H, v16.8H
	smlal v31.4S, v24.4H, v28.4H
	smlal2 v10.4S, v24.8H, v28.8H

	/* P0=v31/v10, P1=v4/v9, P2=v6/v3, P3=v13/v14. */
	saddw v31.4S, v31.4S, v19.4H
	saddw2 v10.4S, v10.4S, v19.8H
	sqrdmulh v19.4S, v31.4S, v11.S[2]
	mls v31.4S, v19.4S, v11.S[0]
	xtn v19.4H, v31.4S
	sqrdmulh v31.4S, v10.4S, v11.S[2]
	mls v10.4S, v31.4S, v11.S[0]
	xtn2 v19.8H, v10.4S

	saddw v4.4S, v4.4S, v20.4H
	saddw2 v9.4S, v9.4S, v20.8H
	sqrdmulh v20.4S, v4.4S, v11.S[2]
	mls v4.4S, v20.4S, v11.S[0]
	xtn v20.4H, v4.4S
	sqrdmulh v4.4S, v9.4S, v11.S[2]
	mls v9.4S, v4.4S, v11.S[0]
	xtn2 v20.8H, v9.4S

	saddw v6.4S, v6.4S, v21.4H
	saddw2 v3.4S, v3.4S, v21.8H
	sqrdmulh v21.4S, v6.4S, v11.S[2]
	mls v6.4S, v21.4S, v11.S[0]
	xtn v21.4H, v6.4S
	sqrdmulh v6.4S, v3.4S, v11.S[2]
	mls v3.4S, v6.4S, v11.S[0]
	xtn2 v21.8H, v3.4S

	saddw v13.4S, v13.4S, v22.4H
	saddw2 v14.4S, v14.4S, v22.8H
	sqrdmulh v22.4S, v13.4S, v11.S[2]
	mls v13.4S, v22.4S, v11.S[0]
	xtn v22.4H, v13.4S
	sqrdmulh v13.4S, v14.4S, v11.S[2]
	mls v14.4S, v13.4S, v11.S[0]
	xtn2 v22.8H, v14.4S

	st4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x0], #64
	subs x6, x6, #1
	b.ne Ldirect32_q31_loop

	ret

.align 4
Ldirect32_q31_consts:
	/* h[0]=q, h[2]=Montgomery qinv constant, s[2]=C32, s[0]=Q32. */
	.hword 0x0d81, 0x0000, 0xcd7f, 0xff6d
	.hword 0x7a8f, 0x0009, 0x0000, 0x0363
