.intel_syntax noprefix
.text

.macro MA1_CENTER x,tmp
  vpmulhrsw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\x, ymm\x, ymm\tmp
  vpcmpgtw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lma1_half_q]
  vpand ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\x, ymm\x, ymm\tmp
  vmovdqa ymm\tmp, YMMWORD PTR [rip + .Lma1_negative_half_q]
  vpcmpgtw ymm\tmp, ymm\tmp, ymm\x
  vpand ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm\x, ymm\x, ymm\tmp
.endm

.macro MA1_CENTER2 a,b,ta,tb
  vpmulhrsw ymm\ta, ymm\a, YMMWORD PTR [rip + .Lma1_barrett]
  vpmulhrsw ymm\tb, ymm\b, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\a, ymm\a, ymm\ta
  vpsubw ymm\b, ymm\b, ymm\tb
  vpcmpgtw ymm\ta, ymm\a, YMMWORD PTR [rip + .Lma1_half_q]
  vpcmpgtw ymm\tb, ymm\b, YMMWORD PTR [rip + .Lma1_half_q]
  vpand ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\a, ymm\a, ymm\ta
  vpsubw ymm\b, ymm\b, ymm\tb
  vmovdqa ymm\ta, YMMWORD PTR [rip + .Lma1_negative_half_q]
  vmovdqa ymm\tb, YMMWORD PTR [rip + .Lma1_negative_half_q]
  vpcmpgtw ymm\ta, ymm\ta, ymm\a
  vpcmpgtw ymm\tb, ymm\tb, ymm\b
  vpand ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm\a, ymm\a, ymm\ta
  vpaddw ymm\b, ymm\b, ymm\tb
.endm

.macro MA1_MONT_CONST dst,a,factor,factor_qinv,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + \factor_qinv]
  vpmulhw ymm\dst, ymm\a, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

.macro MA1_MONT_CONST2 da,db,a,b,factor,factor_qinv,ta,tb
  vpmullw ymm\ta, ymm\a, YMMWORD PTR [rip + \factor_qinv]
  vpmullw ymm\tb, ymm\b, YMMWORD PTR [rip + \factor_qinv]
  vpmulhw ymm\da, ymm\a, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\db, ymm\b, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpmulhw ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\da, ymm\da, ymm\ta
  vpsubw ymm\db, ymm\db, ymm\tb
.endm

.macro MA1_MONT_REG dst,a,b,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\tmp, ymm\tmp, ymm\b
  vpmulhw ymm\dst, ymm\a, ymm\b
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

.macro MA1_MONT_REG2 da,db,a,b,ra,rb,ta,tb
  vpmullw ymm\ta, ymm\a, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\tb, ymm\b, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\ta, ymm\ta, ymm\ra
  vpmullw ymm\tb, ymm\tb, ymm\rb
  vpmulhw ymm\da, ymm\a, ymm\ra
  vpmulhw ymm\db, ymm\b, ymm\rb
  vpmulhw ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpmulhw ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\da, ymm\da, ymm\ta
  vpsubw ymm\db, ymm\db, ymm\tb
.endm

.macro MA1_PROJECT_H dst,tmp,aoff,boff,imm,mask,blend
  vmovdqa ymm\dst, YMMWORD PTR [rcx + \aoff]
  vmovdqa ymm\tmp, YMMWORD PTR [rcx + \boff]
  vperm2i128 ymm\dst, ymm\dst, ymm\tmp, \imm
  vpshufb ymm\dst, ymm\dst, YMMWORD PTR [rip + \mask]
  vperm2i128 ymm\tmp, ymm\dst, ymm\dst, 0x01
  vpblendw ymm\dst, ymm\dst, ymm\tmp, \blend
.endm

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
    vpand ymm10, ymm8, YMMWORD PTR [rip + .Lma1_low_half]
    vpaddw ymm5, ymm5, ymm10
    vpxor ymm10, ymm10, ymm8
    vpaddw ymm4, ymm4, ymm10
  .else
    vpaddw ymm5, ymm5, ymm8
  .endif
.endm

.macro MA1_PAIR01 mbase,moff,lambda,lambda_qinv,outoff
  vmovdqa ymm4, YMMWORD PTR [rdx + \mbase + \moff]
  MA1_CENTER 4,9
  vpxor ymm5, ymm5, ymm5
  MA1_PRODUCT 0,0x00,2,2,-1,0
  MA1_PRODUCT 0,0x11,3,2,0x21,1
  MA1_PRODUCT 1,0x00,3,3,-1,2
  MA1_PRODUCT 1,0x11,2,3,0x21,2
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,9
  vpaddw ymm4, ymm4, ymm8
  MA1_MONT_CONST 4,4,.Lma1_inv4,.Lma1_inv4_qinv,9
  MA1_CENTER 4,9
  vmovdqa YMMWORD PTR [r8 + \outoff], ymm4
.endm

