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

/* F-R3D0: direct half packing and one resident q, otherwise unchanged. */
.macro PAPER_D0_MONT row,stage
  vpmullw ymm11, ymm10, YMMWORD PTR [rip + .Lgt_paper_row\row\()_\stage\()_qinv]
  vpmulhw ymm12, ymm10, YMMWORD PTR [rip + .Lgt_paper_row\row\()_\stage\()_zeta]
  vpmulhw ymm11, ymm11, ymm15
  vpsubw ymm11, ymm12, ymm11
  vpaddw ymm13, ymm9, ymm11
  vpsubw ymm14, ymm9, ymm11
.endm

.macro PAPER_D0_ROW row
  vmovdqu ymm0, YMMWORD PTR [rsi + (\row)*64]
  vmovdqu ymm1, YMMWORD PTR [rsi + (\row)*64 + 32]
  vperm2i128 ymm9, ymm0, ymm1, 0x20
  vperm2i128 ymm10, ymm0, ymm1, 0x31
  PAPER_D0_MONT \row,distance8
  vpunpcklqdq ymm9, ymm13, ymm14
  vpunpckhqdq ymm10, ymm13, ymm14
  PAPER_D0_MONT \row,distance4
  vpsllq ymm2, ymm14, 32
  vpsrlq ymm3, ymm13, 32
  vpblendd ymm9, ymm13, ymm2, 0xaa
  vpblendd ymm10, ymm3, ymm14, 0xaa
  PAPER_D0_MONT \row,distance2
  vpsllq ymm2, ymm14, 16
  vpsrlq ymm3, ymm13, 16
  vpblendw ymm9, ymm13, ymm2, 0xaa
  vpblendw ymm10, ymm3, ymm14, 0xaa
  PAPER_D0_MONT \row,distance1
  vmovdqu YMMWORD PTR [rdi + (\row)*64], ymm13
  vmovdqu YMMWORD PTR [rdi + (\row)*64 + 32], ymm14
.endm

.macro PAPER_D0_BODY
  .irp row,0,1,2,3,4,5,6,7,8
    PAPER_D0_ROW \row
  .endr
.endm

/* F-R3D1: two independent in-place Montgomery chains in flight. */
.macro PAPER_D1_MONT_PAIR rowa,rowb,stage
  vpmullw ymm4, ymm1, YMMWORD PTR [rip + .Lgt_paper_row\rowa\()_\stage\()_qinv]
  vpmullw ymm6, ymm3, YMMWORD PTR [rip + .Lgt_paper_row\rowb\()_\stage\()_qinv]
  vpmulhw ymm5, ymm1, YMMWORD PTR [rip + .Lgt_paper_row\rowa\()_\stage\()_zeta]
  vpmulhw ymm7, ymm3, YMMWORD PTR [rip + .Lgt_paper_row\rowb\()_\stage\()_zeta]
  vpmulhw ymm4, ymm4, ymm15
  vpmulhw ymm6, ymm6, ymm15
  vpsubw ymm5, ymm5, ymm4
  vpsubw ymm7, ymm7, ymm6
  vpsubw ymm1, ymm0, ymm5
  vpsubw ymm3, ymm2, ymm7
  vpaddw ymm0, ymm0, ymm5
  vpaddw ymm2, ymm2, ymm7
.endm

.macro PAPER_D1_MONT_TAIL row,stage
  vpmullw ymm4, ymm1, YMMWORD PTR [rip + .Lgt_paper_row\row\()_\stage\()_qinv]
  vpmulhw ymm5, ymm1, YMMWORD PTR [rip + .Lgt_paper_row\row\()_\stage\()_zeta]
  vpmulhw ymm4, ymm4, ymm15
  vpsubw ymm5, ymm5, ymm4
  vpsubw ymm1, ymm0, ymm5
  vpaddw ymm0, ymm0, ymm5
.endm

