/*
 * Build the standalone development boundaries and the fused entry from the
 * same macro definitions.  This keeps the exact region tests available while
 * preventing a second hand-copied schedule from drifting.
 */
#define GT_INVNTT_FUSED_INCLUDE 1
#include "gt_invntt_ntt32_soa.s"
#include "gt_invntt_dft3_soa.s"
#include "gt_invntt_postprocess_soa.s"
#undef GT_INVNTT_FUSED_INCLUDE

.text

/*
 * void gt_invntt_soa_avx2_fused_asm(int16_t out[768],
 *                                   const int16_t soa[768])
 *
 * A single SysV AMD64 entry owns one 1536-byte, 32-byte-aligned row scratch.
 * r10 preserves out and r11 preserves the incoming stack pointer; both remain
 * live across all three inlined region loops.  out==soa is safe because the
 * complete SoA input reaches scratch before any canonical output store.
 */
.p2align 5
.globl gt_invntt_soa_avx2_fused_asm
.type gt_invntt_soa_avx2_fused_asm,@function
gt_invntt_soa_avx2_fused_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp

	/* Region 1: direct-SoA inverse NTT32 into row scratch. */
	movq %rsp, %rdi
	vmovdqa .Lintt_q(%rip), %ymm14
	vmovdqa .Lintt_barrett_v(%rip), %ymm15
	movl $3, %r8d
.p2align 5
.Lfused_intt_k3_loop:
	movl $4, %ecx
.p2align 5
.Lfused_intt_coefficient_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu 128(%rsi), %ymm1
	vmovdqu 256(%rsi), %ymm2
	vmovdqu 384(%rsi), %ymm3

	INTT_LOCAL_LEN2
	INTT_LOCAL_MONT .Lintt_mask_len4_low, .Lintt_mask_len4_high, .Lintt_twiddle_len4, 0xcc
	INTT_LOCAL_MONT .Lintt_mask_len8_low, .Lintt_mask_len8_high, .Lintt_twiddle_len8, 0xf0
	INTT_LEN16
	INTT_LEN32
	INTT_BARRETT4

	vmovdqa %ymm0,   0(%rdi)
	vmovdqa %ymm1, 128(%rdi)
	vmovdqa %ymm2, 256(%rdi)
	vmovdqa %ymm3, 384(%rdi)
	addq $32, %rsi
	addq $32, %rdi
	decl %ecx
	jne .Lfused_intt_coefficient_loop
	addq $384, %rsi
	addq $384, %rdi
	decl %r8d
	jne .Lfused_intt_k3_loop

	/* Region 2: in-place inverse DFT3 and three packed checkpoints. */
	movq %rsp, %rdi
	vmovdqa .Ldft3_q(%rip), %ymm11
	vmovdqa .Ldft3_barrett_v(%rip), %ymm12
	vmovdqa .Ldft3_omega3_qinv(%rip), %ymm13
	vmovdqa .Ldft3_omega3(%rip), %ymm14
	movl $16, %ecx
.p2align 5
.Lfused_dft3_loop:
	INTT_DFT3_BARRETT
	addq $32, %rdi
	decl %ecx
	jne .Lfused_dft3_loop

	/* Region 3: untwist, merge, normalize, transpose, and final stores. */
	movq %r10, %rdi
	movq %rsp, %rsi
	vmovdqa .Lpost_q(%rip), %ymm15
	leaq gt_inv_untwist(%rip), %r8
	leaq gt_inv_untwist_qinv(%rip), %r9
	leaq gt_inv_output_block(%rip), %rdx
	movl $12, %ecx
.p2align 5
.Lfused_post_group_loop:
	POSTPROCESS_GROUP .Lpost_ninv_pair, .Lpost_2ninv_pair
	addq $128, %rsi
	addq $32, %r8
	addq $32, %r9
	addq $8, %rdx
	decl %ecx
	jne .Lfused_post_group_loop

	movq %r11, %rsp
	vzeroupper
	ret
.size gt_invntt_soa_avx2_fused_asm,.-gt_invntt_soa_avx2_fused_asm

.section .note.GNU-stack,"",@progbits
