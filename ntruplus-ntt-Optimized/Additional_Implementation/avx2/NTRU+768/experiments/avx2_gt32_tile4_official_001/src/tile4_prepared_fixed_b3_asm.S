/* PREPARED-FIXED-B3-001, bounded general-product probe.
 *
 * dynamic private-SoA e=0 x prepared fixed row packets e=1 -> private-SoA
 * e=0.  The e=1 prepare-time scaling lets REDC16 replace the general B3 R2
 * output finalizer rather than merely moving it to another runtime pass.
 */

	.text

	.macro FIXED_DOT_HALF ap01,ap23,koff,dst
	vpmaddwd \koff(%rdx), \ap01, %ymm12
	vpmaddwd \koff+32(%rdx), \ap23, %ymm13
	vpaddd %ymm13, %ymm12, %ymm12
	vpmullw .Lfixed_b3_qinv(%rip), %ymm12, %ymm13
	vpmulhuw .Lfixed_b3_q(%rip), %ymm13, %ymm13
	vpsrad $16, %ymm12, %ymm12
	vpsubw %ymm13, %ymm12, %ymm12
	vpshufb .Lfixed_b3_compact_even(%rip), %ymm12, %ymm12
	vpermq $0xd8, %ymm12, %ymm12
	vmovdqa %ymm12, \dst
	.endm

	.macro FIXED_DOT_COEFFICIENT outoff,koff
	FIXED_DOT_HALF %ymm0,%ymm2,\koff,%ymm14
	FIXED_DOT_HALF %ymm1,%ymm3,\koff+64,%ymm15
	vpunpcklqdq %ymm15, %ymm14, %ymm11
	vpunpckhqdq %ymm15, %ymm14, %ymm13
	vperm2i128 $0x20, %ymm13, %ymm11, %ymm12
	vmovdqu %ymm12, \outoff(%rdi)
	.endm

	.p2align 5
	.globl gt32_tile4_basemul_general_fixed_soa_e1_asm
	.type gt32_tile4_basemul_general_fixed_soa_e1_asm,@function
gt32_tile4_basemul_general_fixed_soa_e1_asm:
	movl $12, %ecx
	.p2align 5
.Lfixed_b3_loop:
	vmovdqu   0(%rsi), %ymm11
	vmovdqu  32(%rsi), %ymm12
	vmovdqu  64(%rsi), %ymm13
	vmovdqu  96(%rsi), %ymm14
	vpunpcklwd %ymm12, %ymm11, %ymm0
	vpunpckhwd %ymm12, %ymm11, %ymm1
	vpunpcklwd %ymm14, %ymm13, %ymm2
	vpunpckhwd %ymm14, %ymm13, %ymm3

	FIXED_DOT_COEFFICIENT   0,0
	FIXED_DOT_COEFFICIENT  32,128
	FIXED_DOT_COEFFICIENT  64,256
	FIXED_DOT_COEFFICIENT  96,384

	addq $128, %rsi
	addq $512, %rdx
	addq $128, %rdi
	decl %ecx
	jne .Lfixed_b3_loop
	vzeroupper
	ret
	.size gt32_tile4_basemul_general_fixed_soa_e1_asm,.-gt32_tile4_basemul_general_fixed_soa_e1_asm

	.section .rodata
	.p2align 5
.Lfixed_b3_q:
	.rept 16
	.short 3457
	.endr
.Lfixed_b3_qinv:
	.rept 16
	.short 12929
	.endr
.Lfixed_b3_compact_even:
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128

	.section .note.GNU-stack,"",@progbits
