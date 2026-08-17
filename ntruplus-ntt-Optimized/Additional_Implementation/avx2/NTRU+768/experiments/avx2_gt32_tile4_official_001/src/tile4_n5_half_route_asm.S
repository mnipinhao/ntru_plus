/* Priority-2 bounded route: current N5 TILE4 output -> N32 half-native ABI. */

	.text
	.p2align 5
	.globl gt32_tile4_n5_to_n32_half_asm
	.type gt32_tile4_n5_to_n32_half_asm,@function
gt32_tile4_n5_to_n32_half_asm:
	/*
	 * N5 vectors are (k3,branch,group).  The half-native destination is
	 * (branch,group,slot), with slot 1/2 reflecting k3=1/2 in the high half.
	 * The N5 DAG completes one eight-vector (k3,branch) tile at a time, so the
	 * three source tiles cannot coexist in the 16-register AVX2 file.  This
	 * bounded control measures the irreducible materialized terminal route.
	 */
	xorl %eax, %eax
.Ln5_half_branch_loop:
	/* Source bases for k3=0,1,2 at this branch. */
	movq %rax, %r8
	shlq $8, %r8
	leaq (%rsi,%r8), %r9
	leaq 512(%r9), %r10
	leaq 1024(%r9), %r11

	/* Destination branch stride is 24 YMM = 768 bytes. */
	movq %rax, %r8
	imulq $768, %r8, %r8
	leaq (%rdi,%r8), %rdx
	movl $8, %ecx
	.p2align 5
.Ln5_half_group_loop:
	vmovdqu (%r9), %ymm0
	vmovdqu (%r10), %ymm1
	vmovdqu (%r11), %ymm2
	vmovdqu %ymm0, 0(%rdx)
	vperm2i128 $0x30, %ymm2, %ymm1, %ymm3
	vperm2i128 $0x30, %ymm1, %ymm2, %ymm4
	vmovdqu %ymm3, 32(%rdx)
	vmovdqu %ymm4, 64(%rdx)
	addq $32, %r9
	addq $32, %r10
	addq $32, %r11
	addq $96, %rdx
	decl %ecx
	jne .Ln5_half_group_loop
	incq %rax
	cmpq $2, %rax
	jne .Ln5_half_branch_loop
	vzeroupper
	ret
	.size gt32_tile4_n5_to_n32_half_asm,.-gt32_tile4_n5_to_n32_half_asm

	.section .note.GNU-stack,"",@progbits
