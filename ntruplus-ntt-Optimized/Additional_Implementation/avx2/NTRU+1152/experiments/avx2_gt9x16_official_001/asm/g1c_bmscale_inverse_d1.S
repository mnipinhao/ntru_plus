.intel_syntax noprefix
.text

/*
 * G1C-M/C2-L keeps Official's degree-4 BMScale arithmetic order.  The only
 * arithmetic rekey is the generated lane-wise X^4 factor.  In linked mode,
 * each c_j is consumed by inverse distance-1 at its actual live cutpoint and
 * is stored only after that butterfly.
 */

.macro G1C_DIRECT_D1 result,row
  vpshufb ymm8, ymm\result, YMMWORD PTR [rip + .Lgt_g1c_bmscale_adjacent_word_swap]
  vpaddw ymm9, ymm\result, ymm8
  vpsubw ymm8, ymm\result, ymm8
  vpmullw ymm10, ymm8, YMMWORD PTR [rip + .Lgt_g1c_bmscale_row\row\()_direct_inverse_d1_qinv]
  vpmulhw ymm8, ymm8, YMMWORD PTR [rip + .Lgt_g1c_bmscale_row\row\()_direct_inverse_d1_zeta]
  vpmulhw ymm10, ymm10, ymm0
  vpsubw ymm8, ymm8, ymm10
  vpblendw ymm\result, ymm9, ymm8, 0xaa
.endm

.macro G1C_DIRECT_D1_STORE result,row,offset
  G1C_DIRECT_D1 \result,\row
  vmovdqa YMMWORD PTR [rdi + \offset], ymm\result
.endm

.macro G1C_RESULT_STORE mode,result,row,offset
  .ifc \mode,linked
    G1C_DIRECT_D1_STORE \result,\row,\offset
  .else
    vmovdqa YMMWORD PTR [rdi + \offset], ymm\result
  .endif
.endm

