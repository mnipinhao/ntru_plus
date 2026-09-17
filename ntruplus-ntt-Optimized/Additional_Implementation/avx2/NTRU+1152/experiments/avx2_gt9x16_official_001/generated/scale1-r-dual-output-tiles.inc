/* Generated live-terminal r serializer tiles. */
.macro PROD3_R_DUAL_OUTPUT_TILE_0_0
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 288], ymm4
  vmovdqu YMMWORD PTR [rsi + 320], ymm5
  vmovdqu YMMWORD PTR [rsi + 352], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_1
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 480], ymm4
  vmovdqu YMMWORD PTR [rsi + 512], ymm5
  vmovdqu YMMWORD PTR [rsi + 544], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_2
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 384], ymm4
  vmovdqu YMMWORD PTR [rsi + 416], ymm5
  vmovdqu YMMWORD PTR [rsi + 448], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_3
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 192], ymm4
  vmovdqu YMMWORD PTR [rsi + 224], ymm5
  vmovdqu YMMWORD PTR [rsi + 256], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_4
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 96], ymm4
  vmovdqu YMMWORD PTR [rsi + 128], ymm5
  vmovdqu YMMWORD PTR [rsi + 160], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_5
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 0], ymm4
  vmovdqu YMMWORD PTR [rsi + 32], ymm5
  vmovdqu YMMWORD PTR [rsi + 64], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_6
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 672], ymm4
  vmovdqu YMMWORD PTR [rsi + 704], ymm5
  vmovdqu YMMWORD PTR [rsi + 736], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_7
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 576], ymm4
  vmovdqu YMMWORD PTR [rsi + 608], ymm5
  vmovdqu YMMWORD PTR [rsi + 640], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_0_8
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 768], ymm4
  vmovdqu YMMWORD PTR [rsi + 800], ymm5
  vmovdqu YMMWORD PTR [rsi + 832], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_0
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 960], ymm4
  vmovdqu YMMWORD PTR [rsi + 992], ymm5
  vmovdqu YMMWORD PTR [rsi + 1024], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_1
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 864], ymm4
  vmovdqu YMMWORD PTR [rsi + 896], ymm5
  vmovdqu YMMWORD PTR [rsi + 928], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_2
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1056], ymm4
  vmovdqu YMMWORD PTR [rsi + 1088], ymm5
  vmovdqu YMMWORD PTR [rsi + 1120], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_3
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1632], ymm4
  vmovdqu YMMWORD PTR [rsi + 1664], ymm5
  vmovdqu YMMWORD PTR [rsi + 1696], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_4
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1536], ymm4
  vmovdqu YMMWORD PTR [rsi + 1568], ymm5
  vmovdqu YMMWORD PTR [rsi + 1600], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_5
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1440], ymm4
  vmovdqu YMMWORD PTR [rsi + 1472], ymm5
  vmovdqu YMMWORD PTR [rsi + 1504], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_6
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1344], ymm4
  vmovdqu YMMWORD PTR [rsi + 1376], ymm5
  vmovdqu YMMWORD PTR [rsi + 1408], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_7
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1248], ymm4
  vmovdqu YMMWORD PTR [rsi + 1280], ymm5
  vmovdqu YMMWORD PTR [rsi + 1312], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE_1_8
  vpmulhrsw ymm14, ymm4, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm14
  vpsraw ymm14, ymm4, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm14
  vpmulhrsw ymm14, ymm5, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm5, ymm5, ymm14
  vpsraw ymm14, ymm5, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm5, ymm5, ymm14
  vpmulhrsw ymm14, ymm6, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm6, ymm6, ymm14
  vpsraw ymm14, ymm6, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm6, ymm6, ymm14
  vpmulhrsw ymm14, ymm7, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm7, ymm7, ymm14
  vpsraw ymm14, ymm7, 15
  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm7, ymm7, ymm14
  vpunpcklwd ymm0, ymm4, ymm5
  vpunpckhwd ymm1, ymm4, ymm5
  vpunpcklwd ymm2, ymm6, ymm7
  vpunpckhwd ymm3, ymm6, ymm7
  vpmaddwd ymm0, ymm0, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm1, ymm1, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm2, ymm2, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpmaddwd ymm3, ymm3, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]
  vpunpckldq ymm4, ymm0, ymm2
  vpunpckhdq ymm5, ymm0, ymm2
  vperm2i128 ymm8, ymm4, ymm5, 0x20
  vperm2i128 ymm9, ymm4, ymm5, 0x31
  vpunpckldq ymm4, ymm1, ymm3
  vpunpckhdq ymm5, ymm1, ymm3
  vperm2i128 ymm6, ymm4, ymm5, 0x20
  vperm2i128 ymm7, ymm4, ymm5, 0x31
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm8, 1
  vextracti128 xmm1, ymm6, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm8
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm6, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm8, xmm6, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm8, xmm8, xmm13
  vmovdqa ymm10, ymm2
  vmovdqa ymm11, ymm3
  vmovdqa ymm12, ymm8
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pack24]
  vextracti128 xmm0, ymm9, 1
  vextracti128 xmm1, ymm7, 1
  vpslldq xmm2, xmm0, 12
  vpor xmm2, xmm2, xmm9
  vpsrldq xmm3, xmm0, 4
  vpslldq xmm13, xmm7, 8
  vpor xmm3, xmm3, xmm13
  vpsrldq xmm9, xmm7, 8
  vpslldq xmm13, xmm1, 4
  vpor xmm9, xmm9, xmm13
  vinserti128 ymm4, ymm10, xmm11, 1
  vinserti128 ymm5, ymm12, xmm2, 1
  vinserti128 ymm6, ymm3, xmm9, 1
  vmovdqu YMMWORD PTR [rsi + 1152], ymm4
  vmovdqu YMMWORD PTR [rsi + 1184], ymm5
  vmovdqu YMMWORD PTR [rsi + 1216], ymm6
