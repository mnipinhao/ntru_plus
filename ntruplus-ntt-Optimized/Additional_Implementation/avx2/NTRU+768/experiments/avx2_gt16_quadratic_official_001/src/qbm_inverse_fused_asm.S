.text

/* out=rdi, a=rsi, b=rdx.  rcx is a public byte offset. */
.macro MONTREDUCE32 x, tmp
	vpmullw %ymm14, \x, \tmp
	vpand %ymm13, \tmp, \tmp
	vpmaddwd %ymm12, \tmp, \tmp
	vpsubd \tmp, \x, \x
	vpsrad $16, \x, \x
.endm

.macro CENTER_EXACT x, tmp
	vpmulhrsw .Lfq_ten(%rip), \x, \tmp
	vpmullw %ymm15, \tmp, \tmp
	vpsubw \tmp, \x, \x
	vpcmpgtw %ymm8, \x, \tmp
	vpand %ymm15, \tmp, \tmp
	vpsubw \tmp, \x, \x
	vpcmpgtw \x, %ymm9, \tmp
	vpand %ymm15, \tmp, \tmp
	vpaddw \tmp, \x, \x
.endm

/* Produce one centered quartic vector directly from two quadratic QBM pairs. */
.macro QBM_MERGE offset
	vmovdqa (%rsi,\offset), %ymm0
	vmovdqa (%rdx,\offset), %ymm1
	/* Weighted b, then both quadratic products. */
	vpmullw (%r9,\offset), %ymm1, %ymm2
	vpmulhw (%r8,\offset), %ymm1, %ymm3
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm2, %ymm3, %ymm3
	vpmaddwd %ymm3, %ymm0, %ymm4
	vpshufb %ymm11, %ymm1, %ymm5
	vpmaddwd %ymm5, %ymm0, %ymm5
	MONTREDUCE32 %ymm4, %ymm2
	MONTREDUCE32 %ymm5, %ymm2
	vpackssdw %ymm5, %ymm4, %ymm4
	vpshufb %ymm10, %ymm4, %ymm4

	/* Quadratic +/- merge. */
	vpshufb .Lfq_low_dup(%rip), %ymm4, %ymm5
	vpshufb .Lfq_high_dup(%rip), %ymm4, %ymm6
	vpaddw %ymm6, %ymm5, %ymm0
	vpsubw %ymm6, %ymm5, %ymm1
	vpmullw (%r11,\offset), %ymm1, %ymm2
	vpmulhw (%r10,\offset), %ymm1, %ymm3
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm2, %ymm3, %ymm3
	vpblendw $0xcc, %ymm3, %ymm0, %ymm0
	/* This is the first point that must recover the inverse int16 ABI. */
	CENTER_EXACT %ymm0, %ymm2
.endm

.p2align 5
.globl round4c_qbm_inverse_stage1_fused_asm
.type round4c_qbm_inverse_stage1_fused_asm,@function
round4c_qbm_inverse_stage1_fused_asm:
	movq round4c_weight_mont_asm(%rip), %r8
	movq round4c_weight_qinv_asm(%rip), %r9
	movq round4c_merge_mont_asm(%rip), %r10
	movq round4c_merge_qinv_asm(%rip), %r11
	leaq .Lfq_pair_offsets(%rip), %rax
	vpbroadcastw .Lfq_q(%rip), %ymm15
	vpbroadcastw .Lfq_qinv(%rip), %ymm14
	vmovdqu .Lfq_lowmask(%rip), %ymm13
	vmovdqu .Lfq_qpair(%rip), %ymm12
	vmovdqu .Lfq_swap(%rip), %ymm11
	vmovdqu .Lfq_interleave(%rip), %ymm10
	vpbroadcastw .Lfq_center(%rip), %ymm8
	vpbroadcastw .Lfq_negative_center(%rip), %ymm9
.Lfq_pair_loop:
	movzwl (%rax), %ecx
	cmpl $65535, %ecx
	je .Lfq_stage1_done
	QBM_MERGE %rcx
	vmovdqa %ymm0, %ymm7
	addl $256, %ecx
	QBM_MERGE %rcx
	/* Both operands are canonical, so one correction is sufficient. */
	vpaddw %ymm0, %ymm7, %ymm1
	vpsubw %ymm0, %ymm7, %ymm2
	vpcmpgtw %ymm8, %ymm1, %ymm3
	vpand %ymm15, %ymm3, %ymm3
	vpsubw %ymm3, %ymm1, %ymm1
	vpcmpgtw %ymm1, %ymm9, %ymm3
	vpand %ymm15, %ymm3, %ymm3
	vpaddw %ymm3, %ymm1, %ymm1
	vpcmpgtw %ymm8, %ymm2, %ymm3
	vpand %ymm15, %ymm3, %ymm3
	vpsubw %ymm3, %ymm2, %ymm2
	vpcmpgtw %ymm2, %ymm9, %ymm3
	vpand %ymm15, %ymm3, %ymm3
	vpaddw %ymm3, %ymm2, %ymm2
	vmovdqa %ymm1, (%rdi)
	vmovdqa %ymm2, 32(%rdi)
	addq $64, %rdi
	addq $2, %rax
	jmp .Lfq_pair_loop
