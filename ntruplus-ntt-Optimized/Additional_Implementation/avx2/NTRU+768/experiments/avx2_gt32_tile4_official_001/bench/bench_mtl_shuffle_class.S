.text

.macro OP_PERM r
	vperm2i128 $0x31,%ymm\r,%ymm\r,%ymm\r
.endm
.macro OP_W r
	vpunpckhwd %ymm\r,%ymm\r,%ymm\r
.endm
.macro OP_D r
	vpunpckhdq %ymm\r,%ymm\r,%ymm\r
.endm
.macro OP_Q r
	vpunpckhqdq %ymm\r,%ymm\r,%ymm\r
.endm

.macro OPS op,streams
.if \streams == 1
	.rept 64
	\op 0
	.endr
.elseif \streams == 2
	.rept 32
	\op 0
	\op 1
	.endr
.elseif \streams == 4
	.rept 16
	\op 0
	\op 1
	\op 2
	\op 3
	.endr
.else
	.rept 8
	\op 0
	\op 1
	\op 2
	\op 3
	\op 4
	\op 5
	\op 6
	\op 7
	.endr
.endif
.endm

.macro MAKE_FUNC name,op,streams
.p2align 6
.globl \name
.type \name,@function
\name:
	testq %rdi,%rdi
	jz 2f
1:
	OPS \op,\streams
	decq %rdi
	jne 1b
2:
	vzeroupper
	ret
.size \name,.-\name
.endm

.p2align 6
.globl mtl_shuffle_empty
.type mtl_shuffle_empty,@function
mtl_shuffle_empty:
	testq %rdi,%rdi
	jz 2f
1:
	decq %rdi
	jne 1b
2:
	ret
.size mtl_shuffle_empty,.-mtl_shuffle_empty

MAKE_FUNC mtl_perm_1,OP_PERM,1
MAKE_FUNC mtl_perm_2,OP_PERM,2
MAKE_FUNC mtl_perm_4,OP_PERM,4
MAKE_FUNC mtl_perm_8,OP_PERM,8
MAKE_FUNC mtl_unpackw_1,OP_W,1
MAKE_FUNC mtl_unpackw_2,OP_W,2
MAKE_FUNC mtl_unpackw_4,OP_W,4
MAKE_FUNC mtl_unpackw_8,OP_W,8
MAKE_FUNC mtl_unpackd_1,OP_D,1
MAKE_FUNC mtl_unpackd_2,OP_D,2
MAKE_FUNC mtl_unpackd_4,OP_D,4
MAKE_FUNC mtl_unpackd_8,OP_D,8
MAKE_FUNC mtl_unpackq_1,OP_Q,1
MAKE_FUNC mtl_unpackq_2,OP_Q,2
MAKE_FUNC mtl_unpackq_4,OP_Q,4
MAKE_FUNC mtl_unpackq_8,OP_Q,8

.macro MIX_BASE
	OP_PERM 0; OP_PERM 1; OP_PERM 2; OP_PERM 3
	OP_PERM 4; OP_PERM 5; OP_PERM 6; OP_PERM 7
	OP_PERM 0; OP_PERM 1; OP_PERM 2; OP_PERM 3
	OP_PERM 4; OP_PERM 5; OP_PERM 6; OP_PERM 7
.endm
.macro MIX_FREE
	OP_PERM 0; OP_W 1; OP_Q 2
	OP_PERM 3; OP_W 4; OP_Q 5
	OP_PERM 6; OP_W 7; OP_Q 0
	OP_PERM 1; OP_W 2; OP_Q 3
	OP_PERM 4; OP_W 5; OP_Q 6
	OP_PERM 7; OP_W 0; OP_Q 1
	OP_PERM 2; OP_W 3; OP_Q 4
	OP_PERM 5; OP_W 6; OP_Q 7
.endm
.macro MIX_12_8
	OP_PERM 0; OP_W 1; OP_PERM 2; OP_Q 3
	OP_PERM 4; OP_W 5; OP_PERM 6; OP_Q 7
	OP_PERM 0; OP_W 2; OP_PERM 1; OP_Q 4
	OP_PERM 3; OP_W 6; OP_PERM 5; OP_Q 0
	OP_PERM 7; OP_PERM 2; OP_PERM 4; OP_PERM 6
.endm
.macro MIX_10_12
	OP_PERM 0; OP_W 1; OP_Q 2; OP_PERM 3
	OP_W 4; OP_Q 5; OP_PERM 6; OP_W 7
	OP_Q 0; OP_PERM 1; OP_W 2; OP_Q 3
	OP_PERM 4; OP_W 5; OP_Q 6; OP_PERM 7
	OP_W 0; OP_Q 1; OP_PERM 2; OP_PERM 5
	OP_W 3; OP_Q 4
