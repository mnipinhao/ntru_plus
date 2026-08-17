/* GT-N32-CONJ-BRANCH-AT-A-TIME-019: one-wave producer schedule probe. */

	.text

	.macro BAT_FORM_TOP b0,b1,tmp,vector
	vmovdqu 32*\vector(%rsi), \b0
	vmovdqu 768+32*\vector(%rsi), \b1
	vpmullw .Ln32_fwd_top_raw(%rip), \b1, \tmp
	vpaddw \b0, \b1, \b1
	vpsubw \tmp, \b1, \b1
	vpaddw \tmp, \b0, \b0
	.endm

	.macro BAT_MONT_SERIAL lo,hi,tmp,qinv,factor,offset
	vpmullw \qinv+\offset(%rip), \hi, \tmp
	vpmulhw \factor+\offset(%rip), \hi, \hi
	vpmulhw .Ln32_fwd_q(%rip), \tmp, \tmp
	vpsubw \tmp, \hi, \hi
	vpsubw \hi, \lo, \tmp
	vpaddw \hi, \lo, \lo
	vmovdqa \tmp, \hi
	.endm

	.macro BAT_MONT_PAR_MEMQ l0,h0,l1,h1,l2,h2,l3,h3,t0,t1,t2,t3,qinv,factor
	vpmullw \qinv+0(%rip), \h0, \t0
	vpmullw \qinv+32(%rip), \h1, \t1
	vpmullw \qinv+64(%rip), \h2, \t2
	vpmullw \qinv+96(%rip), \h3, \t3
	vpmulhw \factor+0(%rip), \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw .Ln32_fwd_q(%rip), \t0, \t0
	vpmulhw .Ln32_fwd_q(%rip), \t1, \t1
	vpmulhw .Ln32_fwd_q(%rip), \t2, \t2
	vpmulhw .Ln32_fwd_q(%rip), \t3, \t3
	vpsubw \t0, \h0, \h0
	vpsubw \t1, \h1, \h1
	vpsubw \t2, \h2, \h2
	vpsubw \t3, \h3, \h3
	vpsubw \h0, \l0, \t0
	vpsubw \h1, \l1, \t1
	vpsubw \h2, \l2, \t2
	vpsubw \h3, \l3, \t3
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
	vmovdqa \t0, \h0
	vmovdqa \t1, \h1
	vmovdqa \t2, \h2
	vmovdqa \t3, \h3
	.endm

	.macro BAT_MONT_PAR_QREG l0,h0,l1,h1,l2,h2,l3,h3,t0,t1,t2,t3,qinv,factor
	vpmullw \qinv+0(%rip), \h0, \t0
	vpmullw \qinv+32(%rip), \h1, \t1
	vpmullw \qinv+64(%rip), \h2, \t2
	vpmullw \qinv+96(%rip), \h3, \t3
	vpmulhw \factor+0(%rip), \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw %ymm15, \t0, \t0
	vpmulhw %ymm15, \t1, \t1
	vpmulhw %ymm15, \t2, \t2
	vpmulhw %ymm15, \t3, \t3
	vpsubw \t0, \h0, \h0
	vpsubw \t1, \h1, \h1
	vpsubw \t2, \h2, \h2
	vpsubw \t3, \h3, \h3
	vpsubw \h0, \l0, \t0
	vpsubw \h1, \l1, \t1
	vpsubw \h2, \l2, \t2
	vpsubw \h3, \l3, \t3
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
	vmovdqa \t0, \h0
	vmovdqa \t1, \h1
	vmovdqa \t2, \h2
	vmovdqa \t3, \h3
	.endm

	/* Current production-shaped one-wave schedule. */
	.p2align 5
	.globl gt32_n32_conj_wave_control_asm
	.type gt32_n32_conj_wave_control_asm,@function
