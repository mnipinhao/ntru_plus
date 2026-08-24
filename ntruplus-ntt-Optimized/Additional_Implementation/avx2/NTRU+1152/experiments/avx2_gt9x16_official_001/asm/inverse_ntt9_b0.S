.intel_syntax noprefix
.text

/* One exact Barrett step; the generated proof supplies every input bound. */
.macro B0_REDUCE x
  vpmulhrsw ymm13, ymm\x, ymm14
  vpmullw ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
.endm

.macro B0_CENTER x
  B0_REDUCE \x
  vpcmpgtw ymm13, ymm\x, ymm11
  vpand ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
  vpcmpgtw ymm13, ymm12, ymm\x
  vpand ymm13, ymm13, ymm15
  vpaddw ymm\x, ymm\x, ymm13
.endm

.macro B0_MONT x,zeta,qinv
  vpmullw ymm13, ymm\x, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\x, ymm\x, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm13, ymm13, ymm15
  vpsubw ymm\x, ymm\x, ymm13
.endm

/* In-place inverse paper radix-3. ymm9..ymm12 are the only scratch. */
.macro B0_R3 a,b,c
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

.macro B0_BLOCK branch,j,layout
  .set B0_BASE, (\branch)*1152 + (\j)*32
  .ifc \layout,B
    vmovdqu ymm0, YMMWORD PTR [rsi + B0_BASE + 0*128]
    vmovdqu ymm1, YMMWORD PTR [rsi + B0_BASE + 1*128]
    vmovdqu ymm2, YMMWORD PTR [rsi + B0_BASE + 2*128]
    vmovdqu ymm3, YMMWORD PTR [rsi + B0_BASE + 3*128]
    vmovdqu ymm4, YMMWORD PTR [rsi + B0_BASE + 4*128]
    vmovdqu ymm5, YMMWORD PTR [rsi + B0_BASE + 5*128]
    vmovdqu ymm6, YMMWORD PTR [rsi + B0_BASE + 6*128]
    vmovdqu ymm7, YMMWORD PTR [rsi + B0_BASE + 7*128]
    vmovdqu ymm8, YMMWORD PTR [rsi + B0_BASE + 8*128]
  .else
    vmovdqu ymm0, YMMWORD PTR [rsi + B0_BASE + 0*128]
    vmovdqu ymm1, YMMWORD PTR [rsi + B0_BASE + 3*128]
    vmovdqu ymm2, YMMWORD PTR [rsi + B0_BASE + 6*128]
    vmovdqu ymm3, YMMWORD PTR [rsi + B0_BASE + 1*128]
    vmovdqu ymm4, YMMWORD PTR [rsi + B0_BASE + 4*128]
    vmovdqu ymm5, YMMWORD PTR [rsi + B0_BASE + 7*128]
    vmovdqu ymm6, YMMWORD PTR [rsi + B0_BASE + 8*128]
    vmovdqu ymm7, YMMWORD PTR [rsi + B0_BASE + 2*128]
    vmovdqu ymm8, YMMWORD PTR [rsi + B0_BASE + 5*128]
  .endif
  B0_REDUCE 0
  B0_REDUCE 1
  B0_REDUCE 2
  B0_REDUCE 3
  B0_REDUCE 4
  B0_REDUCE 5
  B0_REDUCE 6
  B0_REDUCE 7
  B0_REDUCE 8

  B0_R3 0,1,2
  B0_R3 3,4,5
  B0_R3 6,7,8

  B0_REDUCE 0
  B0_REDUCE 1
  B0_REDUCE 2
  B0_REDUCE 3
  B0_MONT 4,.Litail_b0_rho_inv,.Litail_b0_rho_inv_qinv
  B0_MONT 5,.Litail_b0_rho,.Litail_b0_rho_qinv
  B0_REDUCE 6
  B0_MONT 7,.Litail_b0_rho,.Litail_b0_rho_qinv
  B0_MONT 8,.Litail_b0_rho_inv,.Litail_b0_rho_inv_qinv

  B0_R3 0,3,6
  B0_R3 1,4,7
  B0_R3 2,5,8

  vmovdqa ymm11, YMMWORD PTR [rip + .Litail_b0_half_q]
  vmovdqa ymm12, YMMWORD PTR [rip + .Litail_b0_negative_half_q]
  B0_CENTER 0
  B0_CENTER 1
  B0_CENTER 2
  B0_CENTER 3
  B0_CENTER 4
  B0_CENTER 5
  B0_CENTER 6
  B0_CENTER 7
  B0_CENTER 8

  vmovdqu YMMWORD PTR [rdi + B0_BASE + 0*128], ymm0
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 3*128], ymm3
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 6*128], ymm6
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 1*128], ymm1
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 4*128], ymm4
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 7*128], ymm7
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 8*128], ymm2
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 2*128], ymm5
  vmovdqu YMMWORD PTR [rdi + B0_BASE + 5*128], ymm8
