
/* ---- selected production component ---- */
 .text
 .macro TILE4_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
 vpunpcklwd %\s1, %\s0, %\t0
 vpunpckhwd %\s1, %\s0, %\t1
 vpunpcklwd %\s3, %\s2, %\t2
 vpunpckhwd %\s3, %\s2, %\t3
 vpunpckldq %\t2, %\t0, %\s0
 vpunpckhdq %\t2, %\t0, %\s1
 vpunpckldq %\t3, %\t1, %\s2
 vpunpckhdq %\t3, %\t1, %\s3
 vpunpcklqdq %\s2, %\s0, %\t0
 vpunpckhqdq %\s2, %\s0, %\t1
 vpunpcklqdq %\s3, %\s1, %\t2
 vpunpckhqdq %\s3, %\s1, %\t3
 .endm
 .macro TILE4_MONT_FIRST a,aq,b
 vpmullw %\aq, %\b, %ymm13
 vpmulhw %\a, %\b, %ymm15
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm15, %ymm15
 .endm
 .macro TILE4_MONT_ADD a,aq,b
 vpmullw %\aq, %\b, %ymm13
 vpmulhw %\a, %\b, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm14
 vpaddw %ymm14, %ymm15, %ymm15
 .endm
 .macro TILE4_MONT_TO_HOIST dst,a,aq,b,tmp
 vpmullw %\aq, %\b, %\tmp
 vpmulhw %\a, %\b, %\dst
 vpmulhw %ymm0, %\tmp, %\tmp
 vpsubw %\tmp, %\dst, %\dst
 .endm
 .macro TILE4_MONT_ADD_HOIST acc,a,aq,b,lo,hi
 vpmullw %\aq, %\b, %\lo
 vpmulhw %\a, %\b, %\hi
 vpmulhw %ymm0, %\lo, %\lo
 vpsubw %\lo, %\hi, %\hi
 vpaddw %\hi, %\acc, %\acc
 .endm
 .macro TILE4_MONT_TO_DEMAND dst,a,b,tmp
 vpmullw .Ltile4_bm_qinv(%rip), %\a, %\tmp
 vpmulhw %\a, %\b, %\dst
 vpmullw %\b, %\tmp, %\tmp
 vpmulhw %ymm0, %\tmp, %\tmp
 vpsubw %\tmp, %\dst, %\dst
 .endm
 .macro TILE4_MONT_ADD_DEMAND acc,a,b,lo,hi
 vpmullw .Ltile4_bm_qinv(%rip), %\a, %\lo
 vpmullw %\b, %\lo, %\lo
 vpmulhw %\a, %\b, %\hi
 vpmulhw %ymm0, %\lo, %\lo
 vpsubw %\lo, %\hi, %\hi
 vpaddw %\hi, %\acc, %\acc
 .endm
 .macro TILE4_MONT_RAW_TO dst,a,b,lo
 vpmullw %\a, %\b, %\lo
 vpmullw .Ltile4_bm_qinv(%rip), %\lo, %\lo
 vpmulhw %\a, %\b, %\dst
 vpmulhw %ymm0, %\lo, %\lo
 vpsubw %\lo, %\dst, %\dst
 .endm
 .macro TILE4_MONT_LAMBDA
 vpmullw (%r9), %ymm15, %ymm13
 vpmulhw (%r8), %ymm15, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm15
 .endm
 .macro TILE4_BASEMUL_K2_FUNCTION name
 .p2align 5
 .globl \name
 .type \name,@function
\name:
 leaq .Ltile4_bm_lambda(%rip), %r8
 leaq .Ltile4_bm_lambda_qinv(%rip), %r9
 vmovdqa .Ltile4_bm_q(%rip), %ymm0
 movl $12, %ecx
 .p2align 5
