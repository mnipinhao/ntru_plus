/* P2 bounded executable probe: private M -> I-112 packet -> native inverse. */

	.text

	/*
	 * M tile: [c0p01,c1p01,c2p01,c3p01,c0p23,c1p23,c2p23,c3p23]
	 * I-112: [c0p0|c1p0,c0p1|c1p1,c0p2|c1p2,c0p3|c1p3,
	 *         c2p01,c2p23,c3p01,c3p23]
	 */
	.p2align 5
	.globl gt32_tile4_m_to_i112_asm
	.type gt32_tile4_m_to_i112_asm,@function
gt32_tile4_m_to_i112_asm:
	movl $6, %ecx
	.p2align 5
.Li112_form_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
	vperm2i128 $0x31, %ymm1, %ymm0, %ymm9
	vperm2i128 $0x20, %ymm5, %ymm4, %ymm10
	vperm2i128 $0x31, %ymm5, %ymm4, %ymm11
	vmovdqu %ymm8,   0(%rdi)
	vmovdqu %ymm9,  32(%rdi)
	vmovdqu %ymm10, 64(%rdi)
	vmovdqu %ymm11, 96(%rdi)
	vmovdqu  64(%rsi), %ymm0
	vmovdqu 192(%rsi), %ymm1
	vmovdqu  96(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	vmovdqu %ymm0, 128(%rdi)
	vmovdqu %ymm1, 160(%rdi)
	vmovdqu %ymm2, 192(%rdi)
	vmovdqu %ymm3, 224(%rdi)
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Li112_form_loop
	vzeroupper
	ret
	.size gt32_tile4_m_to_i112_asm,.-gt32_tile4_m_to_i112_asm

	/* Exact inverse map, used only as the executable correctness control. */
	.p2align 5
	.globl gt32_tile4_i112_to_m_asm
	.type gt32_tile4_i112_to_m_asm,@function
gt32_tile4_i112_to_m_asm:
	movl $6, %ecx
	.p2align 5
.Li112_unform_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
	vperm2i128 $0x31, %ymm1, %ymm0, %ymm9
	vperm2i128 $0x20, %ymm3, %ymm2, %ymm10
	vperm2i128 $0x31, %ymm3, %ymm2, %ymm11
	vmovdqu %ymm8,   0(%rdi)
	vmovdqu %ymm9,  32(%rdi)
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 192(%rsi), %ymm1
	vmovdqu 160(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	vmovdqu %ymm0,  64(%rdi)
	vmovdqu %ymm1,  96(%rdi)
	vmovdqu %ymm10,128(%rdi)
	vmovdqu %ymm11,160(%rdi)
	vmovdqu %ymm2, 192(%rdi)
	vmovdqu %ymm3, 224(%rdi)
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Li112_unform_loop
	vzeroupper
	ret
	.size gt32_tile4_i112_to_m_asm,.-gt32_tile4_i112_to_m_asm

	/* Common-endpoint control: private M planes -> standard TILE4 AoS. */
	.macro I112_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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

	.p2align 5
	.globl gt32_tile4_m_to_aos_asm
	.type gt32_tile4_m_to_aos_asm,@function
gt32_tile4_m_to_aos_asm:
	movl $12, %ecx
	.p2align 5
.Li112_m_to_aos_loop:
	vmovdqu  0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	I112_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4,  0(%rdi)
	vmovdqu %ymm5, 32(%rdi)
	vmovdqu %ymm6, 64(%rdi)
	vmovdqu %ymm7, 96(%rdi)
	addq $128, %rsi
	addq $128, %rdi
	decl %ecx
	jne .Li112_m_to_aos_loop
	vzeroupper
	ret
	.size gt32_tile4_m_to_aos_asm,.-gt32_tile4_m_to_aos_asm

	.section .note.GNU-stack,"",@progbits
