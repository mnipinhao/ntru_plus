	.file	"gt9x16_shear.c"
	.text
	.p2align 4
	.globl	ntruplus1152_exp001_gt9x16_shear_z
	.type	ntruplus1152_exp001_gt9x16_shear_z, @function
ntruplus1152_exp001_gt9x16_shear_z:
.LFB7278:
	.cfi_startproc
	endbr64
	vmovdqu	(%rsi), %ymm7
	vmovdqu	32(%rsi), %ymm9
	vmovdqu	64(%rsi), %ymm6
	vmovdqu	96(%rsi), %ymm4
	vmovdqu	128(%rsi), %ymm2
	vmovdqu	160(%rsi), %ymm5
	vpblendw	$170, %ymm9, %ymm7, %ymm8
	vmovdqu	192(%rsi), %ymm1
	vmovdqu	224(%rsi), %ymm3
	vpblendw	$170, %ymm6, %ymm9, %ymm9
	vpblendw	$170, %ymm4, %ymm6, %ymm6
	vmovdqu	256(%rsi), %ymm0
	vpblendw	$170, %ymm2, %ymm4, %ymm4
	vpblendw	$170, %ymm5, %ymm2, %ymm2
	vpblendw	$170, %ymm1, %ymm5, %ymm5
	vpblendw	$170, %ymm3, %ymm1, %ymm1
	vpblendw	$170, %ymm0, %ymm3, %ymm3
	vpblendw	$170, %ymm7, %ymm0, %ymm0
	vpblendw	$204, %ymm6, %ymm8, %ymm7
	vpblendw	$204, %ymm2, %ymm6, %ymm6
	vpblendw	$204, %ymm1, %ymm2, %ymm2
	vpblendw	$204, %ymm0, %ymm1, %ymm1
	vpblendw	$204, %ymm9, %ymm0, %ymm0
	vpblendw	$204, %ymm4, %ymm9, %ymm9
	vpblendw	$204, %ymm5, %ymm4, %ymm4
	vpblendw	$204, %ymm3, %ymm5, %ymm5
	vpblendw	$204, %ymm8, %ymm3, %ymm3
	vpblendw	$240, %ymm2, %ymm7, %ymm8
	vpblendw	$240, %ymm0, %ymm2, %ymm2
	vpblendw	$240, %ymm4, %ymm0, %ymm0
	vmovdqu	%ymm8, (%rdi)
	vpblendw	$240, %ymm3, %ymm4, %ymm4
	vpblendw	$240, %ymm6, %ymm3, %ymm3
	vpblendw	$240, %ymm1, %ymm6, %ymm6
	vpblendw	$240, %ymm9, %ymm1, %ymm1
	vmovdqu	%ymm4, 96(%rdi)
	vpblendw	$240, %ymm5, %ymm9, %ymm9
	vpblendw	$240, %ymm7, %ymm5, %ymm5
	vmovdqu	%ymm6, 64(%rdi)
	vmovdqu	%ymm9, 32(%rdi)
	vmovdqu	%ymm2, 128(%rdi)
	vmovdqu	%ymm5, 160(%rdi)
	vmovdqu	%ymm1, 192(%rdi)
	vmovdqu	%ymm3, 224(%rdi)
	vmovdqu	%ymm0, 256(%rdi)
	vzeroupper
	ret
	.cfi_endproc
.LFE7278:
	.size	ntruplus1152_exp001_gt9x16_shear_z, .-ntruplus1152_exp001_gt9x16_shear_z
	.p2align 4
	.globl	ntruplus1152_exp001_gt9x16_shear_materialized
	.type	ntruplus1152_exp001_gt9x16_shear_materialized, @function
