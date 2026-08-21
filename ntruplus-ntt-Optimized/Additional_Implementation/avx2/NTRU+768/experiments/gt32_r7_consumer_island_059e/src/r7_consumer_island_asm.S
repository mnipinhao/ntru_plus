/* 059E: scale-deferred, H-elided R7 point-product/message/Q24 island. */

	.text

	.macro R7E_MONT_POINT hoff,roff,moff,koff,first
	vmovdqu \hoff(%rsi), %ymm8
	vmovdqu \roff(%rdx), %ymm9
	vpmullw .Lr7e_qinv(%rip), %ymm8, %ymm10
	vpmullw %ymm9, %ymm10, %ymm10
	vpmulhw %ymm9, %ymm8, %ymm8
	vpmulhw .Lr7e_q(%rip), %ymm10, %ymm10
	vpsubw %ymm10, %ymm8, %ymm8
	vmovdqu \moff(%rcx), %ymm9
	vpunpcklwd %ymm9, %ymm8, %ymm11
	vpunpckhwd %ymm9, %ymm8, %ymm12
	.if \first
	vpmaddwd \koff+0(%r8), %ymm11, %ymm0
	vpmaddwd \koff+32(%r8), %ymm12, %ymm1
	vpmaddwd \koff+64(%r8), %ymm11, %ymm2
	vpmaddwd \koff+96(%r8), %ymm12, %ymm3
	vpmaddwd \koff+128(%r8), %ymm11, %ymm4
	vpmaddwd \koff+160(%r8), %ymm12, %ymm5
	vpmaddwd \koff+192(%r8), %ymm11, %ymm6
	vpmaddwd \koff+224(%r8), %ymm12, %ymm7
	.else
	vpmaddwd \koff+0(%r8), %ymm11, %ymm13
	vpaddd %ymm13, %ymm0, %ymm0
	vpmaddwd \koff+32(%r8), %ymm12, %ymm13
	vpaddd %ymm13, %ymm1, %ymm1
	vpmaddwd \koff+64(%r8), %ymm11, %ymm13
	vpaddd %ymm13, %ymm2, %ymm2
	vpmaddwd \koff+96(%r8), %ymm12, %ymm13
	vpaddd %ymm13, %ymm3, %ymm3
	vpmaddwd \koff+128(%r8), %ymm11, %ymm13
	vpaddd %ymm13, %ymm4, %ymm4
	vpmaddwd \koff+160(%r8), %ymm12, %ymm13
	vpaddd %ymm13, %ymm5, %ymm5
	vpmaddwd \koff+192(%r8), %ymm11, %ymm13
	vpaddd %ymm13, %ymm6, %ymm6
	vpmaddwd \koff+224(%r8), %ymm12, %ymm13
	vpaddd %ymm13, %ymm7, %ymm7
	.endif
	.endm

	.macro R7E_REDC_HALF src,dst
	vpmullw .Lr7e_qinv(%rip), \src, %ymm13
	vpmulhw .Lr7e_q(%rip), %ymm13, %ymm13
	vpsrad $16, \src, \src
	vpsubw %ymm13, \src, \src
	vpshufb .Lr7e_compact_even(%rip), \src, \src
	vpermq $0xd8, \src, \dst
	.endm

	.macro R7E_REDC_PAIR lo,hi,dst
	R7E_REDC_HALF \lo,%ymm14
	R7E_REDC_HALF \hi,%ymm15
	vpunpcklqdq %ymm15, %ymm14, %ymm11
	vpunpckhqdq %ymm15, %ymm14, %ymm13
	vperm2i128 $0x20, %ymm13, %ymm11, \dst
	.endm

	.macro R7E_TRANSPOSE
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

	.macro R7E_PACK src,perm,outoff,safe
	vpermq $\perm, \src, \src
	vpsraw $15, \src, %ymm14
	vpand .Lr7e_q(%rip), %ymm14, %ymm14
	vpaddw %ymm14, \src, \src
	vpmaddwd .Lr7e_pair_factor(%rip), \src, \src
	vpshufb .Lr7e_pack_mask(%rip), \src, \src
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

	.macro R7E_ACCUM_BLOCK inblock,kblock
	leaq .Lr7e_k_table+(\kblock*1792)(%rip), %r8
	R7E_MONT_POINT (\inblock*224)+0,(\inblock*224)+0,(\inblock*224)+0,0,1
	R7E_MONT_POINT (\inblock*224)+32,(\inblock*224)+32,(\inblock*224)+32,256,0
	R7E_MONT_POINT (\inblock*224)+64,(\inblock*224)+64,(\inblock*224)+64,512,0
	R7E_MONT_POINT (\inblock*224)+96,(\inblock*224)+96,(\inblock*224)+96,768,0
	R7E_MONT_POINT (\inblock*224)+128,(\inblock*224)+128,(\inblock*224)+128,1024,0
	R7E_MONT_POINT (\inblock*224)+160,(\inblock*224)+160,(\inblock*224)+160,1280,0
	R7E_MONT_POINT (\inblock*224)+192,(\inblock*224)+192,(\inblock*224)+192,1536,0
	.endm

	.macro R7E_REDUCE_BLOCK inblock,kblock
	R7E_ACCUM_BLOCK \inblock,\kblock
	R7E_REDC_PAIR %ymm0,%ymm1,%ymm8
	/* Match the frozen Q24 transpose register contract: c0,c2,c1,c3. */
	R7E_REDC_PAIR %ymm2,%ymm3,%ymm10
	R7E_REDC_PAIR %ymm4,%ymm5,%ymm9
	R7E_REDC_PAIR %ymm6,%ymm7,%ymm4
	.endm

	.macro R7E_FORM_BLOCK inblock,kblock
	R7E_REDUCE_BLOCK \inblock,\kblock
	R7E_TRANSPOSE
	.endm

	.macro R7E_FULL_BLOCK inblock,kblock,outoff,o0,p0,o1,p1,o2,p2,o3,p3,safe
	R7E_FORM_BLOCK \inblock,\kblock
	R7E_PACK %ymm\o0,\p0,\outoff+0,0
	R7E_PACK %ymm\o1,\p1,\outoff+24,0
	R7E_PACK %ymm\o2,\p2,\outoff+48,0
	R7E_PACK %ymm\o3,\p3,\outoff+72,\safe
	.endm

	.section .text.r7e_e1_block0_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e1_block0_asm
	.type r7e_e1_block0_asm,@function