.macro MA1_PAIR23 mbase,moff,lambda,lambda_qinv,outoff
  vmovdqa ymm4, YMMWORD PTR [rdx + \mbase + \moff]
  MA1_CENTER 4,9
  vpxor ymm5, ymm5, ymm5
  MA1_PRODUCT 0,0x00,3,3,-1,0
  MA1_PRODUCT 0,0x11,2,3,0x21,0
  MA1_PRODUCT 1,0x00,2,2,-1,0
  MA1_PRODUCT 1,0x11,3,2,0x21,1
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,9
  vpaddw ymm4, ymm4, ymm8
  MA1_MONT_CONST 4,4,.Lma1_inv4,.Lma1_inv4_qinv,9
  MA1_CENTER 4,9
  vmovdqa YMMWORD PTR [r8 + \outoff], ymm4
.endm

.macro MA1_STREAM_C0 rbase,mbase,roff0,roff1,moff0,moff1,lambda,lambda_qinv,h0,h1,out0,out1
  vmovdqa ymm0, YMMWORD PTR [r8 + \h0]
  vmovdqa ymm1, YMMWORD PTR [r8 + \h1]
  MA1_CENTER 0,9
  MA1_CENTER 1,9
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,9
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,9
  vmovdqa ymm2, YMMWORD PTR [rsi + \rbase + \roff0]
  vmovdqa ymm3, YMMWORD PTR [rsi + \rbase + \roff1]
  MA1_CENTER 2,9
  MA1_CENTER 3,9
  MA1_PAIR01 \mbase,\moff0,\lambda,\lambda_qinv,\out0
  MA1_PAIR23 \mbase,\moff1,\lambda,\lambda_qinv,\out1
.endm

.macro MA1_PACK_CHUNK ctoff
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vmovdqa ymm1, YMMWORD PTR [r8 + 288]
  vmovdqa ymm2, YMMWORD PTR [r8 + 320]
  vmovdqa ymm3, YMMWORD PTR [r8 + 352]
  vmovdqa ymm4, YMMWORD PTR [r8 + 384]
  vmovdqa ymm5, YMMWORD PTR [r8 + 416]
  vmovdqa ymm6, YMMWORD PTR [r8 + 448]
  vmovdqa ymm7, YMMWORD PTR [r8 + 480]
  vpmulhrsw ymm10, ymm0, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm11, ymm1, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm12, ymm2, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm13, ymm3, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmullw ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm10
  vpsubw ymm1, ymm1, ymm11
  vpsubw ymm2, ymm2, ymm12
  vpsubw ymm3, ymm3, ymm13
  vpmulhrsw ymm10, ymm4, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm11, ymm5, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm12, ymm6, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm13, ymm7, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmullw ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm10
  vpsubw ymm5, ymm5, ymm11
  vpsubw ymm6, ymm6, ymm12
  vpsubw ymm7, ymm7, ymm13
  vpsraw ymm10, ymm0, 15
  vpsraw ymm11, ymm1, 15
  vpsraw ymm12, ymm2, 15
  vpsraw ymm13, ymm3, 15
  vpand ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm10
  vpaddw ymm1, ymm1, ymm11
  vpaddw ymm2, ymm2, ymm12
  vpaddw ymm3, ymm3, ymm13
  vpsraw ymm10, ymm4, 15
  vpsraw ymm11, ymm5, 15
  vpsraw ymm12, ymm6, 15
  vpsraw ymm13, ymm7, 15
  vpand ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm10
  vpaddw ymm5, ymm5, ymm11
  vpaddw ymm6, ymm6, ymm12
  vpaddw ymm7, ymm7, ymm13
  vpsllw ymm10, ymm1, 12
  vpsllw ymm11, ymm5, 12
  vpxor ymm0, ymm0, ymm10
  vpxor ymm4, ymm4, ymm11
  vpsllw ymm10, ymm2, 8
  vpsllw ymm11, ymm6, 8
  vpsrlw ymm12, ymm1, 4
  vpsrlw ymm13, ymm5, 4
  vpxor ymm1, ymm12, ymm10
  vpxor ymm5, ymm13, ymm11
  vpsllw ymm10, ymm3, 4
  vpsllw ymm11, ymm7, 4
  vpsrlw ymm12, ymm2, 8
  vpsrlw ymm13, ymm6, 8
  vpxor ymm2, ymm12, ymm10
  vpxor ymm6, ymm13, ymm11
  vpslld ymm7, ymm1, 16
  vpslld ymm8, ymm4, 16
  vpslld ymm9, ymm6, 16
  vpblendw ymm7, ymm0, ymm7, 0xaa
  vpblendw ymm8, ymm2, ymm8, 0xaa
  vpblendw ymm9, ymm5, ymm9, 0xaa
  vpsrlq ymm10, ymm0, 16
  vpsrlq ymm11, ymm2, 16
  vpsrlq ymm12, ymm5, 16
  vpblendw ymm10, ymm10, ymm1, 0xaa
  vpblendw ymm11, ymm11, ymm4, 0xaa
  vpblendw ymm12, ymm12, ymm6, 0xaa
  vpsllq ymm0, ymm8, 32
  vpsllq ymm1, ymm10, 32
  vpsllq ymm2, ymm12, 32
  vpblendd ymm0, ymm7, ymm0, 0xaa
  vpblendd ymm1, ymm9, ymm1, 0xaa
  vpblendd ymm2, ymm11, ymm2, 0xaa
  vpsrlq ymm3, ymm7, 32
  vpsrlq ymm4, ymm9, 32
  vpsrlq ymm5, ymm11, 32
  vpblendd ymm3, ymm3, ymm8, 0xaa
  vpblendd ymm4, ymm4, ymm10, 0xaa
  vpblendd ymm5, ymm5, ymm12, 0xaa
  vpunpcklqdq ymm6, ymm0, ymm1
  vpunpcklqdq ymm7, ymm2, ymm3
  vpunpcklqdq ymm8, ymm4, ymm5
  vpunpckhqdq ymm9, ymm0, ymm1
  vpunpckhqdq ymm10, ymm2, ymm3
  vpunpckhqdq ymm11, ymm4, ymm5
  vperm2i128 ymm0, ymm6, ymm7, 0x20
  vperm2i128 ymm1, ymm8, ymm9, 0x20
  vperm2i128 ymm2, ymm10, ymm11, 0x20
  vperm2i128 ymm3, ymm6, ymm7, 0x31
  vperm2i128 ymm4, ymm8, ymm9, 0x31
  vperm2i128 ymm5, ymm10, ymm11, 0x31
  vmovdqu YMMWORD PTR [rdi + \ctoff], ymm0
  vmovdqu YMMWORD PTR [rdi + \ctoff + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + \ctoff + 64], ymm2
  vmovdqu YMMWORD PTR [rdi + \ctoff + 96], ymm3
  vmovdqu YMMWORD PTR [rdi + \ctoff + 128], ymm4
  vmovdqu YMMWORD PTR [rdi + \ctoff + 160], ymm5
