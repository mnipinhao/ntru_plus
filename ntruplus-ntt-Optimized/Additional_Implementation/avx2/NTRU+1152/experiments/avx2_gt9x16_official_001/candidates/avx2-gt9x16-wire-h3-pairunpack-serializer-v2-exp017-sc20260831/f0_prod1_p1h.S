.intel_syntax noprefix
.text

.include "gt9x16_ntt9_paper.inc"
.include "gt9x16_ntt16_paper.inc"

/* Four aligned split loads -> two coefficient streams -> branch pre-twist. */
.macro P1H_FORM_ROW split_offset,twist_offset,shuffle_imm,out0,out1
  vmovdqa ymm0, YMMWORD PTR [rsi + \split_offset + 0]
  vmovdqa ymm1, YMMWORD PTR [rsi + \split_offset + 32]
  vmovdqa ymm2, YMMWORD PTR [rsi + \split_offset + 64]
  vmovdqa ymm3, YMMWORD PTR [rsi + \split_offset + 96]
  vpshufd ymm0, ymm0, \shuffle_imm
  vpshufd ymm1, ymm1, \shuffle_imm
  vpshufd ymm2, ymm2, \shuffle_imm
  vpshufd ymm3, ymm3, \shuffle_imm
  vpermq ymm0, ymm0, 0xd8
  vpermq ymm1, ymm1, 0xd8
  vpermq ymm2, ymm2, 0xd8
  vpermq ymm3, ymm3, 0xd8
  vperm2i128 ymm4, ymm0, ymm1, 0x20
  vperm2i128 ymm5, ymm2, ymm3, 0x20
  vpshufb ymm4, ymm4, YMMWORD PTR [rip + .Lf0_prod1_route_mask]
  vpshufb ymm5, ymm5, YMMWORD PTR [rip + .Lf0_prod1_route_mask]
  vpunpcklqdq ymm6, ymm4, ymm5
  vpunpckhqdq ymm7, ymm4, ymm5
  vpermq ymm\out0, ymm6, 0xd8
  vpermq ymm\out1, ymm7, 0xd8
  vpmullw ymm0, ymm\out0, YMMWORD PTR [rdx + \twist_offset + 32]
  vpmulhw ymm\out0, ymm\out0, YMMWORD PTR [rdx + \twist_offset]
  vpmulhw ymm0, ymm0, ymm15
  vpsubw ymm\out0, ymm\out0, ymm0
  vpmullw ymm0, ymm\out1, YMMWORD PTR [rdx + \twist_offset + 32]
  vpmulhw ymm\out1, ymm\out1, YMMWORD PTR [rdx + \twist_offset]
  vpmulhw ymm0, ymm0, ymm15
  vpsubw ymm\out1, ymm\out1, ymm0
.endm

/* Exact PAPER_R3/PAPER_REDUCE arithmetic with scratch registers 0..3. */
.macro P1H_R3 a,b,c
  vpaddw ymm0, ymm\b, ymm\c
  vpsubw ymm1, ymm\b, ymm\c
  vpmullw ymm2, ymm1, ymm4
  vpmulhw ymm1, ymm1, ymm5
  vpmulhw ymm2, ymm2, ymm15
  vpsubw ymm1, ymm1, ymm2
  vpaddw ymm2, ymm\a, ymm\a
  vpsubw ymm3, ymm2, ymm0
  vpaddw ymm\a, ymm2, ymm0
  vpaddw ymm\a, ymm\a, ymm0
  vpaddw ymm\b, ymm3, ymm1
  vpsubw ymm\c, ymm3, ymm1
.endm

.macro P1H_REDUCE x
  vpmulhrsw ymm0, ymm\x, ymm6
  vpmullw ymm0, ymm0, ymm15
  vpsubw ymm\x, ymm\x, ymm0
.endm

