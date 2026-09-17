 .text
 .macro FR_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
 vpmullw \qinv+0(%rip), \h0, %ymm8
 vpmullw \qinv+32(%rip), \h1, %ymm9
 vpmullw \qinv+64(%rip), \h2, %ymm10
 vpmullw \qinv+96(%rip), \h3, %ymm11
 vpmulhw \factor+0(%rip), \h0, \h0
 vpmulhw \factor+32(%rip), \h1, \h1
 vpmulhw \factor+64(%rip), \h2, \h2
 vpmulhw \factor+96(%rip), \h3, \h3
 vpmulhw %ymm15, %ymm8, %ymm8
 vpmulhw %ymm15, %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm11, %ymm11
 vpsubw %ymm8, \h0, \h0
 vpsubw %ymm9, \h1, \h1
 vpsubw %ymm10, \h2, \h2
 vpsubw %ymm11, \h3, \h3
 vpsubw \h0, \l0, %ymm8
 vpsubw \h1, \l1, %ymm9
 vpsubw \h2, \l2, %ymm10
 vpsubw \h3, \l3, %ymm11
 vpaddw \h0, \l0, \l0
 vpaddw \h1, \l1, \l1
 vpaddw \h2, \l2, \l2
 vpaddw \h3, \l3, \l3
 vmovdqa %ymm8, \h0
 vmovdqa %ymm9, \h1
 vmovdqa %ymm10, \h2
 vmovdqa %ymm11, \h3
 .endm
 .macro FR_PACKED_TO_BM_REGS v0,v1,v2,v3
 vpshufb %ymm14, \v0, \v0
 vpshufb %ymm14, \v1, \v1
 vpshufb %ymm14, \v2, \v2
 vpshufb %ymm14, \v3, \v3
 vpunpckldq \v2, \v0, %ymm4
 vpunpckhdq \v2, \v0, %ymm5
 vpunpckldq \v3, \v1, %ymm6
 vpunpckhdq \v3, \v1, %ymm7
 vpunpcklqdq %ymm6, %ymm4, %ymm9
 vpunpckhqdq %ymm6, %ymm4, %ymm10
 vpunpcklqdq %ymm7, %ymm5, %ymm11
 vpunpckhqdq %ymm7, %ymm5, %ymm12
 .endm
 .macro FR_STREAM_MONT_FIRST a,aq,b
 vpmullw \aq, \b, %ymm13
 vpmulhw \a, \b, %ymm0
 vpmulhw %ymm15, %ymm13, %ymm13
 vpsubw %ymm13, %ymm0, %ymm0
 .endm
 .macro FR_STREAM_MONT_ADD a,aq,b
 vpmullw \aq, \b, %ymm13
 vpmulhw \a, \b, %ymm14
 vpmulhw %ymm15, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm14
 vpaddw %ymm14, %ymm0, %ymm0
 .endm
 .macro FR_STREAM_MONT_LAMBDA
 vpmullw (%r9), %ymm0, %ymm13
 vpmulhw (%r8), %ymm0, %ymm14
 vpmulhw %ymm15, %ymm13, %ymm13
 vpsubw %ymm13, %ymm14, %ymm0
 .endm
 .macro FR_STREAM_BM_BLOCK
 vmovdqu 0(%rsi), %ymm1
 vmovdqu 32(%rsi), %ymm2
 vmovdqu 64(%rsi), %ymm3
 vmovdqu 96(%rsi), %ymm4
 vpmullw .Lfr_stream_qinv(%rip), %ymm1, %ymm5
 vpmullw .Lfr_stream_qinv(%rip), %ymm2, %ymm6
 vpmullw .Lfr_stream_qinv(%rip), %ymm3, %ymm7
 vpmullw .Lfr_stream_qinv(%rip), %ymm4, %ymm8
 FR_STREAM_MONT_FIRST %ymm2,%ymm6,%ymm12
 FR_STREAM_MONT_ADD %ymm3,%ymm7,%ymm11
 FR_STREAM_MONT_ADD %ymm4,%ymm8,%ymm10
 FR_STREAM_MONT_LAMBDA
 FR_STREAM_MONT_ADD %ymm1,%ymm5,%ymm9
 vmovdqu %ymm0, 0(%rdi)
 FR_STREAM_MONT_FIRST %ymm3,%ymm7,%ymm12
 FR_STREAM_MONT_ADD %ymm4,%ymm8,%ymm11
 FR_STREAM_MONT_LAMBDA
 FR_STREAM_MONT_ADD %ymm1,%ymm5,%ymm10
 FR_STREAM_MONT_ADD %ymm2,%ymm6,%ymm9
 vmovdqu %ymm0, 32(%rdi)
 FR_STREAM_MONT_FIRST %ymm4,%ymm8,%ymm12
 FR_STREAM_MONT_LAMBDA
 FR_STREAM_MONT_ADD %ymm1,%ymm5,%ymm11
 FR_STREAM_MONT_ADD %ymm2,%ymm6,%ymm10
 FR_STREAM_MONT_ADD %ymm3,%ymm7,%ymm9
 vmovdqu %ymm0, 64(%rdi)
 FR_STREAM_MONT_FIRST %ymm1,%ymm5,%ymm12
 FR_STREAM_MONT_ADD %ymm2,%ymm6,%ymm11
 FR_STREAM_MONT_ADD %ymm3,%ymm7,%ymm10
 FR_STREAM_MONT_ADD %ymm4,%ymm8,%ymm9
 vpmulhrsw .Lfr_stream_center10(%rip), %ymm0, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, %ymm0, %ymm0
 vmovdqu %ymm0, 96(%rdi)
 .endm
 .macro FR_MONT_QWORD_PACKED4
 vpunpckhqdq %ymm1, %ymm0, %ymm8
 vpunpckhqdq %ymm3, %ymm2, %ymm9
 vpunpckhqdq %ymm5, %ymm4, %ymm10
 vpunpckhqdq %ymm7, %ymm6, %ymm11
 vpunpcklqdq %ymm1, %ymm0, %ymm0
 vpunpcklqdq %ymm3, %ymm2, %ymm2
 vpunpcklqdq %ymm5, %ymm4, %ymm4
 vpunpcklqdq %ymm7, %ymm6, %ymm6
 vpmullw .Ltile4_fwd_s5_pair_qinv+0(%rip), %ymm8, %ymm1
 vpmullw .Ltile4_fwd_s5_pair_qinv+32(%rip), %ymm9, %ymm3
 vpmullw .Ltile4_fwd_s5_pair_qinv+64(%rip), %ymm10, %ymm5
 vpmullw .Ltile4_fwd_s5_pair_qinv+96(%rip), %ymm11, %ymm7
 vpmulhw .Ltile4_fwd_s5_pair_factor+0(%rip), %ymm8, %ymm8
 vpmulhw .Ltile4_fwd_s5_pair_factor+32(%rip), %ymm9, %ymm9
 vpmulhw .Ltile4_fwd_s5_pair_factor+64(%rip), %ymm10, %ymm10
 vpmulhw .Ltile4_fwd_s5_pair_factor+96(%rip), %ymm11, %ymm11
 vpmulhw %ymm15, %ymm1, %ymm1
 vpmulhw %ymm15, %ymm3, %ymm3
 vpmulhw %ymm15, %ymm5, %ymm5
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm1, %ymm8, %ymm8
 vpsubw %ymm3, %ymm9, %ymm9
 vpsubw %ymm5, %ymm10, %ymm10
 vpsubw %ymm7, %ymm11, %ymm11
 vpsubw %ymm8, %ymm0, %ymm1
 vpsubw %ymm9, %ymm2, %ymm3
 vpsubw %ymm10, %ymm4, %ymm5
 vpsubw %ymm11, %ymm6, %ymm7
 vpaddw %ymm8, %ymm0, %ymm0
 vpaddw %ymm9, %ymm2, %ymm2
 vpaddw %ymm10, %ymm4, %ymm4
 vpaddw %ymm11, %ymm6, %ymm6
 .endm
 .macro FR_RAW_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3
 vpsubw \h0, \l0, %ymm8
 vpsubw \h1, \l1, %ymm9
 vpsubw \h2, \l2, %ymm10
 vpsubw \h3, \l3, %ymm11
 vpaddw \h0, \l0, \l0
 vpaddw \h1, \l1, \l1
 vpaddw \h2, \l2, \l2
 vpaddw \h3, \l3, \l3
 vmovdqa %ymm8, \h0
 vmovdqa %ymm9, \h1
 vmovdqa %ymm10, \h2
 vmovdqa %ymm11, \h3
 .endm
 .macro FR_MONT_HALF_PAIR v0,v1,offset
 vperm2i128 $0x20, \v1, \v0, %ymm8
 vperm2i128 $0x31, \v1, \v0, %ymm9
 vpmullw .Ltile4_fwd_s4_pair_qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw .Ltile4_fwd_s4_pair_factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vperm2i128 $0x20, %ymm10, %ymm8, \v0
 vperm2i128 $0x31, %ymm10, %ymm8, \v1
 .endm
 .macro FR_MONT_QWORD_PACKED v0,v1,offset
 vpunpcklqdq \v1, \v0, %ymm8
 vpunpckhqdq \v1, \v0, %ymm9
 vpmullw .Ltile4_fwd_s5_pair_qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw .Ltile4_fwd_s5_pair_factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, \v0
 vmovdqa %ymm10, \v1
 .endm
 .macro FR_MONT_HALF_QPAIR02 v0,v1,offset
 vperm2i128 $0x20, \v1, \v0, %ymm8
 vperm2i128 $0x31, \v1, \v0, %ymm9
 vpmullw .Ltile4_fwd_s4_qpair02_qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw .Ltile4_fwd_s4_qpair02_factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, \v1
 vpaddw %ymm9, %ymm8, \v0
 .endm
 .macro FR_MONT_QWORD_QPAIR02 v0,v1,offset
 vpunpcklqdq \v1, \v0, %ymm8
 vpunpckhqdq \v1, \v0, %ymm9
 vpmullw .Ltile4_fwd_s5_qpair02_qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw .Ltile4_fwd_s5_qpair02_factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, \v0
 vmovdqa %ymm10, \v1
 .endm
 .macro FR_PACKED_TO_PLANES v0,v1,v2,v3,outoff
 vpshufb %ymm14, \v0, \v0
 vpshufb %ymm14, \v1, \v1
 vpshufb %ymm14, \v2, \v2
 vpshufb %ymm14, \v3, \v3
 vpunpckldq \v2, \v0, %ymm8
 vpunpckhdq \v2, \v0, %ymm9
 vpunpckldq \v3, \v1, %ymm10
 vpunpckhdq \v3, \v1, %ymm11
 vpunpcklqdq %ymm10, %ymm8, \v0
 vpunpckhqdq %ymm10, %ymm8, \v1
 vpunpcklqdq %ymm11, %ymm9, \v2
 vpunpckhqdq %ymm11, %ymm9, \v3
 vmovdqu \v0, \outoff+0(%rdi)
 vmovdqu \v1, \outoff+32(%rdi)
 vmovdqu \v2, \outoff+64(%rdi)
 vmovdqu \v3, \outoff+96(%rdi)
 .endm
 .macro FR_PACKED_TO_PLANES_SHUFPS v0,v1,v2,v3,outoff
 vpshufb %ymm14, \v0, \v0
 vpshufb %ymm14, \v1, \v1
 vpshufb %ymm14, \v2, \v2
 vpshufb %ymm14, \v3, \v3
 vshufps $0x11, \v2, \v0, %ymm8
 vshufps $0xbb, \v2, \v0, %ymm9
 vshufps $0x11, \v3, \v1, %ymm10
 vshufps $0xbb, \v3, \v1, %ymm11
 vshufps $0xdd, %ymm10, %ymm8, \v0
 vshufps $0x88, %ymm10, %ymm8, \v1
 vshufps $0xdd, %ymm11, %ymm9, \v2
 vshufps $0x88, %ymm11, %ymm9, \v3
 vmovdqu \v0, \outoff+0(%rdi)
 vmovdqu \v1, \outoff+32(%rdi)
 vmovdqu \v2, \outoff+64(%rdi)
 vmovdqu \v3, \outoff+96(%rdi)
 .endm
 .macro FR_PACKED_TO_L1 v0,v1,v2,v3,outoff
 vpshufb %ymm14, \v0, \v0
 vpshufb %ymm14, \v1, \v1
 vpshufb %ymm14, \v2, \v2
 vpshufb %ymm14, \v3, \v3
 vmovdqu \v0, \outoff+0(%rdi)
 vmovdqu \v1, \outoff+32(%rdi)
 vmovdqu \v2, \outoff+64(%rdi)
 vmovdqu \v3, \outoff+96(%rdi)
 .endm
 .macro FR_PACKED_TO_L2 v0,v1,v2,v3,outoff
 vpshufb %ymm14, \v0, \v0
 vpshufb %ymm14, \v1, \v1
 vpshufb %ymm14, \v2, \v2
 vpshufb %ymm14, \v3, \v3
 vpunpckldq \v2, \v0, %ymm8
 vpunpckhdq \v2, \v0, %ymm9
 vpunpckldq \v3, \v1, %ymm10
 vpunpckhdq \v3, \v1, %ymm11
 vmovdqu %ymm8, \outoff+0(%rdi)
 vmovdqu %ymm9, \outoff+32(%rdi)
 vmovdqu %ymm10, \outoff+64(%rdi)
 vmovdqu %ymm11, \outoff+96(%rdi)
 .endm
 .macro FR_TRANSPOSE_CUT_FORWARD_FUNCTION name,deposit
 .p2align 5
 .globl \name
 .type \name,@function
