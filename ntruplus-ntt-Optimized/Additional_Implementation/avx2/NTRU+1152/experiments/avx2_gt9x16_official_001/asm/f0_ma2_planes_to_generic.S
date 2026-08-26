.intel_syntax noprefix
.text

/*
 * Invert the materialized generic-F0 -> MA2 coefficient-plane projection.
 * Both pointers must be 32-byte aligned.  This is a pure permutation: the
 * scale-4 representatives and every signed 16-bit lane are preserved exactly.
 */
.macro F0_UNPROJECT_ROW base
  vmovdqa ymm0, YMMWORD PTR [rsi + \base + 0]
  vmovdqa ymm1, YMMWORD PTR [rsi + \base + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + \base + 0], ymm2
  vmovdqa YMMWORD PTR [rdi + \base + 32], ymm3
  vmovdqa ymm0, YMMWORD PTR [rsi + \base + 64]
  vmovdqa ymm1, YMMWORD PTR [rsi + \base + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vperm2i128 ymm3, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + \base + 64], ymm2
  vmovdqa YMMWORD PTR [rdi + \base + 96], ymm3
.endm

.p2align 5
.globl ntruplus1152_exp001_f0_ma2_planes_to_generic
.type ntruplus1152_exp001_f0_ma2_planes_to_generic,@function
ntruplus1152_exp001_f0_ma2_planes_to_generic:
  .set branch,0
  .rept 2
    .set row,0
    .rept 9
      F0_UNPROJECT_ROW (branch * 1152 + row * 128)
      .set row,row + 1
    .endr
    .set branch,branch + 1
  .endr
  ret
.size ntruplus1152_exp001_f0_ma2_planes_to_generic, .-ntruplus1152_exp001_f0_ma2_planes_to_generic

.section .note.GNU-stack,"",@progbits
