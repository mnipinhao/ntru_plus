/* Generated pair-resident D1/Serializer V2 macros. */
.macro PAIR_WIRE_OUTPUT branch,row,coefficient,base,source,qimm,shuffle
  .if \source == 0
    vpermq ymm8, ymm8, \qimm
    .if \shuffle
      vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm8
  .elseif \source == 1
    vpermq ymm9, ymm9, \qimm
    .if \shuffle
      vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm9
  .elseif \source == 2
    vpermq ymm10, ymm10, \qimm
    .if \shuffle
      vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm10
  .else
    vpermq ymm11, ymm11, \qimm
    .if \shuffle
      vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm11
  .endif
.endm

.macro PROD3_PASS_B_PAIR_SECOND branch,base,row
  /* ymm4..ymm7 retain the first tile.  The paired input uses ymm0..ymm3. */
  vmovdqu ymm0, YMMWORD PTR [rdi + (\base) + (\row)*128 + 0]
  vmovdqu ymm1, YMMWORD PTR [rdi + (\base) + (\row)*128 + 32]
  vmovdqu ymm2, YMMWORD PTR [rdi + (\base) + (\row)*128 + 64]
  vmovdqu ymm3, YMMWORD PTR [rdi + (\base) + (\row)*128 + 96]

  /* D8/D4: same butterflies, one reusable temporary pair. */
  PROD3_BFLY 0,2,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance8_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance8_qinv
  PROD3_BFLY 1,3,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance8_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance8_qinv
  PROD3_BFLY 0,1,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance4_lo_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance4_lo_qinv
  PROD3_BFLY 2,3,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance4_hi_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance4_hi_qinv

  /* D2: form both pairs, then serialize their Montgomery products. */
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vperm2i128 ymm10, ymm2, ymm3, 0x20
  vperm2i128 ymm11, ymm2, ymm3, 0x31
  vpmullw ymm0, ymm9, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_lo_qinv]
  vpmulhw ymm1, ymm9, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_lo_zeta]
  vpmulhw ymm0, ymm0, ymm15
  vpsubw ymm0, ymm1, ymm0
  vpsubw ymm9, ymm8, ymm0
  vpaddw ymm8, ymm8, ymm0
  vpmullw ymm0, ymm11, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_hi_qinv]
  vpmulhw ymm1, ymm11, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_hi_zeta]
  vpmulhw ymm0, ymm0, ymm15
  vpsubw ymm0, ymm1, ymm0
  vpsubw ymm11, ymm10, ymm0
  vpaddw ymm10, ymm10, ymm0

  /* D1: identical arithmetic with the same reusable temporary pair. */
  vpunpcklqdq ymm0, ymm8, ymm9
  vpunpckhqdq ymm1, ymm8, ymm9
  vpunpcklqdq ymm2, ymm10, ymm11
  vpunpckhqdq ymm3, ymm10, ymm11
  vpmullw ymm8, ymm1, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_lo_qinv]
  vpmulhw ymm9, ymm1, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_lo_zeta]
  vpmulhw ymm8, ymm8, ymm15
  vpsubw ymm8, ymm9, ymm8
  vpsubw ymm1, ymm0, ymm8
  vpaddw ymm0, ymm0, ymm8
  vpmullw ymm8, ymm3, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_hi_qinv]
  vpmulhw ymm9, ymm3, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_hi_zeta]
  vpmulhw ymm8, ymm8, ymm15
  vpsubw ymm8, ymm9, ymm8
  vpsubw ymm3, ymm2, ymm8
  vpaddw ymm2, ymm2, ymm8

  /* Isomorphic wire transpose: final sources are ymm8..ymm11. */
  PROD3_WIRE_GROUP 8,9,0,1,.Lwire_abs_b\branch\()p\row\()_g0,vpunpcklwd,vpunpckhwd
  PROD3_WIRE_GROUP 10,11,2,3,.Lwire_abs_b\branch\()p\row\()_g1,vpunpcklwd,vpunpckhwd
  PROD3_WIRE_GROUP 0,1,8,9,.Lwire_abs_b\branch\()p\row\()_g2,vpunpckldq,vpunpckhdq
  PROD3_WIRE_GROUP 2,3,10,11,.Lwire_abs_b\branch\()p\row\()_g3,vpunpckldq,vpunpckhdq
  PROD3_WIRE_GROUP 8,9,0,2,.Lwire_abs_b\branch\()p\row\()_g4,vpunpcklqdq,vpunpckhqdq
  PROD3_WIRE_GROUP 10,11,1,3,.Lwire_abs_b\branch\()p\row\()_g5,vpunpcklqdq,vpunpckhqdq
  PAIR_WIRE_OUTPUT \branch,\row,0,\base,.Lwire_abs_b\branch\()p\row\()_o0_src,.Lwire_abs_b\branch\()p\row\()_o0_qimm,.Lwire_abs_b\branch\()p\row\()_o0_shuffle
  PAIR_WIRE_OUTPUT \branch,\row,1,\base,.Lwire_abs_b\branch\()p\row\()_o1_src,.Lwire_abs_b\branch\()p\row\()_o1_qimm,.Lwire_abs_b\branch\()p\row\()_o1_shuffle
  PAIR_WIRE_OUTPUT \branch,\row,2,\base,.Lwire_abs_b\branch\()p\row\()_o2_src,.Lwire_abs_b\branch\()p\row\()_o2_qimm,.Lwire_abs_b\branch\()p\row\()_o2_shuffle
  PAIR_WIRE_OUTPUT \branch,\row,3,\base,.Lwire_abs_b\branch\()p\row\()_o3_src,.Lwire_abs_b\branch\()p\row\()_o3_qimm,.Lwire_abs_b\branch\()p\row\()_o3_shuffle
