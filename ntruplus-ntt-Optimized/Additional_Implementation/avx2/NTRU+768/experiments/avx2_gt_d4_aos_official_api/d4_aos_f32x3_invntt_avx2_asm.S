/* Default-off F32X3 inverse candidate: verified NTT32 radix-2 stage 0 only.
 * SysV: rdi=out, rsi=in.  Each YMM is [b0u0,b0u1,b1u0,b1u1] qwords.
 * ymm0 input; ymm1 swapped; ymm2 sum; ymm3 diff/mask; ymm4 q; ymm5 q-1;
 * ymm6 zero.  No stack frame, calls, or branch-half crossing.
 */
.text
.p2align 5
.globl gt_d4aos_f32x3_invntt32_stage0_asm
.type gt_d4aos_f32x3_invntt32_stage0_asm,@function
gt_d4aos_f32x3_invntt32_stage0_asm:
	mov $48, %ecx
	vmovdqa .Lq(%rip), %ymm4
	vmovdqa .Lqminus1(%rip), %ymm5
	vpxor %ymm6, %ymm6, %ymm6
.Lstage0:
	vmovdqa (%rsi), %ymm0
	vpermq $0xb1, %ymm0, %ymm1
	vpaddw %ymm1, %ymm0, %ymm2
	vpcmpgtw %ymm2, %ymm6, %ymm3
	vpand %ymm4, %ymm3, %ymm3
	vpaddw %ymm3, %ymm2, %ymm2
	vpcmpgtw %ymm5, %ymm2, %ymm3
	vpand %ymm4, %ymm3, %ymm3
	vpsubw %ymm3, %ymm2, %ymm2
	vpsubw %ymm1, %ymm0, %ymm0
	vpcmpgtw %ymm0, %ymm6, %ymm3
	vpand %ymm4, %ymm3, %ymm3
	vpaddw %ymm3, %ymm0, %ymm0
	vpcmpgtw %ymm5, %ymm0, %ymm3
	vpand %ymm4, %ymm3, %ymm3
	vpsubw %ymm3, %ymm0, %ymm0
	vpermq $0xb1, %ymm0, %ymm0
	vpblendd $0xcc, %ymm0, %ymm2, %ymm2
	vmovdqa %ymm2, (%rdi)
	add $32, %rsi
	add $32, %rdi
	dec %ecx
	jne .Lstage0
	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_stage0_asm,.-gt_d4aos_f32x3_invntt32_stage0_asm

/*
 * Merged CT L0-L2 candidate.
 *
 * Input domain: canonical R^0 native F32X3 state, natural j order.
 * Output domain: canonical R^0 CT state after inverse NTT32 layers L0-L2.
 * Alias contract: out and in are aligned and non-overlapping.
 *
 * Each tile fixes (row,j3,j4) and keeps all four (j1,j2) combinations in
 * ymm0..ymm3.  A compact vector is
 *   qword0=b0,u0,c0..c3; qword1=b0,u1,c0..c3;
 *   qword2=b1,u0,c0..c3; qword3=b1,u1,c0..c3.
 * Bit reversal is folded into the four pairs of native-state loads.
 */

/* Canonicalize one vector known to be in (-q,2q).  Clobbers mask. */
.macro CT_CANON value,mask
	vpcmpgtw \value, %ymm14, \mask
	vpand %ymm12, \mask, \mask
	vpaddw \mask, \value, \value
	vpcmpgtw %ymm13, \value, \mask
	vpand %ymm12, \mask, \mask
	vpsubw \mask, \value, \value
.endm

/*
 * One qword-local L0 butterfly.
 * Input/output: data is canonical R^0 with lane meaning 8*b+4*u+c.
 * Clobbers ymm4..ymm7.  Branches stay in their original 128-bit halves.
 */
.macro CT_L0 data
	vpermq $0xb1, \data, %ymm4
	vpaddw %ymm4, \data, %ymm5
	vpsubw %ymm4, \data, %ymm6
	CT_CANON %ymm5, %ymm7
	CT_CANON %ymm6, %ymm7
	vpermq $0xb1, %ymm6, %ymm6
	vpblendd $0xcc, %ymm6, %ymm5, \data
.endm

/*
 * Montgomery CT pair: right is multiplied by the generated factor, then
 * left +/- product are canonicalized.  Both operands remain at R^0 scale.
 * Clobbers ymm6..ymm10; factor/factor_qinv are retained in ymm4/ymm5.
 */
.macro CT_PAIR left,right,factor,factor_qinv
	vpmullw \factor_qinv, \right, %ymm6
	vpmulhw \factor, \right, %ymm7
	vpmulhw %ymm12, %ymm6, %ymm6
	vpsubw %ymm6, %ymm7, %ymm7
	CT_CANON %ymm7, %ymm10
	vpaddw %ymm7, \left, %ymm8
	vpsubw %ymm7, \left, %ymm9
	CT_CANON %ymm8, %ymm10
	CT_CANON %ymm9, %ymm10
	vmovdqa %ymm8, \left
	vmovdqa %ymm9, \right
