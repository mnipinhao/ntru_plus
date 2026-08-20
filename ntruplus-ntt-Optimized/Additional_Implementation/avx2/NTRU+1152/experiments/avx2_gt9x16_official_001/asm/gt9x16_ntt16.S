.intel_syntax noprefix
.text

.include "asm/gt9x16_ntt16.inc"

.macro LOAD_ROWS
  vmovdqu ymm0, YMMWORD PTR [rsi + 0]
  vmovdqu ymm1, YMMWORD PTR [rsi + 32]
  vmovdqu ymm2, YMMWORD PTR [rsi + 64]
  vmovdqu ymm3, YMMWORD PTR [rsi + 96]
  vmovdqu ymm4, YMMWORD PTR [rsi + 128]
  vmovdqu ymm5, YMMWORD PTR [rsi + 160]
  vmovdqu ymm6, YMMWORD PTR [rsi + 192]
  vmovdqu ymm7, YMMWORD PTR [rsi + 224]
  vmovdqu ymm8, YMMWORD PTR [rsi + 256]
.endm

.macro STORE_ROWS
  vmovdqu YMMWORD PTR [rdi + 0], ymm0
  vmovdqu YMMWORD PTR [rdi + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + 64], ymm2
  vmovdqu YMMWORD PTR [rdi + 96], ymm3
  vmovdqu YMMWORD PTR [rdi + 128], ymm4
  vmovdqu YMMWORD PTR [rdi + 160], ymm5
  vmovdqu YMMWORD PTR [rdi + 192], ymm6
  vmovdqu YMMWORD PTR [rdi + 224], ymm7
  vmovdqu YMMWORD PTR [rdi + 256], ymm8
.endm

.globl ntruplus1152_exp001_gt9x16_ntt16_c0
.type ntruplus1152_exp001_gt9x16_ntt16_c0,@function
ntruplus1152_exp001_gt9x16_ntt16_c0:
  LOAD_ROWS
  GT9X16_NTT16_C0_BODY
  STORE_ROWS
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c0, .-ntruplus1152_exp001_gt9x16_ntt16_c0

.globl ntruplus1152_exp001_gt9x16_ntt16_c0_repeat
.type ntruplus1152_exp001_gt9x16_ntt16_c0_repeat,@function
ntruplus1152_exp001_gt9x16_ntt16_c0_repeat:
  LOAD_ROWS
  test edx, edx
  jz .Lc0_repeat_done
.p2align 5
.Lc0_repeat_loop:
  GT9X16_NTT16_C0_BODY
  dec edx
  jne .Lc0_repeat_loop
.Lc0_repeat_done:
  STORE_ROWS
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c0_repeat, .-ntruplus1152_exp001_gt9x16_ntt16_c0_repeat

.globl ntruplus1152_exp001_gt9x16_ntt16_c1
.type ntruplus1152_exp001_gt9x16_ntt16_c1,@function
ntruplus1152_exp001_gt9x16_ntt16_c1:
  LOAD_ROWS
  GT9X16_NTT16_C1_BODY
  STORE_ROWS
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c1, .-ntruplus1152_exp001_gt9x16_ntt16_c1

.globl ntruplus1152_exp001_gt9x16_ntt16_c1_repeat
.type ntruplus1152_exp001_gt9x16_ntt16_c1_repeat,@function
ntruplus1152_exp001_gt9x16_ntt16_c1_repeat:
  LOAD_ROWS
  test edx, edx
  jz .Lc1_repeat_done
.p2align 5
.Lc1_repeat_loop:
  GT9X16_NTT16_C1_BODY
  dec edx
  jne .Lc1_repeat_loop
.Lc1_repeat_done:
  STORE_ROWS
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c1_repeat, .-ntruplus1152_exp001_gt9x16_ntt16_c1_repeat

.include "generated/gt9x16-ntt16-constants.inc"

.section .note.GNU-stack,"",@progbits
