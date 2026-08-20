/*
 * C2 pair-packed arithmetic.  ymm0/ymm1 are the two terminal-coefficient
 * rows.  Every Montgomery operand in ymm10 contains eight unique products
 * from coefficient 0 and eight from coefficient 1.
 */

.macro GT9X16_C2_MONT zeta, qinv
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11
.endm

.macro GT9X16_C2_STAGE4
  vpermq ymm2, ymm0, 0x88
  vpermq ymm3, ymm1, 0x88
  vinserti128 ymm9, ymm2, xmm3, 1
  vpermq ymm4, ymm0, 0xdd
  vpermq ymm5, ymm1, 0xdd
  vinserti128 ymm10, ymm4, xmm5, 1
  GT9X16_C2_MONT .Lgt_c2_stage4_zeta, .Lgt_c2_stage4_qinv
  vpunpcklqdq ymm2, ymm13, ymm14
  vpunpckhqdq ymm3, ymm13, ymm14
  vperm2i128 ymm0, ymm2, ymm3, 0x20
  vperm2i128 ymm1, ymm2, ymm3, 0x31
.endm

.macro GT9X16_C2_STAGE2
  vpshufd ymm2, ymm0, 0xd8
  vpshufd ymm3, ymm1, 0xd8
  vpermq ymm2, ymm2, 0x88
  vpermq ymm3, ymm3, 0x88
  vinserti128 ymm9, ymm2, xmm3, 1
  vpshufd ymm4, ymm0, 0xd8
  vpshufd ymm5, ymm1, 0xd8
  vpermq ymm4, ymm4, 0xdd
  vpermq ymm5, ymm5, 0xdd
  vinserti128 ymm10, ymm4, xmm5, 1
  GT9X16_C2_MONT .Lgt_c2_stage2_zeta, .Lgt_c2_stage2_qinv
  vpunpckldq ymm2, ymm13, ymm14
  vpunpckhdq ymm3, ymm13, ymm14
  vperm2i128 ymm0, ymm2, ymm3, 0x20
  vperm2i128 ymm1, ymm2, ymm3, 0x31
.endm

.macro GT9X16_C2_STAGE1
  vpshufb ymm2, ymm0, YMMWORD PTR [rip + .Lgt_c2_compress_even]
  vpshufb ymm3, ymm1, YMMWORD PTR [rip + .Lgt_c2_compress_even]
  vpermq ymm2, ymm2, 0x88
  vpermq ymm3, ymm3, 0x88
  vinserti128 ymm9, ymm2, xmm3, 1
  vpshufb ymm4, ymm0, YMMWORD PTR [rip + .Lgt_c2_compress_odd]
  vpshufb ymm5, ymm1, YMMWORD PTR [rip + .Lgt_c2_compress_odd]
  vpermq ymm4, ymm4, 0x88
  vpermq ymm5, ymm5, 0x88
  vinserti128 ymm10, ymm4, xmm5, 1
  GT9X16_C2_MONT .Lgt_c2_stage1_zeta, .Lgt_c2_stage1_qinv
  vpunpcklwd ymm2, ymm13, ymm14
  vpunpckhwd ymm3, ymm13, ymm14
  vperm2i128 ymm0, ymm2, ymm3, 0x20
  vperm2i128 ymm1, ymm2, ymm3, 0x31
.endm

.macro GT9X16_C2_LOAD_PREVIOUS_HIGH
  vmovdqu ymm2, YMMWORD PTR [rsi + 256]
  vmovdqu ymm3, YMMWORD PTR [rsi + 544]
  vextracti128 xmm10, ymm2, 1
  vextracti128 xmm11, ymm3, 1
  vinserti128 ymm10, ymm10, xmm11, 1
.endm

.macro GT9X16_C2_ROW offset, finish
  vmovdqu ymm0, YMMWORD PTR [rsi + \offset]
  vmovdqu ymm1, YMMWORD PTR [rsi + 288 + \offset]
  vextracti128 xmm2, ymm0, 1
  vextracti128 xmm3, ymm1, 1
  vinserti128 ymm15, ymm2, xmm3, 1
  vinserti128 ymm9, ymm0, xmm1, 1
  GT9X16_C2_MONT .Lgt_stage8_zeta, .Lgt_stage8_qinv
  vperm2i128 ymm0, ymm13, ymm14, 0x20
  vperm2i128 ymm1, ymm13, ymm14, 0x31
  .if \finish
    GT9X16_C2_STAGE4
    GT9X16_C2_STAGE2
    GT9X16_C2_STAGE1
  .endif
  vmovdqu YMMWORD PTR [rdi + \offset], ymm0
  vmovdqu YMMWORD PTR [rdi + 288 + \offset], ymm1
  vmovdqa ymm10, ymm15
.endm

.macro GT9X16_C2_ROWS finish
  GT9X16_C2_LOAD_PREVIOUS_HIGH
  GT9X16_C2_ROW 0, \finish
  GT9X16_C2_ROW 32, \finish
  GT9X16_C2_ROW 64, \finish
  GT9X16_C2_ROW 96, \finish
  GT9X16_C2_ROW 128, \finish
  GT9X16_C2_ROW 160, \finish
  GT9X16_C2_ROW 192, \finish
  GT9X16_C2_ROW 224, \finish
  GT9X16_C2_ROW 256, \finish
.endm

.macro GT9X16_C2_STAGE8_PAIR_FUNCTION_BODY
  GT9X16_C2_ROWS 0
.endm

.macro GT9X16_C2_FULL_PAIR_FROM_Z_BODY
  GT9X16_C2_ROWS 1
.endm
