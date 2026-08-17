/* GT-N32-PHYSICAL-SCHEDULE-005: executable post-twist S1-S3 wave probe. */

	.text

	.macro W_RAW_PAR l0,h0,l1,h1,l2,h2,l3,h3
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

	.macro W_MONT_PAR l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip), \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip), \h0, \h0
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

	.macro W_RAW_DESTRUCTIVE l,h
	vpaddw \h, \l, \l
	vpaddw \h, \h, \h
	vpsubw \h, \l, \h
	.endm

	.macro W_MONT_SERIAL l,h,tmp,qinv,factor,offset
	vpmullw \qinv+\offset(%rip), \h, \tmp
	vpmulhw \factor+\offset(%rip), \h, \h
	vpmulhw .Ln32w_q(%rip), \tmp, \tmp
	vpsubw \tmp, \h, \h
	vpsubw \h, \l, \tmp
	vpaddw \h, \l, \l
	vmovdqa \tmp, \h
	.endm

	/* Isolated Branch-1 q-source probe.  Explicit temporaries keep the eight
	 * data vectors in ymm4..ymm11 while ymm0..ymm3 carry four parallel chains. */
	.macro W_MONT_EXPLICIT_MEMQ l0,h0,l1,h1,l2,h2,l3,h3,t0,t1,t2,t3,qinv,factor
	vpmullw \qinv+0(%rip), \h0, \t0
	vpmullw \qinv+32(%rip), \h1, \t1
	vpmullw \qinv+64(%rip), \h2, \t2
	vpmullw \qinv+96(%rip), \h3, \t3
	vpmulhw \factor+0(%rip), \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw .Ln32w_q(%rip), \t0, \t0
	vpmulhw .Ln32w_q(%rip), \t1, \t1
	vpmulhw .Ln32w_q(%rip), \t2, \t2
	vpmulhw .Ln32w_q(%rip), \t3, \t3
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

	.macro W_MONT_EXPLICIT_QREG l0,h0,l1,h1,l2,h2,l3,h3,t0,t1,t2,t3,qinv,factor
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

	/* Control: two independent materialized rows, current parallel schedule. */
	.p2align 5
	.globl gt32_n32_wave_s1s3_control_asm
	.type gt32_n32_wave_s1s3_control_asm,@function
gt32_n32_wave_s1s3_control_asm:
	vmovdqa .Ln32w_q(%rip), %ymm15
	movl $2, %ecx
.Ln32w_control_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	W_RAW_PAR %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
	W_MONT_PAR %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ln32w_s2_qinv,.Ln32w_s2_factor
	W_MONT_PAR %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ln32w_s3_qinv,.Ln32w_s3_factor
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ln32w_control_loop
	vzeroupper
	ret
	.size gt32_n32_wave_s1s3_control_asm,.-gt32_n32_wave_s1s3_control_asm

	/* R3/C2: 16 live data vectors, one spill slot, q from memory. */
	.p2align 5
	.globl gt32_n32_wave_s1s3_c2_asm
	.type gt32_n32_wave_s1s3_c2_asm,@function
