#define CAGE_BYTES 768

.text

.macro REDUCE32 value, tmp, mq
    vpmullw %ymm13, %ymm\value, %ymm\tmp
    vpand %ymm14, %ymm\tmp, %ymm\tmp
    vpmaddwd %ymm15, %ymm\tmp, %ymm\mq
    vpsubd %ymm\mq, %ymm\value, %ymm\value
    vpsrad $16, %ymm\value, %ymm\value
.endm

.macro FUNCTION_BEGIN name
    .p2align 6
    .globl \name
    .type \name,@function
\name:
.Lstart_\name:
    vmovdqa .Lq(%rip), %ymm12
    vmovdqa .Lqinv(%rip), %ymm13
    vmovdqa .Llowmask(%rip), %ymm14
    vmovdqa .Lqpair(%rip), %ymm15
    mov $48, %r9d
.endm

.macro FUNCTION_END name
    vzeroupper
    ret
    .fill CAGE_BYTES-(.-.Lstart_\name),1,0x90
    .size \name,.-\name
.endm

.macro CONTROL_FUNCTION name
    FUNCTION_BEGIN \name
.Lloop_control_\name:
    vmovdqu (%rsi), %ymm0
    vmovdqu (%rdx), %ymm1
    vpmullw (%r8), %ymm1, %ymm2
    vpmulhw (%rcx), %ymm1, %ymm3
    vpmulhw %ymm12, %ymm2, %ymm2
    vpsubw %ymm2, %ymm3, %ymm3
    vpshufb .Lswap(%rip), %ymm1, %ymm4
    vpmaddwd %ymm3, %ymm0, %ymm5
    vpmaddwd %ymm4, %ymm0, %ymm6
    REDUCE32 5,7,8
    REDUCE32 6,7,8
    vpackssdw %ymm6, %ymm5, %ymm5
    vpshufb .Linterleave(%rip), %ymm5, %ymm5
    vmovdqu %ymm5, (%rdi)
    add $32, %rdi
    add $32, %rsi
    add $32, %rdx
    add $32, %rcx
    add $32, %r8
    dec %r9d
    jnz .Lloop_control_\name
    FUNCTION_END \name
.endm

.macro ATOMIC_FUNCTION name
    FUNCTION_BEGIN \name
.Lloop_atomic_\name:
    vmovdqu (%rsi), %ymm0
    vmovdqu (%rdx), %ymm1
    vpmullw (%r8), %ymm1, %ymm2
    vpmulhw (%rcx), %ymm1, %ymm3
    vpmulhw %ymm12, %ymm2, %ymm2
    vpsubw %ymm2, %ymm3, %ymm3
    vpshufb .Lswap(%rip), %ymm1, %ymm4

    /* Four factors per packet.  Low selects factors 0,1,4,5; high
       selects 2,3,6,7.  Each A pair is duplicated so adjacent madd
       dwords become c0,c1 for the same factor. */
    vpshufb .Ldup_lo(%rip), %ymm0, %ymm9
    vpshufb .Ldup_hi(%rip), %ymm0, %ymm10
    vpunpckldq %ymm4, %ymm3, %ymm7
    vpunpckhdq %ymm4, %ymm3, %ymm8
    vpmaddwd %ymm7, %ymm9, %ymm5
    vpmaddwd %ymm8, %ymm10, %ymm6
    REDUCE32 5,7,8
    REDUCE32 6,7,8
    /* Lane-local pack already restores factor order; unlike control,
       no final interleave shuffle is required. */
    vpackssdw %ymm6, %ymm5, %ymm5
    vmovdqu %ymm5, (%rdi)
    add $32, %rdi
    add $32, %rsi
    add $32, %rdx
    add $32, %rcx
    add $32, %r8
    dec %r9d
    jnz .Lloop_atomic_\name
    FUNCTION_END \name
.endm

#ifdef REVERSED
ATOMIC_FUNCTION qbm_atomic_expanded_asm
CONTROL_FUNCTION qbm_selected_control_asm
#else
CONTROL_FUNCTION qbm_selected_control_asm
ATOMIC_FUNCTION qbm_atomic_expanded_asm
#endif

.section .rodata
.p2align 5
.Lq:
    .rept 16
    .short 3457
    .endr
.Lqinv:
    .rept 16
    .short 12929
    .endr
.Llowmask:
    .rept 8
    .long 0x0000ffff
    .endr
.Lqpair:
    .rept 8
    .long 3457
    .endr
.Lswap:
    .byte 2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13
    .byte 2,3,0,1,6,7,4,5,10,11,8,9,14,15,12,13
.Linterleave:
    .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
    .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
.Ldup_lo:
    .byte 0,1,2,3,0,1,2,3,4,5,6,7,4,5,6,7
    .byte 0,1,2,3,0,1,2,3,4,5,6,7,4,5,6,7
.Ldup_hi:
    .byte 8,9,10,11,8,9,10,11,12,13,14,15,12,13,14,15
    .byte 8,9,10,11,8,9,10,11,12,13,14,15,12,13,14,15

.section .note.GNU-stack,"",@progbits
