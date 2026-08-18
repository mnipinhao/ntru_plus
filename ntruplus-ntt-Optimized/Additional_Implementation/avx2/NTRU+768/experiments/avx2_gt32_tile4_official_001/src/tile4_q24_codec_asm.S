/* Benchmark-only quartic-native 24-byte wire codec. */

	.text

#ifndef Q24_LAZY_SCHEDULE
#define Q24_LAZY_SCHEDULE 0
#endif

.macro Q24_LOAD12 disp,dst,safe
.if \safe
	vmovq \disp(%rsi), \dst
	vpinsrd $2, \disp+8(%rsi), \dst, \dst
.else
	vmovdqu \disp(%rsi), \dst
.endif
.endm

.macro Q24_DECODE_REG low,high,safelow,safehigh,mask,dst,tmp,acc
	Q24_LOAD12 \low,%xmm14,\safelow
	Q24_LOAD12 \high,%xmm15,\safehigh
	vinserti128 $1, %xmm15, %ymm14, \dst
	vpshufb \mask(%rip), \dst, \dst
	vpsrlw $4, \dst, \tmp
	vpblendw $0xaa, \tmp, \dst, \dst
	vpand %ymm12, \dst, \dst
	vpmaxuw \dst, \acc, \acc
.endm

#if defined(Q24_DECODE_DEBT_GATE)
.macro Q24_DECODE_REG_NOVAL low,high,safelow,safehigh,mask,dst,tmp
	Q24_LOAD12 \low,%xmm14,\safelow
	Q24_LOAD12 \high,%xmm15,\safehigh
	vinserti128 $1, %xmm15, %ymm14, \dst
	vpshufb \mask(%rip), \dst, \dst
	vpsrlw $4, \dst, \tmp
	vpblendw $0xaa, \tmp, \dst, \dst
	vpand %ymm12, \dst, \dst
.endm

.macro Q24_DECODE_WIRE_PACKET low,high,safelow,safehigh,out,acc
	Q24_DECODE_REG \low,\high,\safelow,\safehigh,.Lq24_decode_mask_0123,%ymm0,%ymm14,\acc
	vmovdqu %ymm0, \out(%rdi)
.endm
#endif

.macro Q24_DECODE_AOS_PACKET low,high,safelow,safehigh,mask,acc,out
	Q24_DECODE_REG \low,\high,\safelow,\safehigh,\mask,%ymm0,%ymm14,\acc
	vmovdqu %ymm0, \out(%rdi)
.endm

.macro Q24_DECODE_COMPACT_DESC offset,dst,acc
	movzwl \offset(%r8), %edx
	vmovdqu (%rsi,%rdx), %xmm14
	movzwl \offset+2(%r8), %edx
	vmovdqu (%rsi,%rdx), %xmm15
	vinserti128 $1, %xmm15, %ymm14, \dst
	movzbl \offset+4(%r8), %edx
	shll $5, %edx
	vpshufb (%r12,%rdx), \dst, \dst
	vpsrlw $4, \dst, %ymm14
	vpblendw $0xaa, %ymm14, \dst, \dst
	vpand %ymm12, \dst, \dst
	vpmaxuw \dst, \acc, \acc
.endm

.macro Q24_DECODE_PATTERN_REG low,high,mask,dst,tmp,acc
	vmovdqu \low(%r12), %xmm14
	vmovdqu \high(%r12), %xmm15
	vinserti128 $1, %xmm15, %ymm14, \dst
	vpshufb \mask(%rip), \dst, \dst
	vpsrlw $4, \dst, \tmp
	vpblendw $0xaa, \tmp, \dst, \dst
	vpand %ymm12, \dst, \dst
	vpmaxuw \dst, \acc, \acc
.endm

.macro Q24_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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

/* Absorb a symmetric qword swap into the final transpose layer. */
.macro Q24_TRANSPOSE_TF1 s0,s1,s2,s3,t0,t1,t2,t3,o0,o1,o2,o3
	vpunpcklwd %\s1, %\s0, %\t0
	vpunpckhwd %\s1, %\s0, %\t1
	vpunpcklwd %\s3, %\s2, %\t2
	vpunpckhwd %\s3, %\s2, %\t3
	vpunpckldq %\t2, %\t0, %\s0
	vpunpckhdq %\t2, %\t0, %\s1
	vpunpckldq %\t3, %\t1, %\s2
	vpunpckhdq %\t3, %\t1, %\s3
.if \o0
	vpunpcklqdq %\s0, %\s2, %\t0
.else
	vpunpcklqdq %\s2, %\s0, %\t0
.endif
.if \o1
	vpunpckhqdq %\s0, %\s2, %\t1
.else
	vpunpckhqdq %\s2, %\s0, %\t1
.endif
.if \o2
	vpunpcklqdq %\s1, %\s3, %\t2
.else
	vpunpcklqdq %\s3, %\s1, %\t2
.endif
.if \o3
	vpunpckhqdq %\s1, %\s3, %\t3
.else
	vpunpckhqdq %\s3, %\s1, %\t3
.endif
.endm

.macro Q24_DECODE_INIT
	vmovdqa .Lq24_low12(%rip), %ymm12
.endm

.macro Q24_DECODE_ZERO
	vpxor %ymm8, %ymm8, %ymm8
	vpxor %ymm9, %ymm9, %ymm9
	vpxor %ymm10, %ymm10, %ymm10
	vpxor %ymm11, %ymm11, %ymm11
.endm

.macro Q24_DECODE_FINISH
	vpmaxuw %ymm9, %ymm8, %ymm8
	vpmaxuw %ymm11, %ymm10, %ymm10
	vpmaxuw %ymm10, %ymm8, %ymm8
	vpcmpgtw .Lq24_qm1(%rip), %ymm8, %ymm8
	vpmovmskb %ymm8, %edx
	orl %edx, %eax
.endm

