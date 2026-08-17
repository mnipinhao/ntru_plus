.text

/*
 * Benchmark-only forward CT16 for 48 aligned YMM vectors arranged as
 * [k3][bit-reversed i16][4*branch+degree].  Addresses and loop counts are
 * public.  The length-2 and length-8 boundaries center once, matching the C
 * oracle; length-4 and length-16 stay lazy.  No stack or data spill is used.
 */

.macro CENTER_ONCE reg, tmp
	vpcmpgtw %ymm14, \reg, \tmp
	vpand %ymm15, \tmp, \tmp
	vpsubw \tmp, \reg, \reg
	vpcmpgtw \reg, %ymm13, \tmp
	vpand %ymm15, \tmp, \tmp
	vpaddw \tmp, \reg, \reg
.endm

.macro IDENTITY_BUTTERFLY low, high, correct
	vpaddw \high, \low, %ymm8
	vpsubw \high, \low, \high
	vmovdqa %ymm8, \low
	.if \correct
	CENTER_ONCE \low, %ymm8
	CENTER_ONCE \high, %ymm8
	.endif
.endm

.macro MONT_BUTTERFLY low, high, correct
	vpmullw %ymm11, \high, %ymm8
	vpmulhw %ymm12, \high, %ymm9
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm9, \high
	vpaddw \high, \low, %ymm8
	vpsubw \high, \low, \high
	vmovdqa %ymm8, \low
	.if \correct
	CENTER_ONCE \low, %ymm8
	CENTER_ONCE \high, %ymm8
	.endif
.endm

.macro LOAD_TWIDDLE index
	vpbroadcastw .Lfwd16_mont+2*\index(%rip), %ymm12
	vpbroadcastw .Lfwd16_qinv+2*\index(%rip), %ymm11
.endm

.macro RUN_GROUP2 stride, pairs, low, high, twiddle, correct
	.if \twiddle >= 0
	vpbroadcastw .Lfwd16_mont+2*\twiddle(%rip), %ymm12
	vpbroadcastw .Lfwd16_qinv+2*\twiddle(%rip), %ymm11
	.endif
	movq %rdi, %rax
	movl $\pairs, %ecx
.Lpair_\@:
	vmovdqa \low(%rax), %ymm0
	vmovdqa \high(%rax), %ymm1
	vmovdqa \low+\stride(%rax), %ymm6
	vmovdqa \high+\stride(%rax), %ymm7
	.if \twiddle >= 0
	vpmullw %ymm11, %ymm1, %ymm2
	vpmullw %ymm11, %ymm7, %ymm8
	vpmulhw %ymm12, %ymm1, %ymm3
	vpmulhw %ymm12, %ymm7, %ymm9
	vpmulhw %ymm15, %ymm2, %ymm2
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm2, %ymm3, %ymm1
	vpsubw %ymm8, %ymm9, %ymm7
	.endif
	vpaddw %ymm1, %ymm0, %ymm2
	vpsubw %ymm1, %ymm0, %ymm3
	vpaddw %ymm7, %ymm6, %ymm8
	vpsubw %ymm7, %ymm6, %ymm9
	.if \correct
	CENTER_ONCE %ymm2, %ymm4
	CENTER_ONCE %ymm3, %ymm4
	CENTER_ONCE %ymm8, %ymm4
	CENTER_ONCE %ymm9, %ymm4
	.endif
	vmovdqa %ymm2, \low(%rax)
	vmovdqa %ymm3, \high(%rax)
	vmovdqa %ymm8, \low+\stride(%rax)
	vmovdqa %ymm9, \high+\stride(%rax)
	addq $2*\stride, %rax
	decl %ecx
	jnz .Lpair_\@
.endm

.macro RUN_GROUP base, stride, count, low, high, twiddle, correct
	.if \twiddle >= 0
	vpbroadcastw .Lfwd16_mont+2*\twiddle(%rip), %ymm12
	vpbroadcastw .Lfwd16_qinv+2*\twiddle(%rip), %ymm11
	.endif
	movq \base, %rax
	movl $\count, %ecx