r7e_e1_block0_asm:
	R7E_FORM_BLOCK 0,0
	R7E_PACK %ymm3,177,0,0
	R7E_PACK %ymm2,75,24,0
	R7E_PACK %ymm0,75,48,0
	R7E_PACK %ymm1,75,72,1
	vzeroupper
	ret
	.size r7e_e1_block0_asm,.-r7e_e1_block0_asm

	.section .text.r7e_e1_coeff_block0_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e1_coeff_block0_asm
	.type r7e_e1_coeff_block0_asm,@function
r7e_e1_coeff_block0_asm:
	R7E_REDUCE_BLOCK 0,0
	vmovdqu %ymm8, 0(%rdi)
	vmovdqu %ymm10, 32(%rdi)
	vmovdqu %ymm9, 64(%rdi)
	vmovdqu %ymm4, 96(%rdi)
	vzeroupper
	ret
	.size r7e_e1_coeff_block0_asm,.-r7e_e1_coeff_block0_asm

	.section .text.r7e_e1_accum_block0_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e1_accum_block0_asm
	.type r7e_e1_accum_block0_asm,@function
r7e_e1_accum_block0_asm:
	R7E_ACCUM_BLOCK 0,0
	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vzeroupper
	ret
	.size r7e_e1_accum_block0_asm,.-r7e_e1_accum_block0_asm

	.section .text.r7e_e1_full_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e1_full_asm
	.type r7e_e1_full_asm,@function
r7e_e1_full_asm:
	R7E_FULL_BLOCK 0,0,0,3,177,2,75,0,75,1,75,0
	R7E_FULL_BLOCK 1,1,96,3,177,2,75,0,75,1,75,0
	R7E_FULL_BLOCK 9,9,192,0,228,1,228,2,228,3,228,0
	R7E_FULL_BLOCK 8,8,288,2,228,3,228,1,228,0,30,0
	R7E_FULL_BLOCK 4,4,384,1,30,0,177,3,30,2,177,0
	R7E_FULL_BLOCK 5,5,480,1,30,0,177,3,30,2,177,0
	R7E_FULL_BLOCK 11,11,576,2,30,3,30,1,30,0,177,0
	R7E_FULL_BLOCK 10,10,672,1,30,0,177,3,30,2,177,0
	R7E_FULL_BLOCK 6,6,768,3,177,2,75,0,75,1,75,0
	R7E_FULL_BLOCK 7,7,864,3,177,2,75,0,75,1,75,0
	R7E_FULL_BLOCK 3,3,960,0,228,1,228,2,228,3,228,0
	R7E_FULL_BLOCK 2,2,1056,2,228,3,228,1,228,0,30,1
	vzeroupper
	ret
	.size r7e_e1_full_asm,.-r7e_e1_full_asm

	/* Same semantic endpoint, using current general B3 add-m and H1 Q24. */
	.section .text.r7e_current_full_asm,"ax",@progbits
	.p2align 5
	.globl r7e_current_full_asm
	.type r7e_current_full_asm,@function
