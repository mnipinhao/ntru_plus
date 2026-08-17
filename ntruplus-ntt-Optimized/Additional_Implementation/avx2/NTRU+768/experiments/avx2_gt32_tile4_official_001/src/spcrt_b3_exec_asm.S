/* GT32-SPCRT-B3-EXEC-001: natural-j/AUTO11 Forward and SP-native B3. */

	.text

	.macro SP_MONT lo,hi,tmp,qinv,factor,offset
	vpmullw \qinv+\offset(%rip), \hi, \tmp
	vpmulhw \factor+\offset(%rip), \hi, \hi
	vpmulhw .Lspcrt_q(%rip), \tmp, \tmp
	vpsubw \tmp, \hi, \hi
	vpsubw \hi, \lo, \tmp
	vpaddw \hi, \lo, \lo
	vmovdqa \tmp, \hi
	.endm

	/* R2 shares the complete packet producer.  A single entry selector picks
	 * a raw or compile-time repaired terminal; only the six-row tail is
	 * duplicated. */
	.macro SP_FORWARD_R2_SHARED
	.section .text.gt32_spcrt_forward_r2_shared,"ax",@progbits
	.p2align 6
	.globl gt32_spcrt_forward_raw_r2_shared_asm
	.type gt32_spcrt_forward_raw_r2_shared_asm,@function
gt32_spcrt_forward_raw_r2_shared_asm:
	xorl %eax, %eax
	jmp .Lspcrt_r2_shared
	.size gt32_spcrt_forward_raw_r2_shared_asm,.-gt32_spcrt_forward_raw_r2_shared_asm
	.p2align 5
	.globl gt32_spcrt_forward_a_repaired_r2_shared_asm
	.type gt32_spcrt_forward_a_repaired_r2_shared_asm,@function
gt32_spcrt_forward_a_repaired_r2_shared_asm:
	movl $1, %eax
.Lspcrt_r2_shared:
	movq %rsp, %rdx
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1600, %rsp
	movq %rdx, 1544(%rsp)
	SP_INPUT_SLAB 0,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 1,%ymm5,%ymm4,%ymm6
	SP_INPUT_SLAB 2,%ymm6,%ymm5,%ymm4
	SP_INPUT_SLAB 3,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 4,%ymm5,%ymm4,%ymm6
	SP_INPUT_SLAB 5,%ymm6,%ymm5,%ymm4
	SP_INPUT_SLAB 6,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 7,%ymm5,%ymm4,%ymm6
	testl %eax, %eax
	je .Lspcrt_r2_raw_tail
	vmovdqa .Lspcrt_center10(%rip), %ymm12
	vmovdqa .Lspcrt_q(%rip), %ymm13
	SP_ROW_SCHEDULED 0,0,2
	SP_ROW_SCHEDULED 256,256,0
	SP_ROW_SCHEDULED 512,512,0
	SP_ROW_SCHEDULED 768,768,2
	SP_ROW_SCHEDULED 1024,1024,0
	SP_ROW_SCHEDULED 1280,1280,0
	jmp .Lspcrt_r2_done
.Lspcrt_r2_raw_tail:
	SP_ROW_SCHEDULED 0,0,0
	SP_ROW_SCHEDULED 256,256,0
	SP_ROW_SCHEDULED 512,512,0
	SP_ROW_SCHEDULED 768,768,0
	SP_ROW_SCHEDULED 1024,1024,0
	SP_ROW_SCHEDULED 1280,1280,0
