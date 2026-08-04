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

.macro RUN_GROUP stride, count, low, high, twiddle, correct
	.if \twiddle >= 0
	vpbroadcastw .Lfwd16_mont+2*\twiddle(%rip), %ymm12
	vpbroadcastw .Lfwd16_qinv+2*\twiddle(%rip), %ymm11
	.endif
	movq %rdi, %rax
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

.p2align 5
.globl round4c_forward_ntt16_asm
.type round4c_forward_ntt16_asm,@function
round4c_forward_ntt16_asm:
	vpbroadcastw .Lq(%rip), %ymm15
	vpbroadcastw .Lcenter(%rip), %ymm14
	vpbroadcastw .Lnegative_center(%rip), %ymm13

	/* length 2, offset 0, identity twiddle */
	RUN_GROUP2 64, 12, 0, 32, -1, 1

	/* length 4, offset 1: [1, omega^4] */
	RUN_GROUP2 128, 6, 0, 64, -1, 0
	RUN_GROUP2 128, 6, 32, 96, 2, 0

	/* length 8, offset 3: [1, omega^2, omega^4, omega^6] */
	RUN_GROUP2 256, 3, 0, 128, -1, 1
	RUN_GROUP2 256, 3, 32, 160, 4, 1
	RUN_GROUP2 256, 3, 64, 192, 5, 1
	RUN_GROUP2 256, 3, 96, 224, 6, 1

	/* length 16, offset 7: [1, omega, ..., omega^7] */
	RUN_GROUP 512, 3, 0, 256, -1, 0
	RUN_GROUP 512, 3, 32, 288, 8, 0
	RUN_GROUP 512, 3, 64, 320, 9, 0
	RUN_GROUP 512, 3, 96, 352, 10, 0
	RUN_GROUP 512, 3, 128, 384, 11, 0
	RUN_GROUP 512, 3, 160, 416, 12, 0
	RUN_GROUP 512, 3, 192, 448, 13, 0
	RUN_GROUP 512, 3, 224, 480, 14, 0

	vzeroupper
	ret
.size round4c_forward_ntt16_asm,.-round4c_forward_ntt16_asm

.section .rodata
#include "../generated/forward-ntt16-constants.inc"

.section .note.GNU-stack,"",@progbits
