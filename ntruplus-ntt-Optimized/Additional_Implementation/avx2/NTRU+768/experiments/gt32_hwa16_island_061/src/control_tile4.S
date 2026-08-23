/* Fixed TILE4 control island: current pair Forward/B3-late/pair Inverse. */

	.text

	.macro CTL_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip),  \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip),  \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8, \h0, \h0
	vpsubw %ymm9, \h1, \h1
	vpsubw %ymm10, \h2, \h2
	vpsubw %ymm11, \h3, \h3
	vpsubw \h0, \l0, %ymm8
	vpsubw \h1, \l1, %ymm9
	vpsubw \h2, \l2, %ymm10
	vpsubw \h3, \l3, %ymm11
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
	vmovdqa %ymm8, \h0
	vmovdqa %ymm9, \h1
	vmovdqa %ymm10, \h2
	vmovdqa %ymm11, \h3
	.endm

	.macro CTL_RAW_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3
	vpsubw \h0, \l0, %ymm8
	vpsubw \h1, \l1, %ymm9
	vpsubw \h2, \l2, %ymm10
	vpsubw \h3, \l3, %ymm11
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
	vmovdqa %ymm8, \h0
	vmovdqa %ymm9, \h1
	vmovdqa %ymm10, \h2
	vmovdqa %ymm11, \h3
	.endm

	.macro CTL_MONT_HALF_PAIR v0,v1,qinv,factor,offset
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

	.macro CTL_MONT_QWORD_PAIR v0,v1,qinv,factor,offset
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro CTL_RAW_QWORD_PAIR v0,v1
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro CTL_LOAD
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	.endm

	.macro CTL_STORE
	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	.endm

	.p2align 5
	.globl ctl_tile4_forward_asm
	.type ctl_tile4_forward_asm,@function
ctl_tile4_forward_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	CTL_LOAD
	CTL_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
	CTL_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7,.Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
	CTL_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,.Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor
	CTL_MONT_HALF_PAIR %ymm0,%ymm1,.Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor,0
	CTL_MONT_HALF_PAIR %ymm2,%ymm3,.Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor,32
	CTL_MONT_HALF_PAIR %ymm4,%ymm5,.Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor,64
	CTL_MONT_HALF_PAIR %ymm6,%ymm7,.Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor,96
	CTL_MONT_QWORD_PAIR %ymm0,%ymm1,.Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor,0
	CTL_MONT_QWORD_PAIR %ymm2,%ymm3,.Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor,32
	CTL_MONT_QWORD_PAIR %ymm4,%ymm5,.Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor,64
	CTL_MONT_QWORD_PAIR %ymm6,%ymm7,.Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor,96
	CTL_STORE
	vzeroupper
	ret
	.size ctl_tile4_forward_asm,.-ctl_tile4_forward_asm

	.p2align 5
	.globl ctl_tile4_inverse_asm
	.type ctl_tile4_inverse_asm,@function
ctl_tile4_inverse_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	CTL_LOAD
	CTL_RAW_QWORD_PAIR %ymm0,%ymm1
	CTL_RAW_QWORD_PAIR %ymm2,%ymm3
	CTL_RAW_QWORD_PAIR %ymm4,%ymm5
	CTL_RAW_QWORD_PAIR %ymm6,%ymm7
	CTL_MONT_HALF_PAIR %ymm0,%ymm1,.Ltile4_inv_s1_pair_qinv,.Ltile4_inv_s1_pair_factor,0
	CTL_MONT_HALF_PAIR %ymm2,%ymm3,.Ltile4_inv_s1_pair_qinv,.Ltile4_inv_s1_pair_factor,32
	CTL_MONT_HALF_PAIR %ymm4,%ymm5,.Ltile4_inv_s1_pair_qinv,.Ltile4_inv_s1_pair_factor,64
	CTL_MONT_HALF_PAIR %ymm6,%ymm7,.Ltile4_inv_s1_pair_qinv,.Ltile4_inv_s1_pair_factor,96
	CTL_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,.Ltile4_inv_s2_qinv,.Ltile4_inv_s2_factor
	CTL_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7,.Ltile4_inv_s3_qinv,.Ltile4_inv_s3_factor
	CTL_MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7,.Ltile4_inv_s4_qinv,.Ltile4_inv_s4_factor
	CTL_STORE
	vzeroupper
	ret
	.size ctl_tile4_inverse_asm,.-ctl_tile4_inverse_asm

	/* 16 quartics x four int16 coefficient transpose, self-inverse. */
	.macro CTL_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd \s1, \s0, \t0
	vpunpckhwd \s1, \s0, \t1
	vpunpcklwd \s3, \s2, \t2
	vpunpckhwd \s3, \s2, \t3
	vpunpckldq \t2, \t0, \s0
	vpunpckhdq \t2, \t0, \s1
	vpunpckldq \t3, \t1, \s2
	vpunpckhdq \t3, \t1, \s3
	vpunpcklqdq \s2, \s0, \t0
	vpunpckhqdq \s2, \s0, \t1
	vpunpcklqdq \s3, \s1, \t2
	vpunpckhqdq \s3, \s1, \t3
	.endm

	.macro CTL_BM_FIRST a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm15, %ymm15
	.endm
	.macro CTL_BM_ADD a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm15, %ymm15
	.endm
	.macro CTL_BM_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm

	.p2align 5
	.globl ctl_tile4_basemul_asm
	.type ctl_tile4_basemul_asm,@function
