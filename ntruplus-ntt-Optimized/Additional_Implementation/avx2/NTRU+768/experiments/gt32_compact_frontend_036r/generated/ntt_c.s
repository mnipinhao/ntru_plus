
/* ---- selected production component ---- */
.text
.macro MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
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
.macro FWD_S2_CENTER_ID2 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
 vpmulhrsw .Ltile4_fwd_center10(%rip), \h0, %ymm8
 vpmulhrsw .Ltile4_fwd_center10(%rip), \h1, %ymm9
 vpmullw %ymm15, %ymm8, %ymm8
 vpmullw %ymm15, %ymm9, %ymm9
 vpsubw %ymm8, \h0, \h0
 vpsubw %ymm9, \h1, \h1
 vpmullw \qinv+64(%rip), \h2, %ymm10
 vpmullw \qinv+96(%rip), \h3, %ymm11
 vpmulhw \factor+64(%rip), \h2, \h2
 vpmulhw \factor+96(%rip), \h3, \h3
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm11, %ymm11
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
.macro RAW_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3
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
.macro MONT_LOCAL_HALF value,qinv,factor,offset
 vperm2i128 $0x00, \value, \value, %ymm8
 vperm2i128 $0x11, \value, \value, %ymm9
 vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vperm2i128 $0x20, %ymm10, %ymm8, \value
.endm
.macro MONT_LOCAL_QWORD value,qinv,factor,offset
 vpshufd $0x44, \value, %ymm8
 vpshufd $0xee, \value, %ymm9
 vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vpblendd $0xcc, %ymm10, %ymm8, \value
.endm
.macro MONT_LOCAL_HALF_PAIR v0,v1,qinv,factor,offset
 vperm2i128 $0x20, \v1, \v0, %ymm8
 vperm2i128 $0x31, \v1, \v0, %ymm9
 vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vperm2i128 $0x20, %ymm10, %ymm8, \v0
 vperm2i128 $0x31, %ymm10, %ymm8, \v1
.endm
.macro MONT_LOCAL_QWORD_PAIR v0,v1,qinv,factor,offset
 vpunpcklqdq \v1, \v0, %ymm8
 vpunpckhqdq \v1, \v0, %ymm9
 vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
 vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vpunpcklqdq %ymm10, %ymm8, \v0
 vpunpckhqdq %ymm10, %ymm8, \v1
.endm
.macro MONT_LOCAL_HALF3 v0,v1,v2,qinv,factor,o0,o1,o2
 vperm2i128 $0x00, \v0, \v0, %ymm8
 vperm2i128 $0x00, \v1, \v1, %ymm9
 vperm2i128 $0x00, \v2, \v2, %ymm10
 vperm2i128 $0x11, \v0, \v0, \v0
 vperm2i128 $0x11, \v1, \v1, \v1
 vperm2i128 $0x11, \v2, \v2, \v2
 vpmullw \qinv+\o0(%rip), \v0, %ymm11
 vpmullw \qinv+\o1(%rip), \v1, %ymm12
 vpmullw \qinv+\o2(%rip), \v2, %ymm13
 vpmulhw \factor+\o0(%rip), \v0, \v0
 vpmulhw \factor+\o1(%rip), \v1, \v1
 vpmulhw \factor+\o2(%rip), \v2, \v2
 vpmulhw %ymm15, %ymm11, %ymm11
 vpmulhw %ymm15, %ymm12, %ymm12
 vpmulhw %ymm15, %ymm13, %ymm13
 vpsubw %ymm11, \v0, \v0
 vpsubw %ymm12, \v1, \v1
 vpsubw %ymm13, \v2, \v2
 vpsubw \v0, %ymm8, %ymm11
 vpsubw \v1, %ymm9, %ymm12
 vpsubw \v2, %ymm10, %ymm13
 vpaddw \v0, %ymm8, %ymm8
 vpaddw \v1, %ymm9, %ymm9
 vpaddw \v2, %ymm10, %ymm10
 vperm2i128 $0x20, %ymm11, %ymm8, \v0
 vperm2i128 $0x20, %ymm12, %ymm9, \v1
 vperm2i128 $0x20, %ymm13, %ymm10, \v2
.endm
.macro MONT_LOCAL_HALF2 v0,v1,qinv,factor,o0,o1
 vperm2i128 $0x00, \v0, \v0, %ymm8
 vperm2i128 $0x00, \v1, \v1, %ymm9
 vperm2i128 $0x11, \v0, \v0, \v0
 vperm2i128 $0x11, \v1, \v1, \v1
 vpmullw \qinv+\o0(%rip), \v0, %ymm11
 vpmullw \qinv+\o1(%rip), \v1, %ymm12
 vpmulhw \factor+\o0(%rip), \v0, \v0
 vpmulhw \factor+\o1(%rip), \v1, \v1
 vpmulhw %ymm15, %ymm11, %ymm11
 vpmulhw %ymm15, %ymm12, %ymm12
 vpsubw %ymm11, \v0, \v0
 vpsubw %ymm12, \v1, \v1
 vpsubw \v0, %ymm8, %ymm11
 vpsubw \v1, %ymm9, %ymm12
 vpaddw \v0, %ymm8, %ymm8
 vpaddw \v1, %ymm9, %ymm9
 vperm2i128 $0x20, %ymm11, %ymm8, \v0
 vperm2i128 $0x20, %ymm12, %ymm9, \v1