.Lsingle_\@:
	vmovdqa \low(%rax), %ymm0
	vmovdqa \high(%rax), %ymm1
	.if \twiddle >= 0
	vpmullw %ymm11, %ymm1, %ymm4
	vpmulhw %ymm12, %ymm1, %ymm5
	vpmulhw %ymm15, %ymm4, %ymm4
	vpsubw %ymm4, %ymm5, %ymm1
	.endif
	vpaddw %ymm1, %ymm0, %ymm2
	vpsubw %ymm1, %ymm0, %ymm3
	.if \correct
	CENTER_ONCE %ymm2, %ymm4
	CENTER_ONCE %ymm3, %ymm4
	.endif
	vmovdqa %ymm2, \low(%rax)
	vmovdqa %ymm3, \high(%rax)
	addq $\stride, %rax
	decl %ecx
	jnz .Lsingle_\@
.endm

.macro RUN_CT16 base
	vpbroadcastw .Lq(%rip), %ymm15
	vpbroadcastw .Lcenter(%rip), %ymm14
	vpbroadcastw .Lnegative_center(%rip), %ymm13

	/* Fuse length 2, 4, and 8 inside one register-resident 8-vector tile. */
	movq \base, %rax
	movl $6, %ecx
.Lhalf_tile_\@:
	vmovdqa   0(%rax), %ymm0
	vmovdqa  32(%rax), %ymm1
	vmovdqa  64(%rax), %ymm2
	vmovdqa  96(%rax), %ymm3
	vmovdqa 128(%rax), %ymm4
	vmovdqa 160(%rax), %ymm5
	vmovdqa 192(%rax), %ymm6
	vmovdqa 224(%rax), %ymm7

	/* length 2: all identity butterflies, one correction. */
	IDENTITY_BUTTERFLY %ymm0, %ymm1, 1
	IDENTITY_BUTTERFLY %ymm2, %ymm3, 1
	IDENTITY_BUTTERFLY %ymm4, %ymm5, 1
	IDENTITY_BUTTERFLY %ymm6, %ymm7, 1

	/* length 4: identity columns and shared omega^4 columns. */
	IDENTITY_BUTTERFLY %ymm0, %ymm2, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm6, 0
	LOAD_TWIDDLE 2
	MONT_BUTTERFLY %ymm1, %ymm3, 0
	MONT_BUTTERFLY %ymm5, %ymm7, 0

	/* length 8: one identity plus omega^2, omega^4, omega^6. */
	IDENTITY_BUTTERFLY %ymm0, %ymm4, 1
	LOAD_TWIDDLE 4
	MONT_BUTTERFLY %ymm1, %ymm5, 1
	LOAD_TWIDDLE 5
	MONT_BUTTERFLY %ymm2, %ymm6, 1
	LOAD_TWIDDLE 6
	MONT_BUTTERFLY %ymm3, %ymm7, 1

	vmovdqa %ymm0,   0(%rax)
	vmovdqa %ymm1,  32(%rax)
	vmovdqa %ymm2,  64(%rax)
	vmovdqa %ymm3,  96(%rax)
	vmovdqa %ymm4, 128(%rax)
	vmovdqa %ymm5, 160(%rax)
	vmovdqa %ymm6, 192(%rax)
	vmovdqa %ymm7, 224(%rax)
	addq $256, %rax
	decl %ecx
	jnz .Lhalf_tile_\@

	/* length 16, offset 7: [1, omega, ..., omega^7] */
	RUN_GROUP \base, 512, 3, 0, 256, -1, 0
	RUN_GROUP \base, 512, 3, 32, 288, 8, 0
	RUN_GROUP \base, 512, 3, 64, 320, 9, 0
	RUN_GROUP \base, 512, 3, 96, 352, 10, 0
	RUN_GROUP \base, 512, 3, 128, 384, 11, 0
	RUN_GROUP \base, 512, 3, 160, 416, 12, 0
	RUN_GROUP \base, 512, 3, 192, 448, 13, 0
	RUN_GROUP \base, 512, 3, 224, 480, 14, 0
.endm

.macro SPLIT_STORE value, displacement
	vpshufb %ymm13, \value, %ymm7
	vpshufb %ymm14, \value, %ymm8
	vpmullw \displacement(%rdx,%rax), %ymm8, %ymm9
	vpmulhw \displacement(%rcx,%rax), %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm8
	vpaddw %ymm8, %ymm7, %ymm7
	vmovdqu %ymm7, \displacement(%r8,%rax)
.endm

