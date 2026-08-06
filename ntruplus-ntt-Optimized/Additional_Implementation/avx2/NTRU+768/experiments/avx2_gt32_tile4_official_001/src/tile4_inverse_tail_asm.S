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

/* Algebraically equivalent IDFT3 with one Montgomery multiplication. */
.macro IDFT3_ONE r0,r1,r2,t0,t1,t2,t3,t4
	vpsubw \r2, \r1, \t0
	vpmullw .Ltail_w_qinv(%rip), \t0, \t2
	vpmulhw .Ltail_w_factor(%rip), \t0, \t1
	vpmulhw %ymm15, \t2, \t2
	vpsubw \t2, \t1, \t1
	vpaddw \r1, \r0, \t2
	vpaddw \r2, \t2, \t2
	vpsubw \r1, \r0, \t3
	vpsubw \t1, \t3, \t3
	vpsubw \r2, \r0, \t4
	vpaddw \t1, \t4, \t4
	vmovdqa \t2, \r0
	vmovdqa \t3, \r1
	vmovdqa \t4, \r2
.endm

/* One center on r1+r2; raw difference and all outputs remain int16-safe. */
.macro IDFT3_ONE_REDUCED_CENTER r0,r1,r2,t0,t1,t2,t3,t4
	vpaddw \r2, \r1, \t0
	CENTER \t0
	vpsubw \r2, \r1, \t1
	vpmullw .Ltail_w_qinv(%rip), \t1, \t3
	vpmulhw .Ltail_w_factor(%rip), \t1, \t2
	vpmulhw %ymm15, \t3, \t3
	vpsubw \t3, \t2, \t2
	vpsubw \r1, \r0, \t3
	vpsubw \t2, \t3, \t3
	vpsubw \r2, \r0, \t4
	vpaddw \t2, \t4, \t4
	vpaddw \t0, \r0, \r0
	vmovdqa \t3, \r1
	vmovdqa \t4, \r2
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

.macro MATRIX_PAIR_RELAXED y0,y1,matrix_offset,out_low,out_high
	vpmullw .Ltail_matrix_qinv+\matrix_offset(%rip), \y0, %ymm7
	vpmulhw .Ltail_matrix_factor+\matrix_offset(%rip), \y0, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm7, %ymm6, %ymm6
	vpmullw .Ltail_matrix_qinv+\matrix_offset+32(%rip), \y1, %ymm8
	vpmulhw .Ltail_matrix_factor+\matrix_offset+32(%rip), \y1, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm7
	vpaddw %ymm7, %ymm6, %ymm6
	CENTER %ymm6
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
	CENTER %ymm6
	vmovdqu %ymm6, \out_high(%rdi)
.endm