gt32_n32_conj_wave_control_asm:
	subq $32, %rsp
	BAT_FORM_TOP %ymm0,%ymm8,%ymm15,0
	BAT_FORM_TOP %ymm1,%ymm9,%ymm15,9
	BAT_FORM_TOP %ymm2,%ymm10,%ymm15,18
	BAT_FORM_TOP %ymm3,%ymm11,%ymm15,3
	BAT_FORM_TOP %ymm4,%ymm12,%ymm15,12
	BAT_FORM_TOP %ymm5,%ymm13,%ymm15,21
	BAT_FORM_TOP %ymm6,%ymm14,%ymm15,6
	vmovdqu %ymm14, (%rsp)
	BAT_FORM_TOP %ymm7,%ymm14,%ymm15,15
	BAT_MONT_SERIAL %ymm0,%ymm4,%ymm15,.Ln32_conj_b0_w0_s1_qinv,.Ln32_conj_b0_w0_s1_factor,0
	BAT_MONT_SERIAL %ymm1,%ymm5,%ymm15,.Ln32_conj_b0_w0_s1_qinv,.Ln32_conj_b0_w0_s1_factor,32
	BAT_MONT_SERIAL %ymm2,%ymm6,%ymm15,.Ln32_conj_b0_w0_s1_qinv,.Ln32_conj_b0_w0_s1_factor,64
	BAT_MONT_SERIAL %ymm3,%ymm7,%ymm15,.Ln32_conj_b0_w0_s1_qinv,.Ln32_conj_b0_w0_s1_factor,96
	BAT_MONT_SERIAL %ymm0,%ymm2,%ymm15,.Ln32_conj_b0_w0_s2_qinv,.Ln32_conj_b0_w0_s2_factor,0
	BAT_MONT_SERIAL %ymm1,%ymm3,%ymm15,.Ln32_conj_b0_w0_s2_qinv,.Ln32_conj_b0_w0_s2_factor,32
	BAT_MONT_SERIAL %ymm4,%ymm6,%ymm15,.Ln32_conj_b0_w0_s2_qinv,.Ln32_conj_b0_w0_s2_factor,64
	BAT_MONT_SERIAL %ymm5,%ymm7,%ymm15,.Ln32_conj_b0_w0_s2_qinv,.Ln32_conj_b0_w0_s2_factor,96
	BAT_MONT_SERIAL %ymm0,%ymm1,%ymm15,.Ln32_conj_b0_w0_s3_qinv,.Ln32_conj_b0_w0_s3_factor,0
	BAT_MONT_SERIAL %ymm2,%ymm3,%ymm15,.Ln32_conj_b0_w0_s3_qinv,.Ln32_conj_b0_w0_s3_factor,32
	BAT_MONT_SERIAL %ymm4,%ymm5,%ymm15,.Ln32_conj_b0_w0_s3_qinv,.Ln32_conj_b0_w0_s3_factor,64
	BAT_MONT_SERIAL %ymm6,%ymm7,%ymm15,.Ln32_conj_b0_w0_s3_qinv,.Ln32_conj_b0_w0_s3_factor,96
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vmovdqu (%rsp), %ymm6
	BAT_MONT_PAR_MEMQ %ymm8,%ymm12,%ymm9,%ymm13,%ymm10,%ymm6,%ymm11,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_conj_b1_w0_s1_qinv,.Ln32_conj_b1_w0_s1_factor
	BAT_MONT_PAR_MEMQ %ymm8,%ymm10,%ymm9,%ymm11,%ymm12,%ymm6,%ymm13,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_conj_b1_w0_s2_qinv,.Ln32_conj_b1_w0_s2_factor
	BAT_MONT_PAR_MEMQ %ymm8,%ymm9,%ymm10,%ymm11,%ymm12,%ymm13,%ymm6,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_conj_b1_w0_s3_qinv,.Ln32_conj_b1_w0_s3_factor
	vmovdqu %ymm8,  256(%rdi)
	vmovdqu %ymm9,  288(%rdi)
	vmovdqu %ymm10, 320(%rdi)
	vmovdqu %ymm11, 352(%rdi)
	vmovdqu %ymm12, 384(%rdi)
	vmovdqu %ymm13, 416(%rdi)
	vmovdqu %ymm6,  448(%rdi)
	vmovdqu %ymm14, 480(%rdi)
	addq $32, %rsp
	vzeroupper
	ret
	.size gt32_n32_conj_wave_control_asm,.-gt32_n32_conj_wave_control_asm

	/* Shared top split; inactive branch is immediately materialized. */
	.p2align 5
	.globl gt32_n32_conj_wave_branch_at_time_asm
	.type gt32_n32_conj_wave_branch_at_time_asm,@function
gt32_n32_conj_wave_branch_at_time_asm:
	BAT_FORM_TOP %ymm0,%ymm8,%ymm9,0
	vmovdqu %ymm8, 256(%rdi)
	BAT_FORM_TOP %ymm1,%ymm8,%ymm9,9
	vmovdqu %ymm8, 288(%rdi)
	BAT_FORM_TOP %ymm2,%ymm8,%ymm9,18
	vmovdqu %ymm8, 320(%rdi)
	BAT_FORM_TOP %ymm3,%ymm8,%ymm9,3
	vmovdqu %ymm8, 352(%rdi)
	BAT_FORM_TOP %ymm4,%ymm8,%ymm9,12
	vmovdqu %ymm8, 384(%rdi)
	BAT_FORM_TOP %ymm5,%ymm8,%ymm9,21
	vmovdqu %ymm8, 416(%rdi)
	BAT_FORM_TOP %ymm6,%ymm8,%ymm9,6
	vmovdqu %ymm8, 448(%rdi)
	BAT_FORM_TOP %ymm7,%ymm8,%ymm9,15
	vmovdqu %ymm8, 480(%rdi)
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	BAT_MONT_PAR_QREG %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b0_w0_s1_qinv,.Ln32_conj_b0_w0_s1_factor
	BAT_MONT_PAR_QREG %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b0_w0_s2_qinv,.Ln32_conj_b0_w0_s2_factor
	BAT_MONT_PAR_QREG %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b0_w0_s3_qinv,.Ln32_conj_b0_w0_s3_factor
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vmovdqu 256(%rdi), %ymm0
	vmovdqu 288(%rdi), %ymm1
	vmovdqu 320(%rdi), %ymm2
	vmovdqu 352(%rdi), %ymm3
	vmovdqu 384(%rdi), %ymm4
	vmovdqu 416(%rdi), %ymm5
	vmovdqu 448(%rdi), %ymm6
	vmovdqu 480(%rdi), %ymm7
	BAT_MONT_PAR_QREG %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b1_w0_s1_qinv,.Ln32_conj_b1_w0_s1_factor
	BAT_MONT_PAR_QREG %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b1_w0_s2_qinv,.Ln32_conj_b1_w0_s2_factor
	BAT_MONT_PAR_QREG %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b1_w0_s3_qinv,.Ln32_conj_b1_w0_s3_factor
	vmovdqu %ymm0, 256(%rdi)
	vmovdqu %ymm1, 288(%rdi)
	vmovdqu %ymm2, 320(%rdi)
	vmovdqu %ymm3, 352(%rdi)
	vmovdqu %ymm4, 384(%rdi)
	vmovdqu %ymm5, 416(%rdi)
	vmovdqu %ymm6, 448(%rdi)
	vmovdqu %ymm7, 480(%rdi)
	vzeroupper
	ret
	.size gt32_n32_conj_wave_branch_at_time_asm,.-gt32_n32_conj_wave_branch_at_time_asm

	.section .rodata
#include "../generated/tile4_n32_forward_constants.inc"

	.section .note.GNU-stack,"",@progbits
