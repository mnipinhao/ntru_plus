/* Generated H4-M3B: H3 canonical scratch -> machine-probed exact wire egress. */
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

.globl ntruplus1152_exp001_encap_h4_m3b_exact_egress
.type ntruplus1152_exp001_encap_h4_m3b_exact_egress,@function
.p2align 5
ntruplus1152_exp001_encap_h4_m3b_exact_egress:
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b0p4,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 512], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p4,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 544], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p4,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 576], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 608]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p4,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 608], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p7,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 640], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p7,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 672], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p7,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 704], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 736]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p7,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 736], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b0p0,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 0], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p0,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 32], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p0,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 64], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 96]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p0,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 96], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p1,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 384], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p1,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 416], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p1,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 448], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 480]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p1,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 480], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b0p3,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 128], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p3,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 160], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p3,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 192], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 224]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p3,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 224], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p6,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 256], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p6,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 288], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p6,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 320], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 352]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p6,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 352], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b0p2,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 896], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p2,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 928], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p2,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 960], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 992]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p2,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 992], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p8,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 768], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p8,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 800], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p8,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 832], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 864]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p8,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 864], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b0p5,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1024], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p5,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1056], ymm4
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
  /* H4_M3B_CANONICAL_STORE b0p5,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1088], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1120]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b0p5,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1120], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p3,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1280], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p3,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1312], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p3,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1344], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1376]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p3,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1376], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b1p0,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1152], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p0,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1184], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p0,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1216], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1248]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p0,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1248], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p6,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1408], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p6,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1440], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p6,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1472], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1504]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p6,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1504], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b1p2,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2048], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p2,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2080], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p2,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2112], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2144]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p2,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2144], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p5,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2176], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p5,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2208], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p5,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2240], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2272]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p5,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2272], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b1p7,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1792], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p7,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1824], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p7,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1856], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1888]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p7,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1888], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p8,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1920], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p8,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1952], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p8,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1984], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 2016]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p8,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 2016], ymm4
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  vpmovmskb r9d, ymm15
  or eax, r9d
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
  /* H4_M3B_CANONICAL_STORE b1p1,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1536], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p1,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1568], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p1,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1600], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1632]
  H3_MONT_REG 14,6,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,11,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,12,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,13,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p1,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1632], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p4,0. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1664], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p4,1. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1696], ymm4
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
  /* H4_M3B_CANONICAL_STORE b1p4,2. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1728], ymm4
  vmovdqa ymm4, YMMWORD PTR [rcx + 1760]
  H3_MONT_REG 14,7,3,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,8,2,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,9,1,15
  vpaddw ymm4, ymm4, ymm14
  H3_MONT_REG 14,10,0,15
  vpaddw ymm4, ymm4, ymm14
  /* H4_M3B_CANONICAL_STORE b1p4,3. */
  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm15
  vpsraw ymm15, ymm4, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm15
  vmovdqa YMMWORD PTR [r8 + 1760], ymm4
  /* All PK loads are complete before exact wire stores. */
  /* Machine-probed exact wire egress for vectors [20, 21, 22, 23]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 640]
  vmovdqa ymm1, YMMWORD PTR [r8 + 672]
  vmovdqa ymm2, YMMWORD PTR [r8 + 704]
  vmovdqa ymm3, YMMWORD PTR [r8 + 736]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_0]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm5, ymm0, ymm5
  vpermd ymm6, ymm0, ymm6
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 0], ymm0
  vmovdqu YMMWORD PTR [rdi + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + 64], ymm2
  /* Machine-probed exact wire egress for vectors [16, 17, 18, 19]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 512]
  vmovdqa ymm1, YMMWORD PTR [r8 + 544]
  vmovdqa ymm2, YMMWORD PTR [r8 + 576]
  vmovdqa ymm3, YMMWORD PTR [r8 + 608]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_1]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_2]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 96], ymm0
  vmovdqu YMMWORD PTR [rdi + 128], ymm1
  vmovdqu YMMWORD PTR [rdi + 160], ymm2
  /* Machine-probed exact wire egress for vectors [12, 13, 14, 15]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 384]
  vmovdqa ymm1, YMMWORD PTR [r8 + 416]
  vmovdqa ymm2, YMMWORD PTR [r8 + 448]
  vmovdqa ymm3, YMMWORD PTR [r8 + 480]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_3]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_4]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 192], ymm0
  vmovdqu YMMWORD PTR [rdi + 224], ymm1
  vmovdqu YMMWORD PTR [rdi + 256], ymm2
  /* Machine-probed exact wire egress for vectors [0, 1, 2, 3]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 0]
  vmovdqa ymm1, YMMWORD PTR [r8 + 32]
  vmovdqa ymm2, YMMWORD PTR [r8 + 64]
  vmovdqa ymm3, YMMWORD PTR [r8 + 96]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_5]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_1]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 288], ymm0
  vmovdqu YMMWORD PTR [rdi + 320], ymm1
  vmovdqu YMMWORD PTR [rdi + 352], ymm2
  /* Machine-probed exact wire egress for vectors [8, 9, 10, 11]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vmovdqa ymm1, YMMWORD PTR [r8 + 288]
  vmovdqa ymm2, YMMWORD PTR [r8 + 320]
  vmovdqa ymm3, YMMWORD PTR [r8 + 352]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_3]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm5, ymm0, ymm5
  vpermd ymm6, ymm0, ymm6
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 384], ymm0
  vmovdqu YMMWORD PTR [rdi + 416], ymm1
  vmovdqu YMMWORD PTR [rdi + 448], ymm2
  /* Machine-probed exact wire egress for vectors [4, 5, 6, 7]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 128]
  vmovdqa ymm1, YMMWORD PTR [r8 + 160]
  vmovdqa ymm2, YMMWORD PTR [r8 + 192]
  vmovdqa ymm3, YMMWORD PTR [r8 + 224]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_6]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_7]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 480], ymm0
  vmovdqu YMMWORD PTR [rdi + 512], ymm1
  vmovdqu YMMWORD PTR [rdi + 544], ymm2
  /* Machine-probed exact wire egress for vectors [28, 29, 30, 31]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 896]
  vmovdqa ymm1, YMMWORD PTR [r8 + 928]
  vmovdqa ymm2, YMMWORD PTR [r8 + 960]
  vmovdqa ymm3, YMMWORD PTR [r8 + 992]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_0]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_3]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 576], ymm0
  vmovdqu YMMWORD PTR [rdi + 608], ymm1
  vmovdqu YMMWORD PTR [rdi + 640], ymm2
  /* Machine-probed exact wire egress for vectors [24, 25, 26, 27]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 768]
  vmovdqa ymm1, YMMWORD PTR [r8 + 800]
  vmovdqa ymm2, YMMWORD PTR [r8 + 832]
  vmovdqa ymm3, YMMWORD PTR [r8 + 864]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_2]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_6]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 672], ymm0
  vmovdqu YMMWORD PTR [rdi + 704], ymm1
  vmovdqu YMMWORD PTR [rdi + 736], ymm2
  /* Machine-probed exact wire egress for vectors [32, 33, 34, 35]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1024]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1056]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1088]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1120]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_4]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm5, ymm0, ymm5
  vpermd ymm6, ymm0, ymm6
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 768], ymm0
  vmovdqu YMMWORD PTR [rdi + 800], ymm1
  vmovdqu YMMWORD PTR [rdi + 832], ymm2
  /* Machine-probed exact wire egress for vectors [40, 41, 42, 43]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1280]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1312]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1344]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1376]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_0]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm5, ymm0, ymm5
  vpermd ymm6, ymm0, ymm6
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 864], ymm0
  vmovdqu YMMWORD PTR [rdi + 896], ymm1
  vmovdqu YMMWORD PTR [rdi + 928], ymm2
  /* Machine-probed exact wire egress for vectors [36, 37, 38, 39]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1152]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1184]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1216]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1248]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_1]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_2]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 960], ymm0
  vmovdqu YMMWORD PTR [rdi + 992], ymm1
  vmovdqu YMMWORD PTR [rdi + 1024], ymm2
  /* Machine-probed exact wire egress for vectors [44, 45, 46, 47]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1408]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1440]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1472]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1504]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_3]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_4]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 1056], ymm0
  vmovdqu YMMWORD PTR [rdi + 1088], ymm1
  vmovdqu YMMWORD PTR [rdi + 1120], ymm2
  /* Machine-probed exact wire egress for vectors [68, 69, 70, 71]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 2176]
  vmovdqa ymm1, YMMWORD PTR [r8 + 2208]
  vmovdqa ymm2, YMMWORD PTR [r8 + 2240]
  vmovdqa ymm3, YMMWORD PTR [r8 + 2272]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_5]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_1]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 1152], ymm0
  vmovdqu YMMWORD PTR [rdi + 1184], ymm1
  vmovdqu YMMWORD PTR [rdi + 1216], ymm2
  /* Machine-probed exact wire egress for vectors [64, 65, 66, 67]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 2048]
  vmovdqa ymm1, YMMWORD PTR [r8 + 2080]
  vmovdqa ymm2, YMMWORD PTR [r8 + 2112]
  vmovdqa ymm3, YMMWORD PTR [r8 + 2144]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_3]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm5, ymm0, ymm5
  vpermd ymm6, ymm0, ymm6
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 1248], ymm0
  vmovdqu YMMWORD PTR [rdi + 1280], ymm1
  vmovdqu YMMWORD PTR [rdi + 1312], ymm2
  /* Machine-probed exact wire egress for vectors [60, 61, 62, 63]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1920]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1952]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1984]
  vmovdqa ymm3, YMMWORD PTR [r8 + 2016]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_6]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_7]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 1344], ymm0
  vmovdqu YMMWORD PTR [rdi + 1376], ymm1
  vmovdqu YMMWORD PTR [rdi + 1408], ymm2
  /* Machine-probed exact wire egress for vectors [56, 57, 58, 59]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1792]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1824]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1856]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1888]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_0]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_3]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 1440], ymm0
  vmovdqu YMMWORD PTR [rdi + 1472], ymm1
  vmovdqu YMMWORD PTR [rdi + 1504], ymm2
  /* Machine-probed exact wire egress for vectors [52, 53, 54, 55]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1664]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1696]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1728]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1760]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_2]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm6, ymm0, ymm6
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_6]
  vpermd ymm5, ymm0, ymm5
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm3, 1
  vextracti128 xmm5, ymm9, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm3
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm9, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm3, xmm9, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm3, xmm3, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm3, 1
  vmovdqu YMMWORD PTR [rdi + 1536], ymm0
  vmovdqu YMMWORD PTR [rdi + 1568], ymm1
  vmovdqu YMMWORD PTR [rdi + 1600], ymm2
  /* Machine-probed exact wire egress for vectors [48, 49, 50, 51]. */
  vmovdqa ymm0, YMMWORD PTR [r8 + 1536]
  vmovdqa ymm1, YMMWORD PTR [r8 + 1568]
  vmovdqa ymm2, YMMWORD PTR [r8 + 1600]
  vmovdqa ymm3, YMMWORD PTR [r8 + 1632]
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vmovdqa ymm0, YMMWORD PTR [rip + .Lh4_m3b_index_4]
  vpermd ymm4, ymm0, ymm4
  vpermd ymm5, ymm0, ymm5
  vpermd ymm6, ymm0, ymm6
  vpermd ymm7, ymm0, ymm7
  vpunpckldq ymm0, ymm5, ymm7
  vpunpckhdq ymm1, ymm5, ymm7
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vpunpckldq ymm0, ymm4, ymm6
  vpunpckhdq ymm1, ymm4, ymm6
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm8, 1
  vextracti128 xmm5, ymm2, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm8
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm2, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm8, xmm2, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm6
  vmovdqa ymm11, ymm7
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm4, ymm9, 1
  vextracti128 xmm5, ymm3, 1
  vpslldq xmm6, xmm4, 12
  vpor xmm6, xmm6, xmm9
  vpsrldq xmm7, xmm4, 4
  vpslldq xmm13, xmm3, 8
  vpor xmm7, xmm7, xmm13
  vpsrldq xmm9, xmm3, 8
  vpslldq xmm13, xmm5, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm0, ymm10, xmm11, 1
  vinserti128 ymm1, ymm12, xmm6, 1
  vinserti128 ymm2, ymm7, xmm9, 1
  vmovdqu YMMWORD PTR [rdi + 1632], ymm0
  vmovdqu YMMWORD PTR [rdi + 1664], ymm1
  vmovdqu YMMWORD PTR [rdi + 1696], ymm2
  test eax, eax
  setne al
  movzx eax, al
  ret
