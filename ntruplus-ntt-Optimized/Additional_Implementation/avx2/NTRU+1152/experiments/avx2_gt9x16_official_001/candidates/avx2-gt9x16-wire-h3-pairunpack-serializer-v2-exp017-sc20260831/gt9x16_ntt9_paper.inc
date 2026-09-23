/* F-R3B: scaled paper radix-3 variants on persistent [row][stream][lane]. */
.macro PAPER_R3 a,b,c
  vpaddw ymm11, ymm\b, ymm\c
  vpsubw ymm12, ymm\b, ymm\c
  vpmullw ymm13, ymm12, ymm1
  vpmulhw ymm12, ymm12, ymm2
  vpmulhw ymm13, ymm13, ymm0
  vpsubw ymm12, ymm12, ymm13
  vpaddw ymm13, ymm\a, ymm\a
  vpsubw ymm14, ymm13, ymm11
  vpaddw ymm\a, ymm13, ymm11
  vpaddw ymm\a, ymm\a, ymm11
  vpaddw ymm\b, ymm14, ymm12
  vpsubw ymm\c, ymm14, ymm12
.endm

.macro PAPER_REDUCE x,tmp
  vpmulhrsw ymm\tmp, ymm\x, ymm3
  vpmullw ymm\tmp, ymm\tmp, ymm0
  vpsubw ymm\x, ymm\x, ymm\tmp
.endm

.macro PAPER_MONT_MEM x,tmp,zeta,qinv
  vpmullw ymm\tmp, ymm\x, YMMWORD PTR [rip + \qinv]
  vpmulhw ymm\x, ymm\x, YMMWORD PTR [rip + \zeta]
  vpmulhw ymm\tmp, ymm\tmp, ymm0
  vpsubw ymm\x, ymm\x, ymm\tmp
.endm

.macro PAPER_MONT_CACHED x,tmp,zeta,qinv
  vpmullw ymm\tmp, ymm\x, ymm\qinv
  vpmulhw ymm\x, ymm\x, ymm\zeta
  vpmulhw ymm\tmp, ymm\tmp, ymm0
  vpsubw ymm\x, ymm\x, ymm\tmp
.endm

.macro PAPER_FIRST input,output,stream,in0,in1,in2,out0,out1,out2
  vmovdqu ymm8, YMMWORD PTR [\input + (\in0)*64 + (\stream)*32]
  vmovdqu ymm9, YMMWORD PTR [\input + (\in1)*64 + (\stream)*32]
  vmovdqu ymm10, YMMWORD PTR [\input + (\in2)*64 + (\stream)*32]
  PAPER_R3 8,9,10
  PAPER_REDUCE 8,11
  PAPER_REDUCE 9,11
  PAPER_REDUCE 10,11
  vmovdqu YMMWORD PTR [\output + (\out0)*64 + (\stream)*32], ymm8
  vmovdqu YMMWORD PTR [\output + (\out1)*64 + (\stream)*32], ymm9
  vmovdqu YMMWORD PTR [\output + (\out2)*64 + (\stream)*32], ymm10
.endm

.macro PAPER_SECOND_MEMORY output,stream,row0,row1,row2,zeta1,qinv1,zeta2,qinv2
  vmovdqu ymm8, YMMWORD PTR [\output + (\row0)*64 + (\stream)*32]
  vmovdqu ymm9, YMMWORD PTR [\output + (\row1)*64 + (\stream)*32]
  vmovdqu ymm10, YMMWORD PTR [\output + (\row2)*64 + (\stream)*32]
  .ifnb \zeta1
    PAPER_MONT_MEM 9,11,\zeta1,\qinv1
    PAPER_MONT_MEM 10,11,\zeta2,\qinv2
  .endif
  PAPER_R3 8,9,10
  vmovdqu YMMWORD PTR [\output + (\row0)*64 + (\stream)*32], ymm8
  vmovdqu YMMWORD PTR [\output + (\row1)*64 + (\stream)*32], ymm9
  vmovdqu YMMWORD PTR [\output + (\row2)*64 + (\stream)*32], ymm10
.endm

.macro PAPER_SECOND_CACHED output,stream,row0,row1,row2,zeta1,qinv1,zeta2,qinv2
  vmovdqu ymm8, YMMWORD PTR [\output + (\row0)*64 + (\stream)*32]
  vmovdqu ymm9, YMMWORD PTR [\output + (\row1)*64 + (\stream)*32]
  vmovdqu ymm10, YMMWORD PTR [\output + (\row2)*64 + (\stream)*32]
  .ifnb \zeta1
    PAPER_MONT_CACHED 9,11,\zeta1,\qinv1
    PAPER_MONT_CACHED 10,11,\zeta2,\qinv2
  .endif
  PAPER_R3 8,9,10
  vmovdqu YMMWORD PTR [\output + (\row0)*64 + (\stream)*32], ymm8
  vmovdqu YMMWORD PTR [\output + (\row1)*64 + (\stream)*32], ymm9
  vmovdqu YMMWORD PTR [\output + (\row2)*64 + (\stream)*32], ymm10
.endm

.macro PAPER_R1_STREAM stream
  PAPER_FIRST rsi,rdi,\stream,0,3,6,0,3,6
  PAPER_FIRST rsi,rdi,\stream,1,4,7,1,4,7
  PAPER_FIRST rsi,rdi,\stream,2,5,8,2,5,8
  PAPER_SECOND_MEMORY rdi,\stream,0,1,2,,,,
  PAPER_SECOND_MEMORY rdi,\stream,3,4,5,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4,.Lgt_ntt9_zeta5,.Lgt_ntt9_qinv5
  PAPER_SECOND_MEMORY rdi,\stream,6,7,8,.Lgt_ntt9_zeta6,.Lgt_ntt9_qinv6,.Lgt_ntt9_zeta7,.Lgt_ntt9_qinv7
.endm

.macro PAPER_R2_MEMORY_STREAM stream
  PAPER_FIRST rsi,rdi,\stream,0,3,6,0,3,6
  PAPER_FIRST rsi,rdi,\stream,1,4,7,1,4,7
  /* Figure 9(b): address rotation, no vector permutation. */
  PAPER_FIRST rsi,rdi,\stream,8,2,5,2,5,8
  PAPER_SECOND_MEMORY rdi,\stream,0,1,2,,,,
  PAPER_SECOND_MEMORY rdi,\stream,3,4,5,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4,.Lgt_paper_rhoinv,.Lgt_paper_rhoinv_qinv
  PAPER_SECOND_MEMORY rdi,\stream,6,7,8,.Lgt_paper_rhoinv,.Lgt_paper_rhoinv_qinv,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4
.endm

.macro PAPER_R2_CACHED_STREAM stream
  PAPER_FIRST rsi,rdi,\stream,0,3,6,0,3,6
  PAPER_FIRST rsi,rdi,\stream,1,4,7,1,4,7
  PAPER_FIRST rsi,rdi,\stream,8,2,5,2,5,8
  PAPER_SECOND_CACHED rdi,\stream,0,1,2,,,,
  PAPER_SECOND_CACHED rdi,\stream,3,4,5,5,4,7,6
  PAPER_SECOND_CACHED rdi,\stream,6,7,8,7,6,5,4
.endm