\name:
 vmovdqa .Lfr_q(%rip), %ymm15
 vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
 movl $6, %ecx
 .p2align 5
.Lfr_transpose_cut_loop\@:
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vmovdqu 128(%rsi), %ymm4
 vmovdqu 160(%rsi), %ymm5
 vmovdqu 192(%rsi), %ymm6
 vmovdqu 224(%rsi), %ymm7
 FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
 FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor
 FR_MONT_HALF_PAIR %ymm0,%ymm1,0
 FR_MONT_HALF_PAIR %ymm2,%ymm3,32
 FR_MONT_HALF_PAIR %ymm4,%ymm5,64
 FR_MONT_HALF_PAIR %ymm6,%ymm7,96
 FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
 FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
 \deposit %ymm0,%ymm1,%ymm2,%ymm3,0
 FR_MONT_QWORD_PACKED %ymm4,%ymm5,64
 FR_MONT_QWORD_PACKED %ymm6,%ymm7,96
 \deposit %ymm4,%ymm5,%ymm6,%ymm7,128
 addq $256, %rsi
 addq $256, %rdi
 decl %ecx
 jne .Lfr_transpose_cut_loop\@
 vzeroupper
 ret
 .size \name,.-\name
 .endm
 .p2align 5
 .globl ntruplus768_ntt_m_avx2
 .type ntruplus768_ntt_m_avx2,@function
