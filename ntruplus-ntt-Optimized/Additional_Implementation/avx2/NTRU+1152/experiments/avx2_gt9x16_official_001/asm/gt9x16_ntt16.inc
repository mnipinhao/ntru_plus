/*
 * Register-only GT NTT16 bodies.
 * Contract: ymm0..ymm8 contain R0..R8 on entry and completed rows on exit.
 * The bodies clobber ymm9..ymm15, make no calls, and touch no stack memory.
 */

.macro GT9X16_SHEAR
  vmovdqa ymm9, ymm0
  vpblendw ymm0, ymm0, ymm1, 0xaa
  vpblendw ymm1, ymm1, ymm2, 0xaa
  vpblendw ymm2, ymm2, ymm3, 0xaa
  vpblendw ymm3, ymm3, ymm4, 0xaa
  vpblendw ymm4, ymm4, ymm5, 0xaa
  vpblendw ymm5, ymm5, ymm6, 0xaa
  vpblendw ymm6, ymm6, ymm7, 0xaa
  vpblendw ymm7, ymm7, ymm8, 0xaa
  vpblendw ymm8, ymm8, ymm9, 0xaa

  vmovdqa ymm9, ymm0
  vpblendw ymm0, ymm0, ymm2, 0xcc
  vpblendw ymm2, ymm2, ymm4, 0xcc
  vpblendw ymm4, ymm4, ymm6, 0xcc
  vpblendw ymm6, ymm6, ymm8, 0xcc
  vpblendw ymm8, ymm8, ymm1, 0xcc
  vpblendw ymm1, ymm1, ymm3, 0xcc
  vpblendw ymm3, ymm3, ymm5, 0xcc
  vpblendw ymm5, ymm5, ymm7, 0xcc
  vpblendw ymm7, ymm7, ymm9, 0xcc

  vmovdqa ymm9, ymm0
  vpblendw ymm0, ymm0, ymm4, 0xf0
  vpblendw ymm4, ymm4, ymm8, 0xf0
  vpblendw ymm8, ymm8, ymm3, 0xf0
  vpblendw ymm3, ymm3, ymm7, 0xf0
  vpblendw ymm7, ymm7, ymm2, 0xf0
  vpblendw ymm2, ymm2, ymm6, 0xf0
  vpblendw ymm6, ymm6, ymm1, 0xf0
  vpblendw ymm1, ymm1, ymm5, 0xf0
  vpblendw ymm5, ymm5, ymm9, 0xf0
.endm

.macro GT9X16_STAGE8_ROW row, next
  vextracti128 xmm10, ymm\next, 1
  vpmullw xmm14, xmm9, XMMWORD PTR [rip + .Lgt_stage8_qinv]
  vpmulhw xmm15, xmm9, XMMWORD PTR [rip + .Lgt_stage8_zeta]
  vpmulhw xmm14, xmm14, XMMWORD PTR [rip + .Lgt_q]
  vpsubw xmm15, xmm15, xmm14
  vpsubw xmm14, xmm\row, xmm15
  vpaddw xmm15, xmm\row, xmm15
  vinserti128 ymm\row, ymm15, xmm14, 1
  vmovdqa xmm9, xmm10
.endm

.macro GT9X16_STAGE8_STREAM
  vextracti128 xmm9, ymm8, 1
  GT9X16_STAGE8_ROW 0, 0
  GT9X16_STAGE8_ROW 1, 1
  GT9X16_STAGE8_ROW 2, 2
  GT9X16_STAGE8_ROW 3, 3
  GT9X16_STAGE8_ROW 4, 4
  GT9X16_STAGE8_ROW 5, 5
  GT9X16_STAGE8_ROW 6, 6
  GT9X16_STAGE8_ROW 7, 7
  GT9X16_STAGE8_ROW 8, 8
.endm