.Lspcrt_r2_done:
	movq 1544(%rsp), %rsp
	vzeroupper
	ret
	.size gt32_spcrt_forward_a_repaired_r2_shared_asm,.-gt32_spcrt_forward_a_repaired_r2_shared_asm
	.endm

	.macro SP_MONT4 lo0,hi0,lo1,hi1,lo2,hi2,lo3,hi3,t0,t1,t2,t3,qinv,factor
	vpmullw \qinv+0(%rip), \hi0, \t0
	vpmullw \qinv+32(%rip), \hi1, \t1
	vpmullw \qinv+64(%rip), \hi2, \t2
	vpmullw \qinv+96(%rip), \hi3, \t3
	vpmulhw \factor+0(%rip), \hi0, \hi0
	vpmulhw \factor+32(%rip), \hi1, \hi1
	vpmulhw \factor+64(%rip), \hi2, \hi2
	vpmulhw \factor+96(%rip), \hi3, \hi3
	vpmulhw .Lspcrt_q(%rip), \t0, \t0
	vpmulhw .Lspcrt_q(%rip), \t1, \t1
	vpmulhw .Lspcrt_q(%rip), \t2, \t2
	vpmulhw .Lspcrt_q(%rip), \t3, \t3
	vpsubw \t0, \hi0, \hi0
	vpsubw \t1, \hi1, \hi1
	vpsubw \t2, \hi2, \hi2
	vpsubw \t3, \hi3, \hi3
	vpsubw \hi0, \lo0, \t0
	vpsubw \hi1, \lo1, \t1
	vpsubw \hi2, \lo2, \t2
	vpsubw \hi3, \lo3, \t3
	vpaddw \hi0, \lo0, \lo0
	vpaddw \hi1, \lo1, \lo1
	vpaddw \hi2, \lo2, \lo2
	vpaddw \hi3, \lo3, \lo3
	vmovdqa \t0, \hi0
	vmovdqa \t1, \hi1
	vmovdqa \t2, \hi2
	vmovdqa \t3, \hi3
	.endm

	.macro SP_RAW lo,hi
	vpaddw \hi, \lo, \lo
	vpaddw \hi, \hi, \hi
	vpsubw \hi, \lo, \hi
	.endm

	.macro SP_FORM_PAIR b0,b1,tmp,vector
	vmovdqu 32*\vector(%rsi), \b0
	vmovdqu 768+32*\vector(%rsi), \b1
	vpmullw .Lspcrt_top_raw(%rip), \b1, \tmp
	vpaddw \b0, \b1, \b1
	vpsubw \tmp, \b1, \b1
	vpaddw \tmp, \b0, \b0
	vpmullw .Ln32_fwd_twist_qinv+64*\vector(%rip), \b0, \tmp
	vpmulhw .Ln32_fwd_twist_factor+64*\vector(%rip), \b0, \b0
	vpmulhw .Lspcrt_q(%rip), \tmp, \tmp
	vpsubw \tmp, \b0, \b0
	vpmullw .Ln32_fwd_twist_qinv+64*\vector+32(%rip), \b1, \tmp
	vpmulhw .Ln32_fwd_twist_factor+64*\vector+32(%rip), \b1, \b1
	vpmulhw .Lspcrt_q(%rip), \tmp, \tmp
	vpsubw \tmp, \b1, \b1
	.endm

	/* Build all three same-position CRT mosaics from source blocks S0/S1/S2. */
	.macro SP_MOSAICS s0,s1,s2
	vpblendd $0x0c, \s1, \s0, %ymm3
	vpblendd $0x30, \s2, %ymm3, %ymm4
	vpblendd $0x0c, \s2, \s1, %ymm3
	vpblendd $0x30, \s0, %ymm3, %ymm5
	vpblendd $0x0c, \s0, \s2, %ymm3
	vpblendd $0x30, \s1, %ymm3, %ymm6
	.endm

	/* DFT3 with candidate root W3^2.  Outputs row0/1/2 in ymm12/13/14. */
	.macro SP_DFT3 a,b,c
	vpsubw \c, \b, %ymm11
	vpmullw .Lspcrt_omega2_qinv(%rip), %ymm11, %ymm12
	vpmulhw .Lspcrt_omega2_factor(%rip), %ymm11, %ymm11
	vpmulhw .Lspcrt_q(%rip), %ymm12, %ymm12
	vpsubw %ymm12, %ymm11, %ymm11
	vpaddw \b, \a, %ymm12
	vpaddw \c, %ymm12, %ymm12
	vpsubw \c, \a, %ymm13
	vpaddw %ymm11, %ymm13, %ymm13
	vpsubw \b, \a, %ymm14
	vpsubw %ymm11, %ymm14, %ymm14
	.endm

	.macro SP_ROUTE_BRANCH s0,s1,s2,a,b,c,branch,t
	SP_MOSAICS \s0,\s1,\s2
	SP_DFT3 \a,\b,\c
	vmovdqu %ymm12, (768*\branch+32*\t)(%rsp)
	vmovdqu %ymm13, (768*\branch+256+32*\t)(%rsp)
	vmovdqu %ymm14, (768*\branch+512+32*\t)(%rsp)
	.endm

	.macro SP_INPUT_SLAB t,p0,p1,p2
	SP_FORM_PAIR %ymm0,%ymm8,%ymm15,\t
	SP_FORM_PAIR %ymm1,%ymm9,%ymm15,(\t+8)
	SP_FORM_PAIR %ymm2,%ymm10,%ymm15,(\t+16)
	SP_ROUTE_BRANCH %ymm0,%ymm1,%ymm2,\p0,\p1,\p2,0,\t
	SP_ROUTE_BRANCH %ymm8,%ymm9,%ymm10,\p0,\p1,\p2,1,\t
	.endm

	.macro SP_HALF_PAIR v0,v1,offset
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw .Lspcrt_s4_qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw .Lspcrt_s4_factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw .Lspcrt_q(%rip), %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

	.macro SP_QWORD_PAIR v0,v1,offset
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpmullw .Lspcrt_s5_qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw .Lspcrt_s5_factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw .Lspcrt_q(%rip), %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro SP_CENTER value
	vpmulhrsw .Lspcrt_center10(%rip), \value, %ymm8
	vpmullw .Lspcrt_q(%rip), %ymm8, %ymm8
	vpsubw %ymm8, \value, \value
	.endm

	.macro SP_CENTER4_MEM v0,v1,v2,v3,t0,t1,t2,t3
	vpmulhrsw .Lspcrt_center10(%rip), \v0, \t0
	vpmulhrsw .Lspcrt_center10(%rip), \v1, \t1
	vpmulhrsw .Lspcrt_center10(%rip), \v2, \t2
	vpmulhrsw .Lspcrt_center10(%rip), \v3, \t3
	vpmullw .Lspcrt_q(%rip), \t0, \t0
	vpmullw .Lspcrt_q(%rip), \t1, \t1
	vpmullw .Lspcrt_q(%rip), \t2, \t2
	vpmullw .Lspcrt_q(%rip), \t3, \t3
	vpsubw \t0, \v0, \v0
	vpsubw \t1, \v1, \v1
	vpsubw \t2, \v2, \v2
	vpsubw \t3, \v3, \v3
	.endm

	.macro SP_CENTER4_REG v0,v1,v2,v3,t0,t1,t2,t3
	vpmulhrsw %ymm12, \v0, \t0
	vpmulhrsw %ymm12, \v1, \t1
	vpmulhrsw %ymm12, \v2, \t2
	vpmulhrsw %ymm12, \v3, \t3
	vpmullw %ymm13, \t0, \t0
	vpmullw %ymm13, \t1, \t1
	vpmullw %ymm13, \t2, \t2
	vpmullw %ymm13, \t3, \t3
	vpsubw \t0, \v0, \v0
	vpsubw \t1, \v1, \v1
	vpsubw \t2, \v2, \v2
	vpsubw \t3, \v3, \v3
	.endm

	.macro SP_ROW scratch,output,repair
	vmovdqu \scratch+0(%rsp), %ymm0
	vmovdqu \scratch+32(%rsp), %ymm1
	vmovdqu \scratch+64(%rsp), %ymm2
	vmovdqu \scratch+96(%rsp), %ymm3
	vmovdqu \scratch+128(%rsp), %ymm4
	vmovdqu \scratch+160(%rsp), %ymm5
	vmovdqu \scratch+192(%rsp), %ymm6
	vmovdqu \scratch+224(%rsp), %ymm7
	SP_RAW %ymm0,%ymm4
	SP_RAW %ymm1,%ymm5
	SP_RAW %ymm2,%ymm6
	SP_RAW %ymm3,%ymm7
	SP_MONT4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Lspcrt_s2_qinv,.Lspcrt_s2_factor
	SP_MONT4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Lspcrt_s3_qinv,.Lspcrt_s3_factor
	SP_HALF_PAIR %ymm0,%ymm1,0
	SP_HALF_PAIR %ymm2,%ymm3,32
	SP_HALF_PAIR %ymm4,%ymm5,64
	SP_HALF_PAIR %ymm6,%ymm7,96
	SP_QWORD_PAIR %ymm0,%ymm1,0
	SP_QWORD_PAIR %ymm2,%ymm3,32
	SP_QWORD_PAIR %ymm4,%ymm5,64
	SP_QWORD_PAIR %ymm6,%ymm7,96
	.if \repair
	cmpl $0, 1536(%rsp)
	je .Lsp_no_center\@
	SP_CENTER %ymm0
	SP_CENTER %ymm1
	SP_CENTER %ymm2
	SP_CENTER %ymm3
	SP_CENTER %ymm4
	SP_CENTER %ymm5
	SP_CENTER %ymm6
	SP_CENTER %ymm7