.macro SPLIT_STORE_TMP value, displacement, low, high, product
	vpshufb %ymm13, \value, \low
	vpshufb %ymm14, \value, \high
	vpmullw \displacement(%rdx,%rax), \high, \product
	vpmulhw \displacement(%rcx,%rax), \high, \high
	vpmulhw %ymm15, \product, \product
	vpsubw \product, \high, \high
	vpaddw \high, \low, \low
	vmovdqu \low, \displacement(%r8,%rax)
.endm

.macro DFT3_VALUES x0, x1, x2
	vpsubw \x2, \x1, %ymm6
	vpmullw %ymm11, %ymm6, %ymm8
	vpmulhw %ymm12, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm6, %ymm6
	vpaddw \x1, \x0, %ymm7
	vpaddw \x2, %ymm7, %ymm7
	vpsubw \x2, \x0, %ymm8
	vpaddw %ymm6, %ymm8, %ymm8
	vpsubw \x1, \x0, %ymm9
	vpsubw %ymm6, %ymm9, %ymm9
.endm

.macro FRONTEND_ONE target, coeff_offset, input_offset
	movswq \input_offset(%rdx), %rax
	vpbroadcastq    0(%rsi,%rax), \target
	vpmullw \coeff_offset(%rcx), \target, \target
	vpbroadcastq  384(%rsi,%rax), %ymm8
	vpmullw 1536+\coeff_offset(%rcx), %ymm8, %ymm8
	vpaddw %ymm8, \target, \target
	vpbroadcastq  768(%rsi,%rax), %ymm8
	vpmullw 3072+\coeff_offset(%rcx), %ymm8, %ymm8
	vpaddw %ymm8, \target, \target
	vpbroadcastq 1152(%rsi,%rax), %ymm8
	vpmullw 4608+\coeff_offset(%rcx), %ymm8, %ymm8
	vpaddw %ymm8, \target, \target
	vpmullw %ymm11, \target, %ymm8
	vpmulhw %ymm12, \target, \target
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, \target, \target
.endm

.macro DFT3_RENAMED x0, x1, x2, o0, o1, o2, t0, t1
	vpsubw \x2, \x1, \t0
	vpmullw %ymm11, \t0, \t1
	vpmulhw %ymm12, \t0, \t0
	vpmulhw %ymm15, \t1, \t1
	vpsubw \t1, \t0, \t0
	vpaddw \x1, \x0, \o0
	vpaddw \x2, \o0, \o0
	vpsubw \x2, \x0, \o1
	vpaddw \t0, \o1, \o1
	vpsubw \x1, \x0, \o2
	vpsubw \t0, \o2, \o2
.endm

.macro CENTER10_3_RENAMED a, b, c, ta, tb, tc
	vpmulhrsw .Lcenter10_vector(%rip), \a, \ta
	vpmulhrsw .Lcenter10_vector(%rip), \b, \tb
	vpmulhrsw .Lcenter10_vector(%rip), \c, \tc
	vpmullw %ymm15, \ta, \ta
	vpmullw %ymm15, \tb, \tb
	vpmullw %ymm15, \tc, \tc
	vpsubw \ta, \a, \a
	vpsubw \tb, \b, \b
	vpsubw \tc, \c, \c
.endm

.macro CENTER10_4 a, b, c, d
	vpmulhrsw %ymm12, \a, %ymm8
	vpmulhrsw %ymm12, \b, %ymm9
	vpmulhrsw %ymm12, \c, %ymm10
	vpmulhrsw %ymm12, \d, %ymm11
	vpmullw %ymm15, %ymm8, %ymm8
	vpmullw %ymm15, %ymm9, %ymm9
	vpmullw %ymm15, %ymm10, %ymm10
	vpmullw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8, \a, \a
	vpsubw %ymm9, \b, \b
	vpsubw %ymm10, \c, \c
	vpsubw %ymm11, \d, \d
.endm

.macro CENTER10_4_TMP a, b, c, d, ta, tb, tc, td
	vpmulhrsw %ymm12, \a, \ta
	vpmulhrsw %ymm12, \b, \tb
	vpmulhrsw %ymm12, \c, \tc
	vpmulhrsw %ymm12, \d, \td
	vpmullw %ymm15, \ta, \ta
	vpmullw %ymm15, \tb, \tb
	vpmullw %ymm15, \tc, \tc
	vpmullw %ymm15, \td, \td
	vpsubw \ta, \a, \a
	vpsubw \tb, \b, \b
	vpsubw \tc, \c, \c
	vpsubw \td, \d, \d