.endm

.macro MA3_QM1 h0,h1,r0,r1,lambda,lambda_qinv
  vmovdqa ymm0, YMMWORD PTR [r8 + \h0]
  vmovdqa ymm1, YMMWORD PTR [r8 + \h1]
  vmovdqa ymm2, YMMWORD PTR [r8 + \r0]
  vmovdqa ymm3, YMMWORD PTR [r8 + \r1]
  MA1_MONT_REG 4,0,2,6
  MA1_MONT_REG 5,1,3,7
  vpaddw ymm0, ymm0, ymm1
  vpaddw ymm2, ymm2, ymm3
  MA1_CENTER 0,6
  MA1_CENTER 2,7
  MA1_MONT_REG 8,0,2,6
  vpsubw ymm9, ymm8, ymm4
  vpsubw ymm9, ymm9, ymm5
  MA1_CENTER 9,6
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,6
  vpaddw ymm4, ymm4, ymm8
  MA1_CENTER 4,6
  /* first in ymm4, second in ymm9 */
.endm

.macro MA3_QM2 ah0,bh0,ah1,bh1,ar0,br0,ar1,br1,alambda,alambda_qinv,blambda,blambda_qinv
  vmovdqa ymm0, YMMWORD PTR [r8 + \ah0]
  vmovdqa ymm1, YMMWORD PTR [r8 + \bh0]
  vmovdqa ymm2, YMMWORD PTR [r8 + \ah1]
  vmovdqa ymm3, YMMWORD PTR [r8 + \bh1]
  vmovdqa ymm4, YMMWORD PTR [r8 + \ar0]
  vmovdqa ymm5, YMMWORD PTR [r8 + \br0]
  vmovdqa ymm6, YMMWORD PTR [r8 + \ar1]
  vmovdqa ymm7, YMMWORD PTR [r8 + \br1]
  MA1_MONT_REG2 8,9,0,1,4,5,12,13
  MA1_MONT_REG2 10,11,2,3,6,7,12,13
  vpaddw ymm0, ymm0, ymm2
  vpaddw ymm1, ymm1, ymm3
  vpaddw ymm4, ymm4, ymm6
  vpaddw ymm5, ymm5, ymm7
  MA1_CENTER2 0,1,12,13
  MA1_CENTER2 4,5,12,13
  MA1_MONT_REG2 14,15,0,1,4,5,12,13
  vpsubw ymm14, ymm14, ymm8
  vpsubw ymm15, ymm15, ymm9
  vpsubw ymm14, ymm14, ymm10
  vpsubw ymm15, ymm15, ymm11
  MA1_CENTER2 14,15,12,13
  MA1_MONT_CONST 12,10,\alambda,\alambda_qinv,2
  MA1_MONT_CONST 13,11,\blambda,\blambda_qinv,3
  vpaddw ymm8, ymm8, ymm12
  vpaddw ymm9, ymm9, ymm13
  MA1_CENTER2 8,9,12,13
  /* first A/B in ymm8/9, second A/B in ymm14/15 */
.endm

