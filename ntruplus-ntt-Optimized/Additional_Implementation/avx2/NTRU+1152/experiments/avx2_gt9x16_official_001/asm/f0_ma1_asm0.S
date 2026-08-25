.intel_syntax noprefix
.text

/* Correctness-first fixed B0/P0 MA1 tile. No call, frame, or vzeroupper. */
.macro MA1_CENTER x,tmp
  vpmulhrsw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lf0_ma1_barrett]
  vpmullw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lf0_ma1_q]
  vpsubw ymm\x, ymm\x, ymm\tmp
  vpcmpgtw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lf0_ma1_half_q]
  vpand ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lf0_ma1_q]
  vpsubw ymm\x, ymm\x, ymm\tmp
  vpcmpgtw ymm\tmp, ymm12, ymm\x
  vpand ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lf0_ma1_q]
  vpaddw ymm\x, ymm\x, ymm\tmp
.endm

.macro MA1_MONT_CONST dst,a,factor,factor_qinv,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + \factor_qinv]
  vpmulhw ymm\dst, ymm\a, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lf0_ma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

.macro MA1_MONT_REG dst,a,b,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + .Lf0_ma1_qinv]
  vpmullw ymm\tmp, ymm\tmp, ymm\b
  vpmulhw ymm\dst, ymm\a, ymm\b
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lf0_ma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

/* mode: 0=plain, 1=lower-half wrapped, 2=both wrapped. */
.macro MA1_PRODUCT hbase,himm,rbase0,rbase1,rimm,mode
  vperm2i128 ymm6, ymm\hbase, ymm\hbase, \himm
  .if \rimm < 0
    MA1_MONT_REG 8,6,\rbase0,9
  .else
    vperm2i128 ymm7, ymm\rbase0, ymm\rbase1, \rimm
    MA1_MONT_REG 8,6,7,9
  .endif
  .if \mode == 0
    vpaddw ymm4, ymm4, ymm8
  .elseif \mode == 1
    vpand ymm10, ymm8, ymm11
    vpaddw ymm5, ymm5, ymm10
    vpandn ymm10, ymm11, ymm8
    vpaddw ymm4, ymm4, ymm10
  .else
    vpaddw ymm5, ymm5, ymm8
  .endif
.endm

.macro MA1_PAIR01 m_offset,lambda,lambda_qinv,out_offset
  vmovdqa ymm4, YMMWORD PTR [rdx + \m_offset]
  MA1_CENTER 4,9
  vpxor ymm5, ymm5, ymm5
  MA1_PRODUCT 0,0x00,2,2,-1,0
  MA1_PRODUCT 0,0x11,3,2,0x21,1
  MA1_PRODUCT 1,0x00,3,3,-1,2
  MA1_PRODUCT 1,0x11,2,3,0x21,2
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,9
  vpaddw ymm4, ymm4, ymm8
  MA1_MONT_CONST 4,4,.Lf0_ma1_inv4,.Lf0_ma1_inv4_qinv,9
  MA1_CENTER 4,9
  vmovdqa YMMWORD PTR [rdi + \out_offset], ymm4
.endm

.macro MA1_PAIR23 m_offset,lambda,lambda_qinv,out_offset
  vmovdqa ymm4, YMMWORD PTR [rdx + \m_offset]
  MA1_CENTER 4,9
  vpxor ymm5, ymm5, ymm5
  MA1_PRODUCT 0,0x00,3,3,-1,0
  MA1_PRODUCT 0,0x11,2,3,0x21,0
  MA1_PRODUCT 1,0x00,2,2,-1,0
  MA1_PRODUCT 1,0x11,3,2,0x21,1
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,9
  vpaddw ymm4, ymm4, ymm8
  MA1_MONT_CONST 4,4,.Lf0_ma1_inv4,.Lf0_ma1_inv4_qinv,9
  MA1_CENTER 4,9
  vmovdqa YMMWORD PTR [rdi + \out_offset], ymm4
.endm

.macro MA1_PROJECT_H_PLANE dst,a_offset,b_offset
  vmovdqa ymm\dst, YMMWORD PTR [rcx + \a_offset]
  vmovdqa ymm8, YMMWORD PTR [rcx + \b_offset]
  vperm2i128 ymm\dst, ymm\dst, ymm8, 0x31
  vpshufb ymm\dst, ymm\dst, YMMWORD PTR [rip + .Lf0_ma1_h_shuffle]
  vperm2i128 ymm8, ymm\dst, ymm\dst, 0x01
  vpblendw ymm\dst, ymm\dst, ymm8, 0x80
.endm

.macro MA1_STREAM r01_offset,r23_offset,m01_offset,m23_offset,lambda,lambda_qinv,out01,out23
  vmovdqa ymm0, YMMWORD PTR [rdi + \out01]
  vmovdqa ymm1, YMMWORD PTR [rdi + \out23]
  MA1_CENTER 0,9
  MA1_CENTER 1,9
  MA1_MONT_CONST 0,0,.Lf0_ma1_r2,.Lf0_ma1_r2_qinv,9
  MA1_MONT_CONST 1,1,.Lf0_ma1_r2,.Lf0_ma1_r2_qinv,9

  vmovdqa ymm2, YMMWORD PTR [rsi + \r01_offset]
  vmovdqa ymm3, YMMWORD PTR [rsi + \r23_offset]
  MA1_CENTER 2,9
  MA1_CENTER 3,9
  MA1_PAIR01 \m01_offset,\lambda,\lambda_qinv,\out01
  MA1_PAIR23 \m23_offset,\lambda,\lambda_qinv,\out23
.endm

.globl ntruplus1152_exp001_f0_ma1_asm0_b0p0
.type ntruplus1152_exp001_f0_ma1_asm0_b0p0,@function
.p2align 5
ntruplus1152_exp001_f0_ma1_asm0_b0p0:
  vmovdqa ymm11, YMMWORD PTR [rip + .Lf0_ma1_low_half]
  vmovdqa ymm12, YMMWORD PTR [rip + .Lf0_ma1_negative_half_q]

  /* Exact B0/P0 h projection, including the lane-7 cross-half exchange. */
  MA1_PROJECT_H_PLANE 0,256,384
  MA1_PROJECT_H_PLANE 1,288,416
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + 0], ymm8
  vmovdqa YMMWORD PTR [rdi + 32], ymm9
  MA1_PROJECT_H_PLANE 0,320,448
  MA1_PROJECT_H_PLANE 1,352,480
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + 64], ymm8
  vmovdqa YMMWORD PTR [rdi + 96], ymm9

  MA1_STREAM 0,64,0,64,.Lf0_ma1_lambda_s0,.Lf0_ma1_lambda_s0_qinv,0,64
  MA1_STREAM 32,96,32,96,.Lf0_ma1_lambda_s1,.Lf0_ma1_lambda_s1_qinv,32,96

  /* Convert the four pair-packed scratch vectors to semantic planes. */
  vmovdqa ymm0, YMMWORD PTR [rdi + 0]
  vmovdqa ymm1, YMMWORD PTR [rdi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + 0], ymm2
  vmovdqa YMMWORD PTR [rdi + 32], ymm3
  vmovdqa ymm0, YMMWORD PTR [rdi + 64]
  vmovdqa ymm1, YMMWORD PTR [rdi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + 64], ymm2
  vmovdqa YMMWORD PTR [rdi + 96], ymm3
  ret
.size ntruplus1152_exp001_f0_ma1_asm0_b0p0, .-ntruplus1152_exp001_f0_ma1_asm0_b0p0

.section .rodata
#include "generated/f0-ma1-asm0-constants.inc"

.section .note.GNU-stack,"",@progbits
