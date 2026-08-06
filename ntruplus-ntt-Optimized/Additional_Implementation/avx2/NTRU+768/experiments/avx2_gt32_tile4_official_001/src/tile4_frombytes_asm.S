/*
 * P1-V decoder controls.  The 12-bit unpack and invalid-mask arithmetic are
 * the Official AVX2 shape.  Generator-owned fixed qword stores route each
 * unpacked quartic directly to TILE4 AoS without an Official-layout buffer.
 */

	.text
#include "../generated/tile4_frombytes_aos_stores.inc"

	.macro TILE4_UNPACK_128 base
	vmovdqu \base+0(%rsi), %ymm0
	vmovdqu \base+32(%rsi), %ymm1
	vmovdqu \base+64(%rsi), %ymm2
	vmovdqu \base+96(%rsi), %ymm3
	vmovdqu \base+128(%rsi), %ymm4
	vmovdqu \base+160(%rsi), %ymm5

	vperm2i128 $0x20, %ymm3, %ymm0, %ymm6
	vperm2i128 $0x31, %ymm3, %ymm0, %ymm7
	vperm2i128 $0x20, %ymm4, %ymm1, %ymm8
	vperm2i128 $0x31, %ymm4, %ymm1, %ymm9
	vperm2i128 $0x20, %ymm5, %ymm2, %ymm10
	vperm2i128 $0x31, %ymm5, %ymm2, %ymm11

	vpunpcklqdq %ymm9, %ymm6, %ymm0
	vpunpckhqdq %ymm9, %ymm6, %ymm1
	vpunpcklqdq %ymm10, %ymm7, %ymm2
	vpunpckhqdq %ymm10, %ymm7, %ymm3
	vpunpcklqdq %ymm11, %ymm8, %ymm4
	vpunpckhqdq %ymm11, %ymm8, %ymm5

	vpsllq $32, %ymm3, %ymm8
	vpsrlq $32, %ymm0, %ymm9
	vpsllq $32, %ymm4, %ymm10
	vpsrlq $32, %ymm1, %ymm11
	vpsllq $32, %ymm5, %ymm12
	vpsrlq $32, %ymm2, %ymm13
	vpblendd $0xaa, %ymm8, %ymm0, %ymm8
	vpblendd $0xaa, %ymm3, %ymm9, %ymm9
	vpblendd $0xaa, %ymm10, %ymm1, %ymm10
	vpblendd $0xaa, %ymm4, %ymm11, %ymm11
	vpblendd $0xaa, %ymm12, %ymm2, %ymm12
	vpblendd $0xaa, %ymm5, %ymm13, %ymm13

	vpsllq $16, %ymm11, %ymm0
	vpsrlq $16, %ymm8, %ymm1
	vpsllq $16, %ymm12, %ymm2
	vpsrlq $16, %ymm9, %ymm3
	vpsllq $16, %ymm13, %ymm4
	vpsrlq $16, %ymm10, %ymm5
	vpblendw $0xaa, %ymm0, %ymm8, %ymm0
	vpblendw $0xaa, %ymm11, %ymm1, %ymm1
	vpblendw $0xaa, %ymm2, %ymm9, %ymm2
	vpblendw $0xaa, %ymm12, %ymm3, %ymm3
	vpblendw $0xaa, %ymm4, %ymm10, %ymm4
	vpblendw $0xaa, %ymm13, %ymm5, %ymm5

	vpand %ymm15, %ymm0, %ymm11
	vpand %ymm15, %ymm3, %ymm7
	vpsrlw $12, %ymm0, %ymm0
	vpsrlw $12, %ymm3, %ymm3
	vpsllw $4, %ymm1, %ymm6
	vpsllw $4, %ymm4, %ymm9
	vpxor %ymm6, %ymm0, %ymm0
	vpxor %ymm9, %ymm3, %ymm3
	vpand %ymm15, %ymm0, %ymm12
	vpand %ymm15, %ymm3, %ymm8
	vpsrlw $8, %ymm1, %ymm0
	vpsrlw $8, %ymm4, %ymm3
	vpsllw $8, %ymm2, %ymm1
	vpsllw $8, %ymm5, %ymm4
	vpxor %ymm1, %ymm0, %ymm0
	vpxor %ymm4, %ymm3, %ymm3
	vpand %ymm15, %ymm0, %ymm13
	vpand %ymm15, %ymm3, %ymm9
	vpsrlw $4, %ymm2, %ymm0
	vpsrlw $4, %ymm5, %ymm3
	vpand %ymm15, %ymm0, %ymm14
	vpand %ymm15, %ymm3, %ymm10

	vpmaxuw %ymm12, %ymm11, %ymm0
	vpmaxuw %ymm14, %ymm13, %ymm1
	vpmaxuw %ymm8, %ymm7, %ymm2
	vpmaxuw %ymm10, %ymm9, %ymm3
	vpmaxuw %ymm1, %ymm0, %ymm0
	vpmaxuw %ymm3, %ymm2, %ymm2
	vpmaxuw %ymm2, %ymm0, %ymm0
	vpcmpgtw _16xqm1(%rip), %ymm0, %ymm0
	vpmovmskb %ymm0, %edx
	orl %edx, %eax
	.endm

	.macro TILE4_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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

	.macro TILE4_TRANSPOSE_PAIR offset
	vmovdqu \offset+0(%rdi), %ymm0
	vmovdqu \offset+32(%rdi), %ymm1
	vmovdqu \offset+64(%rdi), %ymm2
	vmovdqu \offset+96(%rdi), %ymm3
	vmovdqu \offset+128(%rdi), %ymm4
	vmovdqu \offset+160(%rdi), %ymm5
	vmovdqu \offset+192(%rdi), %ymm6
	vmovdqu \offset+224(%rdi), %ymm7

	vpunpcklwd %ymm1, %ymm0, %ymm8
	vpunpckhwd %ymm1, %ymm0, %ymm9
	vpunpcklwd %ymm3, %ymm2, %ymm10
	vpunpckhwd %ymm3, %ymm2, %ymm11
	vpunpcklwd %ymm5, %ymm4, %ymm12
	vpunpckhwd %ymm5, %ymm4, %ymm13
	vpunpcklwd %ymm7, %ymm6, %ymm14
	vpunpckhwd %ymm7, %ymm6, %ymm15

	vpunpckldq %ymm10, %ymm8, %ymm0
	vpunpckhdq %ymm10, %ymm8, %ymm1
	vpunpckldq %ymm11, %ymm9, %ymm2
	vpunpckhdq %ymm11, %ymm9, %ymm3
	vpunpckldq %ymm14, %ymm12, %ymm4
	vpunpckhdq %ymm14, %ymm12, %ymm5
	vpunpckldq %ymm15, %ymm13, %ymm6
	vpunpckhdq %ymm15, %ymm13, %ymm7

	vpunpcklqdq %ymm2, %ymm0, %ymm8
	vpunpckhqdq %ymm2, %ymm0, %ymm9
	vpunpcklqdq %ymm3, %ymm1, %ymm10
	vpunpckhqdq %ymm3, %ymm1, %ymm11
	vpunpcklqdq %ymm6, %ymm4, %ymm12
	vpunpckhqdq %ymm6, %ymm4, %ymm13
	vpunpcklqdq %ymm7, %ymm5, %ymm14
	vpunpckhqdq %ymm7, %ymm5, %ymm15

	vmovdqu %ymm8, \offset+0(%rdi)
	vmovdqu %ymm9, \offset+32(%rdi)
	vmovdqu %ymm10, \offset+64(%rdi)
	vmovdqu %ymm11, \offset+96(%rdi)
	vmovdqu %ymm12, \offset+128(%rdi)
	vmovdqu %ymm13, \offset+160(%rdi)
	vmovdqu %ymm14, \offset+192(%rdi)
	vmovdqu %ymm15, \offset+224(%rdi)
	.endm

	.p2align 5
