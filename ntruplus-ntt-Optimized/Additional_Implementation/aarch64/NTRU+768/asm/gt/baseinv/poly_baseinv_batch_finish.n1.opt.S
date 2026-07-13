/*
 * Slothy-scheduled GT batch baseinv finish loop.
 *
	 * ABI:
	 *   x0 = dst block-major buffer, 24 blocks of 32 int16 coefficients
	 *   x1 = den_inv buffer, 24 vectors of 8 int16 coefficients
	 *   preserves d8-d15 as required by the AArch64 C ABI
	 *
	 * This inlines the one-block schedule from baseinv_batch_finish.n1.opt.S in a
	 * 24-block loop so production avoids calling the microkernel once per block.
 */

.text
.align 2

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif

.global C_SYM(baseinv_batch_finish24_n1_asm)
baseinv_batch_finish24_n1_asm:
#ifdef __APPLE__
	.global _baseinv_batch_finish24_n1_asm
	_baseinv_batch_finish24_n1_asm:
	#endif
		sub sp, sp, #64
		stp d8, d9, [sp, #0]
		stp d10, d11, [sp, #16]
		stp d12, d13, [sp, #32]
		stp d14, d15, [sp, #48]

		adr x2, Lbaseinv_finish_loop_consts
		ld1 {v0.8h}, [x2]
		mov x3, #24

Lbaseinv_finish24_loop:
	ld4 {v11.8h, v12.8h, v13.8h, v14.8h}, [x0]
	ldr q16, [x1], #16
	movi v20.8h, #0
	sub v18.8h, v20.8h, v16.8h
	smull v10.4s, v14.4h, v18.4h
	smull2 v5.4s, v14.8h, v18.8h
	smull2 v14.4s, v11.8h, v16.8h
	smull v1.4s, v11.4h, v16.4h
	smull2 v9.4s, v12.8h, v18.8h
	smull v28.4s, v12.4h, v18.4h
	uzp1 v24.8h, v10.8h, v5.8h
	smull2 v19.4s, v13.8h, v16.8h
	smull v2.4s, v13.4h, v16.4h
	uzp1 v30.8h, v1.8h, v14.8h
	mul v24.8h, v24.8h, v0.h[2]
	uzp1 v22.8h, v28.8h, v9.8h
	mul v31.8h, v30.8h, v0.h[2]
	uzp1 v30.8h, v2.8h, v19.8h
	mul v26.8h, v22.8h, v0.h[2]
	mul v11.8h, v30.8h, v0.h[2]
	smlal v1.4s, v31.4h, v0.h[0]
	smlal2 v9.4s, v26.8h, v0.h[0]
	smlal v28.4s, v26.4h, v0.h[0]
	smlal2 v19.4s, v11.8h, v0.h[0]
	smlal v2.4s, v11.4h, v0.h[0]
	smlal v10.4s, v24.4h, v0.h[0]
	smlal2 v5.4s, v24.8h, v0.h[0]
	uzp2 v6.8h, v28.8h, v9.8h
	smlal2 v14.4s, v31.8h, v0.h[0]
	uzp2 v7.8h, v2.8h, v19.8h
	uzp2 v8.8h, v10.8h, v5.8h
	uzp2 v5.8h, v1.8h, v14.8h
	st4 {v5.8h, v6.8h, v7.8h, v8.8h}, [x0], #64

		subs x3, x3, #1
		b.ne Lbaseinv_finish24_loop

		ldp d8, d9, [sp, #0]
		ldp d10, d11, [sp, #16]
		ldp d12, d13, [sp, #32]
		ldp d14, d15, [sp, #48]
		add sp, sp, #64
		ret

	.align 4
Lbaseinv_finish_loop_consts:
	.hword 0x0d81, 0x0000, 0xcd7f, 0x0000
	.hword 0x0000, 0x0000, 0x0000, 0x0000