.macro Q24_ENCODE_CANONICAL_REG_PACKET src,srcx,perm,offset,safe
	vpermq $\perm, \src, \src
	vpsraw $15, \src, %ymm14
	vpand %ymm15, %ymm14, %ymm14
	vpaddw %ymm14, \src, \src
	vpmaddwd .Lq24_pair_factor(%rip), \src, \src
	vpshufb .Lq24_pack_mask(%rip), \src, \src
	vmovdqu \srcx, \offset(%rdi)
	vextracti128 $1, \src, %xmm14
.if \safe
	vmovq %xmm14, \offset+12(%rdi)
	vpextrd $2, %xmm14, \offset+20(%rdi)
.else
	vmovdqu %xmm14, \offset+12(%rdi)
.endif
.endm

.macro Q24_ENCODE_REG_PACKET src,srcx,perm,offset,safe
	Q24_ENCODE_CANONICAL_REG_PACKET \src,\srcx,\perm,\offset,\safe
.endm

.macro Q24_ENCODE_MEM_PACKET in,perm,offset,safe
	vmovdqu \in(%rsi), %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,\perm,\offset,\safe
.endm

	/* The generated include ends in fixed shuffle masks. */
	.section .rodata
#include "../generated/tile4_q24_codec.inc"
#if defined(Q24_DECODE_DEBT_GATE)
#include "../generated/tile4_decode_debt.inc"
#endif
#if defined(Q24_SOA_COMPACT) || defined(Q24_SOA_PATTERN_COMPACT) || \
	defined(Q24_INCLUDE_COMPACT_TABLES)
#include "../generated/tile4_q24_compact.inc"
#endif

	.section .text.gt32_q24_decode_aos_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_decode_aos_asm
	.type gt32_q24_decode_aos_asm,@function
gt32_q24_decode_aos_asm:
	xorl %eax, %eax
	Q24_DECODE_INIT
	Q24_DECODE_ZERO
	Q24_DECODE_AOS_BODY
	Q24_DECODE_FINISH
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_q24_decode_aos_asm,.-gt32_q24_decode_aos_asm

#if defined(Q24_SOA_CAGE_OFFSET)
	/*
	 * Attribution-only fixed-size placement cage.  The active private-SoA
	 * decoder body moves inside one page while every following symbol keeps
	 * the same address.  Supported offsets are generated in 32-byte steps.
	 */
	.section .text.gt32_q24_decode_soa_cage,"ax",@progbits
	.p2align 12
.Lq24_decode_soa_cage_start:
	.fill Q24_SOA_CAGE_OFFSET,1,0x90
#else
	.section .text.gt32_q24_decode_soa_asm,"ax",@progbits
	.p2align 5
#endif
	.globl gt32_q24_decode_soa_body_cage
	.type gt32_q24_decode_soa_body_cage,@function
gt32_q24_decode_soa_body_cage:
	Q24_DECODE_ZERO
#if defined(Q24_SOA_COMPACT)
	pushq %r12
	leaq .Lq24_compact_group_table(%rip), %r8
	leaq .Lq24_decode_mask_0123(%rip), %r12
	movl $11, %ecx
.Lq24_decode_soa_compact_loop:
	Q24_DECODE_COMPACT_DESC 2,%ymm0,%ymm8
	Q24_DECODE_COMPACT_DESC 7,%ymm1,%ymm9
	Q24_DECODE_COMPACT_DESC 12,%ymm2,%ymm10
	Q24_DECODE_COMPACT_DESC 17,%ymm3,%ymm11
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	movzwl 0(%r8), %edx
	vmovdqu %ymm4, 0(%rdi,%rdx)
	vmovdqu %ymm5, 32(%rdi,%rdx)
	vmovdqu %ymm6, 64(%rdi,%rdx)
	vmovdqu %ymm7, 96(%rdi,%rdx)
	addq $22, %r8
	decl %ecx
	jne .Lq24_decode_soa_compact_loop
	Q24_DECODE_SOA_COMPACT_FINAL_GROUP
	popq %r12
#elif defined(Q24_SOA_PATTERN_COMPACT)
	pushq %r12
	Q24_DECODE_SOA_PATTERN_COMPACT_BODY
	popq %r12
#else
	Q24_DECODE_SOA_BODY
#endif
	Q24_DECODE_FINISH
	ret
	.size gt32_q24_decode_soa_body_cage,.-gt32_q24_decode_soa_body_cage
#if defined(Q24_SOA_CAGE_OFFSET)
	.if (. - .Lq24_decode_soa_cage_start) > 4096
	.error "Q24 private-SoA decoder does not fit the 4 KiB placement cage"
	.endif
	.fill 4096-(.-.Lq24_decode_soa_cage_start),1,0x90

	.section .text.gt32_q24_decode_soa_asm,"ax",@progbits
#endif

	.p2align 5
	.globl gt32_q24_decode_soa_asm
	.type gt32_q24_decode_soa_asm,@function
gt32_q24_decode_soa_asm:
	xorl %eax, %eax
	Q24_DECODE_INIT
	call gt32_q24_decode_soa_body_cage
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_q24_decode_soa_asm,.-gt32_q24_decode_soa_asm

	/* c/f/hinv decoder with the same arguments as the current decap decoder. */
	.section .text.gt32_q24_decode3_soa_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_decode3_soa_asm
	.type gt32_q24_decode3_soa_asm,@function
gt32_q24_decode3_soa_asm:
	movq %rsi, %r9
	movq %rdx, %r10
	movq %r8, %r11
	xorl %eax, %eax
	Q24_DECODE_INIT
	movq %rcx, %rsi
	call gt32_q24_decode_soa_body_cage
	movq %r9, %rdi
	movq %r11, %rsi
	call gt32_q24_decode_soa_body_cage
	movq %r10, %rdi
	leaq 1152(%r11), %rsi
	call gt32_q24_decode_soa_body_cage
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_q24_decode3_soa_asm,.-gt32_q24_decode3_soa_asm