.endm
.macro MIX_8_12
	OP_PERM 0; OP_W 1; OP_Q 2; OP_PERM 3
	OP_W 4; OP_Q 5; OP_PERM 6; OP_W 7
	OP_Q 0; OP_PERM 1; OP_W 2; OP_Q 3
	OP_PERM 4; OP_W 5; OP_Q 6; OP_PERM 7
	OP_W 0; OP_Q 1
.endm
.macro DEP_FREE
	vpunpckhqdq %ymm1,%ymm0,%ymm9
	vpunpcklqdq %ymm1,%ymm0,%ymm8
	vpunpckhqdq %ymm3,%ymm2,%ymm11
	vpunpcklqdq %ymm3,%ymm2,%ymm10
	vpunpckhqdq %ymm5,%ymm4,%ymm13
	vpunpcklqdq %ymm5,%ymm4,%ymm12
	vpunpckhqdq %ymm7,%ymm6,%ymm15
	vpunpcklqdq %ymm7,%ymm6,%ymm14
	OP_PERM 8; OP_PERM 9; OP_PERM 10; OP_PERM 11
	OP_PERM 12; OP_PERM 13; OP_PERM 14; OP_PERM 15
	vpunpckhwd %ymm9,%ymm8,%ymm1
	vpunpcklwd %ymm9,%ymm8,%ymm0
	vpunpckhwd %ymm11,%ymm10,%ymm3
	vpunpcklwd %ymm11,%ymm10,%ymm2
	vpunpckhwd %ymm13,%ymm12,%ymm5
	vpunpcklwd %ymm13,%ymm12,%ymm4
	vpunpckhwd %ymm15,%ymm14,%ymm7
	vpunpcklwd %ymm15,%ymm14,%ymm6
.endm
.macro ARITH_BG
	/* Four finite Montgomery-like chains.  The first writes break any old
	 * arithmetic destination dependency; inputs intentionally depend on the
	 * preceding routing graph, as they do in the inverse. */
	vpmullw %ymm4,%ymm0,%ymm8
	vpmullw %ymm5,%ymm1,%ymm9
	vpmullw %ymm6,%ymm2,%ymm10
	vpmullw %ymm7,%ymm3,%ymm11
	vpmulhw %ymm4,%ymm0,%ymm12
	vpmulhw %ymm5,%ymm1,%ymm13
	vpmulhw %ymm6,%ymm2,%ymm14
	vpmulhw %ymm7,%ymm3,%ymm15
	vpmulhw %ymm8,%ymm12,%ymm12
	vpmulhw %ymm9,%ymm13,%ymm13
	vpmulhw %ymm10,%ymm14,%ymm14
	vpmulhw %ymm11,%ymm15,%ymm15
	vpsubw %ymm8,%ymm12,%ymm12
	vpsubw %ymm9,%ymm13,%ymm13
	vpsubw %ymm10,%ymm14,%ymm14
	vpsubw %ymm11,%ymm15,%ymm15
	vpaddw %ymm0,%ymm12,%ymm12
	vpaddw %ymm1,%ymm13,%ymm13
	vpaddw %ymm2,%ymm14,%ymm14
	vpaddw %ymm3,%ymm15,%ymm15
	vpsubw %ymm8,%ymm12,%ymm12
	vpsubw %ymm9,%ymm13,%ymm13
	vpsubw %ymm10,%ymm14,%ymm14
	vpsubw %ymm11,%ymm15,%ymm15
.endm
.macro MAKE_MIX_FUNC name,body,arith=0
.p2align 6
.globl \name
.type \name,@function
\name:
	testq %rdi,%rdi
	jz 2f
1:
	\body
.if \arith
	ARITH_BG
.endif
	decq %rdi
	jne 1b
2:
	vzeroupper
	ret
.size \name,.-\name
.endm

MAKE_MIX_FUNC mtl_mix_base16,MIX_BASE
MAKE_MIX_FUNC mtl_mix_free8_16,MIX_FREE
MAKE_MIX_FUNC mtl_mix_balanced12_8,MIX_12_8
MAKE_MIX_FUNC mtl_mix_balanced10_12,MIX_10_12
MAKE_MIX_FUNC mtl_mix_balanced8_12,MIX_8_12
MAKE_MIX_FUNC mtl_mix_dependency_free,DEP_FREE
MAKE_MIX_FUNC mtl_mix_arith_base16,MIX_BASE,1
MAKE_MIX_FUNC mtl_mix_arith_free8_16,MIX_FREE,1
MAKE_MIX_FUNC mtl_mix_arith_dependency_free,DEP_FREE,1

.section .note.GNU-stack,"",@progbits