ntruplus768_ntt_m_avx2:
 vmovdqa .Lfr_q(%rip), %ymm15
 vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
 movl $6, %ecx
 .p2align 5
.Lfr_core_loop:
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vmovdqu 128(%rsi), %ymm4
 vmovdqu 160(%rsi), %ymm5
 vmovdqu 192(%rsi), %ymm6
 vmovdqu 224(%rsi), %ymm7
 FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
 FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor
 FR_MONT_HALF_PAIR %ymm0,%ymm1,0
 FR_MONT_HALF_PAIR %ymm2,%ymm3,32
 FR_MONT_HALF_PAIR %ymm4,%ymm5,64
 FR_MONT_HALF_PAIR %ymm6,%ymm7,96
 FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
 FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
 FR_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
 FR_MONT_QWORD_PACKED %ymm4,%ymm5,64
 FR_MONT_QWORD_PACKED %ymm6,%ymm7,96
 FR_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
 addq $256, %rsi
 addq $256, %rdi
 decl %ecx
 jne .Lfr_core_loop
 vzeroupper
 ret
 .size ntruplus768_ntt_m_avx2,.-ntruplus768_ntt_m_avx2
 .macro FR_S45_W1
 FR_MONT_HALF_PAIR %ymm0,%ymm1,0
 FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
 FR_MONT_HALF_PAIR %ymm2,%ymm3,32
 FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
 FR_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
 FR_MONT_HALF_PAIR %ymm4,%ymm5,64
 FR_MONT_QWORD_PACKED %ymm4,%ymm5,64
 FR_MONT_HALF_PAIR %ymm6,%ymm7,96
 FR_MONT_QWORD_PACKED %ymm6,%ymm7,96
 FR_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
 .endm
 .macro FR_S45_W2
 FR_MONT_HALF_PAIR %ymm0,%ymm1,0
 FR_MONT_HALF_PAIR %ymm2,%ymm3,32
 FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
 FR_MONT_HALF_PAIR %ymm4,%ymm5,64
 FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
 FR_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
 FR_MONT_HALF_PAIR %ymm6,%ymm7,96
 FR_MONT_QWORD_PACKED %ymm4,%ymm5,64
 FR_MONT_QWORD_PACKED %ymm6,%ymm7,96
 FR_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
 .endm
 .macro FR_WAVEFRONT_FUNCTION name,schedule
 .p2align 5
 .globl \name
 .type \name,@function
\name:
 vmovdqa .Lfr_q(%rip), %ymm15
 vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
 movl $6, %ecx
 .p2align 5
.Lfr_wavefront_loop\@:
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vmovdqu 128(%rsi), %ymm4
 vmovdqu 160(%rsi), %ymm5
 vmovdqu 192(%rsi), %ymm6
 vmovdqu 224(%rsi), %ymm7
 FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
 FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor
 \schedule
 addq $256, %rsi
 addq $256, %rdi
 decl %ecx
 jne .Lfr_wavefront_loop\@
 vzeroupper
 ret
 .size \name,.-\name
 .endm
 .p2align 5
 .p2align 5
 .macro FR_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
 vpunpcklwd \s1, \s0, \t0
 vpunpckhwd \s1, \s0, \t1
 vpunpcklwd \s3, \s2, \t2
 vpunpckhwd \s3, \s2, \t3
 vpunpckldq \t2, \t0, \s0
 vpunpckhdq \t2, \t0, \s1
 vpunpckldq \t3, \t1, \s2
 vpunpckhdq \t3, \t1, \s3
 vpunpcklqdq \s2, \s0, \t0
 vpunpckhqdq \s2, \s0, \t1
 vpunpcklqdq \s3, \s1, \t2
 vpunpckhqdq \s3, \s1, \t3
 .endm
 .macro FR_QPAIR02_OUTPUT_AOS
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 vmovdqu 96(%rdi), %ymm4
 FR_TRANSPOSE %ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 vperm2i128 $0x20, %ymm6, %ymm5, %ymm1
 vperm2i128 $0x31, %ymm6, %ymm5, %ymm3
 vperm2i128 $0x20, %ymm8, %ymm7, %ymm2
 vperm2i128 $0x31, %ymm8, %ymm7, %ymm4
 vmovdqu %ymm1, 0(%rdi)
 vmovdqu %ymm2, 32(%rdi)
 vmovdqu %ymm3, 64(%rdi)
 vmovdqu %ymm4, 96(%rdi)
 .endm
 .p2align 5
 .macro FR_P_OUTPUT_AOS
 vmovdqu 0(%rdi), %ymm1
 vmovdqu 32(%rdi), %ymm2
 vmovdqu 64(%rdi), %ymm3
 vmovdqu 96(%rdi), %ymm4
 FR_TRANSPOSE %ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8
 vperm2i128 $0x20, %ymm6, %ymm5, %ymm1
 vperm2i128 $0x31, %ymm6, %ymm5, %ymm2
 vperm2i128 $0x20, %ymm8, %ymm7, %ymm3
 vperm2i128 $0x31, %ymm8, %ymm7, %ymm4
 vmovdqu %ymm1, 0(%rdi)
 vmovdqu %ymm2, 32(%rdi)
 vmovdqu %ymm3, 64(%rdi)
 vmovdqu %ymm4, 96(%rdi)
 .endm
 .p2align 5
 .p2align 5
 .section .rodata
 .section .rodata.gtclean.ntt_m.fr_q,"a",@progbits
 .p2align 5
.Lfr_q:
 .rept 16
 .short 3457
 .endr
.Lfr_plane_pshufb:
 .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
 .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
 .section .rodata.gtclean.ntt_m.fr_stream_qinv,"a",@progbits
 .p2align 5
.Lfr_stream_qinv:
 .rept 16
 .short 12929
 .endr