#if defined(Q24_DECODE_DEBT_GATE)
	/* D1: identical private-M result, intentionally omitting rejection work. */
	.section .text.gt32_q24_decode_soa_noval_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_decode_soa_noval_asm
	.type gt32_q24_decode_soa_noval_asm,@function
gt32_q24_decode_soa_noval_asm:
	Q24_DECODE_INIT
	Q24_DECODE_SOA_NOVAL_BODY
	xorl %eax, %eax
	vzeroupper
	ret
	.size gt32_q24_decode_soa_noval_asm,.-gt32_q24_decode_soa_noval_asm

	/* D2a: canonical wire-order int16, preserving the normal reject result. */
	.section .text.gt32_q24_decode_wire_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_decode_wire_asm
	.type gt32_q24_decode_wire_asm,@function
gt32_q24_decode_wire_asm:
	xorl %eax, %eax
	Q24_DECODE_INIT
	Q24_DECODE_ZERO
	Q24_DECODE_WIRE_BODY
	Q24_DECODE_FINISH
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_q24_decode_wire_asm,.-gt32_q24_decode_wire_asm

	/* D2b: already-unpacked wire-order int16 to current private-M. */
	.section .text.gt32_q24_route_wire_to_soa_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_route_wire_to_soa_asm
	.type gt32_q24_route_wire_to_soa_asm,@function
gt32_q24_route_wire_to_soa_asm:
	Q24_ROUTE_WIRE_TO_SOA_BODY
	vzeroupper
	ret
	.size gt32_q24_route_wire_to_soa_asm,.-gt32_q24_route_wire_to_soa_asm
#endif

	.section .text.gt32_q24_encode_aos_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_aos_asm
	.type gt32_q24_encode_aos_asm,@function
gt32_q24_encode_aos_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	Q24_ENCODE_AOS_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_aos_asm,.-gt32_q24_encode_aos_asm

	.section .text.gt32_q24_encode_soa_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_asm
	.type gt32_q24_encode_soa_asm,@function
gt32_q24_encode_soa_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	Q24_ENCODE_SOA_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_soa_asm,.-gt32_q24_encode_soa_asm

	/*
	 * Independent lazy Forward-output contract.  For every signed word
	 * |x| <= 10788, v=9 computes t=round(x*9/2^15), after which
	 * x-t*q is in [-2188,2188].  The canonical packet macro then performs
	 * the single sign correction and the unchanged Q24 packing route.
	 */
	.purgem Q24_ENCODE_REG_PACKET
.macro Q24_ENCODE_REG_PACKET src,srcx,perm,offset,safe
	vpmulhrsw %ymm13, \src, %ymm14
	vpmullw %ymm15, %ymm14, %ymm14
	vpsubw %ymm14, \src, \src
	Q24_ENCODE_CANONICAL_REG_PACKET \src,\srcx,\perm,\offset,\safe
.endm

.macro Q24_LAZY_STORE_PACKET src,srcx,tmpx,offset,safe
	vmovdqu \srcx, \offset(%rdi)
	vextracti128 $1, \src, \tmpx
.if \safe
	vmovq \tmpx, \offset+12(%rdi)
	vpextrd $2, \tmpx, \offset+20(%rdi)
.else
	vmovdqu \tmpx, \offset+12(%rdi)
.endif
.endm

.macro Q24_LAZY_REDUCE2 a,b,t0,t1
	vpmulhrsw %ymm13, \a, \t0
	vpmulhrsw %ymm13, \b, \t1
	vpmullw %ymm15, \t0, \t0
	vpmullw %ymm15, \t1, \t1
	vpsubw \t0, \a, \a
	vpsubw \t1, \b, \b
.endm

.macro Q24_LAZY_PACK2 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,t0,t0x,t1,t1x
	vpermq $\ap, \a, \a
	vpermq $\bp, \b, \b
	vpsraw $15, \a, \t0
	vpsraw $15, \b, \t1
	vpand %ymm15, \t0, \t0
	vpand %ymm15, \t1, \t1
	vpaddw \t0, \a, \a
	vpaddw \t1, \b, \b
	vpmaddwd .Lq24_pair_factor(%rip), \a, \a
	vpmaddwd .Lq24_pair_factor(%rip), \b, \b
	vpshufb .Lq24_pack_mask(%rip), \a, \a
	vpshufb .Lq24_pack_mask(%rip), \b, \b
	Q24_LAZY_STORE_PACKET \a,\ax,\t0x,\ao,\asafe
	Q24_LAZY_STORE_PACKET \b,\bx,\t1x,\bo,\bsafe
.endm

.macro Q24_LAZY_PAIR a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe
	Q24_LAZY_REDUCE2 \a,\b,%ymm0,%ymm1
	Q24_LAZY_PACK2 \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe,\
		%ymm0,%xmm0,%ymm1,%xmm1
.endm

/* TF1 keeps the L1 schedule but omits qword permutations represented by the
 * final transpose orientation (and pre-existing identity permutations). */
.macro Q24_LAZY_PACK2_TF1 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,t0,t0x,t1,t1x
.if \ap != 228
	vpermq $\ap, \a, \a
.endif
.if \bp != 228
	vpermq $\bp, \b, \b
.endif
	vpsraw $15, \a, \t0
	vpsraw $15, \b, \t1
	vpand %ymm15, \t0, \t0
	vpand %ymm15, \t1, \t1
	vpaddw \t0, \a, \a
	vpaddw \t1, \b, \b
	vpmaddwd .Lq24_pair_factor(%rip), \a, \a
	vpmaddwd .Lq24_pair_factor(%rip), \b, \b
	vpshufb .Lq24_pack_mask(%rip), \a, \a
	vpshufb .Lq24_pack_mask(%rip), \b, \b
	Q24_LAZY_STORE_PACKET \a,\ax,\t0x,\ao,\asafe
	Q24_LAZY_STORE_PACKET \b,\bx,\t1x,\bo,\bsafe