.Ltile4_bm_k2_loop\@:
 vmovdqu 0(%rdx), %ymm1
 vmovdqu 32(%rdx), %ymm2
 vmovdqu 64(%rdx), %ymm3
 vmovdqu 96(%rdx), %ymm4
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
 vmovdqu 0(%rsi), %ymm5
 vmovdqu 32(%rsi), %ymm6
 vmovdqu 64(%rsi), %ymm7
 vmovdqu 96(%rsi), %ymm8
 TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 TILE4_MONT_RAW_TO ymm5,ymm1,ymm9,ymm13
 vmovdqu %ymm5, 0(%rdi)
 TILE4_MONT_RAW_TO ymm5,ymm2,ymm10,ymm13
 vmovdqu %ymm5, 32(%rdi)
 TILE4_MONT_RAW_TO ymm5,ymm3,ymm11,ymm13
 vmovdqu %ymm5, 64(%rdi)
 TILE4_MONT_RAW_TO ymm5,ymm4,ymm12,ymm13
 vmovdqu %ymm5, 96(%rdi)
 vpaddw %ymm3, %ymm1, %ymm5
 vpaddw %ymm11, %ymm9, %ymm6
 TILE4_MONT_RAW_TO ymm7,ymm5,ymm6,ymm8
 vpsubw 0(%rdi), %ymm7, %ymm7
 vpsubw 64(%rdi), %ymm7, %ymm7
 vpaddw %ymm4, %ymm2, %ymm5
 vpaddw %ymm12, %ymm10, %ymm6
 TILE4_MONT_RAW_TO ymm8,ymm5,ymm6,ymm13
 vpsubw 32(%rdi), %ymm8, %ymm8
 vpsubw 96(%rdi), %ymm8, %ymm8
 vmovdqu 64(%rdi), %ymm15
 vpaddw %ymm8, %ymm15, %ymm15
 TILE4_MONT_LAMBDA
 vpaddw 0(%rdi), %ymm15, %ymm15
 vmovdqu %ymm15, 0(%rdi)
 vmovdqu 96(%rdi), %ymm15
 TILE4_MONT_LAMBDA
 vpaddw 32(%rdi), %ymm15, %ymm15
 vpaddw %ymm7, %ymm15, %ymm15
 vmovdqu %ymm15, 64(%rdi)
 TILE4_MONT_RAW_TO ymm5,ymm1,ymm9,ymm13
 vmovdqu %ymm5, 32(%rdi)
 TILE4_MONT_RAW_TO ymm6,ymm2,ymm10,ymm13
 vmovdqu %ymm6, 96(%rdi)
 vpaddw %ymm2, %ymm1, %ymm7
 vpaddw %ymm10, %ymm9, %ymm8
 TILE4_MONT_RAW_TO ymm15,ymm7,ymm8,ymm13
 vpsubw 32(%rdi), %ymm15, %ymm15
 vpsubw 96(%rdi), %ymm15, %ymm15
 vmovdqa %ymm15, %ymm5
 TILE4_MONT_RAW_TO ymm6,ymm3,ymm11,ymm13
 vmovdqu %ymm6, 32(%rdi)
 TILE4_MONT_RAW_TO ymm7,ymm4,ymm12,ymm13
 vmovdqu %ymm7, 96(%rdi)
 vpaddw %ymm4, %ymm3, %ymm8
 vpaddw %ymm12, %ymm11, %ymm14
 TILE4_MONT_RAW_TO ymm15,ymm8,ymm14,ymm13
 vpsubw 32(%rdi), %ymm15, %ymm15
 vpsubw 96(%rdi), %ymm15, %ymm15
 vmovdqa %ymm15, %ymm6
 vpaddw %ymm3, %ymm1, %ymm7
 vpaddw %ymm4, %ymm2, %ymm8
 vpaddw %ymm11, %ymm9, %ymm13
 vpaddw %ymm12, %ymm10, %ymm14
 TILE4_MONT_RAW_TO ymm15,ymm7,ymm13,ymm1
 vmovdqu %ymm15, 32(%rdi)
 TILE4_MONT_RAW_TO ymm15,ymm8,ymm14,ymm1
 vmovdqu %ymm15, 96(%rdi)
 vpaddw %ymm8, %ymm7, %ymm2
 vpaddw %ymm14, %ymm13, %ymm3
 TILE4_MONT_RAW_TO ymm15,ymm2,ymm3,ymm1
 vpsubw 32(%rdi), %ymm15, %ymm15
 vpsubw 96(%rdi), %ymm15, %ymm15
 vpsubw %ymm5, %ymm15, %ymm15
 vpsubw %ymm6, %ymm15, %ymm15
 vmovdqu %ymm15, 96(%rdi)
 vmovdqa %ymm6, %ymm15
 TILE4_MONT_LAMBDA
 vpaddw %ymm5, %ymm15, %ymm15
 vmovdqu %ymm15, 32(%rdi)
 vmovdqu 96(%rdi), %ymm15
 TILE4_OUTPUT_AOS_LATE_CENTER
 addq $128, %rsi
 addq $128, %rdx
 addq $128, %rdi
 addq $32, %r8
 addq $32, %r9
 decl %ecx
 jne .Ltile4_bm_k2_loop\@
 vzeroupper
 ret
 .size \name,.-\name
 .endm
 .macro TILE4_BASEMUL_B4B_FUNCTION name
 .p2align 5
 .globl \name
 .type \name,@function
\name:
 leaq .Ltile4_bm_lambda(%rip), %r8
 leaq .Ltile4_bm_lambda_qinv(%rip), %r9
 vmovdqa .Ltile4_bm_q(%rip), %ymm0
 movl $12, %ecx
 .p2align 5