.Lfr_stream_center10:
 .rept 16
 .short 10
 .endr
 .section .rodata.gtclean.ntt_m.tile4_bm_lambda,"a",@progbits
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
 .section .rodata.gtclean.ntt_m.tile4_bm_lambda_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt_m.tile4_bm_lambda_qpair02,"a",@progbits
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
 .section .rodata.gtclean.ntt_m.tile4_bm_lambda_qpair02_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt_m.tile4_bm_lambda_p,"a",@progbits
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
 .section .rodata.gtclean.ntt_m.tile4_bm_lambda_p_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt_m.tile4_fwd_s1_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s1_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .section .rodata.gtclean.ntt_m.tile4_fwd_s1_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s1_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .section .rodata.gtclean.ntt_m.tile4_fwd_s2_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s2_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .section .rodata.gtclean.ntt_m.tile4_fwd_s2_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s2_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .section .rodata.gtclean.ntt_m.tile4_fwd_s3_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s3_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834
 .section .rodata.gtclean.ntt_m.tile4_fwd_s3_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s3_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,109,109,109,109,109,109,109,109
 .short -1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .section .rodata.gtclean.ntt_m.tile4_fwd_s4_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,23526,23526,23526,23526,23526,23526,23526,23526
 .short -10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
 .short 834,834,834,834,834,834,834,834,834,834,834,834,834,834,834,834
 .short -739,-739,-739,-739,-739,-739,-739,-739,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.ntt_m.tile4_fwd_s4_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,109,109,109,109,109,109,109,109
 .short -1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-794,-794,-794,-794,-794,-794,-794,-794
 .short -1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
 .short -446,-446,-446,-446,-446,-446,-446,-446,-446,-446,-446,-446,-446,-446,-446,-446
 .short 1181,1181,1181,1181,1181,1181,1181,1181,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
 .short 834,834,834,834,834,834,834,834,-739,-739,-739,-739,-739,-739,-739,-739
 .short 31716,31716,31716,31716,31716,31716,31716,31716,24019,24019,24019,24019,24019,24019,24019,24019
 .short 29536,29536,29536,29536,29536,29536,29536,29536,-5327,-5327,-5327,-5327,-5327,-5327,-5327,-5327
 .short 27754,27754,27754,27754,27754,27754,27754,27754,11147,11147,11147,11147,11147,11147,11147,11147
 .short -19242,-19242,-19242,-19242,-19242,-19242,-19242,-19242,-8265,-8265,-8265,-8265,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
 .short -446,-446,-446,-446,-446,-446,-446,-446,1181,1181,1181,1181,1181,1181,1181,1181
 .short 484,484,484,484,484,484,484,484,-429,-429,-429,-429,-429,-429,-429,-429
 .short 864,864,864,864,864,864,864,864,177,177,177,177,177,177,177,177
 .short 874,874,874,874,874,874,874,874,11,11,11,11,11,11,11,11
 .short -554,-554,-554,-554,-554,-554,-554,-554,1591,1591,1591,1591,1591,1591,1591,1591
 .section .rodata.gtclean.ntt_m.tile4_inv_s1_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s1_qinv:
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .section .rodata.gtclean.ntt_m.tile4_inv_s1_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s1_factor:
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .section .rodata.gtclean.ntt_m.tile4_inv_s2_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s2_qinv:
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .section .rodata.gtclean.ntt_m.tile4_inv_s2_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s2_factor:
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .section .rodata.gtclean.ntt_m.tile4_inv_s3_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s3_qinv:
 .short -19,-19,-19,-19,739,739,739,739,-28834,-28834,-28834,-28834,10427,10427,10427,10427
 .short -13422,-13422,-13422,-13422,-834,-834,-834,-834,32531,32531,32531,32531,-23526,-23526,-23526,-23526
 .short -19,-19,-19,-19,739,739,739,739,-28834,-28834,-28834,-28834,10427,10427,10427,10427
 .short -13422,-13422,-13422,-13422,-834,-834,-834,-834,32531,32531,32531,32531,-23526,-23526,-23526,-23526
 .section .rodata.gtclean.ntt_m.tile4_inv_s3_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s3_factor:
 .short -147,-147,-147,-147,-1181,-1181,-1181,-1181,1118,1118,1118,1118,1339,1339,1339,1339
 .short -366,-366,-366,-366,446,446,446,446,-109,-109,-109,-109,794,794,794,794
 .short -147,-147,-147,-147,-1181,-1181,-1181,-1181,1118,1118,1118,1118,1339,1339,1339,1339
 .short -366,-366,-366,-366,446,446,446,446,-109,-109,-109,-109,794,794,794,794
 .section .rodata.gtclean.ntt_m.tile4_inv_s4_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s4_qinv:
 .short -19,-19,-19,-19,8265,8265,8265,8265,739,739,739,739,5327,5327,5327,5327
 .short -28834,-28834,-28834,-28834,-11147,-11147,-11147,-11147,10427,10427,10427,10427,-24019,-24019,-24019,-24019
 .short -13422,-13422,-13422,-13422,19242,19242,19242,19242,-834,-834,-834,-834,-29536,-29536,-29536,-29536
 .short 32531,32531,32531,32531,-27754,-27754,-27754,-27754,-23526,-23526,-23526,-23526,-31716,-31716,-31716,-31716
 .section .rodata.gtclean.ntt_m.tile4_inv_s4_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s4_factor:
 .short -147,-147,-147,-147,-1591,-1591,-1591,-1591,-1181,-1181,-1181,-1181,-177,-177,-177,-177
 .short 1118,1118,1118,1118,-11,-11,-11,-11,1339,1339,1339,1339,429,429,429,429
 .short -366,-366,-366,-366,554,554,554,554,446,446,446,446,-864,-864,-864,-864
 .short -109,-109,-109,-109,-874,-874,-874,-874,794,794,794,794,-484,-484,-484,-484
 .section .rodata.gtclean.ntt_m.tile4_fwd_s4_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_pair_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
 .short 834,834,834,834,834,834,834,834,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.ntt_m.tile4_fwd_s4_pair_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_pair_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
 .short -446,-446,-446,-446,-446,-446,-446,-446,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_pair_qinv:
 .short -19,-19,-19,-19,-32531,-32531,-32531,-32531,13422,13422,13422,13422,28834,28834,28834,28834
 .short 23526,23526,23526,23526,834,834,834,834,-10427,-10427,-10427,-10427,-739,-739,-739,-739
 .short 31716,31716,31716,31716,29536,29536,29536,29536,24019,24019,24019,24019,-5327,-5327,-5327,-5327
 .short 27754,27754,27754,27754,-19242,-19242,-19242,-19242,11147,11147,11147,11147,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_pair_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_pair_factor:
 .short -147,-147,-147,-147,109,109,109,109,366,366,366,366,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-446,-446,-446,-446,-1339,-1339,-1339,-1339,1181,1181,1181,1181
 .short 484,484,484,484,864,864,864,864,-429,-429,-429,-429,177,177,177,177
 .short 874,874,874,874,-554,-554,-554,-554,11,11,11,11,1591,1591,1591,1591
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_p_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_p_pair_qinv:
 .short -19,-19,-19,-19,13422,13422,13422,13422,-32531,-32531,-32531,-32531,28834,28834,28834,28834
 .short 23526,23526,23526,23526,-10427,-10427,-10427,-10427,834,834,834,834,-739,-739,-739,-739
 .short 31716,31716,31716,31716,24019,24019,24019,24019,29536,29536,29536,29536,-5327,-5327,-5327,-5327
 .short 27754,27754,27754,27754,11147,11147,11147,11147,-19242,-19242,-19242,-19242,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_p_pair_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_p_pair_factor:
 .short -147,-147,-147,-147,366,366,366,366,109,109,109,109,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-1339,-1339,-1339,-1339,-446,-446,-446,-446,1181,1181,1181,1181
 .short 484,484,484,484,-429,-429,-429,-429,864,864,864,864,177,177,177,177
 .short 874,874,874,874,11,11,11,11,-554,-554,-554,-554,1591,1591,1591,1591
 .section .rodata.gtclean.ntt_m.tile4_fwd_s4_qpair02_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_qpair02_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 13422,13422,13422,13422,13422,13422,13422,13422,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,834,834,834,834,834,834,834,834
 .short -10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.ntt_m.tile4_fwd_s4_qpair02_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_qpair02_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,109,109,109,109,109,109,109,109
 .short 366,366,366,366,366,366,366,366,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-446,-446,-446,-446,-446,-446,-446,-446
 .short -1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_qpair02_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_qpair02_qinv:
 .short -19,-19,-19,-19,13422,13422,13422,13422,23526,23526,23526,23526,-10427,-10427,-10427,-10427
 .short -32531,-32531,-32531,-32531,28834,28834,28834,28834,834,834,834,834,-739,-739,-739,-739
 .short 31716,31716,31716,31716,24019,24019,24019,24019,27754,27754,27754,27754,11147,11147,11147,11147
 .short 29536,29536,29536,29536,-5327,-5327,-5327,-5327,-19242,-19242,-19242,-19242,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt_m.tile4_fwd_s5_qpair02_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_qpair02_factor:
 .short -147,-147,-147,-147,366,366,366,366,-794,-794,-794,-794,-1339,-1339,-1339,-1339
 .short 109,109,109,109,-1118,-1118,-1118,-1118,-446,-446,-446,-446,1181,1181,1181,1181
 .short 484,484,484,484,-429,-429,-429,-429,874,874,874,874,11,11,11,11
 .short 864,864,864,864,177,177,177,177,-554,-554,-554,-554,1591,1591,1591,1591
 .section .rodata.gtclean.ntt_m.tile4_inv_s1_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s1_pair_qinv:
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .section .rodata.gtclean.ntt_m.tile4_inv_s1_pair_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s1_pair_factor:
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .section .rodata.gtclean.ntt_m.tile4_q,"a",@progbits
.p2align 5
.Ltile4_q:
 .rept 16
 .short 3457
 .endr
 .section .rodata.gtclean.ntt_m.tile4_frontend_offsets,"a",@progbits
