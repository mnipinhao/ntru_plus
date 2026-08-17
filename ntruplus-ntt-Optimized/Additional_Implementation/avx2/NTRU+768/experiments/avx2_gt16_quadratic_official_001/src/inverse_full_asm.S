.text

/* All entry points are benchmark-only.  The full entry deliberately uses the
 * same private 1536-byte scratch boundary as the C oracle, so this experiment
 * isolates instruction scheduling before attempting a different ABI. */

.macro MONT_VECTOR_MEM x, montbase, qinvbase, tmp
	vpmullw (\qinvbase,%rcx), \x, \tmp
	vpmulhw (\montbase,%rcx), \x, \x
	vpmulhw %ymm15, \tmp, \tmp
	vpsubw \tmp, \x, \x
.endm

.macro CENTER_ONCE x, tmp
	vpcmpgtw %ymm13, \x, \tmp
	vpand %ymm15, \tmp, \tmp
	vpsubw \tmp, \x, \x
	vpcmpgtw \x, %ymm14, \tmp
	vpand %ymm15, \tmp, \tmp
	vpaddw \tmp, \x, \x
.endm

.macro CENTER_TWICE x, tmp
	CENTER_ONCE \x, \tmp
	CENTER_ONCE \x, \tmp
.endm

.macro CENTER_WIDE_EXACT x, tmp
	vpmulhrsw %ymm12, \x, \tmp
	vpmullw %ymm15, \tmp, \tmp
	vpsubw \tmp, \x, \x
	CENTER_ONCE \x, \tmp
.endm

/* Load and undo one quadratic split at the public vector byte offset in rcx.
 * Result is returned in ymm0; ymm2-ymm5 are temporary. */
.macro MERGE_CURRENT
	vmovdqa (%rsi,%rcx), %ymm0
	vpshufb .Lif_plus_dup(%rip), %ymm0, %ymm2
	vpshufb .Lif_minus_dup(%rip), %ymm0, %ymm3
	vpaddw %ymm3, %ymm2, %ymm4
	vpsubw %ymm3, %ymm2, %ymm0
	vpmullw (%r9,%rcx), %ymm0, %ymm2
	vpmulhw (%r8,%rcx), %ymm0, %ymm0
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm2, %ymm0, %ymm0
	vpblendw $0xcc, %ymm0, %ymm4, %ymm0
.endm

.p2align 5
.globl round4c_inverse_stage1_asm
.type round4c_inverse_stage1_asm,@function
round4c_inverse_stage1_asm:
	xorl %r10d, %r10d
	jmp .Lif_stage1_body
.Lif_stage1_internal:
	movl $1, %r10d
.Lif_stage1_body:
	movq round4c_merge_mont_asm(%rip), %r8
	movq round4c_merge_qinv_asm(%rip), %r9
	leaq .Lif_pair_offsets(%rip), %rax
	movl $24, %edx
	vmovdqa .Lif_plus_dup(%rip), %ymm10
	vmovdqa .Lif_minus_dup(%rip), %ymm11
	vpbroadcastw .Lif_q(%rip), %ymm15
	vpbroadcastw .Lif_center(%rip), %ymm13
	vpbroadcastw .Lif_negative_center(%rip), %ymm14
.Lif_stage1_loop:
	movzwl (%rax), %ecx
	/* Schedule both (k,k+8) quadratic merges together.  This exposes two
	 * independent Montgomery chains instead of serializing low then high. */
	vmovdqa   0(%rsi,%rcx), %ymm0
	vmovdqa 256(%rsi,%rcx), %ymm1
	vpshufb %ymm10, %ymm0, %ymm2
	vpshufb %ymm11, %ymm0, %ymm3
	vpshufb %ymm10, %ymm1, %ymm4
	vpshufb %ymm11, %ymm1, %ymm5
	vpaddw %ymm3, %ymm2, %ymm6
	vpsubw %ymm3, %ymm2, %ymm2
	vpaddw %ymm5, %ymm4, %ymm7
	vpsubw %ymm5, %ymm4, %ymm4
	vpmullw   0(%r9,%rcx), %ymm2, %ymm3
	vpmullw 256(%r9,%rcx), %ymm4, %ymm5
	vpmulhw   0(%r8,%rcx), %ymm2, %ymm2
	vpmulhw 256(%r8,%rcx), %ymm4, %ymm4
	vpmulhw %ymm15, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm5, %ymm5
	vpsubw %ymm3, %ymm2, %ymm2
	vpsubw %ymm5, %ymm4, %ymm4
	vpblendw $0xcc, %ymm2, %ymm6, %ymm6
	vpblendw $0xcc, %ymm4, %ymm7, %ymm7
	vpaddw %ymm7, %ymm6, %ymm0
	vpsubw %ymm7, %ymm6, %ymm1
	CENTER_TWICE %ymm0, %ymm2
	CENTER_TWICE %ymm1, %ymm2
	vmovdqa %ymm0, 0(%rdi)
	vmovdqa %ymm1, 32(%rdi)
	addq $64, %rdi
	addq $2, %rax
	decl %edx
	jne .Lif_stage1_loop