.endm

.macro Q24_LAZY_PAIR_TF1 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe
	Q24_LAZY_REDUCE2 \a,\b,%ymm0,%ymm1
	Q24_LAZY_PACK2_TF1 \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe,\
		%ymm0,%xmm0,%ymm1,%xmm1
.endm

.macro Q24_ENCODE_TF1_PACKET src,srcx,perm,offset,safe
	vpmulhrsw %ymm13, \src, %ymm14
	vpmullw %ymm15, %ymm14, %ymm14
	vpsubw %ymm14, \src, \src
.if \perm != 228
	vpermq $\perm, \src, \src
.endif
	vpsraw $15, \src, %ymm14
	vpand %ymm15, %ymm14, %ymm14
	vpaddw %ymm14, \src, \src
	vpmaddwd .Lq24_pair_factor(%rip), \src, \src
	vpshufb .Lq24_pack_mask(%rip), \src, \src
	vmovdqu \srcx, \offset(%rdi)
	vextracti128 $1, \src, %xmm14
.if \safe
	vmovq %xmm14, \offset+12(%rdi)
	vpextrd $2, %xmm14, \offset+20(%rdi)
.else
	vmovdqu %xmm14, \offset+12(%rdi)
.endif
.endm

.macro Q24_LAZY_QUAD_REDUCE a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,c,cx,cp,co,csafe,d,dx,dp,do,dsafe
	vpmulhrsw %ymm13, \a, %ymm0
	vpmulhrsw %ymm13, \b, %ymm1
	vpmulhrsw %ymm13, \c, %ymm2
	vpmulhrsw %ymm13, \d, %ymm3
	vpmullw %ymm15, %ymm0, %ymm0
	vpmullw %ymm15, %ymm1, %ymm1
	vpmullw %ymm15, %ymm2, %ymm2
	vpmullw %ymm15, %ymm3, %ymm3
	vpsubw %ymm0, \a, \a
	vpsubw %ymm1, \b, \b
	vpsubw %ymm2, \c, \c
	vpsubw %ymm3, \d, \d
.endm

.macro Q24_LAZY_PACK4 a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,c,cx,cp,co,csafe,d,dx,dp,do,dsafe
	vpermq $\ap, \a, \a
	vpermq $\bp, \b, \b
	vpermq $\cp, \c, \c
	vpermq $\dp, \d, \d
	vpsraw $15, \a, %ymm0
	vpsraw $15, \b, %ymm1
	vpsraw $15, \c, %ymm2
	vpsraw $15, \d, %ymm3
	vpand %ymm15, %ymm0, %ymm0
	vpand %ymm15, %ymm1, %ymm1
	vpand %ymm15, %ymm2, %ymm2
	vpand %ymm15, %ymm3, %ymm3
	vpaddw %ymm0, \a, \a
	vpaddw %ymm1, \b, \b
	vpaddw %ymm2, \c, \c
	vpaddw %ymm3, \d, \d
	vpmaddwd .Lq24_pair_factor(%rip), \a, \a
	vpmaddwd .Lq24_pair_factor(%rip), \b, \b
	vpmaddwd .Lq24_pair_factor(%rip), \c, \c
	vpmaddwd .Lq24_pair_factor(%rip), \d, \d
	vpshufb .Lq24_pack_mask(%rip), \a, \a
	vpshufb .Lq24_pack_mask(%rip), \b, \b
	vpshufb .Lq24_pack_mask(%rip), \c, \c
	vpshufb .Lq24_pack_mask(%rip), \d, \d
	Q24_LAZY_STORE_PACKET \a,\ax,%xmm0,\ao,\asafe
	Q24_LAZY_STORE_PACKET \b,\bx,%xmm1,\bo,\bsafe
	Q24_LAZY_STORE_PACKET \c,\cx,%xmm2,\co,\csafe
	Q24_LAZY_STORE_PACKET \d,\dx,%xmm3,\do,\dsafe
.endm

.macro Q24_LAZY_QUAD_PIPELINE a,ax,ap,ao,asafe,b,bx,bp,bo,bsafe,c,cx,cp,co,csafe,d,dx,dp,do,dsafe
	Q24_LAZY_QUAD_REDUCE \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe,\
		\c,\cx,\cp,\co,\csafe,\d,\dx,\dp,\do,\dsafe
	Q24_LAZY_PACK4 \a,\ax,\ap,\ao,\asafe,\b,\bx,\bp,\bo,\bsafe,\
		\c,\cx,\cp,\co,\csafe,\d,\dx,\dp,\do,\dsafe
.endm

.macro Q24_HALF_REDUCE_PACK4 a,b,c,d
	Q24_LAZY_QUAD_REDUCE \a,%xmm4,0,0,0,\b,%xmm5,0,0,0,\c,%xmm6,0,0,0,\d,%xmm7,0,0,0
	vpsraw $15, \a, %ymm0
	vpsraw $15, \b, %ymm1
	vpsraw $15, \c, %ymm2
	vpsraw $15, \d, %ymm3
	vpand %ymm15, %ymm0, %ymm0
	vpand %ymm15, %ymm1, %ymm1
	vpand %ymm15, %ymm2, %ymm2
	vpand %ymm15, %ymm3, %ymm3
	vpaddw %ymm0, \a, \a
	vpaddw %ymm1, \b, \b
	vpaddw %ymm2, \c, \c
	vpaddw %ymm3, \d, \d
	vpmaddwd .Lq24_pair_factor(%rip), \a, \a
	vpmaddwd .Lq24_pair_factor(%rip), \b, \b
	vpmaddwd .Lq24_pair_factor(%rip), \c, \c
	vpmaddwd .Lq24_pair_factor(%rip), \d, \d
	vpshufb .Lq24_pack_mask(%rip), \a, \a
	vpshufb .Lq24_pack_mask(%rip), \b, \b
	vpshufb .Lq24_pack_mask(%rip), \c, \c
	vpshufb .Lq24_pack_mask(%rip), \d, \d