ntruplus1152_exp001_gt9x16_shear_materialized:
.LFB7279:
	.cfi_startproc
	endbr64
	vmovdqu	(%rsi), %ymm8
	vmovdqu	32(%rsi), %ymm7
	vmovdqu	64(%rsi), %ymm6
	vmovdqu	96(%rsi), %ymm2
	vmovdqu	128(%rsi), %ymm5
	vmovdqu	160(%rsi), %ymm4
	vpblendw	$170, %ymm7, %ymm8, %ymm9
	vmovdqu	192(%rsi), %ymm1
	vmovdqu	224(%rsi), %ymm3
	vpblendw	$170, %ymm6, %ymm7, %ymm7
	vpblendw	$170, %ymm2, %ymm6, %ymm6
	vmovdqu	256(%rsi), %ymm0
	vpblendw	$170, %ymm5, %ymm2, %ymm2
	vpblendw	$170, %ymm4, %ymm5, %ymm5
	vpblendw	$170, %ymm1, %ymm4, %ymm4
	vpblendw	$170, %ymm3, %ymm1, %ymm1
	vpblendw	$170, %ymm0, %ymm3, %ymm3
	vpblendw	$170, %ymm8, %ymm0, %ymm0
	vpblendw	$204, %ymm6, %ymm9, %ymm8
	vpblendw	$204, %ymm5, %ymm6, %ymm6
	vpblendw	$204, %ymm1, %ymm5, %ymm5
	vpblendw	$204, %ymm0, %ymm1, %ymm1
	vpblendw	$204, %ymm7, %ymm0, %ymm0
	vpblendw	$204, %ymm2, %ymm7, %ymm7
	vpblendw	$204, %ymm4, %ymm2, %ymm2
	vpblendw	$204, %ymm3, %ymm4, %ymm4
	vpblendw	$204, %ymm9, %ymm3, %ymm3
	vpblendw	$240, %ymm5, %ymm8, %ymm9
	vpblendw	$240, %ymm0, %ymm5, %ymm5
	vpblendw	$240, %ymm2, %ymm0, %ymm0
	vpblendw	$240, %ymm3, %ymm2, %ymm2
	vpblendw	$240, %ymm6, %ymm3, %ymm3
	vpblendw	$240, %ymm1, %ymm6, %ymm6
	vpblendw	$240, %ymm7, %ymm1, %ymm1
	vpblendw	$240, %ymm4, %ymm7, %ymm7
	vpblendw	$240, %ymm8, %ymm4, %ymm4
	vblendps	$240, %ymm0, %ymm9, %ymm8
	vblendps	$240, %ymm9, %ymm7, %ymm9
	vblendps	$240, %ymm3, %ymm0, %ymm0
	vblendps	$240, %ymm7, %ymm6, %ymm7
	vmovdqu	%ymm8, (%rdi)
	vblendps	$240, %ymm6, %ymm2, %ymm6
	vblendps	$240, %ymm2, %ymm5, %ymm2
	vblendps	$240, %ymm5, %ymm4, %ymm5
	vmovdqu	%ymm9, 32(%rdi)
	vblendps	$240, %ymm4, %ymm1, %ymm4
	vblendps	$240, %ymm1, %ymm3, %ymm1
	vmovdqu	%ymm7, 64(%rdi)
	vmovdqu	%ymm6, 96(%rdi)
	vmovdqu	%ymm2, 128(%rdi)
	vmovdqu	%ymm5, 160(%rdi)
	vmovdqu	%ymm4, 192(%rdi)
	vmovdqu	%ymm1, 224(%rdi)
	vmovdqu	%ymm0, 256(%rdi)
	vzeroupper
	ret
	.cfi_endproc
.LFE7279:
	.size	ntruplus1152_exp001_gt9x16_shear_materialized, .-ntruplus1152_exp001_gt9x16_shear_materialized
	.p2align 4
	.globl	ntruplus1152_exp001_gt9x16_shear_stage8
	.type	ntruplus1152_exp001_gt9x16_shear_stage8, @function