.Ltile4_bm_b4b_loop\@:
 vmovdqu 0(%rdx), %ymm1
 vmovdqu 32(%rdx), %ymm2
 vmovdqu 64(%rdx), %ymm3
 vmovdqu 96(%rdx), %ymm4
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
 vmovdqu 0(%rsi), %ymm5
 vmovdqu 32(%rsi), %ymm6
 vmovdqu 64(%rsi), %ymm7
 vmovdqu 96(%rsi), %ymm8
 TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 TILE4_MONT_TO_HOIST ymm7,ymm2,ymm6,ymm12,ymm14
 TILE4_MONT_TO_DEMAND ymm8,ymm3,ymm12,ymm14
 TILE4_MONT_TO_DEMAND ymm13,ymm4,ymm12,ymm14
 TILE4_MONT_ADD_DEMAND ymm7,ymm3,ymm11,ymm14,ymm15
 TILE4_MONT_ADD_DEMAND ymm8,ymm4,ymm11,ymm14,ymm15
 TILE4_MONT_ADD_DEMAND ymm7,ymm4,ymm10,ymm14,ymm15
 vpmullw (%r9), %ymm7, %ymm14
 vpmullw (%r9), %ymm8, %ymm15
 vpmullw (%r9), %ymm13, %ymm5
 vpmulhw (%r8), %ymm7, %ymm7
 vpmulhw (%r8), %ymm8, %ymm8
 vpmulhw (%r8), %ymm13, %ymm13
 vpmulhw %ymm0, %ymm14, %ymm14
 vpmulhw %ymm0, %ymm15, %ymm15
 vpmulhw %ymm0, %ymm5, %ymm5
 vpsubw %ymm14, %ymm7, %ymm7
 vpsubw %ymm15, %ymm8, %ymm8
 vpsubw %ymm5, %ymm13, %ymm13
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 TILE4_MONT_ADD_HOIST ymm7,ymm1,ymm5,ymm9,ymm14,ymm15
 TILE4_MONT_ADD_HOIST ymm8,ymm1,ymm5,ymm10,ymm14,ymm15
 TILE4_MONT_ADD_HOIST ymm8,ymm2,ymm6,ymm9,ymm14,ymm15
 TILE4_MONT_ADD_HOIST ymm13,ymm1,ymm5,ymm11,ymm14,ymm15
 TILE4_MONT_ADD_HOIST ymm13,ymm2,ymm6,ymm10,ymm14,ymm15
 TILE4_MONT_ADD_DEMAND ymm13,ymm3,ymm9,ymm14,ymm15
 TILE4_MONT_TO_HOIST ymm5,ymm1,ymm5,ymm12,ymm14
 TILE4_MONT_ADD_HOIST ymm5,ymm2,ymm6,ymm11,ymm14,ymm15
 TILE4_MONT_ADD_DEMAND ymm5,ymm3,ymm10,ymm14,ymm15
 TILE4_MONT_ADD_DEMAND ymm5,ymm4,ymm9,ymm14,ymm15
 vmovdqu %ymm7, 0(%rdi)
 vmovdqu %ymm8, 32(%rdi)
 vmovdqu %ymm13, 64(%rdi)
 vmovdqa %ymm5, %ymm15
 TILE4_OUTPUT_AOS_LATE_CENTER
 addq $128, %rsi
 addq $128, %rdx
 addq $128, %rdi
 addq $32, %r8
 addq $32, %r9
 decl %ecx
 jne .Ltile4_bm_b4b_loop\@
 vzeroupper
 ret
 .size \name,.-\name
 .endm
 .macro TILE4_CENTER_RMINUS1
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm15, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm15, %ymm15
 .endm
 .macro TILE4_NO_FINALIZER
 .endm
 .macro TILE4_MONT_RSQ
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm15, %ymm13
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm15, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm15
 .endm
 .macro TILE4_OUTPUT_AOS
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 vmovdqu 96(%rdi), %ymm4
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_AOS_LATE_CENTER
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm5, %ymm1
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm6, %ymm2
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm7, %ymm3
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm8, %ymm4
 vpmullw %ymm0, %ymm1, %ymm1
 vpmullw %ymm0, %ymm2, %ymm2
 vpmullw %ymm0, %ymm3, %ymm3
 vpmullw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_AOS_LATE_C3CENTER
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm15, %ymm14
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm15, %ymm15
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_AOS_LATE_RSQ
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm5, %ymm5
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm6, %ymm6
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm7, %ymm7
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_SOA_LATE_RSQ
 vmovdqu 0(%rdi), %ymm5
 vmovdqu 32(%rdi), %ymm6
 vmovdqu 64(%rdi), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm5, %ymm5
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm6, %ymm6
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm7, %ymm7
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_SOA_LATE_RSQ_PRELOAD_B
 vmovdqu 0(%rdi), %ymm5
 vmovdqu 32(%rdi), %ymm6
 vmovdqu 64(%rdi), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm5, %ymm5
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm6, %ymm6
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm7, %ymm7
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm8, %ymm8
 vmovdqu 128(%rdx), %ymm9
 vmovdqu 160(%rdx), %ymm10
 vmovdqu 192(%rdx), %ymm11
 vmovdqu 224(%rdx), %ymm12
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_SOA_LATE_RSQ_ADD_M
 vmovdqu 0(%rdi), %ymm5
 vmovdqu 32(%rdi), %ymm6
 vmovdqu 64(%rdi), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm5, %ymm5
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm6, %ymm6
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm7, %ymm7
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpaddw 0(%r10), %ymm5, %ymm5
 vpaddw 32(%r10), %ymm6, %ymm6
 vpaddw 64(%r10), %ymm7, %ymm7
 vpaddw 96(%r10), %ymm8, %ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_AOS_LATE_RAW
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
 vmovdqu %ymm5, 0(%rdi)
 vmovdqu %ymm6, 32(%rdi)
 vmovdqu %ymm7, 64(%rdi)
 vmovdqu %ymm8, 96(%rdi)
 .endm
 .macro TILE4_OUTPUT_SOA_PRIVATE
 .endm
 .macro TILE4_OUTPUT_SOA_LATE_C3CENTER
 vpmulhrsw .Ltile4_bm_center10(%rip), %ymm15, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm15, %ymm15
 vmovdqu %ymm15, 96(%rdi)
 .endm
 .macro TILE4_INPUT_A_AOS
 vmovdqu 0(%rsi), %ymm5
 vmovdqu 32(%rsi), %ymm6
 vmovdqu 64(%rsi), %ymm7
 vmovdqu 96(%rsi), %ymm8
 TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 .endm
 .macro TILE4_INPUT_A_SOA
 vmovdqu 0(%rsi), %ymm1
 vmovdqu 32(%rsi), %ymm2
 vmovdqu 64(%rsi), %ymm3
 vmovdqu 96(%rsi), %ymm4
 .endm
 .macro TILE4_INPUT_B_AOS
 vmovdqu 0(%rdx), %ymm1
 vmovdqu 32(%rdx), %ymm2
 vmovdqu 64(%rdx), %ymm3
 vmovdqu 96(%rdx), %ymm4
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
 .endm
 .macro TILE4_INPUT_B_SOA
 vmovdqu 0(%rdx), %ymm9
 vmovdqu 32(%rdx), %ymm10
 vmovdqu 64(%rdx), %ymm11
 vmovdqu 96(%rdx), %ymm12
 .endm
 .macro TILE4_INPUT_A_L1
 vmovdqu 0(%rsi), %ymm1
 vmovdqu 32(%rsi), %ymm2
 vmovdqu 64(%rsi), %ymm3
 vmovdqu 96(%rsi), %ymm4
 vpunpckldq %ymm3, %ymm1, %ymm5
 vpunpckhdq %ymm3, %ymm1, %ymm6
 vpunpckldq %ymm4, %ymm2, %ymm7
 vpunpckhdq %ymm4, %ymm2, %ymm8
 vpunpcklqdq %ymm7, %ymm5, %ymm1
 vpunpckhqdq %ymm7, %ymm5, %ymm2
 vpunpcklqdq %ymm8, %ymm6, %ymm3
 vpunpckhqdq %ymm8, %ymm6, %ymm4
 .endm
 .macro TILE4_INPUT_B_L1
 vmovdqu 0(%rdx), %ymm9
 vmovdqu 32(%rdx), %ymm10
 vmovdqu 64(%rdx), %ymm11
 vmovdqu 96(%rdx), %ymm12
 vpunpckldq %ymm11, %ymm9, %ymm1
 vpunpckhdq %ymm11, %ymm9, %ymm2
 vpunpckldq %ymm12, %ymm10, %ymm3
 vpunpckhdq %ymm12, %ymm10, %ymm4
 vpunpcklqdq %ymm3, %ymm1, %ymm9
 vpunpckhqdq %ymm3, %ymm1, %ymm10
 vpunpcklqdq %ymm4, %ymm2, %ymm11
 vpunpckhqdq %ymm4, %ymm2, %ymm12
 .endm
 .macro TILE4_INPUT_A_L2
 vmovdqu 0(%rsi), %ymm5
 vmovdqu 32(%rsi), %ymm6
 vmovdqu 64(%rsi), %ymm7
 vmovdqu 96(%rsi), %ymm8
 vpunpcklqdq %ymm7, %ymm5, %ymm1
 vpunpckhqdq %ymm7, %ymm5, %ymm2
 vpunpcklqdq %ymm8, %ymm6, %ymm3
 vpunpckhqdq %ymm8, %ymm6, %ymm4
 .endm
 .macro TILE4_INPUT_B_L2
 vmovdqu 0(%rdx), %ymm1
 vmovdqu 32(%rdx), %ymm2
 vmovdqu 64(%rdx), %ymm3
 vmovdqu 96(%rdx), %ymm4
 vpunpcklqdq %ymm3, %ymm1, %ymm9
 vpunpckhqdq %ymm3, %ymm1, %ymm10
 vpunpcklqdq %ymm4, %ymm2, %ymm11
 vpunpckhqdq %ymm4, %ymm2, %ymm12
 .endm
 .macro TILE4_BASEMUL_B3_FUNCTION name,output,inputa,inputb
 .p2align 5
 .globl \name
 .type \name,@function