.endm

/*
 * SP1 preserves the TF1 instruction multiset but issues the next block's
 * four loads after the current vpmulhrsw quotient estimate.  ymm8..ymm11
 * are otherwise dead throughout the current reduce/canonicalize/pack tail.
 */
.macro Q24_HALF_REDUCE_PACK4_SP1 a,b,c,d,n0,n1,n2,n3
	vpmulhrsw %ymm13, \a, %ymm0
	vpmulhrsw %ymm13, \b, %ymm1
	vpmulhrsw %ymm13, \c, %ymm2
	vpmulhrsw %ymm13, \d, %ymm3
	vmovdqu \n0(%rsi), %ymm8
	vmovdqu \n1(%rsi), %ymm9
	vmovdqu \n2(%rsi), %ymm10
	vmovdqu \n3(%rsi), %ymm11
	vpmullw %ymm15, %ymm0, %ymm0
	vpmullw %ymm15, %ymm1, %ymm1
	vpmullw %ymm15, %ymm2, %ymm2
	vpmullw %ymm15, %ymm3, %ymm3
	vpsubw %ymm0, \a, \a
	vpsubw %ymm1, \b, \b
	vpsubw %ymm2, \c, \c
	vpsubw %ymm3, \d, \d
	vpsraw $15, \a, %ymm0
	vpsraw $15, \b, %ymm1
	vpsraw $15, \c, %ymm2
	vpsraw $15, \d, %ymm3
	vpand %ymm15, %ymm0, %ymm0
	vpand %ymm15, %ymm1, %ymm1
	vpand %ymm15, %ymm2, %ymm2
	vpand %ymm15, %ymm3, %ymm3
	vpaddw %ymm0, \a, \a
	vpaddw %ymm1, \b, \b
	vpaddw %ymm2, \c, \c
	vpaddw %ymm3, \d, \d
	vpmaddwd .Lq24_pair_factor(%rip), \a, \a
	vpmaddwd .Lq24_pair_factor(%rip), \b, \b
	vpmaddwd .Lq24_pair_factor(%rip), \c, \c
	vpmaddwd .Lq24_pair_factor(%rip), \d, \d
	vpshufb .Lq24_pack_mask(%rip), \a, \a
	vpshufb .Lq24_pack_mask(%rip), \b, \b
	vpshufb .Lq24_pack_mask(%rip), \c, \c
	vpshufb .Lq24_pack_mask(%rip), \d, \d
.endm

.macro Q24_STORE_SCATTER_PACKET low,lowx,lowhalf,high,highx,highhalf,offset,safe
.if \lowhalf
	vextracti128 $1, \low, %xmm14
	vmovdqu %xmm14, \offset(%rdi)
.else
	vmovdqu \lowx, \offset(%rdi)
.endif
.if \highhalf
	vextracti128 $1, \high, %xmm14
.if \safe
	vmovq %xmm14, \offset+12(%rdi)
	vpextrd $2, %xmm14, \offset+20(%rdi)
.else
	vmovdqu %xmm14, \offset+12(%rdi)
.endif
.else
.if \safe
	vmovq \highx, \offset+12(%rdi)
	vpextrd $2, \highx, \offset+20(%rdi)
.else
	vmovdqu \highx, \offset+12(%rdi)
.endif
.endif
.endm

#include "../generated/tile4_q24_lazy_schedules.inc"
#include "../generated/tile4_q24_encap_highrange.inc"
#include "../generated/tile4_q24_p_encode.inc"
#include "../generated/tile4_q24_pack3_compact.inc"

/* C1 code-density probe.  Each table entry is {M source byte offset,
 * serialized destination byte offset}.  The five ordinary route classes and
 * the safe final packet retain the exact production transpose, v=9 reducer,
 * canonicalization and Q24 store atoms. */
	.section .rodata.gt32_q24_hotcompact_c1,"a",@progbits
	.p2align 1
.Lq24_hc_a:
	.short 0,0, 128,96, 768,768, 896,864
.Lq24_hc_b:
	.short 1152,192, 384,960
.Lq24_hc_c:
	.short 1024,288
.Lq24_hc_d:
	.short 512,384, 640,480, 1280,672
.Lq24_hc_e:
	.short 1408,576
.Lq24_hc_f:
	.short 256,1056

.macro Q24_HOTCOMPACT_C1_BLOCK a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
	vmovdqu 0(%rax), %ymm0
	vmovdqu 32(%rax), %ymm1
	vmovdqu 64(%rax), %ymm2
	vmovdqu 96(%rax), %ymm3
	Q24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	Q24_LAZY_QUAD_REDUCE \a,\ax,\ap,0,0,\b,\bx,\bp,24,0,\c,\cx,\cp,48,0,\d,\dx,\dp,72,\safe
	Q24_LAZY_PACK4 \a,\ax,\ap,0,0,\b,\bx,\bp,24,0,\c,\cx,\cp,48,0,\d,\dx,\dp,72,\safe
.endm

.macro Q24_HOTCOMPACT_C1_LOOP table,count,a,ax,ap,b,bx,bp,c,cx,cp,d,dx,dp,safe
	leaq \table(%rip), %r8
	movl $\count, %r9d
.Lq24_hc_loop_\@:
	movzwl 0(%r8), %eax
	leaq (%rsi,%rax), %rax
	movzwl 2(%r8), %edi
	addq %r10, %rdi
	Q24_HOTCOMPACT_C1_BLOCK \a,\ax,\ap,\b,\bx,\bp,\c,\cx,\cp,\d,\dx,\dp,\safe
	addq $4, %r8
	decl %r9d
	jnz .Lq24_hc_loop_\@