.endm

.macro PROD3_PAIR_SERIALIZE_V2_0
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_1
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_2
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_3
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_4
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_5
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_6
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_7
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2_8
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm4, ymm4, 0xd8
  vpermq ymm8, ymm8, 0xd8
  vperm2i128 ymm0, ymm4, ymm8, 0x20
  vperm2i128 ymm1, ymm4, ymm8, 0x31
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm5, ymm5, 0xd8
  vpermq ymm9, ymm9, 0xd8
  vperm2i128 ymm2, ymm5, ymm9, 0x20
  vperm2i128 ymm3, ymm5, ymm9, 0x31
  vpshufb ymm6, ymm6, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm6, ymm6, 0xd8
  vpermq ymm10, ymm10, 0xd8
  vperm2i128 ymm12, ymm6, ymm10, 0x20
  vperm2i128 ymm13, ymm6, ymm10, 0x31
  vpshufb ymm7, ymm7, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lpair_v2_even_odd]
  vpermq ymm7, ymm7, 0xd8
  vpermq ymm11, ymm11, 0xd8
  vperm2i128 ymm4, ymm7, ymm11, 0x20
  vperm2i128 ymm8, ymm7, ymm11, 0x31
  .att_syntax prefix
  vpmulhrsw %ymm14, %ymm0, %ymm7
  vpmulhrsw %ymm14, %ymm2, %ymm9
  vpmulhrsw %ymm14, %ymm12, %ymm10
  vpmulhrsw %ymm14, %ymm4, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm0,  %ymm0
  vpsubw %ymm9, %ymm2,  %ymm2
  vpsubw %ymm10, %ymm12,  %ymm12
  vpsubw %ymm11, %ymm4,  %ymm4
  
  vpmulhrsw %ymm14, %ymm1, %ymm7
  vpmulhrsw %ymm14, %ymm3, %ymm9
  vpmulhrsw %ymm14, %ymm13, %ymm10
  vpmulhrsw %ymm14, %ymm8, %ymm11
  vpmullw %ymm15, %ymm7, %ymm7
  vpmullw %ymm15, %ymm9, %ymm9
  vpmullw %ymm15, %ymm10, %ymm10
  vpmullw %ymm15, %ymm11, %ymm11
  vpsubw %ymm7, %ymm1,  %ymm1
  vpsubw %ymm9, %ymm3,  %ymm3
  vpsubw %ymm10, %ymm13,  %ymm13
  vpsubw %ymm11, %ymm8, %ymm8
  
  vpsraw $15,    %ymm0,  %ymm7
  vpsraw $15,    %ymm2,  %ymm9
  vpsraw $15,    %ymm12,  %ymm10
  vpsraw $15,    %ymm4,  %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm0,  %ymm0
  vpaddw %ymm9, %ymm2,  %ymm2
  vpaddw %ymm10, %ymm12,  %ymm12
  vpaddw %ymm11, %ymm4,  %ymm4
  
  vpsraw $15,    %ymm1,  %ymm7
  vpsraw $15,    %ymm3,  %ymm9
  vpsraw $15,    %ymm13,  %ymm10
  vpsraw $15,    %ymm8, %ymm11
  vpand  %ymm15,  %ymm7, %ymm7
  vpand  %ymm15,  %ymm9, %ymm9
  vpand  %ymm15,  %ymm10, %ymm10
  vpand  %ymm15,  %ymm11, %ymm11
  vpaddw %ymm7, %ymm1,  %ymm1
  vpaddw %ymm9, %ymm3,  %ymm3
  vpaddw %ymm10, %ymm13,  %ymm13
  vpaddw %ymm11, %ymm8, %ymm8
  
  vpsllw $12,    %ymm2,  %ymm7
  vpsllw $12,    %ymm3,  %ymm9
  vpxor  %ymm7, %ymm0,  %ymm0
  vpxor  %ymm9, %ymm1,  %ymm1
  vpsllw $8,     %ymm12,  %ymm7
  vpsllw $8,     %ymm13,  %ymm9
  vpsrlw $4,     %ymm2,  %ymm10
  vpsrlw $4,     %ymm3,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm2
  vpxor  %ymm9, %ymm11, %ymm3
  vpsllw $4,     %ymm4,  %ymm7
  vpsllw $4,     %ymm8, %ymm9
  vpsrlw $8,     %ymm12,  %ymm10
  vpsrlw $8,     %ymm13,  %ymm11
  vpxor  %ymm7, %ymm10, %ymm12
  vpxor  %ymm9, %ymm11, %ymm13
  
  #shuffle
  vpslld      $16, %ymm2, %ymm8
  vpslld      $16, %ymm1, %ymm5
  vpslld      $16, %ymm13, %ymm6
  vpblendw    $0xAA, %ymm8, %ymm0, %ymm8
  vpblendw    $0xAA, %ymm5, %ymm12, %ymm5
  vpblendw    $0xAA, %ymm6, %ymm3, %ymm6
  
  vpsrlq      $16,   %ymm0, %ymm7
  vpsrlq      $16,   %ymm12, %ymm9
  vpsrlq      $16,   %ymm3, %ymm10
  vpblendw    $0xAA, %ymm2, %ymm7, %ymm7
  vpblendw    $0xAA, %ymm1, %ymm9, %ymm9
  vpblendw    $0xAA, %ymm13, %ymm10, %ymm10
  
  vpsllq      $32,   %ymm5,  %ymm0
  vpsllq      $32,   %ymm7, %ymm2
  vpsllq      $32,   %ymm10, %ymm12
  vpblendd    $0xAA, %ymm0,  %ymm8,  %ymm0
  vpblendd    $0xAA, %ymm2,  %ymm6,  %ymm2
  vpblendd    $0xAA, %ymm12,  %ymm9, %ymm12
  
  vpsrlq      $32,   %ymm8,  %ymm4
  vpsrlq      $32,   %ymm6,  %ymm1
  vpsrlq      $32,   %ymm9, %ymm3
  vpblendd    $0xAA, %ymm5,  %ymm4, %ymm4
  vpblendd    $0xAA, %ymm7, %ymm1, %ymm1
  vpblendd    $0xAA, %ymm10, %ymm3, %ymm3
  
  vpunpcklqdq %ymm2, %ymm0, %ymm13
  vpunpcklqdq %ymm4, %ymm12, %ymm8
  vpunpcklqdq %ymm3, %ymm1, %ymm5
  vpunpckhqdq %ymm2, %ymm0, %ymm6
  vpunpckhqdq %ymm4, %ymm12, %ymm7
  vpunpckhqdq %ymm3, %ymm1, %ymm9
  
  vperm2i128  $0x20, %ymm8,  %ymm13,  %ymm0
  vperm2i128  $0x20, %ymm6,  %ymm5,  %ymm2
  vperm2i128  $0x20, %ymm9, %ymm7, %ymm12
  vperm2i128  $0x31, %ymm8,  %ymm13,  %ymm4
  vperm2i128  $0x31, %ymm6,  %ymm5,  %ymm1
  vperm2i128  $0x31, %ymm9, %ymm7, %ymm3
  
  vmovdqu %ymm0,    (%rsi)
  vmovdqu %ymm2,  32(%rsi)
  vmovdqu %ymm12,  64(%rsi)
  vmovdqu %ymm4,  96(%rsi)
  vmovdqu %ymm1, 128(%rsi)
  vmovdqu %ymm3, 160(%rsi)
  .intel_syntax noprefix
