.text

/* Four fixed-factor Montgomery butterflies, issued as four parallel chains. */
.macro MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip),  \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip),  \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw %ymm15, %ymm8,  %ymm8
	vpmulhw %ymm15, %ymm9,  %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8,  \h0, \h0
	vpsubw %ymm9,  \h1, \h1
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
	vmovdqa %ymm8,  \h0
	vmovdqa %ymm9,  \h1
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

/* distance=2: duplicate 128-bit halves, butterfly, and rejoin. */
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

/* distance=1: duplicate qwords in each 128-bit lane, then blend sum/diff. */
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

/* Two distance=2 butterflies packed without duplicated 128-bit lanes. */
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

/* Two distance=1 butterflies packed without duplicated qwords. */
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
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
.endm

/* Match the frontend's two 16-byte stores so store forwarding can succeed. */
.macro LOAD_TILE_SPLIT
	vmovdqu   0(%rsi), %xmm0
	vinserti128 $1,  16(%rsi), %ymm0, %ymm0
	vmovdqu  32(%rsi), %xmm1
	vinserti128 $1,  48(%rsi), %ymm1, %ymm1
	vmovdqu  64(%rsi), %xmm2
	vinserti128 $1,  80(%rsi), %ymm2, %ymm2
	vmovdqu  96(%rsi), %xmm3
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
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
.endm

/*
 * Load one (n3,Q-even/Q-odd) source pair, perform top split and branch twist,
 * and leave [branch0 pair | branch1 pair] in target.
 */
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

.macro FORWARD_BODY_PAIR
	LOAD_TILE
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

/* Proof-safe raw-BM consumer: center only the next length-16 low arms. */
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
.globl gt32_tile4_forward_tile_asm
.type gt32_tile4_forward_tile_asm,@function
gt32_tile4_forward_tile_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	FORWARD_BODY_PAIR
	vzeroupper
	ret
.size gt32_tile4_forward_tile_asm,.-gt32_tile4_forward_tile_asm

.p2align 5
.globl gt32_tile4_inverse_tile_asm
.type gt32_tile4_inverse_tile_asm,@function
gt32_tile4_inverse_tile_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	INVERSE_BODY
	vzeroupper
	ret
.size gt32_tile4_inverse_tile_asm,.-gt32_tile4_inverse_tile_asm

.p2align 5
.globl gt32_tile4_forward_all_asm
.type gt32_tile4_forward_all_asm,@function
gt32_tile4_forward_all_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
.p2align 5
.Ltile4_forward_all_loop:
	FORWARD_BODY_PAIR
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_all_loop
	vzeroupper
	ret
.size gt32_tile4_forward_all_asm,.-gt32_tile4_forward_all_asm

.p2align 5
.globl gt32_tile4_forward_all_serial_asm
.type gt32_tile4_forward_all_serial_asm,@function
gt32_tile4_forward_all_serial_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
.p2align 5
.Ltile4_forward_all_serial_loop:
	FORWARD_BODY_SERIAL
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_all_serial_loop
	vzeroupper
	ret
.size gt32_tile4_forward_all_serial_asm,.-gt32_tile4_forward_all_serial_asm

.p2align 5
.globl gt32_tile4_forward_all_parallel_asm
.type gt32_tile4_forward_all_parallel_asm,@function
gt32_tile4_forward_all_parallel_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
.p2align 5
.Ltile4_forward_all_parallel_loop:
	FORWARD_BODY
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_all_parallel_loop
	vzeroupper
	ret
.size gt32_tile4_forward_all_parallel_asm,.-gt32_tile4_forward_all_parallel_asm

.p2align 5
.globl gt32_tile4_forward_all_pair_asm
.type gt32_tile4_forward_all_pair_asm,@function
gt32_tile4_forward_all_pair_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
.p2align 5
.Ltile4_forward_all_pair_loop:
	FORWARD_BODY_PAIR
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_all_pair_loop
	vzeroupper
	ret