.endm
.macro MONT_LOCAL_QWORD3 v0,v1,v2,qinv,factor,o0,o1,o2
 vpshufd $0x44, \v0, %ymm8
 vpshufd $0x44, \v1, %ymm9
 vpshufd $0x44, \v2, %ymm10
 vpshufd $0xee, \v0, \v0
 vpshufd $0xee, \v1, \v1
 vpshufd $0xee, \v2, \v2
 vpmullw \qinv+\o0(%rip), \v0, %ymm11
 vpmullw \qinv+\o1(%rip), \v1, %ymm12
 vpmullw \qinv+\o2(%rip), \v2, %ymm13
 vpmulhw \factor+\o0(%rip), \v0, \v0
 vpmulhw \factor+\o1(%rip), \v1, \v1
 vpmulhw \factor+\o2(%rip), \v2, \v2
 vpmulhw %ymm15, %ymm11, %ymm11
 vpmulhw %ymm15, %ymm12, %ymm12
 vpmulhw %ymm15, %ymm13, %ymm13
 vpsubw %ymm11, \v0, \v0
 vpsubw %ymm12, \v1, \v1
 vpsubw %ymm13, \v2, \v2
 vpsubw \v0, %ymm8, %ymm11
 vpsubw \v1, %ymm9, %ymm12
 vpsubw \v2, %ymm10, %ymm13
 vpaddw \v0, %ymm8, %ymm8
 vpaddw \v1, %ymm9, %ymm9
 vpaddw \v2, %ymm10, %ymm10
 vpblendd $0xcc, %ymm11, %ymm8, \v0
 vpblendd $0xcc, %ymm12, %ymm9, \v1
 vpblendd $0xcc, %ymm13, %ymm10, \v2
.endm
.macro MONT_LOCAL_QWORD2 v0,v1,qinv,factor,o0,o1
 vpshufd $0x44, \v0, %ymm8
 vpshufd $0x44, \v1, %ymm9
 vpshufd $0xee, \v0, \v0
 vpshufd $0xee, \v1, \v1
 vpmullw \qinv+\o0(%rip), \v0, %ymm11
 vpmullw \qinv+\o1(%rip), \v1, %ymm12
 vpmulhw \factor+\o0(%rip), \v0, \v0
 vpmulhw \factor+\o1(%rip), \v1, \v1
 vpmulhw %ymm15, %ymm11, %ymm11
 vpmulhw %ymm15, %ymm12, %ymm12
 vpsubw %ymm11, \v0, \v0
 vpsubw %ymm12, \v1, \v1
 vpsubw \v0, %ymm8, %ymm11
 vpsubw \v1, %ymm9, %ymm12
 vpaddw \v0, %ymm8, %ymm8
 vpaddw \v1, %ymm9, %ymm9
 vpblendd $0xcc, %ymm11, %ymm8, \v0
 vpblendd $0xcc, %ymm12, %ymm9, \v1
.endm
.macro RAW_LOCAL_QWORD value
 vpshufd $0x44, \value, %ymm8
 vpshufd $0xee, \value, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vpblendd $0xcc, %ymm10, %ymm8, \value
.endm
.macro RAW_LOCAL_QWORD_PAIR v0,v1
 vpunpcklqdq \v1, \v0, %ymm8
 vpunpckhqdq \v1, \v0, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vpunpcklqdq %ymm10, %ymm8, \v0
 vpunpckhqdq %ymm10, %ymm8, \v1
.endm
.macro LOAD_TILE
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vmovdqu 128(%rsi), %ymm4
 vmovdqu 160(%rsi), %ymm5
 vmovdqu 192(%rsi), %ymm6
 vmovdqu 224(%rsi), %ymm7
.endm
.macro LOAD_TILE_SPLIT
 vmovdqu 0(%rsi), %xmm0
 vinserti128 $1, 16(%rsi), %ymm0, %ymm0
 vmovdqu 32(%rsi), %xmm1
 vinserti128 $1, 48(%rsi), %ymm1, %ymm1
 vmovdqu 64(%rsi), %xmm2
 vinserti128 $1, 80(%rsi), %ymm2, %ymm2
 vmovdqu 96(%rsi), %xmm3
 vinserti128 $1, 112(%rsi), %ymm3, %ymm3
 vmovdqu 128(%rsi), %xmm4
 vinserti128 $1, 144(%rsi), %ymm4, %ymm4
 vmovdqu 160(%rsi), %xmm5
 vinserti128 $1, 176(%rsi), %ymm5, %ymm5
 vmovdqu 192(%rsi), %xmm6
 vinserti128 $1, 208(%rsi), %ymm6, %ymm6
 vmovdqu 224(%rsi), %xmm7
 vinserti128 $1, 240(%rsi), %ymm7, %ymm7
.endm
.macro STORE_TILE
 vmovdqu %ymm0, 0(%rdi)
 vmovdqu %ymm1, 32(%rdi)
 vmovdqu %ymm2, 64(%rdi)
 vmovdqu %ymm3, 96(%rdi)
 vmovdqu %ymm4, 128(%rdi)
 vmovdqu %ymm5, 160(%rdi)
 vmovdqu %ymm6, 192(%rdi)
 vmovdqu %ymm7, 224(%rdi)
.endm
.macro FRONTEND_N3 target,source_offset,twist_offset
 movzwl \source_offset(%rax), %r8d
 movzwl \source_offset+2(%rax), %r9d
 vmovq (%rsi,%r8), %xmm3
 vmovq (%rsi,%r9), %xmm4
 vpunpcklqdq %xmm4, %xmm3, %xmm3
 vmovq 768(%rsi,%r8), %xmm5
 vmovq 768(%rsi,%r9), %xmm4
 vpunpcklqdq %xmm4, %xmm5, %xmm5
 vmovdqa %xmm5, %xmm7
 vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %xmm5, %xmm4
 vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %xmm5, %xmm5
 vpmulhw %xmm15, %xmm4, %xmm4
 vpsubw %xmm4, %xmm5, %xmm5
 vpaddw %xmm5, %xmm3, %xmm6
 vpaddw %xmm7, %xmm3, %xmm3
 vpsubw %xmm5, %xmm3, %xmm3
 vinserti128 $1, %xmm3, %ymm6, %ymm6
 vpmullw \twist_offset(%rdx), %ymm6, %ymm7
 vpmulhw \twist_offset(%rcx), %ymm6, \target
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, \target, \target
.endm
.macro FRONTEND_LOAD_PAIR low,high,original_high,source_offset
 movzwl \source_offset(%rax), %r8d
 movzwl \source_offset+2(%rax), %r9d
 vmovq (%rsi,%r8), \low
 vmovq (%rsi,%r9), %xmm12
 vpunpcklqdq %xmm12, \low, \low
 vmovq 768(%rsi,%r8), \high
 vmovq 768(%rsi,%r9), %xmm12
 vpunpcklqdq %xmm12, \high, \high
 vmovdqa \high, \original_high