.endm

/* Load two native blocks and form one bit-reversed compact stage vector. */
.macro CT_LOAD_PAIR dst,row,block_a,block_b,perm
	vmovdqa \row+32*\block_a(%rsi), \dst
	vmovdqa \row+32*\block_b(%rsi), %ymm4
	vpermq $\perm, \dst, \dst
	vpermq $\perm, %ymm4, %ymm4
	vpblendd $0xcc, %ymm4, \dst, \dst
.endm

/*
 * Four-vector merged tile.  There are no stores between L0, L1, and L2.
 * Generated factors are consumed in arithmetic order, not source order.
 */
.macro CT_MERGE_L0_L2 row,outbase,perm,a0,b0,a1,b1,a2,b2,a3,b3
	CT_LOAD_PAIR %ymm0, \row, \a0, \b0, \perm
	CT_LOAD_PAIR %ymm1, \row, \a1, \b1, \perm
	CT_LOAD_PAIR %ymm2, \row, \a2, \b2, \perm
	CT_LOAD_PAIR %ymm3, \row, \a3, \b3, \perm

	CT_L0 %ymm0
	CT_L0 %ymm1
	CT_L0 %ymm2
	CT_L0 %ymm3

	vmovdqa .Lct_l1_factor(%rip), %ymm4
	vmovdqa .Lct_l1_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm1, %ymm4, %ymm5
	CT_PAIR %ymm2, %ymm3, %ymm4, %ymm5

	vmovdqa .Lct_l2_j1_0_factor(%rip), %ymm4
	vmovdqa .Lct_l2_j1_0_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm2, %ymm4, %ymm5
	vmovdqa .Lct_l2_j1_1_factor(%rip), %ymm4
	vmovdqa .Lct_l2_j1_1_qinv(%rip), %ymm5
	CT_PAIR %ymm1, %ymm3, %ymm4, %ymm5

	vmovdqa %ymm0, \row+32*(\outbase+0)(%rdi)
	vmovdqa %ymm1, \row+32*(\outbase+1)(%rdi)
	vmovdqa %ymm2, \row+32*(\outbase+2)(%rdi)
	vmovdqa %ymm3, \row+32*(\outbase+3)(%rdi)
.endm

#ifdef D4AOS_F32X3_ASM_CHECKPOINTS
/*
 * Debug-only tile.  r8/r9/r10 receive L0/L1/L2 respectively; rsi is input.
 * These intermediate stores are not assembled into the release symbol.
 */
.macro CT_MERGE_L0_L2_DEBUG row,outbase,perm,a0,b0,a1,b1,a2,b2,a3,b3
	CT_LOAD_PAIR %ymm0, \row, \a0, \b0, \perm
	CT_LOAD_PAIR %ymm1, \row, \a1, \b1, \perm
	CT_LOAD_PAIR %ymm2, \row, \a2, \b2, \perm
	CT_LOAD_PAIR %ymm3, \row, \a3, \b3, \perm

	CT_L0 %ymm0
	CT_L0 %ymm1
	CT_L0 %ymm2
	CT_L0 %ymm3
	vmovdqa %ymm0, \row+32*(\outbase+0)(%r8)
	vmovdqa %ymm1, \row+32*(\outbase+1)(%r8)
	vmovdqa %ymm2, \row+32*(\outbase+2)(%r8)
	vmovdqa %ymm3, \row+32*(\outbase+3)(%r8)

	vmovdqa .Lct_l1_factor(%rip), %ymm4
	vmovdqa .Lct_l1_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm1, %ymm4, %ymm5
	CT_PAIR %ymm2, %ymm3, %ymm4, %ymm5
	vmovdqa %ymm0, \row+32*(\outbase+0)(%r9)
	vmovdqa %ymm1, \row+32*(\outbase+1)(%r9)
	vmovdqa %ymm2, \row+32*(\outbase+2)(%r9)
	vmovdqa %ymm3, \row+32*(\outbase+3)(%r9)

	vmovdqa .Lct_l2_j1_0_factor(%rip), %ymm4
	vmovdqa .Lct_l2_j1_0_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm2, %ymm4, %ymm5
	vmovdqa .Lct_l2_j1_1_factor(%rip), %ymm4
	vmovdqa .Lct_l2_j1_1_qinv(%rip), %ymm5
	CT_PAIR %ymm1, %ymm3, %ymm4, %ymm5
	vmovdqa %ymm0, \row+32*(\outbase+0)(%r10)
	vmovdqa %ymm1, \row+32*(\outbase+1)(%r10)
	vmovdqa %ymm2, \row+32*(\outbase+2)(%r10)
	vmovdqa %ymm3, \row+32*(\outbase+3)(%r10)
.endm
#endif