\name:
 leaq .Ltile4_bm_lambda(%rip), %r8
 leaq .Ltile4_bm_lambda_qinv(%rip), %r9
 vmovdqa .Ltile4_bm_q(%rip), %ymm0
 movl $12, %ecx
 .p2align 5
.Ltile4_bm_b3_loop\@:
 \inputb
 \inputa
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8
 TILE4_MONT_FIRST ymm2,ymm6,ymm12
 TILE4_MONT_ADD ymm3,ymm7,ymm11
 TILE4_MONT_ADD ymm4,ymm8,ymm10
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rdi)
 TILE4_MONT_FIRST ymm3,ymm7,ymm12
 TILE4_MONT_ADD ymm4,ymm8,ymm11
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm10
 TILE4_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rdi)
 TILE4_MONT_FIRST ymm4,ymm8,ymm12
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm11
 TILE4_MONT_ADD ymm2,ymm6,ymm10
 TILE4_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rdi)
 TILE4_MONT_FIRST ymm1,ymm5,ymm12
 TILE4_MONT_ADD ymm2,ymm6,ymm11
 TILE4_MONT_ADD ymm3,ymm7,ymm10
 TILE4_MONT_ADD ymm4,ymm8,ymm9
 \output
 addq $128, %rsi
 addq $128, %rdx
 addq $128, %rdi
 addq $32, %r8
 addq $32, %r9
 decl %ecx
 jne .Ltile4_bm_b3_loop\@
 vzeroupper
 ret
 .size \name,.-\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION name,finalizer0,finalizer1,finalizer2,finalizer3,output
 .p2align 5
 .globl \name
 .type \name,@function