.endm

.macro CENTER10_3 a, b, c
	vpmulhrsw .Lcenter10_vector(%rip), \a, %ymm0
	vpmulhrsw .Lcenter10_vector(%rip), \b, %ymm2
	vpmulhrsw .Lcenter10_vector(%rip), \c, %ymm4
	vpmullw %ymm15, %ymm0, %ymm0
	vpmullw %ymm15, %ymm2, %ymm2
	vpmullw %ymm15, %ymm4, %ymm4
	vpsubw %ymm0, \a, \a
	vpsubw %ymm2, \b, \b
	vpsubw %ymm4, \c, \c
.endm

.p2align 5
.globl round4c_forward_ntt16_asm
.type round4c_forward_ntt16_asm,@function
round4c_forward_ntt16_asm:
	RUN_CT16 %rdi

	vzeroupper
	ret
.size round4c_forward_ntt16_asm,.-round4c_forward_ntt16_asm

/* One selected-N5 length-2/4/8 tile using the current fixed-register ABI. */
.p2align 5
.globl round4c_forward_ct8_baseline_asm
.type round4c_forward_ct8_baseline_asm,@function
round4c_forward_ct8_baseline_asm:
	vmovdqa   0(%rdi), %ymm0
	vmovdqa  32(%rdi), %ymm1
	vmovdqa  64(%rdi), %ymm2
	vmovdqa  96(%rdi), %ymm3
	vmovdqa 128(%rdi), %ymm4
	vmovdqa 160(%rdi), %ymm5
	vmovdqa 192(%rdi), %ymm6
	vmovdqa 224(%rdi), %ymm7
	vpbroadcastw .Lq(%rip), %ymm15
	IDENTITY_BUTTERFLY %ymm0, %ymm1, 0
	IDENTITY_BUTTERFLY %ymm2, %ymm3, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm5, 0
	IDENTITY_BUTTERFLY %ymm6, %ymm7, 0
	IDENTITY_BUTTERFLY %ymm0, %ymm2, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm6, 0
	LOAD_TWIDDLE 2
	MONT_BUTTERFLY %ymm1, %ymm3, 0
	MONT_BUTTERFLY %ymm5, %ymm7, 0
	IDENTITY_BUTTERFLY %ymm0, %ymm4, 0
	LOAD_TWIDDLE 4
	MONT_BUTTERFLY %ymm1, %ymm5, 0
	LOAD_TWIDDLE 5
	MONT_BUTTERFLY %ymm2, %ymm6, 0
	LOAD_TWIDDLE 6
	MONT_BUTTERFLY %ymm3, %ymm7, 0
	vpbroadcastw .Lcenter10(%rip), %ymm12
	CENTER10_4 %ymm0, %ymm1, %ymm2, %ymm3
	CENTER10_4 %ymm4, %ymm5, %ymm6, %ymm7
	vmovdqa %ymm0,   0(%rdi)
	vmovdqa %ymm1,  32(%rdi)
	vmovdqa %ymm2,  64(%rdi)
	vmovdqa %ymm3,  96(%rdi)
	vmovdqa %ymm4, 128(%rdi)
	vmovdqa %ymm5, 160(%rdi)
	vmovdqa %ymm6, 192(%rdi)
	vmovdqa %ymm7, 224(%rdi)
	vzeroupper
	ret
.size round4c_forward_ct8_baseline_asm,.-round4c_forward_ct8_baseline_asm

/*
 * Same tile and exact representation with Official-style operation-class
 * Montgomery scheduling and SSA register renaming across all three layers.
 */