.size gt32_tile4_forward_all_pair_asm,.-gt32_tile4_forward_all_pair_asm

.p2align 5
.globl gt32_tile4_inverse_all_asm
.type gt32_tile4_inverse_all_asm,@function
gt32_tile4_inverse_all_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
.p2align 5
.Ltile4_inverse_all_loop:
	INVERSE_BODY
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_inverse_all_loop
	vzeroupper
	ret
.size gt32_tile4_inverse_all_asm,.-gt32_tile4_inverse_all_asm

	.section .text.gt32_tile4_inverse_all_pair_asm,"ax",@progbits
.p2align 5
.globl gt32_tile4_inverse_all_pair_asm
.type gt32_tile4_inverse_all_pair_asm,@function
gt32_tile4_inverse_all_pair_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
.p2align 5
.Ltile4_inverse_all_pair_loop:
	INVERSE_BODY_PAIR
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_inverse_all_pair_loop
	vzeroupper
	ret
.size gt32_tile4_inverse_all_pair_asm,.-gt32_tile4_inverse_all_pair_asm
	.text

.p2align 5
.globl gt32_tile4_inverse_all_pair_selective_asm
.type gt32_tile4_inverse_all_pair_selective_asm,@function
gt32_tile4_inverse_all_pair_selective_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	vmovdqa .Ltile4_i1_center10(%rip), %ymm14
	movl $6, %ecx
.p2align 5
.Ltile4_inverse_all_pair_selective_loop:
	INVERSE_BODY_PAIR_SELECTIVE
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_inverse_all_pair_selective_loop
	vzeroupper
	ret
.size gt32_tile4_inverse_all_pair_selective_asm,.-gt32_tile4_inverse_all_pair_selective_asm

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
	/* Build [branch0 Q-pair | branch1 Q-pair] for all three n3 rows. */
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

	/* Three independent branch-twist Montgomery chains. */
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
	/* A/B/C are four contiguous quartic qwords. */
	vmovdqu 0+\disp(%rsi), %ymm0
	vmovdqu 256+\disp(%rsi), %ymm1
	vmovdqu 512+\disp(%rsi), %ymm2
	vmovdqu 768+\disp(%rsi), %ymm3
	vmovdqu 1024+\disp(%rsi), %ymm4
	vmovdqu 1280+\disp(%rsi), %ymm5

	/* Raw top split before the linear GT permutation. */
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

.macro FRONTEND_WIDE_ITER_0 disp
	FRONTEND_WIDE_ITER_BODY \disp,%ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5
.endm
.macro FRONTEND_WIDE_ITER_1 disp
	FRONTEND_WIDE_ITER_BODY \disp,%ymm1,%ymm2,%ymm0,%ymm4,%ymm5,%ymm3
.endm
.macro FRONTEND_WIDE_ITER_2 disp
	FRONTEND_WIDE_ITER_BODY \disp,%ymm2,%ymm0,%ymm1,%ymm5,%ymm3,%ymm4
.endm

/*
 * void gt32_tile4_frontend_asm(int16_t out[768], const int16_t in[768])
 *
 * out and in must be disjoint.  Each fixed iteration consumes Q,Q+1 and
 * stores one 128-bit pair directly into each of the six final TILE4 tiles.
 */
.p2align 5
.globl gt32_tile4_frontend_asm
.type gt32_tile4_frontend_asm,@function
gt32_tile4_frontend_asm:
	leaq .Ltile4_frontend_offsets(%rip), %rax
	leaq .Ltile4_frontend_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $16, %r10d