\name:
 leaq .Ltile4_bm_lambda(%rip), %r8
 leaq .Ltile4_bm_lambda_qinv(%rip), %r9
 vmovdqa .Ltile4_bm_q(%rip), %ymm0
 movl $12, %ecx
 .p2align 5
.Ltile4_bm_loop\@:
 vmovdqu 0(%rdx), %ymm1
 vmovdqu 32(%rdx), %ymm2
 vmovdqu 64(%rdx), %ymm3
 vmovdqu 96(%rdx), %ymm4
 TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
 vmovdqu 0(%rsi), %ymm5
 vmovdqu 32(%rsi), %ymm6
 vmovdqu 64(%rsi), %ymm7
 vmovdqu 96(%rsi), %ymm8
 TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8
 TILE4_MONT_FIRST ymm2,ymm6,ymm12
 TILE4_MONT_ADD ymm3,ymm7,ymm11
 TILE4_MONT_ADD ymm4,ymm8,ymm10
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm9
 \finalizer0
 vmovdqu %ymm15, 0(%rdi)
 TILE4_MONT_FIRST ymm3,ymm7,ymm12
 TILE4_MONT_ADD ymm4,ymm8,ymm11
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm10
 TILE4_MONT_ADD ymm2,ymm6,ymm9
 \finalizer1
 vmovdqu %ymm15, 32(%rdi)
 TILE4_MONT_FIRST ymm4,ymm8,ymm12
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm11
 TILE4_MONT_ADD ymm2,ymm6,ymm10
 TILE4_MONT_ADD ymm3,ymm7,ymm9
 \finalizer2
 vmovdqu %ymm15, 64(%rdi)
 TILE4_MONT_FIRST ymm1,ymm5,ymm12
 TILE4_MONT_ADD ymm2,ymm6,ymm11
 TILE4_MONT_ADD ymm3,ymm7,ymm10
 TILE4_MONT_ADD ymm4,ymm8,ymm9
 \finalizer3
 vmovdqu %ymm15, 96(%rdi)
 \output
 addq $128, %rsi
 addq $128, %rdx
 addq $128, %rdi
 addq $32, %r8
 addq $32, %r9
 decl %ecx
 jne .Ltile4_bm_loop\@
 vzeroupper
 ret
 .size \name,.-\name
 .endm
 .section .text.gt32_tile4_basemul_c3center_late_aos_private_asm,"ax",@progbits
 .text
 TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_scale_m_avx2, TILE4_OUTPUT_SOA_LATE_C3CENTER,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA
 TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA
 .p2align 5
 .section .rodata
 .section .rodata.gtclean.basemul.tile4_bm_q,"a",@progbits
 .p2align 5
.Ltile4_bm_q:
 .rept 16
 .short 3457
 .endr
.Ltile4_bm_qinv:
 .rept 16
 .short 12929
 .endr
.Ltile4_bm_center10:
 .rept 16
 .short 10
 .endr
.Ltile4_bm_rsq:
 .rept 16
 .short 867
 .endr
.Ltile4_bm_rsq_qinv:
 .rept 16
 .short 2787
 .endr
 .section .rodata.gtclean.basemul.tile4_bm_lambda,"a",@progbits
.p2align 5
.Ltile4_bm_lambda:
 .short 1655, -1674, -397, -223, -1655, 1674, 397, 223, 183, -559, 1059, -1138, -183, 559, -1059, 1138
 .short 242, 432, 437, -277, -242, -432, -437, 277, 1514, -1640, -1723, -933, -1514, 1640, 1723, 933
 .short 779, -1095, 1221, 294, -779, 1095, -1221, -294, 1588, 892, -218, -732, -1588, -892, 218, 732
 .short 22, -275, 354, -968, -22, 275, -354, 968, 1709, 1108, -1728, 858, -1709, -1108, 1728, -858
 .short -443, 352, 100, -1250, 443, -352, -100, 1250, -943, -312, -1660, 8, 943, 312, 1660, -8
 .short 1341, -1206, -1364, -235, -1341, 1206, 1364, 235, 1247, -31, 1209, 444, -1247, 31, -1209, -444
 .short 274, 32, -1248, -1685, -274, -32, 1248, 1685, -400, 1543, -1408, 315, 400, -1543, 1408, -315
 .short 1379, -1681, -124, 1550, -1379, 1681, 124, -1550, -1458, 940, 1367, -1531, 1458, -940, -1367, 1531
 .short -1212, 1322, 297, 1473, 1212, -1322, -297, -1473, 760, 871, 601, 1130, -760, -871, -601, -1130
 .short -1583, 774, 927, 512, 1583, -774, -927, -512, 696, 1671, 514, 489, -696, -1671, -514, -489
 .short -1053, 1063, 27, 1391, 1053, -1063, -27, -1391, -1188, 1022, 1626, 417, 1188, -1022, -1626, -417
 .short -1401, -1501, -230, -582, 1401, 1501, 230, 582, -251, 1409, 361, 673, 251, -1409, -361, -673
 .section .rodata.gtclean.basemul.tile4_bm_lambda_qinv,"a",@progbits