.endm

.macro PROD3_R_DUAL_OUTPUT_TILE branch,row
  .if \branch == 0
    .if \row == 0
      PROD3_R_DUAL_OUTPUT_TILE_0_0
    .elseif \row == 1
      PROD3_R_DUAL_OUTPUT_TILE_0_1
    .elseif \row == 2
      PROD3_R_DUAL_OUTPUT_TILE_0_2
    .elseif \row == 3
      PROD3_R_DUAL_OUTPUT_TILE_0_3
    .elseif \row == 4
      PROD3_R_DUAL_OUTPUT_TILE_0_4
    .elseif \row == 5
      PROD3_R_DUAL_OUTPUT_TILE_0_5
    .elseif \row == 6
      PROD3_R_DUAL_OUTPUT_TILE_0_6
    .elseif \row == 7
      PROD3_R_DUAL_OUTPUT_TILE_0_7
    .elseif \row == 8
      PROD3_R_DUAL_OUTPUT_TILE_0_8
    .endif
  .else
    .if \row == 0
      PROD3_R_DUAL_OUTPUT_TILE_1_0
    .elseif \row == 1
      PROD3_R_DUAL_OUTPUT_TILE_1_1
    .elseif \row == 2
      PROD3_R_DUAL_OUTPUT_TILE_1_2
    .elseif \row == 3
      PROD3_R_DUAL_OUTPUT_TILE_1_3
    .elseif \row == 4
      PROD3_R_DUAL_OUTPUT_TILE_1_4
    .elseif \row == 5
      PROD3_R_DUAL_OUTPUT_TILE_1_5
    .elseif \row == 6
      PROD3_R_DUAL_OUTPUT_TILE_1_6
    .elseif \row == 7
      PROD3_R_DUAL_OUTPUT_TILE_1_7
    .elseif \row == 8
      PROD3_R_DUAL_OUTPUT_TILE_1_8
    .endif
  .endif
.endm

.section .rodata,"a",@progbits
.p2align 5
.Lh4_m3b_pair_weight:
  .short 1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096,1,4096
.p2align 5
.Lh4_m3b_pack24:
  .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
.include "generated/f0-ma2-constants.inc"