.Lif_stage1_done:
	testl %r10d, %r10d
	jnz .Lif_stage1_ret
	vzeroupper
.Lif_stage1_ret:
	ret
.size round4c_inverse_stage1_asm,.-round4c_inverse_stage1_asm

/* The N4 QBM may retain its R^-1 representative in [-9793,9793].  Fold the
 * required representative repair into the stage-1 loads, avoiding a separate
 * 1536-byte canonicalization pass between QBM and inverse. */
.p2align 5
.globl round4c_inverse_stage1_wide_asm
.type round4c_inverse_stage1_wide_asm,@function
round4c_inverse_stage1_wide_asm:
	xorl %r10d, %r10d
	jmp .Lif_stage1_wide_body
.Lif_stage1_wide_internal:
	movl $1, %r10d
.Lif_stage1_wide_body:
	movq round4c_merge_mont_asm(%rip), %r8
	movq round4c_merge_qinv_asm(%rip), %r9
	leaq .Lif_pair_offsets(%rip), %rax
	movl $24, %edx
	vmovdqa .Lif_plus_dup(%rip), %ymm10
	vmovdqa .Lif_minus_dup(%rip), %ymm11
	vmovdqa .Lif_ten(%rip), %ymm12
	vpbroadcastw .Lif_q(%rip), %ymm15
	vpbroadcastw .Lif_center(%rip), %ymm13
	vpbroadcastw .Lif_negative_center(%rip), %ymm14
.Lif_stage1_wide_loop:
	movzwl (%rax), %ecx
	vmovdqa   0(%rsi,%rcx), %ymm0
	vmovdqa 256(%rsi,%rcx), %ymm1
	vpshufb %ymm10, %ymm0, %ymm2
	vpshufb %ymm11, %ymm0, %ymm3
	vpshufb %ymm10, %ymm1, %ymm4
	vpshufb %ymm11, %ymm1, %ymm5
	vpaddw %ymm3, %ymm2, %ymm6
	vpsubw %ymm3, %ymm2, %ymm2
	vpaddw %ymm5, %ymm4, %ymm7
	vpsubw %ymm5, %ymm4, %ymm4
	vpmullw   0(%r9,%rcx), %ymm2, %ymm3
	vpmullw 256(%r9,%rcx), %ymm4, %ymm5
	vpmulhw   0(%r8,%rcx), %ymm2, %ymm2
	vpmulhw 256(%r8,%rcx), %ymm4, %ymm4
	vpmulhw %ymm15, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm5, %ymm5
	vpsubw %ymm3, %ymm2, %ymm2
	vpsubw %ymm5, %ymm4, %ymm4
	vpblendw $0xcc, %ymm2, %ymm6, %ymm6
	vpblendw $0xcc, %ymm4, %ymm7, %ymm7
	/* The unreduced QBM's wide c0/c1 lanes stay inside int16 through this
	 * merge.  Repair the merged representatives once; the following length-2
	 * sums then need only one conditional correction. */
	CENTER_WIDE_EXACT %ymm6, %ymm2
	CENTER_WIDE_EXACT %ymm7, %ymm2
	vpaddw %ymm7, %ymm6, %ymm0
	vpsubw %ymm7, %ymm6, %ymm1
	CENTER_ONCE %ymm0, %ymm2
	CENTER_ONCE %ymm1, %ymm2
	vmovdqa %ymm0, 0(%rdi)
	vmovdqa %ymm1, 32(%rdi)
	addq $64, %rdi
	addq $2, %rax
	decl %edx
	jne .Lif_stage1_wide_loop
.Lif_stage1_wide_done:
	testl %r10d, %r10d
	jnz .Lif_stage1_wide_ret
	vzeroupper
.Lif_stage1_wide_ret:
	ret
.size round4c_inverse_stage1_wide_asm,.-round4c_inverse_stage1_wide_asm

