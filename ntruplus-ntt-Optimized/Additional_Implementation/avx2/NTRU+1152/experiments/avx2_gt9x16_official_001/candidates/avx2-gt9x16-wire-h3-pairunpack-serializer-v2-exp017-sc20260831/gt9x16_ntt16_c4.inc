/* C4: nine-row persistent pair pipeline; output[row][0:1] = S,D. */
.macro C4_MONT s,d,a,b,t0,t1,zeta,qinv
  vpmullw ymm\t0, ymm\b, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\t1, ymm\b, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm\t0, ymm\t0, YMMWORD PTR [rip + .Lgt_q]
  vpsubw ymm\t0, ymm\t1, ymm\t0
  vpaddw ymm\s, ymm\a, ymm\t0
  vpsubw ymm\d, ymm\a, ymm\t0
.endm
.macro C4_STAGE4 s,d,a,b,t0,t1
  vpunpcklqdq ymm\a, ymm\s, ymm\d
  vpunpckhqdq ymm\b, ymm\s, ymm\d
  C4_MONT \s,\d,\a,\b,\t0,\t1,.Lgt_c2_stage4_zeta,.Lgt_c2_stage4_qinv
.endm
.macro C4_STAGE2 s,d,a,b,t0,t1
  vpsllq ymm\a, ymm\d, 32
  vpsrlq ymm\b, ymm\s, 32
  vpblendd ymm\a, ymm\s, ymm\a, 0xaa
  vpblendd ymm\b, ymm\b, ymm\d, 0xaa
  C4_MONT \s,\d,\a,\b,\t0,\t1,.Lgt_c2_stage2_zeta,.Lgt_c2_stage2_qinv
.endm
.macro C4_STAGE1 s,d,a,b,t0,t1
  vpsllq ymm\a, ymm\d, 16
  vpsrlq ymm\b, ymm\s, 16
  vpblendw ymm\a, ymm\s, ymm\a, 0xaa
  vpblendw ymm\b, ymm\b, ymm\d, 0xaa
  C4_MONT \s,\d,\a,\b,\t0,\t1,.Lgt_c2_stage1_zeta,.Lgt_c2_stage1_qinv
.endm
.macro C4_INIT_PREV
  vmovdqu ymm8, YMMWORD PTR [rsi + 256]
  vmovdqu ymm9, YMMWORD PTR [rsi + 544]
  vextracti128 xmm10, ymm8, 1
  vextracti128 xmm11, ymm9, 1
  vinserti128 ymm15, ymm10, xmm11, 1
.endm
.macro C4_STAGE8 s,d,offset
  vmovdqu ymm8, YMMWORD PTR [rsi + \offset]
  vmovdqu ymm9, YMMWORD PTR [rsi + 288 + \offset]
  vextracti128 xmm10, ymm8, 1
  vextracti128 xmm11, ymm9, 1
  vinserti128 ymm10, ymm10, xmm11, 1
  vinserti128 ymm4, ymm8, xmm9, 1
  C4_MONT \s,\d,4,15,6,7,.Lgt_stage8_zeta,.Lgt_stage8_qinv
  vmovdqa ymm15, ymm10
.endm
.macro C4_STORE s,d,row
  vmovdqu YMMWORD PTR [rdi + (\row)*64], ymm\s
  vmovdqu YMMWORD PTR [rdi + (\row)*64 + 32], ymm\d
.endm
.macro C4_PAIR_ROWS row0,row1
  C4_STAGE8 0,1,(\row0)*32
  C4_STAGE8 2,3,(\row1)*32
  C4_STAGE4 0,1,4,5,6,7
  C4_STAGE4 2,3,4,5,6,7
  C4_STAGE2 0,1,4,5,6,7
  C4_STAGE2 2,3,4,5,6,7
  C4_STAGE1 0,1,4,5,6,7
  C4_STAGE1 2,3,4,5,6,7
  C4_STORE 0,1,\row0
  C4_STORE 2,3,\row1
.endm
.macro C4_FROM_Z_PIPELINED_BODY
  C4_INIT_PREV
  C4_PAIR_ROWS 0,1
  C4_PAIR_ROWS 2,3
  C4_PAIR_ROWS 4,5
  C4_PAIR_ROWS 6,7
  C4_STAGE8 0,1,256
  C4_STAGE4 0,1,4,5,6,7
  C4_STAGE2 0,1,4,5,6,7
  C4_STAGE1 0,1,4,5,6,7
  C4_STORE 0,1,8
.endm
.macro C4_FROM_Z_SEQUENTIAL_BODY
  C4_INIT_PREV
  .irp row,0,1,2,3,4,5,6,7,8
    C4_STAGE8 0,1,(\row)*32
    C4_STAGE4 0,1,4,5,6,7
    C4_STAGE2 0,1,4,5,6,7
    C4_STAGE1 0,1,4,5,6,7
    C4_STORE 0,1,\row
  .endr
.endm

/* Build paired Y[row].high directly while nine paired-low rows remain live. */
.macro C4_BUILD_HIGH row
  vmovdqu xmm9, XMMWORD PTR [rsi + (((\row)+8)%9)*32 + 16]
  .irp lane,1,2,3,4,5,6,7
    vmovdqu xmm10, XMMWORD PTR [rsi + (((\row)+8+\lane)%9)*32 + 16]
    vpblendw xmm9, xmm9, xmm10, (1<<\lane)
  .endr
  vmovdqu xmm11, XMMWORD PTR [rsi + 288 + (((\row)+8)%9)*32 + 16]
  .irp lane,1,2,3,4,5,6,7
    vmovdqu xmm10, XMMWORD PTR [rsi + 288 + (((\row)+8+\lane)%9)*32 + 16]
    vpblendw xmm11, xmm11, xmm10, (1<<\lane)
  .endr
  vinserti128 ymm9, ymm9, xmm11, 1
.endm
.macro C4_NATURAL_ROW row,data
  C4_BUILD_HIGH \row
  vmovdqa ymm13, ymm\data
  C4_MONT \data,12,13,9,10,11,.Lgt_stage8_zeta,.Lgt_stage8_qinv
  C4_STAGE4 \data,12,13,14,10,11
  C4_STAGE2 \data,12,13,14,10,11
  C4_STAGE1 \data,12,13,14,10,11
  C4_STORE \data,12,\row
.endm
.macro C4_BUILD_PAIRED_LOW
  .irp row,0,1,2,3,4,5,6,7,8
    vmovdqu xmm\row, XMMWORD PTR [rsi + (\row)*32]
    vmovdqu xmm9, XMMWORD PTR [rsi + 288 + (\row)*32]
    vinserti128 ymm\row, ymm\row, xmm9, 1
  .endr
  GT9X16_SHEAR
.endm
.macro C4_WITH_SHEAR_BODY
  C4_BUILD_PAIRED_LOW
  C4_NATURAL_ROW 0,0
  C4_NATURAL_ROW 1,1
  C4_NATURAL_ROW 2,2
  C4_NATURAL_ROW 3,3
  C4_NATURAL_ROW 4,4
  C4_NATURAL_ROW 5,5
  C4_NATURAL_ROW 6,6
  C4_NATURAL_ROW 7,7
  C4_NATURAL_ROW 8,8
.endm