.endm

	.section .text.gt32_q24_encode_soa_lazy10788_compact_c1_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_lazy10788_compact_c1_asm
	.type gt32_q24_encode_soa_lazy10788_compact_c1_asm,@function
gt32_q24_encode_soa_lazy10788_compact_c1_asm:
	movq %rdi, %r10
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	/* Route-class order is not serialized order.  Use the safe 12-byte tail
	 * for every block's fourth packet so an earlier class cannot overstore the
	 * first four bytes of a block emitted by a later class. */
	Q24_HOTCOMPACT_C1_LOOP .Lq24_hc_a,4,%ymm7,%xmm7,177,%ymm6,%xmm6,75,%ymm4,%xmm4,75,%ymm5,%xmm5,75,1
	Q24_HOTCOMPACT_C1_LOOP .Lq24_hc_b,2,%ymm4,%xmm4,228,%ymm5,%xmm5,228,%ymm6,%xmm6,228,%ymm7,%xmm7,228,1
	Q24_HOTCOMPACT_C1_LOOP .Lq24_hc_c,1,%ymm6,%xmm6,228,%ymm7,%xmm7,228,%ymm5,%xmm5,228,%ymm4,%xmm4,30,1
	Q24_HOTCOMPACT_C1_LOOP .Lq24_hc_d,3,%ymm5,%xmm5,30,%ymm4,%xmm4,177,%ymm7,%xmm7,30,%ymm6,%xmm6,177,1
	Q24_HOTCOMPACT_C1_LOOP .Lq24_hc_e,1,%ymm6,%xmm6,30,%ymm7,%xmm7,30,%ymm5,%xmm5,30,%ymm4,%xmm4,177,1
	Q24_HOTCOMPACT_C1_LOOP .Lq24_hc_f,1,%ymm6,%xmm6,228,%ymm7,%xmm7,228,%ymm5,%xmm5,228,%ymm4,%xmm4,30,1
	vzeroupper
	ret
	.size gt32_q24_encode_soa_lazy10788_compact_c1_asm,.-gt32_q24_encode_soa_lazy10788_compact_c1_asm

	.section .text.gt32_q24_encode_soa_lazy10788_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_lazy10788_asm
	.type gt32_q24_encode_soa_lazy10788_asm,@function
gt32_q24_encode_soa_lazy10788_asm:
.Lq24_lazy_cage_begin:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
#if Q24_LAZY_SCHEDULE == 0
#if defined(Q24_M_TF1_PRODUCTION) && Q24_M_TF1_PRODUCTION
	Q24_ENCODE_SOA_TF1_BODY
#else
	Q24_ENCODE_SOA_BODY
#endif
#elif Q24_LAZY_SCHEDULE == 1
	Q24_ENCODE_SOA_L1_BODY
#elif Q24_LAZY_SCHEDULE == 2
	Q24_ENCODE_SOA_L2_BODY
#elif Q24_LAZY_SCHEDULE == 3
	Q24_ENCODE_SOA_L3_BODY
#else
#error "unsupported Q24_LAZY_SCHEDULE"
#endif
	vzeroupper
	ret
	.org .Lq24_lazy_cage_begin + 5120, 0x90
	.size gt32_q24_encode_soa_lazy10788_asm,.-gt32_q24_encode_soa_lazy10788_asm

#if defined(Q24_M_TF1_GATE)
	/* Benchmark-only M-domain TF1 probe.  Match the production L0 control's
	 * cage so unrelated following-symbol addresses do not move. */
	.section .text.gt32_q24_encode_soa_tf1_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_tf1_asm
	.type gt32_q24_encode_soa_tf1_asm,@function
gt32_q24_encode_soa_tf1_asm:
.Lq24_tf1_cage_begin:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_SOA_TF1_BODY
	vzeroupper
	ret
	.org .Lq24_tf1_cage_begin + 5120, 0x90
	.size gt32_q24_encode_soa_tf1_asm,.-gt32_q24_encode_soa_tf1_asm
#endif

	/*
	 * Benchmark-only M-domain serializer with the two packet constants kept
	 * resident.  This preserves the qualified packet order and v=9 reducer,
	 * while replacing 48 pair-factor and 48 pack-mask memory operands by
	 * register operands.
	 */
.macro Q24_ENCODE_RR_PACKET src,srcx,perm,offset,safe
	vpmulhrsw %ymm13, \src, %ymm14
	vpmullw %ymm15, %ymm14, %ymm14
	vpsubw %ymm14, \src, \src
	vpermq $\perm, \src, \src
	vpsraw $15, \src, %ymm14
	vpand %ymm15, %ymm14, %ymm14
	vpaddw %ymm14, \src, \src
	vpmaddwd %ymm12, \src, \src
	vpshufb %ymm11, \src, \src
	vmovdqu \srcx, \offset(%rdi)
	vextracti128 $1, \src, %xmm14
.if \safe
	vmovq %xmm14, \offset+12(%rdi)
	vpextrd $2, %xmm14, \offset+20(%rdi)
.else
	vmovdqu %xmm14, \offset+12(%rdi)
.endif
.endm

	.purgem Q24_ENCODE_MEM_PACKET
.macro Q24_ENCODE_MEM_PACKET in,perm,offset,safe
	vmovdqu \in(%rsi), %ymm0
	Q24_ENCODE_RR_PACKET %ymm0,%xmm0,\perm,\offset,\safe
.endm

	.section .text.gt32_q24_encode_soa_lazy10788_rr_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_lazy10788_rr_asm
	.type gt32_q24_encode_soa_lazy10788_rr_asm,@function
gt32_q24_encode_soa_lazy10788_rr_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	vmovdqa .Lq24_pair_factor(%rip), %ymm12
	vmovdqa .Lq24_pack_mask(%rip), %ymm11
	Q24_ENCODE_SOA_RR_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_soa_lazy10788_rr_asm,.-gt32_q24_encode_soa_lazy10788_rr_asm

	/* Restore the generic generated-body hook for subsequent typed packers. */
	.purgem Q24_ENCODE_MEM_PACKET