.p2align 5
.Ltile4_frontend_offsets:
 .short 0,264,512,8,256,520
 .short 528,24,272,536,16,280
 .short 288,552,32,296,544,40
 .short 48,312,560,56,304,568
 .short 576,72,320,584,64,328
 .short 336,600,80,344,592,88
 .short 96,360,608,104,352,616
 .short 624,120,368,632,112,376
 .short 384,648,128,392,640,136
 .short 144,408,656,152,400,664
 .short 672,168,416,680,160,424
 .short 432,696,176,440,688,184
 .short 192,456,704,200,448,712
 .short 720,216,464,728,208,472
 .short 480,744,224,488,736,232
 .short 240,504,752,248,496,760
 .section .rodata.gtclean.ntt_m.tile4_frontend_twist_qinv,"a",@progbits
.p2align 5
.Ltile4_frontend_twist_qinv:
 .short -19,-19,-19,-19,-17877,-17877,-17877,-17877,-19,-19,-19,-19,8190,8190,8190,8190
 .short 4872,4872,4872,4872,32759,32759,32759,32759,-28815,-28815,-28815,-28815,-20853,-20853,-20853,-20853
 .short 29782,29782,29782,29782,-30332,-30332,-30332,-30332,-16436,-16436,-16436,-16436,22521,22521,22521,22521
 .short -15166,-15166,-15166,-15166,8190,8190,8190,8190,1024,1024,1024,1024,5915,5915,5915,5915
 .short 23830,23830,23830,23830,-7583,-7583,-7583,-7583,30161,30161,30161,30161,11962,11962,11962,11962
 .short 16379,16379,16379,16379,-20853,-20853,-20853,-20853,-948,-948,-948,-948,16266,16266,16266,16266
 .short -10427,-10427,-10427,-10427,-1896,-1896,-1896,-1896,739,739,739,739,8284,8284,8284,8284
 .short 4095,4095,4095,4095,-5213,-5213,-5213,-5213,18142,18142,18142,18142,26844,26844,26844,26844
 .short -3791,-3791,-3791,-3791,2047,2047,2047,2047,-14351,-14351,-14351,-14351,-31943,-31943,-31943,-31943
 .short 1024,1024,1024,1024,-17687,-17687,-17687,-17687,-10389,-10389,-10389,-10389,31469,31469,31469,31469
 .short -948,-948,-948,-948,512,512,512,512,3355,3355,3355,3355,-24303,-24303,-24303,-24303
 .short 30161,30161,30161,30161,-474,-474,-474,-474,-28569,-28569,-28569,-28569,21005,21005,21005,21005
 .short 32531,32531,32531,32531,16512,16512,16512,16512,-28834,-28834,-28834,-28834,30010,30010,30010,30010
 .short 23924,23924,23924,23924,16266,16266,16266,16266,13346,13346,13346,13346,1668,1668,1668,1668
 .short -32512,-32512,-32512,-32512,11962,11962,11962,11962,4853,4853,4853,4853,607,607,607,607
 .short -26787,-26787,-26787,-26787,-28702,-28702,-28702,-28702,11943,11943,11943,11943,17877,17877,17877,17877
 .short -24512,-24512,-24512,-24512,19375,19375,19375,19375,-19488,-19488,-19488,-19488,30332,30332,30332,30332
 .short 8133,8133,8133,8133,20512,20512,20512,20512,76,76,76,76,-6844,-6844,-6844,-6844
 .short 10256,10256,10256,10256,-27924,-27924,-27924,-27924,8626,8626,8626,8626,9270,9270,9270,9270
 .short -14351,-14351,-14351,-14351,-27640,-27640,-27640,-27640,3791,3791,3791,3791,-14502,-14502,-14502,-14502
 .short 9687,9687,9687,9687,25593,25593,25593,25593,7337,7337,7337,7337,-23659,-23659,-23659,-23659
 .short 12796,12796,12796,12796,25858,25858,25858,25858,-7033,-7033,-7033,-7033,-4228,-4228,-4228,-4228
 .short 18806,18806,18806,18806,-26370,-26370,-26370,-26370,-26389,-26389,-26389,-26389,-3299,-3299,-3299,-3299
 .short -13820,-13820,-13820,-13820,9403,9403,9403,9403,-27469,-27469,-27469,-27469,4758,4758,4758,4758
 .short 4701,4701,4701,4701,-22976,-22976,-22976,-22976,-8720,-8720,-8720,-8720,31678,31678,31678,31678
 .short 12929,12929,12929,12929,2351,2351,2351,2351,2787,2787,2787,2787,-24228,-24228,-24228,-24228
 .short 19583,19583,19583,19583,6464,6464,6464,6464,-23981,-23981,-23981,-23981,-14768,-14768,-14768,-14768
 .short -29536,-29536,-29536,-29536,588,588,588,588,8265,8265,8265,8265,-31735,-31735,-31735,-31735
 .short -11488,-11488,-11488,-11488,-14768,-14768,-14768,-14768,-19412,-19412,-19412,-19412,-17498,-17498,-17498,-17498
 .short 1175,1175,1175,1175,-5744,-5744,-5744,-5744,22730,22730,22730,22730,11033,11033,11033,11033
 .short 29896,29896,29896,29896,-20076,-20076,-20076,-20076,12417,12417,12417,12417,-22920,-22920,-22920,-22920
 .short -32474,-32474,-32474,-32474,-17820,-17820,-17820,-17820,22389,22389,22389,22389,27375,27375,27375,27375
 .short 25384,25384,25384,25384,16531,16531,16531,16531,20057,20057,20057,20057,-13877,-13877,-13877,-13877
 .short 8265,8265,8265,8265,-4455,-4455,-4455,-4455,5327,5327,5327,5327,-7526,-7526,-7526,-7526
 .short 22730,22730,22730,22730,4133,4133,4133,4133,19811,19811,19811,19811,27052,27052,27052,27052
 .short -8910,-8910,-8910,-8910,-21403,-21403,-21403,-21403,31033,31033,31033,31033,-31868,-31868,-31868,-31868
 .short 22067,22067,22067,22067,-31735,-31735,-31735,-31735,7488,7488,7488,7488,-23640,-23640,-23640,-23640
 .short 30540,30540,30540,30540,11033,11033,11033,11033,-21194,-21194,-21194,-21194,-20512,-20512,-20512,-20512
 .short 2066,2066,2066,2066,-17498,-17498,-17498,-17498,4209,4209,4209,4209,16910,16910,16910,16910
 .short 24019,24019,24019,24019,-30010,-30010,-30010,-30010,-11147,-11147,-11147,-11147,22976,22976,22976,22976
 .short -15867,-15867,-15867,-15867,-20758,-20758,-20758,-20758,13820,13820,13820,13820,-6464,-6464,-6464,-6464
 .short 5517,5517,5517,5517,24834,24834,24834,24834,-18806,-18806,-18806,-18806,-2351,-2351,-2351,-2351
 .short 12417,12417,12417,12417,-21574,-21574,-21574,-21574,-29896,-29896,-29896,-29896,4455,4455,4455,4455
 .short 17763,17763,17763,17763,-26559,-26559,-26559,-26559,-22787,-22787,-22787,-22787,13536,13536,13536,13536
 .short 22389,22389,22389,22389,-23886,-23886,-23886,-23886,32474,32474,32474,32474,-30825,-30825,-30825,-30825
 .short -11943,-11943,-11943,-11943,9744,9744,9744,9744,-25232,-25232,-25232,-25232,21422,21422,21422,21422
 .short -10787,-10787,-10787,-10787,-5972,-5972,-5972,-5972,-14692,-14692,-14692,-14692,31621,31621,31621,31621
 .short 19488,19488,19488,19488,27375,27375,27375,27375,12531,12531,12531,12531,26142,26142,26142,26142
 .section .rodata.gtclean.ntt_m.tile4_frontend_wide_twist_qinv,"a",@progbits
