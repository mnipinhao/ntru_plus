/*
 * Native-centered Stage345 body shared by the full-forward fused candidates.
 *
 * Live-in:
 *   rdi = native-layout output
 *   rsi = aligned 1536-byte stage2 scratch
 *
 * Clobbers rdx, r9, ymm0..ymm15.  The including function owns the epilogue,
 * so this body deliberately has no call, stack adjustment, vzeroupper, or ret.
 * Constants and twiddle tables are hidden linked-object symbols exported by
 * gt_ntt_stage345_soa.s; keeping one table copy makes the benchmark compare
 * control-flow fusion rather than duplicated rodata placement.
 */

.macro GT_NATIVE_MONT_STAGE_NOCOPY l0, h0, l1, h1, l2, h2, l3, h3, t0, t1, t2, t3, table_offset
	vpmullw \table_offset+0(%rdx),   \h0, \t0
	vpmullw \table_offset+64(%rdx),  \h1, \t1
	vpmullw \table_offset+128(%rdx), \h2, \t2
	vpmullw \table_offset+192(%rdx), \h3, \t3

	vpmulhw \table_offset+32(%rdx),  \h0, \h0
	vpmulhw \table_offset+96(%rdx),  \h1, \h1
	vpmulhw \table_offset+160(%rdx), \h2, \h2
	vpmulhw \table_offset+224(%rdx), \h3, \h3

	vpmulhw gt_ntt_avx2_stage345_q_const(%rip), \t0, \t0
	vpmulhw gt_ntt_avx2_stage345_q_const(%rip), \t1, \t1
	vpmulhw gt_ntt_avx2_stage345_q_const(%rip), \t2, \t2
	vpmulhw gt_ntt_avx2_stage345_q_const(%rip), \t3, \t3

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
.endm

.macro GT_NATIVE_CENTER8_REMAPPED_PARALLEL
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm0,  %ymm1
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm2,  %ymm5
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm4,  %ymm7
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm3,  %ymm9
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm8,  %ymm12
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm10, %ymm13
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm6,  %ymm14
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm11, %ymm15

	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm1,  %ymm1
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm5,  %ymm5
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm7,  %ymm7
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm9,  %ymm9
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm12, %ymm12
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm13, %ymm13
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm14, %ymm14
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm15, %ymm15

	vpsubw %ymm1,  %ymm0,  %ymm0
	vpsubw %ymm5,  %ymm2,  %ymm2
	vpsubw %ymm7,  %ymm4,  %ymm4
	vpsubw %ymm9,  %ymm3,  %ymm3
	vpsubw %ymm12, %ymm8,  %ymm8
	vpsubw %ymm13, %ymm10, %ymm10
	vpsubw %ymm14, %ymm6,  %ymm6
	vpsubw %ymm15, %ymm11, %ymm11
.endm

.macro GT_NATIVE_TRANSPOSE8X8_LAYERS23
	vpunpckldq %ymm10, %ymm8,  %ymm0
	vpunpckhdq %ymm10, %ymm8,  %ymm1
	vpunpckldq %ymm11, %ymm9,  %ymm2
	vpunpckhdq %ymm11, %ymm9,  %ymm3
	vpunpckldq %ymm14, %ymm12, %ymm4
	vpunpckhdq %ymm14, %ymm12, %ymm5
	vpunpckldq %ymm15, %ymm13, %ymm6
	vpunpckhdq %ymm15, %ymm13, %ymm7

	vpunpcklqdq %ymm4, %ymm0, %ymm8
	vpunpckhqdq %ymm4, %ymm0, %ymm9
	vpunpcklqdq %ymm5, %ymm1, %ymm10
	vpunpckhqdq %ymm5, %ymm1, %ymm11
	vpunpcklqdq %ymm6, %ymm2, %ymm12
	vpunpckhqdq %ymm6, %ymm2, %ymm13
	vpunpcklqdq %ymm7, %ymm3, %ymm14
	vpunpckhqdq %ymm7, %ymm3, %ymm15
.endm

.macro GT_NATIVE_TRANSPOSE8X8_REMAPPED
	vpunpcklwd %ymm10, %ymm8, %ymm12
	vpunpckhwd %ymm10, %ymm8, %ymm13
	vpunpcklwd %ymm11, %ymm6, %ymm14
	vpunpckhwd %ymm11, %ymm6, %ymm15

	vpunpcklwd %ymm2, %ymm0, %ymm8
	vpunpckhwd %ymm2, %ymm0, %ymm9
	vpunpcklwd %ymm3, %ymm4, %ymm10
	vpunpckhwd %ymm3, %ymm4, %ymm11

	GT_NATIVE_TRANSPOSE8X8_LAYERS23
.endm

.macro GT_NATIVE_STORE_BATCH_PAIR
	vmovdqu %ymm8,    0(%rdi)
	vmovdqu %ymm9,   32(%rdi)
	vmovdqu %ymm10,  64(%rdi)
	vmovdqu %ymm11,  96(%rdi)
	vmovdqu %ymm12, 128(%rdi)
	vmovdqu %ymm13, 160(%rdi)
	vmovdqu %ymm14, 192(%rdi)
	vmovdqu %ymm15, 224(%rdi)
.endm

.macro GT_NATIVE_STAGE345_BLOCK
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	GT_NATIVE_STAGE345_COMPUTE_PRELOADED
	GT_NATIVE_STORE_BATCH_PAIR
.endm

