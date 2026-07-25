/*
 * Direct GTN16-to-WIRE12 pack.
 *
 * The generated schedule gathers each production four-lane chunk from one
 * native XMM half.  Four chunks reconstruct each sign vector; the unchanged
 * production PACK_GROUP body then canonicalizes and serializes the two signs.
 */

.macro GT_GATHER_COEFFICIENT coff, out0, out1, \
	o0, m0, o1, m1, o2, m2, o3, m3
	vmovdqu \o0+\coff(%rsi), %xmm8
	vpshufb \m0(%rip), %xmm8, %xmm8

	vmovdqu \o1+\coff(%rsi), %xmm9
	vpshufb \m1(%rip), %xmm9, %xmm9

	vmovdqu \o2+\coff(%rsi), %xmm10
	vpshufb \m2(%rip), %xmm10, %xmm10

	vmovdqu \o3+\coff(%rsi), %xmm11
	vpshufb \m3(%rip), %xmm11, %xmm11

	vpunpcklqdq %xmm9, %xmm8, %xmm12
	vpunpckhqdq %xmm9, %xmm8, %xmm13
	vpunpcklqdq %xmm11, %xmm10, %xmm9
	vpunpckhqdq %xmm11, %xmm10, %xmm10
	vinserti128 $1, %xmm9, %ymm12, \out0
	vinserti128 $1, %xmm10, %ymm13, \out1
.endm

.macro GT_GATHER_COEFFICIENT_PAIRED coff, out0, out1, \
	o0, m0, o1, m1
	vmovdqu \o0+\coff(%rsi), %ymm8
	vpshufb \m0(%rip), %ymm8, %ymm9

	vmovdqu \o1+\coff(%rsi), %ymm8
	vpshufb \m1(%rip), %ymm8, %ymm10

	vpunpcklqdq %ymm10, %ymm9, %ymm11
	vpunpckhqdq %ymm10, %ymm9, %ymm12
	vpermq $0x1e, %ymm11, \out0
	vpermq $0x1e, %ymm12, \out1
.endm