.p2align 5
.Ltile4_frontend_wide_twist_qinv:
 .short -19,-19,-19,-19,-17877,-17877,-17877,-17877,-15166,-15166,-15166,-15166,8190,8190,8190,8190
 .short 4872,4872,4872,4872,32759,32759,32759,32759,23830,23830,23830,23830,-7583,-7583,-7583,-7583
 .short 29782,29782,29782,29782,-30332,-30332,-30332,-30332,16379,16379,16379,16379,-20853,-20853,-20853,-20853
 .short -19,-19,-19,-19,8190,8190,8190,8190,1024,1024,1024,1024,5915,5915,5915,5915
 .short -28815,-28815,-28815,-28815,-20853,-20853,-20853,-20853,30161,30161,30161,30161,11962,11962,11962,11962
 .short -16436,-16436,-16436,-16436,22521,22521,22521,22521,-948,-948,-948,-948,16266,16266,16266,16266
 .short -10427,-10427,-10427,-10427,-1896,-1896,-1896,-1896,1024,1024,1024,1024,-17687,-17687,-17687,-17687
 .short 4095,4095,4095,4095,-5213,-5213,-5213,-5213,-948,-948,-948,-948,512,512,512,512
 .short -3791,-3791,-3791,-3791,2047,2047,2047,2047,30161,30161,30161,30161,-474,-474,-474,-474
 .short 739,739,739,739,8284,8284,8284,8284,-10389,-10389,-10389,-10389,31469,31469,31469,31469
 .short 18142,18142,18142,18142,26844,26844,26844,26844,3355,3355,3355,3355,-24303,-24303,-24303,-24303
 .short -14351,-14351,-14351,-14351,-31943,-31943,-31943,-31943,-28569,-28569,-28569,-28569,21005,21005,21005,21005
 .short 32531,32531,32531,32531,16512,16512,16512,16512,-26787,-26787,-26787,-26787,-28702,-28702,-28702,-28702
 .short 23924,23924,23924,23924,16266,16266,16266,16266,-24512,-24512,-24512,-24512,19375,19375,19375,19375
 .short -32512,-32512,-32512,-32512,11962,11962,11962,11962,8133,8133,8133,8133,20512,20512,20512,20512
 .short -28834,-28834,-28834,-28834,30010,30010,30010,30010,11943,11943,11943,11943,17877,17877,17877,17877
 .short 13346,13346,13346,13346,1668,1668,1668,1668,-19488,-19488,-19488,-19488,30332,30332,30332,30332
 .short 4853,4853,4853,4853,607,607,607,607,76,76,76,76,-6844,-6844,-6844,-6844
 .short 10256,10256,10256,10256,-27924,-27924,-27924,-27924,12796,12796,12796,12796,25858,25858,25858,25858
 .short -14351,-14351,-14351,-14351,-27640,-27640,-27640,-27640,18806,18806,18806,18806,-26370,-26370,-26370,-26370
 .short 9687,9687,9687,9687,25593,25593,25593,25593,-13820,-13820,-13820,-13820,9403,9403,9403,9403
 .short 8626,8626,8626,8626,9270,9270,9270,9270,-7033,-7033,-7033,-7033,-4228,-4228,-4228,-4228
 .short 3791,3791,3791,3791,-14502,-14502,-14502,-14502,-26389,-26389,-26389,-26389,-3299,-3299,-3299,-3299
 .short 7337,7337,7337,7337,-23659,-23659,-23659,-23659,-27469,-27469,-27469,-27469,4758,4758,4758,4758
 .short 4701,4701,4701,4701,-22976,-22976,-22976,-22976,-29536,-29536,-29536,-29536,588,588,588,588
 .short 12929,12929,12929,12929,2351,2351,2351,2351,-11488,-11488,-11488,-11488,-14768,-14768,-14768,-14768
 .short 19583,19583,19583,19583,6464,6464,6464,6464,1175,1175,1175,1175,-5744,-5744,-5744,-5744
 .short -8720,-8720,-8720,-8720,31678,31678,31678,31678,8265,8265,8265,8265,-31735,-31735,-31735,-31735
 .short 2787,2787,2787,2787,-24228,-24228,-24228,-24228,-19412,-19412,-19412,-19412,-17498,-17498,-17498,-17498
 .short -23981,-23981,-23981,-23981,-14768,-14768,-14768,-14768,22730,22730,22730,22730,11033,11033,11033,11033
 .short 29896,29896,29896,29896,-20076,-20076,-20076,-20076,8265,8265,8265,8265,-4455,-4455,-4455,-4455
 .short -32474,-32474,-32474,-32474,-17820,-17820,-17820,-17820,22730,22730,22730,22730,4133,4133,4133,4133
 .short 25384,25384,25384,25384,16531,16531,16531,16531,-8910,-8910,-8910,-8910,-21403,-21403,-21403,-21403
 .short 12417,12417,12417,12417,-22920,-22920,-22920,-22920,5327,5327,5327,5327,-7526,-7526,-7526,-7526
 .short 22389,22389,22389,22389,27375,27375,27375,27375,19811,19811,19811,19811,27052,27052,27052,27052
 .short 20057,20057,20057,20057,-13877,-13877,-13877,-13877,31033,31033,31033,31033,-31868,-31868,-31868,-31868
 .short 22067,22067,22067,22067,-31735,-31735,-31735,-31735,24019,24019,24019,24019,-30010,-30010,-30010,-30010
 .short 30540,30540,30540,30540,11033,11033,11033,11033,-15867,-15867,-15867,-15867,-20758,-20758,-20758,-20758
 .short 2066,2066,2066,2066,-17498,-17498,-17498,-17498,5517,5517,5517,5517,24834,24834,24834,24834
 .short 7488,7488,7488,7488,-23640,-23640,-23640,-23640,-11147,-11147,-11147,-11147,22976,22976,22976,22976
 .short -21194,-21194,-21194,-21194,-20512,-20512,-20512,-20512,13820,13820,13820,13820,-6464,-6464,-6464,-6464
 .short 4209,4209,4209,4209,16910,16910,16910,16910,-18806,-18806,-18806,-18806,-2351,-2351,-2351,-2351
 .short 12417,12417,12417,12417,-21574,-21574,-21574,-21574,-11943,-11943,-11943,-11943,9744,9744,9744,9744
 .short 17763,17763,17763,17763,-26559,-26559,-26559,-26559,-10787,-10787,-10787,-10787,-5972,-5972,-5972,-5972
 .short 22389,22389,22389,22389,-23886,-23886,-23886,-23886,19488,19488,19488,19488,27375,27375,27375,27375
 .short -29896,-29896,-29896,-29896,4455,4455,4455,4455,-25232,-25232,-25232,-25232,21422,21422,21422,21422
 .short -22787,-22787,-22787,-22787,13536,13536,13536,13536,-14692,-14692,-14692,-14692,31621,31621,31621,31621
 .short 32474,32474,32474,32474,-30825,-30825,-30825,-30825,12531,12531,12531,12531,26142,26142,26142,26142
 .section .rodata.gtclean.ntt_m.tile4_frontend_twist_factor,"a",@progbits
