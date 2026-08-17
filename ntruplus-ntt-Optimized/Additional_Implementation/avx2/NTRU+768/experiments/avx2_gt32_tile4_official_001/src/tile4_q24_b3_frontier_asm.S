/* Benchmark-only Q24 Decode(c,f) -> first scale-B3 streaming frontier. */

	.text

	.macro Q24_B3_DECODE_PACKET low,high,safelow,safehigh,mask,base,dst
.if \safelow
	vmovq \low(%\base), %xmm14
	vpinsrd $2, \low+8(%\base), %xmm14, %xmm14
.else
	vmovdqu \low(%\base), %xmm14
.endif
.if \safehigh
	vmovq \high(%\base), %xmm15
	vpinsrd $2, \high+8(%\base), %xmm15, %xmm15
.else
	vmovdqu \high(%\base), %xmm15
.endif
	vinserti128 $1, %xmm15, %ymm14, %\dst
	vpshufb \mask(%rip), %\dst, %\dst
	vpsrlw $4, %\dst, %ymm14
	vpblendw $0xaa, %ymm14, %\dst, %\dst
	vpand %ymm13, %\dst, %\dst
	.endm

	/* Collapse one four-packet group before B3 takes all sixteen YMMs. */
	.macro Q24_B3_VALIDATE4 a,b,c,d
	vpmaxuw %\b, %\a, %ymm14
	vpmaxuw %\d, %\c, %ymm15
	vpmaxuw %ymm15, %ymm14, %ymm14
	vpcmpgtw .Lq24_b3_qm1(%rip), %ymm14, %ymm14
	vpmovmskb %ymm14, %r10d
	orl %r10d, %eax
	.endm

	.macro Q24_B3_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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

	.macro Q24_B3_MONT_FIRST a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm15, %ymm15
	.endm

	.macro Q24_B3_MONT_ADD a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm14
	vpaddw  %ymm14, %ymm15, %ymm15
	.endm

	.macro Q24_B3_MONT_LAMBDA offset
	vpmullw .Ltile4_bm_lambda_qinv+\offset(%rip), %ymm15, %ymm13
	vpmulhw .Ltile4_bm_lambda+\offset(%rip), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	/* Exact production B3 arithmetic/output sequence with register inputs. */
	.macro Q24_B3_SCALE_BLOCK outoff,lambdaoff
	vpmullw .Lq24_b3_qinv(%rip), %ymm1, %ymm5
	vpmullw .Lq24_b3_qinv(%rip), %ymm2, %ymm6
	vpmullw .Lq24_b3_qinv(%rip), %ymm3, %ymm7
	vpmullw .Lq24_b3_qinv(%rip), %ymm4, %ymm8

	Q24_B3_MONT_FIRST ymm2,ymm6,ymm12
	Q24_B3_MONT_ADD   ymm3,ymm7,ymm11
	Q24_B3_MONT_ADD   ymm4,ymm8,ymm10
	Q24_B3_MONT_LAMBDA \lambdaoff
	Q24_B3_MONT_ADD   ymm1,ymm5,ymm9
	vmovdqu %ymm15, \outoff(%rdi)

	Q24_B3_MONT_FIRST ymm3,ymm7,ymm12
	Q24_B3_MONT_ADD   ymm4,ymm8,ymm11
	Q24_B3_MONT_LAMBDA \lambdaoff
	Q24_B3_MONT_ADD   ymm1,ymm5,ymm10
	Q24_B3_MONT_ADD   ymm2,ymm6,ymm9
	vmovdqu %ymm15, \outoff+32(%rdi)

	Q24_B3_MONT_FIRST ymm4,ymm8,ymm12
	Q24_B3_MONT_LAMBDA \lambdaoff
	Q24_B3_MONT_ADD   ymm1,ymm5,ymm11
	Q24_B3_MONT_ADD   ymm2,ymm6,ymm10
	Q24_B3_MONT_ADD   ymm3,ymm7,ymm9
	vmovdqu %ymm15, \outoff+64(%rdi)

	Q24_B3_MONT_FIRST ymm1,ymm5,ymm12
	Q24_B3_MONT_ADD   ymm2,ymm6,ymm11
	Q24_B3_MONT_ADD   ymm3,ymm7,ymm10
	Q24_B3_MONT_ADD   ymm4,ymm8,ymm9

	/* Production late-c3 center and four-plane -> AoS materialization. */
	vpmulhrsw .Lq24_b3_center10(%rip), %ymm15, %ymm14
	vmovdqu \outoff(%rdi), %ymm1
	vmovdqu \outoff+32(%rdi), %ymm2
	vmovdqu \outoff+64(%rdi), %ymm3
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	Q24_B3_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
	vmovdqu %ymm5, \outoff(%rdi)
	vmovdqu %ymm6, \outoff+32(%rdi)
	vmovdqu %ymm7, \outoff+64(%rdi)
	vmovdqu %ymm8, \outoff+96(%rdi)
	.endm

	.section .text.gt32_q24_decode2_b3_scale_stream_asm,"ax",@progbits
	.p2align 5
	.globl gt32_q24_decode2_b3_scale_stream_asm
	.type gt32_q24_decode2_b3_scale_stream_asm,@function
gt32_q24_decode2_b3_scale_stream_asm:
	xorl %eax, %eax
	vmovdqa .Lq24_b3_q(%rip), %ymm0
#include "../generated/tile4_q24_b3_frontier.inc"
	testl %eax, %eax
	setne %al
	movzbl %al, %eax
	vzeroupper
	ret
	.size gt32_q24_decode2_b3_scale_stream_asm,.-gt32_q24_decode2_b3_scale_stream_asm

	.section .rodata
	.p2align 5
.Lq24_b3_low12:
	.rept 16
	.short 4095
	.endr
.Lq24_b3_qm1:
	.rept 16
	.short 3456
	.endr
.Lq24_b3_q:
	.rept 16
	.short 3457
	.endr
.Lq24_b3_qinv:
	.rept 16
	.short 12929
	.endr
.Lq24_b3_center10:
	.rept 16
	.short 10
	.endr

	.p2align 5
.Lq24_decode_mask_0123:
	.byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
	.byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
.Lq24_decode_mask_1032:
	.byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5
	.byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5
.Lq24_decode_mask_2310:
	.byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5
	.byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
.Lq24_decode_mask_3201:
	.byte 0,1,1,2,3,4,4,5,6,7,7,8,9,10,10,11
	.byte 6,7,7,8,9,10,10,11,0,1,1,2,3,4,4,5

#include "../generated/tile4_basemul_constants.inc"

	.section .note.GNU-stack,"",@progbits