.p2align 5
.globl round4c_forward_ct8_sched_asm
.type round4c_forward_ct8_sched_asm,@function
round4c_forward_ct8_sched_asm:
	vmovdqa   0(%rdi), %ymm0
	vmovdqa  32(%rdi), %ymm1
	vmovdqa  64(%rdi), %ymm2
	vmovdqa  96(%rdi), %ymm3
	vmovdqa 128(%rdi), %ymm4
	vmovdqa 160(%rdi), %ymm5
	vmovdqa 192(%rdi), %ymm6
	vmovdqa 224(%rdi), %ymm7
	vpbroadcastw .Lq(%rip), %ymm15

	/* L2: keep sums in temporary names and differences in odd registers. */
	vpaddw %ymm1, %ymm0, %ymm8
	vpaddw %ymm3, %ymm2, %ymm9
	vpaddw %ymm5, %ymm4, %ymm10
	vpaddw %ymm7, %ymm6, %ymm13
	vpsubw %ymm1, %ymm0, %ymm1
	vpsubw %ymm3, %ymm2, %ymm3
	vpsubw %ymm5, %ymm4, %ymm5
	vpsubw %ymm7, %ymm6, %ymm7

	/* L4 identity columns consume the renamed L2 sums. */
	vpaddw %ymm9, %ymm8, %ymm0
	vpsubw %ymm9, %ymm8, %ymm2
	vpaddw %ymm13, %ymm10, %ymm4
	vpsubw %ymm13, %ymm10, %ymm6

	/* L4 twiddled columns: two independent Montgomery chains. */
	LOAD_TWIDDLE 2
	vpmullw %ymm11, %ymm3, %ymm8
	vpmullw %ymm11, %ymm7, %ymm9
	vpmulhw %ymm12, %ymm3, %ymm3
	vpmulhw %ymm12, %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm8, %ymm3, %ymm3
	vpsubw %ymm9, %ymm7, %ymm7
	vpaddw %ymm3, %ymm1, %ymm10
	vpsubw %ymm3, %ymm1, %ymm3
	vpaddw %ymm7, %ymm5, %ymm13
	vpsubw %ymm7, %ymm5, %ymm7

	/* L8 identity column frees two registers for the three twiddled chains. */
	vpaddw %ymm4, %ymm0, %ymm1
	vpsubw %ymm4, %ymm0, %ymm5

	LOAD_TWIDDLE 4
	vpmullw %ymm11, %ymm13, %ymm8
	vpmulhw %ymm12, %ymm13, %ymm13
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm13, %ymm13
	LOAD_TWIDDLE 5
	vpmullw %ymm11, %ymm6, %ymm8
	vpmulhw %ymm12, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm6, %ymm6
	LOAD_TWIDDLE 6
	vpmullw %ymm11, %ymm7, %ymm8
	vpmulhw %ymm12, %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm7

	/* Renamed L8 outputs, with no sum copy-back moves. */
	vpaddw %ymm13, %ymm10, %ymm0
	vpsubw %ymm13, %ymm10, %ymm4
	vpaddw %ymm6, %ymm2, %ymm10
	vpsubw %ymm6, %ymm2, %ymm13
	vpaddw %ymm7, %ymm3, %ymm2
	vpsubw %ymm7, %ymm3, %ymm6

	vpbroadcastw .Lcenter10(%rip), %ymm12
	CENTER10_4_TMP %ymm1, %ymm0, %ymm10, %ymm2, %ymm3, %ymm7, %ymm8, %ymm9
	CENTER10_4_TMP %ymm5, %ymm4, %ymm13, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9
	vmovdqa %ymm1,   0(%rdi)
	vmovdqa %ymm0,  32(%rdi)
	vmovdqa %ymm10, 64(%rdi)
	vmovdqa %ymm2,  96(%rdi)
	vmovdqa %ymm5, 128(%rdi)
	vmovdqa %ymm4, 160(%rdi)
	vmovdqa %ymm13,192(%rdi)
	vmovdqa %ymm6, 224(%rdi)
	vzeroupper
	ret
.size round4c_forward_ct8_sched_asm,.-round4c_forward_ct8_sched_asm

/*
 * Complete benchmark-only F1 producer.  The static scratch preserves the
 * existing alias contract while keeping this first all-assembly version
 * directly comparable with the C and hybrid producers.
 */
.p2align 5
.globl round4c_forward_f1_full_asm
.type round4c_forward_f1_full_asm,@function
round4c_forward_f1_full_asm:
	movq %rdi, %r8
	leaq .Lforward_scratch(%rip), %r10
	leaq .Lfrontend_input_offsets(%rip), %rdx
	leaq .Lfrontend_c0(%rip), %rcx
	movq %r10, %rdi
	vpbroadcastw .Lq(%rip), %ymm15
	vpbroadcastw .Lcenter(%rip), %ymm14
	vpbroadcastw .Lnegative_center(%rip), %ymm13
	movl $6, %r9d
