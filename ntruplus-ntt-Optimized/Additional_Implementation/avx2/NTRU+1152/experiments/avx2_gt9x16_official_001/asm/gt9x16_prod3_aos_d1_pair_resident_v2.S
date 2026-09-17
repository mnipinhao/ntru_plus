/* Generated namespaced pair-resident D1 + Serializer V2 prototype. */
#define PROD3_FULL_ONLY 1
#define PROD3_NATURAL_Q 1
#define PROD3_WIRE_MONOTONE 1
#define PROD3_T0_BETA 1
#define PROD3_SCALE1 1
#define PROD3_LAZY_R2_REDUCTIONS 1
#define ntruplus1152_exp001_gt9x16_prod3_aos_full ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r
.include "generated/d1-wire-monotone-absorption.inc"
.include "generated/d1-pair-resident-v2-macros.inc"
.intel_syntax noprefix
.text

/* Exact scaled paper radix-3 arithmetic; data live in ymm7..ymm15. */
.macro PROD3_R3 a,b,c
  vpaddw ymm0, ymm\b, ymm\c
  vpsubw ymm1, ymm\b, ymm\c
  vpmullw ymm2, ymm1, ymm4
  vpmulhw ymm1, ymm1, ymm5
  vpmulhw ymm2, ymm2, ymm6
  vpsubw ymm1, ymm1, ymm2
  vpaddw ymm2, ymm\a, ymm\a
  vpsubw ymm3, ymm2, ymm0
  vpaddw ymm\a, ymm2, ymm0
  vpaddw ymm\a, ymm\a, ymm0
  vpaddw ymm\b, ymm3, ymm1
  vpsubw ymm\c, ymm3, ymm1
.endm

/* Same radix-3 DAG with one rotating temporary.  Physical results are
 * C=out0, B=out1, S=out2; the old A register becomes the next temporary. */
.macro PROD3_R3_LOW a,b,c,s
  vpaddw ymm\s, ymm\b, ymm\c
  vpsubw ymm\b, ymm\b, ymm\c
  vpmullw ymm\c, ymm\b, ymm4
  vpmulhw ymm\b, ymm\b, ymm5
  vpmulhw ymm\c, ymm\c, ymm6
  vpsubw ymm\b, ymm\b, ymm\c
  vpaddw ymm\c, ymm\a, ymm\a
  vpsubw ymm\a, ymm\c, ymm\s
  vpaddw ymm\c, ymm\c, ymm\s
  vpaddw ymm\c, ymm\c, ymm\s
  vpsubw ymm\s, ymm\a, ymm\b
  vpaddw ymm\b, ymm\a, ymm\b
.endm

.macro PROD3_REDUCE x
  vpmulhrsw ymm0, ymm\x, YMMWORD PTR [rip + .Lgt_v]
  vpmullw ymm0, ymm0, ymm6
  vpsubw ymm\x, ymm\x, ymm0
.endm

.macro PROD3_REDUCE_TMP x,tmp
  vpmulhrsw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lgt_v]
  vpmullw ymm\tmp, ymm\tmp, ymm6
  vpsubw ymm\x, ymm\x, ymm\tmp
.endm

.macro PROD3_MONT6 x,tmp,zeta,qinv
  vpmullw ymm\tmp, ymm\x, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\x, ymm\x, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm\tmp, ymm\tmp, ymm6
  vpsubw ymm\x, ymm\x, ymm\tmp
.endm

.macro PROD3_LOAD_TWIST branch,base,row,qblock,reg
  /* Top-split source h is (5*GT-row) mod 9; q/j remain AoS. */
  vmovdqu ymm\reg, YMMWORD PTR [rdi + (\base) + ((5*(\row)%9)*128) + (\qblock)*32]
#ifdef PROD3_T0_BETA
  /* beta_q lives in the branch-specific radix-2 table; alpha_0 is one. */
#ifdef PROD3_SCALE1
  /* H4 caller-wide gauge: every alpha row also absorbs inv4. */
  PROD3_MONT6 \reg,0,.Lprod3_h4s1_b\branch\()_r\row\()_alpha,.Lprod3_h4s1_b\branch\()_r\row\()_alpha_qinv
#else
  .if \row != 0
    PROD3_MONT6 \reg,0,.Lprod3_t0b_b\branch\()_r\row\()_alpha,.Lprod3_t0b_b\branch\()_r\row\()_alpha_qinv
  .endif