.macro G1C_BMSCALE_BLOCK branch,row,offset,mode
  /* Official BMScale load, product, add, and Montgomery-reduction order. */
  vmovdqa ymm1, YMMWORD PTR [rsi + \offset + 96]
  vmovdqa ymm2, YMMWORD PTR [rsi + \offset + 32]
  vmovdqa ymm3, YMMWORD PTR [rdx + \offset + 96]
  vmovdqa ymm4, YMMWORD PTR [rdx + \offset + 32]

  vpmullw ymm13, ymm15, ymm1
  vpmullw ymm14, ymm15, ymm2

  vpmullw ymm5, ymm14, ymm3
  vpmullw ymm6, ymm13, ymm4
  vpmullw ymm7, ymm13, ymm3
  vpmulhw ymm8, ymm2, ymm3
  vpmulhw ymm9, ymm1, ymm4
  vpmulhw ymm10, ymm1, ymm3

  vpmulhw ymm5, ymm5, ymm0
  vpmulhw ymm6, ymm6, ymm0
  vpmulhw ymm7, ymm7, ymm0
  vpsubw ymm8, ymm8, ymm5
  vpsubw ymm9, ymm9, ymm6
  vpsubw ymm10, ymm10, ymm7
  vpaddw ymm8, ymm8, ymm9

  vmovdqa ymm2, YMMWORD PTR [rsi + \offset + 64]
  vmovdqa ymm4, YMMWORD PTR [rdx + \offset + 64]
  vpmullw ymm14, ymm15, ymm2

  vpmullw ymm5, ymm14, ymm4
  vpmullw ymm6, ymm14, ymm3
  vpmullw ymm7, ymm13, ymm4
  vpmulhw ymm11, ymm2, ymm4
  vpmulhw ymm12, ymm2, ymm3
  vpmulhw ymm13, ymm1, ymm4

  vpmulhw ymm5, ymm5, ymm0
  vpmulhw ymm6, ymm6, ymm0
  vpmulhw ymm7, ymm7, ymm0
  vpsubw ymm11, ymm11, ymm5
  vpsubw ymm12, ymm12, ymm6
  vpsubw ymm13, ymm13, ymm7
  vpaddw ymm8, ymm8, ymm11
  vpaddw ymm9, ymm12, ymm13

  vpmullw ymm5, ymm8, YMMWORD PTR [rip + .Lgt_g1c_bmscale_branch\branch\()_row\row\()_factor_qinv]
  vpmullw ymm6, ymm9, YMMWORD PTR [rip + .Lgt_g1c_bmscale_branch\branch\()_row\row\()_factor_qinv]
  vpmullw ymm7, ymm10, YMMWORD PTR [rip + .Lgt_g1c_bmscale_branch\branch\()_row\row\()_factor_qinv]
  vpmulhw ymm8, ymm8, YMMWORD PTR [rip + .Lgt_g1c_bmscale_branch\branch\()_row\row\()_factor_zeta]
  vpmulhw ymm9, ymm9, YMMWORD PTR [rip + .Lgt_g1c_bmscale_branch\branch\()_row\row\()_factor_zeta]
  vpmulhw ymm10, ymm10, YMMWORD PTR [rip + .Lgt_g1c_bmscale_branch\branch\()_row\row\()_factor_zeta]
  vpmulhw ymm5, ymm5, ymm0
  vpmulhw ymm6, ymm6, ymm0
  vpmulhw ymm7, ymm7, ymm0
  vpsubw ymm5, ymm8, ymm5
  vpsubw ymm6, ymm9, ymm6
  vpsubw ymm7, ymm10, ymm7

  vmovdqa ymm1, YMMWORD PTR [rsi + \offset]
  vmovdqa ymm3, YMMWORD PTR [rdx + \offset]
  vpmullw ymm13, ymm15, ymm1

  vpmullw ymm8, ymm13, ymm3
  vpmullw ymm9, ymm13, ymm4
  vpmullw ymm10, ymm14, ymm3
  vpmulhw ymm11, ymm1, ymm3
  vpmulhw ymm12, ymm1, ymm4
  vpmulhw ymm14, ymm2, ymm3
  vpmulhw ymm8, ymm8, ymm0
  vpmulhw ymm9, ymm9, ymm0
  vpmulhw ymm10, ymm10, ymm0
  vpsubw ymm8, ymm11, ymm8
  vpsubw ymm9, ymm12, ymm9
  vpsubw ymm10, ymm14, ymm10
  vpaddw ymm5, ymm5, ymm8
  vpaddw ymm7, ymm7, ymm9
  vpaddw ymm7, ymm7, ymm10

  vmovdqa ymm2, YMMWORD PTR [rsi + \offset + 32]
  vmovdqa ymm4, YMMWORD PTR [rdx + \offset + 32]
  vpmullw ymm14, ymm15, ymm2

  vpmullw ymm8, ymm13, ymm4
  vpmullw ymm9, ymm14, ymm3
  vpmullw ymm10, ymm14, ymm4
  vpmulhw ymm11, ymm1, ymm4
  vpmulhw ymm12, ymm2, ymm3
  vpmulhw ymm13, ymm2, ymm4
  vpmulhw ymm8, ymm8, ymm0
  vpmulhw ymm9, ymm9, ymm0
  vpmulhw ymm10, ymm10, ymm0
  vpsubw ymm8, ymm11, ymm8
  vpsubw ymm9, ymm12, ymm9
  vpsubw ymm10, ymm13, ymm10
  vpaddw ymm6, ymm6, ymm8
  vpaddw ymm6, ymm6, ymm9
  vpaddw ymm7, ymm7, ymm10

  /* c0/c1/c2 are consumed before ymm7 is reused by the c3 tail. */
  G1C_RESULT_STORE \mode,5,\row,\offset
  G1C_RESULT_STORE \mode,6,\row,(\offset + 32)
  G1C_RESULT_STORE \mode,7,\row,(\offset + 64)

  vmovdqa ymm5, YMMWORD PTR [rsi + \offset + 64]
  vmovdqa ymm6, YMMWORD PTR [rsi + \offset + 96]
  vmovdqa ymm7, YMMWORD PTR [rdx + \offset + 64]
  vmovdqa ymm8, YMMWORD PTR [rdx + \offset + 96]

  vpmullw ymm13, ymm15, ymm1
  vpmullw ymm11, ymm15, ymm5
  vpmullw ymm12, ymm15, ymm6
  vpmullw ymm13, ymm13, ymm8
  vpmullw ymm14, ymm14, ymm7
  vpmullw ymm11, ymm11, ymm4
  vpmullw ymm12, ymm12, ymm3
  vpmulhw ymm1, ymm1, ymm8
  vpmulhw ymm2, ymm2, ymm7
  vpmulhw ymm5, ymm5, ymm4
  vpmulhw ymm6, ymm6, ymm3
  vpmulhw ymm13, ymm13, ymm0
  vpmulhw ymm14, ymm14, ymm0
  vpmulhw ymm11, ymm11, ymm0
  vpmulhw ymm12, ymm12, ymm0
  vpsubw ymm13, ymm1, ymm13
  vpsubw ymm14, ymm2, ymm14
  vpsubw ymm11, ymm5, ymm11
  vpsubw ymm12, ymm6, ymm12
  vpaddw ymm1, ymm13, ymm14
  vpaddw ymm2, ymm11, ymm12
  vpaddw ymm1, ymm1, ymm2

  G1C_RESULT_STORE \mode,1,\row,(\offset + 96)
