.intel_syntax noprefix
.text

/*
 * GT9X16-PROD3-AOS-ASM0.
 *
 * Input:  one physical-p row immediately after D4, in AoS order
 *         [q0.j0..j3, q1.j0..j3, ... q15.j0..j3].
 * Output: four MA2-native coefficient planes [j0.q0..q15, ... j3.q0..q15].
 *
 * This row-0 feasibility leaf implements only D2, D1, and the live C1
 * transpose.  It intentionally does not include NTT9, D8, D4, a caller, or a
 * benchmark loop.  rdi/rsi need not be aligned.
 */
.p2align 5
.globl ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0
.type ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0,@function
ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0:
  /* D4-output AoS: four adjacent-q blocks. */
  vmovdqu ymm0, YMMWORD PTR [rsi + 0]
  vmovdqu ymm1, YMMWORD PTR [rsi + 32]
  vmovdqu ymm2, YMMWORD PTR [rsi + 64]
  vmovdqu ymm3, YMMWORD PTR [rsi + 96]
  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_aos_q]

  /* D2: [q0,q1,q4,q5] against [q2,q3,q6,q7], then q8..q15. */
  vperm2i128 ymm4, ymm0, ymm1, 0x20
  vperm2i128 ymm5, ymm0, ymm1, 0x31
  vperm2i128 ymm6, ymm2, ymm3, 0x20
  vperm2i128 ymm7, ymm2, ymm3, 0x31

  vpmullw ymm8, ymm5, YMMWORD PTR [rip + .Lprod3_aos_d2_qinv]
  vpmullw ymm10, ymm7, YMMWORD PTR [rip + .Lprod3_aos_d2_qinv]
  vpmulhw ymm9, ymm5, YMMWORD PTR [rip + .Lprod3_aos_d2_zeta]
  vpmulhw ymm11, ymm7, YMMWORD PTR [rip + .Lprod3_aos_d2_zeta]
  vpmulhw ymm8, ymm8, ymm15
  vpmulhw ymm10, ymm10, ymm15
  vpsubw ymm8, ymm9, ymm8
  vpsubw ymm10, ymm11, ymm10
  vpsubw ymm5, ymm4, ymm8
  vpsubw ymm7, ymm6, ymm10
  vpaddw ymm4, ymm4, ymm8
  vpaddw ymm6, ymm6, ymm10

  /* D1 pairing: even physical q owners in ymm0/2, adjacent odd in ymm1/3. */
  vpunpcklqdq ymm0, ymm4, ymm5
  vpunpckhqdq ymm1, ymm4, ymm5
  vpunpcklqdq ymm2, ymm6, ymm7
  vpunpckhqdq ymm3, ymm6, ymm7

  vpmullw ymm4, ymm1, YMMWORD PTR [rip + .Lprod3_aos_d1_lo_qinv]
  vpmullw ymm6, ymm3, YMMWORD PTR [rip + .Lprod3_aos_d1_hi_qinv]
  vpmulhw ymm5, ymm1, YMMWORD PTR [rip + .Lprod3_aos_d1_lo_zeta]
  vpmulhw ymm7, ymm3, YMMWORD PTR [rip + .Lprod3_aos_d1_hi_zeta]
  vpmulhw ymm4, ymm4, ymm15
  vpmulhw ymm6, ymm6, ymm15
  vpsubw ymm4, ymm5, ymm4
  vpsubw ymm6, ymm7, ymm6
  vpsubw ymm1, ymm0, ymm4
  vpsubw ymm3, ymm2, ymm6
  vpaddw ymm0, ymm0, ymm4
  vpaddw ymm2, ymm2, ymm6

  /*
   * Live D1 results flow directly through the fixed 16/32/64/128-bit
   * hierarchy.  No post-D1 AoS store/reload boundary exists.
   */
  vpunpcklwd ymm4, ymm0, ymm1
  vpunpckhwd ymm5, ymm0, ymm1
  vpunpcklwd ymm6, ymm2, ymm3
  vpunpckhwd ymm7, ymm2, ymm3

  vpunpckldq ymm0, ymm4, ymm5
  vpunpckhdq ymm1, ymm4, ymm5
  vpunpckldq ymm2, ymm6, ymm7
  vpunpckhdq ymm3, ymm6, ymm7

  vpunpcklqdq ymm4, ymm0, ymm2
  vpunpckhqdq ymm5, ymm0, ymm2
  vpunpcklqdq ymm6, ymm1, ymm3
  vpunpckhqdq ymm7, ymm1, ymm3

  vpermq ymm4, ymm4, 0xd8
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm7, ymm7, 0xd8

  vmovdqu YMMWORD PTR [rdi + 0], ymm4
  vmovdqu YMMWORD PTR [rdi + 32], ymm5
  vmovdqu YMMWORD PTR [rdi + 64], ymm6
  vmovdqu YMMWORD PTR [rdi + 96], ymm7
  ret
.size ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0, .-ntruplus1152_exp001_gt9x16_prod3_aos_c1_tile_row0

.include "generated/gt9x16-prod3-aos-tile-constants.inc"

.section .note.GNU-stack,"",@progbits
