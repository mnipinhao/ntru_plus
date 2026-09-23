.intel_syntax noprefix
.text
.globl ntruplus1152_exp001_f0_ma0_to_official
.type ntruplus1152_exp001_f0_ma0_to_official,@function
.p2align 5
ntruplus1152_exp001_f0_ma0_to_official:
  /* Official vector 0: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 672]
  vmovdqa ymm1, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 672]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 0], ymm3
  /* Official vector 1: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 672]
  vmovdqa ymm1, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 672]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 32], ymm3
  /* Official vector 2: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 736]
  vmovdqa ymm1, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 736]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 64], ymm3
  /* Official vector 3: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 736]
  vmovdqa ymm1, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 736]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 96], ymm3
  /* Official vector 4: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 128], ymm3
  /* Official vector 5: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 512]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 160], ymm3
  /* Official vector 6: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 192], ymm3
  /* Official vector 7: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 576]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_0]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 224], ymm3
  /* Official vector 8: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 416]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 256], ymm3
  /* Official vector 9: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 416]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 288], ymm3
  /* Official vector 10: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 480]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 320], ymm3
  /* Official vector 11: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 480]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 352], ymm3
  /* Official vector 12: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 416]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 384], ymm3
  /* Official vector 13: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 0]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 416]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 416], ymm3
  /* Official vector 14: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 480]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 448], ymm3
  /* Official vector 15: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 64]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 480]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_2]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 480], ymm3
  /* Official vector 16: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 288]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 512], ymm3
  /* Official vector 17: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 288]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 544], ymm3
  /* Official vector 18: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 352]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 576], ymm3
  /* Official vector 19: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 352]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 608], ymm3
  /* Official vector 20: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 288]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 640], ymm3
  /* Official vector 21: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 128]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 288]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 672], ymm3
  /* Official vector 22: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 352]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 704], ymm3
  /* Official vector 23: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 192]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 352]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_4]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 736], ymm3
  /* Official vector 24: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 928]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 768], ymm3
  /* Official vector 25: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 928]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 800], ymm3
  /* Official vector 26: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 992]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 832], ymm3
  /* Official vector 27: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 992]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 864], ymm3
  /* Official vector 28: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 928]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 896], ymm3
  /* Official vector 29: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 768]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 928]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 928], ymm3
  /* Official vector 30: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 992]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 960], ymm3
  /* Official vector 31: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 832]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 992]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_6]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 992], ymm3
  /* Official vector 32: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1024], ymm3
  /* Official vector 33: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1056], ymm3
  /* Official vector 34: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1088], ymm3
  /* Official vector 35: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1120], ymm3
  /* Official vector 36: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1056]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1280]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1152], ymm3
  /* Official vector 37: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1056]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1280]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1184], ymm3
  /* Official vector 38: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1120]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1344]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1216], ymm3
  /* Official vector 39: 1 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1120]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1344]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1248], ymm3
  /* Official vector 40: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1184]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1280], ymm3
  /* Official vector 41: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1184]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1312], ymm3
  /* Official vector 42: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1248]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1344], ymm3
  /* Official vector 43: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1248]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1376], ymm3
  /* Official vector 44: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1184]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1408], ymm3
  /* Official vector 45: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1408]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1184]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1440], ymm3
  /* Official vector 46: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1248]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1472], ymm3
  /* Official vector 47: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1472]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_10]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1248]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_9]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1504], ymm3
  /* Official vector 48: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2208]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1536], ymm3
  /* Official vector 49: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2208]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1568], ymm3
  /* Official vector 50: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2272]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1600], ymm3
  /* Official vector 51: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2272]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1632], ymm3
  /* Official vector 52: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2208]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1664], ymm3
  /* Official vector 53: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2048]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2208]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1696], ymm3
  /* Official vector 54: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2272]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1728], ymm3
  /* Official vector 55: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2112]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2272]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_11]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1760], ymm3
  /* Official vector 56: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1952]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1792], ymm3
  /* Official vector 57: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1952]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1824], ymm3
  /* Official vector 58: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2016]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1856], ymm3
  /* Official vector 59: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2016]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1888], ymm3
  /* Official vector 60: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1952]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1920], ymm3
  /* Official vector 61: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1792]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1952]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1952], ymm3
  /* Official vector 62: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2016]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 1984], ymm3
  /* Official vector 63: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1856]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2016]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_13]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2016], ymm3
  /* Official vector 64: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1696]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2048], ymm3
  /* Official vector 65: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1696]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1536]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2080], ymm3
  /* Official vector 66: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1760]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2112], ymm3
  /* Official vector 67: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1760]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1600]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2144], ymm3
  /* Official vector 68: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1696]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2176], ymm3
  /* Official vector 69: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1696]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2208], ymm3
  /* Official vector 70: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1760]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2240], ymm3
  /* Official vector 71: 2 source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_16]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1760]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lma0_mask_15]
  vpor ymm3, ymm3, ymm2
  vmovdqa YMMWORD PTR [rdi + 2272], ymm3
  ret
.size ntruplus1152_exp001_f0_ma0_to_official, .-ntruplus1152_exp001_f0_ma0_to_official

.section .rodata
#include "f0-ma0-adapter-constants.inc"

.section .note.GNU-stack,"",@progbits
