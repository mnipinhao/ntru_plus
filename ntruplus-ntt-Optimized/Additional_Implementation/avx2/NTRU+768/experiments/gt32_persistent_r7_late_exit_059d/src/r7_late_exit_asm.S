/* 059D: executable persistent-R7 late K_lambda + REDC32 + Q24 exit. */

	.text

	.macro R7_REDC_HALF src,dst
	vpmullw .Lr7_qinv(%rip), \src, %ymm13
	/* Signed m keeps |m|<=32768 and the REDC output within one q. */
	vpmulhw .Lr7_q(%rip), %ymm13, %ymm13
	vpsrad $16, \src, \src
	vpsubw %ymm13, \src, \src
	vpshufb .Lr7_compact_even(%rip), \src, \src
	vpermq $0xd8, \src, \dst
	.endm

	/* ymm0/1 are pair 0 low/high; ymm2/3 are pair 1 low/high. */
	.macro R7_DOT_COEFFICIENT koff,dst
	vpmaddwd \koff+0(%rdx), %ymm0, %ymm12
	vpmaddwd \koff+64(%rdx), %ymm2, %ymm13
	vpaddd %ymm13, %ymm12, %ymm12
	R7_REDC_HALF %ymm12,%ymm14

	vpmaddwd \koff+32(%rdx), %ymm1, %ymm12
	vpmaddwd \koff+96(%rdx), %ymm3, %ymm13
	vpaddd %ymm13, %ymm12, %ymm12
	R7_REDC_HALF %ymm12,%ymm15

	vpunpcklqdq %ymm15, %ymm14, %ymm11
	vpunpckhqdq %ymm15, %ymm14, %ymm13
	vperm2i128 $0x20, %ymm13, %ymm11, \dst
	.endm

	.macro R7_BUILD_PAIR aoff,boff,lo,hi
	vmovdqu \aoff(%rsi), %ymm4
	vmovdqu \boff(%rsi), %ymm5
	vpunpcklwd %ymm5, %ymm4, \lo
	vpunpckhwd %ymm5, %ymm4, \hi
	.endm

	.macro R7_BUILD_ZERO_PAIR aoff,lo,hi
	vmovdqu \aoff(%rsi), %ymm4
	vpxor %ymm5, %ymm5, %ymm5
	vpunpcklwd %ymm5, %ymm4, \lo
	vpunpckhwd %ymm5, %ymm4, \hi
	.endm

	.macro R7_TRANSPOSE
	vpunpcklwd %ymm10, %ymm8, %ymm0
	vpunpckhwd %ymm10, %ymm8, %ymm1
	vpunpcklwd %ymm4, %ymm9, %ymm2
	vpunpckhwd %ymm4, %ymm9, %ymm3
	vpunpckldq %ymm2, %ymm0, %ymm8
	vpunpckhdq %ymm2, %ymm0, %ymm10
	vpunpckldq %ymm3, %ymm1, %ymm9
	vpunpckhdq %ymm3, %ymm1, %ymm4
	vpunpcklqdq %ymm9, %ymm8, %ymm0
	vpunpckhqdq %ymm9, %ymm8, %ymm1
	vpunpcklqdq %ymm4, %ymm10, %ymm2
	vpunpckhqdq %ymm4, %ymm10, %ymm3
	.endm

	.macro R7_PACK src,perm,outoff,safe
	vpermq $\perm, \src, \src
	vpsraw $15, \src, %ymm14
	vpand .Lr7_q(%rip), %ymm14, %ymm14
	vpaddw %ymm14, \src, \src
	vpmaddwd .Lr7_pair_factor(%rip), \src, \src
	vpshufb .Lr7_pack_mask(%rip), \src, \src
	vextracti128 $0, \src, %xmm14
	vmovdqu %xmm14, \outoff(%rdi)
	vextracti128 $1, \src, %xmm14
	.if \safe
	vmovq %xmm14, \outoff+12(%rdi)
	vpextrd $2, %xmm14, \outoff+20(%rdi)
	.else
	vmovdqu %xmm14, \outoff+12(%rdi)
	.endif
	.endm

	/* Input block is seven contiguous YMM planes in H-domain order. */
	.macro R7_FORM_BLOCK inoff,koff
	/* Even support: (P0,S1), (S2,S4) -> c0,c2. */
	R7_BUILD_PAIR \inoff+0,\inoff+32,%ymm0,%ymm1
	R7_BUILD_PAIR \inoff+96,\inoff+160,%ymm2,%ymm3
	leaq .Lr7_k_table+\koff(%rip), %rdx
	R7_DOT_COEFFICIENT 0,%ymm8
	R7_DOT_COEFFICIENT 256,%ymm9

	/* Odd support: (D1,D2), (D4,zero) -> c1,c3. */
	R7_BUILD_PAIR \inoff+64,\inoff+128,%ymm0,%ymm1
	R7_BUILD_ZERO_PAIR \inoff+192,%ymm2,%ymm3
	R7_DOT_COEFFICIENT 128,%ymm10
	R7_DOT_COEFFICIENT 384,%ymm4
	R7_TRANSPOSE
	.endm

	/* t0,t1,t2,t3 are ymm0,ymm1,ymm2,ymm3 after R7_TRANSPOSE. */
	.macro R7_FULL_BLOCK inblock,kblock,outoff,o0,p0,o1,p1,o2,p2,o3,p3,safe
	R7_FORM_BLOCK (\inblock*224),(\kblock*512)
	R7_PACK %ymm\o0,\p0,\outoff+0,0
	R7_PACK %ymm\o1,\p1,\outoff+24,0
	R7_PACK %ymm\o2,\p2,\outoff+48,0
	R7_PACK %ymm\o3,\p3,\outoff+72,\safe
	.endm

	.section .text.r7_late_exit_block0_asm,"ax",@progbits
	.p2align 5
	.globl r7_late_exit_block0_asm
	.type r7_late_exit_block0_asm,@function
