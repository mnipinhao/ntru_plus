/*
 * GT encap-only poly_basemul_add direct32 Q31 byte-contract path.
 *
 * This is the fixed production poly_basemul_add endpoint used by the
 * encapsulation ciphertext path.  It keeps the selected register allocation
 * through the quartic product accumulator boundary, then replaces the product
 * Montgomery fold plus add32 finalizer with:
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

/* Instruction scheduling was generated with Slothy; release annotations removed. */

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

.global poly_basemul_add
.global _poly_basemul_add
poly_basemul_add:
_poly_basemul_add:
 sub sp, sp, #64
 stp d8, d9, [sp, #0]
 stp d10, d11, [sp, #16]
 stp d12, d13, [sp, #32]
 stp d14, d15, [sp, #48]
 LOAD_ADDR_PAGE(x4, gt_rowbitrev_lambda)
 LOAD_ADDR_OFF(x4, gt_rowbitrev_lambda)
 adr x5, Lpoly_basemul_add_consts
 ldr q11, [x5]
 mov x6, #24

Lpoly_basemul_add_loop:
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

 // live-in: x0-x4, v11, and iteration-N accumulators/c vectors
 // live-out: advanced x0-x4 and iteration-N+1 Q31 accumulators/c vectors
 // coefficient range: identical to the audited production Q31 byte contract
 // reserved physical registers: x7-x30 and sp; physical vector allocation fixed
 // Packed-16 Barrett finalizer: preserve x low16, pack Q31 quotients, then
 // apply one eight-lane halfword correction.  The region is Slothy scheduled.
 saddw2 v10.4S, v10.4S, v19.8H
 saddw v31.4S, v31.4S, v19.4H
 saddw v4.4S, v4.4S, v20.4H
 saddw2 v9.4S, v9.4S, v20.8H
 uzp1 v19.8H, v31.8H, v10.8H
 sqrdmulh v10.4S, v10.4S, v11.S[2]
 saddw v6.4S, v6.4S, v21.4H
 saddw2 v3.4S, v3.4S, v21.8H
 sqrdmulh v31.4S, v31.4S, v11.S[2]
 uzp1 v20.8H, v4.8H, v9.8H
 sqrdmulh v4.4S, v4.4S, v11.S[2]
 saddw2 v14.4S, v14.4S, v22.8H
 uzp1 v31.8H, v31.8H, v10.8H
 sqrdmulh v9.4S, v9.4S, v11.S[2]
 saddw v13.4S, v13.4S, v22.4H
 mls v19.8H, v31.8H, v11.H[0]
 uzp1 v21.8H, v6.8H, v3.8H
 uzp1 v22.8H, v13.8H, v14.8H
 sqrdmulh v6.4S, v6.4S, v11.S[2]
 uzp1 v4.8H, v4.8H, v9.8H
 ld4 {v28.8H, v29.8H, v30.8H, v31.8H}, [x2], #64
 sqrdmulh v3.4S, v3.4S, v11.S[2]
 ld4 {v24.8H, v25.8H, v26.8H, v27.8H}, [x1], #64
 sqrdmulh v14.4S, v14.4S, v11.S[2]
 sqrdmulh v13.4S, v13.4S, v11.S[2]
 uzp1 v6.8H, v6.8H, v3.8H
 uzp1 v13.8H, v13.8H, v14.8H
 mls v20.8H, v4.8H, v11.H[0]
 ldr q16, [x4], #16
 mls v21.8H, v6.8H, v11.H[0]
 mls v22.8H, v13.8H, v11.H[0]
 smull v1.4S, v27.4H, v31.4H
 smull2 v23.4S, v25.8H, v31.8H
 smull2 v6.4S, v27.8H, v31.8H
 st4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x0], #64
 smlal2 v23.4S, v26.8H, v30.8H
 smlal2 v23.4S, v27.8H, v29.8H
 ld4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x3], #64
 smull v15.4S, v25.4H, v31.4H
 smlal v15.4S, v26.4H, v30.4H
 smull v17.4S, v26.4H, v31.4H
 smlal v17.4S, v27.4H, v30.4H
 uzp1 v4.8H, v1.8H, v6.8H
 smlal v15.4S, v27.4H, v29.4H
 smull2 v10.4S, v26.8H, v31.8H
 smlal2 v10.4S, v27.8H, v30.8H
 smull2 v14.4S, v27.8H, v28.8H
 uzp1 v12.8H, v15.8H, v23.8H
 smull v13.4S, v27.4H, v28.4H
 smlal2 v14.4S, v24.8H, v31.8H
 smlal v13.4S, v24.4H, v31.4H
 smlal v13.4S, v25.4H, v30.4H
 uzp1 v31.8H, v17.8H, v10.8H
 mul v2.8H, v4.8H, v11.H[2]
 smlal2 v14.4S, v25.8H, v30.8H
 smlal v13.4S, v26.4H, v29.4H
 smlal2 v14.4S, v26.8H, v29.8H
 smlal v1.4S, v2.4H, v11.H[0]
 smlal2 v6.4S, v2.8H, v11.H[0]
 mul v5.8H, v31.8H, v11.H[2]
 uzp2 v27.8H, v1.8H, v6.8H
 smlal2 v10.4S, v5.8H, v11.H[0]
 smlal v17.4S, v5.4H, v11.H[0]
 smull v6.4S, v27.4H, v16.4H
 smull2 v3.4S, v27.8H, v16.8H
 smlal v6.4S, v24.4H, v30.4H
 uzp2 v1.8H, v17.8H, v10.8H
 smlal2 v3.4S, v24.8H, v30.8H
 smlal v6.4S, v25.4H, v29.4H
 mul v27.8H, v12.8H, v11.H[2]
 smlal2 v3.4S, v25.8H, v29.8H
 smlal v6.4S, v26.4H, v28.4H
 smull v4.4S, v1.4H, v16.4H
 smlal2 v23.4S, v27.8H, v11.H[0]
 smlal v15.4S, v27.4H, v11.H[0]
 smull2 v9.4S, v1.8H, v16.8H
 smlal2 v3.4S, v26.8H, v28.8H
 smlal v4.4S, v24.4H, v29.4H
 smlal2 v9.4S, v24.8H, v29.8H
 smlal v4.4S, v25.4H, v28.4H
 uzp2 v5.8H, v15.8H, v23.8H
 smlal2 v9.4S, v25.8H, v28.8H
 smull v31.4S, v5.4H, v16.4H
 smlal v31.4S, v24.4H, v28.4H
 smull2 v10.4S, v5.8H, v16.8H
 smlal2 v10.4S, v24.8H, v28.8H
 saddw v31.4S, v31.4S, v19.4H
 saddw2 v10.4S, v10.4S, v19.8H
 uzp1 v19.8H, v31.8H, v10.8H
 saddw v4.4S, v4.4S, v20.4H
 sqrdmulh v31.4S, v31.4S, v11.S[2]
 saddw2 v9.4S, v9.4S, v20.8H
 sqrdmulh v10.4S, v10.4S, v11.S[2]
 uzp1 v31.8H, v31.8H, v10.8H
 mls v19.8H, v31.8H, v11.H[0]
 saddw v6.4S, v6.4S, v21.4H
 uzp1 v20.8H, v4.8H, v9.8H
 sqrdmulh v4.4S, v4.4S, v11.S[2]
 sqrdmulh v9.4S, v9.4S, v11.S[2]
 saddw2 v3.4S, v3.4S, v21.8H
 uzp1 v4.8H, v4.8H, v9.8H
 uzp1 v21.8H, v6.8H, v3.8H
 sqrdmulh v6.4S, v6.4S, v11.S[2]
 saddw2 v14.4S, v14.4S, v22.8H
 mls v20.8H, v4.8H, v11.H[0]
 saddw v13.4S, v13.4S, v22.4H
 sqrdmulh v3.4S, v3.4S, v11.S[2]
 uzp1 v22.8H, v13.8H, v14.8H
 uzp1 v6.8H, v6.8H, v3.8H
 sqrdmulh v14.4S, v14.4S, v11.S[2]
 sqrdmulh v13.4S, v13.4S, v11.S[2]
 mls v21.8H, v6.8H, v11.H[0]
 uzp1 v13.8H, v13.8H, v14.8H
 mls v22.8H, v13.8H, v11.H[0]
 st4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x0], #64

 subs x6, x6, #2
 b.ne Lpoly_basemul_add_loop

 ldp d14, d15, [sp, #48]
 ldp d12, d13, [sp, #32]
 ldp d10, d11, [sp, #16]
 ldp d8, d9, [sp, #0]
 add sp, sp, #64
 ret

.align 4
Lpoly_basemul_add_consts:
 /* h[0]=q, h[2]=Montgomery qinv constant, s[2]=C32, s[0]=Q32. */
 .hword 0x0d81, 0x0000, 0xcd7f, 0xff6d
 .hword 0x7a8f, 0x0009, 0x0000, 0x0363
