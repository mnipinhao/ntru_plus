.intel_syntax noprefix
.text

.include "asm/gt9x16_ntt16.inc"

.macro LOAD_ROWS offset=0
  vmovdqu ymm0, YMMWORD PTR [rsi + \offset + 0]
  vmovdqu ymm1, YMMWORD PTR [rsi + \offset + 32]
  vmovdqu ymm2, YMMWORD PTR [rsi + \offset + 64]
  vmovdqu ymm3, YMMWORD PTR [rsi + \offset + 96]
  vmovdqu ymm4, YMMWORD PTR [rsi + \offset + 128]
  vmovdqu ymm5, YMMWORD PTR [rsi + \offset + 160]
  vmovdqu ymm6, YMMWORD PTR [rsi + \offset + 192]
  vmovdqu ymm7, YMMWORD PTR [rsi + \offset + 224]
  vmovdqu ymm8, YMMWORD PTR [rsi + \offset + 256]
.endm

.macro STORE_ROWS offset=0
  vmovdqu YMMWORD PTR [rdi + \offset + 0], ymm0
  vmovdqu YMMWORD PTR [rdi + \offset + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + \offset + 64], ymm2
  vmovdqu YMMWORD PTR [rdi + \offset + 96], ymm3
  vmovdqu YMMWORD PTR [rdi + \offset + 128], ymm4
  vmovdqu YMMWORD PTR [rdi + \offset + 160], ymm5
  vmovdqu YMMWORD PTR [rdi + \offset + 192], ymm6
  vmovdqu YMMWORD PTR [rdi + \offset + 224], ymm7
  vmovdqu YMMWORD PTR [rdi + \offset + 256], ymm8
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

/* Baseline: two independent C0 islands in one call. */
.globl ntruplus1152_exp001_gt9x16_ntt16_c0_pair
.type ntruplus1152_exp001_gt9x16_ntt16_c0_pair,@function
ntruplus1152_exp001_gt9x16_ntt16_c0_pair:
  LOAD_ROWS 0
  GT9X16_NTT16_C0_BODY
  STORE_ROWS 0
  LOAD_ROWS 288
  GT9X16_NTT16_C0_BODY
  STORE_ROWS 288
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c0_pair, .-ntruplus1152_exp001_gt9x16_ntt16_c0_pair

/* Distance-8-only baseline; input is already the verified skewed Z layout. */
.globl ntruplus1152_exp001_gt9x16_stage8_c0_pair
.type ntruplus1152_exp001_gt9x16_stage8_c0_pair,@function
ntruplus1152_exp001_gt9x16_stage8_c0_pair:
  LOAD_ROWS 0
  GT9X16_STAGE8_STREAM
  STORE_ROWS 0
  LOAD_ROWS 288
  GT9X16_STAGE8_STREAM
  STORE_ROWS 288
  ret
.size ntruplus1152_exp001_gt9x16_stage8_c0_pair, .-ntruplus1152_exp001_gt9x16_stage8_c0_pair

.include "asm/gt9x16_ntt16_c2.inc"

.globl ntruplus1152_exp001_gt9x16_stage8_c2_pair
.type ntruplus1152_exp001_gt9x16_stage8_c2_pair,@function
ntruplus1152_exp001_gt9x16_stage8_c2_pair:
  GT9X16_C2_STAGE8_PAIR_FUNCTION_BODY
  ret
.size ntruplus1152_exp001_gt9x16_stage8_c2_pair, .-ntruplus1152_exp001_gt9x16_stage8_c2_pair

.globl ntruplus1152_exp001_gt9x16_ntt16_c2_pair
.type ntruplus1152_exp001_gt9x16_ntt16_c2_pair,@function
ntruplus1152_exp001_gt9x16_ntt16_c2_pair:
  /* Correctness-first shear for each coefficient, materialized once. */
  LOAD_ROWS 0
  GT9X16_SHEAR
  STORE_ROWS 0
  LOAD_ROWS 288
  GT9X16_SHEAR
  STORE_ROWS 288
  /* Consume the skewed rows pair-packed and finish all four stages per row. */
  mov rsi, rdi
  GT9X16_C2_FULL_PAIR_FROM_Z_BODY
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c2_pair, .-ntruplus1152_exp001_gt9x16_ntt16_c2_pair

.globl ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair
.type ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair,@function
ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair:
  GT9X16_C2_ROW_PAIR_BODY
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair, .-ntruplus1152_exp001_gt9x16_ntt16_c2_row_pair

.globl ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair
.type ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair,@function
ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair:
  GT9X16_C3_ROW_PAIR_BODY
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair, .-ntruplus1152_exp001_gt9x16_ntt16_c3_row_pair

.include "asm/gt9x16_ntt16_c4.inc"
.globl ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential
.type ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential,@function
ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential:
  C4_FROM_Z_SEQUENTIAL_BODY
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential, .-ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_sequential
.globl ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined
.type ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined,@function
ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined:
  C4_FROM_Z_PIPELINED_BODY
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined, .-ntruplus1152_exp001_gt9x16_ntt16_c4_from_z_pipelined
.globl ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear
.type ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear,@function
ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear:
  C4_WITH_SHEAR_BODY
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear, .-ntruplus1152_exp001_gt9x16_ntt16_c4_with_shear
.globl ntruplus1152_exp001_gt9x16_ntt16_c4_probe_row0
.type ntruplus1152_exp001_gt9x16_ntt16_c4_probe_row0,@function
ntruplus1152_exp001_gt9x16_ntt16_c4_probe_row0:
  C4_BUILD_PAIRED_LOW
  vmovdqu YMMWORD PTR [rdi], ymm0
  C4_BUILD_HIGH 0
  vmovdqu YMMWORD PTR [rdi + 32], ymm9
  ret
.size ntruplus1152_exp001_gt9x16_ntt16_c4_probe_row0, .-ntruplus1152_exp001_gt9x16_ntt16_c4_probe_row0

.include "asm/gt9x16_ntt9.inc"
.globl ntruplus1152_exp001_gt9x16_ntt9_d_a
.type ntruplus1152_exp001_gt9x16_ntt9_d_a,@function
ntruplus1152_exp001_gt9x16_ntt9_d_a:
  vmovdqa ymm0, YMMWORD PTR [rip + .Lgt_q]
  NTT9_STREAM 0
  NTT9_STREAM 1
  ret
.size ntruplus1152_exp001_gt9x16_ntt9_d_a, .-ntruplus1152_exp001_gt9x16_ntt9_d_a

.include "generated/gt9x16-ntt16-constants.inc"

.section .note.GNU-stack,"",@progbits
