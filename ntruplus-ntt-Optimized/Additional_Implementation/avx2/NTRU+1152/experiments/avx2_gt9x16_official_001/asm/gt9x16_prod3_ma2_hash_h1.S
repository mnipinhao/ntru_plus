/* Generated H1 ASM0: materialized scale-4 MA2 planes -> exact hash bytes. */
.intel_syntax noprefix
.text
.globl ntruplus1152_exp001_prod3_ma2_hash_h1
.type ntruplus1152_exp001_prod3_ma2_hash_h1,@function
.p2align 5
ntruplus1152_exp001_prod3_ma2_hash_h1:
  /* H1 block 0: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 640]
  vmovdqu ymm9, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vmovdqu ymm8, YMMWORD PTR [rsi + 640]
  vmovdqu ymm9, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 672]
  vmovdqu ymm9, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vmovdqu ymm8, YMMWORD PTR [rsi + 672]
  vmovdqu ymm9, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 704]
  vmovdqu ymm9, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vmovdqu ymm8, YMMWORD PTR [rsi + 704]
  vmovdqu ymm9, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 736]
  vmovdqu ymm9, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vmovdqu ymm8, YMMWORD PTR [rsi + 736]
  vmovdqu ymm9, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 640]
  vmovdqu ymm9, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vmovdqu ymm8, YMMWORD PTR [rsi + 640]
  vmovdqu ymm9, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 672]
  vmovdqu ymm9, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vmovdqu ymm8, YMMWORD PTR [rsi + 672]
  vmovdqu ymm9, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 704]
  vmovdqu ymm9, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vmovdqu ymm8, YMMWORD PTR [rsi + 704]
  vmovdqu ymm9, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 736]
  vmovdqu ymm9, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_1]
  vmovdqu ymm8, YMMWORD PTR [rsi + 736]
  vmovdqu ymm9, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_0]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 0], ymm0
  vmovdqu YMMWORD PTR [rdi + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + 64], ymm2
  vmovdqu YMMWORD PTR [rdi + 96], ymm3
  vmovdqu YMMWORD PTR [rdi + 128], ymm4
  vmovdqu YMMWORD PTR [rdi + 160], ymm5
  /* H1 block 1: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 384]
  vmovdqu ymm9, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vmovdqu ymm8, YMMWORD PTR [rsi + 384]
  vmovdqu ymm9, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 416]
  vmovdqu ymm9, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vmovdqu ymm8, YMMWORD PTR [rsi + 416]
  vmovdqu ymm9, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 448]
  vmovdqu ymm9, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vmovdqu ymm8, YMMWORD PTR [rsi + 448]
  vmovdqu ymm9, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 480]
  vmovdqu ymm9, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vmovdqu ymm8, YMMWORD PTR [rsi + 480]
  vmovdqu ymm9, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 384]
  vmovdqu ymm9, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vmovdqu ymm8, YMMWORD PTR [rsi + 384]
  vmovdqu ymm9, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 416]
  vmovdqu ymm9, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vmovdqu ymm8, YMMWORD PTR [rsi + 416]
  vmovdqu ymm9, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 448]
  vmovdqu ymm9, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vmovdqu ymm8, YMMWORD PTR [rsi + 448]
  vmovdqu ymm9, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 480]
  vmovdqu ymm9, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_3]
  vmovdqu ymm8, YMMWORD PTR [rsi + 480]
  vmovdqu ymm9, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_2]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 192], ymm0
  vmovdqu YMMWORD PTR [rdi + 224], ymm1
  vmovdqu YMMWORD PTR [rdi + 256], ymm2
  vmovdqu YMMWORD PTR [rdi + 288], ymm3
  vmovdqu YMMWORD PTR [rdi + 320], ymm4
  vmovdqu YMMWORD PTR [rdi + 352], ymm5
  /* H1 block 2: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 256]
  vmovdqu ymm9, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vmovdqu ymm8, YMMWORD PTR [rsi + 256]
  vmovdqu ymm9, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 288]
  vmovdqu ymm9, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vmovdqu ymm8, YMMWORD PTR [rsi + 288]
  vmovdqu ymm9, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 320]
  vmovdqu ymm9, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vmovdqu ymm8, YMMWORD PTR [rsi + 320]
  vmovdqu ymm9, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 352]
  vmovdqu ymm9, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vmovdqu ymm8, YMMWORD PTR [rsi + 352]
  vmovdqu ymm9, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 256]
  vmovdqu ymm9, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vmovdqu ymm8, YMMWORD PTR [rsi + 256]
  vmovdqu ymm9, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 288]
  vmovdqu ymm9, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vmovdqu ymm8, YMMWORD PTR [rsi + 288]
  vmovdqu ymm9, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 320]
  vmovdqu ymm9, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vmovdqu ymm8, YMMWORD PTR [rsi + 320]
  vmovdqu ymm9, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 352]
  vmovdqu ymm9, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_5]
  vmovdqu ymm8, YMMWORD PTR [rsi + 352]
  vmovdqu ymm9, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_4]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 384], ymm0
  vmovdqu YMMWORD PTR [rdi + 416], ymm1
  vmovdqu YMMWORD PTR [rdi + 448], ymm2
  vmovdqu YMMWORD PTR [rdi + 480], ymm3
  vmovdqu YMMWORD PTR [rdi + 512], ymm4
  vmovdqu YMMWORD PTR [rdi + 544], ymm5
  /* H1 block 3: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 896]
  vmovdqu ymm9, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vmovdqu ymm8, YMMWORD PTR [rsi + 896]
  vmovdqu ymm9, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 928]
  vmovdqu ymm9, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vmovdqu ymm8, YMMWORD PTR [rsi + 928]
  vmovdqu ymm9, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 960]
  vmovdqu ymm9, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vmovdqu ymm8, YMMWORD PTR [rsi + 960]
  vmovdqu ymm9, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 992]
  vmovdqu ymm9, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vmovdqu ymm8, YMMWORD PTR [rsi + 992]
  vmovdqu ymm9, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 896]
  vmovdqu ymm9, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vmovdqu ymm8, YMMWORD PTR [rsi + 896]
  vmovdqu ymm9, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 928]
  vmovdqu ymm9, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vmovdqu ymm8, YMMWORD PTR [rsi + 928]
  vmovdqu ymm9, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 960]
  vmovdqu ymm9, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vmovdqu ymm8, YMMWORD PTR [rsi + 960]
  vmovdqu ymm9, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 992]
  vmovdqu ymm9, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_7]
  vmovdqu ymm8, YMMWORD PTR [rsi + 992]
  vmovdqu ymm9, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_6]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 576], ymm0
  vmovdqu YMMWORD PTR [rdi + 608], ymm1
  vmovdqu YMMWORD PTR [rdi + 640], ymm2
  vmovdqu YMMWORD PTR [rdi + 672], ymm3
  vmovdqu YMMWORD PTR [rdi + 704], ymm4
  vmovdqu YMMWORD PTR [rdi + 736], ymm5
  /* H1 block 4: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 1024]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1280]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1056]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1088]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1344]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1120]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1024]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1280]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1056]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1088]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1344]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1120]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_8]
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 768], ymm0
  vmovdqu YMMWORD PTR [rdi + 800], ymm1
  vmovdqu YMMWORD PTR [rdi + 832], ymm2
  vmovdqu YMMWORD PTR [rdi + 864], ymm3
  vmovdqu YMMWORD PTR [rdi + 896], ymm4
  vmovdqu YMMWORD PTR [rdi + 928], ymm5
  /* H1 block 5: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 1152]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1152]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1184]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1184]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1216]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1216]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1248]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1248]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1152]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1152]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1184]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1184]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1216]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1216]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1248]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_10]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1248]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_9]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 960], ymm0
  vmovdqu YMMWORD PTR [rdi + 992], ymm1
  vmovdqu YMMWORD PTR [rdi + 1024], ymm2
  vmovdqu YMMWORD PTR [rdi + 1056], ymm3
  vmovdqu YMMWORD PTR [rdi + 1088], ymm4
  vmovdqu YMMWORD PTR [rdi + 1120], ymm5
  /* H1 block 6: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 2176]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2176]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2208]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2208]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2240]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2240]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2272]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2272]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2176]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2176]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2208]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2208]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2240]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2240]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2272]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_12]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2272]
  vmovdqu ymm9, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_11]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 1152], ymm0
  vmovdqu YMMWORD PTR [rdi + 1184], ymm1
  vmovdqu YMMWORD PTR [rdi + 1216], ymm2
  vmovdqu YMMWORD PTR [rdi + 1248], ymm3
  vmovdqu YMMWORD PTR [rdi + 1280], ymm4
  vmovdqu YMMWORD PTR [rdi + 1312], ymm5
  /* H1 block 7: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 1920]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1920]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1952]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1952]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1984]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1984]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2016]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2016]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1920]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1920]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1952]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1952]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1984]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1984]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 2016]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_14]
  vmovdqu ymm8, YMMWORD PTR [rsi + 2016]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_13]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 1344], ymm0
  vmovdqu YMMWORD PTR [rdi + 1376], ymm1
  vmovdqu YMMWORD PTR [rdi + 1408], ymm2
  vmovdqu YMMWORD PTR [rdi + 1440], ymm3
  vmovdqu YMMWORD PTR [rdi + 1472], ymm4
  vmovdqu YMMWORD PTR [rdi + 1504], ymm5
  /* H1 block 8: exact Official vectors. */
  vmovdqu ymm8, YMMWORD PTR [rsi + 1664]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm0, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1664]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vpor ymm0, ymm0, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1696]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm1, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1696]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vpor ymm1, ymm1, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1728]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm2, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1728]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vpor ymm2, ymm2, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1760]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm10, ymm8, ymm9, 0x20
  vpshufb ymm3, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1760]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm10, ymm8, ymm9, 0x21
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vpor ymm3, ymm3, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1664]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm4, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1664]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vpor ymm4, ymm4, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1696]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm5, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1696]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vpor ymm5, ymm5, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1728]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm6, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1728]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vpor ymm6, ymm6, ymm10
  vmovdqu ymm8, YMMWORD PTR [rsi + 1760]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm10, ymm8, ymm9, 0x30
  vpshufb ymm7, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_16]
  vmovdqu ymm8, YMMWORD PTR [rsi + 1760]
  vmovdqu ymm9, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm10, ymm8, ymm9, 0x31
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lprod3_hash_h1_mask_15]
  vpor ymm7, ymm7, ymm10
  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]
  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]
  vpmullw ymm11, ymm0, ymm13
  vpmulhw ymm0, ymm0, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm0, ymm0, ymm11
  vpsraw ymm11, ymm0, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm0, ymm0, ymm11
  vpmullw ymm11, ymm1, ymm13
  vpmulhw ymm1, ymm1, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm1, ymm1, ymm11
  vpsraw ymm11, ymm1, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm1, ymm1, ymm11
  vpmullw ymm11, ymm2, ymm13
  vpmulhw ymm2, ymm2, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm2, ymm2, ymm11
  vpsraw ymm11, ymm2, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm2, ymm2, ymm11
  vpmullw ymm11, ymm3, ymm13
  vpmulhw ymm3, ymm3, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm3, ymm3, ymm11
  vpsraw ymm11, ymm3, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm3, ymm3, ymm11
  vpmullw ymm11, ymm4, ymm13
  vpmulhw ymm4, ymm4, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm4, ymm4, ymm11
  vpsraw ymm11, ymm4, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm4, ymm4, ymm11
  vpmullw ymm11, ymm5, ymm13
  vpmulhw ymm5, ymm5, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm5, ymm5, ymm11
  vpsraw ymm11, ymm5, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm5, ymm5, ymm11
  vpmullw ymm11, ymm6, ymm13
  vpmulhw ymm6, ymm6, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm6, ymm6, ymm11
  vpsraw ymm11, ymm6, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm6, ymm6, ymm11
  vpmullw ymm11, ymm7, ymm13
  vpmulhw ymm7, ymm7, ymm14
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm7, ymm7, ymm11
  vpsraw ymm11, ymm7, 15
  vpand ymm11, ymm11, ymm15
  vpaddw ymm7, ymm7, ymm11
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
  vmovdqu YMMWORD PTR [rdi + 1536], ymm0
  vmovdqu YMMWORD PTR [rdi + 1568], ymm1
  vmovdqu YMMWORD PTR [rdi + 1600], ymm2
  vmovdqu YMMWORD PTR [rdi + 1632], ymm3
  vmovdqu YMMWORD PTR [rdi + 1664], ymm4
  vmovdqu YMMWORD PTR [rdi + 1696], ymm5
  ret