/* Two normalized untwists plus one top-branch correction. */
.macro MATRIX3_PAIR y0,y1,matrix_offset,out_low,out_high,center_op
	vpmullw .Ltail_matrix3_qinv+\matrix_offset(%rip), \y0, %ymm7
	vpmulhw .Ltail_matrix3_factor+\matrix_offset(%rip), \y0, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm7, %ymm6, %ymm6
	vpmullw .Ltail_matrix3_qinv+\matrix_offset+32(%rip), \y1, %ymm8
	vpmulhw .Ltail_matrix3_factor+\matrix_offset+32(%rip), \y1, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm7
	vpaddw %ymm7, %ymm6, %ymm8
	vpsubw %ymm7, %ymm6, %ymm9
	vpmullw .Ltail_matrix3_qinv+\matrix_offset+64(%rip), %ymm9, %ymm10
	vpmulhw .Ltail_matrix3_factor+\matrix_offset+64(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm6
	vpaddw %ymm9, %ymm9, %ymm7
	\center_op %ymm6
	\center_op %ymm7
	vmovdqu %ymm6, \out_low(%rdi)
	vmovdqu %ymm7, \out_high(%rdi)
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

.macro LOAD_CENTERED_GROUP group
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
.endm

.macro LOAD_RAW_GROUP group
	vmovdqu 0+32*\group(%rsi), %ymm0
	vmovdqu 512+32*\group(%rsi), %ymm1
	vmovdqu 1024+32*\group(%rsi), %ymm2
	vmovdqu 256+32*\group(%rsi), %ymm3
	vmovdqu 768+32*\group(%rsi), %ymm4
	vmovdqu 1280+32*\group(%rsi), %ymm5
.endm

.macro TAIL_GROUP_T1 group,a0,a1,b0,b1,c0,c1
	LOAD_CENTERED_GROUP \group
	IDFT3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	IDFT3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
	BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
	MATRIX_PAIR_RELAXED \a0,\a1,384*\group+0,0+32*\group,768+32*\group
	MATRIX_PAIR_RELAXED \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
	MATRIX_PAIR_RELAXED \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm

.macro TAIL_GROUP_T2 group,a0,a1,b0,b1,c0,c1
	LOAD_CENTERED_GROUP \group
	IDFT3_ONE %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	IDFT3_ONE %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
	BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
	MATRIX_PAIR \a0,\a1,384*\group+0,0+32*\group,768+32*\group
	MATRIX_PAIR \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
	MATRIX_PAIR \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm

.macro TAIL_GROUP_T3 group,a0,a1,b0,b1,c0,c1
	LOAD_RAW_GROUP \group
	IDFT3_ONE_REDUCED_CENTER %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	IDFT3_ONE_REDUCED_CENTER %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
	BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
	MATRIX_PAIR \a0,\a1,384*\group+0,0+32*\group,768+32*\group
	MATRIX_PAIR \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
	MATRIX_PAIR \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm

.macro TAIL_GROUP_T3_RELAXED group,a0,a1,b0,b1,c0,c1
	LOAD_RAW_GROUP \group
	IDFT3_ONE_REDUCED_CENTER %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	IDFT3_ONE_REDUCED_CENTER %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
	BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
	MATRIX_PAIR_RELAXED \a0,\a1,384*\group+0,0+32*\group,768+32*\group
	MATRIX_PAIR_RELAXED \b0,\b1,384*\group+128,256+32*\group,1024+32*\group
	MATRIX_PAIR_RELAXED \c0,\c1,384*\group+256,512+32*\group,1280+32*\group
.endm

.macro TAIL_GROUP_T4 group,a0,a1,b0,b1,c0,c1,center_op
	LOAD_RAW_GROUP \group
	IDFT3_ONE_REDUCED_CENTER %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	IDFT3_ONE_REDUCED_CENTER %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10
	BLEND3 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
	BLEND3 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
	MATRIX3_PAIR \a0,\a1,288*\group+0,0+32*\group,768+32*\group,\center_op
	MATRIX3_PAIR \b0,\b1,288*\group+96,256+32*\group,1024+32*\group,\center_op
	MATRIX3_PAIR \c0,\c1,288*\group+192,512+32*\group,1280+32*\group,\center_op
.endm

.macro TAIL_PROLOGUE
	vmovdqa .Ltail_q(%rip), %ymm15
	vmovdqa .Ltail_center10(%rip), %ymm14
	vmovdqa .Ltail_half_q(%rip), %ymm12
	vmovdqa .Ltail_minus_half_q(%rip), %ymm11
.endm

.macro RUN_8 macro_name
	\macro_name 0,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
	\macro_name 1,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
	\macro_name 2,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3
	\macro_name 3,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
	\macro_name 4,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
	\macro_name 5,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3
	\macro_name 6,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5
	\macro_name 7,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4
.endm

.macro RUN_8_EXTRA macro_name extra
	\macro_name 0,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5,\extra
	\macro_name 1,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4,\extra
	\macro_name 2,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3,\extra
	\macro_name 3,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5,\extra
	\macro_name 4,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4,\extra
	\macro_name 5,%ymm1,%ymm4,%ymm2,%ymm5,%ymm0,%ymm3,\extra
	\macro_name 6,%ymm0,%ymm3,%ymm1,%ymm4,%ymm2,%ymm5,\extra
	\macro_name 7,%ymm2,%ymm5,%ymm0,%ymm3,%ymm1,%ymm4,\extra
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

.p2align 5
.globl gt32_tile4_inverse_tail_t1_relaxed_asm
.type gt32_tile4_inverse_tail_t1_relaxed_asm,@function
gt32_tile4_inverse_tail_t1_relaxed_asm:
	TAIL_PROLOGUE
	RUN_8 TAIL_GROUP_T1
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_t1_relaxed_asm,.-gt32_tile4_inverse_tail_t1_relaxed_asm

.p2align 5
.globl gt32_tile4_inverse_tail_t2_one_mont_asm
.type gt32_tile4_inverse_tail_t2_one_mont_asm,@function
gt32_tile4_inverse_tail_t2_one_mont_asm:
	TAIL_PROLOGUE
	RUN_8 TAIL_GROUP_T2
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_t2_one_mont_asm,.-gt32_tile4_inverse_tail_t2_one_mont_asm

.p2align 5
.globl gt32_tile4_inverse_tail_t3_reduced_center_asm
.type gt32_tile4_inverse_tail_t3_reduced_center_asm,@function
gt32_tile4_inverse_tail_t3_reduced_center_asm:
	TAIL_PROLOGUE
	RUN_8 TAIL_GROUP_T3
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_t3_reduced_center_asm,.-gt32_tile4_inverse_tail_t3_reduced_center_asm

.p2align 5
.globl gt32_tile4_inverse_tail_t3_relaxed_control_asm
.type gt32_tile4_inverse_tail_t3_relaxed_control_asm,@function
gt32_tile4_inverse_tail_t3_relaxed_control_asm:
	TAIL_PROLOGUE
	RUN_8 TAIL_GROUP_T3_RELAXED
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_t3_relaxed_control_asm,.-gt32_tile4_inverse_tail_t3_relaxed_control_asm

.p2align 5
.globl gt32_tile4_inverse_tail_t4_matrix3_asm
.type gt32_tile4_inverse_tail_t4_matrix3_asm,@function
gt32_tile4_inverse_tail_t4_matrix3_asm:
	TAIL_PROLOGUE
	RUN_8_EXTRA TAIL_GROUP_T4,CENTER_CANONICAL
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_t4_matrix3_asm,.-gt32_tile4_inverse_tail_t4_matrix3_asm

.p2align 5
.globl gt32_tile4_inverse_tail_champion_private_asm
.type gt32_tile4_inverse_tail_champion_private_asm,@function
gt32_tile4_inverse_tail_champion_private_asm:
	TAIL_PROLOGUE
	RUN_8_EXTRA TAIL_GROUP_T4,CENTER
	vzeroupper
	ret
.size gt32_tile4_inverse_tail_champion_private_asm,.-gt32_tile4_inverse_tail_champion_private_asm

.section .rodata
.include "generated/tile4_inverse_tail_constants.inc"
.section .note.GNU-stack,"",@progbits