.macro GT_CANONICALIZE_GENERAL
	vpmulhw %ymm15, %ymm0, %ymm10
	vpmulhw %ymm15, %ymm1, %ymm11
	vpmulhw %ymm15, %ymm2, %ymm12
	vpmulhw %ymm15, %ymm3, %ymm13
	vpsraw $10, %ymm10, %ymm10
	vpsraw $10, %ymm11, %ymm11
	vpsraw $10, %ymm12, %ymm12
	vpsraw $10, %ymm13, %ymm13
	vpmullw %ymm14, %ymm10, %ymm10
	vpmullw %ymm14, %ymm11, %ymm11
	vpmullw %ymm14, %ymm12, %ymm12
	vpmullw %ymm14, %ymm13, %ymm13
	vpsubw %ymm10, %ymm0, %ymm0
	vpsubw %ymm11, %ymm1, %ymm1
	vpsubw %ymm12, %ymm2, %ymm2
	vpsubw %ymm13, %ymm3, %ymm3

	vpmulhw %ymm15, %ymm4, %ymm10
	vpmulhw %ymm15, %ymm5, %ymm11
	vpmulhw %ymm15, %ymm6, %ymm12
	vpmulhw %ymm15, %ymm7, %ymm13
	vpsraw $10, %ymm10, %ymm10
	vpsraw $10, %ymm11, %ymm11
	vpsraw $10, %ymm12, %ymm12
	vpsraw $10, %ymm13, %ymm13
	vpmullw %ymm14, %ymm10, %ymm10
	vpmullw %ymm14, %ymm11, %ymm11
	vpmullw %ymm14, %ymm12, %ymm12
	vpmullw %ymm14, %ymm13, %ymm13
	vpsubw %ymm10, %ymm4, %ymm4
	vpsubw %ymm11, %ymm5, %ymm5
	vpsubw %ymm12, %ymm6, %ymm6
	vpsubw %ymm13, %ymm7, %ymm7

	vpsubw %ymm14, %ymm0, %ymm0
	vpsubw %ymm14, %ymm1, %ymm1
	vpsubw %ymm14, %ymm2, %ymm2
	vpsubw %ymm14, %ymm3, %ymm3
	vpsraw $15, %ymm0, %ymm10
	vpsraw $15, %ymm1, %ymm11
	vpsraw $15, %ymm2, %ymm12
	vpsraw $15, %ymm3, %ymm13
	vpand %ymm14, %ymm10, %ymm10
	vpand %ymm14, %ymm11, %ymm11
	vpand %ymm14, %ymm12, %ymm12
	vpand %ymm14, %ymm13, %ymm13
	vpaddw %ymm10, %ymm0, %ymm0
	vpaddw %ymm11, %ymm1, %ymm1
	vpaddw %ymm12, %ymm2, %ymm2
	vpaddw %ymm13, %ymm3, %ymm3

	vpsubw %ymm14, %ymm4, %ymm4
	vpsubw %ymm14, %ymm5, %ymm5
	vpsubw %ymm14, %ymm6, %ymm6
	vpsubw %ymm14, %ymm7, %ymm7
	vpsraw $15, %ymm4, %ymm10
	vpsraw $15, %ymm5, %ymm11
	vpsraw $15, %ymm6, %ymm12
	vpsraw $15, %ymm7, %ymm13
	vpand %ymm14, %ymm10, %ymm10
	vpand %ymm14, %ymm11, %ymm11
	vpand %ymm14, %ymm12, %ymm12
	vpand %ymm14, %ymm13, %ymm13
	vpaddw %ymm10, %ymm4, %ymm4
	vpaddw %ymm11, %ymm5, %ymm5
	vpaddw %ymm12, %ymm6, %ymm6
	vpaddw %ymm13, %ymm7, %ymm7
.endm

.macro GT_CANONICALIZE_CENTERED
	vpsraw $15, %ymm0, %ymm10
	vpsraw $15, %ymm1, %ymm11
	vpsraw $15, %ymm2, %ymm12
	vpsraw $15, %ymm3, %ymm13
	vpand %ymm14, %ymm10, %ymm10
	vpand %ymm14, %ymm11, %ymm11
	vpand %ymm14, %ymm12, %ymm12
	vpand %ymm14, %ymm13, %ymm13
	vpaddw %ymm10, %ymm0, %ymm0
	vpaddw %ymm11, %ymm1, %ymm1
	vpaddw %ymm12, %ymm2, %ymm2
	vpaddw %ymm13, %ymm3, %ymm3

	vpsraw $15, %ymm4, %ymm10
	vpsraw $15, %ymm5, %ymm11
	vpsraw $15, %ymm6, %ymm12
	vpsraw $15, %ymm7, %ymm13
	vpand %ymm14, %ymm10, %ymm10
	vpand %ymm14, %ymm11, %ymm11
	vpand %ymm14, %ymm12, %ymm12
	vpand %ymm14, %ymm13, %ymm13
	vpaddw %ymm10, %ymm4, %ymm4
	vpaddw %ymm11, %ymm5, %ymm5
	vpaddw %ymm12, %ymm6, %ymm6
	vpaddw %ymm13, %ymm7, %ymm7
.endm