.size ntruplus1152_exp001_encap_h4_m3b_exact_egress, .-ntruplus1152_exp001_encap_h4_m3b_exact_egress

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
#include "generated/f0-ma2-constants.inc"
#include "generated/gt9x16-prod3-ma2-qorder-natural-constants.inc"

.section .rodata,"a",@progbits
.p2align 5
.Lh4_m3b_index_0:
  .long 7,6,5,4,3,2,1,0
.p2align 5
.Lh4_m3b_index_1:
  .long 2,3,0,1,4,5,7,6
.p2align 5
.Lh4_m3b_index_2:
  .long 0,1,3,2,4,5,7,6
.p2align 5
.Lh4_m3b_index_3:
  .long 5,4,6,7,1,0,2,3
.p2align 5
.Lh4_m3b_index_4:
  .long 6,7,4,5,2,3,0,1
.p2align 5
.Lh4_m3b_index_5:
  .long 2,3,0,1,6,7,4,5
.p2align 5
.Lh4_m3b_index_6:
  .long 0,1,3,2,7,6,5,4
.p2align 5
.Lh4_m3b_index_7:
  .long 3,2,1,0,7,6,5,4
.p2align 5
.Lh4_m3b_pair_weight:
  .short 1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096
.p2align 5
.Lh4_m3b_pack24:
  .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128

.section .note.GNU-stack,"",@progbits
