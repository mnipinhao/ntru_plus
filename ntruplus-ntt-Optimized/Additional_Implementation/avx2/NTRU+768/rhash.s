.section .rhash_tail,"ax",@progbits
.p2align 4
.globl ntruplus768_hash_g_from_m_avx2
.hidden ntruplus768_hash_g_from_m_avx2
.type ntruplus768_hash_g_from_m_avx2,@function
ntruplus768_hash_g_from_m_avx2:
	endbr64
	pushq %rbp
	pushq %rbx
	subq $0x498, %rsp
	movq %fs:0x28, %rbp
	movq %rbp, 0x488(%rsp)
	movq %rdi, %rbp
	leaq 1(%rsp), %rdi
	movb $1, (%rsp)
	call ntruplus768_pack_m_lazy10788_avx2@PLT
	movl $0x481, %ecx
	movq %rsp, %rdx
	movl $0xc0, %esi
	movq %rbp, %rdi
	call fips202avx_shake256@PLT
	movl $0x481, %edx
	movl $0x481, %esi
	movq %rsp, %rdi
	call __explicit_bzero_chk@PLT
	movq 0x488(%rsp), %rax
	subq %fs:0x28, %rax
	jne .Lrhash_stack_fail
	addq $0x498, %rsp
	popq %rbx
	popq %rbp
	ret
.Lrhash_stack_fail:
	call __stack_chk_fail@PLT
.size ntruplus768_hash_g_from_m_avx2,.-ntruplus768_hash_g_from_m_avx2

.section .note.GNU-stack,"",@progbits