.macro P1H_FIRST_GROUP in0,in1,in2,out0,out1,out2,shuffle_imm
  /* source h rows are (5*GT-row) mod 9; each h row is 128 bytes. */
  P1H_FORM_ROW ((5*(\in0)%9)*128),((\in0)*64),\shuffle_imm,8,9
  P1H_FORM_ROW ((5*(\in1)%9)*128),((\in1)*64),\shuffle_imm,10,11
  P1H_FORM_ROW ((5*(\in2)%9)*128),((\in2)*64),\shuffle_imm,12,13
  vmovdqa ymm4, YMMWORD PTR [rip + .Lgt_paper_kappa_qinv]
  vmovdqa ymm5, YMMWORD PTR [rip + .Lgt_paper_kappa]
  vmovdqa ymm6, YMMWORD PTR [rip + .Lgt_v]
  P1H_R3 8,10,12
  P1H_REDUCE 8
  P1H_REDUCE 10
  P1H_REDUCE 12
  P1H_R3 9,11,13
  P1H_REDUCE 9
  P1H_REDUCE 11
  P1H_REDUCE 13
  vmovdqa YMMWORD PTR [rdi + (\out0)*128], ymm8
  vmovdqa YMMWORD PTR [rdi + (\out0)*128 + 32], ymm9
  vmovdqa YMMWORD PTR [rdi + (\out1)*128], ymm10
  vmovdqa YMMWORD PTR [rdi + (\out1)*128 + 32], ymm11
  vmovdqa YMMWORD PTR [rdi + (\out2)*128], ymm12
  vmovdqa YMMWORD PTR [rdi + (\out2)*128 + 32], ymm13
.endm

.macro P1H_FORM_AND_FIRST shuffle_imm
  P1H_FIRST_GROUP 0,3,6,0,3,6,\shuffle_imm
  P1H_FIRST_GROUP 1,4,7,1,4,7,\shuffle_imm
  /* Paper R2 Figure 9(b): rotate addresses, not vector lanes. */
  P1H_FIRST_GROUP 8,2,5,2,5,8,\shuffle_imm
.endm

.macro P1H_SECOND stream,row0,row1,row2,zeta1,qinv1,zeta2,qinv2
  vmovdqa ymm8, YMMWORD PTR [rdi + (\row0)*128 + (\stream)*32]
  vmovdqa ymm9, YMMWORD PTR [rdi + (\row1)*128 + (\stream)*32]
  vmovdqa ymm10, YMMWORD PTR [rdi + (\row2)*128 + (\stream)*32]
  .ifnb \zeta1
    PAPER_MONT_CACHED 9,11,\zeta1,\qinv1
    PAPER_MONT_CACHED 10,11,\zeta2,\qinv2
  .endif
  PAPER_R3 8,9,10
  vmovdqa YMMWORD PTR [rdi + (\row0)*128 + (\stream)*32], ymm8
  vmovdqa YMMWORD PTR [rdi + (\row1)*128 + (\stream)*32], ymm9
  vmovdqa YMMWORD PTR [rdi + (\row2)*128 + (\stream)*32], ymm10
.endm

.macro P1H_R2_SECOND_STREAM stream
  P1H_SECOND \stream,0,1,2,,,,
  P1H_SECOND \stream,3,4,5,5,4,7,6
  P1H_SECOND \stream,6,7,8,7,6,5,4
.endm

.macro P1H_D1_PAIR rowa,rowb
  vmovdqa ymm8, YMMWORD PTR [rdi + (\rowa)*128]
  vmovdqa ymm9, YMMWORD PTR [rdi + (\rowa)*128 + 32]
  vperm2i128 ymm0, ymm8, ymm9, 0x20
  vperm2i128 ymm1, ymm8, ymm9, 0x31
  vmovdqa ymm8, YMMWORD PTR [rdi + (\rowb)*128]
  vmovdqa ymm9, YMMWORD PTR [rdi + (\rowb)*128 + 32]
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
  vmovdqa YMMWORD PTR [rdi + (\rowa)*128], ymm0
  vmovdqa YMMWORD PTR [rdi + (\rowa)*128 + 32], ymm1
  vmovdqa YMMWORD PTR [rdi + (\rowb)*128], ymm2
  vmovdqa YMMWORD PTR [rdi + (\rowb)*128 + 32], ymm3
.endm

.macro P1H_D1_TAIL row
  vmovdqa ymm8, YMMWORD PTR [rdi + (\row)*128]
  vmovdqa ymm9, YMMWORD PTR [rdi + (\row)*128 + 32]
  vperm2i128 ymm0, ymm8, ymm9, 0x20
  vperm2i128 ymm1, ymm8, ymm9, 0x31
  PAPER_D1_MONT_TAIL \row,distance8
  PAPER_D1_ROUTE4 0,1,8
  PAPER_D1_MONT_TAIL \row,distance4
  PAPER_D1_ROUTE2 0,1,8,9
  PAPER_D1_MONT_TAIL \row,distance2
  PAPER_D1_ROUTE1 0,1,8,9
  PAPER_D1_MONT_TAIL \row,distance1
  vmovdqa YMMWORD PTR [rdi + (\row)*128], ymm0
  vmovdqa YMMWORD PTR [rdi + (\row)*128 + 32], ymm1