.macro GT_NATIVE_STAGE345_COMPUTE_PRELOADED
	GT_NATIVE_MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	GT_NATIVE_MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	GT_NATIVE_MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	GT_NATIVE_CENTER8_REMAPPED_PARALLEL
	GT_NATIVE_TRANSPOSE8X8_REMAPPED
.endm

/*
 * Matching consumer for the no-checkpoint fused frontend.  After stage 3 the
 * four stage-4 low arms are ymm0/ymm1/ymm8/ymm9; ymm4..ymm7 are dead and can
 * hold the exact center10 quotients.  Centering only those four operands keeps
 * the following add arms inside int16 while halving the number of delayed
 * reducers (24 here versus 48 in the frontend checkpoint).  With final_center
 * zero, the generated terminal contract is 10172 for row01 batches and 9992
 * for row2 batches; both fit GTN-L3 and direct native baseinv.
 */
.macro GT_NATIVE_STAGE345_COMPUTE_PRELOADED_DELAYED_CENTER final_center=1
	GT_NATIVE_MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0

	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm0, %ymm4
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm1, %ymm5
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm8, %ymm6
	vpmulhrsw gt_ntt_avx2_stage345_center10_const(%rip), %ymm9, %ymm7
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm4, %ymm4
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm5, %ymm5
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm6, %ymm6
	vpmullw gt_ntt_avx2_stage345_q_const(%rip), %ymm7, %ymm7
	vpsubw %ymm4, %ymm0, %ymm0
	vpsubw %ymm5, %ymm1, %ymm1
	vpsubw %ymm6, %ymm8, %ymm8
	vpsubw %ymm7, %ymm9, %ymm9

	GT_NATIVE_MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	GT_NATIVE_MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	.if \final_center == 2
	testb $1, %r11b
	jz .Lgt_native_skip_final_center_\@
	GT_NATIVE_CENTER8_REMAPPED_PARALLEL
.Lgt_native_skip_final_center_\@:
	.elseif \final_center
	GT_NATIVE_CENTER8_REMAPPED_PARALLEL
	.endif
	GT_NATIVE_TRANSPOSE8X8_REMAPPED
.endm

.macro GT_NATIVE_STAGE345_BODY
	leaq gt_ntt_avx2_stage345_row01_twiddles(%rip), %rdx
	movl $4, %r9d
.p2align 5
.Lgt_native_fused_row01_loop_\@:
	GT_NATIVE_STAGE345_BLOCK
	addq $256, %rsi
	addq $768, %rdx
	addq $256, %rdi
	decl %r9d
	jne .Lgt_native_fused_row01_loop_\@

	leaq gt_ntt_avx2_stage345_row2_twiddles(%rip), %rdx
	movl $2, %r9d
.p2align 5
.Lgt_native_fused_row2_loop_\@:
	GT_NATIVE_STAGE345_BLOCK
	addq $256, %rsi
	addq $768, %rdx
	addq $256, %rdi
	decl %r9d
	jne .Lgt_native_fused_row2_loop_\@
.endm

/*
 * NTTRU-style producer/consumer overlap candidate.  Once a block has reached
 * native layout, ymm8..ymm15 hold all eight output vectors and ymm0..ymm7 are
 * dead.  Fill those dead registers from the next 256-byte stage2 block while
 * the current eight vectors are being retired to memory.  The sixth block has
 * a store-only epilogue, so the body never reads past the 1536-byte scratch.
 */
.macro GT_NATIVE_STAGE345_PIPELINED_BODY delayed_center=0, contiguous_twiddles=0, final_center=1
	leaq gt_ntt_avx2_stage345_row01_twiddles(%rip), %rdx
	movl $6, %r9d

	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

.p2align 5
.Lgt_native_fused_pipelined_loop_\@:
	.if \delayed_center
	GT_NATIVE_STAGE345_COMPUTE_PRELOADED_DELAYED_CENTER \final_center
	.else
	GT_NATIVE_STAGE345_COMPUTE_PRELOADED
	.endif
	decl %r9d
	je .Lgt_native_fused_pipelined_final_store_\@

	vmovdqa 256(%rsi), %ymm0
	vmovdqu %ymm8,    0(%rdi)
	vmovdqa 288(%rsi), %ymm1
	vmovdqu %ymm9,   32(%rdi)
	vmovdqa 320(%rsi), %ymm2
	vmovdqu %ymm10,  64(%rdi)
	vmovdqa 352(%rsi), %ymm3
	vmovdqu %ymm11,  96(%rdi)
	vmovdqa 384(%rsi), %ymm4
	vmovdqu %ymm12, 128(%rdi)
	vmovdqa 416(%rsi), %ymm5
	vmovdqu %ymm13, 160(%rdi)
	vmovdqa 448(%rsi), %ymm6
	vmovdqu %ymm14, 192(%rdi)
	vmovdqa 480(%rsi), %ymm7
	vmovdqu %ymm15, 224(%rdi)

	addq $256, %rsi
	addq $256, %rdi
	.if \contiguous_twiddles
	addq $768, %rdx
	jmp .Lgt_native_fused_pipelined_loop_\@
	.else
	cmpl $2, %r9d
	je .Lgt_native_fused_pipelined_row2_\@
	addq $768, %rdx
	jmp .Lgt_native_fused_pipelined_loop_\@

.Lgt_native_fused_pipelined_row2_\@:
	leaq gt_ntt_avx2_stage345_row2_twiddles(%rip), %rdx
	jmp .Lgt_native_fused_pipelined_loop_\@
	.endif

.Lgt_native_fused_pipelined_final_store_\@:
	GT_NATIVE_STORE_BATCH_PAIR
.endm
