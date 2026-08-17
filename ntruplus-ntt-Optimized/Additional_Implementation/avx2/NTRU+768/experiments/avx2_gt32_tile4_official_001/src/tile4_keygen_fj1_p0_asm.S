/*
 * GT32-KEYGEN-FJ1-P0-ASM-001, benchmark-only bounded probes.
 *
 * rdi: exact 48-vector Official pack input P0 (1536 bytes)
 * rsi: F0, TILE4 AoS, e=0
 * rdx: J1, TILE4 AoS, e=1
 *
 * S0 redeposits each R1-U source vector directly into eight two-word P0
 * fragments.  S1 retains four R1-U vectors, transposes them in registers,
 * and writes four half-tile degree packets.  Neither symbol materializes an
 * intermediate AoS product polynomial or uses stack/scratch storage.
 */

	.text

	.macro FJ1_R1U_ONE dst,aoff,boff,loff
	vmovdqu \boff(%rdx), %ymm12
	vmovdqu \aoff(%rsi), %ymm13

	/* lambda*b, scale e=1 -> e=1. */
	vpmullw \loff(%r8), %ymm12, %ymm10
	vpmulhw \loff(%rcx), %ymm12, %ymm11
	vpmulhw .Laos_dot_q(%rip), %ymm10, %ymm10
	vpsubw %ymm10, %ymm11, %ymm11

	/* Exact A1/R1-U qword-local quartic dot products. */
	vpblendw $0xee, %ymm11, %ymm12, %ymm10
	vpshufb .Laos_dot_d0(%rip), %ymm10, %ymm9
	vpmaddwd %ymm9, %ymm13, %ymm9
	vpblendw $0xcc, %ymm10, %ymm12, %ymm8
	vpshufb .Laos_dot_d1(%rip), %ymm8, %ymm8
	vpmaddwd %ymm8, %ymm13, %ymm8
	vphaddd %ymm8, %ymm9, %ymm9

	vpblendw $0x88, %ymm10, %ymm12, %ymm8
	vpshufb .Laos_dot_d2(%rip), %ymm8, %ymm8
	vpmaddwd %ymm8, %ymm13, %ymm8
	vpshufb .Laos_dot_d3(%rip), %ymm12, %ymm7
	vpmaddwd %ymm7, %ymm13, %ymm7
	vphaddd %ymm7, %ymm8, %ymm8

	/* REDC16: e=0+1-1=0, unsigned low-word representative. */
	vpmullw .Laos_dot_qinv(%rip), %ymm9, %ymm10
	vpmullw .Laos_dot_qinv(%rip), %ymm8, %ymm11
	vpmulhuw .Laos_dot_q(%rip), %ymm10, %ymm10
	vpmulhuw .Laos_dot_q(%rip), %ymm11, %ymm11
	vpsrad $16, %ymm9, %ymm9
	vpsrad $16, %ymm8, %ymm8
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm11, %ymm8, %ymm8

	vpshufb .Laos_dot_pack_c01(%rip), %ymm9, %ymm9
	vpshufb .Laos_dot_pack_c23(%rip), %ymm8, %ymm8
	vpor %ymm8, %ymm9, \dst
	.endm

	.macro FJ1_TRANSPOSE4
	vpunpcklwd %ymm1, %ymm0, %ymm4
	vpunpckhwd %ymm1, %ymm0, %ymm5
	vpunpcklwd %ymm3, %ymm2, %ymm6
	vpunpckhwd %ymm3, %ymm2, %ymm7
	vpunpckldq %ymm6, %ymm4, %ymm0
	vpunpckhdq %ymm6, %ymm4, %ymm1
	vpunpckldq %ymm7, %ymm5, %ymm2
	vpunpckhdq %ymm7, %ymm5, %ymm3
	vpunpcklqdq %ymm2, %ymm0, %ymm4
	vpunpckhqdq %ymm2, %ymm0, %ymm5
	vpunpcklqdq %ymm3, %ymm1, %ymm6
	vpunpckhqdq %ymm3, %ymm1, %ymm7
	.endm

	/* Route one coefficient plane to two P0 vectors. */
	.macro FJ1_S1_PLANE plane,coff
	vperm2i128 $0x01, \plane, \plane, %ymm8
	vpshufb %ymm14, \plane, %ymm9
	vpshufb %ymm15, %ymm8, %ymm8
	vpor %ymm8, %ymm9, %ymm9
	vmovdqu %xmm9, \coff(%rax)
	vextracti128 $1, %ymm9, \coff+128(%rax)
	.endm

	.p2align 5
	.globl gt32_tile4_keygen_fj1_p0_s0_asm
	.type gt32_tile4_keygen_fj1_p0_s0_asm,@function