/* Y1/Y2 range-driven lazy primitives.  Proven signed bounds:
 * input q-1; L0 6912; L1 9005; L2 11209; L3 13529; L4 15972.
 * Canonicalization occurs only at the post-L2 and post-L4 state boundaries.
 */
.macro CT_L0_YANG data
	vpermq $0xb1, \data, %ymm8
	vpaddw %ymm8, \data, %ymm9
	vpsubw %ymm8, \data, \data
	vpermq $0xb1, \data, \data
	vpblendd $0xcc, \data, %ymm9, \data
.endm

/* factor=ymm10, qinv=ymm11, q=ymm12; clobbers ymm8/ymm9/ymm15. */
.macro CT_PAIR_YANG left,right
	vpmullw %ymm11, \right, %ymm8
	vpmulhw %ymm10, \right, %ymm9
	vpmulhw %ymm12, %ymm8, %ymm8
	vpsubw %ymm8, %ymm9, %ymm9
	vpaddw %ymm9, \left, %ymm15
	vpsubw %ymm9, \left, \right
	vmovdqa %ymm15, \left
.endm

/* Signed Barrett to centered range, then one add-q to canonical [0,q). */
.macro CT_BARRETT_CANON_YANG value
	vpmulhrsw .Lcenter10(%rip), \value, %ymm10
	vpmullw %ymm12, %ymm10, %ymm10
	vpsubw %ymm10, \value, \value
	vpcmpgtw \value, %ymm14, %ymm10
	vpand %ymm12, %ymm10, %ymm10
	vpaddw %ymm10, \value, \value
.endm

/* Load each native block once and derive both source-u compact vectors. */
.macro CT_LOAD_DUAL lo,hi,offset_a,offset_b
	vmovdqa \offset_a(%rsi), \hi
	vmovdqa \offset_b(%rsi), %ymm8
	vpermq $0xa0, \hi, %ymm9
	vpermq $0xa0, %ymm8, %ymm15
	vpblendd $0xcc, %ymm15, %ymm9, \lo
	vpermq $0xf5, \hi, \hi
	vpermq $0xf5, %ymm8, %ymm8
	vpblendd $0xcc, %ymm8, \hi, \hi
.endm

/* Two L0-L2 tiles share eight one-time native loads and all factor loads. */
.macro CT_YANG_L0_L2_GROUP outlo,outhi,a0,b0,a1,b1,a2,b2,a3,b3
	CT_LOAD_DUAL %ymm0, %ymm4, 32*\a0, 32*\b0
	CT_LOAD_DUAL %ymm1, %ymm5, 32*\a1, 32*\b1
	CT_LOAD_DUAL %ymm2, %ymm6, 32*\a2, 32*\b2
	CT_LOAD_DUAL %ymm3, %ymm7, 32*\a3, 32*\b3

	CT_L0_YANG %ymm0
	CT_L0_YANG %ymm1
	CT_L0_YANG %ymm2
	CT_L0_YANG %ymm3
	CT_L0_YANG %ymm4
	CT_L0_YANG %ymm5
	CT_L0_YANG %ymm6
	CT_L0_YANG %ymm7

	vmovdqa .Lct_l1_factor(%rip), %ymm10
	vmovdqa .Lct_l1_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm0, %ymm1
	CT_PAIR_YANG %ymm2, %ymm3
	CT_PAIR_YANG %ymm4, %ymm5
	CT_PAIR_YANG %ymm6, %ymm7

	vmovdqa .Lct_l2_j1_0_factor(%rip), %ymm10
	vmovdqa .Lct_l2_j1_0_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm0, %ymm2
	CT_PAIR_YANG %ymm4, %ymm6
	vmovdqa .Lct_l2_j1_1_factor(%rip), %ymm10
	vmovdqa .Lct_l2_j1_1_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm1, %ymm3
	CT_PAIR_YANG %ymm5, %ymm7

	CT_BARRETT_CANON_YANG %ymm0
	CT_BARRETT_CANON_YANG %ymm1
	CT_BARRETT_CANON_YANG %ymm2
	CT_BARRETT_CANON_YANG %ymm3
	CT_BARRETT_CANON_YANG %ymm4
	CT_BARRETT_CANON_YANG %ymm5
	CT_BARRETT_CANON_YANG %ymm6
	CT_BARRETT_CANON_YANG %ymm7
	vmovdqa %ymm0, 32*(\outlo+0)(%rdi)
	vmovdqa %ymm1, 32*(\outlo+1)(%rdi)
	vmovdqa %ymm2, 32*(\outlo+2)(%rdi)
	vmovdqa %ymm3, 32*(\outlo+3)(%rdi)
	vmovdqa %ymm4, 32*(\outhi+0)(%rdi)
	vmovdqa %ymm5, 32*(\outhi+1)(%rdi)
	vmovdqa %ymm6, 32*(\outhi+2)(%rdi)
	vmovdqa %ymm7, 32*(\outhi+3)(%rdi)
.endm

