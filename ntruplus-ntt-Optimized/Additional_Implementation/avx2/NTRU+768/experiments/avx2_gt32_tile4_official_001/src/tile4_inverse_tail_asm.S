.text

.macro CENTER value
	vpmulhrsw %ymm14, \value, %ymm13
	vpmullw %ymm15, %ymm13, %ymm13
	vpsubw %ymm13, \value, \value
.endm

.macro CENTER_CANONICAL value
	CENTER \value
	vpcmpgtw %ymm12, \value, %ymm13
	vpand %ymm15, %ymm13, %ymm13
	vpsubw %ymm13, \value, \value
	vpcmpgtw \value, %ymm11, %ymm13
	vpand %ymm15, %ymm13, %ymm13
	vpaddw %ymm13, \value, \value
.endm

/* In-place inverse DFT3.  t0..t4 must not alias r0..r2. */
.macro IDFT3 r0,r1,r2,t0,t1,t2,t3,t4
	/* t0 = Mont(r1,w2), t1 = Mont(r2,w). */
	vpmullw .Ltail_w2_qinv(%rip), \r1, \t1
	vpmulhw .Ltail_w2_factor(%rip), \r1, \t0
	vpmulhw %ymm15, \t1, \t1
	vpsubw \t1, \t0, \t0
	vpmullw .Ltail_w_qinv(%rip), \r2, \t2
	vpmulhw .Ltail_w_factor(%rip), \r2, \t1
	vpmulhw %ymm15, \t2, \t2
	vpsubw \t2, \t1, \t1
	vpaddw \t1, \t0, \t0
	vpaddw \r0, \t0, \t0

	/* t1 = Mont(r1,w), t2 = Mont(r2,w2). */
	vpmullw .Ltail_w_qinv(%rip), \r1, \t2
	vpmulhw .Ltail_w_factor(%rip), \r1, \t1
	vpmulhw %ymm15, \t2, \t2
	vpsubw \t2, \t1, \t1
	vpmullw .Ltail_w2_qinv(%rip), \r2, \t3
	vpmulhw .Ltail_w2_factor(%rip), \r2, \t2
	vpmulhw %ymm15, \t3, \t3
	vpsubw \t3, \t2, \t2
	vpaddw \t2, \t1, \t1
	vpaddw \r0, \t1, \t1

	/* t2 = r0+r1+r2, then commit all three outputs. */
	vpaddw \r1, \r0, \t2
	vpaddw \r2, \t2, \t2
	vmovdqa \t2, \r0
	vmovdqa \t0, \r1
	vmovdqa \t1, \r2
.endm

.macro BLEND3 r0,r1,r2,t0,t1,t2
	vpblendd $0x0c, \r1, \r0, \t0
	vpblendd $0x30, \r2, \t0, \t0
	vpblendd $0x0c, \r0, \r2, \t1
	vpblendd $0x30, \r1, \t1, \t1
	vpblendd $0x0c, \r2, \r1, \t2
	vpblendd $0x30, \r0, \t2, \t2
	vmovdqa \t0, \r0
	vmovdqa \t1, \r1
	vmovdqa \t2, \r2
.endm

/* Apply one 2x2 branch matrix and immediately retire both output vectors. */
.macro MATRIX_PAIR y0,y1,matrix_offset,out_low,out_high
	vpmullw .Ltail_matrix_qinv+\matrix_offset(%rip), \y0, %ymm7
	vpmulhw .Ltail_matrix_factor+\matrix_offset(%rip), \y0, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm7, %ymm6, %ymm6
	vpmullw .Ltail_matrix_qinv+\matrix_offset+32(%rip), \y1, %ymm8
	vpmulhw .Ltail_matrix_factor+\matrix_offset+32(%rip), \y1, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm7
	vpaddw %ymm7, %ymm6, %ymm6
	CENTER_CANONICAL %ymm6
	vmovdqu %ymm6, \out_low(%rdi)

	vpmullw .Ltail_matrix_qinv+\matrix_offset+64(%rip), \y0, %ymm7
	vpmulhw .Ltail_matrix_factor+\matrix_offset+64(%rip), \y0, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm7, %ymm6, %ymm6
	vpmullw .Ltail_matrix_qinv+\matrix_offset+96(%rip), \y1, %ymm8
	vpmulhw .Ltail_matrix_factor+\matrix_offset+96(%rip), \y1, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm7
	vpaddw %ymm7, %ymm6, %ymm6
	CENTER_CANONICAL %ymm6
	vmovdqu %ymm6, \out_high(%rdi)
.endm

.macro TAIL_GROUP group,a0,a1,b0,b1,c0,c1
	vmovdqu 0+32*\group(%rsi), %ymm0
	vmovdqu 512+32*\group(%rsi), %ymm1
	vmovdqu 1024+32*\group(%rsi), %ymm2
	vmovdqu 256+32*\group(%rsi), %ymm3
	vmovdqu 768+32*\group(%rsi), %ymm4
	vmovdqu 1280+32*\group(%rsi), %ymm5
	CENTER %ymm0
	CENTER %ymm1
	CENTER %ymm2
	CENTER %ymm3
	CENTER %ymm4
	CENTER %ymm5
	IDFT3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	IDFT3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
	BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
	MATRIX_PAIR \a0,\a1,384*\group+0,0+32*\group,768+32*\group
	MATRIX_PAIR \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
	MATRIX_PAIR \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm

.p2align 5
.globl gt32_tile4_inverse_tail_asm_rminus1
.type gt32_tile4_inverse_tail_asm_rminus1,@function
gt32_tile4_inverse_tail_asm_rminus1:
	vmovdqa .Ltail_q(%rip), %ymm15
	vmovdqa .Ltail_center10(%rip), %ymm14
	vmovdqa .Ltail_half_q(%rip), %ymm12
	vmovdqa .Ltail_minus_half_q(%rip), %ymm11
	TAIL_GROUP 0,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
	TAIL_GROUP 1,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
	TAIL_GROUP 2,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3
	TAIL_GROUP 3,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
	TAIL_GROUP 4,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
	TAIL_GROUP 5,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3
	TAIL_GROUP 6,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
	TAIL_GROUP 7,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_asm_rminus1,.-gt32_tile4_inverse_tail_asm_rminus1

.section .rodata
.include "generated/tile4_inverse_tail_constants.inc"
.section .note.GNU-stack,"",@progbits