.endm

.globl ntruplus1152_exp001_inverse_ntt9_b0
.type ntruplus1152_exp001_inverse_ntt9_b0,@function
ntruplus1152_exp001_inverse_ntt9_b0:
  vmovdqa ymm15, YMMWORD PTR [rip + .Litail_b0_q]
  vmovdqa ymm14, YMMWORD PTR [rip + .Litail_b0_barrett]
  B0_BLOCK 0,0,B
  B0_BLOCK 0,1,B
  B0_BLOCK 0,2,B
  B0_BLOCK 0,3,B
  B0_BLOCK 1,0,B
  B0_BLOCK 1,1,B
  B0_BLOCK 1,2,B
  B0_BLOCK 1,3,B
  ret
.size ntruplus1152_exp001_inverse_ntt9_b0, .-ntruplus1152_exp001_inverse_ntt9_b0

.globl ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p
.type ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p,@function
ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p:
  vmovdqa ymm15, YMMWORD PTR [rip + .Litail_b0_q]
  vmovdqa ymm14, YMMWORD PTR [rip + .Litail_b0_barrett]
  B0_BLOCK 0,0,A
  B0_BLOCK 0,1,A
  B0_BLOCK 0,2,A
  B0_BLOCK 0,3,A
  B0_BLOCK 1,0,A
  B0_BLOCK 1,1,A
  B0_BLOCK 1,2,A
  B0_BLOCK 1,3,A
  ret
.size ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p, .-ntruplus1152_exp001_inverse_ntt9_b0_from_vector_canonical_p

.macro B0_REPACK_BLOCK branch,j
  .set B0_REPACK_BASE, (\branch)*1152 + (\j)*32
  vmovdqu ymm0, YMMWORD PTR [rsi + B0_REPACK_BASE + 0*128]
  vmovdqu ymm1, YMMWORD PTR [rsi + B0_REPACK_BASE + 1*128]
  vmovdqu ymm2, YMMWORD PTR [rsi + B0_REPACK_BASE + 2*128]
  vmovdqu ymm3, YMMWORD PTR [rsi + B0_REPACK_BASE + 3*128]
  vmovdqu ymm4, YMMWORD PTR [rsi + B0_REPACK_BASE + 4*128]
  vmovdqu ymm5, YMMWORD PTR [rsi + B0_REPACK_BASE + 5*128]
  vmovdqu ymm6, YMMWORD PTR [rsi + B0_REPACK_BASE + 6*128]
  vmovdqu ymm7, YMMWORD PTR [rsi + B0_REPACK_BASE + 7*128]
  vmovdqu ymm8, YMMWORD PTR [rsi + B0_REPACK_BASE + 8*128]
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 0*128], ymm0
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 3*128], ymm1
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 6*128], ymm2
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 1*128], ymm3
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 4*128], ymm4
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 7*128], ymm5
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 8*128], ymm6
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 2*128], ymm7
  vmovdqu YMMWORD PTR [rdi + B0_REPACK_BASE + 5*128], ymm8
.endm

.globl ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p
.type ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p,@function
ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p:
  B0_REPACK_BLOCK 0,0
  B0_REPACK_BLOCK 0,1
  B0_REPACK_BLOCK 0,2
  B0_REPACK_BLOCK 0,3
  B0_REPACK_BLOCK 1,0
  B0_REPACK_BLOCK 1,1
  B0_REPACK_BLOCK 1,2
  B0_REPACK_BLOCK 1,3
  ret
.size ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p, .-ntruplus1152_exp001_inverse9_b0_repack_vector_canonical_p

.include "generated/g1c-inverse-ntt9-b0-constants.inc"
.section .note.GNU-stack,"",@progbits
