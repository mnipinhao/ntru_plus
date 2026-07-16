.text

/*
 * Load two adjacent Q slots for all three Good-Thomas rows.  The generated
 * offset table replaces six runtime modulo-96 calculations per iteration.
 * Low and high polynomial halves are kept separately until the top split.
 */
.macro FRONTEND_LOADS
	movzwl 0(%rdx), %eax
	movzwl 2(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm0
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm0, %ymm0
	vmovq 768(%rsi,%rax), %xmm3
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm3, %ymm3

	movzwl 4(%rdx), %eax
	movzwl 6(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm1
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	vmovq 768(%rsi,%rax), %xmm4
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4

	movzwl 8(%rdx), %eax
	movzwl 10(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm2
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm2, %ymm2
	vmovq 768(%rsi,%rax), %xmm5
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm5, %ymm5
.endm

/*
 * Three independent top-split Montgomery chains are issued together.  This
 * fills the packed-multiply latency without extending any value beyond the
 * proven 3(q-1) DFT3 output bound.
 */
.macro FRONTEND_SPLIT_AND_TWIST
	/* correction lows for Mont(high, zeta_top) */
	vpmullw %ymm14, %ymm3, %ymm6
	vpmullw %ymm14, %ymm4, %ymm7
	vpmullw %ymm14, %ymm5, %ymm8
	/* product highs */
	vpmulhw %ymm13, %ymm3, %ymm9
	vpmulhw %ymm13, %ymm4, %ymm10
	vpmulhw %ymm13, %ymm5, %ymm11
	/* q times the Montgomery corrections */
	vpmulhw %ymm15, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm6, %ymm9, %ymm9
	vpsubw %ymm7, %ymm10, %ymm10
	vpsubw %ymm8, %ymm11, %ymm11

	/* streams = [branch0 lanes 0..3 | branch1 lanes 0..3] per half. */
	vpaddw %ymm9,  %ymm0, %ymm6
	vpaddw %ymm10, %ymm1, %ymm7
	vpaddw %ymm11, %ymm2, %ymm8
	vpaddw %ymm3, %ymm0, %ymm3
	vpaddw %ymm4, %ymm1, %ymm4
	vpaddw %ymm5, %ymm2, %ymm5
	vpsubw %ymm9,  %ymm3, %ymm3
	vpsubw %ymm10, %ymm4, %ymm4
	vpsubw %ymm11, %ymm5, %ymm5
	vpunpcklqdq %ymm3, %ymm6, %ymm6
	vpunpcklqdq %ymm4, %ymm7, %ymm7
	vpunpcklqdq %ymm5, %ymm8, %ymm8

	/* Each 64-byte table entry is [twist*qinv | twist]. */
	vpmullw   0(%r8), %ymm6, %ymm3
	vpmullw  64(%r8), %ymm7, %ymm4
	vpmullw 128(%r8), %ymm8, %ymm5
	vpmulhw  32(%r8), %ymm6, %ymm0
	vpmulhw  96(%r8), %ymm7, %ymm1
	vpmulhw 160(%r8), %ymm8, %ymm2
	vpmulhw %ymm15, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpsubw %ymm3, %ymm0, %ymm0
	vpsubw %ymm4, %ymm1, %ymm1
	vpsubw %ymm5, %ymm2, %ymm2
.endm

.macro FRONTEND_DFT3_STORE
	/* t = Mont(x1-x2, omega3), interleaved with the three DFT sums. */
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4
	vpaddw %ymm2, %ymm6, %ymm6
	vpsubw %ymm4, %ymm5, %ymm5
	vpaddw %ymm5, %ymm7, %ymm7
	vpsubw %ymm5, %ymm8, %ymm8

	/* row01 uses one YMM per Q; row2 remains one XMM per Q. */
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm1
	vmovdqa %ymm0,    0(%rdi,%r9,2)
	vmovdqa %ymm1,   32(%rdi,%r9,2)
	vmovdqa %xmm8, 1024(%rdi,%r9)
	vextracti128 $1, %ymm8, 1040(%rdi,%r9)
.endm

.macro FRONTEND_BODY
	leaq gt_frontend_input_byte_offset(%rip), %rdx
	leaq gt_frontend_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_zeta_top(%rip), %ymm13
	vmovdqa .Lfront_zeta_top_qinv(%rip), %ymm14
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r9d, %r9d
.p2align 5
.Lfrontend_loop\@:
	FRONTEND_LOADS
	FRONTEND_SPLIT_AND_TWIST
	FRONTEND_DFT3_STORE
	addq $12, %rdx
	addq $192, %r8
	addq $32, %r9
	cmpq $512, %r9
	jne .Lfrontend_loop\@
.endm

/*
 * Two breadth-first radix-2 layers.  All Montgomery chains at a dependency
 * level are issued together.  The high input of each butterfly is reduced by
 * its fixed factor; additions remain lazy, giving the existing 4(q-1) and
 * 5(q-1) stage bounds.
 */
.macro STAGE12_BODY
	vmovdqa .Lstage12_row2_factor(%rip), %ymm9
	vmovdqa .Lstage12_row2_qinv(%rip), %ymm10
	vmovdqa .Lstage12_omega8(%rip), %ymm11
	vmovdqa .Lstage12_omega8_qinv(%rip), %ymm12
	vmovdqa .Lstage12_r(%rip), %ymm13
	vmovdqa .Lstage12_r_qinv(%rip), %ymm14
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r8d, %r8d
	xorl %r9d, %r9d
.p2align 5
.Lstage12_loop\@:
	/* row0/row1: Q, Q+8, Q+16, Q+24 */
	vmovdqa   0(%rsi,%r9), %ymm0
	vmovdqa 256(%rsi,%r9), %ymm1
	vmovdqa 512(%rsi,%r9), %ymm2
	vmovdqa 768(%rsi,%r9), %ymm3

	/* Stage 1: identity Montgomery reductions for Q+16 and Q+24. */
	vpmullw %ymm14, %ymm2, %ymm4
	vpmullw %ymm14, %ymm3, %ymm5
	vpmulhw %ymm13, %ymm2, %ymm6
	vpmulhw %ymm13, %ymm3, %ymm7
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpsubw %ymm4, %ymm6, %ymm2
	vpsubw %ymm5, %ymm7, %ymm3
	vpaddw %ymm2, %ymm0, %ymm4
	vpsubw %ymm2, %ymm0, %ymm5
	vpaddw %ymm3, %ymm1, %ymm6
	vpsubw %ymm3, %ymm1, %ymm7

	/* Stage 2: identity and omega^8 chains are independent. */
	vpmullw %ymm14, %ymm6, %ymm8
	vpmullw %ymm12, %ymm7, %ymm2
	vpmulhw %ymm13, %ymm6, %ymm6
	vpmulhw %ymm11, %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm8, %ymm6, %ymm6
	vpsubw %ymm2, %ymm7, %ymm7
	vpaddw %ymm6, %ymm4, %ymm0
	vpsubw %ymm6, %ymm4, %ymm1
	vpaddw %ymm7, %ymm5, %ymm2
	vpsubw %ymm7, %ymm5, %ymm3
	vmovdqa %ymm0,   0(%rdi,%r9)
	vmovdqa %ymm1, 256(%rdi,%r9)
	vmovdqa %ymm2, 512(%rdi,%r9)
	vmovdqa %ymm3, 768(%rdi,%r9)

	/* row2 stage 1: pack [Q | Q+16] and [Q+8 | Q+24]. */
	vmovdqa 1024(%rsi,%r8), %xmm0
	vmovdqa 1152(%rsi,%r8), %xmm1
	vmovdqa 1280(%rsi,%r8), %xmm2
	vmovdqa 1408(%rsi,%r8), %xmm3
	vpmullw %xmm14, %xmm2, %xmm4
	vpmullw %xmm14, %xmm3, %xmm5
	vpmulhw %xmm13, %xmm2, %xmm6
	vpmulhw %xmm13, %xmm3, %xmm7
	vpmulhw %xmm15, %xmm4, %xmm4
	vpmulhw %xmm15, %xmm5, %xmm5
	vpsubw %xmm4, %xmm6, %xmm2
	vpsubw %xmm5, %xmm7, %xmm3
	vpaddw %xmm2, %xmm0, %xmm4
	vpsubw %xmm2, %xmm0, %xmm6
	vinserti128 $1, %xmm6, %ymm4, %ymm4
	vpaddw %xmm3, %xmm1, %xmm5
	vpsubw %xmm3, %xmm1, %xmm7
	vinserti128 $1, %xmm7, %ymm5, %ymm5

	/* row2 stage 2: low half identity, high half omega^8. */
	vpmullw %ymm10, %ymm5, %ymm6
	vpmulhw %ymm9,  %ymm5, %ymm7
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm7, %ymm7
	vpaddw %ymm7, %ymm4, %ymm0
	vpsubw %ymm7, %ymm4, %ymm1
	vmovdqa %ymm0, 1024(%rdi,%r9)
	vmovdqa %ymm1, 1280(%rdi,%r9)

	addq $16, %r8
	addq $32, %r9
	cmpq $256, %r9
	jne .Lstage12_loop\@
.endm

/* Standalone exact-boundary regression entry points. */
.p2align 5
.globl gt_ntt_avx2_frontend_asm
.type gt_ntt_avx2_frontend_asm,@function
gt_ntt_avx2_frontend_asm:
	FRONTEND_BODY
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_asm,.-gt_ntt_avx2_frontend_asm

.p2align 5
.globl gt_ntt_avx2_stage12_asm
.type gt_ntt_avx2_stage12_asm,@function
gt_ntt_avx2_stage12_asm:
	STAGE12_BODY
	vzeroupper
	ret
.size gt_ntt_avx2_stage12_asm,.-gt_ntt_avx2_stage12_asm

/*
 * void gt_ntt_avx2_frontend_stage12_asm(gt_stage2_scratch *out,
 *                                       const int16_t in[768])
 *
 * One aligned semantic frontend scratch is shared by the two inlined regions.
 * There are no internal calls or compiler spill slots.  out==in is safe because
 * the complete polynomial reaches scratch before stage1+2 writes begin.
 */
.p2align 5
.globl gt_ntt_avx2_frontend_stage12_asm
.type gt_ntt_avx2_frontend_stage12_asm,@function
gt_ntt_avx2_frontend_stage12_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp
	movq %rsp, %rdi
	FRONTEND_BODY
	movq %r10, %rdi
	movq %rsp, %rsi
	STAGE12_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_asm,.-gt_ntt_avx2_frontend_stage12_asm

.section .rodata
.p2align 5
.Lfront_q:
	.rept 16
	.short 3457
	.endr
.Lfront_zeta_top:
	.rept 16
	.short -1033
	.endr
.Lfront_zeta_top_qinv:
	.rept 16
	.short 13687
	.endr
.Lfront_omega3:
	.rept 16
	.short -886
	.endr
.Lfront_omega3_qinv:
	.rept 16
	.short 13706
	.endr
.Lstage12_r:
	.rept 16
	.short -147
	.endr
.Lstage12_r_qinv:
	.rept 16
	.short -19
	.endr
.Lstage12_omega8:
	.rept 16
	.short 366
	.endr
.Lstage12_omega8_qinv:
	.rept 16
	.short 13422
	.endr
.Lstage12_row2_factor:
	.rept 8
	.short -147
	.endr
	.rept 8
	.short 366
	.endr
.Lstage12_row2_qinv:
	.rept 8
	.short -19
	.endr
	.rept 8
	.short 13422
	.endr

.section .note.GNU-stack,"",@progbits