.globl ntruplus1152_exp001_f0_ma3_asm0_b0p0
.type ntruplus1152_exp001_f0_ma3_asm0_b0p0,@function
.p2align 5
ntruplus1152_exp001_f0_ma3_asm0_b0p0:
  /* Exact B0/P0 single-tile EE -> OO -> TT streaming DAG. */
  MA1_PROJECT_H 0,8,256,384,0x31,.Lma3_mask_0,0x80
  MA1_CENTER 0,12
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,12
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  MA1_PROJECT_H 0,8,288,416,0x31,.Lma3_mask_0,0x80
  MA1_CENTER 0,12
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,12
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  MA1_PROJECT_H 0,8,320,448,0x31,.Lma3_mask_0,0x80
  MA1_CENTER 0,12
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,12
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  MA1_PROJECT_H 0,8,352,480,0x31,.Lma3_mask_0,0x80
  MA1_CENTER 0,12
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,12
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm2, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm2, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm2, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm2, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa ymm0, YMMWORD PTR [rdx + 0]
  vmovdqa ymm2, YMMWORD PTR [rdx + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa ymm0, YMMWORD PTR [rdx + 0]
  vmovdqa ymm2, YMMWORD PTR [rdx + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa ymm0, YMMWORD PTR [rdx + 64]
  vmovdqa ymm2, YMMWORD PTR [rdx + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa ymm0, YMMWORD PTR [rdx + 64]
  vmovdqa ymm2, YMMWORD PTR [rdx + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  MA3_QM1 256,320,512,576,.Llambda_b0p0,.Llambda_b0p0_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm4
  vmovdqa YMMWORD PTR [r8 + 800], ymm9
  vpaddw ymm4, ymm4, YMMWORD PTR [r8 + 0]
  vmovdqa YMMWORD PTR [r8 + 0], ymm4
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 64]
  vmovdqa YMMWORD PTR [r8 + 64], ymm9
  MA3_QM1 288,352,544,608,.Llambda_b0p0,.Llambda_b0p0_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm4
  vmovdqa YMMWORD PTR [r8 + 864], ymm9
  vpaddw ymm4, ymm4, YMMWORD PTR [r8 + 64]
  vmovdqa YMMWORD PTR [r8 + 64], ymm4
  MA1_MONT_CONST 10,9,.Llambda_b0p0,.Llambda_b0p0_qinv,12
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  MA3_QM1 1024,1056,1088,1120,.Llambda_b0p0,.Llambda_b0p0_qinv
  vpsubw ymm4, ymm4, YMMWORD PTR [r8 + 768]
  vpsubw ymm4, ymm4, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 800]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 864]
  MA1_CENTER 4,12
  MA1_CENTER 9,12
  vpaddw ymm4, ymm4, YMMWORD PTR [r8 + 32]
  vmovdqa YMMWORD PTR [r8 + 32], ymm4
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 96]
  vmovdqa YMMWORD PTR [r8 + 96], ymm9
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  MA1_MONT_CONST 0,0,.Lma1_inv4,.Lma1_inv4_qinv,12
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  MA1_MONT_CONST 0,0,.Lma1_inv4,.Lma1_inv4_qinv,12
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  MA1_MONT_CONST 0,0,.Lma1_inv4,.Lma1_inv4_qinv,12
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  MA1_MONT_CONST 0,0,.Lma1_inv4,.Lma1_inv4_qinv,12
  MA1_CENTER 0,12
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa YMMWORD PTR [rdi + 0], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa YMMWORD PTR [rdi + 32], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa YMMWORD PTR [rdi + 64], ymm0
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa YMMWORD PTR [rdi + 96], ymm0
  ret
.size ntruplus1152_exp001_f0_ma3_asm0_b0p0, .-ntruplus1152_exp001_f0_ma3_asm0_b0p0