.Lsp_no_center\@:
	.endif
	vmovdqu %ymm0, \output+0(%r11)
	vmovdqu %ymm1, \output+32(%r11)
	vmovdqu %ymm2, \output+64(%r11)
	vmovdqu %ymm3, \output+96(%r11)
	vmovdqu %ymm4, \output+128(%r11)
	vmovdqu %ymm5, \output+160(%r11)
	vmovdqu %ymm6, \output+192(%r11)
	vmovdqu %ymm7, \output+224(%r11)
	.endm

	/* Compile-time repaired row: mode 1 keeps memory constants, mode 2 uses
	 * center10/q resident in ymm12/ymm13. */
	.macro SP_ROW_SCHEDULED scratch,output,mode
	vmovdqu \scratch+0(%rsp), %ymm0
	vmovdqu \scratch+32(%rsp), %ymm1
	vmovdqu \scratch+64(%rsp), %ymm2
	vmovdqu \scratch+96(%rsp), %ymm3
	vmovdqu \scratch+128(%rsp), %ymm4
	vmovdqu \scratch+160(%rsp), %ymm5
	vmovdqu \scratch+192(%rsp), %ymm6
	vmovdqu \scratch+224(%rsp), %ymm7
	SP_RAW %ymm0,%ymm4
	SP_RAW %ymm1,%ymm5
	SP_RAW %ymm2,%ymm6
	SP_RAW %ymm3,%ymm7
	SP_MONT4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Lspcrt_s2_qinv,.Lspcrt_s2_factor
	SP_MONT4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Lspcrt_s3_qinv,.Lspcrt_s3_factor
	SP_HALF_PAIR %ymm0,%ymm1,0
	SP_HALF_PAIR %ymm2,%ymm3,32
	SP_HALF_PAIR %ymm4,%ymm5,64
	SP_HALF_PAIR %ymm6,%ymm7,96
	SP_QWORD_PAIR %ymm0,%ymm1,0
	SP_QWORD_PAIR %ymm2,%ymm3,32
	SP_QWORD_PAIR %ymm4,%ymm5,64
	SP_QWORD_PAIR %ymm6,%ymm7,96
	.if \mode == 1
	SP_CENTER4_MEM %ymm0,%ymm1,%ymm2,%ymm3,%ymm8,%ymm9,%ymm10,%ymm11
	SP_CENTER4_MEM %ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10,%ymm11
	.elseif \mode == 2
	SP_CENTER4_REG %ymm0,%ymm1,%ymm2,%ymm3,%ymm8,%ymm9,%ymm10,%ymm11
	SP_CENTER4_REG %ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10,%ymm11
	.endif
	vmovdqu %ymm0, \output+0(%r11)
	vmovdqu %ymm1, \output+32(%r11)
	vmovdqu %ymm2, \output+64(%r11)
	vmovdqu %ymm3, \output+96(%r11)
	vmovdqu %ymm4, \output+128(%r11)
	vmovdqu %ymm5, \output+160(%r11)
	vmovdqu %ymm6, \output+192(%r11)
	vmovdqu %ymm7, \output+224(%r11)
	.endm

	.macro SP_FORWARD_SCHEDULED_FUNCTION name,mode
	.section .text.\name,"ax",@progbits
	.p2align 6
	.globl \name
	.type \name,@function
