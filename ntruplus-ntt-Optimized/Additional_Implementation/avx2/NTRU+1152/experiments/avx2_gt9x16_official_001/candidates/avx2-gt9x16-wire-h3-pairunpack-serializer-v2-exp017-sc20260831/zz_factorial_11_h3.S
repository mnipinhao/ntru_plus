/* Generated H3-full: PK bytes flow directly into Natural-Q MA2. */
.intel_syntax noprefix
.text
.macro H3_MONT_CONST dst,a,factor,factor_qinv,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + \factor_qinv]
  vpmulhw ymm\dst, ymm\a, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

.macro H3_MONT_REG dst,a,b,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\tmp, ymm\tmp, ymm\b
  vpmulhw ymm\dst, ymm\a, ymm\b
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

/* Zero-instruction attachment point for a future terminal consumer. */
.macro H3_TERMINAL_C tile,coefficient,reg
.endm

.globl ntruplus1152_exp001_encap_h_ingress_ma2_h3
.type ntruplus1152_exp001_encap_h_ingress_ma2_h3,@function
.p2align 5
ntruplus1152_exp001_encap_h_ingress_ma2_h3:
  xor eax, eax
  /* H3 block 0: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 0]
  vmovdqu ymm1, YMMWORD PTR [rsi + 32]
  vmovdqu ymm2, YMMWORD PTR [rsi + 64]
  vmovdqu ymm3, YMMWORD PTR [rsi + 96]
  vmovdqu ymm4, YMMWORD PTR [rsi + 128]
  vmovdqu ymm5, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm7, ymm7, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm11, ymm7, ymm7, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm8, ymm8, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm12, ymm8, ymm8, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm9, ymm9, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm13, ymm9, ymm9, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm10, ymm10, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm14, ymm10, ymm10, 0x20
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b0p4: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 512]
  vmovdqa ymm1, YMMWORD PTR [rdx + 544]
  vmovdqa ymm2, YMMWORD PTR [rdx + 576]
  vmovdqa ymm3, YMMWORD PTR [rdx + 608]
  vmovdqa ymm4, YMMWORD PTR [rcx + 512]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p4,.Lqnat_lambda_b0p4_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p4,0,4
  vmovdqa YMMWORD PTR [rdi + 512], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 544]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p4,.Lqnat_lambda_b0p4_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p4,1,4
  vmovdqa YMMWORD PTR [rdi + 544], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 576]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p4,.Lqnat_lambda_b0p4_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p4,2,4
  vmovdqa YMMWORD PTR [rdi + 576], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 608]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p4,3,4
  vmovdqa YMMWORD PTR [rdi + 608], ymm4
  /* Tile B b0p7: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 640]
  vmovdqa ymm1, YMMWORD PTR [rdx + 672]
  vmovdqa ymm2, YMMWORD PTR [rdx + 704]
  vmovdqa ymm3, YMMWORD PTR [rdx + 736]
  vmovdqa ymm4, YMMWORD PTR [rcx + 640]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p7,.Lqnat_lambda_b0p7_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p7,0,4
  vmovdqa YMMWORD PTR [rdi + 640], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 672]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p7,.Lqnat_lambda_b0p7_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p7,1,4
  vmovdqa YMMWORD PTR [rdi + 672], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 704]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p7,.Lqnat_lambda_b0p7_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p7,2,4
  vmovdqa YMMWORD PTR [rdi + 704], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 736]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p7,3,4
  vmovdqa YMMWORD PTR [rdi + 736], ymm4
  /* H3 block 1: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 192]
  vmovdqu ymm1, YMMWORD PTR [rsi + 224]
  vmovdqu ymm2, YMMWORD PTR [rsi + 256]
  vmovdqu ymm3, YMMWORD PTR [rsi + 288]
  vmovdqu ymm4, YMMWORD PTR [rsi + 320]
  vmovdqu ymm5, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm15, ymm7, ymm7, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm11, ymm7, ymm7, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm15, ymm8, ymm8, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm12, ymm8, ymm8, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm15, ymm9, ymm9, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm13, ymm9, ymm9, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm15, ymm10, ymm10, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm14, ymm10, ymm10, 0x20
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b0p0: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 0]
  vmovdqa ymm1, YMMWORD PTR [rdx + 32]
  vmovdqa ymm2, YMMWORD PTR [rdx + 64]
  vmovdqa ymm3, YMMWORD PTR [rdx + 96]
  vmovdqa ymm4, YMMWORD PTR [rcx + 0]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p0,.Lqnat_lambda_b0p0_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p0,0,4
  vmovdqa YMMWORD PTR [rdi + 0], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 32]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p0,.Lqnat_lambda_b0p0_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p0,1,4
  vmovdqa YMMWORD PTR [rdi + 32], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 64]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p0,.Lqnat_lambda_b0p0_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p0,2,4
  vmovdqa YMMWORD PTR [rdi + 64], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 96]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p0,3,4
  vmovdqa YMMWORD PTR [rdi + 96], ymm4
  /* Tile B b0p1: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 384]
  vmovdqa ymm1, YMMWORD PTR [rdx + 416]
  vmovdqa ymm2, YMMWORD PTR [rdx + 448]
  vmovdqa ymm3, YMMWORD PTR [rdx + 480]
  vmovdqa ymm4, YMMWORD PTR [rcx + 384]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p1,.Lqnat_lambda_b0p1_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p1,0,4
  vmovdqa YMMWORD PTR [rdi + 384], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 416]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p1,.Lqnat_lambda_b0p1_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p1,1,4
  vmovdqa YMMWORD PTR [rdi + 416], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 448]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p1,.Lqnat_lambda_b0p1_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p1,2,4
  vmovdqa YMMWORD PTR [rdi + 448], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 480]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p1,3,4
  vmovdqa YMMWORD PTR [rdi + 480], ymm4
  /* H3 block 2: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 384]
  vmovdqu ymm1, YMMWORD PTR [rsi + 416]
  vmovdqu ymm2, YMMWORD PTR [rsi + 448]
  vmovdqu ymm3, YMMWORD PTR [rsi + 480]
  vmovdqu ymm4, YMMWORD PTR [rsi + 512]
  vmovdqu ymm5, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm15, ymm7, ymm7, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm11, ymm7, ymm7, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm15, ymm8, ymm8, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm12, ymm8, ymm8, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm15, ymm9, ymm9, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm13, ymm9, ymm9, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm15, ymm10, ymm10, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm14, ymm10, ymm10, 0x20
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b0p3: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 128]
  vmovdqa ymm1, YMMWORD PTR [rdx + 160]
  vmovdqa ymm2, YMMWORD PTR [rdx + 192]
  vmovdqa ymm3, YMMWORD PTR [rdx + 224]
  vmovdqa ymm4, YMMWORD PTR [rcx + 128]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p3,.Lqnat_lambda_b0p3_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p3,0,4
  vmovdqa YMMWORD PTR [rdi + 128], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 160]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p3,.Lqnat_lambda_b0p3_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p3,1,4
  vmovdqa YMMWORD PTR [rdi + 160], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 192]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p3,.Lqnat_lambda_b0p3_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p3,2,4
  vmovdqa YMMWORD PTR [rdi + 192], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 224]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p3,3,4
  vmovdqa YMMWORD PTR [rdi + 224], ymm4
  /* Tile B b0p6: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 256]
  vmovdqa ymm1, YMMWORD PTR [rdx + 288]
  vmovdqa ymm2, YMMWORD PTR [rdx + 320]
  vmovdqa ymm3, YMMWORD PTR [rdx + 352]
  vmovdqa ymm4, YMMWORD PTR [rcx + 256]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p6,.Lqnat_lambda_b0p6_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p6,0,4
  vmovdqa YMMWORD PTR [rdi + 256], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 288]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p6,.Lqnat_lambda_b0p6_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p6,1,4
  vmovdqa YMMWORD PTR [rdi + 288], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 320]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p6,.Lqnat_lambda_b0p6_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p6,2,4
  vmovdqa YMMWORD PTR [rdi + 320], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 352]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p6,3,4
  vmovdqa YMMWORD PTR [rdi + 352], ymm4
  /* H3 block 3: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 576]
  vmovdqu ymm1, YMMWORD PTR [rsi + 608]
  vmovdqu ymm2, YMMWORD PTR [rsi + 640]
  vmovdqu ymm3, YMMWORD PTR [rsi + 672]
  vmovdqu ymm4, YMMWORD PTR [rsi + 704]
  vmovdqu ymm5, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x20
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm7, ymm7, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm11, ymm7, ymm7, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm8, ymm8, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm12, ymm8, ymm8, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm9, ymm9, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm13, ymm9, ymm9, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm10, ymm10, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm14, ymm10, ymm10, 0x31
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b0p2: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 896]
  vmovdqa ymm1, YMMWORD PTR [rdx + 928]
  vmovdqa ymm2, YMMWORD PTR [rdx + 960]
  vmovdqa ymm3, YMMWORD PTR [rdx + 992]
  vmovdqa ymm4, YMMWORD PTR [rcx + 896]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p2,.Lqnat_lambda_b0p2_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p2,0,4
  vmovdqa YMMWORD PTR [rdi + 896], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 928]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p2,.Lqnat_lambda_b0p2_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p2,1,4
  vmovdqa YMMWORD PTR [rdi + 928], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 960]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p2,.Lqnat_lambda_b0p2_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p2,2,4
  vmovdqa YMMWORD PTR [rdi + 960], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 992]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p2,3,4
  vmovdqa YMMWORD PTR [rdi + 992], ymm4
  /* Tile B b0p8: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 768]
  vmovdqa ymm1, YMMWORD PTR [rdx + 800]
  vmovdqa ymm2, YMMWORD PTR [rdx + 832]
  vmovdqa ymm3, YMMWORD PTR [rdx + 864]
  vmovdqa ymm4, YMMWORD PTR [rcx + 768]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p8,.Lqnat_lambda_b0p8_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p8,0,4
  vmovdqa YMMWORD PTR [rdi + 768], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 800]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p8,.Lqnat_lambda_b0p8_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p8,1,4
  vmovdqa YMMWORD PTR [rdi + 800], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 832]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p8,.Lqnat_lambda_b0p8_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p8,2,4
  vmovdqa YMMWORD PTR [rdi + 832], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 864]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p8,3,4
  vmovdqa YMMWORD PTR [rdi + 864], ymm4
  /* H3 block 4: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 768]
  vmovdqu ymm1, YMMWORD PTR [rsi + 800]
  vmovdqu ymm2, YMMWORD PTR [rsi + 832]
  vmovdqu ymm3, YMMWORD PTR [rsi + 864]
  vmovdqu ymm4, YMMWORD PTR [rsi + 896]
  vmovdqu ymm5, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x20
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm7, ymm7, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm11, ymm7, ymm7, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm8, ymm8, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm12, ymm8, ymm8, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm9, ymm9, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm13, ymm9, ymm9, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm10, ymm10, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vperm2i128 ymm14, ymm10, ymm10, 0x31
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_3]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b0p5: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1024]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1056]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1088]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1120]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1024]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p5,.Lqnat_lambda_b0p5_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p5,0,4
  vmovdqa YMMWORD PTR [rdi + 1024], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1056]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p5,.Lqnat_lambda_b0p5_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p5,1,4
  vmovdqa YMMWORD PTR [rdi + 1056], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1088]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b0p5,.Lqnat_lambda_b0p5_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p5,2,4
  vmovdqa YMMWORD PTR [rdi + 1088], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1120]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b0p5,3,4
  vmovdqa YMMWORD PTR [rdi + 1120], ymm4
  /* Tile B b1p3: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1280]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1312]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1344]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1376]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1280]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p3,.Lqnat_lambda_b1p3_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p3,0,4
  vmovdqa YMMWORD PTR [rdi + 1280], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1312]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p3,.Lqnat_lambda_b1p3_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p3,1,4
  vmovdqa YMMWORD PTR [rdi + 1312], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1344]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p3,.Lqnat_lambda_b1p3_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p3,2,4
  vmovdqa YMMWORD PTR [rdi + 1344], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1376]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p3,3,4
  vmovdqa YMMWORD PTR [rdi + 1376], ymm4
  /* H3 block 5: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 960]
  vmovdqu ymm1, YMMWORD PTR [rsi + 992]
  vmovdqu ymm2, YMMWORD PTR [rsi + 1024]
  vmovdqu ymm3, YMMWORD PTR [rsi + 1056]
  vmovdqu ymm4, YMMWORD PTR [rsi + 1088]
  vmovdqu ymm5, YMMWORD PTR [rsi + 1120]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x20
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm7, ymm7, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm11, ymm7, ymm7, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm8, ymm8, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm12, ymm8, ymm8, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm9, ymm9, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm13, ymm9, ymm9, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_0]
  vperm2i128 ymm15, ymm10, ymm10, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_1]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_6]
  vperm2i128 ymm14, ymm10, ymm10, 0x31
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_7]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b1p0: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1152]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1184]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1216]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1248]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1152]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p0,.Lqnat_lambda_b1p0_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p0,0,4
  vmovdqa YMMWORD PTR [rdi + 1152], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1184]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p0,.Lqnat_lambda_b1p0_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p0,1,4
  vmovdqa YMMWORD PTR [rdi + 1184], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1216]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p0,.Lqnat_lambda_b1p0_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p0,2,4
  vmovdqa YMMWORD PTR [rdi + 1216], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1248]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p0,3,4
  vmovdqa YMMWORD PTR [rdi + 1248], ymm4
  /* Tile B b1p6: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1408]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1440]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1472]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1504]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1408]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p6,.Lqnat_lambda_b1p6_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p6,0,4
  vmovdqa YMMWORD PTR [rdi + 1408], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1440]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p6,.Lqnat_lambda_b1p6_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p6,1,4
  vmovdqa YMMWORD PTR [rdi + 1440], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1472]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p6,.Lqnat_lambda_b1p6_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p6,2,4
  vmovdqa YMMWORD PTR [rdi + 1472], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1504]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p6,3,4
  vmovdqa YMMWORD PTR [rdi + 1504], ymm4
  /* H3 block 6: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqu ymm1, YMMWORD PTR [rsi + 1184]
  vmovdqu ymm2, YMMWORD PTR [rsi + 1216]
  vmovdqu ymm3, YMMWORD PTR [rsi + 1248]
  vmovdqu ymm4, YMMWORD PTR [rsi + 1280]
  vmovdqu ymm5, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm15, ymm7, ymm7, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm11, ymm7, ymm7, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm15, ymm8, ymm8, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm12, ymm8, ymm8, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm15, ymm9, ymm9, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm13, ymm9, ymm9, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_10]
  vperm2i128 ymm15, ymm10, ymm10, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_11]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_4]
  vperm2i128 ymm14, ymm10, ymm10, 0x20
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_5]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b1p2: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 2048]
  vmovdqa ymm1, YMMWORD PTR [rdx + 2080]
  vmovdqa ymm2, YMMWORD PTR [rdx + 2112]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2144]
  vmovdqa ymm4, YMMWORD PTR [rcx + 2048]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p2,.Lqnat_lambda_b1p2_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p2,0,4
  vmovdqa YMMWORD PTR [rdi + 2048], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2080]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p2,.Lqnat_lambda_b1p2_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p2,1,4
  vmovdqa YMMWORD PTR [rdi + 2080], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2112]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p2,.Lqnat_lambda_b1p2_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p2,2,4
  vmovdqa YMMWORD PTR [rdi + 2112], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2144]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p2,3,4
  vmovdqa YMMWORD PTR [rdi + 2144], ymm4
  /* Tile B b1p5: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 2176]
  vmovdqa ymm1, YMMWORD PTR [rdx + 2208]
  vmovdqa ymm2, YMMWORD PTR [rdx + 2240]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2272]
  vmovdqa ymm4, YMMWORD PTR [rcx + 2176]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p5,.Lqnat_lambda_b1p5_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p5,0,4
  vmovdqa YMMWORD PTR [rdi + 2176], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2208]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p5,.Lqnat_lambda_b1p5_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p5,1,4
  vmovdqa YMMWORD PTR [rdi + 2208], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2240]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p5,.Lqnat_lambda_b1p5_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p5,2,4
  vmovdqa YMMWORD PTR [rdi + 2240], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2272]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p5,3,4
  vmovdqa YMMWORD PTR [rdi + 2272], ymm4
  /* H3 block 7: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 1344]
  vmovdqu ymm1, YMMWORD PTR [rsi + 1376]
  vmovdqu ymm2, YMMWORD PTR [rsi + 1408]
  vmovdqu ymm3, YMMWORD PTR [rsi + 1440]
  vmovdqu ymm4, YMMWORD PTR [rsi + 1472]
  vmovdqu ymm5, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm7, ymm7, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm11, ymm7, ymm7, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm8, ymm8, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm12, ymm8, ymm8, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm9, ymm9, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm13, ymm9, ymm9, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_12]
  vperm2i128 ymm15, ymm10, ymm10, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_13]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_8]
  vperm2i128 ymm14, ymm10, ymm10, 0x20
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_9]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b1p7: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1792]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1824]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1856]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1888]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1792]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p7,.Lqnat_lambda_b1p7_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p7,0,4
  vmovdqa YMMWORD PTR [rdi + 1792], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1824]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p7,.Lqnat_lambda_b1p7_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p7,1,4
  vmovdqa YMMWORD PTR [rdi + 1824], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1856]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p7,.Lqnat_lambda_b1p7_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p7,2,4
  vmovdqa YMMWORD PTR [rdi + 1856], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1888]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p7,3,4
  vmovdqa YMMWORD PTR [rdi + 1888], ymm4
  /* Tile B b1p8: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1920]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1952]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1984]
  vmovdqa ymm3, YMMWORD PTR [rdx + 2016]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1920]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p8,.Lqnat_lambda_b1p8_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p8,0,4
  vmovdqa YMMWORD PTR [rdi + 1920], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1952]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p8,.Lqnat_lambda_b1p8_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p8,1,4
  vmovdqa YMMWORD PTR [rdi + 1952], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1984]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p8,.Lqnat_lambda_b1p8_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p8,2,4
  vmovdqa YMMWORD PTR [rdi + 1984], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2016]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p8,3,4
  vmovdqa YMMWORD PTR [rdi + 2016], ymm4
  /* H3 block 8: decode/validate/dual-form, then two MA2 tiles. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqu ymm1, YMMWORD PTR [rsi + 1568]
  vmovdqu ymm2, YMMWORD PTR [rsi + 1600]
  vmovdqu ymm3, YMMWORD PTR [rsi + 1632]
  vmovdqu ymm4, YMMWORD PTR [rsi + 1664]
  vmovdqu ymm5, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm6, ymm0, ymm3, 0x20
  vperm2i128 ymm7, ymm0, ymm3, 0x31
  vperm2i128 ymm8, ymm1, ymm4, 0x20
  vperm2i128 ymm9, ymm1, ymm4, 0x31
  vperm2i128 ymm10, ymm2, ymm5, 0x20
  vperm2i128 ymm11, ymm2, ymm5, 0x31
  vpunpcklqdq ymm0, ymm6, ymm9
  vpunpckhqdq ymm1, ymm6, ymm9
  vpunpcklqdq ymm2, ymm7, ymm10
  vpunpckhqdq ymm3, ymm7, ymm10
  vpunpcklqdq ymm4, ymm8, ymm11
  vpunpckhqdq ymm5, ymm8, ymm11
  vpsllq ymm8, ymm3, 32
  vpsrlq ymm9, ymm0, 32
  vpsllq ymm10, ymm4, 32
  vpsrlq ymm11, ymm1, 32
  vpsllq ymm12, ymm5, 32
  vpsrlq ymm13, ymm2, 32
  vpblendd ymm8, ymm0, ymm8, 0xaa
  vpblendd ymm9, ymm9, ymm3, 0xaa
  vpblendd ymm10, ymm1, ymm10, 0xaa
  vpblendd ymm11, ymm11, ymm4, 0xaa
  vpblendd ymm12, ymm2, ymm12, 0xaa
  vpblendd ymm13, ymm13, ymm5, 0xaa
  vpsllq ymm0, ymm11, 16
  vpsrlq ymm1, ymm8, 16
  vpsllq ymm2, ymm12, 16
  vpsrlq ymm3, ymm9, 16
  vpsllq ymm4, ymm13, 16
  vpsrlq ymm5, ymm10, 16
  vpblendw ymm0, ymm8, ymm0, 0xaa
  vpblendw ymm1, ymm1, ymm11, 0xaa
  vpblendw ymm2, ymm9, ymm2, 0xaa
  vpblendw ymm3, ymm3, ymm12, 0xaa
  vpblendw ymm4, ymm10, ymm4, 0xaa
  vpblendw ymm5, ymm5, ymm13, 0xaa
  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d0/d4; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm11, ymm7
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  vpsrlw ymm0, ymm0, 12
  vpsrlw ymm3, ymm3, 12
  vpsllw ymm6, ymm1, 4
  vpsllw ymm9, ymm4, 4
  vpxor ymm0, ymm0, ymm6
  vpxor ymm3, ymm3, ymm9
  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d1/d5; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm12, ymm8
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h0 -> ymm6. */
  vperm2i128 ymm6, ymm11, ymm11, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm7, ymm7, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm6, ymm6, ymm15
  /* Tile B h0 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm11, ymm11, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm11, ymm7, ymm7, 0x20
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm7, ymm15, ymm11
  vpsrlw ymm0, ymm1, 8
  vpsrlw ymm3, ymm4, 8
  vpsllw ymm1, ymm2, 8
  vpsllw ymm4, ymm5, 8
  vpxor ymm0, ymm0, ymm1
  vpxor ymm3, ymm3, ymm4
  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d2/d6; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm13, ymm9
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h1 -> ymm11. */
  vperm2i128 ymm11, ymm12, ymm12, 0x31
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm8, ymm8, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm11, ymm11, ymm15
  /* Tile B h1 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm12, ymm12, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm12, ymm8, ymm8, 0x20
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm8, ymm15, ymm12
  vpsrlw ymm0, ymm2, 4
  vpsrlw ymm3, ymm5, 4
  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]
  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]
  /* Validate d3/d7; eax is the public invalid accumulator. */
  vpmaxuw ymm15, ymm14, ymm10
  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]
  vpmovmskb r8d, ymm15
  or eax, r8d
  /* Delayed dual formation: tile A h2 -> ymm12. */
  vperm2i128 ymm12, ymm13, ymm13, 0x31
  vpshufb ymm12, ymm12, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm9, ymm9, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm12, ymm12, ymm15
  /* Tile B h2 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm13, ymm13, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm13, ymm9, ymm9, 0x20
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm9, ymm15, ymm13
  /* Delayed dual formation: tile A h3 -> ymm13. */
  vperm2i128 ymm13, ymm14, ymm14, 0x31
  vpshufb ymm13, ymm13, YMMWORD PTR [rip + .Lh3_mask_3]
  vperm2i128 ymm15, ymm10, ymm10, 0x31
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_2]
  vpor ymm13, ymm13, ymm15
  /* Tile B h3 overwrites the dead decoded source pair. */
  vperm2i128 ymm15, ymm14, ymm14, 0x20
  vpshufb ymm15, ymm15, YMMWORD PTR [rip + .Lh3_mask_14]
  vperm2i128 ymm14, ymm10, ymm10, 0x20
  vpshufb ymm14, ymm14, YMMWORD PTR [rip + .Lh3_mask_15]
  vpor ymm10, ymm15, ymm14
  /* Same H1 R2 conversion, performed in place for both live quartets. */
  H3_MONT_CONST 6,6,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 11,11,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 12,12,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 13,13,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 7,7,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 8,8,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 9,9,.Lma1_r2,.Lma1_r2_qinv,15
  H3_MONT_CONST 10,10,.Lma1_r2,.Lma1_r2_qinv,15
  /* Tile A b1p1: exact 16/16 YMM cut. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1536]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1568]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1600]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1632]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1536]
  H3_MONT_REG 14,6,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,12,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,13,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p1,.Lqnat_lambda_b1p1_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p1,0,4
  vmovdqa YMMWORD PTR [rdi + 1536], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1568]
  H3_MONT_REG 14,6,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,13,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p1,.Lqnat_lambda_b1p1_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p1,1,4
  vmovdqa YMMWORD PTR [rdi + 1568], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1600]
  H3_MONT_REG 14,6,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p1,.Lqnat_lambda_b1p1_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p1,2,4
  vmovdqa YMMWORD PTR [rdi + 1600], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1632]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p1,3,4
  vmovdqa YMMWORD PTR [rdi + 1632], ymm4
  /* Tile B b1p4: tile-A h/r are dead. */
  vmovdqa ymm0, YMMWORD PTR [rdx + 1664]
  vmovdqa ymm1, YMMWORD PTR [rdx + 1696]
  vmovdqa ymm2, YMMWORD PTR [rdx + 1728]
  vmovdqa ymm3, YMMWORD PTR [rdx + 1760]
  vmovdqa ymm4, YMMWORD PTR [rcx + 1664]
  H3_MONT_REG 14,7,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,9,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_REG 14,10,1,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p4,.Lqnat_lambda_b1p4_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p4,0,4
  vmovdqa YMMWORD PTR [rdi + 1664], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1696]
  H3_MONT_REG 14,7,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_REG 14,10,2,15
  vpaddw ymm5, ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p4,.Lqnat_lambda_b1p4_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p4,1,4
  vmovdqa YMMWORD PTR [rdi + 1696], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1728]
  H3_MONT_REG 14,7,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,3,15
  vmovdqa ymm5, ymm14
  H3_MONT_CONST 14,5,.Lqnat_lambda_b1p4,.Lqnat_lambda_b1p4_qinv,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p4,2,4
  vmovdqa YMMWORD PTR [rdi + 1728], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1760]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  H3_TERMINAL_C b1p4,3,4
  vmovdqa YMMWORD PTR [rdi + 1760], ymm4
  test eax, eax
  setne al
  movzx eax, al
  ret
