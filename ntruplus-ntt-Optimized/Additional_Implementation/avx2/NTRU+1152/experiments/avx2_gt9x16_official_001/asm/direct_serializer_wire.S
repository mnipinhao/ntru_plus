/* Generated direct scale-1 exact-wire serializer. */
.intel_syntax noprefix
.text
.p2align 5
.globl ntruplus1152_exp001_direct_serializer_wire
.type ntruplus1152_exp001_direct_serializer_wire,@function
ntruplus1152_exp001_direct_serializer_wire:
  /* Machine-probed exact wire egress for vectors [20, 21, 22, 23]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 672]
  vmovdqa ymm2, YMMWORD PTR [rsi + 704]
  vmovdqa ymm3, YMMWORD PTR [rsi + 736]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 0], ymm0
  vmovdqu YMMWORD PTR [rdi + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + 64], ymm2
  /* Machine-probed exact wire egress for vectors [16, 17, 18, 19]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vmovdqa ymm2, YMMWORD PTR [rsi + 576]
  vmovdqa ymm3, YMMWORD PTR [rsi + 608]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 96], ymm0
  vmovdqu YMMWORD PTR [rdi + 128], ymm1
  vmovdqu YMMWORD PTR [rdi + 160], ymm2
  /* Machine-probed exact wire egress for vectors [12, 13, 14, 15]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 416]
  vmovdqa ymm2, YMMWORD PTR [rsi + 448]
  vmovdqa ymm3, YMMWORD PTR [rsi + 480]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vmovdqa ymm2, YMMWORD PTR [rsi + 64]
  vmovdqa ymm3, YMMWORD PTR [rsi + 96]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 288], ymm0
  vmovdqu YMMWORD PTR [rdi + 320], ymm1
  vmovdqu YMMWORD PTR [rdi + 352], ymm2
  /* Machine-probed exact wire egress for vectors [8, 9, 10, 11]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 288]
  vmovdqa ymm2, YMMWORD PTR [rsi + 320]
  vmovdqa ymm3, YMMWORD PTR [rsi + 352]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 384], ymm0
  vmovdqu YMMWORD PTR [rdi + 416], ymm1
  vmovdqu YMMWORD PTR [rdi + 448], ymm2
  /* Machine-probed exact wire egress for vectors [4, 5, 6, 7]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 128]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vmovdqa ymm2, YMMWORD PTR [rsi + 192]
  vmovdqa ymm3, YMMWORD PTR [rsi + 224]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 480], ymm0
  vmovdqu YMMWORD PTR [rdi + 512], ymm1
  vmovdqu YMMWORD PTR [rdi + 544], ymm2
  /* Machine-probed exact wire egress for vectors [28, 29, 30, 31]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 928]
  vmovdqa ymm2, YMMWORD PTR [rsi + 960]
  vmovdqa ymm3, YMMWORD PTR [rsi + 992]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqa ymm0, YMMWORD PTR [rsi + 768]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vmovdqa ymm2, YMMWORD PTR [rsi + 832]
  vmovdqa ymm3, YMMWORD PTR [rsi + 864]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 672], ymm0
  vmovdqu YMMWORD PTR [rdi + 704], ymm1
  vmovdqu YMMWORD PTR [rdi + 736], ymm2
  /* Machine-probed exact wire egress for vectors [32, 33, 34, 35]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1056]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1120]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 768], ymm0
  vmovdqu YMMWORD PTR [rdi + 800], ymm1
  vmovdqu YMMWORD PTR [rdi + 832], ymm2
  /* Machine-probed exact wire egress for vectors [40, 41, 42, 43]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1376]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 864], ymm0
  vmovdqu YMMWORD PTR [rdi + 896], ymm1
  vmovdqu YMMWORD PTR [rdi + 928], ymm2
  /* Machine-probed exact wire egress for vectors [36, 37, 38, 39]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1184]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1248]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 960], ymm0
  vmovdqu YMMWORD PTR [rdi + 992], ymm1
  vmovdqu YMMWORD PTR [rdi + 1024], ymm2
  /* Machine-probed exact wire egress for vectors [44, 45, 46, 47]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1504]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2208]
  vmovdqa ymm2, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2272]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 1152], ymm0
  vmovdqu YMMWORD PTR [rdi + 1184], ymm1
  vmovdqu YMMWORD PTR [rdi + 1216], ymm2
  /* Machine-probed exact wire egress for vectors [64, 65, 66, 67]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vmovdqa ymm2, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2144]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 1248], ymm0
  vmovdqu YMMWORD PTR [rdi + 1280], ymm1
  vmovdqu YMMWORD PTR [rdi + 1312], ymm2
  /* Machine-probed exact wire egress for vectors [60, 61, 62, 63]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1952]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm3, YMMWORD PTR [rsi + 2016]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 1344], ymm0
  vmovdqu YMMWORD PTR [rdi + 1376], ymm1
  vmovdqu YMMWORD PTR [rdi + 1408], ymm2
  /* Machine-probed exact wire egress for vectors [56, 57, 58, 59]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1888]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1696]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1760]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 1536], ymm0
  vmovdqu YMMWORD PTR [rdi + 1568], ymm1
  vmovdqu YMMWORD PTR [rdi + 1600], ymm2
  /* Machine-probed exact wire egress for vectors [48, 49, 50, 51]. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vmovdqa ymm2, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm3, YMMWORD PTR [rsi + 1632]
  vpmulhrsw ymm15, ymm0, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm15
  vpsraw ymm15, ymm0, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm15
  vpmulhrsw ymm15, ymm1, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm1, ymm1, ymm15
  vpsraw ymm15, ymm1, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm1, ymm1, ymm15
  vpmulhrsw ymm15, ymm2, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm2, ymm2, ymm15
  vpsraw ymm15, ymm2, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm2, ymm2, ymm15
  vpmulhrsw ymm15, ymm3, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm3, ymm3, ymm15
  vpsraw ymm15, ymm3, 15
  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm3, ymm3, ymm15
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3
  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
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
  vmovdqu YMMWORD PTR [rdi + 1632], ymm0
  vmovdqu YMMWORD PTR [rdi + 1664], ymm1
  vmovdqu YMMWORD PTR [rdi + 1696], ymm2
  ret
.size ntruplus1152_exp001_direct_serializer_wire, .-ntruplus1152_exp001_direct_serializer_wire
.section .rodata,"a",@progbits
.p2align 5
.Lh4_m3b_pair_weight:
  .short 1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096
.p2align 5
.Lh4_m3b_pack24:
  .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
#include "generated/f0-ma2-constants.inc"
.section .note.GNU-stack,"",@progbits
