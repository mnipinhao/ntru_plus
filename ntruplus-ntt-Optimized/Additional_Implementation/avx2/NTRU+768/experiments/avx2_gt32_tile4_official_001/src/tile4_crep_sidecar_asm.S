.text

/*
 * Benchmark-only production crepmod3 ABI extension.
 *
 * rdi: aligned coefficient-order int16_t m[768], updated in place exactly as
 *      Official poly_crepmod3.
 * rsi: gt32_sotp_sidecar_t { neg[96], nz[96] }.
 *
 * The full m stores remain unchanged.  Sidecar bits are tapped only after the
 * crepmod3 outputs have reached {-1,0,1}; neither T9 nor N5 is modified.
 */

.macro CREP_SIDECAR_BATCH input_offset,side_offset
	vmovdqa \input_offset+0(%rdi), %ymm7
	vmovdqa \input_offset+32(%rdi), %ymm8
	vmovdqa \input_offset+64(%rdi), %ymm9
	vmovdqa \input_offset+96(%rdi), %ymm10

	vpsraw $15, %ymm7, %ymm11
	vpsraw $15, %ymm8, %ymm12
	vpsraw $15, %ymm9, %ymm13
	vpsraw $15, %ymm10, %ymm14
	vpand %ymm0, %ymm11, %ymm11
	vpand %ymm0, %ymm12, %ymm12
	vpand %ymm0, %ymm13, %ymm13
	vpand %ymm0, %ymm14, %ymm14
	vpaddw %ymm11, %ymm7, %ymm7
	vpaddw %ymm12, %ymm8, %ymm8
	vpaddw %ymm13, %ymm9, %ymm9
	vpaddw %ymm14, %ymm10, %ymm10
	vpsubw %ymm1, %ymm7, %ymm7
	vpsubw %ymm1, %ymm8, %ymm8
	vpsubw %ymm1, %ymm9, %ymm9
	vpsubw %ymm1, %ymm10, %ymm10

	vpsraw $15, %ymm7, %ymm11
	vpsraw $15, %ymm8, %ymm12
	vpsraw $15, %ymm9, %ymm13
	vpsraw $15, %ymm10, %ymm14
	vpand %ymm0, %ymm11, %ymm11
	vpand %ymm0, %ymm12, %ymm12
	vpand %ymm0, %ymm13, %ymm13
	vpand %ymm0, %ymm14, %ymm14
	vpaddw %ymm11, %ymm7, %ymm7
	vpaddw %ymm12, %ymm8, %ymm8
	vpaddw %ymm13, %ymm9, %ymm9
	vpaddw %ymm14, %ymm10, %ymm10
	vpsubw %ymm2, %ymm7, %ymm7
	vpsubw %ymm2, %ymm8, %ymm8
	vpsubw %ymm2, %ymm9, %ymm9
	vpsubw %ymm2, %ymm10, %ymm10

	vpmulhrsw %ymm3, %ymm7, %ymm11
	vpmulhrsw %ymm3, %ymm8, %ymm12
	vpmulhrsw %ymm3, %ymm9, %ymm13
	vpmulhrsw %ymm3, %ymm10, %ymm14
	vpmullw %ymm4, %ymm11, %ymm11
	vpmullw %ymm4, %ymm12, %ymm12
	vpmullw %ymm4, %ymm13, %ymm13
	vpmullw %ymm4, %ymm14, %ymm14
	vpsubw %ymm11, %ymm7, %ymm7
	vpsubw %ymm12, %ymm8, %ymm8
	vpsubw %ymm13, %ymm9, %ymm9
	vpsubw %ymm14, %ymm10, %ymm10

	/* Pack coefficient-order words into two consecutive 32-byte bit blocks. */
	vpacksswb %ymm8, %ymm7, %ymm11
	vpacksswb %ymm10, %ymm9, %ymm12
	vpermq $0xd8, %ymm11, %ymm11
	vpermq $0xd8, %ymm12, %ymm12

	/* Preserve the production full-m representation and store schedule. */
	vmovdqa %ymm7, \input_offset+0(%rdi)
	vmovdqa %ymm8, \input_offset+32(%rdi)
	vmovdqa %ymm9, \input_offset+64(%rdi)
	vmovdqa %ymm10, \input_offset+96(%rdi)

	/* -1 has a set byte sign bit; 0 and +1 do not. */
	vpmovmskb %ymm11, %eax
	vpmovmskb %ymm12, %ecx
	movl %eax, \side_offset+0(%rsi)
	movl %ecx, \side_offset+4(%rsi)

	/* For {-1,0,+1}, shifting packed bytes by seven exposes nonzero bits. */
	vpsllw $7, %ymm11, %ymm11
	vpsllw $7, %ymm12, %ymm12
	vpmovmskb %ymm11, %eax
	vpmovmskb %ymm12, %ecx
	movl %eax, 96+\side_offset+0(%rsi)
	movl %ecx, 96+\side_offset+4(%rsi)
.endm

.macro LOAD_CREP_CONSTANTS
	vmovdqa _16xq(%rip), %ymm0
	vmovdqa _16xqp1div2(%rip), %ymm1
	vmovdqa _16xqm1div2(%rip), %ymm2
	vmovdqa _16xv2(%rip), %ymm3
	vmovdqa _16x3(%rip), %ymm4
.endm

.p2align 5
.globl gt32_poly_crepmod3_sidecar_s1_asm
.type gt32_poly_crepmod3_sidecar_s1_asm,@function
gt32_poly_crepmod3_sidecar_s1_asm:
	LOAD_CREP_CONSTANTS
	leaq 1536(%rdi), %r8
.p2align 5
.Lcrep_sidecar_s1_loop:
	CREP_SIDECAR_BATCH 0,0
	addq $128, %rdi
	addq $8, %rsi
	cmpq %r8, %rdi
	jb .Lcrep_sidecar_s1_loop
	ret
.size gt32_poly_crepmod3_sidecar_s1_asm,.-gt32_poly_crepmod3_sidecar_s1_asm

/* Two-batch loop-unrolled control; semantics and stores are identical to S1. */
.p2align 5
.globl gt32_poly_crepmod3_sidecar_s2_asm
.type gt32_poly_crepmod3_sidecar_s2_asm,@function
gt32_poly_crepmod3_sidecar_s2_asm:
	LOAD_CREP_CONSTANTS
	leaq 1536(%rdi), %r8
.p2align 5
.Lcrep_sidecar_s2_loop:
	CREP_SIDECAR_BATCH 0,0
	CREP_SIDECAR_BATCH 128,8
	addq $256, %rdi
	addq $16, %rsi
	cmpq %r8, %rdi
	jb .Lcrep_sidecar_s2_loop
	ret
.size gt32_poly_crepmod3_sidecar_s2_asm,.-gt32_poly_crepmod3_sidecar_s2_asm

.ifndef no_gnu_stack
.section .note.GNU-stack,"",@progbits
.endif