.size ntruplus1152_exp001_encap_h_ingress_ma2_h3, .-ntruplus1152_exp001_encap_h_ingress_ma2_h3

.section .rodata,"a",@progbits
.p2align 5
.Lhdec_low_mask:
  .short 4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095,4095
.Lh3_qm1:
  .short 3456,3456,3456,3456,3456,3456,3456,3456,3456,3456,3456,3456,3456,3456,3456,3456
.p2align 5
.Lh3_mask_0:
  .byte 2,3,128,128,0,1,128,128,4,5,128,128,128,128,6,7,12,13,128,128,128,128,14,15,8,9,128,128,128,128,10,11
.p2align 5
.Lh3_mask_1:
  .byte 128,128,2,3,128,128,0,1,128,128,4,5,6,7,128,128,128,128,12,13,14,15,128,128,128,128,8,9,10,11,128,128
.p2align 5
.Lh3_mask_2:
  .byte 128,128,14,15,128,128,12,13,128,128,10,11,128,128,8,9,128,128,6,7,128,128,4,5,128,128,2,3,128,128,0,1
.p2align 5
.Lh3_mask_3:
  .byte 14,15,128,128,12,13,128,128,10,11,128,128,8,9,128,128,6,7,128,128,4,5,128,128,2,3,128,128,0,1,128,128
