/* Generated cumulative Natural-Q MA2 scale-4 boundary. */
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

.globl ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4
.type ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4,@function
.p2align 5
ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4:
  /* Natural-Q lane-wise MA2 tile b0p0. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 256]
  vmovdqa ymm9, YMMWORD PTR [rcx + 384]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 288]
  vmovdqa ymm9, YMMWORD PTR [rcx + 416]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 320]
  vmovdqa ymm9, YMMWORD PTR [rcx + 448]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 352]
  vmovdqa ymm9, YMMWORD PTR [rcx + 480]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 0]
  vmovdqa ymm5, YMMWORD PTR [rsi + 32]
  vmovdqa ymm6, YMMWORD PTR [rsi + 64]
  vmovdqa ymm7, YMMWORD PTR [rsi + 96]
  vmovdqa ymm8, YMMWORD PTR [rdx + 0]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p0,.Lqnat_lambda_b0p0_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 0], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 32]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p0,.Lqnat_lambda_b0p0_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 32], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 64]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p0,.Lqnat_lambda_b0p0_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 64], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 96]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 96], ymm8
  /* Natural-Q lane-wise MA2 tile b0p3. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 512]
  vmovdqa ymm9, YMMWORD PTR [rcx + 640]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 544]
  vmovdqa ymm9, YMMWORD PTR [rcx + 672]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 576]
  vmovdqa ymm9, YMMWORD PTR [rcx + 704]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 608]
  vmovdqa ymm9, YMMWORD PTR [rcx + 736]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 128]
  vmovdqa ymm5, YMMWORD PTR [rsi + 160]
  vmovdqa ymm6, YMMWORD PTR [rsi + 192]
  vmovdqa ymm7, YMMWORD PTR [rsi + 224]
  vmovdqa ymm8, YMMWORD PTR [rdx + 128]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p3,.Lqnat_lambda_b0p3_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 128], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 160]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p3,.Lqnat_lambda_b0p3_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 160], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 192]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p3,.Lqnat_lambda_b0p3_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 192], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 224]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 224], ymm8
  /* Natural-Q lane-wise MA2 tile b0p6. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 512]
  vmovdqa ymm9, YMMWORD PTR [rcx + 640]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 544]
  vmovdqa ymm9, YMMWORD PTR [rcx + 672]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 576]
  vmovdqa ymm9, YMMWORD PTR [rcx + 704]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 608]
  vmovdqa ymm9, YMMWORD PTR [rcx + 736]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 256]
  vmovdqa ymm5, YMMWORD PTR [rsi + 288]
  vmovdqa ymm6, YMMWORD PTR [rsi + 320]
  vmovdqa ymm7, YMMWORD PTR [rsi + 352]
  vmovdqa ymm8, YMMWORD PTR [rdx + 256]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p6,.Lqnat_lambda_b0p6_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 256], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 288]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p6,.Lqnat_lambda_b0p6_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 288], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 320]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p6,.Lqnat_lambda_b0p6_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 320], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 352]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 352], ymm8
  /* Natural-Q lane-wise MA2 tile b0p1. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 256]
  vmovdqa ymm9, YMMWORD PTR [rcx + 384]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 288]
  vmovdqa ymm9, YMMWORD PTR [rcx + 416]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 320]
  vmovdqa ymm9, YMMWORD PTR [rcx + 448]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 352]
  vmovdqa ymm9, YMMWORD PTR [rcx + 480]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 384]
  vmovdqa ymm5, YMMWORD PTR [rsi + 416]
  vmovdqa ymm6, YMMWORD PTR [rsi + 448]
  vmovdqa ymm7, YMMWORD PTR [rsi + 480]
  vmovdqa ymm8, YMMWORD PTR [rdx + 384]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p1,.Lqnat_lambda_b0p1_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 384], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 416]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p1,.Lqnat_lambda_b0p1_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 416], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 448]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p1,.Lqnat_lambda_b0p1_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 448], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 480]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 480], ymm8
  /* Natural-Q lane-wise MA2 tile b0p4. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 0]
  vmovdqa ymm9, YMMWORD PTR [rcx + 128]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 32]
  vmovdqa ymm9, YMMWORD PTR [rcx + 160]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 64]
  vmovdqa ymm9, YMMWORD PTR [rcx + 192]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 96]
  vmovdqa ymm9, YMMWORD PTR [rcx + 224]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 512]
  vmovdqa ymm5, YMMWORD PTR [rsi + 544]
  vmovdqa ymm6, YMMWORD PTR [rsi + 576]
  vmovdqa ymm7, YMMWORD PTR [rsi + 608]
  vmovdqa ymm8, YMMWORD PTR [rdx + 512]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p4,.Lqnat_lambda_b0p4_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 512], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 544]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p4,.Lqnat_lambda_b0p4_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 544], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 576]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p4,.Lqnat_lambda_b0p4_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 576], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 608]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 608], ymm8
  /* Natural-Q lane-wise MA2 tile b0p7. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 0]
  vmovdqa ymm9, YMMWORD PTR [rcx + 128]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 32]
  vmovdqa ymm9, YMMWORD PTR [rcx + 160]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 64]
  vmovdqa ymm9, YMMWORD PTR [rcx + 192]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 96]
  vmovdqa ymm9, YMMWORD PTR [rcx + 224]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 640]
  vmovdqa ymm5, YMMWORD PTR [rsi + 672]
  vmovdqa ymm6, YMMWORD PTR [rsi + 704]
  vmovdqa ymm7, YMMWORD PTR [rsi + 736]
  vmovdqa ymm8, YMMWORD PTR [rdx + 640]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p7,.Lqnat_lambda_b0p7_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 640], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 672]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p7,.Lqnat_lambda_b0p7_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 672], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 704]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p7,.Lqnat_lambda_b0p7_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 704], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 736]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 736], ymm8
  /* Natural-Q lane-wise MA2 tile b0p8. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 768]
  vmovdqa ymm9, YMMWORD PTR [rcx + 896]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 800]
  vmovdqa ymm9, YMMWORD PTR [rcx + 928]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 832]
  vmovdqa ymm9, YMMWORD PTR [rcx + 960]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 864]
  vmovdqa ymm9, YMMWORD PTR [rcx + 992]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 768]
  vmovdqa ymm5, YMMWORD PTR [rsi + 800]
  vmovdqa ymm6, YMMWORD PTR [rsi + 832]
  vmovdqa ymm7, YMMWORD PTR [rsi + 864]
  vmovdqa ymm8, YMMWORD PTR [rdx + 768]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p8,.Lqnat_lambda_b0p8_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 768], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 800]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p8,.Lqnat_lambda_b0p8_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 800], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 832]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p8,.Lqnat_lambda_b0p8_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 832], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 864]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 864], ymm8
  /* Natural-Q lane-wise MA2 tile b0p2. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 768]
  vmovdqa ymm9, YMMWORD PTR [rcx + 896]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 800]
  vmovdqa ymm9, YMMWORD PTR [rcx + 928]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 832]
  vmovdqa ymm9, YMMWORD PTR [rcx + 960]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 864]
  vmovdqa ymm9, YMMWORD PTR [rcx + 992]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 896]
  vmovdqa ymm5, YMMWORD PTR [rsi + 928]
  vmovdqa ymm6, YMMWORD PTR [rsi + 960]
  vmovdqa ymm7, YMMWORD PTR [rsi + 992]
  vmovdqa ymm8, YMMWORD PTR [rdx + 896]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p2,.Lqnat_lambda_b0p2_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 896], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 928]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p2,.Lqnat_lambda_b0p2_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 928], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 960]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p2,.Lqnat_lambda_b0p2_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 960], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 992]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 992], ymm8
  /* Natural-Q lane-wise MA2 tile b0p5. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1024]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1152]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1056]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1184]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1088]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1216]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1120]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1248]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1056]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1120]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1024]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p5,.Lqnat_lambda_b0p5_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1024], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1056]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p5,.Lqnat_lambda_b0p5_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1056], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1088]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b0p5,.Lqnat_lambda_b0p5_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1088], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1120]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1120], ymm8
  /* Natural-Q lane-wise MA2 tile b1p0. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1280]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1408]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1312]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1440]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1344]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1472]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1376]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1504]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_8]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_9]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1184]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1248]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1152]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p0,.Lqnat_lambda_b1p0_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1152], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1184]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p0,.Lqnat_lambda_b1p0_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1184], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1216]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p0,.Lqnat_lambda_b1p0_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1216], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1248]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1248], ymm8
  /* Natural-Q lane-wise MA2 tile b1p3. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1024]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1152]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1056]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1184]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1088]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1216]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1120]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1248]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1312]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1376]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1280]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p3,.Lqnat_lambda_b1p3_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1280], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1312]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p3,.Lqnat_lambda_b1p3_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1312], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1344]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p3,.Lqnat_lambda_b1p3_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1344], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1376]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1376], ymm8
  /* Natural-Q lane-wise MA2 tile b1p6. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1280]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1408]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1312]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1440]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1344]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1472]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1376]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1504]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_6]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_7]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1440]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1504]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1408]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p6,.Lqnat_lambda_b1p6_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1408], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1440]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p6,.Lqnat_lambda_b1p6_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1440], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1472]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p6,.Lqnat_lambda_b1p6_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1472], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1504]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1504], ymm8
  /* Natural-Q lane-wise MA2 tile b1p1. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 2048]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2176]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 2080]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2208]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 2112]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2240]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 2144]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2272]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_11]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_10]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1568]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1632]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1536]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p1,.Lqnat_lambda_b1p1_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1536], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1568]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p1,.Lqnat_lambda_b1p1_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1568], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1600]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p1,.Lqnat_lambda_b1p1_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1600], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1632]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1632], ymm8
  /* Natural-Q lane-wise MA2 tile b1p4. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 2048]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2176]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 2080]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2208]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 2112]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2240]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 2144]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2272]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_12]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_13]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1696]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1760]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1664]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p4,.Lqnat_lambda_b1p4_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1664], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1696]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p4,.Lqnat_lambda_b1p4_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1696], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1728]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p4,.Lqnat_lambda_b1p4_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1728], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1760]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1760], ymm8
  /* Natural-Q lane-wise MA2 tile b1p7. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1792]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1920]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1824]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1952]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1856]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1984]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1888]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2016]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_14]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_15]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1824]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm7, YMMWORD PTR [rsi + 1888]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1792]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p7,.Lqnat_lambda_b1p7_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1792], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1824]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p7,.Lqnat_lambda_b1p7_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1824], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1856]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p7,.Lqnat_lambda_b1p7_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1856], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1888]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1888], ymm8
  /* Natural-Q lane-wise MA2 tile b1p8. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1792]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1920]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1824]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1952]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1856]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1984]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1888]
  vmovdqa ymm9, YMMWORD PTR [rcx + 2016]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_2]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_3]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm5, YMMWORD PTR [rsi + 1952]
  vmovdqa ymm6, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm7, YMMWORD PTR [rsi + 2016]
  vmovdqa ymm8, YMMWORD PTR [rdx + 1920]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p8,.Lqnat_lambda_b1p8_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1920], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1952]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p8,.Lqnat_lambda_b1p8_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1952], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 1984]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p8,.Lqnat_lambda_b1p8_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 1984], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2016]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2016], ymm8
  /* Natural-Q lane-wise MA2 tile b1p2. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1536]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1664]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1568]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1696]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1600]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1728]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1632]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1760]
  vperm2i128 ymm10, ymm8, ymm8, 0x31
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_4]
  vperm2i128 ymm10, ymm9, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_5]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm5, YMMWORD PTR [rsi + 2080]
  vmovdqa ymm6, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm7, YMMWORD PTR [rsi + 2144]
  vmovdqa ymm8, YMMWORD PTR [rdx + 2048]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p2,.Lqnat_lambda_b1p2_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2048], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2080]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p2,.Lqnat_lambda_b1p2_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2080], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2112]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p2,.Lqnat_lambda_b1p2_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2112], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2144]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2144], ymm8
  /* Natural-Q lane-wise MA2 tile b1p5. */
  vmovdqa ymm8, YMMWORD PTR [rcx + 1536]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1664]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm0, ymm0, ymm10
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1568]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1696]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm1, ymm1, ymm10
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1600]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1728]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm2, ymm2, ymm10
  MA1_MONT_CONST 2,2,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm8, YMMWORD PTR [rcx + 1632]
  vmovdqa ymm9, YMMWORD PTR [rcx + 1760]
  vperm2i128 ymm10, ymm8, ymm8, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_0]
  vperm2i128 ymm10, ymm9, ymm9, 0x20
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lqnat_h_mask_1]
  vpor ymm3, ymm3, ymm10
  MA1_MONT_CONST 3,3,.Lma1_r2,.Lma1_r2_qinv,11
  vmovdqa ymm4, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm5, YMMWORD PTR [rsi + 2208]
  vmovdqa ymm6, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm7, YMMWORD PTR [rsi + 2272]
  vmovdqa ymm8, YMMWORD PTR [rdx + 2176]
  MA1_MONT_REG 10,0,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,2,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_REG 10,3,5,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p5,.Lqnat_lambda_b1p5_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2176], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2208]
  MA1_MONT_REG 10,0,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_REG 10,3,6,11
  vpaddw ymm9, ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p5,.Lqnat_lambda_b1p5_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2208], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2240]
  MA1_MONT_REG 10,0,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,4,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,7,11
  vmovdqa ymm9, ymm10
  MA1_MONT_CONST 10,9,.Lqnat_lambda_b1p5,.Lqnat_lambda_b1p5_qinv,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2240], ymm8
  vmovdqa ymm8, YMMWORD PTR [rdx + 2272]
  MA1_MONT_REG 10,0,7,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,1,6,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,2,5,11
  vpaddw ymm8, ymm8, ymm10
  MA1_MONT_REG 10,3,4,11
  vpaddw ymm8, ymm8, ymm10
  vmovdqa YMMWORD PTR [rdi + 2272], ymm8
  ret
.size ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4, .-ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4

.section .rodata,"a",@progbits
#include "f0-ma2-constants.inc"
#include "gt9x16-prod3-ma2-qorder-natural-constants.inc"

.section .note.GNU-stack,"",@progbits