.macro CT_YANG_PASS_A_ROW
	CT_YANG_L0_L2_GROUP 0,8, 0,8, 4,12, 2,10, 6,14
	CT_YANG_L0_L2_GROUP 4,12, 1,9, 5,13, 3,11, 7,15
.endm

.macro CT_YANG_L3_L4_TILE tile
	vmovdqa 32*(\tile+0)(%rsi), %ymm0
	vmovdqa 32*(\tile+4)(%rsi), %ymm1
	vmovdqa 32*(\tile+8)(%rsi), %ymm2
	vmovdqa 32*(\tile+12)(%rsi), %ymm3
	vmovdqa .Lct_l3_t\tile\()_pair_0_4_factor(%rip), %ymm10
	vmovdqa .Lct_l3_t\tile\()_pair_0_4_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm0, %ymm1
	vmovdqa .Lct_l3_t\tile\()_pair_8_12_factor(%rip), %ymm10
	vmovdqa .Lct_l3_t\tile\()_pair_8_12_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm2, %ymm3
	vmovdqa .Lct_l4_t\tile\()_pair_0_8_factor(%rip), %ymm10
	vmovdqa .Lct_l4_t\tile\()_pair_0_8_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm0, %ymm2
	vmovdqa .Lct_l4_t\tile\()_pair_4_12_factor(%rip), %ymm10
	vmovdqa .Lct_l4_t\tile\()_pair_4_12_qinv(%rip), %ymm11
	CT_PAIR_YANG %ymm1, %ymm3
	CT_BARRETT_CANON_YANG %ymm0
	CT_BARRETT_CANON_YANG %ymm1
	CT_BARRETT_CANON_YANG %ymm2
	CT_BARRETT_CANON_YANG %ymm3
	vmovdqa %ymm0, 32*(\tile+0)(%rdi)
	vmovdqa %ymm1, 32*(\tile+4)(%rdi)
	vmovdqa %ymm2, 32*(\tile+8)(%rdi)
	vmovdqa %ymm3, 32*(\tile+12)(%rdi)
.endm

.macro CT_YANG_PASS_B_ROW
	CT_YANG_L3_L4_TILE 0
	CT_YANG_L3_L4_TILE 1
	CT_YANG_L3_L4_TILE 2
	CT_YANG_L3_L4_TILE 3
.endm

.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_merged_yang_asm
.type gt_d4aos_f32x3_invntt32_ct_merged_yang_asm,@function
gt_d4aos_f32x3_invntt32_ct_merged_yang_asm:
	mov %rdi, %rax
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14
	CT_YANG_PASS_A_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_A_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_A_ROW
	mov %rax, %rsi
	mov %rax, %rdi
	CT_YANG_PASS_B_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_B_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_B_ROW
	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_merged_yang_asm,.-gt_d4aos_f32x3_invntt32_ct_merged_yang_asm

.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm
.type gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm,@function
gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm:
	mov %rdi, %rax
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14
	mov $3, %ecx
.Lyang_compact_pass_a:
	CT_YANG_PASS_A_ROW
	add $512, %rsi
	add $512, %rdi
	dec %ecx
	jne .Lyang_compact_pass_a
	mov %rax, %rsi
	mov %rax, %rdi
	mov $3, %ecx
.Lyang_compact_pass_b:
	CT_YANG_PASS_B_ROW
	add $512, %rsi
	add $512, %rdi
	dec %ecx
	jne .Lyang_compact_pass_b
	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm,.-gt_d4aos_f32x3_invntt32_ct_merged_yang_compact_asm

/*
 * Compact inverse DFT3 plus the required immediate signed Barrett boundary.
 * ymm0..2: Y0/Y1/Y2 loads, dead after raw outputs are formed.
 * ymm3: delta then shared omega term; ymm4: Montgomery correction.
 * ymm5..7: raw then reduced D0/D1/D2, retained through probe stores.
 * ymm8..10: Barrett quotients; ymm11=q; ymm12=Barrett reciprocal;
 * ymm13=omega qinv; ymm14=omega Montgomery factor; ymm15 free.
 * Input [0,q), raw D0 [0,3q), raw D1/D2 conservatively [-5368,5368],
 * output [0,q), scale R^0. Lane meaning remains 8*b+4*u+c.
 */