.p2align 5
.Ltile4_bm_lambda_qinv:
 .short 32759, -16266, -21005, 417, -32759, 16266, 21005, -417, 6711, -18351, -5213, 32398, -6711, 18351, 5213, -32398
 .short -16910, 14768, 13877, 23147, 16910, -14768, -13877, -23147, -20758, 30104, 5573, -4133, 20758, -30104, -5573, 4133
 .short -20853, -1479, -7867, 38, 20853, 1479, 7867, -38, 18484, -1668, -474, -26844, -18484, 1668, 474, 26844
 .short 22294, -16531, -10654, 2104, -22294, 16531, 10654, -2104, 10029, -27052, 6464, 17498, -10029, 27052, -6464, -17498
 .short -25915, 29024, -17820, 26142, 25915, -29024, 17820, -26142, -2351, 29384, -31868, -27640, 2351, -29384, 31868, 27640
 .short -29251, 5194, -5972, -23659, 29251, -5194, 5972, 23659, 607, -7583, -31943, -26692, -607, 7583, 31943, 26692
 .short 3602, 20512, -13536, -27413, -3602, -20512, 13536, 27413, 5744, 26503, 14976, 9403, -5744, -26503, -14976, -9403
 .short 3299, 24303, -30332, -14066, -3299, -24303, 30332, 14066, 23886, 29100, -20777, -2427, -23886, -29100, 20777, 2427
 .short -6844, -12758, -26711, -26559, 6844, 12758, 26711, 26559, -4360, -11033, -28455, -4758, 4360, 11033, 28455, 4758
 .short -19375, -19962, -7905, 512, 19375, 19962, 7905, -512, 20152, -22521, 26370, 30825, -20152, 22521, -26370, -30825
 .short 17251, -19033, 21403, 27375, -17251, 19033, -21403, -27375, -24228, -24834, -14502, 17441, 24228, 24834, 14502, -17441
 .short -25593, -7773, -24550, 11962, 25593, 7773, 24550, -11962, 31621, -2047, 14313, -15071, -31621, 2047, -14313, 15071
 .section .rodata.gtclean.basemul.tile4_bm_lambda_qpair02,"a",@progbits
.p2align 5
.Ltile4_bm_lambda_qpair02:
 .short 1655, 183, -1674, -559, -1655, -183, 1674, 559, -397, 1059, -223, -1138, 397, -1059, 223, 1138
 .short 242, 1514, 432, -1640, -242, -1514, -432, 1640, 437, -1723, -277, -933, -437, 1723, 277, 933
 .short 779, 1588, -1095, 892, -779, -1588, 1095, -892, 1221, -218, 294, -732, -1221, 218, -294, 732
 .short 22, 1709, -275, 1108, -22, -1709, 275, -1108, 354, -1728, -968, 858, -354, 1728, 968, -858
 .short -443, -943, 352, -312, 443, 943, -352, 312, 100, -1660, -1250, 8, -100, 1660, 1250, -8
 .short 1341, 1247, -1206, -31, -1341, -1247, 1206, 31, -1364, 1209, -235, 444, 1364, -1209, 235, -444
 .short 274, -400, 32, 1543, -274, 400, -32, -1543, -1248, -1408, -1685, 315, 1248, 1408, 1685, -315
 .short 1379, -1458, -1681, 940, -1379, 1458, 1681, -940, -124, 1367, 1550, -1531, 124, -1367, -1550, 1531
 .short -1212, 760, 1322, 871, 1212, -760, -1322, -871, 297, 601, 1473, 1130, -297, -601, -1473, -1130
 .short -1583, 696, 774, 1671, 1583, -696, -774, -1671, 927, 514, 512, 489, -927, -514, -512, -489
 .short -1053, -1188, 1063, 1022, 1053, 1188, -1063, -1022, 27, 1626, 1391, 417, -27, -1626, -1391, -417
 .short -1401, -251, -1501, 1409, 1401, 251, 1501, -1409, -230, 361, -582, 673, 230, -361, 582, -673
 .section .rodata.gtclean.basemul.tile4_bm_lambda_qpair02_qinv,"a",@progbits