.endm
.macro FORWARD_BODY
 LOAD_TILE
 RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
 MONT_LOCAL_HALF3 %ymm0,%ymm1,%ymm2, .Ltile4_fwd_s4_qinv,.Ltile4_fwd_s4_factor, 0,32,64
 MONT_LOCAL_HALF3 %ymm3,%ymm4,%ymm5, .Ltile4_fwd_s4_qinv,.Ltile4_fwd_s4_factor, 96,128,160
 MONT_LOCAL_HALF2 %ymm6,%ymm7, .Ltile4_fwd_s4_qinv,.Ltile4_fwd_s4_factor, 192,224
 MONT_LOCAL_QWORD3 %ymm0,%ymm1,%ymm2, .Ltile4_fwd_s5_qinv,.Ltile4_fwd_s5_factor, 0,32,64
 MONT_LOCAL_QWORD3 %ymm3,%ymm4,%ymm5, .Ltile4_fwd_s5_qinv,.Ltile4_fwd_s5_factor, 96,128,160
 MONT_LOCAL_QWORD2 %ymm6,%ymm7, .Ltile4_fwd_s5_qinv,.Ltile4_fwd_s5_factor, 192,224
 STORE_TILE
.endm
.macro FORWARD_BODY_SERIAL
 LOAD_TILE
 RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
 MONT_LOCAL_HALF %ymm0, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 0
 MONT_LOCAL_HALF %ymm1, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 32
 MONT_LOCAL_HALF %ymm2, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 64
 MONT_LOCAL_HALF %ymm3, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 96
 MONT_LOCAL_HALF %ymm4, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 128
 MONT_LOCAL_HALF %ymm5, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 160
 MONT_LOCAL_HALF %ymm6, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 192
 MONT_LOCAL_HALF %ymm7, .Ltile4_fwd_s4_qinv, .Ltile4_fwd_s4_factor, 224
 MONT_LOCAL_QWORD %ymm0, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 0
 MONT_LOCAL_QWORD %ymm1, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 32
 MONT_LOCAL_QWORD %ymm2, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 64
 MONT_LOCAL_QWORD %ymm3, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 96
 MONT_LOCAL_QWORD %ymm4, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 128
 MONT_LOCAL_QWORD %ymm5, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 160
 MONT_LOCAL_QWORD %ymm6, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 192
 MONT_LOCAL_QWORD %ymm7, .Ltile4_fwd_s5_qinv, .Ltile4_fwd_s5_factor, 224
 STORE_TILE
.endm
.macro FORWARD_BODY_PAIR_CORE
 RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
 MONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 0
 MONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 32
 MONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 64
 MONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 96
 MONT_LOCAL_QWORD_PAIR %ymm0,%ymm1, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 0
 MONT_LOCAL_QWORD_PAIR %ymm2,%ymm3, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 32
 MONT_LOCAL_QWORD_PAIR %ymm4,%ymm5, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 64
 MONT_LOCAL_QWORD_PAIR %ymm6,%ymm7, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 96
.endm
.macro FORWARD_BODY_PAIR
 LOAD_TILE
 FORWARD_BODY_PAIR_CORE
 STORE_TILE
.endm
.macro FORWARD_BODY_PAIR_ID_CENTER
 LOAD_TILE
 RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 FWD_S2_CENTER_ID2 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
 MONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 0
 MONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 32
 MONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 64
 MONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 96
 MONT_LOCAL_QWORD_PAIR %ymm0,%ymm1, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 0
 MONT_LOCAL_QWORD_PAIR %ymm2,%ymm3, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 32
 MONT_LOCAL_QWORD_PAIR %ymm4,%ymm5, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 64
 MONT_LOCAL_QWORD_PAIR %ymm6,%ymm7, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 96
 STORE_TILE
.endm
.macro FORWARD_BODY_PAIR_SPLITLOAD
 LOAD_TILE_SPLIT
 RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
 MONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 0
 MONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 32
 MONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 64
 MONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 96
 MONT_LOCAL_QWORD_PAIR %ymm0,%ymm1, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 0
 MONT_LOCAL_QWORD_PAIR %ymm2,%ymm3, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 32
 MONT_LOCAL_QWORD_PAIR %ymm4,%ymm5, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 64
 MONT_LOCAL_QWORD_PAIR %ymm6,%ymm7, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 96
 STORE_TILE
.endm
.macro INVERSE_BODY
 LOAD_TILE
 RAW_LOCAL_QWORD %ymm0
 RAW_LOCAL_QWORD %ymm1
 RAW_LOCAL_QWORD %ymm2
 RAW_LOCAL_QWORD %ymm3
 RAW_LOCAL_QWORD %ymm4
 RAW_LOCAL_QWORD %ymm5
 RAW_LOCAL_QWORD %ymm6
 RAW_LOCAL_QWORD %ymm7
 MONT_LOCAL_HALF %ymm0, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 0
 MONT_LOCAL_HALF %ymm1, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 32
 MONT_LOCAL_HALF %ymm2, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 64
 MONT_LOCAL_HALF %ymm3, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 96
 MONT_LOCAL_HALF %ymm4, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 128
 MONT_LOCAL_HALF %ymm5, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 160
 MONT_LOCAL_HALF %ymm6, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 192
 MONT_LOCAL_HALF %ymm7, .Ltile4_inv_s1_qinv, .Ltile4_inv_s1_factor, 224
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_inv_s2_qinv, .Ltile4_inv_s2_factor
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_inv_s3_qinv, .Ltile4_inv_s3_factor
 MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, .Ltile4_inv_s4_qinv, .Ltile4_inv_s4_factor
 STORE_TILE