.p2align 5
.Lh3_mask_4:
  .byte 6,7,128,128,4,5,128,128,2,3,128,128,0,1,128,128,10,11,128,128,8,9,128,128,12,13,128,128,128,128,14,15
.p2align 5
.Lh3_mask_5:
  .byte 128,128,6,7,128,128,4,5,128,128,2,3,128,128,0,1,128,128,10,11,128,128,8,9,128,128,12,13,14,15,128,128
.p2align 5
.Lh3_mask_6:
  .byte 128,128,8,9,10,11,128,128,14,15,128,128,12,13,128,128,128,128,0,1,2,3,128,128,6,7,128,128,4,5,128,128
.p2align 5
.Lh3_mask_7:
  .byte 8,9,128,128,128,128,10,11,128,128,14,15,128,128,12,13,0,1,128,128,128,128,2,3,128,128,6,7,128,128,4,5
.p2align 5
.Lh3_mask_8:
  .byte 0,1,128,128,128,128,2,3,128,128,6,7,128,128,4,5,128,128,14,15,128,128,12,13,128,128,10,11,128,128,8,9
.p2align 5
.Lh3_mask_9:
  .byte 128,128,0,1,2,3,128,128,6,7,128,128,4,5,128,128,14,15,128,128,12,13,128,128,10,11,128,128,8,9,128,128