.endm

.macro PROD3_PAIR_SERIALIZE_V2 packet
  .if \packet == 0
    PROD3_PAIR_SERIALIZE_V2_0
  .elseif \packet == 1
    PROD3_PAIR_SERIALIZE_V2_1
  .elseif \packet == 2
    PROD3_PAIR_SERIALIZE_V2_2
  .elseif \packet == 3
    PROD3_PAIR_SERIALIZE_V2_3
  .elseif \packet == 4
    PROD3_PAIR_SERIALIZE_V2_4
  .elseif \packet == 5
    PROD3_PAIR_SERIALIZE_V2_5
  .elseif \packet == 6
    PROD3_PAIR_SERIALIZE_V2_6
  .elseif \packet == 7
    PROD3_PAIR_SERIALIZE_V2_7
  .elseif \packet == 8
    PROD3_PAIR_SERIALIZE_V2_8
  .endif
.endm

.macro PROD3_PAIR_PACKET packet,b0,base0,row0,b1,base1,row1,last=0
  PROD3_PASS_B \b0,\base0,\row0
  PROD3_PASS_B_PAIR_SECOND \b1,\base1,\row1
  PROD3_PAIR_SERIALIZE_V2 \packet
  .if \last == 0
    add rsi, 192
  .endif
.endm

.section .rodata,"a",@progbits
.p2align 5
.Lpair_v2_even_odd:
  .byte 0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15