r7e_current_full_asm:
	pushq %r12
	pushq %r13
	pushq %r14
	movq %rdi, %r12
	movq %rcx, %r13
	movq %r8, %r14
	movq %r14, %rdi
	call gt32_tile4_basemul_general_soa_soa_add_m_asm
	movq %r12, %rdi
	movq %r14, %rsi
	call gt32_q24_encode_soa_encap_hr_h1_asm
	popq %r14
	popq %r13
	popq %r12
	ret
	.size r7e_current_full_asm,.-r7e_current_full_asm

	/* E0: faithful R7 point products -> R2 -> H materialization -> late exit. */
	.macro R7E_E0_POINT off,dst
	vmovdqu \off(%rsi), \dst
	vmovdqu \off(%rdx), %ymm12
	vpmullw \dst, %ymm12, %ymm13
	vpmullw .Lr7e_qinv(%rip), %ymm13, %ymm13
	vpmulhw \dst, %ymm12, \dst
	vpmulhw .Lr7e_q(%rip), %ymm13, %ymm13
	vpsubw %ymm13, \dst, \dst
	vpmullw .Lr7e_rsq_qinv(%rip), \dst, %ymm13
	vpmulhw .Lr7e_rsq(%rip), \dst, \dst
	vpmulhw .Lr7e_q(%rip), %ymm13, %ymm13
	vpsubw %ymm13, \dst, \dst
	vpaddw \off(%rcx), \dst, \dst
	.endm

	.macro R7E_E0_PREP_BLOCK block
	R7E_E0_POINT (\block*224)+0,%ymm8
	vmovdqu %ymm8, (\block*224)+0(%rdi)
	R7E_E0_POINT (\block*224)+32,%ymm8
	R7E_E0_POINT (\block*224)+64,%ymm9
	vpaddw %ymm9, %ymm8, %ymm10
	vpsubw %ymm9, %ymm8, %ymm11
	vmovdqu %ymm10, (\block*224)+32(%rdi)
	vmovdqu %ymm11, (\block*224)+64(%rdi)
	R7E_E0_POINT (\block*224)+96,%ymm8
	R7E_E0_POINT (\block*224)+128,%ymm9
	vpaddw %ymm9, %ymm8, %ymm10
	vpsubw %ymm9, %ymm8, %ymm11
	vmovdqu %ymm10, (\block*224)+96(%rdi)
	vmovdqu %ymm11, (\block*224)+128(%rdi)
	R7E_E0_POINT (\block*224)+160,%ymm8
	R7E_E0_POINT (\block*224)+192,%ymm9
	vpaddw %ymm9, %ymm8, %ymm10
	vpsubw %ymm9, %ymm8, %ymm11
	vmovdqu %ymm10, (\block*224)+160(%rdi)
	vmovdqu %ymm11, (\block*224)+192(%rdi)
	.endm

	.section .text.r7e_e0_prepare_full_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e0_prepare_full_asm
	.type r7e_e0_prepare_full_asm,@function
r7e_e0_prepare_full_asm:
	R7E_E0_PREP_BLOCK 0
	R7E_E0_PREP_BLOCK 1
	R7E_E0_PREP_BLOCK 2
	R7E_E0_PREP_BLOCK 3
	R7E_E0_PREP_BLOCK 4
	R7E_E0_PREP_BLOCK 5
	R7E_E0_PREP_BLOCK 6
	R7E_E0_PREP_BLOCK 7
	R7E_E0_PREP_BLOCK 8
	R7E_E0_PREP_BLOCK 9
	R7E_E0_PREP_BLOCK 10
	R7E_E0_PREP_BLOCK 11
	vzeroupper
	ret
	.size r7e_e0_prepare_full_asm,.-r7e_e0_prepare_full_asm

	.macro R7E_E0_BUILD_PAIR aoff,boff,lo,hi
	vmovdqu \aoff(%rsi), %ymm4
	vmovdqu \boff(%rsi), %ymm5
	vpunpcklwd %ymm5, %ymm4, \lo
	vpunpckhwd %ymm5, %ymm4, \hi
	.endm

	.macro R7E_E0_BUILD_ZERO_PAIR aoff,lo,hi
	vmovdqu \aoff(%rsi), %ymm4
	vpxor %ymm5, %ymm5, %ymm5
	vpunpcklwd %ymm5, %ymm4, \lo
	vpunpckhwd %ymm5, %ymm4, \hi
	.endm

	.macro R7E_E0_DOT koff,dst
	vpmaddwd \koff+0(%r9), %ymm0, %ymm12
	vpmaddwd \koff+64(%r9), %ymm2, %ymm13
	vpaddd %ymm13, %ymm12, %ymm12
	R7E_REDC_HALF %ymm12,%ymm14
	vpmaddwd \koff+32(%r9), %ymm1, %ymm12
	vpmaddwd \koff+96(%r9), %ymm3, %ymm13
	vpaddd %ymm13, %ymm12, %ymm12
	R7E_REDC_HALF %ymm12,%ymm15
	vpunpcklqdq %ymm15, %ymm14, %ymm11
	vpunpckhqdq %ymm15, %ymm14, %ymm13
	vperm2i128 $0x20, %ymm13, %ymm11, \dst
	.endm

	.macro R7E_E0_FORM_BLOCK inblock,kblock
	leaq .Lr7e_hk_table+(\kblock*512)(%rip), %r9
	R7E_E0_BUILD_PAIR (\inblock*224)+0,(\inblock*224)+32,%ymm0,%ymm1
	R7E_E0_BUILD_PAIR (\inblock*224)+96,(\inblock*224)+160,%ymm2,%ymm3
	R7E_E0_DOT 0,%ymm8
	R7E_E0_DOT 256,%ymm9
	R7E_E0_BUILD_PAIR (\inblock*224)+64,(\inblock*224)+128,%ymm0,%ymm1
	R7E_E0_BUILD_ZERO_PAIR (\inblock*224)+192,%ymm2,%ymm3
	R7E_E0_DOT 128,%ymm10
	R7E_E0_DOT 384,%ymm4
	R7E_TRANSPOSE
	.endm

	.macro R7E_E0_FULL_BLOCK inblock,kblock,outoff,o0,p0,o1,p1,o2,p2,o3,p3,safe
	R7E_E0_FORM_BLOCK \inblock,\kblock
	R7E_PACK %ymm\o0,\p0,\outoff+0,0
	R7E_PACK %ymm\o1,\p1,\outoff+24,0
	R7E_PACK %ymm\o2,\p2,\outoff+48,0
	R7E_PACK %ymm\o3,\p3,\outoff+72,\safe
	.endm

	.section .text.r7e_e0_late_full_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e0_late_full_asm
	.type r7e_e0_late_full_asm,@function
