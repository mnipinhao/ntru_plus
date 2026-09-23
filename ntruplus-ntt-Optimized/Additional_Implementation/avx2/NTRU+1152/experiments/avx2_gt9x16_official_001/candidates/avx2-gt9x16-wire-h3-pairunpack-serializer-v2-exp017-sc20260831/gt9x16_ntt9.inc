/* D-A: two-layer radix-3 NTT9 directly on state[row][S_or_D][lane]. */
.macro NTT9_RADIX3 a,b,c,zeta1,qinv1,zeta2,qinv2
  vmovdqa ymm4, YMMWORD PTR [rip + \qinv1]
  vmovdqa ymm5, YMMWORD PTR [rip + \qinv2]
  vmovdqa ymm6, YMMWORD PTR [rip + \zeta1]
  vmovdqa ymm7, YMMWORD PTR [rip + \zeta2]

  vpmullw ymm11, ymm\b, ymm4
  vpmullw ymm12, ymm\c, ymm5
  vpmulhw ymm\b, ymm\b, ymm6
  vpmulhw ymm\c, ymm\c, ymm7
  vpmulhw ymm11, ymm11, ymm0
  vpmulhw ymm12, ymm12, ymm0
  vpsubw ymm\b, ymm\b, ymm11
  vpsubw ymm\c, ymm\c, ymm12

  vpsubw ymm11, ymm\b, ymm\c
  vpmullw ymm12, ymm11, YMMWORD PTR [rip + .Lgt_wqinv]
  vpmulhw ymm11, ymm11, YMMWORD PTR [rip + .Lgt_w]
  vpmulhw ymm12, ymm12, ymm0
  vpsubw ymm11, ymm11, ymm12

  vpaddw ymm12, ymm\a, ymm\b
  vpsubw ymm13, ymm\a, ymm\c
  vpsubw ymm14, ymm\a, ymm\b
  vpaddw ymm\a, ymm12, ymm\c
  vpaddw ymm\b, ymm13, ymm11
  vpsubw ymm\c, ymm14, ymm11
.endm

.macro NTT9_TRIPLE input,output,stream,row0,row1,row2,zeta1,qinv1,zeta2,qinv2
  vmovdqu ymm8, YMMWORD PTR [\input + (\row0)*64 + (\stream)*32]
  vmovdqu ymm9, YMMWORD PTR [\input + (\row1)*64 + (\stream)*32]
  vmovdqu ymm10, YMMWORD PTR [\input + (\row2)*64 + (\stream)*32]
  NTT9_RADIX3 8,9,10,\zeta1,\qinv1,\zeta2,\qinv2
  vmovdqu YMMWORD PTR [\output + (\row0)*64 + (\stream)*32], ymm8
  vmovdqu YMMWORD PTR [\output + (\row1)*64 + (\stream)*32], ymm9
  vmovdqu YMMWORD PTR [\output + (\row2)*64 + (\stream)*32], ymm10
.endm

.macro NTT9_STREAM stream
  /* Layer 1: distance three, common unity roots. */
  NTT9_TRIPLE rsi,rdi,\stream,0,3,6,.Lgt_ntt9_zeta0,.Lgt_ntt9_qinv0,.Lgt_ntt9_zeta1,.Lgt_ntt9_qinv1
  NTT9_TRIPLE rsi,rdi,\stream,1,4,7,.Lgt_ntt9_zeta0,.Lgt_ntt9_qinv0,.Lgt_ntt9_zeta1,.Lgt_ntt9_qinv1
  NTT9_TRIPLE rsi,rdi,\stream,2,5,8,.Lgt_ntt9_zeta0,.Lgt_ntt9_qinv0,.Lgt_ntt9_zeta1,.Lgt_ntt9_qinv1
  /* Intentional clean memory boundary, matching Official's two layers. */
  NTT9_TRIPLE rdi,rdi,\stream,0,1,2,.Lgt_ntt9_zeta2,.Lgt_ntt9_qinv2,.Lgt_ntt9_zeta3,.Lgt_ntt9_qinv3
  NTT9_TRIPLE rdi,rdi,\stream,3,4,5,.Lgt_ntt9_zeta4,.Lgt_ntt9_qinv4,.Lgt_ntt9_zeta5,.Lgt_ntt9_qinv5
  NTT9_TRIPLE rdi,rdi,\stream,6,7,8,.Lgt_ntt9_zeta6,.Lgt_ntt9_qinv6,.Lgt_ntt9_zeta7,.Lgt_ntt9_qinv7
.endm