.globl ntruplus1152_exp001_f0_ma3_asm1_c1
.type ntruplus1152_exp001_f0_ma3_asm1_c1,@function
.p2align 5
ntruplus1152_exp001_f0_ma3_asm1_c1:
  /* MA3 two-tile chunk 0. */
  MA1_PROJECT_H 0,8,0,128,0x31,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,0,128,0x20,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,32,160,0x31,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,32,160,0x20,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,64,192,0x31,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,64,192,0x20,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,96,224,0x31,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,96,224,0x20,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm2, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 640]
  vmovdqa ymm3, YMMWORD PTR [rsi + 672]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm2, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 640]
  vmovdqa ymm3, YMMWORD PTR [rsi + 672]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 576]
  vmovdqa ymm2, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 704]
  vmovdqa ymm3, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 576]
  vmovdqa ymm2, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 704]
  vmovdqa ymm3, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 512]
  vmovdqa ymm2, YMMWORD PTR [rdx + 544]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 640]
  vmovdqa ymm3, YMMWORD PTR [rdx + 672]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 512]
  vmovdqa ymm2, YMMWORD PTR [rdx + 544]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 640]
  vmovdqa ymm3, YMMWORD PTR [rdx + 672]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 576]
  vmovdqa ymm2, YMMWORD PTR [rdx + 608]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 704]
  vmovdqa ymm3, YMMWORD PTR [rdx + 736]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 576]
  vmovdqa ymm2, YMMWORD PTR [rdx + 608]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 704]
  vmovdqa ymm3, YMMWORD PTR [rdx + 736]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b0p4,.Llambda_b0p4_qinv,.Llambda_b0p7,.Llambda_b0p7_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b0p4,.Llambda_b0p4_qinv,.Llambda_b0p7,.Llambda_b0p7_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b0p4,.Llambda_b0p4_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b0p7,.Llambda_b0p7_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b0p4,.Llambda_b0p4_qinv,.Llambda_b0p7,.Llambda_b0p7_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 0: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_8]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_9]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_9]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_8]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_8]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_9]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_9]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_8]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_8]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_9]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_9]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_8]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_8]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_9]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_9]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_8]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 0
  /* MA3 two-tile chunk 1. */
  MA1_PROJECT_H 0,8,256,384,0x31,.Lma3_mask_0,0x80
  MA1_PROJECT_H 1,9,256,384,0x20,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,288,416,0x31,.Lma3_mask_0,0x80
  MA1_PROJECT_H 1,9,288,416,0x20,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,320,448,0x31,.Lma3_mask_0,0x80
  MA1_PROJECT_H 1,9,320,448,0x20,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,352,480,0x31,.Lma3_mask_0,0x80
  MA1_PROJECT_H 1,9,352,480,0x20,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm2, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 384]
  vmovdqa ymm3, YMMWORD PTR [rsi + 416]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm2, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 384]
  vmovdqa ymm3, YMMWORD PTR [rsi + 416]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm2, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 448]
  vmovdqa ymm3, YMMWORD PTR [rsi + 480]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm2, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 448]
  vmovdqa ymm3, YMMWORD PTR [rsi + 480]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 0]
  vmovdqa ymm2, YMMWORD PTR [rdx + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 384]
  vmovdqa ymm3, YMMWORD PTR [rdx + 416]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 0]
  vmovdqa ymm2, YMMWORD PTR [rdx + 32]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 384]
  vmovdqa ymm3, YMMWORD PTR [rdx + 416]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 64]
  vmovdqa ymm2, YMMWORD PTR [rdx + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 448]
  vmovdqa ymm3, YMMWORD PTR [rdx + 480]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 64]
  vmovdqa ymm2, YMMWORD PTR [rdx + 96]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 448]
  vmovdqa ymm3, YMMWORD PTR [rdx + 480]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b0p0,.Llambda_b0p0_qinv,.Llambda_b0p1,.Llambda_b0p1_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b0p0,.Llambda_b0p0_qinv,.Llambda_b0p1,.Llambda_b0p1_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b0p0,.Llambda_b0p0_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b0p1,.Llambda_b0p1_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b0p0,.Llambda_b0p0_qinv,.Llambda_b0p1,.Llambda_b0p1_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 1: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_10]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_11]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_11]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_10]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_10]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_11]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_11]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_10]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_10]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_11]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_11]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_10]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_10]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_11]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_11]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_10]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 192
  /* MA3 two-tile chunk 2. */
  MA1_PROJECT_H 0,8,512,640,0x31,.Lma3_mask_1,0xfe
  MA1_PROJECT_H 1,9,512,640,0x20,.Lma3_mask_2,0x55
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,544,672,0x31,.Lma3_mask_1,0xfe
  MA1_PROJECT_H 1,9,544,672,0x20,.Lma3_mask_2,0x55
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,576,704,0x31,.Lma3_mask_1,0xfe
  MA1_PROJECT_H 1,9,576,704,0x20,.Lma3_mask_2,0x55
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,608,736,0x31,.Lma3_mask_1,0xfe
  MA1_PROJECT_H 1,9,608,736,0x20,.Lma3_mask_2,0x55
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 128]
  vmovdqa ymm2, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 256]
  vmovdqa ymm3, YMMWORD PTR [rsi + 288]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 128]
  vmovdqa ymm2, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 256]
  vmovdqa ymm3, YMMWORD PTR [rsi + 288]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 192]
  vmovdqa ymm2, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 320]
  vmovdqa ymm3, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 192]
  vmovdqa ymm2, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 320]
  vmovdqa ymm3, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 128]
  vmovdqa ymm2, YMMWORD PTR [rdx + 160]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 256]
  vmovdqa ymm3, YMMWORD PTR [rdx + 288]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 128]
  vmovdqa ymm2, YMMWORD PTR [rdx + 160]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 256]
  vmovdqa ymm3, YMMWORD PTR [rdx + 288]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 192]
  vmovdqa ymm2, YMMWORD PTR [rdx + 224]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 320]
  vmovdqa ymm3, YMMWORD PTR [rdx + 352]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 192]
  vmovdqa ymm2, YMMWORD PTR [rdx + 224]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 320]
  vmovdqa ymm3, YMMWORD PTR [rdx + 352]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b0p3,.Llambda_b0p3_qinv,.Llambda_b0p6,.Llambda_b0p6_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b0p3,.Llambda_b0p3_qinv,.Llambda_b0p6,.Llambda_b0p6_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b0p3,.Llambda_b0p3_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b0p6,.Llambda_b0p6_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b0p3,.Llambda_b0p3_qinv,.Llambda_b0p6,.Llambda_b0p6_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 2: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_12]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_13]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_13]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_12]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_12]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_13]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_13]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_12]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_12]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_13]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_13]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_12]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_12]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_13]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_13]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_12]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 384
  /* MA3 two-tile chunk 3. */
  MA1_PROJECT_H 0,8,768,896,0x20,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,768,896,0x31,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,800,928,0x20,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,800,928,0x31,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,832,960,0x20,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,832,960,0x31,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,864,992,0x20,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,864,992,0x31,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm2, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 768]
  vmovdqa ymm3, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm2, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 768]
  vmovdqa ymm3, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm2, YMMWORD PTR [rsi + 992]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 832]
  vmovdqa ymm3, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm2, YMMWORD PTR [rsi + 992]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 832]
  vmovdqa ymm3, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 896]
  vmovdqa ymm2, YMMWORD PTR [rdx + 928]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 768]
  vmovdqa ymm3, YMMWORD PTR [rdx + 800]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 896]
  vmovdqa ymm2, YMMWORD PTR [rdx + 928]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 768]
  vmovdqa ymm3, YMMWORD PTR [rdx + 800]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 960]
  vmovdqa ymm2, YMMWORD PTR [rdx + 992]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 832]
  vmovdqa ymm3, YMMWORD PTR [rdx + 864]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 960]
  vmovdqa ymm2, YMMWORD PTR [rdx + 992]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 832]
  vmovdqa ymm3, YMMWORD PTR [rdx + 864]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b0p2,.Llambda_b0p2_qinv,.Llambda_b0p8,.Llambda_b0p8_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b0p2,.Llambda_b0p2_qinv,.Llambda_b0p8,.Llambda_b0p8_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b0p2,.Llambda_b0p2_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b0p8,.Llambda_b0p8_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b0p2,.Llambda_b0p2_qinv,.Llambda_b0p8,.Llambda_b0p8_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 3: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_14]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_15]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_15]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_14]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_14]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_15]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_15]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_14]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_14]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_15]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_15]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_14]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_14]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_15]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_15]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_14]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 576
  /* MA3 two-tile chunk 4. */
  MA1_PROJECT_H 0,8,1024,1152,0x20,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,1024,1152,0x31,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,1056,1184,0x20,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,1056,1184,0x31,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,1088,1216,0x20,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,1088,1216,0x31,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,1120,1248,0x20,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,1120,1248,0x31,.Lma3_mask_5,0xff
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1056]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1056]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1120]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1120]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1024]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1056]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1280]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1312]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1024]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1056]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1280]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1312]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1088]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1120]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1344]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1376]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1088]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1120]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1344]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1376]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b0p5,.Llambda_b0p5_qinv,.Llambda_b1p3,.Llambda_b1p3_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b0p5,.Llambda_b0p5_qinv,.Llambda_b1p3,.Llambda_b1p3_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b0p5,.Llambda_b0p5_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b1p3,.Llambda_b1p3_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b0p5,.Llambda_b0p5_qinv,.Llambda_b1p3,.Llambda_b1p3_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 4: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_16]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_17]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_17]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_16]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_16]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_17]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_17]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_16]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_16]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_17]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_17]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_16]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_16]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_17]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_17]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_16]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 768
  /* MA3 two-tile chunk 5. */
  MA1_PROJECT_H 0,8,1280,1408,0x20,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,1280,1408,0x31,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,1312,1440,0x20,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,1312,1440,0x31,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,1344,1472,0x20,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,1344,1472,0x31,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,1376,1504,0x20,.Lma3_mask_4,0xa8
  MA1_PROJECT_H 1,9,1376,1504,0x31,.Lma3_mask_3,0x11
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1184]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1184]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1248]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1248]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1152]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1184]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1408]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1440]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1152]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1184]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1408]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1440]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1216]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1248]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1472]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1504]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1216]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1248]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1472]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1504]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b1p0,.Llambda_b1p0_qinv,.Llambda_b1p6,.Llambda_b1p6_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b1p0,.Llambda_b1p0_qinv,.Llambda_b1p6,.Llambda_b1p6_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b1p0,.Llambda_b1p0_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b1p6,.Llambda_b1p6_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b1p0,.Llambda_b1p0_qinv,.Llambda_b1p6,.Llambda_b1p6_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 5: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_18]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_19]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_19]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_18]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_18]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_19]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_19]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_18]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_18]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_19]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_19]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_18]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_18]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_19]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_19]
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_18]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 960
  /* MA3 two-tile chunk 6. */
  MA1_PROJECT_H 0,8,1536,1664,0x31,.Lma3_mask_2,0x55
  MA1_PROJECT_H 1,9,1536,1664,0x20,.Lma3_mask_0,0x80
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,1568,1696,0x31,.Lma3_mask_2,0x55
  MA1_PROJECT_H 1,9,1568,1696,0x20,.Lma3_mask_0,0x80
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,1600,1728,0x31,.Lma3_mask_2,0x55
  MA1_PROJECT_H 1,9,1600,1728,0x20,.Lma3_mask_0,0x80
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,1632,1760,0x31,.Lma3_mask_2,0x55
  MA1_PROJECT_H 1,9,1632,1760,0x20,.Lma3_mask_0,0x80
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm2, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2208]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm2, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2208]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm2, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2272]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm2, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2272]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 2048]
  vmovdqa ymm2, YMMWORD PTR [rdx + 2080]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 2176]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2208]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 2048]
  vmovdqa ymm2, YMMWORD PTR [rdx + 2080]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 2176]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2208]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 2112]
  vmovdqa ymm2, YMMWORD PTR [rdx + 2144]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 2240]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2272]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 2112]
  vmovdqa ymm2, YMMWORD PTR [rdx + 2144]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 2240]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2272]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b1p2,.Llambda_b1p2_qinv,.Llambda_b1p5,.Llambda_b1p5_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b1p2,.Llambda_b1p2_qinv,.Llambda_b1p5,.Llambda_b1p5_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b1p2,.Llambda_b1p2_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b1p5,.Llambda_b1p5_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b1p2,.Llambda_b1p2_qinv,.Llambda_b1p5,.Llambda_b1p5_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 6: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_20]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_21]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_21]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_20]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_20]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_21]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_21]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_20]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_20]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_21]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_21]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_20]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_20]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_21]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_21]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_20]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 1152
  /* MA3 two-tile chunk 7. */
  MA1_PROJECT_H 0,8,1792,1920,0x31,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,1792,1920,0x20,.Lma3_mask_1,0xfe
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,1824,1952,0x31,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,1824,1952,0x20,.Lma3_mask_1,0xfe
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,1856,1984,0x31,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,1856,1984,0x20,.Lma3_mask_1,0xfe
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,1888,2016,0x31,.Lma3_mask_7,0x77
  MA1_PROJECT_H 1,9,1888,2016,0x20,.Lma3_mask_1,0xfe
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1952]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1952]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2016]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2016]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1792]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1824]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1920]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1952]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1792]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1824]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1920]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1952]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1856]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1888]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1984]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2016]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1856]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1888]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1984]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2016]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b1p7,.Llambda_b1p7_qinv,.Llambda_b1p8,.Llambda_b1p8_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b1p7,.Llambda_b1p7_qinv,.Llambda_b1p8,.Llambda_b1p8_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b1p7,.Llambda_b1p7_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b1p8,.Llambda_b1p8_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b1p7,.Llambda_b1p7_qinv,.Llambda_b1p8,.Llambda_b1p8_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 7: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_22]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_23]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_23]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_22]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_22]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_23]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_23]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_22]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_22]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_23]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_23]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_22]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_22]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_23]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_23]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_22]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 1344
  /* MA3 two-tile chunk 8. */
  MA1_PROJECT_H 0,8,2048,2176,0x31,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,2048,2176,0x20,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 256], ymm0
  vmovdqa YMMWORD PTR [r8 + 384], ymm1
  MA1_PROJECT_H 0,8,2080,2208,0x31,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,2080,2208,0x20,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 288], ymm0
  vmovdqa YMMWORD PTR [r8 + 416], ymm1
  MA1_PROJECT_H 0,8,2112,2240,0x31,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,2112,2240,0x20,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 320], ymm0
  vmovdqa YMMWORD PTR [r8 + 448], ymm1
  MA1_PROJECT_H 0,8,2144,2272,0x31,.Lma3_mask_5,0x00
  MA1_PROJECT_H 1,9,2144,2272,0x20,.Lma3_mask_6,0xea
  MA1_CENTER2 0,1,12,13
  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 352], ymm0
  vmovdqa YMMWORD PTR [r8 + 480], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 512], ymm0
  vmovdqa YMMWORD PTR [r8 + 640], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 544], ymm0
  vmovdqa YMMWORD PTR [r8 + 672], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1760]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 576], ymm0
  vmovdqa YMMWORD PTR [r8 + 704], ymm1
  vmovdqa ymm0, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1760]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 608], ymm0
  vmovdqa YMMWORD PTR [r8 + 736], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1536]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1568]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1664]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1696]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1536]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1568]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1664]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1696]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1600]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1632]
  vperm2i128 ymm0, ymm0, ymm2, 0x20
  vmovdqa ymm1, YMMWORD PTR [rdx + 1728]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1760]
  vperm2i128 ymm1, ymm1, ymm3, 0x20
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [rdx + 1600]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1632]
  vperm2i128 ymm0, ymm0, ymm2, 0x31
  vmovdqa ymm1, YMMWORD PTR [rdx + 1728]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1760]
  vperm2i128 ymm1, ymm1, ymm3, 0x31
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 288]
  vmovdqa ymm1, YMMWORD PTR [r8 + 384]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 416]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1024], ymm0
  vmovdqa YMMWORD PTR [r8 + 1152], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 320]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 352]
  vmovdqa ymm1, YMMWORD PTR [r8 + 448]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 480]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1056], ymm0
  vmovdqa YMMWORD PTR [r8 + 1184], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 544]
  vmovdqa ymm1, YMMWORD PTR [r8 + 640]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 672]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1088], ymm0
  vmovdqa YMMWORD PTR [r8 + 1216], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 576]
  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + 608]
  vmovdqa ymm1, YMMWORD PTR [r8 + 704]
  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + 736]
  MA1_CENTER2 0,1,12,13
  vmovdqa YMMWORD PTR [r8 + 1120], ymm0
  vmovdqa YMMWORD PTR [r8 + 1248], ymm1
  MA3_QM2 256,384,320,448,512,640,576,704,.Llambda_b1p1,.Llambda_b1p1_qinv,.Llambda_b1p4,.Llambda_b1p4_qinv
  vmovdqa YMMWORD PTR [r8 + 768], ymm8
  vmovdqa YMMWORD PTR [r8 + 896], ymm9
  vmovdqa YMMWORD PTR [r8 + 800], ymm14
  vmovdqa YMMWORD PTR [r8 + 928], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 0]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm8
  vmovdqa YMMWORD PTR [r8 + 128], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 64]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm14
  vmovdqa YMMWORD PTR [r8 + 192], ymm15
  MA3_QM2 288,416,352,480,544,672,608,736,.Llambda_b1p1,.Llambda_b1p1_qinv,.Llambda_b1p4,.Llambda_b1p4_qinv
  vmovdqa YMMWORD PTR [r8 + 832], ymm8
  vmovdqa YMMWORD PTR [r8 + 960], ymm9
  vmovdqa YMMWORD PTR [r8 + 864], ymm14
  vmovdqa YMMWORD PTR [r8 + 992], ymm15
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 64]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 192]
  vmovdqa YMMWORD PTR [r8 + 64], ymm8
  vmovdqa YMMWORD PTR [r8 + 192], ymm9
  MA1_MONT_CONST 10,14,.Llambda_b1p1,.Llambda_b1p1_qinv,12
  MA1_MONT_CONST 11,15,.Llambda_b1p4,.Llambda_b1p4_qinv,13
  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]
  vpaddw ymm11, ymm11, YMMWORD PTR [r8 + 128]
  vmovdqa YMMWORD PTR [r8 + 0], ymm10
  vmovdqa YMMWORD PTR [r8 + 128], ymm11
  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,.Llambda_b1p1,.Llambda_b1p1_qinv,.Llambda_b1p4,.Llambda_b1p4_qinv
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]
  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]
  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]
  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]
  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]
  MA1_CENTER2 8,9,12,13
  MA1_CENTER2 14,15,12,13
  vpaddw ymm8, ymm8, YMMWORD PTR [r8 + 32]
  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 160]
  vmovdqa YMMWORD PTR [r8 + 32], ymm8
  vmovdqa YMMWORD PTR [r8 + 160], ymm9
  vpaddw ymm14, ymm14, YMMWORD PTR [r8 + 96]
  vpaddw ymm15, ymm15, YMMWORD PTR [r8 + 224]
  vmovdqa YMMWORD PTR [r8 + 96], ymm14
  vmovdqa YMMWORD PTR [r8 + 224], ymm15
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 0], ymm0
  vmovdqa YMMWORD PTR [r8 + 128], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 32], ymm0
  vmovdqa YMMWORD PTR [r8 + 160], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 64], ymm0
  vmovdqa YMMWORD PTR [r8 + 192], ymm1
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13
  vmovdqa YMMWORD PTR [r8 + 96], ymm0
  vmovdqa YMMWORD PTR [r8 + 224], ymm1
  /* Chunk 8: semantic planes to eight Official vectors. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_24]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_25]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 256], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_25]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_24]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 384], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 32]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_24]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_25]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 288], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_25]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_24]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 416], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 64]
  vmovdqa ymm1, YMMWORD PTR [r8 + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_24]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_25]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 320], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_25]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_24]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 448], ymm2
  vmovdqa ymm0, YMMWORD PTR [r8 + 96]
  vmovdqa ymm1, YMMWORD PTR [r8 + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_24]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_25]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 352], ymm2
  vperm2i128 ymm2, ymm0, ymm1, 0x02
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma3_mask_25]
  vperm2i128 ymm3, ymm0, ymm1, 0x13
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lma3_mask_24]
  vpor ymm2, ymm2, ymm3
  vmovdqa YMMWORD PTR [r8 + 480], ymm2
  MA1_PACK_CHUNK 1536
  ret
.size ntruplus1152_exp001_f0_ma3_asm1_c1, .-ntruplus1152_exp001_f0_ma3_asm1_c1

.section .rodata
#include "f0-ma3-constants.inc"

.section .note.GNU-stack,"",@progbits