.macro COMPACT_IDFT3_BARRETT
	vmovdqa    0(%rsi), %ymm0
	vmovdqa  512(%rsi), %ymm1
	vmovdqa 1024(%rsi), %ymm2

	vpsubw  %ymm1,  %ymm2, %ymm3
	vpmullw %ymm13, %ymm3, %ymm4
	vpmulhw %ymm14, %ymm3, %ymm3
	vpaddw  %ymm1,  %ymm0, %ymm5
	vpsubw  %ymm1,  %ymm0, %ymm6
	vpsubw  %ymm2,  %ymm0, %ymm7
	vpaddw  %ymm2,  %ymm5, %ymm5
	vpmulhw %ymm11, %ymm4, %ymm4
	vpsubw  %ymm4,  %ymm3, %ymm3
	vpaddw  %ymm3,  %ymm6, %ymm6
	vpsubw  %ymm3,  %ymm7, %ymm7

	vpmulhw %ymm12, %ymm5,  %ymm8
	vpmulhw %ymm12, %ymm6,  %ymm9
	vpmulhw %ymm12, %ymm7, %ymm10
	vpsraw  $10, %ymm8,  %ymm8
	vpsraw  $10, %ymm9,  %ymm9
	vpsraw  $10, %ymm10, %ymm10
	vpmullw %ymm11, %ymm8,  %ymm8
	vpmullw %ymm11, %ymm9,  %ymm9
	vpmullw %ymm11, %ymm10, %ymm10
	vpsubw  %ymm8,  %ymm5, %ymm5
	vpsubw  %ymm9,  %ymm6, %ymm6
	vpsubw  %ymm10, %ymm7, %ymm7
.endm

.p2align 5
.globl gt_d4aos_f32x3_idft3_barrett_probe_asm
.type gt_d4aos_f32x3_idft3_barrett_probe_asm,@function
gt_d4aos_f32x3_idft3_barrett_probe_asm:
	vmovdqa .Ld4_dft3_q(%rip), %ymm11
	vmovdqa .Ld4_dft3_barrett_v(%rip), %ymm12
	vmovdqa .Ld4_dft3_omega_qinv(%rip), %ymm13
	vmovdqa .Ld4_dft3_omega(%rip), %ymm14
	mov $16, %ecx
.Ld4_compact_dft3_loop:
	COMPACT_IDFT3_BARRETT
	/* Probe-only materialization; terminal integration will consume registers. */
	vmovdqa %ymm5,    0(%rdi)
	vmovdqa %ymm6,  512(%rdi)
	vmovdqa %ymm7, 1024(%rdi)
	add $32, %rsi
	add $32, %rdi
	dec %ecx
	jne .Ld4_compact_dft3_loop
	vzeroupper
	ret
.size gt_d4aos_f32x3_idft3_barrett_probe_asm,.-gt_d4aos_f32x3_idft3_barrett_probe_asm

/* DFT3 arithmetic only. Raw D0/D1/D2 are returned in ymm5/ymm6/ymm7. */
.macro COMPACT_IDFT3_RAW
	vmovdqa    0(%rsi), %ymm0
	vmovdqa  512(%rsi), %ymm1
	vmovdqa 1024(%rsi), %ymm2
	vpsubw  %ymm1,  %ymm2, %ymm3
	vpmullw %ymm13, %ymm3, %ymm4
	vpmulhw %ymm14, %ymm3, %ymm3
	vpaddw  %ymm1,  %ymm0, %ymm5
	vpsubw  %ymm1,  %ymm0, %ymm6
	vpsubw  %ymm2,  %ymm0, %ymm7
	vpaddw  %ymm2,  %ymm5, %ymm5
	vpmulhw %ymm11, %ymm4, %ymm4
	vpsubw  %ymm4,  %ymm3, %ymm3
	vpaddw  %ymm3,  %ymm6, %ymm6
	vpsubw  %ymm3,  %ymm7, %ymm7
.endm

.macro PACKED_BARRETT_ONE value,tmp
	vpmulhw %ymm12, \value, \tmp
	vpsraw $10, \tmp, \tmp
	vpmullw %ymm11, \tmp, \tmp
	vpsubw \tmp, \value, \value
.endm

/*
 * Destructive terminal for one Barrett-reduced D_r[t].
 * value is a numeric YMM id (5, 6 or 7). D1/D2 may remain live in the other
 * value registers. r8 points to the direct CRT P/Pqinv/Q/Qqinv record, rdx
 * to four offsets, and r10 to natural output. Four qword stores are issued;
 * no coefficient extract. P consumes the original branch halves and Q the
 * half-swapped value, producing packed low=a and high=h in two Montgomery
 * chains instead of materializing the intermediate CRT difference.
 */
