/* F-R3C: paper physical-row adjusted NTT16, persistent terminal S/D output. */
.macro PAPER_NTT16_MONT row,stage
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_paper_row\row\()_\stage\()_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_paper_row\row\()_\stage\()_zeta]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11
.endm

.macro PAPER_NTT16_ROW row
  /* Canonical R2 physical row: two independent streams. */
  vmovdqu ymm0, YMMWORD PTR [rsi + (\row)*64]
  vmovdqu ymm1, YMMWORD PTR [rsi + (\row)*64 + 32]
  vextracti128 xmm2, ymm0, 1
  vextracti128 xmm3, ymm1, 1
  vinserti128 ymm10, ymm2, xmm3, 1
  vinserti128 ymm9, ymm0, xmm1, 1
  PAPER_NTT16_MONT \row,distance8

  /* Keep S/D across all remaining layers; no canonical reconstruction. */
  vpunpcklqdq ymm9, ymm13, ymm14
  vpunpckhqdq ymm10, ymm13, ymm14
  PAPER_NTT16_MONT \row,distance4

  vpsllq ymm2, ymm14, 32
  vpsrlq ymm3, ymm13, 32
  vpblendd ymm9, ymm13, ymm2, 0xaa
  vpblendd ymm10, ymm3, ymm14, 0xaa
  PAPER_NTT16_MONT \row,distance2

  vpsllq ymm2, ymm14, 16
  vpsrlq ymm3, ymm13, 16
  vpblendw ymm9, ymm13, ymm2, 0xaa
  vpblendw ymm10, ymm3, ymm14, 0xaa
  PAPER_NTT16_MONT \row,distance1

  vmovdqu YMMWORD PTR [rdi + (\row)*64], ymm13
  vmovdqu YMMWORD PTR [rdi + (\row)*64 + 32], ymm14
.endm

.macro PAPER_ADJUSTED_NTT16_BODY
  PAPER_NTT16_ROW 0
  PAPER_NTT16_ROW 1
  PAPER_NTT16_ROW 2
  PAPER_NTT16_ROW 3
  PAPER_NTT16_ROW 4
  PAPER_NTT16_ROW 5
  PAPER_NTT16_ROW 6
  PAPER_NTT16_ROW 7
  PAPER_NTT16_ROW 8
.endm