gt32_n32_wave_s1s3_c2_asm:
	subq $32, %rsp
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	vmovdqu 256(%rsi), %ymm8
	vmovdqu 288(%rsi), %ymm9
	vmovdqu 320(%rsi), %ymm10
	vmovdqu 352(%rsi), %ymm11
	vmovdqu 384(%rsi), %ymm12
	vmovdqu 416(%rsi), %ymm13
	vmovdqu 448(%rsi), %ymm14
	vmovdqu 480(%rsi), %ymm15
	vmovdqu %ymm15, (%rsp)

	W_RAW_DESTRUCTIVE %ymm0,%ymm4
	W_RAW_DESTRUCTIVE %ymm1,%ymm5
	W_RAW_DESTRUCTIVE %ymm2,%ymm6
	W_RAW_DESTRUCTIVE %ymm3,%ymm7
	W_MONT_SERIAL %ymm0,%ymm2,%ymm15,.Ln32w_s2_qinv,.Ln32w_s2_factor,0
	W_MONT_SERIAL %ymm1,%ymm3,%ymm15,.Ln32w_s2_qinv,.Ln32w_s2_factor,32
	W_MONT_SERIAL %ymm4,%ymm6,%ymm15,.Ln32w_s2_qinv,.Ln32w_s2_factor,64
	W_MONT_SERIAL %ymm5,%ymm7,%ymm15,.Ln32w_s2_qinv,.Ln32w_s2_factor,96
	W_MONT_SERIAL %ymm0,%ymm1,%ymm15,.Ln32w_s3_qinv,.Ln32w_s3_factor,0
	W_MONT_SERIAL %ymm2,%ymm3,%ymm15,.Ln32w_s3_qinv,.Ln32w_s3_factor,32
	W_MONT_SERIAL %ymm4,%ymm5,%ymm15,.Ln32w_s3_qinv,.Ln32w_s3_factor,64
	W_MONT_SERIAL %ymm6,%ymm7,%ymm15,.Ln32w_s3_qinv,.Ln32w_s3_factor,96
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)

	vmovdqu (%rsp), %ymm15
	W_RAW_DESTRUCTIVE %ymm8,%ymm12
	W_RAW_DESTRUCTIVE %ymm9,%ymm13
	W_RAW_DESTRUCTIVE %ymm10,%ymm14
	W_RAW_DESTRUCTIVE %ymm11,%ymm15
	/* Four parallel chains use the now-dead branch-0 registers as temps. */
	vpmullw .Ln32w_s2_qinv+0(%rip), %ymm10, %ymm0
	vpmullw .Ln32w_s2_qinv+32(%rip), %ymm11, %ymm1
	vpmullw .Ln32w_s2_qinv+64(%rip), %ymm14, %ymm2
	vpmullw .Ln32w_s2_qinv+96(%rip), %ymm15, %ymm3
	vpmulhw .Ln32w_s2_factor+0(%rip), %ymm10, %ymm10
	vpmulhw .Ln32w_s2_factor+32(%rip), %ymm11, %ymm11
	vpmulhw .Ln32w_s2_factor+64(%rip), %ymm14, %ymm14
	vpmulhw .Ln32w_s2_factor+96(%rip), %ymm15, %ymm15
	vpmulhw .Ln32w_q(%rip), %ymm0, %ymm0
	vpmulhw .Ln32w_q(%rip), %ymm1, %ymm1
	vpmulhw .Ln32w_q(%rip), %ymm2, %ymm2
	vpmulhw .Ln32w_q(%rip), %ymm3, %ymm3
	vpsubw %ymm0, %ymm10, %ymm10
	vpsubw %ymm1, %ymm11, %ymm11
	vpsubw %ymm2, %ymm14, %ymm14
	vpsubw %ymm3, %ymm15, %ymm15
	vpsubw %ymm10, %ymm8, %ymm0
	vpsubw %ymm11, %ymm9, %ymm1
	vpsubw %ymm14, %ymm12, %ymm2
	vpsubw %ymm15, %ymm13, %ymm3
	vpaddw %ymm10, %ymm8, %ymm8
	vpaddw %ymm11, %ymm9, %ymm9
	vpaddw %ymm14, %ymm12, %ymm12
	vpaddw %ymm15, %ymm13, %ymm13
	vmovdqa %ymm0, %ymm10
	vmovdqa %ymm1, %ymm11
	vmovdqa %ymm2, %ymm14
	vmovdqa %ymm3, %ymm15

	/* S3, with the same four dead registers as parallel temporaries. */
	vpmullw .Ln32w_s3_qinv+0(%rip), %ymm9, %ymm0
	vpmullw .Ln32w_s3_qinv+32(%rip), %ymm11, %ymm1
	vpmullw .Ln32w_s3_qinv+64(%rip), %ymm13, %ymm2
	vpmullw .Ln32w_s3_qinv+96(%rip), %ymm15, %ymm3
	vpmulhw .Ln32w_s3_factor+0(%rip), %ymm9, %ymm9
	vpmulhw .Ln32w_s3_factor+32(%rip), %ymm11, %ymm11
	vpmulhw .Ln32w_s3_factor+64(%rip), %ymm13, %ymm13
	vpmulhw .Ln32w_s3_factor+96(%rip), %ymm15, %ymm15
	vpmulhw .Ln32w_q(%rip), %ymm0, %ymm0
	vpmulhw .Ln32w_q(%rip), %ymm1, %ymm1
	vpmulhw .Ln32w_q(%rip), %ymm2, %ymm2
	vpmulhw .Ln32w_q(%rip), %ymm3, %ymm3
	vpsubw %ymm0, %ymm9, %ymm9
	vpsubw %ymm1, %ymm11, %ymm11
	vpsubw %ymm2, %ymm13, %ymm13
	vpsubw %ymm3, %ymm15, %ymm15
	vpsubw %ymm9, %ymm8, %ymm0
	vpsubw %ymm11, %ymm10, %ymm1
	vpsubw %ymm13, %ymm12, %ymm2
	vpsubw %ymm15, %ymm14, %ymm3
	vpaddw %ymm9, %ymm8, %ymm8
	vpaddw %ymm11, %ymm10, %ymm10
	vpaddw %ymm13, %ymm12, %ymm12
	vpaddw %ymm15, %ymm14, %ymm14
	vmovdqa %ymm0, %ymm9
	vmovdqa %ymm1, %ymm11
	vmovdqa %ymm2, %ymm13
	vmovdqa %ymm3, %ymm15

	vmovdqu %ymm8,  256(%rdi)
	vmovdqu %ymm9,  288(%rdi)
	vmovdqu %ymm10, 320(%rdi)
	vmovdqu %ymm11, 352(%rdi)
	vmovdqu %ymm12, 384(%rdi)
	vmovdqu %ymm13, 416(%rdi)
	vmovdqu %ymm14, 448(%rdi)
	vmovdqu %ymm15, 480(%rdi)
	addq $32, %rsp
	vzeroupper
	ret
	.size gt32_n32_wave_s1s3_c2_asm,.-gt32_n32_wave_s1s3_c2_asm

	/* Twelve correction multiplies with q as a memory source. */
	.p2align 5
	.globl gt32_n32_branch1_qmem_asm
	.type gt32_n32_branch1_qmem_asm,@function