.macro Q24_ENCODE_MEM_PACKET in,perm,offset,safe
	vmovdqu \in(%rsi), %ymm0
	Q24_ENCODE_REG_PACKET %ymm0,%xmm0,\perm,\offset,\safe
.endm

	/* Progressive-P typed keygen pack. */
	.section .text.gt32_q24_encode_p_soa_lazy10788_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_p_soa_lazy10788_asm
	.type gt32_q24_encode_p_soa_lazy10788_asm,@function
gt32_q24_encode_p_soa_lazy10788_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_P_SOA_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_p_soa_lazy10788_asm,.-gt32_q24_encode_p_soa_lazy10788_asm

	.section .text.gt32_q24_encode_p_soa_halfscatter_lazy10788_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_p_soa_halfscatter_lazy10788_asm
	.type gt32_q24_encode_p_soa_halfscatter_lazy10788_asm,@function
gt32_q24_encode_p_soa_halfscatter_lazy10788_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_P_SOA_HALF_SCATTER_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_p_soa_halfscatter_lazy10788_asm,.-gt32_q24_encode_p_soa_halfscatter_lazy10788_asm

	/* Benchmark-only transpose-tail orientation fusion probe. */
	.section .text.gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm
	.type gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm,@function
gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_P_SOA_HALF_SCATTER_TF1_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm,.-gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm

	/* Compact three-polynomial TF1 scheduling probe.
	 * Args: out0,in0,out1,in1,out2,in2 in SysV register order. */
	.section .text.gt32_q24_encode_p_soa_pack3_tf1_compact_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_p_soa_pack3_tf1_compact_asm
	.type gt32_q24_encode_p_soa_pack3_tf1_compact_asm,@function
gt32_q24_encode_p_soa_pack3_tf1_compact_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_P_SOA_PACK3_COMPACT_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_p_soa_pack3_tf1_compact_asm,.-gt32_q24_encode_p_soa_pack3_tf1_compact_asm

	/* Benchmark-only TF1 next-block preload scheduling probe. */
	.section .text.gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm
	.type gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm,@function
gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_P_SOA_HALF_SCATTER_SP1_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm,.-gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm

	/* Benchmark-only register-resident pair/pack constant probe. */
	.purgem Q24_HALF_REDUCE_PACK4
.macro Q24_HALF_REDUCE_PACK4 a,b,c,d
	Q24_LAZY_QUAD_REDUCE \a,%xmm4,0,0,0,\b,%xmm5,0,0,0,\c,%xmm6,0,0,0,\d,%xmm7,0,0,0
	vpsraw $15, \a, %ymm0
	vpsraw $15, \b, %ymm1
	vpsraw $15, \c, %ymm2
	vpsraw $15, \d, %ymm3
	vpand %ymm15, %ymm0, %ymm0
	vpand %ymm15, %ymm1, %ymm1
	vpand %ymm15, %ymm2, %ymm2
	vpand %ymm15, %ymm3, %ymm3
	vpaddw %ymm0, \a, \a
	vpaddw %ymm1, \b, \b
	vpaddw %ymm2, \c, \c
	vpaddw %ymm3, \d, \d
	vpmaddwd %ymm12, \a, \a
	vpmaddwd %ymm12, \b, \b
	vpmaddwd %ymm12, \c, \c
	vpmaddwd %ymm12, \d, \d
	vpshufb %ymm11, \a, \a
	vpshufb %ymm11, \b, \b
	vpshufb %ymm11, \c, \c
	vpshufb %ymm11, \d, \d
.endm

	.section .text.gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm
	.type gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm,@function
gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	vmovdqa .Lq24_pair_factor(%rip), %ymm12
	vmovdqa .Lq24_pack_mask(%rip), %ymm11
	Q24_ENCODE_P_SOA_HALF_SCATTER_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm,.-gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm

	/*
	 * Typed encap high-range H1.  The proven |x| <= 12699 contract is a
	 * subset of the qualified v=9 reducer's exact domain, so retain the
	 * production-qualified packet-first body and its fixed placement.
	 */
	.section .text.gt32_q24_encode_soa_encap_hr_h1_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_encap_hr_h1_asm
	.type gt32_q24_encode_soa_encap_hr_h1_asm,@function
gt32_q24_encode_soa_encap_hr_h1_asm:
	jmp gt32_q24_encode_soa_lazy10788_asm
	.size gt32_q24_encode_soa_encap_hr_h1_asm,.-gt32_q24_encode_soa_encap_hr_h1_asm

	/*
	 * Serializer-side Encap sum gate.
	 *
	 * rsi: B3-general private-SoA e=0 product
	 * rdx: N5 private-SoA e=0 message
	 *
	 * Each source block is added before the frozen M->Q24 transpose.  The
	 * proven |product + message| <= 12699 contract is then handled by the
	 * same v=9 reducer and packet route as the production H1 serializer.
	 */
	.section .text.gt32_q24_encode_soa_encap_hr_sum_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_encap_hr_sum_asm
	.type gt32_q24_encode_soa_encap_hr_sum_asm,@function
gt32_q24_encode_soa_encap_hr_sum_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_SOA_SUM_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_soa_encap_hr_sum_asm,.-gt32_q24_encode_soa_encap_hr_sum_asm

	/* H2: canonicalize each four-plane source block before packet routing. */
	.macro Q24_HR_REDUCE4 a,b,c,d
	vpmulhrsw %ymm13, \a, %ymm8
	vpmulhrsw %ymm13, \b, %ymm9
	vpmulhrsw %ymm13, \c, %ymm10
	vpmulhrsw %ymm13, \d, %ymm11
	vpmullw %ymm15, %ymm8, %ymm8
	vpmullw %ymm15, %ymm9, %ymm9
	vpmullw %ymm15, %ymm10, %ymm10
	vpmullw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8, \a, \a
	vpsubw %ymm9, \b, \b
	vpsubw %ymm10, \c, \c
	vpsubw %ymm11, \d, \d
	.endm

	.section .text.gt32_q24_encode_soa_encap_hr_h2_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_encap_hr_h2_asm
	.type gt32_q24_encode_soa_encap_hr_h2_asm,@function