.endm
.macro INVERSE_BODY_PAIR
 LOAD_TILE
 RAW_LOCAL_QWORD_PAIR %ymm0,%ymm1
 RAW_LOCAL_QWORD_PAIR %ymm2,%ymm3
 RAW_LOCAL_QWORD_PAIR %ymm4,%ymm5
 RAW_LOCAL_QWORD_PAIR %ymm6,%ymm7
 MONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 0
 MONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 32
 MONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 64
 MONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 96
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_inv_s2_qinv, .Ltile4_inv_s2_factor
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_inv_s3_qinv, .Ltile4_inv_s3_factor
 MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, .Ltile4_inv_s4_qinv, .Ltile4_inv_s4_factor
 STORE_TILE
.endm
.macro CENTER_I1_VECTOR value,tmp
 vpmulhrsw .Ltile4_i1_center10(%rip), %\value, %\tmp
 vpmullw %ymm15, %\tmp, %\tmp
 vpsubw %\tmp, %\value, %\value
.endm
.macro CENTER_I1_LOW_ARMS4
 vpmulhrsw %ymm14, %ymm0, %ymm8
 vpmulhrsw %ymm14, %ymm1, %ymm9
 vpmulhrsw %ymm14, %ymm4, %ymm10
 vpmulhrsw %ymm14, %ymm5, %ymm11
 vpmullw %ymm15, %ymm8, %ymm8
 vpmullw %ymm15, %ymm9, %ymm9
 vpmullw %ymm15, %ymm10, %ymm10
 vpmullw %ymm15, %ymm11, %ymm11
 vpsubw %ymm8, %ymm0, %ymm0
 vpsubw %ymm9, %ymm1, %ymm1
 vpsubw %ymm10, %ymm4, %ymm4
 vpsubw %ymm11, %ymm5, %ymm5
.endm
.macro INVERSE_BODY_PAIR_SELECTIVE
 LOAD_TILE
 RAW_LOCAL_QWORD_PAIR %ymm0,%ymm1
 RAW_LOCAL_QWORD_PAIR %ymm2,%ymm3
 RAW_LOCAL_QWORD_PAIR %ymm4,%ymm5
 RAW_LOCAL_QWORD_PAIR %ymm6,%ymm7
 MONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 0
 MONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 32
 MONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 64
 MONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_inv_s1_pair_qinv, .Ltile4_inv_s1_pair_factor, 96
 MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_inv_s2_qinv, .Ltile4_inv_s2_factor
 CENTER_I1_LOW_ARMS4
 MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_inv_s3_qinv, .Ltile4_inv_s3_factor
 MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, .Ltile4_inv_s4_qinv, .Ltile4_inv_s4_factor
 STORE_TILE
.endm
.p2align 5
.p2align 5
.p2align 5
.p2align 5
.p2align 5
.p2align 5
.p2align 5
 .section .text.gt32_tile4_forward_all_pair_id_center_asm,"ax",@progbits
.p2align 5
 .text
.p2align 5
 .section .text.gt32_tile4_inverse_all_pair_asm,"ax",@progbits
.p2align 5
 .text
.p2align 5
.macro FRONTEND_LOAD_FIXED low,high,original_high,even,odd
 vmovq \even(%rsi), \low
 vmovq \odd(%rsi), %xmm12
 vpunpcklqdq %xmm12, \low, \low
 vmovq 768+\even(%rsi), \high
 vmovq 768+\odd(%rsi), %xmm12
 vpunpcklqdq %xmm12, \high, \high
 vmovdqa \high, \original_high
.endm
.macro FRONTEND_FINISH
 vpaddw %xmm6, %xmm0, %xmm9
 vpaddw %xmm7, %xmm1, %xmm10
 vpaddw %xmm8, %xmm2, %xmm11
 vpsubw %xmm3, %xmm9, %xmm9
 vpsubw %xmm4, %xmm10, %xmm10
 vpsubw %xmm5, %xmm11, %xmm11
 vpaddw %xmm3, %xmm0, %xmm0
 vpaddw %xmm4, %xmm1, %xmm1
 vpaddw %xmm5, %xmm2, %xmm2
 vinserti128 $1, %xmm9, %ymm0, %ymm0
 vinserti128 $1, %xmm10, %ymm1, %ymm1
 vinserti128 $1, %xmm11, %ymm2, %ymm2
 vpmullw 0(%rdx), %ymm0, %ymm9
 vpmullw 32(%rdx), %ymm1, %ymm10
 vpmullw 64(%rdx), %ymm2, %ymm11
 vpmulhw 0(%rcx), %ymm0, %ymm0
 vpmulhw 32(%rcx), %ymm1, %ymm1
 vpmulhw 64(%rcx), %ymm2, %ymm2
 vpmulhw %ymm15, %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm11, %ymm11
 vpsubw %ymm9, %ymm0, %ymm0
 vpsubw %ymm10, %ymm1, %ymm1
 vpsubw %ymm11, %ymm2, %ymm2
 vpsubw %ymm2, %ymm1, %ymm3
 vpmullw .Ltile4_frontend_omega3_qinv(%rip), %ymm3, %ymm4
 vpmulhw .Ltile4_frontend_omega3_factor(%rip), %ymm3, %ymm3
 vpmulhw %ymm15, %ymm4, %ymm4
 vpsubw %ymm4, %ymm3, %ymm3
 vpaddw %ymm1, %ymm0, %ymm4
 vpaddw %ymm2, %ymm4, %ymm4
 vpsubw %ymm2, %ymm0, %ymm5
 vpaddw %ymm3, %ymm5, %ymm5
 vpsubw %ymm1, %ymm0, %ymm6
 vpsubw %ymm3, %ymm6, %ymm6
 vmovdqu %xmm4, 0(%rdi)
 vextracti128 $1, %ymm4, %xmm7
 vmovdqu %xmm7, 256(%rdi)
 vmovdqu %xmm5, 512(%rdi)
 vextracti128 $1, %ymm5, %xmm7
 vmovdqu %xmm7, 768(%rdi)
 vmovdqu %xmm6, 1024(%rdi)
 vextracti128 $1, %ymm6, %xmm7
 vmovdqu %xmm7, 1280(%rdi)