\name:
	movq %rsp, %rdx
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1600, %rsp
	movq %rdx, 1544(%rsp)
	SP_INPUT_SLAB 0,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 1,%ymm5,%ymm4,%ymm6
	SP_INPUT_SLAB 2,%ymm6,%ymm5,%ymm4
	SP_INPUT_SLAB 3,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 4,%ymm5,%ymm4,%ymm6
	SP_INPUT_SLAB 5,%ymm6,%ymm5,%ymm4
	SP_INPUT_SLAB 6,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 7,%ymm5,%ymm4,%ymm6
	.if \mode == 2
	vmovdqa .Lspcrt_center10(%rip), %ymm12
	vmovdqa .Lspcrt_q(%rip), %ymm13
	.endif
	SP_ROW_SCHEDULED 0,0,\mode
	SP_ROW_SCHEDULED 256,256,0
	SP_ROW_SCHEDULED 512,512,0
	SP_ROW_SCHEDULED 768,768,\mode
	SP_ROW_SCHEDULED 1024,1024,0
	SP_ROW_SCHEDULED 1280,1280,0
	movq 1544(%rsp), %rsp
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	.section .text.gt32_spcrt_forward_raw_asm,"ax",@progbits
	.p2align 6
	.globl gt32_spcrt_forward_raw_asm
	.type gt32_spcrt_forward_raw_asm,@function