.macro FUSED_D4_TERMINAL value
	PACKED_BARRETT_ONE %ymm\value, %ymm8

	/* Direct P contribution from [branch0 | branch1]. */
	vperm2i128 $0x01, %ymm\value, %ymm\value, %ymm2
	vpmullw 32(%r8), %ymm\value, %ymm0
	vpmulhw 0(%r8), %ymm\value, %ymm3
	vpmulhw %ymm11, %ymm0, %ymm0
	vpsubw %ymm0, %ymm3, %ymm3

	/* Direct Q contribution from [branch1 | branch0], then combine a/h. */
	vpmullw 96(%r8), %ymm2, %ymm0
	vpmulhw 64(%r8), %ymm2, %ymm4
	vpmulhw %ymm11, %ymm0, %ymm0
	vpsubw %ymm0, %ymm4, %ymm4
	vpaddw %ymm4, %ymm3, %ymm\value

	/* Final canonical natural representatives; low half is a, high half h. */
	PACKED_BARRETT_ONE %ymm\value, %ymm0
	vpcmpeqw %ymm11, %ymm\value, %ymm0
	vpand %ymm11, %ymm0, %ymm0
	vpsubw %ymm0, %ymm\value, %ymm\value
	vextracti128 $1, %ymm\value, %xmm3

	mov 0(%rdx), %eax
	vmovq %xmm\value, (%r10,%rax)
	mov 4(%rdx), %eax
	vpextrq $1, %xmm\value, (%r10,%rax)
	mov 8(%rdx), %eax
	vmovq %xmm3, (%r10,%rax)
	mov 12(%rdx), %eax
	vpextrq $1, %xmm3, (%r10,%rax)
	add $128, %r8
	add $16, %rdx
.endm

.macro DFT3_TERMINAL_LOOP
	leaq .Lterminal_direct_tables(%rip), %r8
	leaq .Lterminal_offsets(%rip), %rdx
	vmovdqa .Ld4_dft3_q(%rip), %ymm11
	vmovdqa .Ld4_dft3_barrett_v(%rip), %ymm12
	vmovdqa .Ld4_dft3_omega_qinv(%rip), %ymm13
	vmovdqa .Ld4_dft3_omega(%rip), %ymm14
	mov $16, %ecx
.Lterminal_loop\@:
	COMPACT_IDFT3_RAW
	FUSED_D4_TERMINAL 5 /* release D0; D1/D2 remain in ymm6/ymm7. */
	FUSED_D4_TERMINAL 6 /* release D1; D2 remains in ymm7. */
	FUSED_D4_TERMINAL 7 /* release D2. */
	add $32, %rsi
	dec %ecx
	jne .Lterminal_loop\@
.endm

/* Complete Y1 endpoint. Stack storage is the one named transform state. */
.p2align 5
.globl gt_d4aos_f32x3_yang_invntt_avx2_asm
.type gt_d4aos_f32x3_yang_invntt_avx2_asm,@function
gt_d4aos_f32x3_yang_invntt_avx2_asm:
	mov %rsp, %r11
	mov %rdi, %r10
	and $-32, %rsp
	sub $1536, %rsp
	mov %rsp, %rax
	mov %rsp, %rdi
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14
	CT_YANG_PASS_A_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_A_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_A_ROW
	mov %rax, %rsi
	mov %rax, %rdi
	CT_YANG_PASS_B_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_B_ROW
	add $512, %rsi
	add $512, %rdi
	CT_YANG_PASS_B_ROW
	mov %rax, %rsi
	DFT3_TERMINAL_LOOP
	mov %r11, %rsp
	vzeroupper
	ret
.size gt_d4aos_f32x3_yang_invntt_avx2_asm,.-gt_d4aos_f32x3_yang_invntt_avx2_asm

/* Complete Y2 endpoint; identical DFT3/terminal, looped NTT32 producer. */
.p2align 5
#ifndef D4AOS_Y2_SYMBOL
#define D4AOS_Y2_SYMBOL gt_d4aos_f32x3_yang_compact_invntt_avx2_asm
#endif
.globl D4AOS_Y2_SYMBOL
.type D4AOS_Y2_SYMBOL,@function
D4AOS_Y2_SYMBOL:
	mov %rsp, %r11
	mov %rdi, %r10
	and $-32, %rsp
	sub $1536, %rsp
	mov %rsp, %rax
	mov %rsp, %rdi
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14
	mov $3, %ecx
.Lcomplete_y2_pass_a:
	CT_YANG_PASS_A_ROW
	add $512, %rsi
	add $512, %rdi
	dec %ecx
	jne .Lcomplete_y2_pass_a
	mov %rax, %rsi
	mov %rax, %rdi
	mov $3, %ecx
.Lcomplete_y2_pass_b:
	CT_YANG_PASS_B_ROW
	add $512, %rsi
	add $512, %rdi
	dec %ecx
	jne .Lcomplete_y2_pass_b
	mov %rax, %rsi
	DFT3_TERMINAL_LOOP
	mov %r11, %rsp
	vzeroupper
	ret
.size D4AOS_Y2_SYMBOL,.-D4AOS_Y2_SYMBOL

/*
 * L3/L4 tile for fixed (row,j1,j2):
 *   ymm0=base+0, ymm1=base+4, ymm2=base+8, ymm3=base+12.
 * L3 pairs (0,4) and (8,12); L4 pairs (0,8) and (4,12).
 * ymm0..3 are canonical R^0 data.  ymm4/5 hold short-lived factor/qinv;
 * ymm6..10 are CT_PAIR temporaries; ymm12=q, ymm13=q-1, ymm14=zero;
 * ymm11 and ymm15 remain free.  No state store occurs between L3 and L4.
 */