.macro GT9X16_C0_FINISH_ROW row
  vpshufd ymm9, ymm\row, 0x44
  vpshufd ymm10, ymm\row, 0xee
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage4_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage4_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11
  vpblendd ymm\row, ymm13, ymm14, 0xcc

  vpshufd ymm9, ymm\row, 0xa0
  vpshufd ymm10, ymm\row, 0xf5
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage2_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage2_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11
  vpblendd ymm\row, ymm13, ymm14, 0xaa

  vpshufb ymm9, ymm\row, YMMWORD PTR [rip + .Lgt_even_words]
  vpshufb ymm10, ymm\row, YMMWORD PTR [rip + .Lgt_odd_words]
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage1_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage1_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11
  vpblendw ymm\row, ymm13, ymm14, 0xaa
.endm

.macro GT9X16_NTT16_C0_BODY
  GT9X16_SHEAR
  GT9X16_STAGE8_STREAM
  GT9X16_C0_FINISH_ROW 0
  GT9X16_C0_FINISH_ROW 1
  GT9X16_C0_FINISH_ROW 2
  GT9X16_C0_FINISH_ROW 3
  GT9X16_C0_FINISH_ROW 4
  GT9X16_C0_FINISH_ROW 5
  GT9X16_C0_FINISH_ROW 6
  GT9X16_C0_FINISH_ROW 7
  GT9X16_C0_FINISH_ROW 8
.endm

/*
 * C1 keeps the distance-4 plus/minus and distance-2 PP/PM/MP/MM states
 * split until the final distance-1 results are available.  It deliberately
 * trades more Montgomery multiplies for eliminating the two intermediate
 * canonical blends; the benchmark decides whether that trade is useful.
 */
.macro GT9X16_C1_STAGE1 state, suffix
  vpshufb ymm9, ymm\state, YMMWORD PTR [rip + .Lgt_even_words]
  vpshufb ymm10, ymm\state, YMMWORD PTR [rip + .Lgt_odd_words]
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c1_stage1_\suffix\()_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c1_stage1_\suffix\()_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm\state, ymm9, ymm11
  vpsubw ymm12, ymm9, ymm11
  vpblendw ymm\state, ymm\state, ymm12, 0xaa
.endm

.macro GT9X16_C1_FINISH_ROW row
  /* distance 4: row=P, ymm13=M */
  vpshufd ymm9, ymm\row, 0x44
  vpshufd ymm10, ymm\row, 0xee
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage4_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c0_stage4_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm\row, ymm9, ymm11
  vpsubw ymm13, ymm9, ymm11

  /* distance 2 on P: row=PP, ymm14=PM */
  vpshufd ymm9, ymm\row, 0xa0
  vpshufd ymm10, ymm\row, 0xf5
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c1_stage2_plus_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c1_stage2_plus_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm\row, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11

  /* distance 2 on M: ymm13=MP, ymm15=MM */
  vpshufd ymm9, ymm13, 0xa0
  vpshufd ymm10, ymm13, 0xf5
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_c1_stage2_minus_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_c1_stage2_minus_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm15, ymm9, ymm11

  GT9X16_C1_STAGE1 \row, 0
  GT9X16_C1_STAGE1 14, 1
  GT9X16_C1_STAGE1 13, 2
  GT9X16_C1_STAGE1 15, 3

  /* Select canonical dwords 0/4, 1/5, 2/6, and 3/7 once, at the boundary. */
  vpblendd ymm\row, ymm\row, ymm14, 0x22
  vpblendd ymm\row, ymm\row, ymm13, 0x44
  vpblendd ymm\row, ymm\row, ymm15, 0x88
.endm

.macro GT9X16_NTT16_C1_BODY
  GT9X16_SHEAR
  GT9X16_STAGE8_STREAM
  GT9X16_C1_FINISH_ROW 0
  GT9X16_C1_FINISH_ROW 1
  GT9X16_C1_FINISH_ROW 2
  GT9X16_C1_FINISH_ROW 3
  GT9X16_C1_FINISH_ROW 4
  GT9X16_C1_FINISH_ROW 5
  GT9X16_C1_FINISH_ROW 6
  GT9X16_C1_FINISH_ROW 7
  GT9X16_C1_FINISH_ROW 8
.endm