#endif
#else
  PROD3_MONT6 \reg,0,.Lprod3_b\branch\()_r\row\()_q\qblock\()_twist,.Lprod3_b\branch\()_r\row\()_q\qblock\()_twist_qinv
#endif
.endm

.macro PROD3_LOAD_TWIST_TMP branch,base,row,qblock,reg,tmp
  vmovdqu ymm\reg, YMMWORD PTR [rdi + (\base) + ((5*(\row)%9)*128) + (\qblock)*32]
  PROD3_MONT6 \reg,\tmp,.Lprod3_h4s1_b\branch\()_r\row\()_alpha,.Lprod3_h4s1_b\branch\()_r\row\()_alpha_qinv
.endm

.macro PROD3_PASS_A branch,base,qblock
  vmovdqa ymm6, YMMWORD PTR [rip + .Lgt_q]
  PROD3_LOAD_TWIST \branch,\base,0,\qblock,7
  PROD3_LOAD_TWIST \branch,\base,1,\qblock,8
  PROD3_LOAD_TWIST \branch,\base,2,\qblock,9
  PROD3_LOAD_TWIST \branch,\base,3,\qblock,10
  PROD3_LOAD_TWIST \branch,\base,4,\qblock,11
  PROD3_LOAD_TWIST \branch,\base,5,\qblock,12
  PROD3_LOAD_TWIST \branch,\base,6,\qblock,13
  PROD3_LOAD_TWIST \branch,\base,7,\qblock,14
  PROD3_LOAD_TWIST \branch,\base,8,\qblock,15

  vmovdqa ymm4, YMMWORD PTR [rip + .Lgt_paper_kappa_qinv]
  vmovdqa ymm5, YMMWORD PTR [rip + .Lgt_paper_kappa]
  PROD3_R3 7,10,13
  PROD3_R3 8,11,14
  /* Paper R2 address rotation: semantic g8,g2,g5 become rows 2,5,8. */
  PROD3_R3 15,9,12
#ifdef PROD3_LAZY_R2_REDUCTIONS
  /* Exact mask 79: twisted b/c inputs reduce in their existing Montgomery. */
  PROD3_REDUCE 7
  PROD3_REDUCE 8
  PROD3_REDUCE 15
  PROD3_REDUCE 10
  PROD3_REDUCE 13
#else
  PROD3_REDUCE 7
  PROD3_REDUCE 8
  PROD3_REDUCE 9
  PROD3_REDUCE 10
  PROD3_REDUCE 11
  PROD3_REDUCE 12
  PROD3_REDUCE 13
  PROD3_REDUCE 14
  PROD3_REDUCE 15
#endif

  /* Second paper-R2 layer; keep all nine vectors resident. */
  PROD3_R3 7,8,15
  PROD3_MONT6 11,0,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4
  PROD3_MONT6 9,0,.Lgt_paper_rhoinv,.Lgt_paper_rhoinv_qinv
  PROD3_R3 10,11,9
  PROD3_MONT6 14,0,.Lgt_paper_rhoinv,.Lgt_paper_rhoinv_qinv
  PROD3_MONT6 12,0,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4
  PROD3_R3 13,14,12

  vmovdqu YMMWORD PTR [rdi + (\base) + 0*128 + (\qblock)*32], ymm7
  vmovdqu YMMWORD PTR [rdi + (\base) + 1*128 + (\qblock)*32], ymm8
  vmovdqu YMMWORD PTR [rdi + (\base) + 2*128 + (\qblock)*32], ymm15
  vmovdqu YMMWORD PTR [rdi + (\base) + 3*128 + (\qblock)*32], ymm10
  vmovdqu YMMWORD PTR [rdi + (\base) + 4*128 + (\qblock)*32], ymm11
  vmovdqu YMMWORD PTR [rdi + (\base) + 5*128 + (\qblock)*32], ymm9
  vmovdqu YMMWORD PTR [rdi + (\base) + 6*128 + (\qblock)*32], ymm13
  vmovdqu YMMWORD PTR [rdi + (\base) + 7*128 + (\qblock)*32], ymm14
  vmovdqu YMMWORD PTR [rdi + (\base) + 8*128 + (\qblock)*32], ymm12
.endm

#ifdef PROD3_WAVEFRONT_W1
/* Retain final p=5 in ymm0..ymm3 across q-blocks.  The selected second-layer
 * group is scheduled between the p=6..8 and p=0..2 groups so its out2 lands
 * back in the q-block-specific retained register. */