.p2align 5
.Ltile4_frontend_twist_factor:
 .short -147,-147,-147,-147,-341,-341,-341,-341,-147,-147,-147,-147,1278,1278,1278,1278
 .short -248,-248,-248,-248,1655,1655,1655,1655,1265,1265,1265,1265,779,779,779,779
 .short -682,-682,-682,-682,-124,-124,-124,-124,460,460,460,460,-1671,-1671,-1671,-1671
 .short -62,-62,-62,-62,1278,1278,1278,1278,1024,1024,1024,1024,923,923,923,923
 .short 1558,1558,1558,1558,-31,-31,-31,-31,-1199,-1199,-1199,-1199,-582,-582,-582,-582
 .short -901,-901,-901,-901,779,779,779,779,-436,-436,-436,-436,1674,1674,1674,1674
 .short -1339,-1339,-1339,-1339,-872,-872,-872,-872,-1181,-1181,-1181,-1181,-1444,-1444,-1444,-1444
 .short 639,639,639,639,1059,1059,1059,1059,-1058,-1058,-1058,-1058,732,732,732,732
 .short 1713,1713,1713,1713,-1409,-1409,-1409,-1409,-655,-655,-655,-655,1209,1209,1209,1209
 .short 1024,1024,1024,1024,1129,1129,1129,1129,-1045,-1045,-1045,-1045,-1427,-1427,-1427,-1427
 .short -436,-436,-436,-436,512,512,512,512,-1637,-1637,-1637,-1637,1681,1681,1681,1681
 .short -1199,-1199,-1199,-1199,-218,-218,-218,-218,-281,-281,-281,-281,397,397,397,397
 .short -109,-109,-109,-109,128,128,128,128,1118,1118,1118,1118,1082,1082,1082,1082
 .short -1164,-1164,-1164,-1164,1674,1674,1674,1674,-222,-222,-222,-222,-892,-892,-892,-892
 .short 256,256,256,256,-582,-582,-582,-582,-395,-395,-395,-395,1247,1247,1247,1247
 .short -291,-291,-291,-291,-1310,-1310,-1310,-1310,-729,-729,-729,-729,341,341,341,341
 .short 64,64,64,64,1583,1583,1583,1583,992,992,992,992,124,124,124,124
 .short 837,837,837,837,32,32,32,32,588,588,588,588,-1212,-1212,-1212,-1212
 .short 16,16,16,16,1260,1260,1260,1260,1202,1202,1202,1202,-714,-714,-714,-714
 .short -655,-655,-655,-655,8,8,8,8,-1713,-1713,-1713,-1713,1626,1626,1626,1626
 .short -937,-937,-937,-937,1401,1401,1401,1401,1577,1577,1577,1577,-235,-235,-235,-235
 .short -1028,-1028,-1028,-1028,2,2,2,2,775,775,775,775,-1668,-1668,-1668,-1668
 .short 630,630,630,630,-514,-514,-514,-514,-661,-661,-661,-661,-1379,-1379,-1379,-1379
 .short 4,4,4,4,315,315,315,315,1331,1331,1331,1331,-1130,-1130,-1130,-1130
 .short -1571,-1571,-1571,-1571,1600,1600,1600,1600,1520,1520,1520,1520,190,190,190,190
 .short 1,1,1,1,943,943,943,943,867,867,867,867,-1188,-1188,-1188,-1188
 .short -257,-257,-257,-257,-1728,-1728,-1728,-1728,723,723,723,723,-432,-432,-432,-432
 .short -864,-864,-864,-864,1100,1100,1100,1100,-1591,-1591,-1591,-1591,-631,-631,-631,-631
 .short 800,800,800,800,-432,-432,-432,-432,1580,1580,1580,1580,-858,-858,-858,-858
 .short -1257,-1257,-1257,-1257,400,400,400,400,-54,-54,-54,-54,-871,-871,-871,-871
 .short 200,200,200,200,-108,-108,-108,-108,-511,-511,-511,-511,-1416,-1416,-1416,-1416
 .short 550,550,550,550,100,100,100,100,757,757,757,757,1391,1391,1391,1391
 .short -216,-216,-216,-216,275,275,275,275,-39,-39,-39,-39,-437,-437,-437,-437
 .short -1591,-1591,-1591,-1591,25,25,25,25,-177,-177,-177,-177,410,410,410,410
 .short -54,-54,-54,-54,933,933,933,933,1507,1507,1507,1507,-1108,-1108,-1108,-1108
 .short 50,50,50,50,-27,-27,-27,-27,-1351,-1351,-1351,-1351,-1660,-1660,-1660,-1660
 .short 1715,1715,1715,1715,-631,-631,-631,-631,-704,-704,-704,-704,-88,-88,-88,-88
 .short -1716,-1716,-1716,-1716,-871,-871,-871,-871,1590,1590,1590,1590,-32,-32,-32,-32
 .short -1262,-1262,-1262,-1262,-858,-858,-858,-858,1521,1521,1521,1521,-242,-242,-242,-242
 .short -429,-429,-429,-429,-1082,-1082,-1082,-1082,-11,-11,-11,-11,-1600,-1600,-1600,-1600
 .short 1413,1413,1413,1413,1514,1514,1514,1514,-4,-4,-4,-4,1728,1728,1728,1728
 .short 1293,1293,1293,1293,-1022,-1022,-1022,-1022,-630,-630,-630,-630,-943,-943,-943,-943
 .short -511,-511,-511,-511,-1350,-1350,-1350,-1350,-200,-200,-200,-200,-25,-25,-25,-25
 .short -541,-541,-541,-541,1473,1473,1473,1473,-387,-387,-387,-387,1248,1248,1248,1248
 .short 757,757,757,757,1458,1458,1458,1458,-550,-550,-550,-550,-489,-489,-489,-489
 .short 729,729,729,729,-496,-496,-496,-496,1392,1392,1392,1392,174,174,174,174
 .short -675,-675,-675,-675,-1364,-1364,-1364,-1364,156,156,156,156,-251,-251,-251,-251
 .short -992,-992,-992,-992,1391,1391,1391,1391,371,371,371,371,-1250,-1250,-1250,-1250
 .section .rodata.gtclean.ntt_m.tile4_frontend_wide_twist_factor,"a",@progbits
