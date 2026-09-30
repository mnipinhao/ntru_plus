/*
 * x86-64 SysV ABI probe for test/test_abi.c.
 *
 * uint64_t abi_probe(struct abi_call *c): calls c->fn(c->a0, c->a1, c->a2) with
 * a sentinel in every callee-saved register (rbx, rbp, r12-r15) and the stack
 * pointer 32-byte aligned (c->misalign = 0) or 16 mod 32 (c->misalign = 16),
 * both SysV-legal.  The upper YMM state is cleaned before the call so that the
 * XINUSE sample taken right after it describes the callee alone.  It records,
 * without running any other code in between: the six registers, whether rsp
 * came back unchanged, MXCSR and the x87 control word before and after,
 * RFLAGS.DF, and (if c->have_xinuse) XGETBV(1), whose bit 2 is set while the
 * upper halves of the YMM registers are in use.
 */
        .text
        .global abi_probe
        .type   abi_probe,@function
abi_probe:
        pushq   %rbx
        pushq   %rbp
        pushq   %r12
        pushq   %r13
        pushq   %r14
        pushq   %r15
        movq    %rdi, abi_ctx(%rip)
        movq    %rsp, abi_saved_rsp(%rip)
        stmxcsr 80(%rdi)
        fnstcw  88(%rdi)
        andq    $-32, %rsp
        subq    32(%rdi), %rsp
        movq    %rsp, abi_expected_rsp(%rip)
        movq    (%rdi), %r11
        movq    16(%rdi), %rsi
        movq    24(%rdi), %rdx
        movq    8(%rdi), %rdi
        movabsq $0x1111111111111111, %rbx
        movabsq $0x2222222222222222, %rbp
        movabsq $0x3333333333333333, %r12
        movabsq $0x4444444444444444, %r13
        movabsq $0x5555555555555555, %r14
        movabsq $0x6666666666666666, %r15
        vzeroupper
        call    *%r11
        movq    %rbx, abi_rbx(%rip)
        movq    abi_ctx(%rip), %rbx
        movq    %rax, 40(%rbx)
        cmpl    $0, 48(%rbx)
        je      1f
        movl    $1, %ecx
        xgetbv
        movl    %eax, 56(%rbx)
1:
        movq    %rbp, 64(%rbx)
        pushfq
        popq    %rax
        movq    %rax, 72(%rbx)
        stmxcsr 84(%rbx)
        fnstcw  90(%rbx)
        movq    %r12, 96(%rbx)
        movq    %r13, 104(%rbx)
        movq    %r14, 112(%rbx)
        movq    %r15, 120(%rbx)
        movq    abi_rbx(%rip), %rax
        movq    %rax, 128(%rbx)
        xorl    %eax, %eax
        cmpq    abi_expected_rsp(%rip), %rsp
        setne   %al
        movq    %rax, 136(%rbx)
        movq    abi_saved_rsp(%rip), %rsp
        popq    %r15
        popq    %r14
        popq    %r13
        popq    %r12
        popq    %rbp
        popq    %rbx
        vzeroupper
        ret
        .size   abi_probe,.-abi_probe

        .bss
        .p2align 3
abi_ctx:          .zero 8
abi_saved_rsp:    .zero 8
abi_expected_rsp: .zero 8
abi_rbx:          .zero 8

.ifndef no_gnu_stack
        .section .note.GNU-stack,"",@progbits
.endif