.p2align 5
.Ltile4_frontend_loop:
	FRONTEND_LOAD_PAIR %xmm0, %xmm3, %xmm6, 0
	FRONTEND_LOAD_PAIR %xmm1, %xmm4, %xmm7, 4
	FRONTEND_LOAD_PAIR %xmm2, %xmm5, %xmm8, 8

	/* Three independent top-split Montgomery chains. */
	vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %xmm3, %xmm9
	vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %xmm4, %xmm10
	vpmullw .Ltile4_frontend_zeta_top_qinv(%rip), %xmm5, %xmm11
	vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %xmm3, %xmm3
	vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %xmm4, %xmm4
	vpmulhw .Ltile4_frontend_zeta_top_factor(%rip), %xmm5, %xmm5
	vpmulhw %xmm15, %xmm9, %xmm9
	vpmulhw %xmm15, %xmm10, %xmm10
	vpmulhw %xmm15, %xmm11, %xmm11
	vpsubw %xmm9, %xmm3, %xmm3
	vpsubw %xmm10, %xmm4, %xmm4
	vpsubw %xmm11, %xmm5, %xmm5

	FRONTEND_FINISH

	addq $12, %rax
	addq $96, %rdx
	addq $96, %rcx
	addq $16, %rdi
	decl %r10d
	jne .Ltile4_frontend_loop
	vzeroupper
	ret
.size gt32_tile4_frontend_asm,.-gt32_tile4_frontend_asm

/* Small-input-only frontend: raw -722 top split, otherwise identical. */
.p2align 5
.globl gt32_tile4_frontend_raw_asm
.type gt32_tile4_frontend_raw_asm,@function
gt32_tile4_frontend_raw_asm:
	leaq .Ltile4_frontend_offsets(%rip), %rax
	leaq .Ltile4_frontend_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $16, %r10d
.p2align 5
.Ltile4_frontend_raw_loop:
	FRONTEND_LOAD_PAIR %xmm0, %xmm3, %xmm6, 0
	FRONTEND_LOAD_PAIR %xmm1, %xmm4, %xmm7, 4
	FRONTEND_LOAD_PAIR %xmm2, %xmm5, %xmm8, 8
	vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %xmm3, %xmm3
	vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %xmm4, %xmm4
	vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %xmm5, %xmm5
	FRONTEND_FINISH
	addq $12, %rax
	addq $96, %rdx
	addq $96, %rcx
	addq $16, %rdi
	decl %r10d
	jne .Ltile4_frontend_raw_loop
	vzeroupper
	ret
.size gt32_tile4_frontend_raw_asm,.-gt32_tile4_frontend_raw_asm

/* Small-input frontend with generator-owned fixed source displacements. */
.p2align 5
.globl gt32_tile4_frontend_fixed_raw_asm
.type gt32_tile4_frontend_fixed_raw_asm,@function
gt32_tile4_frontend_fixed_raw_asm:
	leaq .Ltile4_frontend_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
#include "../generated/tile4_frontend_fixed.inc"
	vzeroupper
	ret
.size gt32_tile4_frontend_fixed_raw_asm,.-gt32_tile4_frontend_fixed_raw_asm

/* N5: contiguous quartic loads and qword-granular Good--Thomas blends. */
.p2align 5
.globl gt32_tile4_frontend_wide_raw_asm
.type gt32_tile4_frontend_wide_raw_asm,@function
gt32_tile4_frontend_wide_raw_asm:
	leaq .Ltile4_frontend_wide_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_wide_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
#include "../generated/tile4_frontend_wide.inc"
	vzeroupper
	ret
.size gt32_tile4_frontend_wide_raw_asm,.-gt32_tile4_frontend_wide_raw_asm

	.section .text.gt32_tile4_forward_promotion_asm,"ax",@progbits
.p2align 5
.globl gt32_tile4_forward_full_wide_raw_pair_align32_asm
.type gt32_tile4_forward_full_wide_raw_pair_align32_asm,@function
gt32_tile4_forward_full_wide_raw_pair_align32_asm:
	movq %rsp, %r10
	movq %rdi, %r11
	andq $-32, %rsp
	subq $1536, %rsp
	jmp .Ltile4_forward_full_wide_raw_pair_common