ntruplus1152_exp001_gt9x16_shear_stage8:
.LFB7280:
	.cfi_startproc
	endbr64
	vmovdqu	(%rsi), %ymm8
	vmovdqu	32(%rsi), %ymm7
	movl	$226561409, %eax
	vmovdqu	64(%rsi), %ymm6
	vmovdqu	96(%rsi), %ymm5
	vmovdqu	128(%rsi), %ymm4
	vmovdqu	160(%rsi), %ymm3
	vpblendw	$170, %ymm7, %ymm8, %ymm9
	vmovdqu	192(%rsi), %ymm2
	vmovdqu	224(%rsi), %ymm1
	vpblendw	$170, %ymm6, %ymm7, %ymm7
	vpblendw	$170, %ymm5, %ymm6, %ymm6
	vmovdqu	256(%rsi), %ymm0
	vpblendw	$170, %ymm4, %ymm5, %ymm5
	vpbroadcastw	(%rdx), %xmm12
	vpblendw	$170, %ymm3, %ymm4, %ymm4
	vpblendw	$170, %ymm2, %ymm3, %ymm3
	vpblendw	$170, %ymm1, %ymm2, %ymm2
	vpblendw	$170, %ymm0, %ymm1, %ymm1
	vpblendw	$170, %ymm8, %ymm0, %ymm0
	vpblendw	$204, %ymm6, %ymm9, %ymm8
	vpblendw	$204, %ymm4, %ymm6, %ymm6
	vpblendw	$204, %ymm2, %ymm4, %ymm4
	vpblendw	$204, %ymm0, %ymm2, %ymm2
	vpblendw	$204, %ymm7, %ymm0, %ymm0
	vpblendw	$204, %ymm5, %ymm7, %ymm7
	vpblendw	$204, %ymm3, %ymm5, %ymm5
	vpblendw	$240, %ymm4, %ymm8, %ymm10
	vpblendw	$204, %ymm1, %ymm3, %ymm3
	vpblendw	$240, %ymm0, %ymm4, %ymm4
	vpblendw	$204, %ymm9, %ymm1, %ymm1
	vpblendw	$240, %ymm5, %ymm0, %ymm0
	vpbroadcastw	(%rcx), %xmm9
	vpblendw	$240, %ymm1, %ymm5, %ymm5
	vpblendw	$240, %ymm6, %ymm1, %ymm1
	vpblendw	$240, %ymm2, %ymm6, %ymm6
	vpblendw	$240, %ymm7, %ymm2, %ymm2
	vpblendw	$240, %ymm3, %ymm7, %ymm7
	vpblendw	$240, %ymm8, %ymm3, %ymm3
	vextracti128	$0x1, %ymm0, %xmm8
	vpmullw	%xmm8, %xmm9, %xmm9
	vpmulhw	%xmm12, %xmm8, %xmm12
	vmovd	%eax, %xmm8
	vpbroadcastd	%xmm8, %xmm8
	vpmulhw	%xmm8, %xmm9, %xmm9
	vpaddw	%xmm10, %xmm12, %xmm11
	vpsubw	%xmm9, %xmm11, %xmm11
	vpaddw	%xmm10, %xmm9, %xmm9
	vextracti128	$0x1, %ymm10, %xmm10
	vpsubw	%xmm12, %xmm9, %xmm9
	vinserti128	$0x1, %xmm9, %ymm11, %ymm9
	vmovdqu	%ymm9, (%rdi)
	vpbroadcastw	2(%rcx), %xmm9
	vpbroadcastw	2(%rdx), %xmm11
	vpmullw	%xmm10, %xmm9, %xmm9
	vpmulhw	%xmm11, %xmm10, %xmm11
	vpmulhw	%xmm8, %xmm9, %xmm9
	vpaddw	%xmm7, %xmm11, %xmm10
	vpsubw	%xmm9, %xmm10, %xmm10
	vpaddw	%xmm7, %xmm9, %xmm9
	vpsubw	%xmm11, %xmm9, %xmm9
	vinserti128	$0x1, %xmm9, %ymm10, %ymm9
	vmovdqu	%ymm9, 32(%rdi)
	vextracti128	$0x1, %ymm7, %xmm9
	vpbroadcastw	4(%rcx), %xmm7
	vpbroadcastw	4(%rdx), %xmm10
	vpmullw	%xmm9, %xmm7, %xmm7
	vpmulhw	%xmm10, %xmm9, %xmm10
	vpmulhw	%xmm8, %xmm7, %xmm7
	vpaddw	%xmm6, %xmm10, %xmm9
	vpsubw	%xmm7, %xmm9, %xmm9
	vpaddw	%xmm6, %xmm7, %xmm7
	vpsubw	%xmm10, %xmm7, %xmm7
	vinserti128	$0x1, %xmm7, %ymm9, %ymm7
	vmovdqu	%ymm7, 64(%rdi)
	vextracti128	$0x1, %ymm6, %xmm7
	vpbroadcastw	6(%rcx), %xmm6
	vpbroadcastw	6(%rdx), %xmm9
	vpmullw	%xmm7, %xmm6, %xmm6
	vpmulhw	%xmm9, %xmm7, %xmm9
	vpmulhw	%xmm8, %xmm6, %xmm6
	vpaddw	%xmm5, %xmm9, %xmm7
	vpsubw	%xmm6, %xmm7, %xmm7
	vpaddw	%xmm5, %xmm6, %xmm6
	vpsubw	%xmm9, %xmm6, %xmm6
	vinserti128	$0x1, %xmm6, %ymm7, %ymm6
	vmovdqu	%ymm6, 96(%rdi)
	vextracti128	$0x1, %ymm5, %xmm6
	vpbroadcastw	8(%rcx), %xmm5
	vpbroadcastw	8(%rdx), %xmm7
	vpmullw	%xmm6, %xmm5, %xmm5
	vpmulhw	%xmm7, %xmm6, %xmm7
	vpmulhw	%xmm8, %xmm5, %xmm5
	vpaddw	%xmm4, %xmm7, %xmm6
	vpsubw	%xmm5, %xmm6, %xmm6
	vpaddw	%xmm4, %xmm5, %xmm5
	vpsubw	%xmm7, %xmm5, %xmm5
	vinserti128	$0x1, %xmm5, %ymm6, %ymm5
	vmovdqu	%ymm5, 128(%rdi)
	vextracti128	$0x1, %ymm4, %xmm5
	vpbroadcastw	10(%rcx), %xmm4
	vpbroadcastw	10(%rdx), %xmm6
	vpmullw	%xmm5, %xmm4, %xmm4
	vpmulhw	%xmm6, %xmm5, %xmm6
	vpmulhw	%xmm8, %xmm4, %xmm4
	vpaddw	%xmm3, %xmm6, %xmm5
	vpsubw	%xmm4, %xmm5, %xmm5
	vpaddw	%xmm3, %xmm4, %xmm4
	vpsubw	%xmm6, %xmm4, %xmm4
	vinserti128	$0x1, %xmm4, %ymm5, %ymm4
	vmovdqu	%ymm4, 160(%rdi)
	vextracti128	$0x1, %ymm3, %xmm4
	vpbroadcastw	12(%rcx), %xmm3
	vpbroadcastw	12(%rdx), %xmm5
	vpmullw	%xmm4, %xmm3, %xmm3
	vpmulhw	%xmm5, %xmm4, %xmm5
	vpmulhw	%xmm8, %xmm3, %xmm3
	vpaddw	%xmm2, %xmm5, %xmm4
	vpsubw	%xmm3, %xmm4, %xmm4
	vpaddw	%xmm2, %xmm3, %xmm3
	vpsubw	%xmm5, %xmm3, %xmm3
	vinserti128	$0x1, %xmm3, %ymm4, %ymm3
	vmovdqu	%ymm3, 192(%rdi)
	vextracti128	$0x1, %ymm2, %xmm3
	vpbroadcastw	14(%rcx), %xmm2
	vpbroadcastw	14(%rdx), %xmm4
	vpmullw	%xmm3, %xmm2, %xmm2
	vpmulhw	%xmm4, %xmm3, %xmm4
	vpmulhw	%xmm8, %xmm2, %xmm2
	vpaddw	%xmm1, %xmm4, %xmm3
	vpsubw	%xmm2, %xmm3, %xmm3
	vpaddw	%xmm1, %xmm2, %xmm2
	vpsubw	%xmm4, %xmm2, %xmm2
	vinserti128	$0x1, %xmm2, %ymm3, %ymm2
	vmovdqu	%ymm2, 224(%rdi)
	vmovdqa	%xmm0, %xmm2
	vextracti128	$0x1, %ymm1, %xmm0
	vpbroadcastw	16(%rcx), %xmm1
	vpbroadcastw	16(%rdx), %xmm3
	vpmullw	%xmm0, %xmm1, %xmm1
	vpmulhw	%xmm3, %xmm0, %xmm3
	vpmulhw	%xmm8, %xmm1, %xmm1
	vpaddw	%xmm2, %xmm3, %xmm0
	vpsubw	%xmm1, %xmm0, %xmm0
	vpaddw	%xmm2, %xmm1, %xmm1
	vpsubw	%xmm3, %xmm1, %xmm1
	vinserti128	$0x1, %xmm1, %ymm0, %ymm0
	vmovdqu	%ymm0, 256(%rdi)
	vzeroupper
	ret
	.cfi_endproc