.macro PROD3_PASS_A_W1 branch,base,qblock,tmp
  vmovdqa ymm6, YMMWORD PTR [rip + .Lgt_q]
  PROD3_LOAD_TWIST_TMP \branch,\base,0,\qblock,7,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,1,\qblock,8,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,2,\qblock,9,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,3,\qblock,10,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,4,\qblock,11,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,5,\qblock,12,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,6,\qblock,13,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,7,\qblock,14,\tmp
  PROD3_LOAD_TWIST_TMP \branch,\base,8,\qblock,15,\tmp

  vmovdqa ymm4, YMMWORD PTR [rip + .Lgt_paper_kappa_qinv]
  vmovdqa ymm5, YMMWORD PTR [rip + .Lgt_paper_kappa]
  PROD3_R3_LOW 7,10,13,\tmp
  PROD3_R3_LOW 8,11,14,7
  PROD3_R3_LOW 15,9,12,8

  /* Position map after layer 1:
   * x0..x8 = 13,14,12,10,11,9,tmp,7,8; scratch=15. */
  PROD3_REDUCE_TMP 13,15
  PROD3_REDUCE_TMP 14,15
  PROD3_REDUCE_TMP 12,15
  PROD3_REDUCE_TMP 10,15
  PROD3_REDUCE_TMP \tmp,15

  /* First finish p=6..8, freeing the retained q-block register. */
  PROD3_MONT6 7,15,.Lgt_paper_rhoinv,.Lgt_paper_rhoinv_qinv
  PROD3_MONT6 8,15,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4
  PROD3_R3_LOW \tmp,7,8,15

  /* Then p=3..5; out2 (p=5) lands in the retained register. */
  PROD3_MONT6 11,\tmp,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4
  PROD3_MONT6 9,\tmp,.Lgt_paper_rhoinv,.Lgt_paper_rhoinv_qinv
  PROD3_R3_LOW 10,11,9,\tmp

  /* Finish p=0..2 using the now-dead old x3 register as scratch. */
  PROD3_R3_LOW 13,14,12,10

  vmovdqu YMMWORD PTR [rdi + (\base) + 0*128 + (\qblock)*32], ymm12
  vmovdqu YMMWORD PTR [rdi + (\base) + 1*128 + (\qblock)*32], ymm14
  vmovdqu YMMWORD PTR [rdi + (\base) + 2*128 + (\qblock)*32], ymm10
  vmovdqu YMMWORD PTR [rdi + (\base) + 3*128 + (\qblock)*32], ymm9
  vmovdqu YMMWORD PTR [rdi + (\base) + 4*128 + (\qblock)*32], ymm11
  /* p=5 remains live in ymm\tmp. */
  vmovdqu YMMWORD PTR [rdi + (\base) + 6*128 + (\qblock)*32], ymm8
  vmovdqu YMMWORD PTR [rdi + (\base) + 7*128 + (\qblock)*32], ymm7
  vmovdqu YMMWORD PTR [rdi + (\base) + 8*128 + (\qblock)*32], ymm15
.endm
#endif

.macro PROD3_MONT15 x,lo,hi,zeta,qinv
  vpmullw ymm\lo, ymm\x, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\hi, ymm\x, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm\lo, ymm\lo, ymm15
  vpsubw ymm\hi, ymm\hi, ymm\lo
.endm

.macro PROD3_BFLY x,t,lo,hi,zeta,qinv
  PROD3_MONT15 \t,\lo,\hi,\zeta,\qinv
  vpsubw ymm\t, ymm\x, ymm\hi
  vpaddw ymm\x, ymm\x, ymm\hi
.endm

#ifdef PROD3_WIRE_MONOTONE
.macro PROD3_WIRE_GROUP out0,out1,a,b,code,lo,hi
  .if ((\code) & 1)
    .if ((\code) & 2)
      \hi ymm\out0, ymm\b, ymm\a
      \lo ymm\out1, ymm\b, ymm\a
    .else
      \lo ymm\out0, ymm\b, ymm\a
      \hi ymm\out1, ymm\b, ymm\a
    .endif
  .else
    .if ((\code) & 2)
      \hi ymm\out0, ymm\a, ymm\b
      \lo ymm\out1, ymm\a, ymm\b
    .else
      \lo ymm\out0, ymm\a, ymm\b
      \hi ymm\out1, ymm\a, ymm\b
    .endif
  .endif