.Lfrontend_half_tile:
	vpbroadcastw .Lidentity_qinv(%rip), %ymm11
	vpbroadcastw .Lidentity_mont(%rip), %ymm12
	FRONTEND_ONE %ymm0,   0,  0
	FRONTEND_ONE %ymm1,  32,  2
	FRONTEND_ONE %ymm2,  64,  4
	FRONTEND_ONE %ymm3,  96,  6
	FRONTEND_ONE %ymm4, 128,  8
	FRONTEND_ONE %ymm5, 160, 10
	FRONTEND_ONE %ymm6, 192, 12
	FRONTEND_ONE %ymm7, 224, 14

	IDENTITY_BUTTERFLY %ymm0, %ymm1, 0
	IDENTITY_BUTTERFLY %ymm2, %ymm3, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm5, 0
	IDENTITY_BUTTERFLY %ymm6, %ymm7, 0
	IDENTITY_BUTTERFLY %ymm0, %ymm2, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm6, 0
	LOAD_TWIDDLE 2
	MONT_BUTTERFLY %ymm1, %ymm3, 0
	MONT_BUTTERFLY %ymm5, %ymm7, 0
	IDENTITY_BUTTERFLY %ymm0, %ymm4, 0
	LOAD_TWIDDLE 4
	MONT_BUTTERFLY %ymm1, %ymm5, 0
	LOAD_TWIDDLE 5
	MONT_BUTTERFLY %ymm2, %ymm6, 0
	LOAD_TWIDDLE 6
	MONT_BUTTERFLY %ymm3, %ymm7, 0
	vpbroadcastw .Lcenter10(%rip), %ymm12
	CENTER10_4 %ymm0, %ymm1, %ymm2, %ymm3
	CENTER10_4 %ymm4, %ymm5, %ymm6, %ymm7

	vmovdqa %ymm0,   0(%rdi)
	vmovdqa %ymm1,  32(%rdi)
	vmovdqa %ymm2,  64(%rdi)
	vmovdqa %ymm3,  96(%rdi)
	vmovdqa %ymm4, 128(%rdi)
	vmovdqa %ymm5, 160(%rdi)
	vmovdqa %ymm6, 192(%rdi)
	vmovdqa %ymm7, 224(%rdi)
	addq $256, %rdi
	addq $256, %rcx
	addq $16, %rdx
	decl %r9d
	jnz .Lfrontend_half_tile

	vmovdqa .Lsplit_low_bytes(%rip), %ymm13
	vmovdqa .Lsplit_high_bytes(%rip), %ymm14
	leaq .Lsplit_mont(%rip), %rcx
	leaq .Lsplit_qinv(%rip), %rdx
	xorl %eax, %eax
	xorl %r9d, %r9d
.Llength16_tail_loop:
	vmovdqa    0(%r10,%rax), %ymm0
	vmovdqa  256(%r10,%rax), %ymm1
	vmovdqa  512(%r10,%rax), %ymm2
	vmovdqa  768(%r10,%rax), %ymm3
	vmovdqa 1024(%r10,%rax), %ymm4
	vmovdqa 1280(%r10,%rax), %ymm5
	testq %rax, %rax
	jz .Llength16_identity
	leaq .Lfwd16_mont+14(%rip), %rdi
	vpbroadcastw (%rdi,%r9,2), %ymm12
	leaq .Lfwd16_qinv+14(%rip), %rdi
	vpbroadcastw (%rdi,%r9,2), %ymm11
	vpmullw %ymm11, %ymm1, %ymm6
	vpmulhw %ymm12, %ymm1, %ymm1
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm1, %ymm1
	vpmullw %ymm11, %ymm3, %ymm6
	vpmulhw %ymm12, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm3, %ymm3
	vpmullw %ymm11, %ymm5, %ymm6
	vpmulhw %ymm12, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm5, %ymm5