.LFE7280:
	.size	ntruplus1152_exp001_gt9x16_shear_stage8, .-ntruplus1152_exp001_gt9x16_shear_stage8
	.p2align 4
	.globl	ntruplus1152_exp001_gt9x16_ntt16_finish_row
	.type	ntruplus1152_exp001_gt9x16_ntt16_finish_row, @function
ntruplus1152_exp001_gt9x16_ntt16_finish_row:
.LFB7282:
	.cfi_startproc
	endbr64
	movq	(%rdx), %rax
	movq	8(%rdx), %rcx
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	pushq	%rbx
	.cfi_offset 3, -24
	movq	%rdi, %rbx
	vmovdqu	(%rsi), %ymm2
	movzwl	(%rax), %edi
	movzwl	2(%rax), %esi
	movzwl	2(%rcx), %eax
	movzwl	(%rcx), %ecx
	vpshufd	$68, %ymm2, %ymm5
	vpshufd	$238, %ymm2, %ymm2
	vmovd	%edi, %xmm0
	vmovd	%esi, %xmm1
	vpinsrw	$1, %edi, %xmm0, %xmm3
	vpinsrw	$1, %esi, %xmm1, %xmm0
	vmovd	%eax, %xmm4
	vpunpckldq	%xmm3, %xmm3, %xmm3
	vpunpckldq	%xmm0, %xmm0, %xmm0
	vpunpcklqdq	%xmm0, %xmm0, %xmm0
	vpunpcklqdq	%xmm3, %xmm3, %xmm3
	vinserti128	$0x1, %xmm0, %ymm3, %ymm3
	vmovd	%ecx, %xmm0
	vpinsrw	$1, %ecx, %xmm0, %xmm1
	vpmulhw	%ymm3, %ymm2, %ymm3
	vpunpckldq	%xmm1, %xmm1, %xmm1
	vpunpcklqdq	%xmm1, %xmm1, %xmm0
	vpinsrw	$1, %eax, %xmm4, %xmm1
	movl	$226561409, %eax
	vpunpckldq	%xmm1, %xmm1, %xmm1
	vpunpcklqdq	%xmm1, %xmm1, %xmm1
	vinserti128	$0x1, %xmm1, %ymm0, %ymm0
	vpaddw	%ymm5, %ymm3, %ymm4
	vpmullw	%ymm2, %ymm0, %ymm0
	vmovd	%eax, %xmm2
	movq	16(%rdx), %rax
	vpbroadcastd	%xmm2, %ymm2
	movzwl	2(%rax), %r10d
	movzwl	(%rax), %r11d
	movzwl	6(%rax), %r8d
	movzwl	4(%rax), %r9d
	vmovd	%r10d, %xmm1
	movq	24(%rdx), %rax
	vpmulhw	%ymm2, %ymm0, %ymm0
	vmovd	%r8d, %xmm6
	movzwl	6(%rax), %ecx
	movzwl	4(%rax), %esi
	movzwl	2(%rax), %edi
	movzwl	(%rax), %eax
	vmovd	%ecx, %xmm7
	vpsubw	%ymm0, %ymm4, %ymm4
	vpaddw	%ymm5, %ymm0, %ymm0
	vpsubw	%ymm3, %ymm0, %ymm0
	vpblendd	$204, %ymm0, %ymm4, %ymm4
	vmovd	%r11d, %xmm0
	vpinsrw	$1, %r11d, %xmm0, %xmm3
	vpinsrw	$1, %r10d, %xmm1, %xmm0
	vmovd	%r9d, %xmm1
	vpunpckldq	%xmm0, %xmm0, %xmm0
	vpunpckldq	%xmm3, %xmm3, %xmm3
	vpshufd	$160, %ymm4, %ymm5
	vpunpcklqdq	%xmm0, %xmm3, %xmm3
	vpinsrw	$1, %r9d, %xmm1, %xmm0
	vpinsrw	$1, %r8d, %xmm6, %xmm1
	vpunpckldq	%xmm1, %xmm1, %xmm1
	vpunpckldq	%xmm0, %xmm0, %xmm0
	vpshufd	$245, %ymm4, %ymm4
	vpunpcklqdq	%xmm1, %xmm0, %xmm0
	vinserti128	$0x1, %xmm0, %ymm3, %ymm3
	vmovd	%eax, %xmm0
	vpinsrw	$1, %eax, %xmm0, %xmm1
	vmovd	%edi, %xmm0
	movq	32(%rdx), %rax
	vpinsrw	$1, %edi, %xmm0, %xmm6
	vpmulhw	%ymm3, %ymm4, %ymm3
	vpunpckldq	%xmm1, %xmm1, %xmm0
	vpunpckldq	%xmm6, %xmm6, %xmm6
	vpunpcklqdq	%xmm6, %xmm0, %xmm0
	vmovd	%esi, %xmm6
	vpinsrw	$1, %esi, %xmm6, %xmm1
	vpinsrw	$1, %ecx, %xmm7, %xmm6
	vpunpckldq	%xmm6, %xmm6, %xmm6
	vpunpckldq	%xmm1, %xmm1, %xmm1
	vpunpcklqdq	%xmm6, %xmm1, %xmm1
	vinserti128	$0x1, %xmm1, %ymm0, %ymm0
	vpaddw	%ymm5, %ymm3, %ymm1
	vpmullw	%ymm4, %ymm0, %ymm0
	vpmulhw	%ymm2, %ymm0, %ymm0
	vpsubw	%ymm0, %ymm1, %ymm1
	vpaddw	%ymm5, %ymm0, %ymm0
	vpsubw	%ymm3, %ymm0, %ymm0
	vpblendd	$170, %ymm0, %ymm1, %ymm1
	vmovdqu	(%rax), %xmm0
	movq	40(%rdx), %rax
	vpshufb	.LC3(%rip), %ymm1, %ymm5
	vpshufb	.LC4(%rip), %ymm1, %ymm1
	vmovdqu	(%rax), %xmm4
	vpunpcklwd	%xmm0, %xmm0, %xmm3
	vpunpckhwd	%xmm0, %xmm0, %xmm0
	vinserti128	$0x1, %xmm0, %ymm3, %ymm3
	vpunpcklwd	%xmm4, %xmm4, %xmm0
	vpmulhw	%ymm3, %ymm1, %ymm3
	vpunpckhwd	%xmm4, %xmm4, %xmm4
	vinserti128	$0x1, %xmm4, %ymm0, %ymm0
	vpmullw	%ymm1, %ymm0, %ymm0
	vpaddw	%ymm5, %ymm3, %ymm1
	vpmulhw	%ymm2, %ymm0, %ymm0
	vpsubw	%ymm0, %ymm1, %ymm1
	vpaddw	%ymm5, %ymm0, %ymm0
	vpsubw	%ymm3, %ymm0, %ymm0
	vpblendw	$170, %ymm0, %ymm1, %ymm0
	vmovdqu	%ymm0, (%rbx)
	vzeroupper
	movq	-8(%rbp), %rbx
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE7282:
	.size	ntruplus1152_exp001_gt9x16_ntt16_finish_row, .-ntruplus1152_exp001_gt9x16_ntt16_finish_row
	.section	.rodata.cst32,"aM",@progbits,32
	.align 32
.LC3:
	.byte	0
	.byte	1
	.byte	0
	.byte	1
	.byte	4
	.byte	5
	.byte	4
	.byte	5
	.byte	8
	.byte	9
	.byte	8
	.byte	9
	.byte	12
	.byte	13
	.byte	12
	.byte	13
	.byte	0
	.byte	1
	.byte	0
	.byte	1
	.byte	4
	.byte	5
	.byte	4
	.byte	5
	.byte	8
	.byte	9
	.byte	8
	.byte	9
	.byte	12
	.byte	13
	.byte	12
	.byte	13
	.align 32
.LC4:
	.byte	2
	.byte	3
	.byte	2
	.byte	3
	.byte	6
	.byte	7
	.byte	6
	.byte	7
	.byte	10
	.byte	11
	.byte	10
	.byte	11
	.byte	14
	.byte	15
	.byte	14
	.byte	15
	.byte	2
	.byte	3
	.byte	2
	.byte	3
	.byte	6
	.byte	7
	.byte	6
	.byte	7
	.byte	10
	.byte	11
	.byte	10
	.byte	11
	.byte	14
	.byte	15
	.byte	14
	.byte	15
	.ident	"GCC: (Ubuntu 15.2.0-16ubuntu1) 15.2.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