.endm

.macro PROD3_WIRE_OUTPUT branch,row,coefficient,base,source,qimm,shuffle
  .if \source == 0
    vpermq ymm4, ymm4, \qimm
    .if \shuffle
      vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm4
  .elseif \source == 1
    vpermq ymm5, ymm5, \qimm
    .if \shuffle
      vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm5
  .elseif \source == 2
    vpermq ymm6, ymm6, \qimm
    .if \shuffle
      vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm6
  .else
    vpermq ymm7, ymm7, \qimm
    .if \shuffle
      vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm7
  .endif
.endm
#endif

.macro PROD3_PASS_B branch,base,row,live=0
  /* All four source vectors are loaded before this row is overwritten. */
  .if \live == 0
  vmovdqu ymm0, YMMWORD PTR [rdi + (\base) + (\row)*128 + 0]
  vmovdqu ymm1, YMMWORD PTR [rdi + (\base) + (\row)*128 + 32]
  vmovdqu ymm2, YMMWORD PTR [rdi + (\base) + (\row)*128 + 64]
  vmovdqu ymm3, YMMWORD PTR [rdi + (\base) + (\row)*128 + 96]
  .endif

  /* D8 then D4 preserve contiguous AoS q blocks: zero routing. */
#ifdef PROD3_T0_BETA
  PROD3_BFLY 0,2,4,5,.Lprod3_t0b_b\branch\()_p\row\()_distance8_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance8_qinv
  PROD3_BFLY 1,3,6,7,.Lprod3_t0b_b\branch\()_p\row\()_distance8_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance8_qinv
  PROD3_BFLY 0,1,4,5,.Lprod3_t0b_b\branch\()_p\row\()_distance4_lo_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance4_lo_qinv
  PROD3_BFLY 2,3,6,7,.Lprod3_t0b_b\branch\()_p\row\()_distance4_hi_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance4_hi_qinv
#else
  PROD3_BFLY 0,2,4,5,.Lprod3_b0_p\row\()_distance8_zeta,.Lprod3_b0_p\row\()_distance8_qinv
  PROD3_BFLY 1,3,6,7,.Lprod3_b0_p\row\()_distance8_zeta,.Lprod3_b0_p\row\()_distance8_qinv
  PROD3_BFLY 0,1,4,5,.Lprod3_b0_p\row\()_distance4_lo_zeta,.Lprod3_b0_p\row\()_distance4_lo_qinv
  PROD3_BFLY 2,3,6,7,.Lprod3_b0_p\row\()_distance4_hi_zeta,.Lprod3_b0_p\row\()_distance4_hi_qinv
#endif

  /* Selected C1 D2 packing: each chain owns two four-q blocks. */
  vperm2i128 ymm4, ymm0, ymm1, 0x20
  vperm2i128 ymm5, ymm0, ymm1, 0x31
  vperm2i128 ymm6, ymm2, ymm3, 0x20
  vperm2i128 ymm7, ymm2, ymm3, 0x31
#ifdef PROD3_T0_BETA
  vpmullw ymm8, ymm5, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_lo_qinv]
  vpmullw ymm10, ymm7, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_hi_qinv]
  vpmulhw ymm9, ymm5, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_lo_zeta]
  vpmulhw ymm11, ymm7, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_hi_zeta]
#else
  vpmullw ymm8, ymm5, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance2_lo_qinv]
  vpmullw ymm10, ymm7, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance2_hi_qinv]
  vpmulhw ymm9, ymm5, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance2_lo_zeta]
  vpmulhw ymm11, ymm7, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance2_hi_zeta]
#endif
  vpmulhw ymm8, ymm8, ymm15
  vpmulhw ymm10, ymm10, ymm15
  vpsubw ymm8, ymm9, ymm8
  vpsubw ymm10, ymm11, ymm10
  vpsubw ymm5, ymm4, ymm8
  vpsubw ymm7, ymm6, ymm10
  vpaddw ymm4, ymm4, ymm8
  vpaddw ymm6, ymm6, ymm10

  /* D1 adjacent physical-q pairing. */
  vpunpcklqdq ymm0, ymm4, ymm5
  vpunpckhqdq ymm1, ymm4, ymm5
  vpunpcklqdq ymm2, ymm6, ymm7
  vpunpckhqdq ymm3, ymm6, ymm7
