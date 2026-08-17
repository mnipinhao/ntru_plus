#include "../generated/tile4_soa_to_official_routes.inc"

	.macro TILE4_PACK_OFFICIAL8 output_offset
	/* Unchanged Official centered reduction for eight input vectors. */
	vpmulhrsw %ymm15, %ymm0, %ymm10
	vpmulhrsw %ymm15, %ymm1, %ymm11
	vpmulhrsw %ymm15, %ymm2, %ymm12
	vpmulhrsw %ymm15, %ymm3, %ymm13
	vpmullw %ymm14, %ymm10, %ymm10
	vpmullw %ymm14, %ymm11, %ymm11
	vpmullw %ymm14, %ymm12, %ymm12
	vpmullw %ymm14, %ymm13, %ymm13
	vpsubw %ymm10, %ymm0, %ymm0
	vpsubw %ymm11, %ymm1, %ymm1
	vpsubw %ymm12, %ymm2, %ymm2
	vpsubw %ymm13, %ymm3, %ymm3
	vpmulhrsw %ymm15, %ymm4, %ymm10
	vpmulhrsw %ymm15, %ymm5, %ymm11
	vpmulhrsw %ymm15, %ymm6, %ymm12
	vpmulhrsw %ymm15, %ymm7, %ymm13
	vpmullw %ymm14, %ymm10, %ymm10
	vpmullw %ymm14, %ymm11, %ymm11
	vpmullw %ymm14, %ymm12, %ymm12
	vpmullw %ymm14, %ymm13, %ymm13
	vpsubw %ymm10, %ymm4, %ymm4
	vpsubw %ymm11, %ymm5, %ymm5
	vpsubw %ymm12, %ymm6, %ymm6
	vpsubw %ymm13, %ymm7, %ymm7

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

	/* Unchanged Official 12-bit packing DAG. */
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
	vpblendw $0xAA, %ymm7, %ymm0, %ymm7
	vpblendw $0xAA, %ymm8, %ymm2, %ymm8
	vpblendw $0xAA, %ymm9, %ymm5, %ymm9
	vpsrlq $16, %ymm0, %ymm10
	vpsrlq $16, %ymm2, %ymm11
	vpsrlq $16, %ymm5, %ymm12
	vpblendw $0xAA, %ymm1, %ymm10, %ymm10
	vpblendw $0xAA, %ymm4, %ymm11, %ymm11
	vpblendw $0xAA, %ymm6, %ymm12, %ymm12
	vpsllq $32, %ymm8, %ymm0
	vpsllq $32, %ymm10, %ymm1
	vpsllq $32, %ymm12, %ymm2
	vpblendd $0xAA, %ymm0, %ymm7, %ymm0
	vpblendd $0xAA, %ymm1, %ymm9, %ymm1
	vpblendd $0xAA, %ymm2, %ymm11, %ymm2
	vpsrlq $32, %ymm7, %ymm3
	vpsrlq $32, %ymm9, %ymm4
	vpsrlq $32, %ymm11, %ymm5
	vpblendd $0xAA, %ymm8, %ymm3, %ymm3
	vpblendd $0xAA, %ymm10, %ymm4, %ymm4
	vpblendd $0xAA, %ymm12, %ymm5, %ymm5

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

	vmovdqu %ymm0, \output_offset(%rdi)
	vmovdqu %ymm1, \output_offset+32(%rdi)
	vmovdqu %ymm2, \output_offset+64(%rdi)
	vmovdqu %ymm3, \output_offset+96(%rdi)
	vmovdqu %ymm4, \output_offset+128(%rdi)
	vmovdqu %ymm5, \output_offset+160(%rdi)
	.endm

	.text
	.p2align 5
	.globl gt32_tile4_soa_to_official_words_asm
	.type gt32_tile4_soa_to_official_words_asm,@function
gt32_tile4_soa_to_official_words_asm:
	/*
	 * rdi: 48-vector Official coefficient-transposed poly_tobytes input.
	 * rsi: private BM coefficient-plane SoA in corrected GT leaf order.
	 *
	 * The generated network has fixed public addresses and exactly two
	 * source routes per destination vector.  Canonicalization and 12-bit
	 * packing remain the unchanged Official poly_tobytes responsibility.
	 */
	TILE4_SOA_TO_OFFICIAL_WORDS
	vzeroupper
	ret
	.size gt32_tile4_soa_to_official_words_asm,.-gt32_tile4_soa_to_official_words_asm

	.p2align 5
	.globl gt32_tile4_soa_to_official_words_grouped_asm
	.type gt32_tile4_soa_to_official_words_grouped_asm,@function
gt32_tile4_soa_to_official_words_grouped_asm:
	/* E1: reuse each selected SoA source-half pair for two targets. */
	TILE4_SOA_TO_OFFICIAL_WORDS_GROUPED
	vzeroupper
	ret
	.size gt32_tile4_soa_to_official_words_grouped_asm,.-gt32_tile4_soa_to_official_words_grouped_asm

#if defined(TILE4_ENCODEQ_DIRECT_EXPERIMENT)
	.p2align 5
	.globl gt32_tile4_soa_tobytes_direct_asm
	.type gt32_tile4_soa_tobytes_direct_asm,@function
gt32_tile4_soa_tobytes_direct_asm:
	/* rdi: 1152 output bytes; rsi: corrected-semantic private SoA. */
	vmovdqa _16xv(%rip), %ymm15
	vmovdqa _16xq(%rip), %ymm14
	TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_0
	TILE4_PACK_OFFICIAL8 0
	TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_1
	TILE4_PACK_OFFICIAL8 192
	TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_2
	TILE4_PACK_OFFICIAL8 384
	TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_3
	TILE4_PACK_OFFICIAL8 576
	TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_4
	TILE4_PACK_OFFICIAL8 768
	TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_5
	TILE4_PACK_OFFICIAL8 960
	vzeroupper
	ret
	.size gt32_tile4_soa_tobytes_direct_asm,.-gt32_tile4_soa_tobytes_direct_asm
#endif

	.section .note.GNU-stack,"",@progbits