.endm

.macro G1C_ALL_BLOCKS mode
  .irp branch,0,1
    .irp row,0,1,2,3,4,5,6,7,8
      G1C_BMSCALE_BLOCK \branch,\row,((\branch)*1152+(\row)*128),\mode
    .endr
  .endr
.endm

.macro G1C_MATERIALIZED_D1_VECTOR row,offset
  vmovdqa ymm5, YMMWORD PTR [rdi + \offset]
  G1C_DIRECT_D1 5,\row
  vmovdqa YMMWORD PTR [rdi + \offset], ymm5
.endm

.macro G1C_MATERIALIZED_D1_ALL
  .irp branch,0,1
    .irp row,0,1,2,3,4,5,6,7,8
      .irp coefficient,0,1,2,3
        G1C_MATERIALIZED_D1_VECTOR \row,((\branch)*1152+(\row)*128+(\coefficient)*32)
      .endr
    .endr
  .endr
.endm

.globl ntruplus1152_exp001_gt9x16_bmscale_raw
.type ntruplus1152_exp001_gt9x16_bmscale_raw,@function
ntruplus1152_exp001_gt9x16_bmscale_raw:
  vmovdqa ymm0, YMMWORD PTR [rip + .Lgt_g1c_bmscale_q]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_g1c_bmscale_qinv]
  G1C_ALL_BLOCKS raw
  ret
.size ntruplus1152_exp001_gt9x16_bmscale_raw, .-ntruplus1152_exp001_gt9x16_bmscale_raw

.globl ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized
.type ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized,@function
ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized:
  vmovdqa ymm0, YMMWORD PTR [rip + .Lgt_g1c_bmscale_q]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_g1c_bmscale_qinv]
  G1C_ALL_BLOCKS raw
  G1C_MATERIALIZED_D1_ALL
  ret
.size ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized, .-ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_materialized

.globl ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l
.type ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l,@function
ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l:
  vmovdqa ymm0, YMMWORD PTR [rip + .Lgt_g1c_bmscale_q]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_g1c_bmscale_qinv]
  G1C_ALL_BLOCKS linked
  ret
.size ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l, .-ntruplus1152_exp001_gt9x16_bmscale_inverse_d1_c2l

.include "generated/g1c-bmscale-live-tail.inc"

.section .note.GNU-stack,"",@progbits