.Ltile4_frombytes_aos_body:
	vmovdqa _low_mask(%rip), %ymm15
	xorl %eax, %eax
	TILE4_UNPACK_128 0
	TILE4_STORE_AOS_CHUNK_0
	TILE4_UNPACK_128 192
	TILE4_STORE_AOS_CHUNK_1
	TILE4_UNPACK_128 384
	TILE4_STORE_AOS_CHUNK_2
	TILE4_UNPACK_128 576
	TILE4_STORE_AOS_CHUNK_3
	TILE4_UNPACK_128 768
	TILE4_STORE_AOS_CHUNK_4
	TILE4_UNPACK_128 960
	TILE4_STORE_AOS_CHUNK_5
	ret

	.p2align 5
	.globl gt32_tile4_frombytes_aos_asm
	.type gt32_tile4_frombytes_aos_asm,@function
gt32_tile4_frombytes_aos_asm:
	call .Ltile4_frombytes_aos_body
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_tile4_frombytes_aos_asm,.-gt32_tile4_frombytes_aos_asm

	.p2align 5
	.globl gt32_tile4_frombytes_bm_soa_aos_control_asm
	.type gt32_tile4_frombytes_bm_soa_aos_control_asm,@function
gt32_tile4_frombytes_bm_soa_aos_control_asm:
	call .Ltile4_frombytes_aos_body
	TILE4_TRANSPOSE_PAIR 0
	TILE4_TRANSPOSE_PAIR 256
	TILE4_TRANSPOSE_PAIR 512
	TILE4_TRANSPOSE_PAIR 768
	TILE4_TRANSPOSE_PAIR 1024
	TILE4_TRANSPOSE_PAIR 1280
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_tile4_frombytes_bm_soa_aos_control_asm,.-gt32_tile4_frombytes_bm_soa_aos_control_asm

	.section .note.GNU-stack,"",@progbits