.endm
.macro FRONTEND_FIXED_ITER e0,o0,e1,o1,e2,o2
 FRONTEND_LOAD_FIXED %xmm0,%xmm3,%xmm6,\e0,\o0
 FRONTEND_LOAD_FIXED %xmm1,%xmm4,%xmm7,\e1,\o1
 FRONTEND_LOAD_FIXED %xmm2,%xmm5,%xmm8,\e2,\o2
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %xmm3, %xmm3
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %xmm4, %xmm4
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %xmm5, %xmm5
 FRONTEND_FINISH
 addq $96, %rdx
 addq $96, %rcx
 addq $16, %rdi
.endm
.macro GT_BLEND3 x,y,z,r0,r1,r2
 vpblendd $0x0c, \y, \x, \r0
 vpblendd $0x30, \z, \r0, \r0
 vpblendd $0x0c, \x, \z, \r1
 vpblendd $0x30, \y, \r1, \r1
 vpblendd $0x0c, \z, \y, \r2
 vpblendd $0x30, \x, \r2, \r2
.endm
.macro MONT_WIDE3 v0,v1,v2,offset
 vpmullw \offset+0(%rdx), \v0, %ymm12
 vpmullw \offset+32(%rdx), \v1, %ymm13
 vpmullw \offset+64(%rdx), \v2, %ymm14
 vpmulhw \offset+0(%rcx), \v0, \v0
 vpmulhw \offset+32(%rcx), \v1, \v1
 vpmulhw \offset+64(%rcx), \v2, \v2
 vpmulhw %ymm15, %ymm12, %ymm12
 vpmulhw %ymm15, %ymm13, %ymm13
 vpmulhw %ymm15, %ymm14, %ymm14
 vpsubw %ymm12, \v0, \v0
 vpsubw %ymm13, \v1, \v1
 vpsubw %ymm14, \v2, \v2
.endm
.macro MONT_WIDE3_START v0,v1,v2,offset
 vpmullw \offset+0(%rdx), \v0, %ymm12
 vpmullw \offset+32(%rdx), \v1, %ymm13
 vpmullw \offset+64(%rdx), \v2, %ymm14
 vpmulhw \offset+0(%rcx), \v0, \v0
 vpmulhw \offset+32(%rcx), \v1, \v1
 vpmulhw \offset+64(%rcx), \v2, \v2
.endm
.macro MONT_WIDE3_FINISH v0,v1,v2
 vpmulhw %ymm15, %ymm12, %ymm12
 vpmulhw %ymm15, %ymm13, %ymm13
 vpmulhw %ymm15, %ymm14, %ymm14
 vpsubw %ymm12, \v0, \v0
 vpsubw %ymm13, \v1, \v1
 vpsubw %ymm14, \v2, \v2
.endm
.macro DFT3_WIDE_STORE x0,x1,x2,o0,o1,o2
 vpsubw \x2, \x1, %ymm0
 vpmullw .Ltile4_frontend_omega3_qinv(%rip), %ymm0, %ymm1
 vpmulhw .Ltile4_frontend_omega3_factor(%rip), %ymm0, %ymm0
 vpmulhw %ymm15, %ymm1, %ymm1
 vpsubw %ymm1, %ymm0, %ymm0
 vpaddw \x1, \x0, %ymm1
 vpaddw \x2, %ymm1, %ymm1
 vpsubw \x2, \x0, %ymm2
 vpaddw %ymm0, %ymm2, %ymm2
 vpsubw \x1, \x0, %ymm3
 vpsubw %ymm0, %ymm3, %ymm3
 vmovdqu %ymm1, \o0(%rdi)
 vmovdqu %ymm2, \o1(%rdi)
 vmovdqu %ymm3, \o2(%rdi)
.endm
.macro FRONTEND_WIDE_ITER_BODY disp,x0,y0,z0,x1,y1,z1
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm6
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm4, %ymm7
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm5, %ymm8
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 GT_BLEND3 \x0,\y0,\z0,%ymm6,%ymm7,%ymm8
 GT_BLEND3 \x1,\y1,\z1,%ymm9,%ymm10,%ymm11
 MONT_WIDE3 %ymm6,%ymm7,%ymm8,0
 MONT_WIDE3 %ymm9,%ymm10,%ymm11,96
 DFT3_WIDE_STORE %ymm6,%ymm7,%ymm8,0,512,1024
 DFT3_WIDE_STORE %ymm9,%ymm10,%ymm11,256,768,1280
 addq $192, %rdx
 addq $192, %rcx
 addq $32, %rdi
.endm
.macro FRONTEND_WIDE_F1_ITER_BODY disp,x0,y0,z0,x1,y1,z1
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm6
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm4, %ymm7
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm5, %ymm8
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 GT_BLEND3 \x0,\y0,\z0,%ymm6,%ymm7,%ymm8
 GT_BLEND3 \x1,\y1,\z1,%ymm9,%ymm10,%ymm11
 MONT_WIDE3 %ymm6,%ymm7,%ymm8,0
 MONT_WIDE3 %ymm9,%ymm10,%ymm11,96
 DFT3_WIDE_STORE %ymm6,%ymm7,%ymm8,0,512,1024
 DFT3_WIDE_STORE %ymm9,%ymm10,%ymm11,256,768,1280
 addq $192, %rdx
 addq $192, %rcx
 addq $32, %rdi