.size ntruplus1152_exp001_prod3_ma2_hash_h1, .-ntruplus1152_exp001_prod3_ma2_hash_h1

.section .rodata,"a",@progbits
.p2align 5
.Lprod3_hash_h1_qinv:
  .short 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379, 16379
.p2align 5
.Lprod3_hash_h1_inv4:
  .short -901, -901, -901, -901, -901, -901, -901, -901, -901, -901, -901, -901, -901, -901, -901, -901
.p2align 5
.Lprod3_hash_h1_q:
  .short 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457, 3457
.p2align 5
.Lprod3_hash_h1_mask_0:
  .byte 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1, 2, 3, 0, 1, 4, 5, 128, 128, 12, 13, 128, 128, 8, 9, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_1:
  .byte 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1, 128, 128, 128, 128, 128, 128, 6, 7, 128, 128, 14, 15, 128, 128, 10, 11
.p2align 5
.Lprod3_hash_h1_mask_2:
  .byte 128, 128, 10, 11, 14, 15, 12, 13, 128, 128, 2, 3, 6, 7, 4, 5, 6, 7, 4, 5, 2, 3, 0, 1, 10, 11, 8, 9, 12, 13, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_3:
  .byte 8, 9, 128, 128, 128, 128, 128, 128, 0, 1, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 14, 15