.p2align 5
.Lh3_mask_10:
  .byte 128,128,12,13,14,15,128,128,128,128,8,9,10,11,128,128,128,128,4,5,6,7,128,128,128,128,0,1,2,3,128,128
.p2align 5
.Lh3_mask_11:
  .byte 12,13,128,128,128,128,14,15,8,9,128,128,128,128,10,11,4,5,128,128,128,128,6,7,0,1,128,128,128,128,2,3
.p2align 5
.Lh3_mask_12:
  .byte 128,128,10,11,128,128,8,9,128,128,12,13,14,15,128,128,128,128,2,3,128,128,0,1,128,128,4,5,6,7,128,128
.p2align 5
.Lh3_mask_13:
  .byte 10,11,128,128,8,9,128,128,12,13,128,128,128,128,14,15,2,3,128,128,0,1,128,128,4,5,128,128,128,128,6,7
.p2align 5
.Lh3_mask_14:
  .byte 4,5,128,128,128,128,6,7,0,1,128,128,128,128,2,3,8,9,128,128,128,128,10,11,128,128,14,15,128,128,12,13
.p2align 5
.Lh3_mask_15:
  .byte 128,128,4,5,6,7,128,128,128,128,0,1,2,3,128,128,128,128,8,9,10,11,128,128,14,15,128,128,12,13,128,128
#include "f0-ma2-constants.inc"
#include "gt9x16-prod3-ma2-qorder-natural-constants.inc"

.section .note.GNU-stack,"",@progbits