.endm
.macro FRONTEND_WIDE_F4_TAIL x0,y0,z0,x1,y1,z1
 GT_BLEND3 \x0,\y0,\z0,%ymm6,%ymm7,%ymm8
 MONT_WIDE3_START %ymm6,%ymm7,%ymm8,0
 GT_BLEND3 \x1,\y1,\z1,%ymm9,%ymm10,%ymm11
 MONT_WIDE3_FINISH %ymm6,%ymm7,%ymm8
 MONT_WIDE3 %ymm9,%ymm10,%ymm11,96
 DFT3_WIDE_STORE %ymm6,%ymm7,%ymm8,0,512,1024
 DFT3_WIDE_STORE %ymm9,%ymm10,%ymm11,256,768,1280
 addq $192, %rdx
 addq $192, %rcx
 addq $32, %rdi
.endm
.macro FRONTEND_WIDE_F4_ITER_BODY disp,x0,y0,z0,x1,y1,z1
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm6
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm4, %ymm7
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm5, %ymm8
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 FRONTEND_WIDE_F4_TAIL \x0,\y0,\z0,\x1,\y1,\z1
.endm
.macro FRONTEND_WIDE_F14_ITER_BODY disp,x0,y0,z0,x1,y1,z1
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm6
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm4, %ymm7
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm5, %ymm8
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 FRONTEND_WIDE_F4_TAIL \x0,\y0,\z0,\x1,\y1,\z1
.endm
.macro FRONTEND_WIDE_F14_W2_ITER_BODY disp,nextdisp,preloaded,hasnext,x0,y0,z0,x1,y1,z1
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
.if !\preloaded
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
.endif
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm6
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm4, %ymm7
 vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm5, %ymm8
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 GT_BLEND3 \x0,\y0,\z0,%ymm6,%ymm7,%ymm8
 MONT_WIDE3_START %ymm6,%ymm7,%ymm8,0
 GT_BLEND3 \x1,\y1,\z1,%ymm9,%ymm10,%ymm11
 MONT_WIDE3_FINISH %ymm6,%ymm7,%ymm8
 MONT_WIDE3 %ymm9,%ymm10,%ymm11,96
 DFT3_WIDE_STORE %ymm6,%ymm7,%ymm8,0,512,1024
.if \hasnext
 vmovdqu 1024+\nextdisp(%rsi), %ymm4
 vmovdqu 1280+\nextdisp(%rsi), %ymm5
.endif
 DFT3_WIDE_STORE %ymm9,%ymm10,%ymm11,256,768,1280
 addq $192, %rdx
 addq $192, %rcx
 addq $32, %rdi
.endm
.macro EMIT_FRONTEND_WIDE_F14_W2
 .p2align 5
.endm
.macro FRONTEND_WIDE_E1_ITER_BODY disp,x0,y0,z0,x1,y1,z1
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
 vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %ymm3, %ymm9
 vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %ymm4, %ymm10
 vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %ymm5, %ymm11
 vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %ymm3, %ymm6
 vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %ymm4, %ymm7
 vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %ymm5, %ymm8
 vpmulhw %ymm15, %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm11, %ymm11
 vpsubw %ymm9, %ymm6, %ymm6
 vpsubw %ymm10, %ymm7, %ymm7
 vpsubw %ymm11, %ymm8, %ymm8
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 GT_BLEND3 \x0,\y0,\z0,%ymm6,%ymm7,%ymm8
 GT_BLEND3 \x1,\y1,\z1,%ymm9,%ymm10,%ymm11
 MONT_WIDE3 %ymm6,%ymm7,%ymm8,0
 MONT_WIDE3 %ymm9,%ymm10,%ymm11,96
 DFT3_WIDE_STORE %ymm6,%ymm7,%ymm8,0,512,1024
 DFT3_WIDE_STORE %ymm9,%ymm10,%ymm11,256,768,1280
 addq $192, %rdx
 addq $192, %rcx
 addq $32, %rdi
.endm
.macro FRONTEND_WIDE_ITER_0 disp
 FRONTEND_WIDE_ITER_BODY \disp,%ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5
.endm
.macro FRONTEND_WIDE_ITER_1 disp
 FRONTEND_WIDE_ITER_BODY \disp,%ymm1,%ymm2,%ymm0,%ymm4,%ymm5,%ymm3
.endm
.macro FRONTEND_WIDE_ITER_2 disp
 FRONTEND_WIDE_ITER_BODY \disp,%ymm2,%ymm0,%ymm1,%ymm5,%ymm3,%ymm4
.endm
.p2align 5
.p2align 5
.p2align 5
.p2align 5
.globl ntruplus768_ntt_frontend_avx2
.type ntruplus768_ntt_frontend_avx2,@function
ntruplus768_ntt_frontend_avx2:
 leaq .Ltile4_frontend_wide_twist_qinv(%rip), %rdx
 leaq .Ltile4_frontend_wide_twist_factor(%rip), %rcx
 vmovdqa .Ltile4_q(%rip), %ymm15
	movl $2, %r8d
.p2align 5
.Ltile4_frontend_compact_u3_loop:
 FRONTEND_WIDE_ITER_0 0
 FRONTEND_WIDE_ITER_1 32
 FRONTEND_WIDE_ITER_2 64
	addq $96, %rsi
	decl %r8d
	jne .Ltile4_frontend_compact_u3_loop
	FRONTEND_WIDE_ITER_0 0
	FRONTEND_WIDE_ITER_1 32
 vzeroupper
 ret
.size ntruplus768_ntt_frontend_avx2,.-ntruplus768_ntt_frontend_avx2
.purgem FRONTEND_WIDE_ITER_0
.purgem FRONTEND_WIDE_ITER_1
.purgem FRONTEND_WIDE_ITER_2
.macro FRONTEND_WIDE_ITER_0 disp
 FRONTEND_WIDE_E1_ITER_BODY \disp,%ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5
.endm
.macro FRONTEND_WIDE_ITER_1 disp
 FRONTEND_WIDE_E1_ITER_BODY \disp,%ymm1,%ymm2,%ymm0,%ymm4,%ymm5,%ymm3
.endm
.macro FRONTEND_WIDE_ITER_2 disp
 FRONTEND_WIDE_E1_ITER_BODY \disp,%ymm2,%ymm0,%ymm1,%ymm5,%ymm3,%ymm4
