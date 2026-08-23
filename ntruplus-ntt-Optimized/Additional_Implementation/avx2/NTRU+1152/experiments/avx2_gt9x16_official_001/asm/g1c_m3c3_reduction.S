.intel_syntax noprefix
.text

/*
 * M3C3 full-D4 controls. Both functions process exactly 72 YMM vectors.
 * The loop count and addresses are public and fixed. No vzeroupper is emitted.
 */

.globl ntruplus1152_exp001_g1c_m3c3_reduce_barrett
.type ntruplus1152_exp001_g1c_m3c3_reduce_barrett,@function
ntruplus1152_exp001_g1c_m3c3_reduce_barrett:
  vmovdqa ymm8, YMMWORD PTR [rip + .Lm3c3_q]
  vmovdqa ymm9, YMMWORD PTR [rip + .Lm3c3_barrett_recip]
  vmovdqa ymm10, YMMWORD PTR [rip + .Lm3c3_half_q]
  vmovdqa ymm11, YMMWORD PTR [rip + .Lm3c3_negative_half_q]
  xor eax, eax
.Lm3c3_barrett_loop:
  vmovdqu ymm0, YMMWORD PTR [rsi + rax]
  vpmulhrsw ymm1, ymm0, ymm9
  vpmullw ymm1, ymm1, ymm8
  vpsubw ymm0, ymm0, ymm1
  vpcmpgtw ymm1, ymm0, ymm10
  vpand ymm1, ymm1, ymm8
  vpsubw ymm0, ymm0, ymm1
  vpcmpgtw ymm1, ymm11, ymm0
  vpand ymm1, ymm1, ymm8
  vpaddw ymm0, ymm0, ymm1
  vmovdqu YMMWORD PTR [rdi + rax], ymm0
  add eax, 32
  cmp eax, 2304
  jne .Lm3c3_barrett_loop
  ret
.size ntruplus1152_exp001_g1c_m3c3_reduce_barrett, .-ntruplus1152_exp001_g1c_m3c3_reduce_barrett

.globl ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity
.type ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity,@function
ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity:
  vmovdqa ymm8, YMMWORD PTR [rip + .Lm3c3_identity_qinv]
  vmovdqa ymm9, YMMWORD PTR [rip + .Lm3c3_identity]
  vmovdqa ymm10, YMMWORD PTR [rip + .Lm3c3_q]
  xor eax, eax
.Lm3c3_montgomery_loop:
  vmovdqu ymm0, YMMWORD PTR [rsi + rax]
  vpmullw ymm1, ymm0, ymm8
  vpmulhw ymm0, ymm0, ymm9
  vpmulhw ymm1, ymm1, ymm10
  vpsubw ymm0, ymm0, ymm1
  vmovdqu YMMWORD PTR [rdi + rax], ymm0
  add eax, 32
  cmp eax, 2304
  jne .Lm3c3_montgomery_loop
  ret
.size ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity, .-ntruplus1152_exp001_g1c_m3c3_reduce_montgomery_identity

.section .rodata
.p2align 5
.Lm3c3_q:
  .rept 16
  .short 3457
  .endr
.Lm3c3_barrett_recip:
  .rept 16
  .short 9
  .endr
.Lm3c3_half_q:
  .rept 16
  .short 1728
  .endr
.Lm3c3_negative_half_q:
  .rept 16
  .short -1728
  .endr
.Lm3c3_identity_qinv:
  .rept 16
  .short -19
  .endr
.Lm3c3_identity:
  .rept 16
  .short -147
  .endr

.section .note.GNU-stack,"",@progbits