.macro CT_MERGE_L3_L4 row,tile
	vmovdqa \row+32*(\tile+0)(%rsi), %ymm0
	vmovdqa \row+32*(\tile+4)(%rsi), %ymm1
	vmovdqa \row+32*(\tile+8)(%rsi), %ymm2
	vmovdqa \row+32*(\tile+12)(%rsi), %ymm3

	vmovdqa .Lct_l3_t\tile\()_pair_0_4_factor(%rip), %ymm4
	vmovdqa .Lct_l3_t\tile\()_pair_0_4_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm1, %ymm4, %ymm5
	vmovdqa .Lct_l3_t\tile\()_pair_8_12_factor(%rip), %ymm4
	vmovdqa .Lct_l3_t\tile\()_pair_8_12_qinv(%rip), %ymm5
	CT_PAIR %ymm2, %ymm3, %ymm4, %ymm5

	vmovdqa .Lct_l4_t\tile\()_pair_0_8_factor(%rip), %ymm4
	vmovdqa .Lct_l4_t\tile\()_pair_0_8_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm2, %ymm4, %ymm5
	vmovdqa .Lct_l4_t\tile\()_pair_4_12_factor(%rip), %ymm4
	vmovdqa .Lct_l4_t\tile\()_pair_4_12_qinv(%rip), %ymm5
	CT_PAIR %ymm1, %ymm3, %ymm4, %ymm5

	vmovdqa %ymm0, \row+32*(\tile+0)(%rdi)
	vmovdqa %ymm1, \row+32*(\tile+4)(%rdi)
	vmovdqa %ymm2, \row+32*(\tile+8)(%rdi)
	vmovdqa %ymm3, \row+32*(\tile+12)(%rdi)
.endm

#ifdef D4AOS_F32X3_ASM_CHECKPOINTS
/* Debug-only L3/L4 tile: r8=L3, r9=L4, rsi=post-L2 input. */
.macro CT_MERGE_L3_L4_DEBUG row,tile
	vmovdqa \row+32*(\tile+0)(%rsi), %ymm0
	vmovdqa \row+32*(\tile+4)(%rsi), %ymm1
	vmovdqa \row+32*(\tile+8)(%rsi), %ymm2
	vmovdqa \row+32*(\tile+12)(%rsi), %ymm3

	vmovdqa .Lct_l3_t\tile\()_pair_0_4_factor(%rip), %ymm4
	vmovdqa .Lct_l3_t\tile\()_pair_0_4_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm1, %ymm4, %ymm5
	vmovdqa .Lct_l3_t\tile\()_pair_8_12_factor(%rip), %ymm4
	vmovdqa .Lct_l3_t\tile\()_pair_8_12_qinv(%rip), %ymm5
	CT_PAIR %ymm2, %ymm3, %ymm4, %ymm5
	vmovdqa %ymm0, \row+32*(\tile+0)(%r8)
	vmovdqa %ymm1, \row+32*(\tile+4)(%r8)
	vmovdqa %ymm2, \row+32*(\tile+8)(%r8)
	vmovdqa %ymm3, \row+32*(\tile+12)(%r8)

	vmovdqa .Lct_l4_t\tile\()_pair_0_8_factor(%rip), %ymm4
	vmovdqa .Lct_l4_t\tile\()_pair_0_8_qinv(%rip), %ymm5
	CT_PAIR %ymm0, %ymm2, %ymm4, %ymm5
	vmovdqa .Lct_l4_t\tile\()_pair_4_12_factor(%rip), %ymm4
	vmovdqa .Lct_l4_t\tile\()_pair_4_12_qinv(%rip), %ymm5
	CT_PAIR %ymm1, %ymm3, %ymm4, %ymm5
	vmovdqa %ymm0, \row+32*(\tile+0)(%r9)
	vmovdqa %ymm1, \row+32*(\tile+4)(%r9)
	vmovdqa %ymm2, \row+32*(\tile+8)(%r9)
	vmovdqa %ymm3, \row+32*(\tile+12)(%r9)
.endm
#endif

.macro CT_ALL_L3_L4_TILES
	CT_MERGE_L3_L4 0, 0
	CT_MERGE_L3_L4 0, 1
	CT_MERGE_L3_L4 0, 2
	CT_MERGE_L3_L4 0, 3
	CT_MERGE_L3_L4 512, 0
	CT_MERGE_L3_L4 512, 1
	CT_MERGE_L3_L4 512, 2
	CT_MERGE_L3_L4 512, 3
	CT_MERGE_L3_L4 1024, 0
	CT_MERGE_L3_L4 1024, 1
	CT_MERGE_L3_L4 1024, 2
	CT_MERGE_L3_L4 1024, 3
.endm

.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm
.type gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm,@function
gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm:
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14
	CT_ALL_L3_L4_TILES
	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm,.-gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm

.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_merged_asm
.type gt_d4aos_f32x3_invntt32_ct_merged_asm,@function
gt_d4aos_f32x3_invntt32_ct_merged_asm:
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14

	/* Pass A: native input to the one named post-L2 semantic state at out. */
	CT_MERGE_L0_L2 0,    0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 0,    4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 0,    8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 0,    12, 0xf5, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 512,  0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 512,  4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 512,  8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 512,  12, 0xf5, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 1024, 0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 1024, 4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 1024, 8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 1024, 12, 0xf5, 1,9, 5,13, 3,11, 7,15

	/* Pass B: transform that state in place from post-L2 to post-L4. */
	mov %rdi, %rsi
	CT_ALL_L3_L4_TILES
	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_merged_asm,.-gt_d4aos_f32x3_invntt32_ct_merged_asm

#ifdef D4AOS_F32X3_ASM_CHECKPOINTS
.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm
.type gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm,@function
gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm:
	/* rdi=L3, rsi=L4, rdx=post-L2 input. */
	mov %rdi, %r8
	mov %rsi, %r9
	mov %rdx, %rsi
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14
	CT_MERGE_L3_L4_DEBUG 0, 0
	CT_MERGE_L3_L4_DEBUG 0, 1
	CT_MERGE_L3_L4_DEBUG 0, 2
	CT_MERGE_L3_L4_DEBUG 0, 3
	CT_MERGE_L3_L4_DEBUG 512, 0
	CT_MERGE_L3_L4_DEBUG 512, 1
	CT_MERGE_L3_L4_DEBUG 512, 2
	CT_MERGE_L3_L4_DEBUG 512, 3
	CT_MERGE_L3_L4_DEBUG 1024, 0
	CT_MERGE_L3_L4_DEBUG 1024, 1
	CT_MERGE_L3_L4_DEBUG 1024, 2
	CT_MERGE_L3_L4_DEBUG 1024, 3
	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm,.-gt_d4aos_f32x3_invntt32_ct_l3_l4_checkpoints_asm
#endif

.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm
.type gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm,@function
gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm:
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14

	/* row 0: source-u0 tiles followed by source-u1 tiles. */
	CT_MERGE_L0_L2 0,    0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 0,    4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 0,    8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 0,    12, 0xf5, 1,9, 5,13, 3,11, 7,15

	/* row 1. */
	CT_MERGE_L0_L2 512,  0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 512,  4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 512,  8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 512,  12, 0xf5, 1,9, 5,13, 3,11, 7,15

	/* row 2. */
	CT_MERGE_L0_L2 1024, 0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 1024, 4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2 1024, 8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2 1024, 12, 0xf5, 1,9, 5,13, 3,11, 7,15

	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm,.-gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm

#ifdef D4AOS_F32X3_ASM_CHECKPOINTS
.p2align 5
.globl gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm
.type gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm,@function
gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm:
	/* rdi=L0, rsi=L1, rdx=L2, rcx=input. */
	mov %rdi, %r8
	mov %rsi, %r9
	mov %rdx, %r10
	mov %rcx, %rsi
	vmovdqa .Lq(%rip), %ymm12
	vmovdqa .Lqminus1(%rip), %ymm13
	vpxor %ymm14, %ymm14, %ymm14

	CT_MERGE_L0_L2_DEBUG 0,    0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2_DEBUG 0,    4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2_DEBUG 0,    8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2_DEBUG 0,    12, 0xf5, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2_DEBUG 512,  0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2_DEBUG 512,  4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2_DEBUG 512,  8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2_DEBUG 512,  12, 0xf5, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2_DEBUG 1024, 0,  0xa0, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2_DEBUG 1024, 4,  0xa0, 1,9, 5,13, 3,11, 7,15
	CT_MERGE_L0_L2_DEBUG 1024, 8,  0xf5, 0,8, 4,12, 2,10, 6,14
	CT_MERGE_L0_L2_DEBUG 1024, 12, 0xf5, 1,9, 5,13, 3,11, 7,15

	vzeroupper
	ret
.size gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm,.-gt_d4aos_f32x3_invntt32_ct_l0_l2_checkpoints_asm
#endif

.section .rodata
.p2align 5
.Lq: .rept 16; .short 3457; .endr
.Lqminus1: .rept 16; .short 3456; .endr
.Lcenter10: .rept 16; .short 10; .endr
#include "generated/f32x3_ct_l0_l2/d4_aos_f32x3_ct_l0_l2_tables.inc"
#include "generated/f32x3_ct_l3_l4/d4_aos_f32x3_ct_l3_l4_tables.inc"
#include "generated/f32x3_dft3/d4_aos_f32x3_dft3_tables.inc"
#ifndef D4AOS_TERMINAL_TABLE_INCLUDE
#define D4AOS_TERMINAL_TABLE_INCLUDE "generated/f32x3_terminal/d4_aos_f32x3_terminal_tables.inc"
#endif
#include D4AOS_TERMINAL_TABLE_INCLUDE
.section .note.GNU-stack,"",@progbits