.endm
.p2align 5
 .section .text.gt32_tile4_forward_promotion_asm,"ax",@progbits
.p2align 5
.p2align 5
.p2align 5
 .text
 .section .text.gt32_tile4_forward_full_wide_raw_pair_id_center_align64_asm,"ax",@progbits
.p2align 6
 .text
.p2align 5
.p2align 5
.section .rodata
 .section .rodata.gtclean.ntt.tile4_i1_center10,"a",@progbits
.p2align 5
.Ltile4_i1_center10:
 .rept 16
 .short 10
 .endr
 .section .rodata.gtclean.ntt.tile4_fwd_center10,"a",@progbits
.p2align 5
.Ltile4_fwd_center10:
 .rept 16
 .short 10
 .endr
 .section .rodata.gtclean.ntt.tile4_fwd_s1_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s1_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .section .rodata.gtclean.ntt.tile4_fwd_s1_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s1_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .section .rodata.gtclean.ntt.tile4_fwd_s2_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s2_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .section .rodata.gtclean.ntt.tile4_fwd_s2_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s2_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .section .rodata.gtclean.ntt.tile4_fwd_s3_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s3_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19,-19
 .short 13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834,28834
 .section .rodata.gtclean.ntt.tile4_fwd_s3_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s3_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147,-147
 .short 366,366,366,366,366,366,366,366,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,109,109,109,109,109,109,109,109
 .short -1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .section .rodata.gtclean.ntt.tile4_fwd_s4_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_fwd_s4_factor,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_fwd_s5_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_fwd_s5_factor,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_inv_s1_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_inv_s1_factor,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_inv_s2_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s2_qinv:
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .short -19,-19,-19,-19,-28834,-28834,-28834,-28834,-13422,-13422,-13422,-13422,32531,32531,32531,32531
 .section .rodata.gtclean.ntt.tile4_inv_s2_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s2_factor:
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .short -147,-147,-147,-147,1118,1118,1118,1118,-366,-366,-366,-366,-109,-109,-109,-109
 .section .rodata.gtclean.ntt.tile4_inv_s3_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s3_qinv:
 .short -19,-19,-19,-19,739,739,739,739,-28834,-28834,-28834,-28834,10427,10427,10427,10427
 .short -13422,-13422,-13422,-13422,-834,-834,-834,-834,32531,32531,32531,32531,-23526,-23526,-23526,-23526
 .short -19,-19,-19,-19,739,739,739,739,-28834,-28834,-28834,-28834,10427,10427,10427,10427
 .short -13422,-13422,-13422,-13422,-834,-834,-834,-834,32531,32531,32531,32531,-23526,-23526,-23526,-23526
 .section .rodata.gtclean.ntt.tile4_inv_s3_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s3_factor:
 .short -147,-147,-147,-147,-1181,-1181,-1181,-1181,1118,1118,1118,1118,1339,1339,1339,1339
 .short -366,-366,-366,-366,446,446,446,446,-109,-109,-109,-109,794,794,794,794
 .short -147,-147,-147,-147,-1181,-1181,-1181,-1181,1118,1118,1118,1118,1339,1339,1339,1339
 .short -366,-366,-366,-366,446,446,446,446,-109,-109,-109,-109,794,794,794,794
 .section .rodata.gtclean.ntt.tile4_inv_s4_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s4_qinv:
 .short -19,-19,-19,-19,8265,8265,8265,8265,739,739,739,739,5327,5327,5327,5327
 .short -28834,-28834,-28834,-28834,-11147,-11147,-11147,-11147,10427,10427,10427,10427,-24019,-24019,-24019,-24019
 .short -13422,-13422,-13422,-13422,19242,19242,19242,19242,-834,-834,-834,-834,-29536,-29536,-29536,-29536
 .short 32531,32531,32531,32531,-27754,-27754,-27754,-27754,-23526,-23526,-23526,-23526,-31716,-31716,-31716,-31716
 .section .rodata.gtclean.ntt.tile4_inv_s4_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s4_factor:
 .short -147,-147,-147,-147,-1591,-1591,-1591,-1591,-1181,-1181,-1181,-1181,-177,-177,-177,-177
 .short 1118,1118,1118,1118,-11,-11,-11,-11,1339,1339,1339,1339,429,429,429,429
 .short -366,-366,-366,-366,554,554,554,554,446,446,446,446,-864,-864,-864,-864
 .short -109,-109,-109,-109,-874,-874,-874,-874,794,794,794,794,-484,-484,-484,-484
 .section .rodata.gtclean.ntt.tile4_fwd_s4_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_pair_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,13422,13422,13422,13422,13422,13422,13422,13422
 .short -32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427
 .short 834,834,834,834,834,834,834,834,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.ntt.tile4_fwd_s4_pair_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_pair_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,366,366,366,366,366,366,366,366
 .short 109,109,109,109,109,109,109,109,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339
 .short -446,-446,-446,-446,-446,-446,-446,-446,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.ntt.tile4_fwd_s5_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_pair_qinv:
 .short -19,-19,-19,-19,-32531,-32531,-32531,-32531,13422,13422,13422,13422,28834,28834,28834,28834
 .short 23526,23526,23526,23526,834,834,834,834,-10427,-10427,-10427,-10427,-739,-739,-739,-739
 .short 31716,31716,31716,31716,29536,29536,29536,29536,24019,24019,24019,24019,-5327,-5327,-5327,-5327
 .short 27754,27754,27754,27754,-19242,-19242,-19242,-19242,11147,11147,11147,11147,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt.tile4_fwd_s5_pair_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_pair_factor:
 .short -147,-147,-147,-147,109,109,109,109,366,366,366,366,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-446,-446,-446,-446,-1339,-1339,-1339,-1339,1181,1181,1181,1181
 .short 484,484,484,484,864,864,864,864,-429,-429,-429,-429,177,177,177,177
 .short 874,874,874,874,-554,-554,-554,-554,11,11,11,11,1591,1591,1591,1591
 .section .rodata.gtclean.ntt.tile4_fwd_s5_p_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_p_pair_qinv:
 .short -19,-19,-19,-19,13422,13422,13422,13422,-32531,-32531,-32531,-32531,28834,28834,28834,28834
 .short 23526,23526,23526,23526,-10427,-10427,-10427,-10427,834,834,834,834,-739,-739,-739,-739
 .short 31716,31716,31716,31716,24019,24019,24019,24019,29536,29536,29536,29536,-5327,-5327,-5327,-5327
 .short 27754,27754,27754,27754,11147,11147,11147,11147,-19242,-19242,-19242,-19242,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt.tile4_fwd_s5_p_pair_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_p_pair_factor:
 .short -147,-147,-147,-147,366,366,366,366,109,109,109,109,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-1339,-1339,-1339,-1339,-446,-446,-446,-446,1181,1181,1181,1181
 .short 484,484,484,484,-429,-429,-429,-429,864,864,864,864,177,177,177,177
 .short 874,874,874,874,11,11,11,11,-554,-554,-554,-554,1591,1591,1591,1591
 .section .rodata.gtclean.ntt.tile4_fwd_s4_qpair02_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_qpair02_qinv:
 .short -19,-19,-19,-19,-19,-19,-19,-19,-32531,-32531,-32531,-32531,-32531,-32531,-32531,-32531
 .short 13422,13422,13422,13422,13422,13422,13422,13422,28834,28834,28834,28834,28834,28834,28834,28834
 .short 23526,23526,23526,23526,23526,23526,23526,23526,834,834,834,834,834,834,834,834
 .short -10427,-10427,-10427,-10427,-10427,-10427,-10427,-10427,-739,-739,-739,-739,-739,-739,-739,-739
 .section .rodata.gtclean.ntt.tile4_fwd_s4_qpair02_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s4_qpair02_factor:
 .short -147,-147,-147,-147,-147,-147,-147,-147,109,109,109,109,109,109,109,109
 .short 366,366,366,366,366,366,366,366,-1118,-1118,-1118,-1118,-1118,-1118,-1118,-1118
 .short -794,-794,-794,-794,-794,-794,-794,-794,-446,-446,-446,-446,-446,-446,-446,-446
 .short -1339,-1339,-1339,-1339,-1339,-1339,-1339,-1339,1181,1181,1181,1181,1181,1181,1181,1181
 .section .rodata.gtclean.ntt.tile4_fwd_s5_qpair02_qinv,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_qpair02_qinv:
 .short -19,-19,-19,-19,13422,13422,13422,13422,23526,23526,23526,23526,-10427,-10427,-10427,-10427
 .short -32531,-32531,-32531,-32531,28834,28834,28834,28834,834,834,834,834,-739,-739,-739,-739
 .short 31716,31716,31716,31716,24019,24019,24019,24019,27754,27754,27754,27754,11147,11147,11147,11147
 .short 29536,29536,29536,29536,-5327,-5327,-5327,-5327,-19242,-19242,-19242,-19242,-8265,-8265,-8265,-8265
 .section .rodata.gtclean.ntt.tile4_fwd_s5_qpair02_factor,"a",@progbits