.Lfq_stage1_done:
	vzeroupper
	ret
.size round4c_qbm_inverse_stage1_fused_asm,.-round4c_qbm_inverse_stage1_fused_asm

/* Four-vector hand schedule for isolating Official-style QBM ILP.  It keeps
 * four independent c1 accumulators live, then reduces c0/c1 pairs together.
 * Output intentionally preserves the ordinary wide QBM representative. */
.macro QBM4_FINISH delta, c1
	vmovdqa \delta(%rsi,%rax), %ymm4
	vmovdqa \delta(%rdx,%rax), %ymm5
	vpmullw \delta(%r9,%rax), %ymm5, %ymm6
	vpmulhw \delta(%r8,%rax), %ymm5, %ymm7
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm7, %ymm7
	vpmaddwd %ymm7, %ymm4, %ymm4
	MONTREDUCE32 %ymm4, %ymm5
	MONTREDUCE32 \c1, %ymm5
	vpackssdw \c1, %ymm4, %ymm4
	vpshufb %ymm10, %ymm4, %ymm4
	vmovdqa %ymm4, \delta(%rdi,%rax)
.endm

.p2align 5
.globl round4c_qbm_wide4_centered_asm
.type round4c_qbm_wide4_centered_asm,@function
round4c_qbm_wide4_centered_asm:
	movl $1, %ecx
	jmp .Lqbm4_start
.size round4c_qbm_wide4_centered_asm,.-round4c_qbm_wide4_centered_asm

.p2align 5
.globl round4c_qbm_wide4_asm
.type round4c_qbm_wide4_asm,@function
round4c_qbm_wide4_asm:
	xorl %ecx, %ecx
.Lqbm4_start:
	movq round4c_weight_mont_asm(%rip), %r8
	movq round4c_weight_qinv_asm(%rip), %r9
	vpbroadcastw .Lfq_q(%rip), %ymm15
	vpbroadcastw .Lfq_qinv(%rip), %ymm14
	vmovdqu .Lfq_lowmask(%rip), %ymm13
	vmovdqu .Lfq_qpair(%rip), %ymm12
	vmovdqu .Lfq_swap(%rip), %ymm11
	vmovdqu .Lfq_interleave(%rip), %ymm10
	xorl %eax, %eax
.Lqbm4_loop:
	/* Four independent c1 chains. */
	vmovdqa   0(%rdx,%rax), %ymm4
	vmovdqa  32(%rdx,%rax), %ymm5
	vmovdqa  64(%rdx,%rax), %ymm6
	vmovdqa  96(%rdx,%rax), %ymm7
	vpshufb %ymm11, %ymm4, %ymm4
	vpshufb %ymm11, %ymm5, %ymm5
	vpshufb %ymm11, %ymm6, %ymm6
	vpshufb %ymm11, %ymm7, %ymm7
	vpmaddwd   0(%rsi,%rax), %ymm4, %ymm0
	vpmaddwd  32(%rsi,%rax), %ymm5, %ymm1
	vpmaddwd  64(%rsi,%rax), %ymm6, %ymm2
	vpmaddwd  96(%rsi,%rax), %ymm7, %ymm3
	QBM4_FINISH 0, %ymm0
	QBM4_FINISH 32, %ymm1
	QBM4_FINISH 64, %ymm2
	QBM4_FINISH 96, %ymm3
	addq $128, %rax
	cmpq $1536, %rax
	jne .Lqbm4_loop
	testl %ecx, %ecx
	jz .Lqbm4_done
	/* Control candidate: exact centered boundary after the faster QBM core. */
	vpbroadcastw .Lfq_center(%rip), %ymm8
	vpbroadcastw .Lfq_negative_center(%rip), %ymm9
	xorl %eax, %eax
.Lqbm4_center_loop:
	vmovdqa (%rdi,%rax), %ymm0
	CENTER_EXACT %ymm0, %ymm2
	vmovdqa %ymm0, (%rdi,%rax)
	addq $32, %rax
	cmpq $1536, %rax
	jne .Lqbm4_center_loop
.Lqbm4_done:
	vzeroupper
	ret
.size round4c_qbm_wide4_asm,.-round4c_qbm_wide4_asm

.section .rodata
.p2align 5
.Lfq_q: .short 3457
.Lfq_qinv: .short 12929
.Lfq_center: .short 1728
.Lfq_negative_center: .short -1728
.Lfq_ten: .rept 16; .short 10; .endr
.Lfq_lowmask: .rept 8; .long 65535; .endr
.Lfq_qpair: .rept 8; .long 3457; .endr
.Lfq_swap:
	.byte 2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13
	.byte 2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13
.Lfq_interleave:
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
.Lfq_low_dup:
	.byte 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
	.byte 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
.Lfq_high_dup:
	.byte 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15
	.byte 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15
/* byte offsets for bitreverse3[k], k=0..7, repeated for each k3 row. */
.Lfq_pair_offsets:
	.short 0,128,64,192,32,160,96,224
	.short 512,640,576,704,544,672,608,736
	.short 1024,1152,1088,1216,1056,1184,1120,1248
	.short 65535

.section .note.GNU-stack,"",@progbits