gt32_q24_encode_soa_encap_hr_h2_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	Q24_ENCODE_SOA_ENCAP_HR_H2_BODY
	vzeroupper
	ret
	.size gt32_q24_encode_soa_encap_hr_h2_asm,.-gt32_q24_encode_soa_encap_hr_h2_asm

	/*
	 * Benchmark-only final-check boundary.  The packed Q24 bytes are compared
	 * directly with the canonical expected string in rdi and are never
	 * materialized.  rsi remains the private-SoA lazy10788 input.  The return
	 * value is exactly verify_bytes semantics: zero for equal, one otherwise.
	 */
	.purgem Q24_ENCODE_REG_PACKET
.macro Q24_ENCODE_REG_PACKET src,srcx,perm,offset,safe
	/* Preserve the qualified lazy10788 reduction and packet mathematics. */
	vpmulhrsw %ymm13, \src, %ymm14
	vpmullw %ymm15, %ymm14, %ymm14
	vpsubw %ymm14, \src, \src
	vpermq $\perm, \src, \src
	vpsraw $15, \src, %ymm14
	vpand %ymm15, %ymm14, %ymm14
	vpaddw %ymm14, \src, \src
	vpmaddwd .Lq24_pair_factor(%rip), \src, \src
	vpshufb .Lq24_pack_mask(%rip), \src, \src

	/*
	 * Form one padded expected YMM and compare the complete packet at once.
	 * Three independent accumulators avoid a 48-packet vpor dependency chain.
	 */
	vmovdqu \offset(%rdi), %xmm14
.if \safe
	vmovq \offset+12(%rdi), %xmm10
	vpinsrd $2, \offset+20(%rdi), %xmm10, %xmm10
.else
	vmovdqu \offset+12(%rdi), %xmm10
.endif
	vinserti128 $1, %xmm10, %ymm14, %ymm14
	vpxor \src, %ymm14, %ymm14
	vpand %ymm11, %ymm14, %ymm14
.if ((\offset / 24) % 3) == 0
	vpor %ymm14, %ymm8, %ymm8
.elseif ((\offset / 24) % 3) == 1
	vpor %ymm14, %ymm9, %ymm9
.else
	vpor %ymm14, %ymm12, %ymm12
.endif
.endm

	.section .text.gt32_q24_encode_soa_lazy10788_verify_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_encode_soa_lazy10788_verify_asm
	.type gt32_q24_encode_soa_lazy10788_verify_asm,@function
gt32_q24_encode_soa_lazy10788_verify_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm13
	vmovdqa .Lq24_compare12(%rip), %ymm11
	vpxor %ymm8, %ymm8, %ymm8
	vpxor %ymm9, %ymm9, %ymm9
	vpxor %xmm12, %xmm12, %xmm12
	Q24_ENCODE_SOA_BODY
	vpor %ymm9, %ymm8, %ymm8
	vpor %ymm12, %ymm8, %ymm8
	vptest %ymm8, %ymm8
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_q24_encode_soa_lazy10788_verify_asm,.-gt32_q24_encode_soa_lazy10788_verify_asm

	/*
	 * Decapsulation-native final equality check.  Both inputs use the same
	 * private BM SoA physical mapping and Montgomery exponent e=0.  For
	 * |recovered| <= 1911 and |derived| <= 10788, the signed word difference
	 * is in [-12699,12699].  The v=9 centered reducer is exact on this range;
	 * therefore the OR accumulator is zero iff every lane is congruent mod q.
	 */
	.section .text.gt32_tile4_soa_equal_modq_12699_asm,"ax",@progbits
	.p2align 5
	.globl gt32_tile4_soa_equal_modq_12699_asm
	.type gt32_tile4_soa_equal_modq_12699_asm,@function
gt32_tile4_soa_equal_modq_12699_asm:
	vmovdqa .Lq24_q(%rip), %ymm15
	vmovdqa .Lq24_v(%rip), %ymm14
	vpxor %ymm0, %ymm0, %ymm0
	mov $48, %eax
.Lsoa_equal_modq_loop:
	vmovdqa 0(%rdi), %ymm1
	vpsubw 0(%rsi), %ymm1, %ymm1
	vpmulhrsw %ymm14, %ymm1, %ymm2
	vpmullw %ymm15, %ymm2, %ymm2
	vpsubw %ymm2, %ymm1, %ymm1
	vpor %ymm1, %ymm0, %ymm0
	add $32, %rdi
	add $32, %rsi
	dec %eax
	jnz .Lsoa_equal_modq_loop
	vptest %ymm0, %ymm0
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_tile4_soa_equal_modq_12699_asm,.-gt32_tile4_soa_equal_modq_12699_asm

	.section .rodata
	.p2align 5
.Lq24_low12:
	.rept 16
	.short 4095
	.endr
.Lq24_qm1:
	.rept 16
	.short 3456
	.endr
.Lq24_q:
	.rept 16
	.short 3457
	.endr
.Lq24_v:
	.rept 16
	.short 9
	.endr
	.p2align 5
.Lq24_compare12:
	.rept 2
		.rept 12
		.byte 0xff
		.endr
		.rept 4
		.byte 0
		.endr
	.endr
.Lq24_pair_factor:
	.rept 8
	.short 1,4096
	.endr
.Lq24_pack_mask:
	.byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
	.byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128

	.section .note.GNU-stack,"",@progbits