r7_late_exit_block0_asm:
	R7_FORM_BLOCK 0,0
	R7_PACK %ymm3,177,0,0
	R7_PACK %ymm2,75,24,0
	R7_PACK %ymm0,75,48,0
	R7_PACK %ymm1,75,72,1
	vzeroupper
	ret
	.size r7_late_exit_block0_asm,.-r7_late_exit_block0_asm

	.section .text.r7_late_exit_full_asm,"ax",@progbits
	.p2align 5
	.globl r7_late_exit_full_asm
	.type r7_late_exit_full_asm,@function
r7_late_exit_full_asm:
	/* True production wire order: 0,1,9,8,4,5,11,10,6,7,3,2. */
	R7_FULL_BLOCK 0,0,0,3,177,2,75,0,75,1,75,0
	R7_FULL_BLOCK 1,1,96,3,177,2,75,0,75,1,75,0
	R7_FULL_BLOCK 9,9,192,0,228,1,228,2,228,3,228,0
	R7_FULL_BLOCK 8,8,288,2,228,3,228,1,228,0,30,0
	R7_FULL_BLOCK 4,4,384,1,30,0,177,3,30,2,177,0
	R7_FULL_BLOCK 5,5,480,1,30,0,177,3,30,2,177,0
	R7_FULL_BLOCK 11,11,576,2,30,3,30,1,30,0,177,0
	R7_FULL_BLOCK 10,10,672,1,30,0,177,3,30,2,177,0
	R7_FULL_BLOCK 6,6,768,3,177,2,75,0,75,1,75,0
	R7_FULL_BLOCK 7,7,864,3,177,2,75,0,75,1,75,0
	R7_FULL_BLOCK 3,3,960,0,228,1,228,2,228,3,228,0
	R7_FULL_BLOCK 2,2,1056,2,228,3,228,1,228,0,30,1
	vzeroupper
	ret
	.size r7_late_exit_full_asm,.-r7_late_exit_full_asm

	/* Centered quartic block-0 control with exactly the same 96-byte endpoint. */
	.section .text.r7_current_q24_block0_asm,"ax",@progbits
	.p2align 5
	.globl r7_current_q24_block0_asm
	.type r7_current_q24_block0_asm,@function
r7_current_q24_block0_asm:
	vmovdqu 0(%rsi), %ymm8
	vmovdqu 32(%rsi), %ymm10
	vmovdqu 64(%rsi), %ymm9
	vmovdqu 96(%rsi), %ymm4
	R7_TRANSPOSE
	R7_PACK %ymm3,177,0,0
	R7_PACK %ymm2,75,24,0
	R7_PACK %ymm0,75,48,0
	R7_PACK %ymm1,75,72,1
	vzeroupper
	ret
	.size r7_current_q24_block0_asm,.-r7_current_q24_block0_asm

	.section .rodata
	.p2align 5
.Lr7_q:
	.rept 16
	.short 3457
	.endr
.Lr7_qinv:
	.rept 16
	.short 12929
	.endr
.Lr7_pair_factor:
	.rept 8
	.short 1,4096
	.endr
.Lr7_compact_even:
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
.Lr7_pack_mask:
	.byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
	.byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
	.p2align 5
.Lr7_k_table:
#include "../../gt32_persistent_r7_encap_059c/generated/persistent_r7_late_exit_constants.inc"

	.section .note.GNU-stack,"",@progbits