.p2align 5
.Ltile4_fwd_s5_qpair02_factor:
 .short -147,-147,-147,-147,366,366,366,366,-794,-794,-794,-794,-1339,-1339,-1339,-1339
 .short 109,109,109,109,-1118,-1118,-1118,-1118,-446,-446,-446,-446,1181,1181,1181,1181
 .short 484,484,484,484,-429,-429,-429,-429,874,874,874,874,11,11,11,11
 .short 864,864,864,864,177,177,177,177,-554,-554,-554,-554,1591,1591,1591,1591
 .section .rodata.gtclean.ntt.tile4_inv_s1_pair_qinv,"a",@progbits
.p2align 5
.Ltile4_inv_s1_pair_qinv:
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .short -19,-19,-19,-19,-13422,-13422,-13422,-13422,-19,-19,-19,-19,-13422,-13422,-13422,-13422
 .section .rodata.gtclean.ntt.tile4_inv_s1_pair_factor,"a",@progbits
.p2align 5
.Ltile4_inv_s1_pair_factor:
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .short -147,-147,-147,-147,-366,-366,-366,-366,-147,-147,-147,-147,-366,-366,-366,-366
 .section .rodata.gtclean.ntt.tile4_q,"a",@progbits
.p2align 5
.Ltile4_q:
 .rept 16
 .short 3457
 .endr
 .section .rodata.gtclean.ntt.tile4_frontend_offsets,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_frontend_twist_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_frontend_wide_twist_qinv,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_frontend_twist_factor,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_frontend_wide_twist_factor,"a",@progbits
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
 .section .rodata.gtclean.ntt.tile4_frontend_zeta_top_qinv,"a",@progbits
.p2align 5
.Ltile4_frontend_zeta_top_qinv:
 .rept 16
 .short 13687
 .endr
 .section .rodata.gtclean.ntt.tile4_frontend_zeta_top_factor,"a",@progbits
.p2align 5
.Ltile4_frontend_zeta_top_factor:
 .rept 16
 .short -1033
 .endr
 .section .rodata.gtclean.ntt.tile4_frontend_omega3_qinv,"a",@progbits
.p2align 5
.Ltile4_frontend_omega3_qinv:
 .rept 16
 .short 13706
 .endr
 .section .rodata.gtclean.ntt.tile4_frontend_omega3_factor,"a",@progbits
.p2align 5
.Ltile4_frontend_omega3_factor:
 .rept 16
 .short -886
 .endr
 .section .rodata.gtclean.ntt.tile4_frontend_zeta_top_raw,"a",@progbits
.p2align 5
.Ltile4_frontend_zeta_top_raw:
 .rept 16
 .short -722
 .endr
.section .note.GNU-stack,"",@progbits
