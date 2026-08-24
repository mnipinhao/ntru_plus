.intel_syntax noprefix
.text

.macro D0_REDUCE x
  vpmulhrsw ymm13, ymm\x, ymm14
  vpmullw ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
.endm

.macro D0_CENTER x
  D0_REDUCE \x
  vpcmpgtw ymm13, ymm\x, ymm11
  vpand ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
  vpcmpgtw ymm13, ymm12, ymm\x
  vpand ymm13, ymm13, ymm15
  vpaddw ymm\x, ymm\x, ymm13
.endm

.macro D0_MONT x,zeta,qinv
  vpmullw ymm13, ymm\x, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\x, ymm\x, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
.endm

.macro D0_R3 a,b,c
  vpaddw ymm9, ymm\b, ymm\c
  vpsubw ymm10, ymm\b, ymm\c
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Litail_b0_kappa_inv_qinv]
  vpmulhw ymm10, ymm10, YMMWORD PTR [rip + .Litail_b0_kappa_inv]
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm10, ymm10, ymm11
  vpaddw ymm11, ymm\a, ymm\a
  vpsubw ymm12, ymm11, ymm9
  vpaddw ymm\a, ymm11, ymm9
  vpaddw ymm\a, ymm\a, ymm9
  vpaddw ymm\b, ymm12, ymm10
  vpsubw ymm\c, ymm12, ymm10
.endm

.macro D0_INVERSE_STAGE result,row,distance,blend
  .if \distance == 2
    vpshufb ymm9, ymm\result, YMMWORD PTR [rip + .Lgt_g1c_m3_swap_d2]
  .elseif \distance == 4
    vpshufb ymm9, ymm\result, YMMWORD PTR [rip + .Lgt_g1c_m3_swap_d4]
  .else
    vperm2i128 ymm9, ymm\result, ymm\result, 0x01
  .endif
  vpaddw ymm10, ymm\result, ymm9
  vpsubw ymm9, ymm\result, ymm9
  vpmullw ymm11, ymm9, YMMWORD PTR [rip + .Lgt_g1c_m3_row\row\()_d\distance\()_qinv]
  vpmulhw ymm9, ymm9, YMMWORD PTR [rip + .Lgt_g1c_m3_row\row\()_d\distance\()_zeta]
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm9, ymm9, ymm11
  .if \distance == 8
    vperm2i128 ymm\result, ymm10, ymm9, 0x30
  .else
    vpblendw ymm\result, ymm10, ymm9, \blend
  .endif
.endm

.macro D0_PRODUCE result,branch,row,j,source
  .set D0_OFFSET, (\branch)*1152 + (\row)*128 + (\j)*32
  vmovdqu ymm\result, YMMWORD PTR [\source + D0_OFFSET]
  D0_INVERSE_STAGE \result,\row,2,0xcc
  D0_INVERSE_STAGE \result,\row,4,0xf0
  D0_INVERSE_STAGE \result,\row,8,0
.endm

.macro D0_FINISH_BLOCK branch,j,destination
  D0_REDUCE 0
  D0_REDUCE 3
  D0_MONT 4,.Litail_b0_rho_inv,.Litail_b0_rho_inv_qinv
  D0_MONT 5,.Litail_b0_rho,.Litail_b0_rho_qinv
  D0_REDUCE 6
  D0_MONT 7,.Litail_b0_rho,.Litail_b0_rho_qinv
  D0_MONT 8,.Litail_b0_rho_inv,.Litail_b0_rho_inv_qinv

  D0_R3 0,3,6
  D0_R3 1,4,7
  D0_R3 2,5,8

  vmovdqa ymm11, YMMWORD PTR [rip + .Litail_b0_half_q]
  vmovdqa ymm12, YMMWORD PTR [rip + .Litail_b0_negative_half_q]
  D0_CENTER 0
  D0_CENTER 1
  D0_CENTER 2
  D0_CENTER 3
  D0_CENTER 4
  D0_CENTER 5
  D0_CENTER 6
  D0_CENTER 7
  D0_CENTER 8

  .set D0_BASE, (\branch)*1152 + (\j)*32
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 0*128], ymm0
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 3*128], ymm3
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 6*128], ymm6
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 1*128], ymm1
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 4*128], ymm4
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 7*128], ymm7
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 8*128], ymm2
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 2*128], ymm5
  vmovdqu YMMWORD PTR [\destination + D0_BASE + 5*128], ymm8
.endm

