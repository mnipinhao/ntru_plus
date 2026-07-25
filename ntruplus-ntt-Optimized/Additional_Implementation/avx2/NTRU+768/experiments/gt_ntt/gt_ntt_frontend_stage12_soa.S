.text

#include "gt_ntt_stage345_native_fused.inc"

/*
 * Load two table-selected Q slots for all three Good-Thomas rows.  The generated
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

/* Same six public CRT loads with pair-specific displacements in the code. */
.macro FRONTEND_LOADS_FIXED o00, o01, o10, o11, o20, o21
	vmovq \o00(%rsi), %xmm0
	vmovq \o01(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm0, %ymm0
	vmovq 768+\o00(%rsi), %xmm3
	vmovq 768+\o01(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm3, %ymm3

	vmovq \o10(%rsi), %xmm1
	vmovq \o11(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	vmovq 768+\o10(%rsi), %xmm4
	vmovq 768+\o11(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4

	vmovq \o20(%rsi), %xmm2
	vmovq \o21(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm2, %ymm2
	vmovq 768+\o20(%rsi), %xmm5
	vmovq 768+\o21(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm5, %ymm5
.endm

/*
 * Q and Q+3 map to quartic blocks three positions apart.  One 32-byte load
 * therefore contains both public inputs; vpermq selects qwords 0 and 3 and
 * duplicates each one into its branch0/branch1 positions.  The sole wrapped
 * row is handled in the pipelined-tail macros below.
 */
.macro FRONTEND_LOADS_WIDE_FIXED o0, o1, o2
	vpermq $0xf0, \o0(%rsi), %ymm0
	vpermq $0xf0, 768+\o0(%rsi), %ymm3
	vpermq $0xf0, \o1(%rsi), %ymm1
	vpermq $0xf0, 768+\o1(%rsi), %ymm4
	vpermq $0xf0, \o2(%rsi), %ymm2
	vpermq $0xf0, 768+\o2(%rsi), %ymm5
.endm

/*
 * Three independent top-split Montgomery chains are issued together.  This
 * fills the packed-multiply latency without extending any value beyond the
 * proven 3(q-1) DFT3 output bound.
 */
.macro FRONTEND_TOP_MONT
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
.endm

.macro FRONTEND_SPLIT_AND_TWIST_FROM_TOP
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

.macro FRONTEND_SPLIT_AND_TWIST
	FRONTEND_TOP_MONT
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
.endm

/*
 * Algebraically fuse the top split and branch twist:
 *   x0 = t0*low + (t0*zeta)*high
 *   x1 = t1*low + (t1*(1-zeta))*high.
 *
 * Six independent Montgomery chains replace the two serial layers.  Their
 * two-term sums are centered before DFT3; exhaustive interval checking over
 * [-2(q-1),2(q-1)] gives [-1998,1998], restoring a tighter-than-canonical
 * frontend range before the existing Stage12/Stage345 lazy schedule.
 */
.macro FRONTEND_FUSED_SPLIT_TWIST
	/* Duplicate each four-coefficient Q slot into branch0/branch1 lanes. */
	vpunpcklqdq %ymm0, %ymm0, %ymm6
	vpunpcklqdq %ymm1, %ymm1, %ymm7
	vpunpcklqdq %ymm2, %ymm2, %ymm8
	vpunpcklqdq %ymm3, %ymm3, %ymm9
	vpunpcklqdq %ymm4, %ymm4, %ymm10
	vpunpcklqdq %ymm5, %ymm5, %ymm11

	/* Table row: low*qinv, low, high*qinv, high (32 bytes each). */
	vpmullw   0(%r8), %ymm6,  %ymm0
	vpmullw 128(%r8), %ymm7,  %ymm1
	vpmullw 256(%r8), %ymm8,  %ymm2
	vpmulhw  32(%r8), %ymm6,  %ymm3
	vpmulhw 160(%r8), %ymm7,  %ymm4
	vpmulhw 288(%r8), %ymm8,  %ymm5
	vpmullw  64(%r8), %ymm9,  %ymm12
	vpmullw 192(%r8), %ymm10, %ymm13
	vpmullw 320(%r8), %ymm11, %ymm14
	vpmulhw  96(%r8), %ymm9,  %ymm6
	vpmulhw 224(%r8), %ymm10, %ymm7
	vpmulhw 352(%r8), %ymm11, %ymm8
	vpmulhw %ymm15, %ymm0,  %ymm0
	vpmulhw %ymm15, %ymm1,  %ymm1
	vpmulhw %ymm15, %ymm2,  %ymm2
	vpmulhw %ymm15, %ymm12, %ymm12
	vpmulhw %ymm15, %ymm13, %ymm13
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm0,  %ymm3, %ymm3
	vpsubw %ymm1,  %ymm4, %ymm4
	vpsubw %ymm2,  %ymm5, %ymm5
	vpsubw %ymm12, %ymm6, %ymm6
	vpsubw %ymm13, %ymm7, %ymm7
	vpsubw %ymm14, %ymm8, %ymm8
	vpaddw %ymm6, %ymm3, %ymm0
	vpaddw %ymm7, %ymm4, %ymm1
	vpaddw %ymm8, %ymm5, %ymm2

	/* Exact centered checkpoint for the two-product lazy sum. */
	vpmulhrsw .Lstage12_center_10(%rip), %ymm0, %ymm3
	vpmulhrsw .Lstage12_center_10(%rip), %ymm1, %ymm4
	vpmulhrsw .Lstage12_center_10(%rip), %ymm2, %ymm5
	vpmullw %ymm15, %ymm3, %ymm3
	vpmullw %ymm15, %ymm4, %ymm4
	vpmullw %ymm15, %ymm5, %ymm5
	vpsubw %ymm3, %ymm0, %ymm0
	vpsubw %ymm4, %ymm1, %ymm1
	vpsubw %ymm5, %ymm2, %ymm2
.endm

/*
 * Wide loads already hold [Q:b0 | Q:b1 | Q+3:b0 | Q+3:b1], so the fused
 * chains can consume them directly.  Keep the two-product sum lazy here;
 * the matching Stage345 candidate centers the four stage-4 low arms later.
 */
.macro FRONTEND_FUSED_SPLIT_TWIST_DUPLICATED_NOCENTER
	/* Table row: low*qinv, low, high*qinv, high (32 bytes each). */
	vpmullw   0(%r8), %ymm0, %ymm6
	vpmullw 128(%r8), %ymm1, %ymm7
	vpmullw 256(%r8), %ymm2, %ymm8
	vpmulhw  32(%r8), %ymm0, %ymm9
	vpmulhw 160(%r8), %ymm1, %ymm10
	vpmulhw 288(%r8), %ymm2, %ymm11
	vpmullw  64(%r8), %ymm3, %ymm12
	vpmullw 192(%r8), %ymm4, %ymm13
	vpmullw 320(%r8), %ymm5, %ymm14
	vpmulhw  96(%r8), %ymm3, %ymm0
	vpmulhw 224(%r8), %ymm4, %ymm1
	vpmulhw 352(%r8), %ymm5, %ymm2
	vpmulhw %ymm15, %ymm6,  %ymm6
	vpmulhw %ymm15, %ymm7,  %ymm7
	vpmulhw %ymm15, %ymm8,  %ymm8
	vpmulhw %ymm15, %ymm12, %ymm12
	vpmulhw %ymm15, %ymm13, %ymm13
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm6,  %ymm9,  %ymm9
	vpsubw %ymm7,  %ymm10, %ymm10
	vpsubw %ymm8,  %ymm11, %ymm11
	vpsubw %ymm12, %ymm0,  %ymm0
	vpsubw %ymm13, %ymm1,  %ymm1
	vpsubw %ymm14, %ymm2,  %ymm2
	vpaddw %ymm9,  %ymm0, %ymm0
	vpaddw %ymm10, %ymm1, %ymm1
	vpaddw %ymm11, %ymm2, %ymm2
.endm

/*
 * Partial cross-pair continuation.  The preceding DFT3 tail has already
 * fused n3=0 into ymm0; n3=1/2 remain as duplicated low/high inputs in
 * ymm1/ymm2 and ymm4/ymm5.  Keep the two remaining rows parallel so moving
 * n3=0 earlier does not serialize the whole six-chain schedule.
 */
.macro FRONTEND_FUSED_SPLIT_TWIST_ROWS12_DUPLICATED_NOCENTER
	vpmullw 128(%r8), %ymm1, %ymm6
	vpmullw 256(%r8), %ymm2, %ymm7
	vpmulhw 160(%r8), %ymm1, %ymm9
	vpmulhw 288(%r8), %ymm2, %ymm10
	vpmullw 192(%r8), %ymm4, %ymm12
	vpmullw 320(%r8), %ymm5, %ymm13
	vpmulhw 224(%r8), %ymm4, %ymm1
	vpmulhw 352(%r8), %ymm5, %ymm2
	vpmulhw %ymm15, %ymm6,  %ymm6
	vpmulhw %ymm15, %ymm7,  %ymm7
	vpmulhw %ymm15, %ymm12, %ymm12
	vpmulhw %ymm15, %ymm13, %ymm13
	vpsubw %ymm6,  %ymm9,  %ymm9
	vpsubw %ymm7,  %ymm10, %ymm10
	vpsubw %ymm12, %ymm1,  %ymm1
	vpsubw %ymm13, %ymm2,  %ymm2
	vpaddw %ymm9,  %ymm1, %ymm1
	vpaddw %ymm10, %ymm2, %ymm2
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

/* Same DFT3, with stores addressed by the non-adjacent public Q pair. */
.macro FRONTEND_DFT3_STORE_FIXED q0, q1
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

	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm1
	vmovdqa %ymm0, \q0*32(%rdi)
	vmovdqa %ymm1, \q1*32(%rdi)
	vmovdqa %xmm8, 1024+\q0*16(%rdi)
	vextracti128 $1, %ymm8, 1024+\q1*16(%rdi)
.endm

/*
 * DFT3 tail for the unrolled frontend experiments.  rdx/r8 already address
 * the next pair: the current pair consumed its twist table before entering.
 *
 * The first six DFT3 operations release ymm0/ymm1/ymm3.  The Montgomery
 * correction then releases ymm4, and the final two sums release ymm5.  Fill
 * those dead registers with the next pair's table-indexed inputs while the
 * current DFT3 dependency chain and stores finish.  ymm6..ymm10 retain the
 * current r0/r1/r2 outputs; ymm12 remains the 128-bit load staging register.
 */
.macro FRONTEND_DFT3_STORE_LOAD_NEXT
	/* Current pair: start all independent DFT3 chains. */
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4

	/* Next pair, n3=0.  ymm0/ymm3 are dead in the current DFT3. */
	movzwl 0(%rdx), %eax
	movzwl 2(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm0
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm0, %ymm0
	vpaddw %ymm2, %ymm6, %ymm6
	vmovq 768(%rsi,%rax), %xmm3
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm3, %ymm3
	vpsubw %ymm4, %ymm5, %ymm5

	/* Next pair, n3=1.  The correction has released ymm4. */
	movzwl 4(%rdx), %eax
	movzwl 6(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm1
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	vpaddw %ymm5, %ymm7, %ymm7
	vmovq 768(%rsi,%rax), %xmm4
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4
	vpsubw %ymm5, %ymm8, %ymm8

	/* Current row01 is now independent of the next pair loads. */
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm9
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm10

	/* Next pair, n3=2.  The final DFT3 sum has released ymm2/ymm5. */
	movzwl 8(%rdx), %eax
	movzwl 10(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm2
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm2, %ymm2
	vmovdqa %ymm9,    0(%rdi,%r9,2)
	vmovq 768(%rsi,%rax), %xmm5
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm5, %ymm5
	vmovdqa %ymm10,  32(%rdi,%r9,2)
	vmovdqa %xmm8, 1024(%rdi,%r9)
	vextracti128 $1, %ymm8, 1040(%rdi,%r9)
.endm

/*
 * Cross-pair high-first tail.  The next pair's high half is loaded before its
 * low half in each row.  Once the current row01 stores release ymm9/ymm10 and
 * the row2 stores release ymm8, start and finish all three next-pair top-zeta
 * Montgomery chains.  The successor therefore enters with top products
 * already resident in ymm9..ymm11.
 */
.macro FRONTEND_DFT3_STORE_LOAD_NEXT_TOP
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4

	/* Next n3=0: high first, then low, while the current DFT3 retires. */
	movzwl 0(%rdx), %eax
	movzwl 2(%rdx), %ecx
	vmovq 768(%rsi,%rax), %xmm3
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm3, %ymm3
	vpaddw %ymm2, %ymm6, %ymm6
	vmovq   0(%rsi,%rax), %xmm0
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm0, %ymm0
	vpsubw %ymm4, %ymm5, %ymm5

	/* Next n3=1: ymm4 is free after the Montgomery correction. */
	movzwl 4(%rdx), %eax
	movzwl 6(%rdx), %ecx
	vmovq 768(%rsi,%rax), %xmm4
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4
	vpaddw %ymm5, %ymm7, %ymm7
	vmovq   0(%rsi,%rax), %xmm1
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	vpsubw %ymm5, %ymm8, %ymm8

	vperm2i128 $0x20, %ymm7, %ymm6, %ymm9
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm10

	/* Next n3=2: the final current DFT3 sums have released ymm2/ymm5. */
	movzwl 8(%rdx), %eax
	movzwl 10(%rdx), %ecx
	vmovq 768(%rsi,%rax), %xmm5
	vmovq 768(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm5, %ymm5
	vmovq   0(%rsi,%rax), %xmm2
	vmovq   0(%rsi,%rcx), %xmm12
	vinserti128 $1, %xmm12, %ymm2, %ymm2

	/* Store current row01, then reuse its output registers for next top-zeta. */
	vmovdqa %ymm9,    0(%rdi,%r9,2)
	vmovdqa %ymm10,  32(%rdi,%r9,2)
	vpmullw %ymm14, %ymm3, %ymm9
	vpmullw %ymm14, %ymm4, %ymm10
	vpmullw %ymm14, %ymm5, %ymm11
	vpmulhw %ymm13, %ymm3, %ymm6
	vpmulhw %ymm13, %ymm4, %ymm7

	/* Store current row2 before its register becomes the third product high. */
	vmovdqa %xmm8, 1024(%rdi,%r9)
	vextracti128 $1, %ymm8, 1040(%rdi,%r9)
	vpmulhw %ymm13, %ymm5, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm9,  %ymm6, %ymm9
	vpsubw %ymm10, %ymm7, %ymm10
	vpsubw %ymm11, %ymm8, %ymm11
.endm

/*
 * Exact high-first schedule with generated instruction displacements.  It
 * removes six scalar offset-table loads and all indexed input addresses from
 * each pair while preserving the vector instruction order and live ranges.
 */
.macro FRONTEND_DFT3_STORE_LOAD_NEXT_TOP_FIXED o00, o01, o10, o11, o20, o21
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4

	/* Next n3=0: high first, then low. */
	vmovq 768+\o00(%rsi), %xmm3
	vmovq 768+\o01(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm3, %ymm3
	vpaddw %ymm2, %ymm6, %ymm6
	vmovq \o00(%rsi), %xmm0
	vmovq \o01(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm0, %ymm0
	vpsubw %ymm4, %ymm5, %ymm5

	/* Next n3=1. */
	vmovq 768+\o10(%rsi), %xmm4
	vmovq 768+\o11(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4
	vpaddw %ymm5, %ymm7, %ymm7
	vmovq \o10(%rsi), %xmm1
	vmovq \o11(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	vpsubw %ymm5, %ymm8, %ymm8

	vperm2i128 $0x20, %ymm7, %ymm6, %ymm9
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm10

	/* Next n3=2. */
	vmovq 768+\o20(%rsi), %xmm5
	vmovq 768+\o21(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm5, %ymm5
	vmovq \o20(%rsi), %xmm2
	vmovq \o21(%rsi), %xmm12
	vinserti128 $1, %xmm12, %ymm2, %ymm2

	vmovdqa %ymm9,    0(%rdi,%r9,2)
	vmovdqa %ymm10,  32(%rdi,%r9,2)
	vpmullw %ymm14, %ymm3, %ymm9
	vpmullw %ymm14, %ymm4, %ymm10
	vpmullw %ymm14, %ymm5, %ymm11
	vpmulhw %ymm13, %ymm3, %ymm6
	vpmulhw %ymm13, %ymm4, %ymm7

	vmovdqa %xmm8, 1024(%rdi,%r9)
	vextracti128 $1, %ymm8, 1040(%rdi,%r9)
	vpmulhw %ymm13, %ymm5, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm9,  %ymm6, %ymm9
	vpsubw %ymm10, %ymm7, %ymm10
	vpsubw %ymm11, %ymm8, %ymm11
.endm

/*
 * Wide-load high-first tail.  o10/o11 are separate only for the single
 * (30,1), n3=1 wrap; wrap1=0 uses o10 as a normal 32-byte load start.
 */
.macro FRONTEND_DFT3_STORE_LOAD_NEXT_TOP_WIDE q0, q1, o0, o10, o11, o2, wrap1
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4

	/* Next n3=0: high first, then low. */
	vpermq $0xf0, 768+\o0(%rsi), %ymm3
	vpaddw %ymm2, %ymm6, %ymm6
	vpermq $0xf0, \o0(%rsi), %ymm0
	vpsubw %ymm4, %ymm5, %ymm5

	/* Next n3=1.  Only pair (30,1) needs two wrapped broadcasts. */
	.if \wrap1
	vpbroadcastq 768+\o10(%rsi), %ymm4
	vpbroadcastq 768+\o11(%rsi), %ymm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4
	.else
	vpermq $0xf0, 768+\o10(%rsi), %ymm4
	.endif
	vpaddw %ymm5, %ymm7, %ymm7
	.if \wrap1
	vpbroadcastq \o10(%rsi), %ymm1
	vpbroadcastq \o11(%rsi), %ymm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	.else
	vpermq $0xf0, \o10(%rsi), %ymm1
	.endif
	vpsubw %ymm5, %ymm8, %ymm8

	vperm2i128 $0x20, %ymm7, %ymm6, %ymm9
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm10

	/* Next n3=2. */
	vpermq $0xf0, 768+\o2(%rsi), %ymm5
	vpermq $0xf0, \o2(%rsi), %ymm2

	/* Store the current arbitrary Q pair, then start the next top split. */
	vmovdqa %ymm9, \q0*32(%rdi)
	vmovdqa %ymm10, \q1*32(%rdi)
	vpmullw %ymm14, %ymm3, %ymm9
	vpmullw %ymm14, %ymm4, %ymm10
	vpmullw %ymm14, %ymm5, %ymm11
	vpmulhw %ymm13, %ymm3, %ymm6
	vpmulhw %ymm13, %ymm4, %ymm7

	vmovdqa %xmm8, 1024+\q0*16(%rdi)
	vextracti128 $1, %ymm8, 1024+\q1*16(%rdi)
	vpmulhw %ymm13, %ymm5, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm9,  %ymm6, %ymm9
	vpsubw %ymm10, %ymm7, %ymm10
	vpsubw %ymm11, %ymm8, %ymm11
.endm

/* Wide-load DFT3 tail for the fused split/twist candidate. */
.macro FRONTEND_DFT3_STORE_LOAD_NEXT_WIDE q0, q1, o0, o10, o11, o2, wrap1
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4

	/* Next n3=0. */
	vpermq $0xf0, \o0(%rsi), %ymm0
	vpaddw %ymm2, %ymm6, %ymm6
	vpermq $0xf0, 768+\o0(%rsi), %ymm3
	vpsubw %ymm4, %ymm5, %ymm5

	/* Next n3=1, including the sole wrapped row. */
	.if \wrap1
	vpbroadcastq \o10(%rsi), %ymm1
	vpbroadcastq \o11(%rsi), %ymm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	.else
	vpermq $0xf0, \o10(%rsi), %ymm1
	.endif
	vpaddw %ymm5, %ymm7, %ymm7
	.if \wrap1
	vpbroadcastq 768+\o10(%rsi), %ymm4
	vpbroadcastq 768+\o11(%rsi), %ymm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4
	.else
	vpermq $0xf0, 768+\o10(%rsi), %ymm4
	.endif
	vpsubw %ymm5, %ymm8, %ymm8

	vperm2i128 $0x20, %ymm7, %ymm6, %ymm9
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm10

	/* Next n3=2. */
	vpermq $0xf0, \o2(%rsi), %ymm2
	vpermq $0xf0, 768+\o2(%rsi), %ymm5

	vmovdqa %ymm9, \q0*32(%rdi)
	vmovdqa %ymm10, \q1*32(%rdi)
	vmovdqa %xmm8, 1024+\q0*16(%rdi)
	vextracti128 $1, %ymm8, 1024+\q1*16(%rdi)
.endm

/*
 * Partial cross-pair fused tail.  r8 addresses the next pair's fused table.
 * Load and completely fuse next n3=0 while the current DFT3 dependency chain
 * retires; leave duplicated n3=1/2 inputs for the two-row continuation.
 */
.macro FRONTEND_DFT3_STORE_LOAD_NEXT_WIDE_FUSE_N0 q0, q1, o0, o10, o11, o2, wrap1
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm15, %ymm4, %ymm4

	/* Next n3=0: issue both low products as soon as the wide load lands. */
	vpermq $0xf0, \o0(%rsi), %ymm0
	vpmullw   0(%r8), %ymm0, %ymm12
	vpmulhw  32(%r8), %ymm0, %ymm13
	vpaddw %ymm2, %ymm6, %ymm6

	/* The high load releases current ymm3 for the second fused chain. */
	vpermq $0xf0, 768+\o0(%rsi), %ymm3
	vpmullw  64(%r8), %ymm3, %ymm14
	vpmulhw  96(%r8), %ymm3, %ymm11
	vpsubw %ymm4, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm12, %ymm12
	vpmulhw %ymm15, %ymm14, %ymm14

	/* Finish current rows 1/2 around the two independent next-row reductions. */
	vpaddw %ymm5, %ymm7, %ymm7
	vpsubw %ymm12, %ymm13, %ymm13
	vpsubw %ymm5, %ymm8, %ymm8
	vpsubw %ymm14, %ymm11, %ymm11
	vpaddw %ymm13, %ymm11, %ymm0

	/* Next n3=1 remains duplicated and unfused for the continuation. */
	.if \wrap1
	vpbroadcastq \o10(%rsi), %ymm1
	vpbroadcastq \o11(%rsi), %ymm12
	vinserti128 $1, %xmm12, %ymm1, %ymm1
	.else
	vpermq $0xf0, \o10(%rsi), %ymm1
	.endif
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm9
	.if \wrap1
	vpbroadcastq 768+\o10(%rsi), %ymm4
	vpbroadcastq 768+\o11(%rsi), %ymm12
	vinserti128 $1, %xmm12, %ymm4, %ymm4
	.else
	vpermq $0xf0, 768+\o10(%rsi), %ymm4
	.endif
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm10

	/* Next n3=2 remains duplicated and unfused. */
	vpermq $0xf0, \o2(%rsi), %ymm2
	vpermq $0xf0, 768+\o2(%rsi), %ymm5

	vmovdqa %ymm9, \q0*32(%rdi)
	vmovdqa %ymm10, \q1*32(%rdi)
	vmovdqa %xmm8, 1024+\q0*16(%rdi)
	vextracti128 $1, %ymm8, 1024+\q1*16(%rdi)
.endm

.macro FRONTEND_PIPELINED_PAIR
	FRONTEND_SPLIT_AND_TWIST
	addq $12, %rdx
	addq $192, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT
	addq $32, %r9
.endm

.macro FRONTEND_FINAL_PAIR
	FRONTEND_SPLIT_AND_TWIST
	FRONTEND_DFT3_STORE
.endm

.macro FRONTEND_FUSED_SPLIT_TWIST_PIPELINED_PAIR
	FRONTEND_FUSED_SPLIT_TWIST
	addq $12, %rdx
	addq $384, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT
	addq $32, %r9
.endm

.macro FRONTEND_FUSED_SPLIT_TWIST_FINAL_PAIR
	FRONTEND_FUSED_SPLIT_TWIST
	FRONTEND_DFT3_STORE
.endm

.macro FRONTEND_HIGH_FIRST_PIPELINED_PAIR
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
	addq $12, %rdx
	addq $192, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_TOP
	addq $32, %r9
.endm

.macro FRONTEND_HIGH_FIRST_FINAL_PAIR
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
	FRONTEND_DFT3_STORE
.endm

.macro FRONTEND_HIGH_FIRST_FIXED_PIPELINED_PAIR o00, o01, o10, o11, o20, o21
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
	addq $192, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_TOP_FIXED \o00, \o01, \o10, \o11, \o20, \o21
	addq $32, %r9
.endm

.macro FRONTEND_WIDE_HIGH_FIRST_PIPELINED_PAIR q0, q1, o0, o1, o2
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
	addq $192, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_TOP_WIDE \q0, \q1, \o0, \o1, \o1, \o2, 0
.endm

.macro FRONTEND_WIDE_HIGH_FIRST_PIPELINED_PAIR_WRAP1 q0, q1, o0, o10, o11, o2
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
	addq $192, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_TOP_WIDE \q0, \q1, \o0, \o10, \o11, \o2, 1
.endm

.macro FRONTEND_WIDE_HIGH_FIRST_FINAL_PAIR q0, q1
	FRONTEND_SPLIT_AND_TWIST_FROM_TOP
	FRONTEND_DFT3_STORE_FIXED \q0, \q1
.endm

.macro FRONTEND_WIDE_FUSED_PIPELINED_PAIR q0, q1, o0, o1, o2
	FRONTEND_FUSED_SPLIT_TWIST_DUPLICATED_NOCENTER
	addq $384, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_WIDE \q0, \q1, \o0, \o1, \o1, \o2, 0
.endm

.macro FRONTEND_WIDE_FUSED_PIPELINED_PAIR_WRAP1 q0, q1, o0, o10, o11, o2
	FRONTEND_FUSED_SPLIT_TWIST_DUPLICATED_NOCENTER
	addq $384, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_WIDE \q0, \q1, \o0, \o10, \o11, \o2, 1
.endm

.macro FRONTEND_WIDE_FUSED_FINAL_PAIR q0, q1
	FRONTEND_FUSED_SPLIT_TWIST_DUPLICATED_NOCENTER
	FRONTEND_DFT3_STORE_FIXED \q0, \q1
.endm

/* Current pair is already fully fused; return with the next pair fully fused. */
.macro FRONTEND_WIDE_FUSED_PARTIAL_N0_PIPELINED_PAIR q0, q1, o0, o1, o2
	addq $384, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_WIDE_FUSE_N0 \q0, \q1, \o0, \o1, \o1, \o2, 0
	FRONTEND_FUSED_SPLIT_TWIST_ROWS12_DUPLICATED_NOCENTER
.endm

.macro FRONTEND_WIDE_FUSED_PARTIAL_N0_PIPELINED_PAIR_WRAP1 q0, q1, o0, o10, o11, o2
	addq $384, %r8
	FRONTEND_DFT3_STORE_LOAD_NEXT_WIDE_FUSE_N0 \q0, \q1, \o0, \o10, \o11, \o2, 1
	FRONTEND_FUSED_SPLIT_TWIST_ROWS12_DUPLICATED_NOCENTER
.endm

.macro FRONTEND_WIDE_FUSED_PARTIAL_N0_FINAL_PAIR q0, q1
	FRONTEND_DFT3_STORE_FIXED \q0, \q1
.endm

#include "gt_ntt_frontend_fixed_offsets.inc"

/*
 * Stripe-first frontend for the no-handoff producer.  A pair is either
 * (q,q+16) or (q+8,q+24), so its two 128-bit halves are already a stage-1
 * butterfly.  ymm12 holds q; ymm13..ymm15 may hold the first pair's three
 * stage-1 rows while the second pair uses ymm0..ymm11.
 */
.macro STRIPE_FRONTEND_LOADS
	movzwl 0(%rdx), %eax
	movzwl 2(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm0
	vmovq   0(%rsi,%rcx), %xmm6
	vinserti128 $1, %xmm6, %ymm0, %ymm0
	vmovq 768(%rsi,%rax), %xmm3
	vmovq 768(%rsi,%rcx), %xmm6
	vinserti128 $1, %xmm6, %ymm3, %ymm3

	movzwl 4(%rdx), %eax
	movzwl 6(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm1
	vmovq   0(%rsi,%rcx), %xmm6
	vinserti128 $1, %xmm6, %ymm1, %ymm1
	vmovq 768(%rsi,%rax), %xmm4
	vmovq 768(%rsi,%rcx), %xmm6
	vinserti128 $1, %xmm6, %ymm4, %ymm4

	movzwl 8(%rdx), %eax
	movzwl 10(%rdx), %ecx
	vmovq   0(%rsi,%rax), %xmm2
	vmovq   0(%rsi,%rcx), %xmm6
	vinserti128 $1, %xmm6, %ymm2, %ymm2
	vmovq 768(%rsi,%rax), %xmm5
	vmovq 768(%rsi,%rcx), %xmm6
	vinserti128 $1, %xmm6, %ymm5, %ymm5
.endm

.macro STRIPE_FRONTEND_SPLIT_AND_TWIST
	/* ymm11 keeps zeta*qinv; stagger the third product-high for one free YMM. */
	vpmullw %ymm11, %ymm3, %ymm6
	vpmullw %ymm11, %ymm4, %ymm7
	vpmullw %ymm11, %ymm5, %ymm8
	vpmulhw .Lfront_zeta_top(%rip), %ymm3, %ymm9
	vpmulhw .Lfront_zeta_top(%rip), %ymm4, %ymm10
	vpmulhw %ymm12, %ymm6, %ymm6
	vpmulhw %ymm12, %ymm7, %ymm7
	vpmulhw %ymm12, %ymm8, %ymm8
	vpsubw %ymm6, %ymm9, %ymm9
	vpsubw %ymm7, %ymm10, %ymm10
	vpaddw %ymm9,  %ymm0, %ymm6
	vpaddw %ymm10, %ymm1, %ymm7
	vpaddw %ymm3, %ymm0, %ymm3
	vpaddw %ymm4, %ymm1, %ymm4
	vpsubw %ymm9,  %ymm3, %ymm3
	vpsubw %ymm10, %ymm4, %ymm4
	vpunpcklqdq %ymm3, %ymm6, %ymm6
	vpunpcklqdq %ymm4, %ymm7, %ymm7

	/* The first two streams released ymm9 for the third product-high. */
	vpmulhw .Lfront_zeta_top(%rip), %ymm5, %ymm9
	vpsubw %ymm8, %ymm9, %ymm9
	vpaddw %ymm9, %ymm2, %ymm8
	vpaddw %ymm5, %ymm2, %ymm5
	vpsubw %ymm9, %ymm5, %ymm5
	vpunpcklqdq %ymm5, %ymm8, %ymm8

	/* Each generated stripe entry remains [twist*qinv | twist]. */
	vpmullw   0(%r8), %ymm6, %ymm3
	vpmullw  64(%r8), %ymm7, %ymm4
	vpmullw 128(%r8), %ymm8, %ymm5
	vpmulhw  32(%r8), %ymm6, %ymm0
	vpmulhw  96(%r8), %ymm7, %ymm1
	vpmulhw 160(%r8), %ymm8, %ymm2
	vpmulhw %ymm12, %ymm3, %ymm3
	vpmulhw %ymm12, %ymm4, %ymm4
	vpmulhw %ymm12, %ymm5, %ymm5
	vpsubw %ymm3, %ymm0, %ymm0
	vpsubw %ymm4, %ymm1, %ymm1
	vpsubw %ymm5, %ymm2, %ymm2
.endm

.macro STRIPE_FRONTEND_DFT3
	/* Outputs are r0=ymm6, r1=ymm7, r2=ymm8. */
	vpsubw %ymm2, %ymm1, %ymm3
	vpmullw .Lfront_omega3_qinv(%rip), %ymm3, %ymm4
	vpmulhw .Lfront_omega3(%rip), %ymm3, %ymm5
	vpaddw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpmulhw %ymm12, %ymm4, %ymm4
	vpaddw %ymm2, %ymm6, %ymm6
	vpsubw %ymm4, %ymm5, %ymm5
	vpaddw %ymm5, %ymm7, %ymm7
	vpsubw %ymm5, %ymm8, %ymm8
.endm

/*
 * Stage 1 for pair A.  Rejoin row0/row1 before the butterfly, so both rows
 * share one full-YMM Montgomery chain.  Save row01 sums/differences plus the
 * packed row2 result in ymm13..ymm15.
 */
.macro STRIPE_STAGE1_SAVE
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm1
	vpmullw .Lstage12_r_qinv(%rip), %ymm1, %ymm2
	vpmulhw .Lstage12_r(%rip), %ymm1, %ymm1
	vextracti128 $1, %ymm8, %xmm3
	vpmullw .Lstage12_r_qinv(%rip), %xmm3, %xmm4
	vpmulhw .Lstage12_r(%rip), %xmm3, %xmm3
	vpmulhw %ymm12, %ymm2, %ymm2
	vpmulhw %xmm12, %xmm4, %xmm4
	vpsubw %ymm2, %ymm1, %ymm1
	vpsubw %xmm4, %xmm3, %xmm3
	vpaddw %ymm1, %ymm0, %ymm13
	vpsubw %ymm1, %ymm0, %ymm14
	vpaddw %xmm3, %xmm8, %xmm15
	vpsubw %xmm3, %xmm8, %xmm5
	vinserti128 $1, %xmm5, %ymm15, %ymm15
.endm

/*
 * Stage 1 for pair B, then three interleaved packed stage-2 chains.  row0 and
 * row1 are rejoined per canonical Q slot; row2 is already [Q|Q+16].
 */
.macro STRIPE_STAGE12_FINISH_STORE
	/* Pair-B stage 1: row01 full YMM plus singleton row2 XMM. */
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm1
	vpmullw .Lstage12_r_qinv(%rip), %ymm1, %ymm2
	vpmulhw .Lstage12_r(%rip), %ymm1, %ymm1
	vextracti128 $1, %ymm8, %xmm3
	vpmullw .Lstage12_r_qinv(%rip), %xmm3, %xmm4
	vpmulhw .Lstage12_r(%rip), %xmm3, %xmm3
	vpmulhw %ymm12, %ymm2, %ymm2
	vpmulhw %xmm12, %xmm4, %xmm4
	vpsubw %ymm2, %ymm1, %ymm1
	vpsubw %xmm4, %xmm3, %xmm3
	vpaddw %ymm1, %ymm0, %ymm9
	vpsubw %ymm1, %ymm0, %ymm10
	vpaddw %xmm3, %xmm8, %xmm11
	vpsubw %xmm3, %xmm8, %xmm5
	vinserti128 $1, %xmm5, %ymm11, %ymm11

	/* Stage 2: identity, omega^8, and packed mixed-half chains. */
	vpmullw .Lstage12_r_qinv(%rip), %ymm9, %ymm0
	vpmullw .Lstage12_omega8_qinv(%rip), %ymm10, %ymm1
	vpmullw .Lstage12_row2_qinv(%rip), %ymm11, %ymm2
	vpmulhw .Lstage12_r(%rip), %ymm9, %ymm9
	vpmulhw .Lstage12_omega8(%rip), %ymm10, %ymm10
	vpmulhw .Lstage12_row2_factor(%rip), %ymm11, %ymm11
	vpmulhw %ymm12, %ymm0, %ymm0
	vpmulhw %ymm12, %ymm1, %ymm1
	vpmulhw %ymm12, %ymm2, %ymm2
	vpsubw %ymm0, %ymm9, %ymm9
	vpsubw %ymm1, %ymm10, %ymm10
	vpsubw %ymm2, %ymm11, %ymm11

	vpaddw %ymm9,  %ymm13, %ymm3
	vpsubw %ymm9,  %ymm13, %ymm4
	vpaddw %ymm10, %ymm14, %ymm5
	vpsubw %ymm10, %ymm14, %ymm6
	vpaddw %ymm11, %ymm15, %ymm7
	vpsubw %ymm11, %ymm15, %ymm8
	vmovdqa %ymm3,    0(%rdi,%r9)
	vmovdqa %ymm4,  256(%rdi,%r9)
	vmovdqa %ymm5,  512(%rdi,%r9)
	vmovdqa %ymm6,  768(%rdi,%r9)
	vmovdqa %ymm7, 1024(%rdi,%r9)
	vmovdqa %ymm8, 1280(%rdi,%r9)
.endm

.macro STRIPE_FRONTEND_STAGE12_BODY
	leaq gt_frontend_stripe_input_byte_offset(%rip), %rdx
	leaq gt_frontend_stripe_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_q(%rip), %ymm12
	xorl %r9d, %r9d
.p2align 5
.Lstripe_loop\@:
	vmovdqa .Lfront_zeta_top_qinv(%rip), %ymm11
	/* Pair A = (q,q+16). */
	STRIPE_FRONTEND_LOADS
	STRIPE_FRONTEND_SPLIT_AND_TWIST
	STRIPE_FRONTEND_DFT3
	STRIPE_STAGE1_SAVE
	addq $12, %rdx
	addq $192, %r8

	/* Pair B = (q+8,q+24). */
	STRIPE_FRONTEND_LOADS
	STRIPE_FRONTEND_SPLIT_AND_TWIST
	STRIPE_FRONTEND_DFT3
	STRIPE_STAGE12_FINISH_STORE
	addq $12, %rdx
	addq $192, %r8
	addq $32, %r9
	cmpq $256, %r9
	jne .Lstripe_loop\@
.endm

/*
 * Lower-pressure stripe experiment.  It uses the original frontend schedule
 * and temporarily writes pair A's three stage-1 vectors into their eventual
 * stage2 output slots.  Pair B then reloads only those 768 bytes in total.
 */
.macro HALF_FRONTEND_DFT3
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
.endm

.macro HALF_STAGE1_STORE
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm1
	vpmullw .Lstage12_r_qinv(%rip), %ymm1, %ymm2
	vpmulhw .Lstage12_r(%rip), %ymm1, %ymm1
	vextracti128 $1, %ymm8, %xmm3
	vpmullw .Lstage12_r_qinv(%rip), %xmm3, %xmm4
	vpmulhw .Lstage12_r(%rip), %xmm3, %xmm3
	vpmulhw %ymm15, %ymm2, %ymm2
	vpmulhw %xmm15, %xmm4, %xmm4
	vpsubw %ymm2, %ymm1, %ymm1
	vpsubw %xmm4, %xmm3, %xmm3
	vpaddw %ymm1, %ymm0, %ymm9
	vpsubw %ymm1, %ymm0, %ymm10
	vpaddw %xmm3, %xmm8, %xmm11
	vpsubw %xmm3, %xmm8, %xmm5
	vinserti128 $1, %xmm5, %ymm11, %ymm11
	vmovdqa %ymm9,     0(%rdi,%r9)
	vmovdqa %ymm10,  512(%rdi,%r9)
	vmovdqa %ymm11, 1024(%rdi,%r9)
.endm

.macro HALF_STAGE12_FINISH_STORE
	/* Pair-B stage 1. */
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm1
	vpmullw .Lstage12_r_qinv(%rip), %ymm1, %ymm2
	vpmulhw .Lstage12_r(%rip), %ymm1, %ymm1
	vextracti128 $1, %ymm8, %xmm3
	vpmullw .Lstage12_r_qinv(%rip), %xmm3, %xmm4
	vpmulhw .Lstage12_r(%rip), %xmm3, %xmm3
	vpmulhw %ymm15, %ymm2, %ymm2
	vpmulhw %xmm15, %xmm4, %xmm4
	vpsubw %ymm2, %ymm1, %ymm1
	vpsubw %xmm4, %xmm3, %xmm3
	vpaddw %ymm1, %ymm0, %ymm9
	vpsubw %ymm1, %ymm0, %ymm10
	vpaddw %xmm3, %xmm8, %xmm11
	vpsubw %xmm3, %xmm8, %xmm5
	vinserti128 $1, %xmm5, %ymm11, %ymm11

	/* Reload pair A and issue the three stage-2 chains together. */
	vmovdqa    0(%rdi,%r9), %ymm3
	vmovdqa  512(%rdi,%r9), %ymm4
	vmovdqa 1024(%rdi,%r9), %ymm5
	vpmullw .Lstage12_r_qinv(%rip), %ymm9, %ymm0
	vpmullw .Lstage12_omega8_qinv(%rip), %ymm10, %ymm1
	vpmullw .Lstage12_row2_qinv(%rip), %ymm11, %ymm2
	vpmulhw .Lstage12_r(%rip), %ymm9, %ymm9
	vpmulhw .Lstage12_omega8(%rip), %ymm10, %ymm10
	vpmulhw .Lstage12_row2_factor(%rip), %ymm11, %ymm11
	vpmulhw %ymm15, %ymm0, %ymm0
	vpmulhw %ymm15, %ymm1, %ymm1
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm0, %ymm9, %ymm9
	vpsubw %ymm1, %ymm10, %ymm10
	vpsubw %ymm2, %ymm11, %ymm11

	vpaddw %ymm9,  %ymm3, %ymm6
	vpsubw %ymm9,  %ymm3, %ymm7
	vpaddw %ymm10, %ymm4, %ymm8
	vpsubw %ymm10, %ymm4, %ymm12
	vpaddw %ymm11, %ymm5, %ymm0
	vpsubw %ymm11, %ymm5, %ymm1
	vmovdqa %ymm6,    0(%rdi,%r9)
	vmovdqa %ymm7,  256(%rdi,%r9)
	vmovdqa %ymm8,  512(%rdi,%r9)
	vmovdqa %ymm12, 768(%rdi,%r9)
	vmovdqa %ymm0, 1024(%rdi,%r9)
	vmovdqa %ymm1, 1280(%rdi,%r9)
.endm

.macro HALF_FRONTEND_STAGE12_BODY
	leaq gt_frontend_stripe_input_byte_offset(%rip), %rdx
	leaq gt_frontend_stripe_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_zeta_top(%rip), %ymm13
	vmovdqa .Lfront_zeta_top_qinv(%rip), %ymm14
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r9d, %r9d
.p2align 5
.Lhalf_loop\@:
	FRONTEND_LOADS
	FRONTEND_SPLIT_AND_TWIST
	HALF_FRONTEND_DFT3
	HALF_STAGE1_STORE
	addq $12, %rdx
	addq $192, %r8

	FRONTEND_LOADS
	FRONTEND_SPLIT_AND_TWIST
	HALF_FRONTEND_DFT3
	HALF_STAGE12_FINISH_STORE
	addq $12, %rdx
	addq $192, %r8
	addq $32, %r9
	cmpq $256, %r9
	jne .Lhalf_loop\@
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
 * Benchmark-only frontend schedules.  Both retain the generated CRT offset
 * table and the exact 1536-byte semantic layout consumed by STAGE12_BODY.
 *
 * u2 runs seven two-pair groups (pairs 0..13), with each current DFT3 tail
 * preloading the next pair.  Pairs 14 and 15 form a straight-line epilogue so
 * the final pair never reads beyond the offset table.
 */
.macro FRONTEND_U2_BODY
	leaq gt_frontend_input_byte_offset(%rip), %rdx
	leaq gt_frontend_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_zeta_top(%rip), %ymm13
	vmovdqa .Lfront_zeta_top_qinv(%rip), %ymm14
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r9d, %r9d

	/* Prologue: pair 0 must be resident before the first pipelined tail. */
	FRONTEND_LOADS
.p2align 5
.Lfrontend_u2_loop\@:
	FRONTEND_PIPELINED_PAIR
	FRONTEND_PIPELINED_PAIR
	cmpq $448, %r9
	jne .Lfrontend_u2_loop\@

	/* Pair 14 preloads pair 15; pair 15 is store-only. */
	FRONTEND_PIPELINED_PAIR
	FRONTEND_FINAL_PAIR
.endm

/* U2 candidate 1: fused split+twist constants and parallel Mont chains. */
.macro FRONTEND_U2_FUSED_SPLIT_TWIST_BODY
	leaq gt_frontend_input_byte_offset(%rip), %rdx
	leaq gt_frontend_fused_split_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r9d, %r9d

	FRONTEND_LOADS
.p2align 5
.Lfrontend_u2_fused_split_twist_loop\@:
	FRONTEND_FUSED_SPLIT_TWIST_PIPELINED_PAIR
	FRONTEND_FUSED_SPLIT_TWIST_PIPELINED_PAIR
	cmpq $448, %r9
	jne .Lfrontend_u2_fused_split_twist_loop\@

	FRONTEND_FUSED_SPLIT_TWIST_PIPELINED_PAIR
	FRONTEND_FUSED_SPLIT_TWIST_FINAL_PAIR
.endm

/* U2 candidate 2: next pair's top-zeta product crosses the DFT3/store tail. */
.macro FRONTEND_U2_HIGH_FIRST_BODY
	leaq gt_frontend_input_byte_offset(%rip), %rdx
	leaq gt_frontend_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_zeta_top(%rip), %ymm13
	vmovdqa .Lfront_zeta_top_qinv(%rip), %ymm14
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r9d, %r9d

	FRONTEND_LOADS
	FRONTEND_TOP_MONT
.p2align 5
.Lfrontend_u2_high_first_loop\@:
	FRONTEND_HIGH_FIRST_PIPELINED_PAIR
	FRONTEND_HIGH_FIRST_PIPELINED_PAIR
	cmpq $448, %r9
	jne .Lfrontend_u2_high_first_loop\@

	FRONTEND_HIGH_FIRST_PIPELINED_PAIR
	FRONTEND_HIGH_FIRST_FINAL_PAIR
.endm

/*
 * u4 runs three four-pair groups (pairs 0..11).  The straight-line epilogue
 * handles pairs 12..15.  This removes four loop branches relative to u2 while
 * preserving the same next-pair load distance and live-register contract.
 */
.macro FRONTEND_U4_BODY
	leaq gt_frontend_input_byte_offset(%rip), %rdx
	leaq gt_frontend_twist_qinv_factor(%rip), %r8
	vmovdqa .Lfront_zeta_top(%rip), %ymm13
	vmovdqa .Lfront_zeta_top_qinv(%rip), %ymm14
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r9d, %r9d

	/* Prologue: pair 0 must be resident before the first pipelined tail. */
	FRONTEND_LOADS
.p2align 5
.Lfrontend_u4_loop\@:
	FRONTEND_PIPELINED_PAIR
	FRONTEND_PIPELINED_PAIR
	FRONTEND_PIPELINED_PAIR
	FRONTEND_PIPELINED_PAIR
	cmpq $384, %r9
	jne .Lfrontend_u4_loop\@

	/* Pair 12 preloads 13, then 14, then 15; pair 15 is store-only. */
	FRONTEND_PIPELINED_PAIR
	FRONTEND_PIPELINED_PAIR
	FRONTEND_PIPELINED_PAIR
	FRONTEND_FINAL_PAIR
.endm

/*
 * Two breadth-first radix-2 layers.  All Montgomery chains at a dependency
 * level are issued together.  The high input of each butterfly is reduced by
 * its fixed factor; additions remain lazy, giving the existing 4(q-1) and
 * 5(q-1) stage bounds.
 */
.macro STAGE12_BODY centered_identity=0
	vmovdqa .Lstage12_row2_factor(%rip), %ymm9
	vmovdqa .Lstage12_row2_qinv(%rip), %ymm10
	vmovdqa .Lstage12_omega8(%rip), %ymm11
	vmovdqa .Lstage12_omega8_qinv(%rip), %ymm12
	.if \centered_identity
	vmovdqa .Lstage12_center_10(%rip), %ymm13
	.else
	vmovdqa .Lstage12_r(%rip), %ymm13
	vmovdqa .Lstage12_r_qinv(%rip), %ymm14
	.endif
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
	.if \centered_identity
	vpmulhrsw %ymm13, %ymm2, %ymm4
	vpmulhrsw %ymm13, %ymm3, %ymm5
	vpmullw %ymm15, %ymm4, %ymm4
	vpmullw %ymm15, %ymm5, %ymm5
	vpsubw %ymm4, %ymm2, %ymm2
	vpsubw %ymm5, %ymm3, %ymm3
	.else
	vpmullw %ymm14, %ymm2, %ymm4
	vpmullw %ymm14, %ymm3, %ymm5
	vpmulhw %ymm13, %ymm2, %ymm6
	vpmulhw %ymm13, %ymm3, %ymm7
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpsubw %ymm4, %ymm6, %ymm2
	vpsubw %ymm5, %ymm7, %ymm3
	.endif
	vpaddw %ymm2, %ymm0, %ymm4
	vpsubw %ymm2, %ymm0, %ymm5
	vpaddw %ymm3, %ymm1, %ymm6
	vpsubw %ymm3, %ymm1, %ymm7

	/* Stage 2: identity and omega^8 chains are independent. */
	.if \centered_identity
	vpmulhrsw %ymm13, %ymm6, %ymm8
	.else
	vpmullw %ymm14, %ymm6, %ymm8
	.endif
	vpmullw %ymm12, %ymm7, %ymm2
	.if !\centered_identity
	vpmulhw %ymm13, %ymm6, %ymm6
	.endif
	vpmulhw %ymm11, %ymm7, %ymm7
	.if \centered_identity
	vpmullw %ymm15, %ymm8, %ymm8
	.else
	vpmulhw %ymm15, %ymm8, %ymm8
	.endif
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
	.if \centered_identity
	vpmulhrsw %xmm13, %xmm2, %xmm4
	vpmulhrsw %xmm13, %xmm3, %xmm5
	vpmullw %xmm15, %xmm4, %xmm4
	vpmullw %xmm15, %xmm5, %xmm5
	vpsubw %xmm4, %xmm2, %xmm2
	vpsubw %xmm5, %xmm3, %xmm3
	.else
	vpmullw %xmm14, %xmm2, %xmm4
	vpmullw %xmm14, %xmm3, %xmm5
	vpmulhw %xmm13, %xmm2, %xmm6
	vpmulhw %xmm13, %xmm3, %xmm7
	vpmulhw %xmm15, %xmm4, %xmm4
	vpmulhw %xmm15, %xmm5, %xmm5
	vpsubw %xmm4, %xmm6, %xmm2
	vpsubw %xmm5, %xmm7, %xmm3
	.endif
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

/*
 * Identity-reduced Stage1/2 candidate with two adjacent singleton-row Q
 * values in each YMM.  For even q, the four row2 loads have lane semantics
 *
 *   ymm0 = [row2[q]    | row2[q+1]]
 *   ymm1 = [row2[q+8]  | row2[q+9]]
 *   ymm2 = [row2[q+16] | row2[q+17]]
 *   ymm3 = [row2[q+24] | row2[q+25]].
 *
 * After the two layers, four vperm2i128 instructions restore the existing
 * consumer contract row2_packed[Q]=[Q | Q+16].  The row01 arithmetic is the
 * selected centered-identity schedule copied byte-for-byte into two adjacent
 * stripes; only the singleton row changes its lane occupancy and schedule.
 */
.macro STAGE12_IDENTITY_ROW01_STRIPE byte_offset
	vmovdqa \byte_offset+0(%rsi,%r9), %ymm0
	vmovdqa \byte_offset+256(%rsi,%r9), %ymm1
	vmovdqa \byte_offset+512(%rsi,%r9), %ymm2
	vmovdqa \byte_offset+768(%rsi,%r9), %ymm3

	vpmulhrsw %ymm13, %ymm2, %ymm4
	vpmulhrsw %ymm13, %ymm3, %ymm5
	vpmullw %ymm15, %ymm4, %ymm4
	vpmullw %ymm15, %ymm5, %ymm5
	vpsubw %ymm4, %ymm2, %ymm2
	vpsubw %ymm5, %ymm3, %ymm3
	vpaddw %ymm2, %ymm0, %ymm4
	vpsubw %ymm2, %ymm0, %ymm5
	vpaddw %ymm3, %ymm1, %ymm6
	vpsubw %ymm3, %ymm1, %ymm7

	vpmulhrsw %ymm13, %ymm6, %ymm8
	vpmullw %ymm12, %ymm7, %ymm2
	vpmulhw %ymm11, %ymm7, %ymm7
	vpmullw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm2, %ymm2
	vpsubw %ymm8, %ymm6, %ymm6
	vpsubw %ymm2, %ymm7, %ymm7
	vpaddw %ymm6, %ymm4, %ymm0
	vpsubw %ymm6, %ymm4, %ymm1
	vpaddw %ymm7, %ymm5, %ymm2
	vpsubw %ymm7, %ymm5, %ymm3
	vmovdqa %ymm0, \byte_offset+0(%rdi,%r9)
	vmovdqa %ymm1, \byte_offset+256(%rdi,%r9)
	vmovdqa %ymm2, \byte_offset+512(%rdi,%r9)
	vmovdqa %ymm3, \byte_offset+768(%rdi,%r9)
.endm

.macro STAGE12_IDENTITY_ROW2Q2_BODY
	vmovdqa .Lstage12_omega8(%rip), %ymm11
	vmovdqa .Lstage12_omega8_qinv(%rip), %ymm12
	vmovdqa .Lstage12_center_10(%rip), %ymm13
	vmovdqa .Lfront_q(%rip), %ymm15
	xorl %r8d, %r8d
	xorl %r9d, %r9d
.p2align 5
.Lstage12_identity_row2q2_loop\@:
	/* Two full-row stripes q and q+1. */
	STAGE12_IDENTITY_ROW01_STRIPE 0
	STAGE12_IDENTITY_ROW01_STRIPE 32

	/* Four adjacent-Q YMMs: low half q, high half q+1. */
	vmovdqa 1024(%rsi,%r8), %ymm0
	vmovdqa 1152(%rsi,%r8), %ymm1
	vmovdqa 1280(%rsi,%r8), %ymm2
	vmovdqa 1408(%rsi,%r8), %ymm3

	/* Stage 1: reduce Q+16/Q+24, then form both adjacent stripes. */
	vpmulhrsw %ymm13, %ymm2, %ymm4
	vpmulhrsw %ymm13, %ymm3, %ymm5
	vpmullw %ymm15, %ymm4, %ymm4
	vpmullw %ymm15, %ymm5, %ymm5
	vpsubw %ymm4, %ymm2, %ymm2
	vpsubw %ymm5, %ymm3, %ymm3
	vpaddw %ymm2, %ymm0, %ymm4
	vpsubw %ymm2, %ymm0, %ymm5
	vpaddw %ymm3, %ymm1, %ymm6
	vpsubw %ymm3, %ymm1, %ymm7

	/* Stage 2: independent identity and omega^8 chains. */
	vpmulhrsw %ymm13, %ymm6, %ymm0
	vpmullw %ymm12, %ymm7, %ymm1
	vpmulhw %ymm11, %ymm7, %ymm7
	vpmullw %ymm15, %ymm0, %ymm0
	vpmulhw %ymm15, %ymm1, %ymm1
	vpsubw %ymm0, %ymm6, %ymm6
	vpsubw %ymm1, %ymm7, %ymm7
	vpaddw %ymm6, %ymm4, %ymm0
	vpsubw %ymm6, %ymm4, %ymm1
	vpaddw %ymm7, %ymm5, %ymm2
	vpsubw %ymm7, %ymm5, %ymm3

	/* Restore row2_packed[Q]=[Q | Q+16] for q and q+1. */
	vperm2i128 $0x20, %ymm2, %ymm0, %ymm4
	vperm2i128 $0x31, %ymm2, %ymm0, %ymm5
	vperm2i128 $0x20, %ymm3, %ymm1, %ymm6
	vperm2i128 $0x31, %ymm3, %ymm1, %ymm7
	vmovdqa %ymm4, 1024(%rdi,%r9)
	vmovdqa %ymm5, 1056(%rdi,%r9)
	vmovdqa %ymm6, 1280(%rdi,%r9)
	vmovdqa %ymm7, 1312(%rdi,%r9)

	addq $32, %r8
	addq $64, %r9
	cmpq $256, %r9
	jne .Lstage12_identity_row2q2_loop\@
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

/* Standalone benchmark-only stage1+2 identity-reducer candidate. */
.p2align 5
.globl gt_ntt_avx2_stage12_identity_asm
.type gt_ntt_avx2_stage12_identity_asm,@function
gt_ntt_avx2_stage12_identity_asm:
	STAGE12_BODY 1
	vzeroupper
	ret
.size gt_ntt_avx2_stage12_identity_asm,.-gt_ntt_avx2_stage12_identity_asm

/* Standalone boundary entry for the adjacent-Q singleton-row candidate. */
.p2align 5
.globl gt_ntt_avx2_stage12_identity_row2q2_asm
.type gt_ntt_avx2_stage12_identity_row2q2_asm,@function
gt_ntt_avx2_stage12_identity_row2q2_asm:
	STAGE12_IDENTITY_ROW2Q2_BODY
	vzeroupper
	ret
.size gt_ntt_avx2_stage12_identity_row2q2_asm,.-gt_ntt_avx2_stage12_identity_row2q2_asm

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

/*
 * Canonical frontend plus the signed identity-reducer stage1+2 candidate.
 * This keeps the same 1536-byte semantic handoff so a benchmark isolates the
 * identity reduction change.
 */
.p2align 5
.globl gt_ntt_avx2_frontend_stage12_identity_asm
.type gt_ntt_avx2_frontend_stage12_identity_asm,@function
gt_ntt_avx2_frontend_stage12_identity_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp
	movq %rsp, %rdi
	FRONTEND_BODY
	movq %r10, %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_identity_asm,.-gt_ntt_avx2_frontend_stage12_identity_asm

/*
 * DFT3-tail next-pair load schedules.  These four entry points are
 * benchmark-only: they preserve the canonical semantic scratch and differ
 * only in frontend unroll factor and the standalone stage1+2 reducer choice.
 */
.p2align 5
.globl gt_ntt_avx2_frontend_stage12_u2_asm
.type gt_ntt_avx2_frontend_stage12_u2_asm,@function
gt_ntt_avx2_frontend_stage12_u2_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp
	movq %rsp, %rdi
	FRONTEND_U2_BODY
	movq %r10, %rdi
	movq %rsp, %rsi
	STAGE12_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_u2_asm,.-gt_ntt_avx2_frontend_stage12_u2_asm

.p2align 5
.globl gt_ntt_avx2_frontend_stage12_u4_asm
.type gt_ntt_avx2_frontend_stage12_u4_asm,@function
gt_ntt_avx2_frontend_stage12_u4_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp
	movq %rsp, %rdi
	FRONTEND_U4_BODY
	movq %r10, %rdi
	movq %rsp, %rsi
	STAGE12_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_u4_asm,.-gt_ntt_avx2_frontend_stage12_u4_asm

.p2align 5
.globl gt_ntt_avx2_frontend_stage12_u2_identity_asm
.type gt_ntt_avx2_frontend_stage12_u2_identity_asm,@function
gt_ntt_avx2_frontend_stage12_u2_identity_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp
	movq %rsp, %rdi
	FRONTEND_U2_BODY
	movq %r10, %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_u2_identity_asm,.-gt_ntt_avx2_frontend_stage12_u2_identity_asm

.p2align 5
.globl gt_ntt_avx2_frontend_stage12_u4_identity_asm
.type gt_ntt_avx2_frontend_stage12_u4_identity_asm,@function
gt_ntt_avx2_frontend_stage12_u4_identity_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $1536, %rsp
	movq %rsp, %rdi
	FRONTEND_U4_BODY
	movq %r10, %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_u4_identity_asm,.-gt_ntt_avx2_frontend_stage12_u4_identity_asm

/*
 * void gt_ntt_avx2_frontend_stage12_direct_asm(gt_stage2_scratch *out,
 *                                              const int16_t in[768])
 *
 * Stripe-first producer with no frontend semantic scratch, stack access, or
 * internal call.  out and in must not overlap.  The public forward wrapper
 * supplies a private stage2 scratch, so its out==in contract remains safe.
 */
.p2align 5
.globl gt_ntt_avx2_frontend_stage12_direct_asm
.type gt_ntt_avx2_frontend_stage12_direct_asm,@function
gt_ntt_avx2_frontend_stage12_direct_asm:
	STRIPE_FRONTEND_STAGE12_BODY
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_direct_asm,.-gt_ntt_avx2_frontend_stage12_direct_asm

/*
 * 768-byte semantic-handoff candidate.  out and in must not overlap; no stack
 * scratch or internal call is used.
 */
.p2align 5
.globl gt_ntt_avx2_frontend_stage12_half_asm
.type gt_ntt_avx2_frontend_stage12_half_asm,@function
gt_ntt_avx2_frontend_stage12_half_asm:
	HALF_FRONTEND_STAGE12_BODY
	vzeroupper
	ret
.size gt_ntt_avx2_frontend_stage12_half_asm,.-gt_ntt_avx2_frontend_stage12_half_asm

/*
 * Benchmark-only single-entry native forward candidates.
 *
 * The lower 1536 stack bytes are the existing frontend semantic scratch; the
 * upper 1536 bytes are the canonical stage2 scratch.  Keeping both boundaries
 * makes this a pure control-flow-fusion experiment: the arithmetic, lazy
 * ranges, native output mapping, and peak semantic scratch match the existing
 * two-call wrappers.  out==in remains safe because the frontend has consumed
 * the complete input before either stage2 or final output stores begin.
 */
.macro GT_FULL_NATIVE_FUSED_FUNCTION name, unroll
.p2align 5
.globl \name
.type \name,@function
\name:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	.if \unroll == 2
	FRONTEND_U2_BODY
	.else
	FRONTEND_U4_BODY
	.endif
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size \name,.-\name
.endm

GT_FULL_NATIVE_FUSED_FUNCTION gt_ntt_avx2_forward_u2_identity_native_centered_fused_asm, 2
GT_FULL_NATIVE_FUSED_FUNCTION gt_ntt_avx2_forward_u4_identity_native_centered_fused_asm, 4

/* U2 single-entry control with Stage345 next-block preload/store overlap. */
.p2align 5
.globl gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm
.type gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm,@function
gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_U2_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm,.-gt_ntt_avx2_forward_u2_identity_native_centered_pipelined_fused_asm

/* Candidate 1: algebraically fused top split + branch twist. */
.p2align 5
.globl gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_U2_FUSED_SPLIT_TWIST_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_u2_fused_split_twist_native_centered_pipelined_asm

/* Candidate 2: high-first next-pair load and cross-pair top-zeta pipeline. */
.p2align 5
.globl gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_U2_HIGH_FIRST_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_u2_high_first_native_centered_pipelined_asm

/* Pair-specific fixed-displacement version of the selected high-first path. */
.p2align 5
.globl gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_HIGH_FIRST_FIXED_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_fixed_high_first_native_centered_pipelined_asm

/* Priority 1: Q/Q+3 wide loads with the selected high-first arithmetic. */
.p2align 5
.globl gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_WIDE_HIGH_FIRST_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_wide_high_first_native_centered_pipelined_asm

/* Priority 2: wide duplicated loads, fused split/twist, delayed centering. */
.p2align 5
.globl gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_WIDE_FUSED_DELAYED_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_wide_fused_delayed_native_centered_pipelined_asm

/* Priority 1 follow-up: process adjacent singleton-row Q values in YMMs. */
.p2align 5
.globl gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_WIDE_FUSED_DELAYED_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_IDENTITY_ROW2Q2_BODY
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_centered_pipelined_asm

/*
 * Asymmetric-consumer candidate: keep the row2q2 schedule, but leave the
 * terminal Stage5 representatives lazy in native layout.  The Stage4 input
 * checkpoint remains mandatory; only the final eight center10 reductions per
 * block are omitted.  Output range is |x| <= 8*(q-1), modulo-equivalent to the
 * centered candidate, and intended for centered-by-lazy native basemul.
 */
.p2align 5
.globl gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm
.type gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,@function
gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp

	movq %rsp, %rdi
	FRONTEND_WIDE_FUSED_DELAYED_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_IDENTITY_ROW2Q2_BODY
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY 1, 0, 0
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,.-gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm

/*
 * Shared-code version for a forward pair.  The third argument selects final
 * centering.  SysV guarantees bit 0 of the entry stack pointer is clear, so
 * r11 carries both the original stack pointer and the one-bit mode without
 * adding semantic scratch or a callee-saved spill.  Stage345 tests that bit
 * once per block; both pair members therefore execute the same code image.
 */
.p2align 5
.globl gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm
.type gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm,@function
gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm:
	movq %rsp, %r11
	andl $1, %edx
	orq %rdx, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_WIDE_FUSED_DELAYED_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_IDENTITY_ROW2Q2_BODY
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY 1, 0, 2
	movq %r11, %rsp
	andq $-2, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm,.-gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_runtime_center_pipelined_asm

/* Priority 2 follow-up: consume the six Stage345 twiddle blocks contiguously. */
.p2align 5
.globl gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm
.type gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm,@function
gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_WIDE_FUSED_DELAYED_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY 1, 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm,.-gt_ntt_avx2_forward_wide_fused_delayed_native_centered_contiguous_twiddles_pipelined_asm

/* Partial cross-pair experiment: fuse next n3=0 in the current DFT3 tail. */
.p2align 5
.globl gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm
.type gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm,@function
gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm:
	movq %rsp, %r11
	movq %rdi, %r10
	andq $-32, %rsp
	subq $3072, %rsp
	movq %rsp, %rdi
	FRONTEND_WIDE_FUSED_PARTIAL_N0_BODY
	leaq 1536(%rsp), %rdi
	movq %rsp, %rsi
	STAGE12_BODY 1
	movq %r10, %rdi
	leaq 1536(%rsp), %rsi
	GT_NATIVE_STAGE345_PIPELINED_BODY 1
	movq %r11, %rsp
	vzeroupper
	ret
.size gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm,.-gt_ntt_avx2_forward_wide_fused_partial_n0_native_centered_pipelined_asm

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
.Lstage12_center_10:
	.rept 16
	.short 10
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