.macro GT_CANONICALIZE_L3
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm0, %ymm10
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm1, %ymm11
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm2, %ymm12
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm3, %ymm13
	vpmullw %ymm14, %ymm10, %ymm10
	vpmullw %ymm14, %ymm11, %ymm11
	vpmullw %ymm14, %ymm12, %ymm12
	vpmullw %ymm14, %ymm13, %ymm13
	vpsubw %ymm10, %ymm0, %ymm0
	vpsubw %ymm11, %ymm1, %ymm1
	vpsubw %ymm12, %ymm2, %ymm2
	vpsubw %ymm13, %ymm3, %ymm3

	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm4, %ymm10
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm5, %ymm11
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm6, %ymm12
	vpmulhrsw .Lgt_native_pack_center10(%rip), %ymm7, %ymm13
	vpmullw %ymm14, %ymm10, %ymm10
	vpmullw %ymm14, %ymm11, %ymm11
	vpmullw %ymm14, %ymm12, %ymm12
	vpmullw %ymm14, %ymm13, %ymm13
	vpsubw %ymm10, %ymm4, %ymm4
	vpsubw %ymm11, %ymm5, %ymm5
	vpsubw %ymm12, %ymm6, %ymm6
	vpsubw %ymm13, %ymm7, %ymm7

	GT_CANONICALIZE_CENTERED
.endm

.macro GT_PACK_WIRE12_GROUP
	vpsllw $12, %ymm1, %ymm10
	vpsllw $12, %ymm5, %ymm11
	vpxor %ymm10, %ymm0, %ymm0
	vpxor %ymm11, %ymm4, %ymm4
	vpsllw $8, %ymm2, %ymm10
	vpsllw $8, %ymm6, %ymm11
	vpsrlw $4, %ymm1, %ymm12
	vpsrlw $4, %ymm5, %ymm13
	vpxor %ymm10, %ymm12, %ymm1
	vpxor %ymm11, %ymm13, %ymm5
	vpsllw $4, %ymm3, %ymm10
	vpsllw $4, %ymm7, %ymm11
	vpsrlw $8, %ymm2, %ymm12
	vpsrlw $8, %ymm6, %ymm13
	vpxor %ymm10, %ymm12, %ymm2
	vpxor %ymm11, %ymm13, %ymm6

	vpslld $16, %ymm1, %ymm7
	vpslld $16, %ymm4, %ymm8
	vpslld $16, %ymm6, %ymm9
	vpblendw $0xaa, %ymm7, %ymm0, %ymm7
	vpblendw $0xaa, %ymm8, %ymm2, %ymm8
	vpblendw $0xaa, %ymm9, %ymm5, %ymm9

	vpsrlq $16, %ymm0, %ymm10
	vpsrlq $16, %ymm2, %ymm11
	vpsrlq $16, %ymm5, %ymm12
	vpblendw $0xaa, %ymm1, %ymm10, %ymm10
	vpblendw $0xaa, %ymm4, %ymm11, %ymm11
	vpblendw $0xaa, %ymm6, %ymm12, %ymm12

	vpsllq $32, %ymm8, %ymm0
	vpsllq $32, %ymm10, %ymm1
	vpsllq $32, %ymm12, %ymm2
	vpblendd $0xaa, %ymm0, %ymm7, %ymm0
	vpblendd $0xaa, %ymm1, %ymm9, %ymm1
	vpblendd $0xaa, %ymm2, %ymm11, %ymm2

	vpsrlq $32, %ymm7, %ymm3
	vpsrlq $32, %ymm9, %ymm4
	vpsrlq $32, %ymm11, %ymm5
	vpblendd $0xaa, %ymm8, %ymm3, %ymm3
	vpblendd $0xaa, %ymm10, %ymm4, %ymm4
	vpblendd $0xaa, %ymm12, %ymm5, %ymm5

	vpunpcklqdq %ymm1, %ymm0, %ymm6
	vpunpcklqdq %ymm3, %ymm2, %ymm7
	vpunpcklqdq %ymm5, %ymm4, %ymm8
	vpunpckhqdq %ymm1, %ymm0, %ymm9
	vpunpckhqdq %ymm3, %ymm2, %ymm10
	vpunpckhqdq %ymm5, %ymm4, %ymm11

	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x20, %ymm9, %ymm8, %ymm1
	vperm2i128 $0x20, %ymm11, %ymm10, %ymm2
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm3
	vperm2i128 $0x31, %ymm9, %ymm8, %ymm4
	vperm2i128 $0x31, %ymm11, %ymm10, %ymm5

	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	add $192, %rdi