#ifdef PROD3_T0_BETA
#ifdef PROD3_D1_SIGN_ORIENTATION
  vpmullw ymm4, ymm1, YMMWORD PTR [rip + .Lprod3_d1v2_b\branch\()_p\row\()_distance1_lo_qinv]
  vpmullw ymm6, ymm3, YMMWORD PTR [rip + .Lprod3_d1v2_b\branch\()_p\row\()_distance1_hi_qinv]
  vpmulhw ymm5, ymm1, YMMWORD PTR [rip + .Lprod3_d1v2_b\branch\()_p\row\()_distance1_lo_zeta]
  vpmulhw ymm7, ymm3, YMMWORD PTR [rip + .Lprod3_d1v2_b\branch\()_p\row\()_distance1_hi_zeta]
#else
  vpmullw ymm4, ymm1, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_lo_qinv]
  vpmullw ymm6, ymm3, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_hi_qinv]
  vpmulhw ymm5, ymm1, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_lo_zeta]
  vpmulhw ymm7, ymm3, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_hi_zeta]
#endif
#else
  vpmullw ymm4, ymm1, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance1_lo_qinv]
  vpmullw ymm6, ymm3, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance1_hi_qinv]
  vpmulhw ymm5, ymm1, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance1_lo_zeta]
  vpmulhw ymm7, ymm3, YMMWORD PTR [rip + .Lprod3_b0_p\row\()_distance1_hi_zeta]
#endif
  vpmulhw ymm4, ymm4, ymm15
  vpmulhw ymm6, ymm6, ymm15
  vpsubw ymm4, ymm5, ymm4
  vpsubw ymm6, ymm7, ymm6
  vpsubw ymm1, ymm0, ymm4
  vpsubw ymm3, ymm2, ymm6
  vpaddw ymm0, ymm0, ymm4
  vpaddw ymm2, ymm2, ymm6

  /* Live D1 results flow directly into the 16/32/64/128-bit transpose. */
#ifdef PROD3_WIRE_MONOTONE
  PROD3_WIRE_GROUP 4,5,0,1,.Lwire_abs_b\branch\()p\row\()_g0,vpunpcklwd,vpunpckhwd
  PROD3_WIRE_GROUP 6,7,2,3,.Lwire_abs_b\branch\()p\row\()_g1,vpunpcklwd,vpunpckhwd
  PROD3_WIRE_GROUP 0,1,4,5,.Lwire_abs_b\branch\()p\row\()_g2,vpunpckldq,vpunpckhdq
  PROD3_WIRE_GROUP 2,3,6,7,.Lwire_abs_b\branch\()p\row\()_g3,vpunpckldq,vpunpckhdq
  PROD3_WIRE_GROUP 4,5,0,2,.Lwire_abs_b\branch\()p\row\()_g4,vpunpcklqdq,vpunpckhqdq
  PROD3_WIRE_GROUP 6,7,1,3,.Lwire_abs_b\branch\()p\row\()_g5,vpunpcklqdq,vpunpckhqdq
  PROD3_WIRE_OUTPUT \branch,\row,0,\base,.Lwire_abs_b\branch\()p\row\()_o0_src,.Lwire_abs_b\branch\()p\row\()_o0_qimm,.Lwire_abs_b\branch\()p\row\()_o0_shuffle
  PROD3_WIRE_OUTPUT \branch,\row,1,\base,.Lwire_abs_b\branch\()p\row\()_o1_src,.Lwire_abs_b\branch\()p\row\()_o1_qimm,.Lwire_abs_b\branch\()p\row\()_o1_shuffle
  PROD3_WIRE_OUTPUT \branch,\row,2,\base,.Lwire_abs_b\branch\()p\row\()_o2_src,.Lwire_abs_b\branch\()p\row\()_o2_qimm,.Lwire_abs_b\branch\()p\row\()_o2_shuffle
  PROD3_WIRE_OUTPUT \branch,\row,3,\base,.Lwire_abs_b\branch\()p\row\()_o3_src,.Lwire_abs_b\branch\()p\row\()_o3_qimm,.Lwire_abs_b\branch\()p\row\()_o3_shuffle
#ifdef PROD3_R_DUAL_OUTPUT
  /* The four exact wire vectors have been retained for MA2.  A specialized
   * r producer may now consume their live registers into exact hash bytes. */
  PROD3_R_DUAL_OUTPUT_TILE \branch,\row