.Llength16_identity:
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm1, %ymm0, %ymm1
	vmovdqa %ymm6, %ymm0
	vpaddw %ymm3, %ymm2, %ymm6
	vpsubw %ymm3, %ymm2, %ymm3
	vmovdqa %ymm6, %ymm2
	vpaddw %ymm5, %ymm4, %ymm6
	vpsubw %ymm5, %ymm4, %ymm5
	vmovdqa %ymm6, %ymm4

	vpbroadcastw .Lfwd3_omega_qinv(%rip), %ymm11
	vpbroadcastw .Lfwd3_omega_mont(%rip), %ymm12
	DFT3_VALUES %ymm0, %ymm2, %ymm4
	CENTER10_3 %ymm7, %ymm8, %ymm9
	SPLIT_STORE_TMP %ymm7, 0, %ymm0, %ymm2, %ymm4
	SPLIT_STORE_TMP %ymm8, 512, %ymm0, %ymm2, %ymm4
	SPLIT_STORE_TMP %ymm9, 1024, %ymm0, %ymm2, %ymm4
	DFT3_VALUES %ymm1, %ymm3, %ymm5
	CENTER10_3 %ymm7, %ymm8, %ymm9
	SPLIT_STORE_TMP %ymm7, 256, %ymm0, %ymm2, %ymm4
	SPLIT_STORE_TMP %ymm8, 768, %ymm0, %ymm2, %ymm4
	SPLIT_STORE_TMP %ymm9, 1280, %ymm0, %ymm2, %ymm4
	addq $32, %rax
	incq %r9
	cmpq $256, %rax
	jne .Llength16_tail_loop

	vzeroupper
	ret
.size round4c_forward_f1_full_asm,.-round4c_forward_f1_full_asm

/*
 * ML-KEM-style scheduling candidate.  It intentionally preserves the selected
 * N5 representation and only changes the length-16 tail schedule: peel the
 * public identity column, hoist twiddle bases, expose three independent
 * Montgomery chains, and keep butterfly sums in their destination registers.
 */
.p2align 5
.globl round4c_forward_f1_mlkem_sched_asm
.type round4c_forward_f1_mlkem_sched_asm,@function
round4c_forward_f1_mlkem_sched_asm:
	movq %rdi, %r8
	leaq .Lforward_scratch(%rip), %r10
	leaq .Lfrontend_input_offsets(%rip), %rdx
	leaq .Lfrontend_c0(%rip), %rcx
	movq %r10, %rdi
	vpbroadcastw .Lq(%rip), %ymm15
	movl $6, %r9d
.Lmlkem_frontend_half_tile:
	vpbroadcastw .Lidentity_qinv(%rip), %ymm11
	vpbroadcastw .Lidentity_mont(%rip), %ymm12
	FRONTEND_ONE %ymm0,   0,  0
	FRONTEND_ONE %ymm1,  32,  2
	FRONTEND_ONE %ymm2,  64,  4
	FRONTEND_ONE %ymm3,  96,  6
	FRONTEND_ONE %ymm4, 128,  8
	FRONTEND_ONE %ymm5, 160, 10
	FRONTEND_ONE %ymm6, 192, 12
	FRONTEND_ONE %ymm7, 224, 14

	IDENTITY_BUTTERFLY %ymm0, %ymm1, 0
	IDENTITY_BUTTERFLY %ymm2, %ymm3, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm5, 0
	IDENTITY_BUTTERFLY %ymm6, %ymm7, 0
	IDENTITY_BUTTERFLY %ymm0, %ymm2, 0
	IDENTITY_BUTTERFLY %ymm4, %ymm6, 0
	LOAD_TWIDDLE 2
	MONT_BUTTERFLY %ymm1, %ymm3, 0
	MONT_BUTTERFLY %ymm5, %ymm7, 0
	IDENTITY_BUTTERFLY %ymm0, %ymm4, 0
	LOAD_TWIDDLE 4
	MONT_BUTTERFLY %ymm1, %ymm5, 0
	LOAD_TWIDDLE 5
	MONT_BUTTERFLY %ymm2, %ymm6, 0
	LOAD_TWIDDLE 6
	MONT_BUTTERFLY %ymm3, %ymm7, 0
	vpbroadcastw .Lcenter10(%rip), %ymm12
	CENTER10_4 %ymm0, %ymm1, %ymm2, %ymm3
	CENTER10_4 %ymm4, %ymm5, %ymm6, %ymm7

	vmovdqa %ymm0,   0(%rdi)
	vmovdqa %ymm1,  32(%rdi)
	vmovdqa %ymm2,  64(%rdi)
	vmovdqa %ymm3,  96(%rdi)
	vmovdqa %ymm4, 128(%rdi)
	vmovdqa %ymm5, 160(%rdi)
	vmovdqa %ymm6, 192(%rdi)
	vmovdqa %ymm7, 224(%rdi)
	addq $256, %rdi
	addq $256, %rcx
	addq $16, %rdx
	decl %r9d
	jnz .Lmlkem_frontend_half_tile

	vmovdqa .Lsplit_low_bytes(%rip), %ymm13
	vmovdqa .Lsplit_high_bytes(%rip), %ymm14
	leaq .Lsplit_mont(%rip), %rcx
	leaq .Lsplit_qinv(%rip), %rdx
	leaq .Lfwd16_mont+14(%rip), %rsi
	leaq .Lfwd16_qinv+14(%rip), %rdi

	/* Peel the sole identity-twiddle column. */
	xorl %eax, %eax
	xorl %r9d, %r9d
	vmovdqa    0(%r10), %ymm0
	vmovdqa  256(%r10), %ymm1
	vmovdqa  512(%r10), %ymm2
	vmovdqa  768(%r10), %ymm3
	vmovdqa 1024(%r10), %ymm4
	vmovdqa 1280(%r10), %ymm5
	jmp .Lmlkem_length16_common