.p2align 5
.Ltile4_bm_lambda_qpair02_qinv:
 .short 32759, 6711, -16266, -18351, -32759, -6711, 16266, 18351, -21005, -5213, 417, 32398, 21005, 5213, -417, -32398
 .short -16910, -20758, 14768, 30104, 16910, 20758, -14768, -30104, 13877, 5573, 23147, -4133, -13877, -5573, -23147, 4133
 .short -20853, 18484, -1479, -1668, 20853, -18484, 1479, 1668, -7867, -474, 38, -26844, 7867, 474, -38, 26844
 .short 22294, 10029, -16531, -27052, -22294, -10029, 16531, 27052, -10654, 6464, 2104, 17498, 10654, -6464, -2104, -17498
 .short -25915, -2351, 29024, 29384, 25915, 2351, -29024, -29384, -17820, -31868, 26142, -27640, 17820, 31868, -26142, 27640
 .short -29251, 607, 5194, -7583, 29251, -607, -5194, 7583, -5972, -31943, -23659, -26692, 5972, 31943, 23659, 26692
 .short 3602, 5744, 20512, 26503, -3602, -5744, -20512, -26503, -13536, 14976, -27413, 9403, 13536, -14976, 27413, -9403
 .short 3299, 23886, 24303, 29100, -3299, -23886, -24303, -29100, -30332, -20777, -14066, -2427, 30332, 20777, 14066, 2427
 .short -6844, -4360, -12758, -11033, 6844, 4360, 12758, 11033, -26711, -28455, -26559, -4758, 26711, 28455, 26559, 4758
 .short -19375, 20152, -19962, -22521, 19375, -20152, 19962, 22521, -7905, 26370, 512, 30825, 7905, -26370, -512, -30825
 .short 17251, -24228, -19033, -24834, -17251, 24228, 19033, 24834, 21403, -14502, 27375, 17441, -21403, 14502, -27375, -17441
 .short -25593, 31621, -7773, -2047, 25593, -31621, 7773, 2047, -24550, 14313, 11962, -15071, 24550, -14313, -11962, 15071
 .section .rodata.gtclean.basemul.tile4_bm_lambda_p,"a",@progbits
.p2align 5
.Ltile4_bm_lambda_p:
 .short 1655, 183, -397, 1059, -1655, -183, 397, -1059, -1674, -559, -223, -1138, 1674, 559, 223, 1138
 .short 242, 1514, 437, -1723, -242, -1514, -437, 1723, 432, -1640, -277, -933, -432, 1640, 277, 933
 .short 779, 1588, 1221, -218, -779, -1588, -1221, 218, -1095, 892, 294, -732, 1095, -892, -294, 732
 .short 22, 1709, 354, -1728, -22, -1709, -354, 1728, -275, 1108, -968, 858, 275, -1108, 968, -858
 .short -443, -943, 100, -1660, 443, 943, -100, 1660, 352, -312, -1250, 8, -352, 312, 1250, -8
 .short 1341, 1247, -1364, 1209, -1341, -1247, 1364, -1209, -1206, -31, -235, 444, 1206, 31, 235, -444
 .short 274, -400, -1248, -1408, -274, 400, 1248, 1408, 32, 1543, -1685, 315, -32, -1543, 1685, -315
 .short 1379, -1458, -124, 1367, -1379, 1458, 124, -1367, -1681, 940, 1550, -1531, 1681, -940, -1550, 1531
 .short -1212, 760, 297, 601, 1212, -760, -297, -601, 1322, 871, 1473, 1130, -1322, -871, -1473, -1130
 .short -1583, 696, 927, 514, 1583, -696, -927, -514, 774, 1671, 512, 489, -774, -1671, -512, -489
 .short -1053, -1188, 27, 1626, 1053, 1188, -27, -1626, 1063, 1022, 1391, 417, -1063, -1022, -1391, -417
 .short -1401, -251, -230, 361, 1401, 251, 230, -361, -1501, 1409, -582, 673, 1501, -1409, 582, -673
 .section .rodata.gtclean.basemul.tile4_bm_lambda_p_qinv,"a",@progbits
.p2align 5
.Ltile4_bm_lambda_p_qinv:
 .short 32759, 6711, -21005, -5213, -32759, -6711, 21005, 5213, -16266, -18351, 417, 32398, 16266, 18351, -417, -32398
 .short -16910, -20758, 13877, 5573, 16910, 20758, -13877, -5573, 14768, 30104, 23147, -4133, -14768, -30104, -23147, 4133
 .short -20853, 18484, -7867, -474, 20853, -18484, 7867, 474, -1479, -1668, 38, -26844, 1479, 1668, -38, 26844
 .short 22294, 10029, -10654, 6464, -22294, -10029, 10654, -6464, -16531, -27052, 2104, 17498, 16531, 27052, -2104, -17498
 .short -25915, -2351, -17820, -31868, 25915, 2351, 17820, 31868, 29024, 29384, 26142, -27640, -29024, -29384, -26142, 27640
 .short -29251, 607, -5972, -31943, 29251, -607, 5972, 31943, 5194, -7583, -23659, -26692, -5194, 7583, 23659, 26692
 .short 3602, 5744, -13536, 14976, -3602, -5744, 13536, -14976, 20512, 26503, -27413, 9403, -20512, -26503, 27413, -9403
 .short 3299, 23886, -30332, -20777, -3299, -23886, 30332, 20777, 24303, 29100, -14066, -2427, -24303, -29100, 14066, 2427
 .short -6844, -4360, -26711, -28455, 6844, 4360, 26711, 28455, -12758, -11033, -26559, -4758, 12758, 11033, 26559, 4758
 .short -19375, 20152, -7905, 26370, 19375, -20152, 7905, -26370, -19962, -22521, 512, 30825, 19962, 22521, -512, -30825
 .short 17251, -24228, 21403, -14502, -17251, 24228, -21403, 14502, -19033, -24834, 27375, 17441, 19033, 24834, -27375, -17441
 .short -25593, 31621, -24550, 14313, 25593, -31621, 24550, -14313, -7773, -2047, 11962, -15071, 7773, 2047, -11962, 15071
 .section .note.GNU-stack,"",@progbits

