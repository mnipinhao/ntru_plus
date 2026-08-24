.intel_syntax noprefix
.text

/* One exact Barrett step; the generated proof supplies every input bound. */
.macro B1_REDUCE x
  vpmulhrsw ymm13, ymm\x, ymm14
  vpmullw ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
.endm

.macro B1_CENTER x
  B1_REDUCE \x
  vpcmpgtw ymm13, ymm\x, ymm11
  vpand ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
  vpcmpgtw ymm13, ymm12, ymm\x
  vpand ymm13, ymm13, ymm15
  vpaddw ymm\x, ymm\x, ymm13
.endm

.macro B1_MONT x,zeta,qinv
  vpmullw ymm13, ymm\x, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\x, ymm\x, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
.endm

/* In-place inverse paper radix-3. ymm9..ymm12 are the only scratch. */
.macro B1_R3 a,b,c
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

.macro B1_BLOCK branch,j,layout
  .set B1_BASE, (\branch)*1152 + (\j)*32
  .ifc \layout,B
    vmovdqu ymm0, YMMWORD PTR [rsi + B1_BASE + 0*128]
    vmovdqu ymm1, YMMWORD PTR [rsi + B1_BASE + 1*128]
    vmovdqu ymm2, YMMWORD PTR [rsi + B1_BASE + 2*128]
    vmovdqu ymm3, YMMWORD PTR [rsi + B1_BASE + 3*128]
    vmovdqu ymm4, YMMWORD PTR [rsi + B1_BASE + 4*128]
    vmovdqu ymm5, YMMWORD PTR [rsi + B1_BASE + 5*128]
    vmovdqu ymm6, YMMWORD PTR [rsi + B1_BASE + 6*128]
    vmovdqu ymm7, YMMWORD PTR [rsi + B1_BASE + 7*128]
    vmovdqu ymm8, YMMWORD PTR [rsi + B1_BASE + 8*128]
  .else
    vmovdqu ymm0, YMMWORD PTR [rsi + B1_BASE + 0*128]
    vmovdqu ymm1, YMMWORD PTR [rsi + B1_BASE + 3*128]
    vmovdqu ymm2, YMMWORD PTR [rsi + B1_BASE + 6*128]
    vmovdqu ymm3, YMMWORD PTR [rsi + B1_BASE + 1*128]
    vmovdqu ymm4, YMMWORD PTR [rsi + B1_BASE + 4*128]
    vmovdqu ymm5, YMMWORD PTR [rsi + B1_BASE + 7*128]
    vmovdqu ymm6, YMMWORD PTR [rsi + B1_BASE + 8*128]
    vmovdqu ymm7, YMMWORD PTR [rsi + B1_BASE + 2*128]
    vmovdqu ymm8, YMMWORD PTR [rsi + B1_BASE + 5*128]
  .endif
  B1_REDUCE 0
  B1_REDUCE 1
  B1_REDUCE 2
  B1_REDUCE 3
  B1_REDUCE 4
  B1_REDUCE 5
  B1_REDUCE 6
  B1_REDUCE 7
  B1_REDUCE 8

  B1_R3 0,1,2
  B1_R3 3,4,5
  B1_R3 6,7,8

  B1_REDUCE 0
  B1_REDUCE 3
  B1_MONT 4,.Litail_b0_rho_inv,.Litail_b0_rho_inv_qinv
  B1_MONT 5,.Litail_b0_rho,.Litail_b0_rho_qinv
  B1_REDUCE 6
  B1_MONT 7,.Litail_b0_rho,.Litail_b0_rho_qinv
  B1_MONT 8,.Litail_b0_rho_inv,.Litail_b0_rho_inv_qinv

  B1_R3 0,3,6
  B1_R3 1,4,7
  B1_R3 2,5,8

  vmovdqa ymm11, YMMWORD PTR [rip + .Litail_b0_half_q]
  vmovdqa ymm12, YMMWORD PTR [rip + .Litail_b0_negative_half_q]
  B1_CENTER 0
  B1_CENTER 1
  B1_CENTER 2
  B1_CENTER 3
  B1_CENTER 4
  B1_CENTER 5
  B1_CENTER 6
  B1_CENTER 7
  B1_CENTER 8

  vmovdqu YMMWORD PTR [rdi + B1_BASE + 0*128], ymm0
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 3*128], ymm3
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 6*128], ymm6
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 1*128], ymm1
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 4*128], ymm4
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 7*128], ymm7
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 8*128], ymm2
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 2*128], ymm5
  vmovdqu YMMWORD PTR [rdi + B1_BASE + 5*128], ymm8