.macro D0_B1_FROM_MEMORY branch,j,source,destination
  .set D0_BASE, (\branch)*1152 + (\j)*32
  vmovdqu ymm0, YMMWORD PTR [\source + D0_BASE + 0*128]
  vmovdqu ymm1, YMMWORD PTR [\source + D0_BASE + 1*128]
  vmovdqu ymm2, YMMWORD PTR [\source + D0_BASE + 2*128]
  vmovdqu ymm3, YMMWORD PTR [\source + D0_BASE + 3*128]
  vmovdqu ymm4, YMMWORD PTR [\source + D0_BASE + 4*128]
  vmovdqu ymm5, YMMWORD PTR [\source + D0_BASE + 5*128]
  vmovdqu ymm6, YMMWORD PTR [\source + D0_BASE + 6*128]
  vmovdqu ymm7, YMMWORD PTR [\source + D0_BASE + 7*128]
  vmovdqu ymm8, YMMWORD PTR [\source + D0_BASE + 8*128]
  D0_REDUCE 0
  D0_REDUCE 1
  D0_REDUCE 2
  D0_REDUCE 3
  D0_REDUCE 4
  D0_REDUCE 5
  D0_REDUCE 6
  D0_REDUCE 7
  D0_REDUCE 8
  D0_R3 0,1,2
  D0_R3 3,4,5
  D0_R3 6,7,8
  D0_FINISH_BLOCK \branch,\j,\destination
.endm

.macro D0_LINKED_BLOCK branch,j,source,destination
  D0_PRODUCE 0,\branch,0,\j,\source
  D0_REDUCE 0
  D0_PRODUCE 1,\branch,1,\j,\source
  D0_REDUCE 1
  D0_PRODUCE 2,\branch,2,\j,\source
  D0_REDUCE 2
  D0_R3 0,1,2

  D0_PRODUCE 3,\branch,3,\j,\source
  D0_REDUCE 3
  D0_PRODUCE 4,\branch,4,\j,\source
  D0_REDUCE 4
  D0_PRODUCE 5,\branch,5,\j,\source
  D0_REDUCE 5
  D0_R3 3,4,5

  D0_PRODUCE 6,\branch,6,\j,\source
  D0_REDUCE 6
  D0_PRODUCE 7,\branch,7,\j,\source
  D0_REDUCE 7
  D0_PRODUCE 8,\branch,8,\j,\source
  D0_REDUCE 8
  D0_R3 6,7,8
  D0_FINISH_BLOCK \branch,\j,\destination
.endm

.macro D0_MATERIALIZE_ALL source,destination
  .irp branch,0,1
    .irp row,0,1,2,3,4,5,6,7,8
      .irp j,0,1,2,3
        D0_PRODUCE 0,\branch,\row,\j,\source
        .set D0_STORE_OFFSET, (\branch)*1152 + (\row)*128 + (\j)*32
        vmovdqu YMMWORD PTR [\destination + D0_STORE_OFFSET], ymm0
      .endr
    .endr
  .endr
.endm

.globl ntruplus1152_exp001_inverse_tail_d0_m0
.type ntruplus1152_exp001_inverse_tail_d0_m0,@function
ntruplus1152_exp001_inverse_tail_d0_m0:
  vmovdqa ymm15, YMMWORD PTR [rip + .Litail_b0_q]
  vmovdqa ymm14, YMMWORD PTR [rip + .Litail_b0_barrett]
  D0_MATERIALIZE_ALL rsi,rdi
  .irp branch,0,1
    .irp j,0,1,2,3
      D0_B1_FROM_MEMORY \branch,\j,rdi,rdi
    .endr
  .endr
  ret
.size ntruplus1152_exp001_inverse_tail_d0_m0, .-ntruplus1152_exp001_inverse_tail_d0_m0

.globl ntruplus1152_exp001_inverse_tail_d0_m1
.type ntruplus1152_exp001_inverse_tail_d0_m1,@function
ntruplus1152_exp001_inverse_tail_d0_m1:
  vmovdqa ymm15, YMMWORD PTR [rip + .Litail_b0_q]
  vmovdqa ymm14, YMMWORD PTR [rip + .Litail_b0_barrett]
  .irp branch,0,1
    .irp j,0,1,2,3
      D0_LINKED_BLOCK \branch,\j,rsi,rdi
    .endr
  .endr
  ret
.size ntruplus1152_exp001_inverse_tail_d0_m1, .-ntruplus1152_exp001_inverse_tail_d0_m1

.include "generated/g1c-m3-inverse16.inc"
.include "generated/g1c-inverse-ntt9-b0-constants.inc"
.section .note.GNU-stack,"",@progbits