.endm

.p2align 5
.globl ntruplus1152_exp001_f0_prod1_p1h_pair
.type ntruplus1152_exp001_f0_prod1_p1h_pair,@function
ntruplus1152_exp001_f0_prod1_p1h_pair:
  /* Select branch-local split/output/constant bases once. */
  mov r8d, edx
  mov eax, edx
  imul eax, eax, 1152
  add rsi, rax
  add rdi, rax
  shl rcx, 6
  add rdi, rcx
  lea rax, [rip + .Lf0_prod1_b0_r0_twist]
  lea rdx, [rip + .Lf0_prod1_b1_r0_twist]
  test r8d, r8d
  cmovne rax, rdx
  mov rdx, rax
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  test ecx, ecx
  jnz .Lp1h_pair1_formation

.globl ntruplus1152_exp001_f0_prod1_p1h_formation_pair0_begin
ntruplus1152_exp001_f0_prod1_p1h_formation_pair0_begin:
  P1H_FORM_AND_FIRST 0x88
.globl ntruplus1152_exp001_f0_prod1_p1h_formation_pair0_end
ntruplus1152_exp001_f0_prod1_p1h_formation_pair0_end:
  jmp .Lp1h_r2_second

.p2align 5
.Lp1h_pair1_formation:
.globl ntruplus1152_exp001_f0_prod1_p1h_formation_pair1_begin
ntruplus1152_exp001_f0_prod1_p1h_formation_pair1_begin:
  P1H_FORM_AND_FIRST 0xdd
.globl ntruplus1152_exp001_f0_prod1_p1h_formation_pair1_end
ntruplus1152_exp001_f0_prod1_p1h_formation_pair1_end:

.p2align 5
.Lp1h_r2_second:
.globl ntruplus1152_exp001_f0_prod1_p1h_r2_second_begin
ntruplus1152_exp001_f0_prod1_p1h_r2_second_begin:
  vmovdqa ymm0, YMMWORD PTR [rip + .Lgt_q]
  vmovdqa ymm1, YMMWORD PTR [rip + .Lgt_paper_kappa_qinv]
  vmovdqa ymm2, YMMWORD PTR [rip + .Lgt_paper_kappa]
  vmovdqa ymm3, YMMWORD PTR [rip + .Lgt_v]
  vmovdqa ymm4, YMMWORD PTR [rip + .Lgt_ntt9_qinv4]
  vmovdqa ymm5, YMMWORD PTR [rip + .Lgt_ntt9_zeta4]
  vmovdqa ymm6, YMMWORD PTR [rip + .Lgt_paper_rhoinv_qinv]
  vmovdqa ymm7, YMMWORD PTR [rip + .Lgt_paper_rhoinv]
  P1H_R2_SECOND_STREAM 0
  P1H_R2_SECOND_STREAM 1
.globl ntruplus1152_exp001_f0_prod1_p1h_r2_second_end
ntruplus1152_exp001_f0_prod1_p1h_r2_second_end:

.globl ntruplus1152_exp001_f0_prod1_p1h_d1_begin
ntruplus1152_exp001_f0_prod1_p1h_d1_begin:
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  P1H_D1_PAIR 0,1
  P1H_D1_PAIR 2,3
  P1H_D1_PAIR 4,5
  P1H_D1_PAIR 6,7
  P1H_D1_TAIL 8
.globl ntruplus1152_exp001_f0_prod1_p1h_d1_end
ntruplus1152_exp001_f0_prod1_p1h_d1_end:
  ret
.size ntruplus1152_exp001_f0_prod1_p1h_pair, .-ntruplus1152_exp001_f0_prod1_p1h_pair

.include "gt9x16-ntt16-constants.inc"
.include "gt9x16-paper-adjusted-ntt16-constants.inc"
.include "f0-prod1-constants.inc"

.section .note.GNU-stack,"",@progbits