.p2align 5
.Lprod3_hash_h1_mask_4:
  .byte 128, 128, 14, 15, 128, 128, 10, 11, 128, 128, 6, 7, 128, 128, 2, 3, 0, 1, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_5:
  .byte 12, 13, 128, 128, 8, 9, 128, 128, 4, 5, 128, 128, 0, 1, 128, 128, 128, 128, 2, 3, 6, 7, 4, 5, 14, 15, 12, 13, 10, 11, 8, 9
.p2align 5
.Lprod3_hash_h1_mask_6:
  .byte 128, 128, 128, 128, 128, 128, 14, 15, 128, 128, 128, 128, 128, 128, 6, 7, 4, 5, 128, 128, 0, 1, 128, 128, 8, 9, 128, 128, 128, 128, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_7:
  .byte 10, 11, 8, 9, 12, 13, 128, 128, 2, 3, 0, 1, 4, 5, 128, 128, 128, 128, 6, 7, 128, 128, 2, 3, 128, 128, 10, 11, 14, 15, 12, 13
.p2align 5
.Lprod3_hash_h1_mask_8:
  .byte 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1, 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1
.p2align 5
.Lprod3_hash_h1_mask_9:
  .byte 2, 3, 0, 1, 4, 5, 128, 128, 12, 13, 128, 128, 8, 9, 128, 128, 128, 128, 10, 11, 14, 15, 12, 13, 128, 128, 2, 3, 6, 7, 4, 5