gt32_tile4_keygen_fj1_p0_s0_asm:
	leaq .Laos_dot_lambda(%rip), %rcx
	leaq .Laos_dot_lambda_qinv(%rip), %r8
	leaq .Lfj1_s0_routes(%rip), %r9
	movl $48, %r11d
	.p2align 5
.Lfj1_s0_loop:
	FJ1_R1U_ONE %ymm0,0,0,0

	/* The generated pair produces eight adjacent two-word fragments. */
	movzbl 2(%r9), %r10d
	shlq $6, %r10
	leaq .Lfj1_s0_masks(%rip), %rax
	addq %rax, %r10
	vperm2i128 $0x01, %ymm0, %ymm0, %ymm8
	vpshufb 0(%r10), %ymm0, %ymm9
	vpshufb 32(%r10), %ymm8, %ymm8
	vpor %ymm8, %ymm9, %ymm9

	movzwl 0(%r9), %eax
	addq %rdi, %rax
	movzbl 3(%r9), %r10d
	addq %r10, %rax
	vpextrd $0, %xmm9,   0(%rax)
	vpextrd $1, %xmm9,  32(%rax)
	vpextrd $2, %xmm9,  64(%rax)
	vpextrd $3, %xmm9,  96(%rax)
	vextracti128 $1, %ymm9, %xmm10
	vpextrd $0, %xmm10, 128(%rax)
	vpextrd $1, %xmm10, 160(%rax)
	vpextrd $2, %xmm10, 192(%rax)
	vpextrd $3, %xmm10, 224(%rax)

	addq $32, %rsi
	addq $32, %rdx
	addq $32, %rcx
	addq $32, %r8
	addq $4, %r9
	decl %r11d
	jne .Lfj1_s0_loop
	vzeroupper
	ret
	.size gt32_tile4_keygen_fj1_p0_s0_asm,.-gt32_tile4_keygen_fj1_p0_s0_asm

	.p2align 5
	.globl gt32_tile4_keygen_fj1_p0_s1_asm
	.type gt32_tile4_keygen_fj1_p0_s1_asm,@function
gt32_tile4_keygen_fj1_p0_s1_asm:
	leaq .Laos_dot_lambda(%rip), %rcx
	leaq .Laos_dot_lambda_qinv(%rip), %r8
	leaq .Lfj1_s1_routes(%rip), %r9
	movl $12, %r11d
	.p2align 5
.Lfj1_s1_loop:
	FJ1_R1U_ONE %ymm0,0,0,0
	FJ1_R1U_ONE %ymm1,32,32,32
	FJ1_R1U_ONE %ymm2,64,64,64
	FJ1_R1U_ONE %ymm3,96,96,96
	FJ1_TRANSPOSE4

	movzbl 2(%r9), %r10d
	shlq $6, %r10
	leaq .Lfj1_s1_masks(%rip), %rax
	addq %rax, %r10
	vmovdqa 0(%r10), %ymm14
	vmovdqa 32(%r10), %ymm15
	movzwl 0(%r9), %eax
	addq %rdi, %rax
	movzbl 3(%r9), %r10d
	addq %r10, %rax
	FJ1_S1_PLANE %ymm4,0
	FJ1_S1_PLANE %ymm5,32
	FJ1_S1_PLANE %ymm6,64
	FJ1_S1_PLANE %ymm7,96

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rcx
	addq $128, %r8
	addq $4, %r9
	decl %r11d
	jne .Lfj1_s1_loop
	vzeroupper
	ret
	.size gt32_tile4_keygen_fj1_p0_s1_asm,.-gt32_tile4_keygen_fj1_p0_s1_asm

	.section .rodata
#include "../generated/tile4_keygen_fj1_p0_routes.inc"
#include "../generated/tile4_aos_dot_redc16_constants.inc"

	.section .note.GNU-stack,"",@progbits