.endm

.globl ntruplus1152_exp001_inverse_ntt9_b1
.type ntruplus1152_exp001_inverse_ntt9_b1,@function
ntruplus1152_exp001_inverse_ntt9_b1:
  vmovdqa ymm15, YMMWORD PTR [rip + .Litail_b0_q]
  vmovdqa ymm14, YMMWORD PTR [rip + .Litail_b0_barrett]
  B1_BLOCK 0,0,B
  B1_BLOCK 0,1,B
  B1_BLOCK 0,2,B
  B1_BLOCK 0,3,B
  B1_BLOCK 1,0,B
  B1_BLOCK 1,1,B
  B1_BLOCK 1,2,B
  B1_BLOCK 1,3,B
  ret
.size ntruplus1152_exp001_inverse_ntt9_b1, .-ntruplus1152_exp001_inverse_ntt9_b1

.globl ntruplus1152_exp001_inverse_ntt9_b1_from_vector_canonical_p
.type ntruplus1152_exp001_inverse_ntt9_b1_from_vector_canonical_p,@function
ntruplus1152_exp001_inverse_ntt9_b1_from_vector_canonical_p:
  vmovdqa ymm15, YMMWORD PTR [rip + .Litail_b0_q]
  vmovdqa ymm14, YMMWORD PTR [rip + .Litail_b0_barrett]
  B1_BLOCK 0,0,A
  B1_BLOCK 0,1,A
  B1_BLOCK 0,2,A
  B1_BLOCK 0,3,A
  B1_BLOCK 1,0,A
  B1_BLOCK 1,1,A
  B1_BLOCK 1,2,A
  B1_BLOCK 1,3,A
  ret
.size ntruplus1152_exp001_inverse_ntt9_b1_from_vector_canonical_p, .-ntruplus1152_exp001_inverse_ntt9_b1_from_vector_canonical_p

.macro B1_REPACK_BLOCK branch,j
  .set B1_REPACK_BASE, (\branch)*1152 + (\j)*32
  vmovdqu ymm0, YMMWORD PTR [rsi + B1_REPACK_BASE + 0*128]
  vmovdqu ymm1, YMMWORD PTR [rsi + B1_REPACK_BASE + 1*128]
  vmovdqu ymm2, YMMWORD PTR [rsi + B1_REPACK_BASE + 2*128]
  vmovdqu ymm3, YMMWORD PTR [rsi + B1_REPACK_BASE + 3*128]
  vmovdqu ymm4, YMMWORD PTR [rsi + B1_REPACK_BASE + 4*128]
  vmovdqu ymm5, YMMWORD PTR [rsi + B1_REPACK_BASE + 5*128]
  vmovdqu ymm6, YMMWORD PTR [rsi + B1_REPACK_BASE + 6*128]
  vmovdqu ymm7, YMMWORD PTR [rsi + B1_REPACK_BASE + 7*128]
  vmovdqu ymm8, YMMWORD PTR [rsi + B1_REPACK_BASE + 8*128]
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 0*128], ymm0
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 3*128], ymm1
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 6*128], ymm2
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 1*128], ymm3
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 4*128], ymm4
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 7*128], ymm5
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 8*128], ymm6
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 2*128], ymm7
  vmovdqu YMMWORD PTR [rdi + B1_REPACK_BASE + 5*128], ymm8
.endm

.globl ntruplus1152_exp001_inverse9_b1_repack_vector_canonical_p
.type ntruplus1152_exp001_inverse9_b1_repack_vector_canonical_p,@function
ntruplus1152_exp001_inverse9_b1_repack_vector_canonical_p:
  B1_REPACK_BLOCK 0,0
  B1_REPACK_BLOCK 0,1
  B1_REPACK_BLOCK 0,2
  B1_REPACK_BLOCK 0,3
  B1_REPACK_BLOCK 1,0
  B1_REPACK_BLOCK 1,1
  B1_REPACK_BLOCK 1,2
  B1_REPACK_BLOCK 1,3
  ret
.size ntruplus1152_exp001_inverse9_b1_repack_vector_canonical_p, .-ntruplus1152_exp001_inverse9_b1_repack_vector_canonical_p

.include "generated/g1c-inverse-ntt9-b0-constants.inc"
.section .note.GNU-stack,"",@progbits