ctl_tile4_basemul_asm:
	leaq .Lctl_bm_lambda(%rip), %r8
	leaq .Lctl_bm_lambda_qinv(%rip), %r9
	vmovdqa .Lhwa_q(%rip), %ymm0
	movl $2, %ecx
.Lctl_bm_loop:
	vmovdqu 0(%rdx), %ymm1
	vmovdqu 32(%rdx), %ymm2
	vmovdqu 64(%rdx), %ymm3
	vmovdqu 96(%rdx), %ymm4
	CTL_TRANSPOSE %ymm1,%ymm2,%ymm3,%ymm4,%ymm9,%ymm10,%ymm11,%ymm12
	vmovdqu 0(%rsi), %ymm5
	vmovdqu 32(%rsi), %ymm6
	vmovdqu 64(%rsi), %ymm7
	vmovdqu 96(%rsi), %ymm8
	CTL_TRANSPOSE %ymm5,%ymm6,%ymm7,%ymm8,%ymm1,%ymm2,%ymm3,%ymm4
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm1, %ymm5
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm2, %ymm6
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm3, %ymm7
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm4, %ymm8
	CTL_BM_FIRST %ymm2,%ymm6,%ymm12
	CTL_BM_ADD %ymm3,%ymm7,%ymm11
	CTL_BM_ADD %ymm4,%ymm8,%ymm10
	CTL_BM_LAMBDA
	CTL_BM_ADD %ymm1,%ymm5,%ymm9
	vmovdqu %ymm15, 0(%rdi)
	CTL_BM_FIRST %ymm3,%ymm7,%ymm12
	CTL_BM_ADD %ymm4,%ymm8,%ymm11
	CTL_BM_LAMBDA
	CTL_BM_ADD %ymm1,%ymm5,%ymm10
	CTL_BM_ADD %ymm2,%ymm6,%ymm9
	vmovdqu %ymm15, 32(%rdi)
	CTL_BM_FIRST %ymm4,%ymm8,%ymm12
	CTL_BM_LAMBDA
	CTL_BM_ADD %ymm1,%ymm5,%ymm11
	CTL_BM_ADD %ymm2,%ymm6,%ymm10
	CTL_BM_ADD %ymm3,%ymm7,%ymm9
	vmovdqu %ymm15, 64(%rdi)
	CTL_BM_FIRST %ymm1,%ymm5,%ymm12
	CTL_BM_ADD %ymm2,%ymm6,%ymm11
	CTL_BM_ADD %ymm3,%ymm7,%ymm10
	CTL_BM_ADD %ymm4,%ymm8,%ymm9
	vpmulhrsw .Lhwa_center10(%rip), %ymm15, %ymm14
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	vmovdqu 0(%rdi), %ymm1
	vmovdqu 32(%rdi), %ymm2
	vmovdqu 64(%rdi), %ymm3
	CTL_TRANSPOSE %ymm1,%ymm2,%ymm3,%ymm15,%ymm5,%ymm6,%ymm7,%ymm8
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
	jne .Lctl_bm_loop
	vzeroupper
	ret
	.size ctl_tile4_basemul_asm,.-ctl_tile4_basemul_asm

	.section .rodata
#include "../../avx2_gt32_tile4_official_001/generated/tile4_constants.inc"
#include "../generated/hwa16_constants.inc"
	.p2align 5
.Lhwa_bm_qinv_scalar:
	.rept 16
	.short 12929
	.endr

	.section .note.GNU-stack,"",@progbits