/* out=rdi, rows=rsi.  rows is modified in place. */
.p2align 5
.globl round4c_inverse_finish_asm
.type round4c_inverse_finish_asm,@function
round4c_inverse_finish_asm:
	/* Preserve the two public pointers while the existing register-resident
	 * length-4/8/16 kernel consumes rows. */
	pushq %rdi
	pushq %rsi
	subq $8, %rsp
	movq %rsi, %rdi
	call round4c_inverse_ntt16_layers_asm
	addq $8, %rsp
	popq %rsi
	popq %rdi

	/* Inverse DFT3 and generated postweight.  The postweight already folds
	 * /16 and /3, matching inverse_dft3_postweight(). */
	movq round4c_inv48_postweight_mont_asm(%rip), %r8
	movq round4c_inv48_postweight_qinv_asm(%rip), %r9
	movq round4c_inv3_omega_mont_asm(%rip), %r10
	movq round4c_inv3_omega_qinv_asm(%rip), %r11
	vpbroadcastw (%r10), %ymm13
	vpbroadcastw (%r11), %ymm14
	vpbroadcastw .Lif_q(%rip), %ymm15
	xorl %eax, %eax
.Lif_dft3_loop:
	vmovdqa    0(%rsi,%rax), %ymm0
	vmovdqa  512(%rsi,%rax), %ymm1
	vmovdqa 1024(%rsi,%rax), %ymm2
	vpsubw %ymm1, %ymm2, %ymm3
	vpmullw %ymm14, %ymm3, %ymm4
	vpmulhw %ymm13, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm4, %ymm4
	vpsubw %ymm4, %ymm3, %ymm3
	vpaddw %ymm1, %ymm0, %ymm5
	vpaddw %ymm2, %ymm5, %ymm5
	vpsubw %ymm1, %ymm0, %ymm6
	vpaddw %ymm3, %ymm6, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm3, %ymm7, %ymm7
	/* Three independent postweight Montgomery chains. */
	vpmullw    0(%r9,%rax), %ymm5, %ymm0
	vpmullw  512(%r9,%rax), %ymm6, %ymm1
	vpmullw 1024(%r9,%rax), %ymm7, %ymm2
	vpmulhw    0(%r8,%rax), %ymm5, %ymm5
	vpmulhw  512(%r8,%rax), %ymm6, %ymm6
	vpmulhw 1024(%r8,%rax), %ymm7, %ymm7
	vpmulhw %ymm15, %ymm0, %ymm0
	vpmulhw %ymm15, %ymm1, %ymm1
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm0, %ymm5, %ymm5
	vpsubw %ymm1, %ymm6, %ymm6
	vpsubw %ymm2, %ymm7, %ymm7
	vmovdqa %ymm5, 0(%rsi,%rax)
	vmovdqa %ymm6, 512(%rsi,%rax)
	vmovdqa %ymm7, 1024(%rsi,%rax)
	addq $32, %rax
	cmpq $512, %rax
	jne .Lif_dft3_loop

	/* Special inverse R2 followed by the top CRT and coefficient-order stores. */
	movq round4c_inv_beta_vector_mont_asm(%rip), %r8
	movq round4c_inv_beta_vector_qinv_asm(%rip), %r9
	movq round4c_final_merge_mont_asm(%rip), %r10
	movq round4c_final_merge_qinv_asm(%rip), %r11
	movq round4c_inverse_natural_byte_offsets_asm(%rip), %rcx
	vmovdqa (%r8), %ymm7
	vmovdqa (%r9), %ymm8
	vpbroadcastw 0(%r10), %ymm9
	vpbroadcastw 0(%r11), %ymm10
	vpbroadcastw 2(%r10), %ymm11
	vpbroadcastw 2(%r11), %ymm12
	vpbroadcastw .Lif_center(%rip), %ymm13
	vpbroadcastw .Lif_negative_center(%rip), %ymm14
	vpbroadcastw .Lif_q(%rip), %ymm15
	xorl %eax, %eax
