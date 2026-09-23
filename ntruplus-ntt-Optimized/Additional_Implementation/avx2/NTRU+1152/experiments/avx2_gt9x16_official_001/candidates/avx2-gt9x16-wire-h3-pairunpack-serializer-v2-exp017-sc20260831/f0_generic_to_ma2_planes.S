.intel_syntax noprefix
.text

/*
 * Materialize the exact MA2 coefficient-plane ABI from the generic F0 ABI.
 * This deliberately preserves the current generic MA2 input geometry: each
 * coefficient plane reloads both source vectors independently.  It is the
 * pricing control, not a new optimized projection.
 */
.macro F0_PROJECT_PLANE source_a,source_b,destination,selector
  vmovdqa ymm0, YMMWORD PTR [rsi + \source_a]
  vmovdqa ymm1, YMMWORD PTR [rsi + \source_b]
  vperm2i128 ymm0, ymm0, ymm1, \selector
  vmovdqa YMMWORD PTR [rdi + \destination], ymm0
.endm

.p2align 5
.globl ntruplus1152_exp001_f0_generic_to_ma2_planes
.type ntruplus1152_exp001_f0_generic_to_ma2_planes,@function
ntruplus1152_exp001_f0_generic_to_ma2_planes:
  .set branch,0
  .rept 2
    .set row,0
    .rept 9
      .set base,(branch * 1152 + row * 128)
      F0_PROJECT_PLANE base + 0,  base + 32, base + 0,  0x20
      F0_PROJECT_PLANE base + 0,  base + 32, base + 32, 0x31
      F0_PROJECT_PLANE base + 64, base + 96, base + 64, 0x20
      F0_PROJECT_PLANE base + 64, base + 96, base + 96, 0x31
      .set row,row + 1
    .endr
    .set branch,branch + 1
  .endr
  ret
.size ntruplus1152_exp001_f0_generic_to_ma2_planes, .-ntruplus1152_exp001_f0_generic_to_ma2_planes

.section .note.GNU-stack,"",@progbits