.endm

.macro GT_NATIVE_PACK_GROUP \
	o0, m0, o1, m1, o2, m2, o3, m3
	GT_GATHER_COEFFICIENT 0, %ymm0, %ymm4, \
		\o0, \m0, \o1, \m1, \o2, \m2, \o3, \m3
	GT_GATHER_COEFFICIENT 32, %ymm1, %ymm5, \
		\o0, \m0, \o1, \m1, \o2, \m2, \o3, \m3
	GT_GATHER_COEFFICIENT 64, %ymm2, %ymm6, \
		\o0, \m0, \o1, \m1, \o2, \m2, \o3, \m3
	GT_GATHER_COEFFICIENT 96, %ymm3, %ymm7, \
		\o0, \m0, \o1, \m1, \o2, \m2, \o3, \m3
	call *%rax
.endm

.macro GT_NATIVE_PACK_GROUP_PAIRED o0, m0, o1, m1
	GT_GATHER_COEFFICIENT_PAIRED 0, %ymm0, %ymm4, \
		\o0, \m0, \o1, \m1
	GT_GATHER_COEFFICIENT_PAIRED 32, %ymm1, %ymm5, \
		\o0, \m0, \o1, \m1
	GT_GATHER_COEFFICIENT_PAIRED 64, %ymm2, %ymm6, \
		\o0, \m0, \o1, \m1
	GT_GATHER_COEFFICIENT_PAIRED 96, %ymm3, %ymm7, \
		\o0, \m0, \o1, \m1
	call *%rax
.endm

.text
.p2align 5
.globl gt_poly_tobytes_native_asm_avx2
.type gt_poly_tobytes_native_asm_avx2, @function
gt_poly_tobytes_native_asm_avx2:
	lea .Lgt_native_pack_general_group(%rip), %rax
	jmp .Lgt_native_pack_common
.size gt_poly_tobytes_native_asm_avx2, .-gt_poly_tobytes_native_asm_avx2

.p2align 4
.globl gt_poly_tobytes_native_l3_asm_avx2
.type gt_poly_tobytes_native_l3_asm_avx2, @function
gt_poly_tobytes_native_l3_asm_avx2:
	lea .Lgt_native_pack_l3_group(%rip), %rax
	jmp .Lgt_native_pack_common
.size gt_poly_tobytes_native_l3_asm_avx2, .-gt_poly_tobytes_native_l3_asm_avx2

.p2align 4
.globl gt_poly_tobytes_native_centered_asm_avx2
.type gt_poly_tobytes_native_centered_asm_avx2, @function
gt_poly_tobytes_native_centered_asm_avx2:
	lea .Lgt_native_pack_centered_group(%rip), %rax
	jmp .Lgt_native_pack_common
.size gt_poly_tobytes_native_centered_asm_avx2, .-gt_poly_tobytes_native_centered_asm_avx2

.Lgt_native_pack_common:
	vmovdqa .Lgt_native_pack_v(%rip), %ymm15
	vmovdqa .Lgt_native_pack_q(%rip), %ymm14

#include "gt_native_pack_asm_tables.inc"

	vzeroupper
	ret

.p2align 5
.Lgt_native_pack_general_group:
	GT_CANONICALIZE_GENERAL
	jmp .Lgt_native_pack_wire12_group

.Lgt_native_pack_l3_group:
	GT_CANONICALIZE_L3
	jmp .Lgt_native_pack_wire12_group

.Lgt_native_pack_centered_group:
	GT_CANONICALIZE_CENTERED

.Lgt_native_pack_wire12_group:
	GT_PACK_WIRE12_GROUP
	ret

.section .note.GNU-stack,"",@progbits