#endif
#else
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
#ifndef PROD3_NATURAL_Q
  /* Frozen P2-B/MA2 packed-lane order: even physical lanes, then odd. */
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lprod3_b0_ma2_q_mask]
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lprod3_b0_ma2_q_mask]
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lprod3_b0_ma2_q_mask]
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lprod3_b0_ma2_q_mask]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm7, ymm7, 0xd8
#else
  /* C1-natural-Q ABI: retain the transpose's native physical-q lanes. */
#endif
  vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + 0], ymm4
  vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + 32], ymm5
  vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + 64], ymm6
  vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + 96], ymm7
#endif
.endm

/*
 * In-place 1152-byte branch-0 leaf.  The caller supplies the existing
 * top-split branch AoS.  No stronger pointer alignment is required.
 */
#ifndef PROD3_FULL_ONLY
.p2align 5
.globl ntruplus1152_exp001_gt9x16_prod3_aos_branch0
.type ntruplus1152_exp001_gt9x16_prod3_aos_branch0,@function
ntruplus1152_exp001_gt9x16_prod3_aos_branch0:
  PROD3_PASS_A 0,0,0
  PROD3_PASS_A 0,0,1
  PROD3_PASS_A 0,0,2
  PROD3_PASS_A 0,0,3
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  PROD3_PASS_B 0,0,0
  PROD3_PASS_B 0,0,1
  PROD3_PASS_B 0,0,2
  PROD3_PASS_B 0,0,3
  PROD3_PASS_B 0,0,4
  PROD3_PASS_B 0,0,5
  PROD3_PASS_B 0,0,6
  PROD3_PASS_B 0,0,7
  PROD3_PASS_B 0,0,8
  ret
.size ntruplus1152_exp001_gt9x16_prod3_aos_branch0, .-ntruplus1152_exp001_gt9x16_prod3_aos_branch0
#endif

/*
 * In-place 2304-byte full leaf.  This deliberately repeats the proven
 * branch-local machine shape; there is no cross-branch fusion or reschedule.
 */
.p2align 5
.globl ntruplus1152_exp001_gt9x16_prod3_aos_full
.type ntruplus1152_exp001_gt9x16_prod3_aos_full,@function
ntruplus1152_exp001_gt9x16_prod3_aos_full:
  /* Exact two-tile Serializer V2 packet ownership. */
  PROD3_PASS_A 0,0,0
  PROD3_PASS_A 0,0,1
  PROD3_PASS_A 0,0,2
  PROD3_PASS_A 0,0,3
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  vmovdqa ymm14, YMMWORD PTR [rip + _16xv]
  PROD3_PAIR_PACKET 0,0,0,5,0,0,4
  PROD3_PAIR_PACKET 1,0,0,3,0,0,0
  PROD3_PAIR_PACKET 2,0,0,2,0,0,1
  PROD3_PAIR_PACKET 3,0,0,7,0,0,6

  PROD3_PASS_A 1,1152,0
  PROD3_PASS_A 1,1152,1
  PROD3_PASS_A 1,1152,2
  PROD3_PASS_A 1,1152,3
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  vmovdqa ymm14, YMMWORD PTR [rip + _16xv]
  PROD3_PAIR_PACKET 4,0,0,8,1,1152,1
  PROD3_PAIR_PACKET 5,1,1152,0,1,1152,2
  PROD3_PAIR_PACKET 6,1,1152,8,1,1152,7
  PROD3_PAIR_PACKET 7,1,1152,6,1,1152,5
  PROD3_PAIR_PACKET 8,1,1152,4,1,1152,3,1
  ret
.size ntruplus1152_exp001_gt9x16_prod3_aos_full, .-ntruplus1152_exp001_gt9x16_prod3_aos_full

.include "generated/gt9x16-ntt16-constants.inc"
#ifdef PROD3_T0_BETA
.include "generated/gt9x16-prod3-natural-q-t0-beta-constants.inc"
#ifdef PROD3_SCALE1
.include "generated/encap-h4-m3-scale1-producer-constants.inc"
#endif
#else
.include "generated/gt9x16-prod3-aos-branch0-constants.inc"
.include "generated/gt9x16-prod3-aos-branch1-constants.inc"
#endif

.section .note.GNU-stack,"",@progbits