gt32_n32_branch1_qmem_asm:
	vmovdqu   0(%rsi), %ymm4
	vmovdqu  32(%rsi), %ymm5
	vmovdqu  64(%rsi), %ymm6
	vmovdqu  96(%rsi), %ymm7
	vmovdqu 128(%rsi), %ymm8
	vmovdqu 160(%rsi), %ymm9
	vmovdqu 192(%rsi), %ymm10
	vmovdqu 224(%rsi), %ymm11
	W_MONT_EXPLICIT_MEMQ %ymm4,%ymm8,%ymm5,%ymm9,%ymm6,%ymm10,%ymm7,%ymm11, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32w_s2_qinv,.Ln32w_s2_factor
	W_MONT_EXPLICIT_MEMQ %ymm4,%ymm6,%ymm5,%ymm7,%ymm8,%ymm10,%ymm9,%ymm11, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32w_s3_qinv,.Ln32w_s3_factor
	W_MONT_EXPLICIT_MEMQ %ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10,%ymm11, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32w_s2_qinv,.Ln32w_s2_factor
	vmovdqu %ymm4,   0(%rdi)
	vmovdqu %ymm5,  32(%rdi)
	vmovdqu %ymm6,  64(%rdi)
	vmovdqu %ymm7,  96(%rdi)
	vmovdqu %ymm8, 128(%rdi)
	vmovdqu %ymm9, 160(%rdi)
	vmovdqu %ymm10,192(%rdi)
	vmovdqu %ymm11,224(%rdi)
	vzeroupper
	ret
	.size gt32_n32_branch1_qmem_asm,.-gt32_n32_branch1_qmem_asm

	/* Same DAG, with one q load and register-source correction multiplies. */
	.p2align 5
	.globl gt32_n32_branch1_qreg_asm
	.type gt32_n32_branch1_qreg_asm,@function