.p2align 5
.Lprod3_hash_h1_mask_10:
  .byte 128, 128, 128, 128, 128, 128, 6, 7, 128, 128, 14, 15, 128, 128, 10, 11, 8, 9, 128, 128, 128, 128, 128, 128, 0, 1, 128, 128, 128, 128, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_11:
  .byte 6, 7, 4, 5, 2, 3, 0, 1, 10, 11, 8, 9, 12, 13, 128, 128, 128, 128, 14, 15, 128, 128, 10, 11, 128, 128, 6, 7, 128, 128, 2, 3
.p2align 5
.Lprod3_hash_h1_mask_12:
  .byte 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 14, 15, 12, 13, 128, 128, 8, 9, 128, 128, 4, 5, 128, 128, 0, 1, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_13:
  .byte 0, 1, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 14, 15, 128, 128, 128, 128, 128, 128, 6, 7
.p2align 5
.Lprod3_hash_h1_mask_14:
  .byte 128, 128, 2, 3, 6, 7, 4, 5, 14, 15, 12, 13, 10, 11, 8, 9, 10, 11, 8, 9, 12, 13, 128, 128, 2, 3, 0, 1, 4, 5, 128, 128
.p2align 5
.Lprod3_hash_h1_mask_15:
  .byte 4, 5, 128, 128, 0, 1, 128, 128, 8, 9, 128, 128, 128, 128, 128, 128, 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1
.p2align 5
.Lprod3_hash_h1_mask_16:
  .byte 128, 128, 6, 7, 128, 128, 2, 3, 128, 128, 10, 11, 14, 15, 12, 13, 14, 15, 12, 13, 10, 11, 8, 9, 6, 7, 4, 5, 2, 3, 0, 1

.section .note.GNU-stack,"",@progbits