gt32_spcrt_forward_raw_asm:
	xorl %eax, %eax
	jmp .Lspcrt_forward_common
	.size gt32_spcrt_forward_raw_asm,.-gt32_spcrt_forward_raw_asm

	.p2align 5
	.globl gt32_spcrt_forward_a_repaired_asm
	.type gt32_spcrt_forward_a_repaired_asm,@function
gt32_spcrt_forward_a_repaired_asm:
	movl $1, %eax
.Lspcrt_forward_common:
	movq %rsp, %rdx
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1600, %rsp
	movl %eax, 1536(%rsp)
	movq %rdx, 1544(%rsp)
	SP_INPUT_SLAB 0,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 1,%ymm5,%ymm4,%ymm6
	SP_INPUT_SLAB 2,%ymm6,%ymm5,%ymm4
	SP_INPUT_SLAB 3,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 4,%ymm5,%ymm4,%ymm6
	SP_INPUT_SLAB 5,%ymm6,%ymm5,%ymm4
	SP_INPUT_SLAB 6,%ymm4,%ymm6,%ymm5
	SP_INPUT_SLAB 7,%ymm5,%ymm4,%ymm6
	SP_ROW 0,0,1
	SP_ROW 256,256,0
	SP_ROW 512,512,0
	SP_ROW 768,768,1
	SP_ROW 1024,1024,0
	SP_ROW 1280,1280,0
	movq 1544(%rsp), %rsp
	vzeroupper
	ret
	.size gt32_spcrt_forward_a_repaired_asm,.-gt32_spcrt_forward_a_repaired_asm

	SP_FORWARD_SCHEDULED_FUNCTION gt32_spcrt_forward_a_repaired_r1_asm,1
	SP_FORWARD_R2_SHARED

	/* B3 support: exact copy of the qualified arithmetic, SP lambda stream. */
	.macro SP_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd %\s1, %\s0, %\t0
	vpunpckhwd %\s1, %\s0, %\t1
	vpunpcklwd %\s3, %\s2, %\t2
	vpunpckhwd %\s3, %\s2, %\t3
	vpunpckldq %\t2, %\t0, %\s0
	vpunpckhdq %\t2, %\t0, %\s1
	vpunpckldq %\t3, %\t1, %\s2
	vpunpckhdq %\t3, %\t1, %\s3
	vpunpcklqdq %\s2, %\s0, %\t0
	vpunpckhqdq %\s2, %\s0, %\t1
	vpunpcklqdq %\s3, %\s1, %\t2
	vpunpckhqdq %\s3, %\s1, %\t3
	.endm

	.macro SP_BM_FIRST a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a, %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm15, %ymm15
	.endm

	.macro SP_BM_ADD a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a, %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm15, %ymm15
	.endm

	.macro SP_BM_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm

	.section .text.gt32_spcrt_basemul_b3_asm,"ax",@progbits
	.p2align 6
	.globl gt32_spcrt_basemul_b3_asm
	.type gt32_spcrt_basemul_b3_asm,@function
