.text

.macro INV_BFLY low, high
	vpmullw %ymm11, \high, %ymm8
	vpmulhw %ymm12, \high, \high
	vpmulhw %ymm15, %ymm8, %ymm8
	vpsubw %ymm8, \high, \high
	vpaddw \high, \low, %ymm9
	vpsubw \high, \low, \high
	vmovdqa %ymm9, \low
.endm

.macro INV_BFLY2 low0, high0, low1, high1
	vpmullw %ymm11, \high0, %ymm8
	vpmullw %ymm11, \high1, %ymm9
	vpmulhw %ymm12, \high0, \high0
	vpmulhw %ymm12, \high1, \high1
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm8, \high0, \high0
	vpsubw %ymm9, \high1, \high1
	vpaddw \high0, \low0, %ymm8
	vpsubw \high0, \low0, \high0
	vmovdqa %ymm8, \low0
	vpaddw \high1, \low1, %ymm9
	vpsubw \high1, \low1, \high1
	vmovdqa %ymm9, \low1
.endm

.macro INV_ID low, high, tmp
	vpaddw \high, \low, \tmp
	vpsubw \high, \low, \high
	vmovdqa \tmp, \low
.endm

.macro CENTER_ONCE x, tmp
	vpcmpgtw %ymm13, \x, \tmp
	vpand %ymm15, \tmp, \tmp
	vpsubw \tmp, \x, \x
	vpcmpgtw \x, %ymm14, \tmp
	vpand %ymm15, \tmp, \tmp
	vpaddw \tmp, \x, \x
.endm

.macro RUN_INV8 ptr
	vmovdqa   0(\ptr), %ymm0
	vmovdqa  32(\ptr), %ymm1
	vmovdqa  64(\ptr), %ymm2
	vmovdqa  96(\ptr), %ymm3
	vmovdqa 128(\ptr), %ymm4
	vmovdqa 160(\ptr), %ymm5
	vmovdqa 192(\ptr), %ymm6
	vmovdqa 224(\ptr), %ymm7
	/* length 4 */
	INV_ID %ymm0, %ymm2, %ymm8
	INV_ID %ymm4, %ymm6, %ymm8
	vpbroadcastw 2(%r8), %ymm12
	vpbroadcastw 2(%r9), %ymm11
	INV_BFLY2 %ymm1, %ymm3, %ymm5, %ymm7
	/* length 8 */
	INV_ID %ymm0, %ymm4, %ymm8
	vpbroadcastw 6(%r8), %ymm12
	vpbroadcastw 6(%r9), %ymm11
	INV_BFLY %ymm1, %ymm5
	vpbroadcastw 8(%r8), %ymm12
	vpbroadcastw 8(%r9), %ymm11
	INV_BFLY %ymm2, %ymm6
	vpbroadcastw 10(%r8), %ymm12
	vpbroadcastw 10(%r9), %ymm11
	INV_BFLY %ymm3, %ymm7
	CENTER_ONCE %ymm0, %ymm10
	CENTER_ONCE %ymm1, %ymm10
	CENTER_ONCE %ymm2, %ymm10
	CENTER_ONCE %ymm3, %ymm10
	CENTER_ONCE %ymm4, %ymm10
	CENTER_ONCE %ymm5, %ymm10
	CENTER_ONCE %ymm6, %ymm10
	CENTER_ONCE %ymm7, %ymm10
	vmovdqa %ymm0,   0(\ptr)
	vmovdqa %ymm1,  32(\ptr)
	vmovdqa %ymm2,  64(\ptr)
	vmovdqa %ymm3,  96(\ptr)
	vmovdqa %ymm4, 128(\ptr)
	vmovdqa %ymm5, 160(\ptr)
	vmovdqa %ymm6, 192(\ptr)
	vmovdqa %ymm7, 224(\ptr)
.endm

.p2align 5
.globl round4c_inverse_ntt16_layers_asm
.type round4c_inverse_ntt16_layers_asm,@function
round4c_inverse_ntt16_layers_asm:
	movq round4c_inv16_twiddle_mont_asm(%rip), %r8
	movq round4c_inv16_twiddle_qinv_asm(%rip), %r9
	vpbroadcastw .Linv_q(%rip), %ymm15
	vpbroadcastw .Linv_center(%rip), %ymm13
	vpbroadcastw .Linv_negative_center(%rip), %ymm14
	movq %rdi, %rsi
	movl $6, %ecx
.Linv8_loop:
	RUN_INV8 %rsi
	addq $256, %rsi
	decl %ecx
	jnz .Linv8_loop

	/* The current ABI needs one memory boundary here: a row owns 16 YMM. */
	movq %rdi, %rsi
	movl $3, %r10d
.Linv16_row:
	movq %rsi, %rcx
	leaq 256(%rsi), %rdx
	leaq 12(%r8), %rax
	leaq 12(%r9), %r11
	xorl %edi, %edi
.Linv16_pair:
	vmovdqa (%rcx), %ymm0
	vmovdqa (%rdx), %ymm1
	testl %edi, %edi
	jz .Linv16_identity
	vpbroadcastw (%rax,%rdi,2), %ymm12
	vpbroadcastw (%r11,%rdi,2), %ymm11
	INV_BFLY %ymm0, %ymm1
	jmp .Linv16_store
.Linv16_identity:
	INV_ID %ymm0, %ymm1, %ymm8
.Linv16_store:
	vmovdqa %ymm0, (%rcx)
	vmovdqa %ymm1, (%rdx)
	addq $32, %rcx
	addq $32, %rdx
	incl %edi
	cmpl $8, %edi
	jne .Linv16_pair
	addq $512, %rsi
	decl %r10d
	jnz .Linv16_row
	vzeroupper
	ret
.size round4c_inverse_ntt16_layers_asm,.-round4c_inverse_ntt16_layers_asm

.section .rodata
.p2align 5
.Linv_q: .short 3457
.Linv_center: .short 1728
.Linv_negative_center: .short -1728

.section .note.GNU-stack,"",@progbits