.Lif_store_loop:
	vmovdqa (%rsi,%rax), %ymm0
	vpshufb .Lif_low64_dup(%rip), %ymm0, %ymm1
	vpshufb .Lif_high64_dup(%rip), %ymm0, %ymm2
	vpaddw %ymm2, %ymm1, %ymm3
	vpsubw %ymm2, %ymm1, %ymm4
	vpmullw %ymm8, %ymm4, %ymm5
	vpmulhw %ymm7, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpsubw %ymm5, %ymm4, %ymm4
	vpblendw $0xf0, %ymm4, %ymm3, %ymm0
	vperm2i128 $0x00, %ymm0, %ymm0, %ymm1
	vperm2i128 $0x11, %ymm0, %ymm0, %ymm2
	vpsubw %ymm2, %ymm1, %ymm3
	/* Three independent final Montgomery chains. */
	vpmullw %ymm10, %ymm1, %ymm4
	vpmulhw %ymm9, %ymm1, %ymm1
	vpmullw %ymm12, %ymm3, %ymm5
	vpmulhw %ymm11, %ymm3, %ymm6
	vpmullw .Lif_final2_qinv(%rip), %ymm3, %ymm0
	vpmulhw .Lif_final2_mont(%rip), %ymm3, %ymm2
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm0, %ymm0
	vpsubw %ymm4, %ymm1, %ymm1
	vpsubw %ymm5, %ymm6, %ymm5
	vpsubw %ymm0, %ymm2, %ymm6
	vpsubw %ymm6, %ymm1, %ymm1
	CENTER_ONCE %ymm1, %ymm4
	CENTER_ONCE %ymm5, %ymm4
	movzwl (%rcx), %edx
	vmovq %xmm1, 0(%rdi,%rdx)
	vpsrldq $8, %xmm1, %xmm0
	vmovq %xmm0, 384(%rdi,%rdx)
	vmovq %xmm5, 768(%rdi,%rdx)
	vpsrldq $8, %xmm5, %xmm0
	vmovq %xmm0, 1152(%rdi,%rdx)
	addq $32, %rax
	addq $2, %rcx
	cmpq $1536, %rax
	jne .Lif_store_loop
	vzeroupper
	ret
.size round4c_inverse_finish_asm,.-round4c_inverse_finish_asm

/* Single externally benchmarked entry.  It is intentionally non-reentrant,
 * like the pre-existing C oracle that owns full_inverse_rows. */
.p2align 5
.globl round4c_inverse_full_asm
.type round4c_inverse_full_asm,@function
round4c_inverse_full_asm:
	pushq %r12
	pushq %r13
	subq $8, %rsp
	movq %rdi, %r12
	movq %rsi, %r13
	leaq round4c_inverse_rows_asm(%rip), %rdi
	movq %r13, %rsi
	call .Lif_stage1_internal
	movq %r12, %rdi
	leaq round4c_inverse_rows_asm(%rip), %rsi
	call round4c_inverse_finish_asm
	addq $8, %rsp
	popq %r13
	popq %r12
	ret
.size round4c_inverse_full_asm,.-round4c_inverse_full_asm

.p2align 5
.globl round4c_inverse_full_wide_asm
.type round4c_inverse_full_wide_asm,@function
round4c_inverse_full_wide_asm:
	pushq %r12
	pushq %r13
	subq $8, %rsp
	movq %rdi, %r12
	movq %rsi, %r13
	leaq round4c_inverse_rows_asm(%rip), %rdi
	movq %r13, %rsi
	call .Lif_stage1_wide_internal
	movq %r12, %rdi
	leaq round4c_inverse_rows_asm(%rip), %rsi
	call round4c_inverse_finish_asm
	addq $8, %rsp
	popq %r13
	popq %r12
	ret
.size round4c_inverse_full_wide_asm,.-round4c_inverse_full_wide_asm

.section .rodata
.p2align 5
.Lif_q: .short 3457
.Lif_center: .short 1728
.Lif_negative_center: .short -1728
.p2align 5
.Lif_ten: .rept 16; .short 10; .endr
.Lif_plus_dup:
	.byte 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
	.byte 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
.Lif_minus_dup:
	.byte 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15
	.byte 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15
.Lif_low64_dup:
	.byte 0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7
	.byte 0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7
.Lif_high64_dup:
	.byte 8,9,10,11,12,13,14,15,8,9,10,11,12,13,14,15
	.byte 8,9,10,11,12,13,14,15,8,9,10,11,12,13,14,15
.Lif_pair_offsets:
	.short 0,128,64,192,32,160,96,224
	.short 512,640,576,704,544,672,608,736
	.short 1024,1152,1088,1216,1056,1184,1120,1248
.p2align 5
.Lif_final2_mont: .rept 16; .short 454; .endr
.Lif_final2_qinv: .rept 16; .short -28474; .endr

.section .bss
.p2align 5
round4c_inverse_rows_asm: .zero 1536

.section .note.GNU-stack,"",@progbits