gt32_n32_branch1_qreg_asm:
	vmovdqa .Ln32w_q(%rip), %ymm15
	vmovdqu   0(%rsi), %ymm4
	vmovdqu  32(%rsi), %ymm5
	vmovdqu  64(%rsi), %ymm6
	vmovdqu  96(%rsi), %ymm7
	vmovdqu 128(%rsi), %ymm8
	vmovdqu 160(%rsi), %ymm9
	vmovdqu 192(%rsi), %ymm10
	vmovdqu 224(%rsi), %ymm11
	W_MONT_EXPLICIT_QREG %ymm4,%ymm8,%ymm5,%ymm9,%ymm6,%ymm10,%ymm7,%ymm11, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32w_s2_qinv,.Ln32w_s2_factor
	W_MONT_EXPLICIT_QREG %ymm4,%ymm6,%ymm5,%ymm7,%ymm8,%ymm10,%ymm9,%ymm11, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32w_s3_qinv,.Ln32w_s3_factor
	W_MONT_EXPLICIT_QREG %ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9,%ymm10,%ymm11, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32w_s2_qinv,.Ln32w_s2_factor
	vmovdqu %ymm4,   0(%rdi)
	vmovdqu %ymm5,  32(%rdi)
	vmovdqu %ymm6,  64(%rdi)
	vmovdqu %ymm7,  96(%rdi)
	vmovdqu %ymm8, 128(%rdi)
	vmovdqu %ymm9, 160(%rdi)
	vmovdqu %ymm10,192(%rdi)
	vmovdqu %ymm11,224(%rdi)
	vzeroupper
	ret
	.size gt32_n32_branch1_qreg_asm,.-gt32_n32_branch1_qreg_asm

	/* Six-blend standard route over all 16 DFT3 components. */
	.p2align 5
	.globl gt32_n32_suffix_route6_control_asm
	.type gt32_n32_suffix_route6_control_asm,@function
gt32_n32_suffix_route6_control_asm:
	movl $16, %ecx
.Ln32w_route6_loop:
	vmovdqu  0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vpblendd $0x0c, %ymm1, %ymm0, %ymm3
	vpblendd $0x30, %ymm2, %ymm3, %ymm3
	vpblendd $0x0c, %ymm0, %ymm2, %ymm4
	vpblendd $0x30, %ymm1, %ymm4, %ymm4
	vpblendd $0x0c, %ymm2, %ymm1, %ymm5
	vpblendd $0x30, %ymm0, %ymm5, %ymm5
	vmovdqu %ymm3,  0(%rdi)
	vmovdqu %ymm4, 32(%rdi)
	vmovdqu %ymm5, 64(%rdi)
	addq $96, %rsi
	addq $96, %rdi
	decl %ecx
	jne .Ln32w_route6_loop
	vzeroupper
	ret
	.size gt32_n32_suffix_route6_control_asm,.-gt32_n32_suffix_route6_control_asm

	/* Five-blend route; the high half carries the typed k3=1/2 swap. */
	.p2align 5
	.globl gt32_n32_suffix_route5_half_asm
	.type gt32_n32_suffix_route5_half_asm,@function
gt32_n32_suffix_route5_half_asm:
	movl $16, %ecx
.Ln32w_route5_loop:
	vmovdqu  0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vpblendd $0x0c, %ymm1, %ymm0, %ymm3
	vpblendd $0x30, %ymm2, %ymm3, %ymm3
	vpblendd $0xc0, %ymm1, %ymm0, %ymm4
	vpblendd $0x03, %ymm2, %ymm4, %ymm4
	vpblendd $0xcc, %ymm2, %ymm1, %ymm5
	vmovdqu %ymm3,  0(%rdi)
	vmovdqu %ymm4, 32(%rdi)
	vmovdqu %ymm5, 64(%rdi)
	addq $96, %rsi
	addq $96, %rdi
	decl %ecx
	jne .Ln32w_route5_loop
	vzeroupper
	ret
	.size gt32_n32_suffix_route5_half_asm,.-gt32_n32_suffix_route5_half_asm

	.section .rodata
	.p2align 5
.Ln32w_q:
	.rept 16
	.short 3457
	.endr

#include "../generated/tile4_constants.inc"

/* Local aliases for the first four vectors of the qualified NTT32 tables. */
	.set .Ln32w_s2_qinv, .Ltile4_fwd_s2_qinv
	.set .Ln32w_s2_factor, .Ltile4_fwd_s2_factor
	.set .Ln32w_s3_qinv, .Ltile4_fwd_s3_qinv
	.set .Ln32w_s3_factor, .Ltile4_fwd_s3_factor

	.section .note.GNU-stack,"",@progbits