.size gt32_tile4_forward_full_wide_raw_pair_align32_asm,.-gt32_tile4_forward_full_wide_raw_pair_align32_asm

.p2align 5
.globl gt32_tile4_forward_full_wide_raw_pair_align64_asm
.type gt32_tile4_forward_full_wide_raw_pair_align64_asm,@function
gt32_tile4_forward_full_wide_raw_pair_align64_asm:
	movq %rsp, %r10
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1536, %rsp
	jmp .Ltile4_forward_full_wide_raw_pair_common
.size gt32_tile4_forward_full_wide_raw_pair_align64_asm,.-gt32_tile4_forward_full_wide_raw_pair_align64_asm

.p2align 5
.globl gt32_tile4_forward_full_wide_raw_pair_asm
.type gt32_tile4_forward_full_wide_raw_pair_asm,@function
gt32_tile4_forward_full_wide_raw_pair_asm:
	movq %rsp, %r10
	movq %rdi, %r11
	subq $1536, %rsp
.Ltile4_forward_full_wide_raw_pair_common:
	movq %rsp, %rdi
	leaq .Ltile4_frontend_wide_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_wide_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
#include "../generated/tile4_frontend_wide.inc"
	movq %rsp, %rsi
	movq %r11, %rdi
	movl $6, %ecx
.p2align 5
.Ltile4_forward_full_wide_raw_pair_loop:
	FORWARD_BODY_PAIR
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_full_wide_raw_pair_loop
	movq %r10, %rsp
	vzeroupper
	ret
.size gt32_tile4_forward_full_wide_raw_pair_asm,.-gt32_tile4_forward_full_wide_raw_pair_asm
	.text

/*
 * Small-input full forward: fixed frontend and pair-packed NTT32 in one leaf.
 * The 1536-byte scratch is backend-private and also makes out == in safe.
 */
.p2align 5
.globl gt32_tile4_forward_full_fixed_pair_wide_load_asm
.type gt32_tile4_forward_full_fixed_pair_wide_load_asm,@function
gt32_tile4_forward_full_fixed_pair_wide_load_asm:
	xorl %r8d, %r8d
	jmp .Ltile4_forward_full_fixed_pair_common
.size gt32_tile4_forward_full_fixed_pair_wide_load_asm,.-gt32_tile4_forward_full_fixed_pair_wide_load_asm

.p2align 5
.globl gt32_tile4_forward_full_fixed_pair_asm
.type gt32_tile4_forward_full_fixed_pair_asm,@function
gt32_tile4_forward_full_fixed_pair_asm:
	movl $1, %r8d
.Ltile4_forward_full_fixed_pair_common:
	movq %rdi, %r11
	subq $1536, %rsp
	movq %rsp, %rdi
	leaq .Ltile4_frontend_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_twist_factor(%rip), %rcx
	vmovdqa .Ltile4_q(%rip), %ymm15
#include "../generated/tile4_frontend_fixed.inc"
	movq %rsp, %rsi
	movq %r11, %rdi
	movl $6, %ecx
	testl %r8d, %r8d
	je .Ltile4_forward_full_fixed_pair_wide_loop
.p2align 5
.Ltile4_forward_full_fixed_pair_loop:
	FORWARD_BODY_PAIR_SPLITLOAD
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_full_fixed_pair_loop
	jmp .Ltile4_forward_full_fixed_pair_done
.p2align 5
.Ltile4_forward_full_fixed_pair_wide_loop:
	FORWARD_BODY_PAIR
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ltile4_forward_full_fixed_pair_wide_loop
.Ltile4_forward_full_fixed_pair_done:
	addq $1536, %rsp
	vzeroupper
	ret
.size gt32_tile4_forward_full_fixed_pair_asm,.-gt32_tile4_forward_full_fixed_pair_asm

.section .rodata
.p2align 5
.Ltile4_i1_center10:
	.rept 16
	.short 10
	.endr
#include "../generated/tile4_constants.inc"

.section .note.GNU-stack,"",@progbits