.p2align 5
.Ltile4_frontend_wide_twist_factor:
 .short -147,-147,-147,-147,-341,-341,-341,-341,-62,-62,-62,-62,1278,1278,1278,1278
 .short -248,-248,-248,-248,1655,1655,1655,1655,1558,1558,1558,1558,-31,-31,-31,-31
 .short -682,-682,-682,-682,-124,-124,-124,-124,-901,-901,-901,-901,779,779,779,779
 .short -147,-147,-147,-147,1278,1278,1278,1278,1024,1024,1024,1024,923,923,923,923
 .short 1265,1265,1265,1265,779,779,779,779,-1199,-1199,-1199,-1199,-582,-582,-582,-582
 .short 460,460,460,460,-1671,-1671,-1671,-1671,-436,-436,-436,-436,1674,1674,1674,1674
 .short -1339,-1339,-1339,-1339,-872,-872,-872,-872,1024,1024,1024,1024,1129,1129,1129,1129
 .short 639,639,639,639,1059,1059,1059,1059,-436,-436,-436,-436,512,512,512,512
 .short 1713,1713,1713,1713,-1409,-1409,-1409,-1409,-1199,-1199,-1199,-1199,-218,-218,-218,-218
 .short -1181,-1181,-1181,-1181,-1444,-1444,-1444,-1444,-1045,-1045,-1045,-1045,-1427,-1427,-1427,-1427
 .short -1058,-1058,-1058,-1058,732,732,732,732,-1637,-1637,-1637,-1637,1681,1681,1681,1681
 .short -655,-655,-655,-655,1209,1209,1209,1209,-281,-281,-281,-281,397,397,397,397
 .short -109,-109,-109,-109,128,128,128,128,-291,-291,-291,-291,-1310,-1310,-1310,-1310
 .short -1164,-1164,-1164,-1164,1674,1674,1674,1674,64,64,64,64,1583,1583,1583,1583
 .short 256,256,256,256,-582,-582,-582,-582,837,837,837,837,32,32,32,32
 .short 1118,1118,1118,1118,1082,1082,1082,1082,-729,-729,-729,-729,341,341,341,341
 .short -222,-222,-222,-222,-892,-892,-892,-892,992,992,992,992,124,124,124,124
 .short -395,-395,-395,-395,1247,1247,1247,1247,588,588,588,588,-1212,-1212,-1212,-1212
 .short 16,16,16,16,1260,1260,1260,1260,-1028,-1028,-1028,-1028,2,2,2,2
 .short -655,-655,-655,-655,8,8,8,8,630,630,630,630,-514,-514,-514,-514
 .short -937,-937,-937,-937,1401,1401,1401,1401,4,4,4,4,315,315,315,315
 .short 1202,1202,1202,1202,-714,-714,-714,-714,775,775,775,775,-1668,-1668,-1668,-1668
 .short -1713,-1713,-1713,-1713,1626,1626,1626,1626,-661,-661,-661,-661,-1379,-1379,-1379,-1379
 .short 1577,1577,1577,1577,-235,-235,-235,-235,1331,1331,1331,1331,-1130,-1130,-1130,-1130
 .short -1571,-1571,-1571,-1571,1600,1600,1600,1600,-864,-864,-864,-864,1100,1100,1100,1100
 .short 1,1,1,1,943,943,943,943,800,800,800,800,-432,-432,-432,-432
 .short -257,-257,-257,-257,-1728,-1728,-1728,-1728,-1257,-1257,-1257,-1257,400,400,400,400
 .short 1520,1520,1520,1520,190,190,190,190,-1591,-1591,-1591,-1591,-631,-631,-631,-631
 .short 867,867,867,867,-1188,-1188,-1188,-1188,1580,1580,1580,1580,-858,-858,-858,-858
 .short 723,723,723,723,-432,-432,-432,-432,-54,-54,-54,-54,-871,-871,-871,-871
 .short 200,200,200,200,-108,-108,-108,-108,-1591,-1591,-1591,-1591,25,25,25,25
 .short 550,550,550,550,100,100,100,100,-54,-54,-54,-54,933,933,933,933
 .short -216,-216,-216,-216,275,275,275,275,50,50,50,50,-27,-27,-27,-27
 .short -511,-511,-511,-511,-1416,-1416,-1416,-1416,-177,-177,-177,-177,410,410,410,410
 .short 757,757,757,757,1391,1391,1391,1391,1507,1507,1507,1507,-1108,-1108,-1108,-1108
 .short -39,-39,-39,-39,-437,-437,-437,-437,-1351,-1351,-1351,-1351,-1660,-1660,-1660,-1660
 .short 1715,1715,1715,1715,-631,-631,-631,-631,-429,-429,-429,-429,-1082,-1082,-1082,-1082
 .short -1716,-1716,-1716,-1716,-871,-871,-871,-871,1413,1413,1413,1413,1514,1514,1514,1514
 .short -1262,-1262,-1262,-1262,-858,-858,-858,-858,1293,1293,1293,1293,-1022,-1022,-1022,-1022
 .short -704,-704,-704,-704,-88,-88,-88,-88,-11,-11,-11,-11,-1600,-1600,-1600,-1600
 .short 1590,1590,1590,1590,-32,-32,-32,-32,-4,-4,-4,-4,1728,1728,1728,1728
 .short 1521,1521,1521,1521,-242,-242,-242,-242,-630,-630,-630,-630,-943,-943,-943,-943
 .short -511,-511,-511,-511,-1350,-1350,-1350,-1350,729,729,729,729,-496,-496,-496,-496
 .short -541,-541,-541,-541,1473,1473,1473,1473,-675,-675,-675,-675,-1364,-1364,-1364,-1364
 .short 757,757,757,757,1458,1458,1458,1458,-992,-992,-992,-992,1391,1391,1391,1391
 .short -200,-200,-200,-200,-25,-25,-25,-25,1392,1392,1392,1392,174,174,174,174
 .short -387,-387,-387,-387,1248,1248,1248,1248,156,156,156,156,-251,-251,-251,-251
 .short -550,-550,-550,-550,-489,-489,-489,-489,371,371,371,371,-1250,-1250,-1250,-1250
 .section .rodata.gtclean.ntt_m.tile4_frontend_zeta_top_qinv,"a",@progbits
.p2align 5
.Ltile4_frontend_zeta_top_qinv:
 .rept 16
 .short 13687
 .endr
 .section .rodata.gtclean.ntt_m.tile4_frontend_zeta_top_factor,"a",@progbits
.p2align 5
.Ltile4_frontend_zeta_top_factor:
 .rept 16
 .short -1033
 .endr
 .section .rodata.gtclean.ntt_m.tile4_frontend_omega3_qinv,"a",@progbits
.p2align 5
.Ltile4_frontend_omega3_qinv:
 .rept 16
 .short 13706
 .endr
 .section .rodata.gtclean.ntt_m.tile4_frontend_omega3_factor,"a",@progbits
.p2align 5
.Ltile4_frontend_omega3_factor:
 .rept 16
 .short -886
 .endr
 .section .rodata.gtclean.ntt_m.tile4_frontend_zeta_top_raw,"a",@progbits
.p2align 5
.Ltile4_frontend_zeta_top_raw:
 .rept 16
 .short -722
 .endr
 .section .note.GNU-stack,"",@progbits

.macro GT103_STORE_QL2 v0,v1,v2,v3,outoff
 vmovdqu \v0, \outoff+0(%rdi)
 vmovdqu \v2, \outoff+32(%rdi)
 vmovdqu \v1, \outoff+64(%rdi)
 vmovdqu \v3, \outoff+96(%rdi)
.endm
.section .ql2_tail.1_ntt,"ax",@progbits
FR_TRANSPOSE_CUT_FORWARD_FUNCTION ntruplus768_ntt_ql2_avx2,GT103_STORE_QL2