.Lmlkem_length16_twiddled:
	vmovdqa    0(%r10,%rax), %ymm0
	vmovdqa  256(%r10,%rax), %ymm1
	vmovdqa  512(%r10,%rax), %ymm2
	vmovdqa  768(%r10,%rax), %ymm3
	vmovdqa 1024(%r10,%rax), %ymm4
	vmovdqa 1280(%r10,%rax), %ymm5
	vpbroadcastw (%rsi,%r9,2), %ymm12
	vpbroadcastw (%rdi,%r9,2), %ymm11

	/* Three independent Montgomery chains, scheduled by operation class. */
	vpmullw %ymm11, %ymm1, %ymm6
	vpmullw %ymm11, %ymm3, %ymm7
	vpmullw %ymm11, %ymm5, %ymm8
	vpmulhw %ymm12, %ymm1, %ymm1
	vpmulhw %ymm12, %ymm3, %ymm3
	vpmulhw %ymm12, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm6, %ymm1, %ymm1
	vpsubw %ymm7, %ymm3, %ymm3
	vpsubw %ymm8, %ymm5, %ymm5

.Lmlkem_length16_common:
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm1, %ymm0, %ymm1
	vpaddw %ymm3, %ymm2, %ymm7
	vpsubw %ymm3, %ymm2, %ymm3
	vpaddw %ymm5, %ymm4, %ymm8
	vpsubw %ymm5, %ymm4, %ymm5

	vpbroadcastw .Lfwd3_omega_qinv(%rip), %ymm11
	vpbroadcastw .Lfwd3_omega_mont(%rip), %ymm12
	DFT3_RENAMED %ymm6, %ymm7, %ymm8, %ymm0, %ymm2, %ymm4, %ymm9, %ymm10
	CENTER10_3_RENAMED %ymm0, %ymm2, %ymm4, %ymm6, %ymm7, %ymm8
	SPLIT_STORE_TMP %ymm0, 0, %ymm6, %ymm7, %ymm8
	SPLIT_STORE_TMP %ymm2, 512, %ymm6, %ymm7, %ymm8
	SPLIT_STORE_TMP %ymm4, 1024, %ymm6, %ymm7, %ymm8
	DFT3_RENAMED %ymm1, %ymm3, %ymm5, %ymm0, %ymm2, %ymm4, %ymm6, %ymm7
	CENTER10_3_RENAMED %ymm0, %ymm2, %ymm4, %ymm6, %ymm7, %ymm8
	SPLIT_STORE_TMP %ymm0, 256, %ymm6, %ymm7, %ymm8
	SPLIT_STORE_TMP %ymm2, 768, %ymm6, %ymm7, %ymm8
	SPLIT_STORE_TMP %ymm4, 1280, %ymm6, %ymm7, %ymm8
	addq $32, %rax
	incq %r9
	cmpq $256, %rax
	jne .Lmlkem_length16_twiddled

	vzeroupper
	ret
.size round4c_forward_f1_mlkem_sched_asm,.-round4c_forward_f1_mlkem_sched_asm

.bss
.p2align 5
.Lforward_scratch:
	.zero 1536

.section .rodata
#include "../generated/forward-ntt16-constants.inc"

.section .note.GNU-stack,"",@progbits