.macro PAPER_D1_ROUTE4 s,d,tmp
  vmovdqa ymm\tmp, ymm\s
  vpunpcklqdq ymm\s, ymm\s, ymm\d
  vpunpckhqdq ymm\d, ymm\tmp, ymm\d
.endm

.macro PAPER_D1_ROUTE2 s,d,tmp0,tmp1
  vpsllq ymm\tmp0, ymm\d, 32
  vpsrlq ymm\tmp1, ymm\s, 32
  vpblendd ymm\s, ymm\s, ymm\tmp0, 0xaa
  vpblendd ymm\d, ymm\tmp1, ymm\d, 0xaa
.endm

.macro PAPER_D1_ROUTE1 s,d,tmp0,tmp1
  vpsllq ymm\tmp0, ymm\d, 16
  vpsrlq ymm\tmp1, ymm\s, 16
  vpblendw ymm\s, ymm\s, ymm\tmp0, 0xaa
  vpblendw ymm\d, ymm\tmp1, ymm\d, 0xaa
.endm

.macro PAPER_D1_PAIR rowa,rowb
  vmovdqu ymm8, YMMWORD PTR [rsi + (\rowa)*64]
  vmovdqu ymm9, YMMWORD PTR [rsi + (\rowa)*64 + 32]
  vperm2i128 ymm0, ymm8, ymm9, 0x20
  vperm2i128 ymm1, ymm8, ymm9, 0x31
  vmovdqu ymm8, YMMWORD PTR [rsi + (\rowb)*64]
  vmovdqu ymm9, YMMWORD PTR [rsi + (\rowb)*64 + 32]
  vperm2i128 ymm2, ymm8, ymm9, 0x20
  vperm2i128 ymm3, ymm8, ymm9, 0x31
  PAPER_D1_MONT_PAIR \rowa,\rowb,distance8
  PAPER_D1_ROUTE4 0,1,8
  PAPER_D1_ROUTE4 2,3,9
  PAPER_D1_MONT_PAIR \rowa,\rowb,distance4
  PAPER_D1_ROUTE2 0,1,8,9
  PAPER_D1_ROUTE2 2,3,8,9
  PAPER_D1_MONT_PAIR \rowa,\rowb,distance2
  PAPER_D1_ROUTE1 0,1,8,9
  PAPER_D1_ROUTE1 2,3,8,9
  PAPER_D1_MONT_PAIR \rowa,\rowb,distance1
  vmovdqu YMMWORD PTR [rdi + (\rowa)*64], ymm0
  vmovdqu YMMWORD PTR [rdi + (\rowa)*64 + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + (\rowb)*64], ymm2
  vmovdqu YMMWORD PTR [rdi + (\rowb)*64 + 32], ymm3
.endm

.macro PAPER_D1_TAIL row
  vmovdqu ymm8, YMMWORD PTR [rsi + (\row)*64]
  vmovdqu ymm9, YMMWORD PTR [rsi + (\row)*64 + 32]
  vperm2i128 ymm0, ymm8, ymm9, 0x20
  vperm2i128 ymm1, ymm8, ymm9, 0x31
  PAPER_D1_MONT_TAIL \row,distance8
  PAPER_D1_ROUTE4 0,1,8
  PAPER_D1_MONT_TAIL \row,distance4
  PAPER_D1_ROUTE2 0,1,8,9
  PAPER_D1_MONT_TAIL \row,distance2
  PAPER_D1_ROUTE1 0,1,8,9
  PAPER_D1_MONT_TAIL \row,distance1
  vmovdqu YMMWORD PTR [rdi + (\row)*64], ymm0
  vmovdqu YMMWORD PTR [rdi + (\row)*64 + 32], ymm1
.endm

.macro PAPER_D1_BODY
  PAPER_D1_PAIR 0,1
  PAPER_D1_PAIR 2,3
  PAPER_D1_PAIR 4,5
  PAPER_D1_PAIR 6,7
  PAPER_D1_TAIL 8
.endm