gt32_spcrt_basemul_b3_asm:
	leaq .Lspcrt_bm_lambda(%rip), %r8
	leaq .Lspcrt_bm_lambda_qinv(%rip), %r9
	vmovdqa .Lspcrt_q(%rip), %ymm0
	movl $12, %ecx
	.p2align 5
.Lspcrt_bm_loop:
	vmovdqu 0(%rdx), %ymm1
	vmovdqu 32(%rdx), %ymm2
	vmovdqu 64(%rdx), %ymm3
	vmovdqu 96(%rdx), %ymm4
	SP_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
	vmovdqu 0(%rsi), %ymm5
	vmovdqu 32(%rsi), %ymm6
	vmovdqu 64(%rsi), %ymm7
	vmovdqu 96(%rsi), %ymm8
	SP_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
	vpmullw .Lspcrt_bm_qinv(%rip), %ymm1, %ymm5
	vpmullw .Lspcrt_bm_qinv(%rip), %ymm2, %ymm6
	vpmullw .Lspcrt_bm_qinv(%rip), %ymm3, %ymm7
	vpmullw .Lspcrt_bm_qinv(%rip), %ymm4, %ymm8
	SP_BM_FIRST ymm2,ymm6,ymm12
	SP_BM_ADD ymm3,ymm7,ymm11
	SP_BM_ADD ymm4,ymm8,ymm10
	SP_BM_LAMBDA
	SP_BM_ADD ymm1,ymm5,ymm9
	vmovdqu %ymm15, 0(%rdi)
	SP_BM_FIRST ymm3,ymm7,ymm12
	SP_BM_ADD ymm4,ymm8,ymm11
	SP_BM_LAMBDA
	SP_BM_ADD ymm1,ymm5,ymm10
	SP_BM_ADD ymm2,ymm6,ymm9
	vmovdqu %ymm15, 32(%rdi)
	SP_BM_FIRST ymm4,ymm8,ymm12
	SP_BM_LAMBDA
	SP_BM_ADD ymm1,ymm5,ymm11
	SP_BM_ADD ymm2,ymm6,ymm10
	SP_BM_ADD ymm3,ymm7,ymm9
	vmovdqu %ymm15, 64(%rdi)
	SP_BM_FIRST ymm1,ymm5,ymm12
	SP_BM_ADD ymm2,ymm6,ymm11
	SP_BM_ADD ymm3,ymm7,ymm10
	SP_BM_ADD ymm4,ymm8,ymm9
	vmovdqu 0(%rdi), %ymm1
	vmovdqu 32(%rdi), %ymm2
	vmovdqu 64(%rdi), %ymm3
	SP_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
	vpmulhrsw .Lspcrt_center10(%rip), %ymm5, %ymm1
	vpmulhrsw .Lspcrt_center10(%rip), %ymm6, %ymm2
	vpmulhrsw .Lspcrt_center10(%rip), %ymm7, %ymm3
	vpmulhrsw .Lspcrt_center10(%rip), %ymm8, %ymm4
	vpmullw %ymm0, %ymm1, %ymm1
	vpmullw %ymm0, %ymm2, %ymm2
	vpmullw %ymm0, %ymm3, %ymm3
	vpmullw %ymm0, %ymm4, %ymm4
	vpsubw %ymm1, %ymm5, %ymm5
	vpsubw %ymm2, %ymm6, %ymm6
	vpsubw %ymm3, %ymm7, %ymm7
	vpsubw %ymm4, %ymm8, %ymm8
	vmovdqu %ymm5, 0(%rdi)
	vmovdqu %ymm6, 32(%rdi)
	vmovdqu %ymm7, 64(%rdi)
	vmovdqu %ymm8, 96(%rdi)
	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Lspcrt_bm_loop
	vzeroupper
	ret
	.size gt32_spcrt_basemul_b3_asm,.-gt32_spcrt_basemul_b3_asm

	.section .rodata
#include "../generated/tile4_n32_forward_constants.inc"
#include "../generated/tile4_spcrt_b3_exec_constants.inc"

	.section .note.GNU-stack,"",@progbits