r7e_e0_late_full_asm:
	R7E_E0_FULL_BLOCK 0,0,0,3,177,2,75,0,75,1,75,0
	R7E_E0_FULL_BLOCK 1,1,96,3,177,2,75,0,75,1,75,0
	R7E_E0_FULL_BLOCK 9,9,192,0,228,1,228,2,228,3,228,0
	R7E_E0_FULL_BLOCK 8,8,288,2,228,3,228,1,228,0,30,0
	R7E_E0_FULL_BLOCK 4,4,384,1,30,0,177,3,30,2,177,0
	R7E_E0_FULL_BLOCK 5,5,480,1,30,0,177,3,30,2,177,0
	R7E_E0_FULL_BLOCK 11,11,576,2,30,3,30,1,30,0,177,0
	R7E_E0_FULL_BLOCK 10,10,672,1,30,0,177,3,30,2,177,0
	R7E_E0_FULL_BLOCK 6,6,768,3,177,2,75,0,75,1,75,0
	R7E_E0_FULL_BLOCK 7,7,864,3,177,2,75,0,75,1,75,0
	R7E_E0_FULL_BLOCK 3,3,960,0,228,1,228,2,228,3,228,0
	R7E_E0_FULL_BLOCK 2,2,1056,2,228,3,228,1,228,0,30,1
	vzeroupper
	ret
	.size r7e_e0_late_full_asm,.-r7e_e0_late_full_asm

	.section .text.r7e_e0_full_asm,"ax",@progbits
	.p2align 5
	.globl r7e_e0_full_asm
	.type r7e_e0_full_asm,@function
r7e_e0_full_asm:
	pushq %r12
	pushq %r13
	pushq %r14
	movq %rdi, %r12
	movq %r8, %r13
	movq %r13, %rdi
	call r7e_e0_prepare_full_asm
	movq %r12, %rdi
	movq %r13, %rsi
	call r7e_e0_late_full_asm
	popq %r14
	popq %r13
	popq %r12
	ret
	.size r7e_e0_full_asm,.-r7e_e0_full_asm

	.section .rodata.r7e,"a",@progbits
	.p2align 5
.Lr7e_q:
	.rept 16
	.short 3457
	.endr
.Lr7e_qinv:
	.rept 16
	.short 12929
	.endr
.Lr7e_rsq:
	.rept 16
	.short 867
	.endr
.Lr7e_rsq_qinv:
	.rept 16
	.short 2787
	.endr
.Lr7e_pair_factor:
	.rept 8
	.short 1,4096
	.endr
.Lr7e_compact_even:
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
.Lr7e_pack_mask:
	.byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
	.byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
	.p2align 5
.Lr7e_k_table:
#include "../generated/r7_consumer_island_constants.inc"
	.p2align 5
.Lr7e_hk_table:
#include "../generated/r7_consumer_e0_h_constants.inc"

	.section .note.GNU-stack,"",@progbits