/* ---- selected production component ---- */
 .text
 .macro GT_MONT_FIRST a, aq, b
 vpmullw %\aq, %\b, %ymm13
 vpmulhw %\a, %\b, %ymm15
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm15, %ymm15
 .endm
 .macro GT_MONT_ADD a, aq, b
 vpmullw %\aq, %\b, %ymm13
 vpmulhw %\a, %\b, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm14
 vpaddw %ymm14, %ymm15, %ymm15
 .endm
 .macro GT_MONT_LAMBDA
 vpmullw (%r9), %ymm15, %ymm13
 vpmulhw (%r8), %ymm15, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm15
 .endm
 .macro GT_MONT_RSQ
 vpmullw .Lgt_rsq_qinv(%rip), %ymm15, %ymm13
 vpmulhw .Lgt_rsq(%rip), %ymm15, %ymm14
 vpmulhw %ymm0, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm15
 .endm
 .macro GT_CENTER_RMINUS1
 vpmulhrsw .Lgt_center10(%rip), %ymm15, %ymm14
 vpmullw %ymm0, %ymm14, %ymm14
 vpsubw %ymm14, %ymm15, %ymm15
 .endm
 .macro GT_KEEP_RMINUS1
 .endm
 .macro GT_BASEMUL_BODY batch_label, c0_finalizer, c123_finalizer
 vmovdqa .Lgt_q(%rip), %ymm0
 movl $12, %ecx
 .p2align 5
\batch_label:
 vmovdqu 0(%rsi), %ymm1
 vmovdqu 32(%rsi), %ymm2
 vmovdqu 64(%rsi), %ymm3
 vmovdqu 96(%rsi), %ymm4
 vmovdqu 0(%rdx), %ymm9
 vmovdqu 32(%rdx), %ymm10
 vmovdqu 64(%rdx), %ymm11
 vmovdqu 96(%rdx), %ymm12
 vpmullw .Lgt_qinv(%rip), %ymm1, %ymm5
 vpmullw .Lgt_qinv(%rip), %ymm2, %ymm6
 vpmullw .Lgt_qinv(%rip), %ymm3, %ymm7
 vpmullw .Lgt_qinv(%rip), %ymm4, %ymm8
 GT_MONT_FIRST ymm2, ymm6, ymm12
 GT_MONT_ADD ymm3, ymm7, ymm11
 GT_MONT_ADD ymm4, ymm8, ymm10
 GT_MONT_LAMBDA
 GT_MONT_ADD ymm1, ymm5, ymm9
 \c0_finalizer
 vmovdqu %ymm15, 0(%rdi)
 GT_MONT_FIRST ymm3, ymm7, ymm12
 GT_MONT_ADD ymm4, ymm8, ymm11
 GT_MONT_LAMBDA
 GT_MONT_ADD ymm1, ymm5, ymm10
 GT_MONT_ADD ymm2, ymm6, ymm9
 \c123_finalizer
 vmovdqu %ymm15, 32(%rdi)
 GT_MONT_FIRST ymm4, ymm8, ymm12
 GT_MONT_LAMBDA
 GT_MONT_ADD ymm1, ymm5, ymm11
 GT_MONT_ADD ymm2, ymm6, ymm10
 GT_MONT_ADD ymm3, ymm7, ymm9
 \c123_finalizer
 vmovdqu %ymm15, 64(%rdi)
 GT_MONT_FIRST ymm1, ymm5, ymm12
 GT_MONT_ADD ymm2, ymm6, ymm11
 GT_MONT_ADD ymm3, ymm7, ymm10
 GT_MONT_ADD ymm4, ymm8, ymm9
 \c123_finalizer
 vmovdqu %ymm15, 96(%rdi)
 addq $128, %rsi
 addq $128, %rdx
 addq $128, %rdi
 addq $32, %r8
 addq $32, %r9
 decl %ecx
 jne \batch_label
 vzeroupper
 ret
 .endm
 .p2align 5
 .p2align 5
 .p2align 5
 .globl ntruplus768_basemul_f0_j1_avx2
 .type ntruplus768_basemul_f0_j1_avx2,@function
ntruplus768_basemul_f0_j1_avx2:
 leaq gt_native_lambda(%rip), %r8
 leaq gt_native_lambda_qinv(%rip), %r9
 GT_BASEMUL_BODY .Lgt_basemul_f0_j1_batch, GT_KEEP_RMINUS1, GT_KEEP_RMINUS1
 .size ntruplus768_basemul_f0_j1_avx2,.-ntruplus768_basemul_f0_j1_avx2
 .p2align 5
 .p2align 5
 .p2align 5
 .p2align 5
 .section .rodata
 .section .rodata.gtclean.basemul.gt_q,"a",@progbits
 .p2align 5
.Lgt_q:
 .rept 16
 .short 3457
 .endr
.Lgt_qinv:
 .rept 16
 .short 12929
 .endr
.Lgt_rsq:
 .rept 16
 .short 867
 .endr
.Lgt_rsq_qinv:
 .rept 16
 .short 2787
 .endr
.Lgt_center10:
 .rept 16
 .short 10
 .endr
 .section .note.GNU-stack,"",@progbits
