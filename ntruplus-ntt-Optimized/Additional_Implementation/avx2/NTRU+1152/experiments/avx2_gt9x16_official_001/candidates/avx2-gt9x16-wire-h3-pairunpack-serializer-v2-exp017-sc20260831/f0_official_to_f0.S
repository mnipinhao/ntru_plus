.intel_syntax noprefix
.text
.globl ntruplus1152_exp001_official_to_f0
.type ntruplus1152_exp001_official_to_f0,@function
.p2align 5
ntruplus1152_exp001_official_to_f0:
  /* F0 vector 0: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 288]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 416]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 0], ymm3
  /* F0 vector 1: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 288]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 416]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 32], ymm3
  /* F0 vector 2: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 480]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 64], ymm3
  /* F0 vector 3: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 480]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 96], ymm3
  /* F0 vector 4: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 672]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 128], ymm3
  /* F0 vector 5: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 672]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 160], ymm3
  /* F0 vector 6: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 576]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 192], ymm3
  /* F0 vector 7: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 576]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 224], ymm3
  /* F0 vector 8: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 672]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 256], ymm3
  /* F0 vector 9: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 512]
  vmovdqa ymm1, YMMWORD PTR [rsi + 544]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 640]
  vmovdqa ymm1, YMMWORD PTR [rsi + 672]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 288], ymm3
  /* F0 vector 10: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 576]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 320], ymm3
  /* F0 vector 11: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 576]
  vmovdqa ymm1, YMMWORD PTR [rsi + 608]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 704]
  vmovdqa ymm1, YMMWORD PTR [rsi + 736]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 352], ymm3
  /* F0 vector 12: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 288]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 416]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 384], ymm3
  /* F0 vector 13: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 256]
  vmovdqa ymm1, YMMWORD PTR [rsi + 288]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 384]
  vmovdqa ymm1, YMMWORD PTR [rsi + 416]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 416], ymm3
  /* F0 vector 14: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 480]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 448], ymm3
  /* F0 vector 15: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 320]
  vmovdqa ymm1, YMMWORD PTR [rsi + 352]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 448]
  vmovdqa ymm1, YMMWORD PTR [rsi + 480]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 480], ymm3
  /* F0 vector 16: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 128]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 512], ymm3
  /* F0 vector 17: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 128]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 544], ymm3
  /* F0 vector 18: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 192]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 576], ymm3
  /* F0 vector 19: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 192]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 608], ymm3
  /* F0 vector 20: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 128]
  vmovdqa ymm1, YMMWORD PTR [rsi + 160]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 640], ymm3
  /* F0 vector 21: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 0]
  vmovdqa ymm1, YMMWORD PTR [rsi + 32]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 672], ymm3
  /* F0 vector 22: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 192]
  vmovdqa ymm1, YMMWORD PTR [rsi + 224]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 704], ymm3
  /* F0 vector 23: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 64]
  vmovdqa ymm1, YMMWORD PTR [rsi + 96]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 736], ymm3
  /* F0 vector 24: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 768]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 768], ymm3
  /* F0 vector 25: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 768]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 800], ymm3
  /* F0 vector 26: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 832]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 992]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 832], ymm3
  /* F0 vector 27: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 832]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 992]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 864], ymm3
  /* F0 vector 28: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 768]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 896], ymm3
  /* F0 vector 29: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 768]
  vmovdqa ymm1, YMMWORD PTR [rsi + 800]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 896]
  vmovdqa ymm1, YMMWORD PTR [rsi + 928]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 928], ymm3
  /* F0 vector 30: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 832]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 992]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 960], ymm3
  /* F0 vector 31: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 832]
  vmovdqa ymm1, YMMWORD PTR [rsi + 864]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 960]
  vmovdqa ymm1, YMMWORD PTR [rsi + 992]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 992], ymm3
  /* F0 vector 32: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1056]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1024], ymm3
  /* F0 vector 33: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1184]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1056], ymm3
  /* F0 vector 34: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1120]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1088], ymm3
  /* F0 vector 35: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1248]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1120], ymm3
  /* F0 vector 36: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1152], ymm3
  /* F0 vector 37: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1184], ymm3
  /* F0 vector 38: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1216], ymm3
  /* F0 vector 39: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_9]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_8]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1248], ymm3
  /* F0 vector 40: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1152]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1184]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1280], ymm3
  /* F0 vector 41: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1024]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1056]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1312], ymm3
  /* F0 vector 42: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1216]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1248]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1344], ymm3
  /* F0 vector 43: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1088]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1120]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1376], ymm3
  /* F0 vector 44: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1408], ymm3
  /* F0 vector 45: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1280]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1312]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1408]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1440]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1440], ymm3
  /* F0 vector 46: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1472], ymm3
  /* F0 vector 47: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1344]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1376]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_7]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1472]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1504]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_6]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1504], ymm3
  /* F0 vector 48: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1536], ymm3
  /* F0 vector 49: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2208]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1568], ymm3
  /* F0 vector 50: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1600], ymm3
  /* F0 vector 51: 1 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2272]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_10]
  vmovdqa ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1632], ymm3
  /* F0 vector 52: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2208]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1664], ymm3
  /* F0 vector 53: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2048]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2080]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2176]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2208]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1696], ymm3
  /* F0 vector 54: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2272]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1728], ymm3
  /* F0 vector 55: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 2112]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2144]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_12]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 2240]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2272]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_11]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1760], ymm3
  /* F0 vector 56: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1952]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1792], ymm3
  /* F0 vector 57: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1952]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1824], ymm3
  /* F0 vector 58: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2016]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1856], ymm3
  /* F0 vector 59: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_14]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2016]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_13]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1888], ymm3
  /* F0 vector 60: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1952]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1920], ymm3
  /* F0 vector 61: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1792]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1824]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1920]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1952]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1952], ymm3
  /* F0 vector 62: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2016]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 1984], ymm3
  /* F0 vector 63: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1856]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1888]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_3]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1984]
  vmovdqa ymm1, YMMWORD PTR [rsi + 2016]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_2]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2016], ymm3
  /* F0 vector 64: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2048], ymm3
  /* F0 vector 65: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2080], ymm3
  /* F0 vector 66: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1760]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2112], ymm3
  /* F0 vector 67: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_5]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1760]
  vperm2i128 ymm2, ymm0, ymm1, 0x31
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_4]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2144], ymm3
  /* F0 vector 68: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2176], ymm3
  /* F0 vector 69: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1536]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1568]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1664]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1696]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2208], ymm3
  /* F0 vector 70: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1760]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2240], ymm3
  /* F0 vector 71: 2 Official source-half groups. */
  vmovdqa ymm0, YMMWORD PTR [rsi + 1600]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1632]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_1]
  vmovdqa ymm3, ymm2
  vmovdqa ymm0, YMMWORD PTR [rsi + 1728]
  vmovdqa ymm1, YMMWORD PTR [rsi + 1760]
  vperm2i128 ymm2, ymm0, ymm1, 0x20
  vpshufb ymm2, ymm2, YMMWORD PTR [rip + .Lofficial_to_f0_mask_0]
  vpor ymm3, ymm3, ymm2
  vpsllw ymm3, ymm3, 2
  vmovdqa YMMWORD PTR [rdi + 2272], ymm3
  ret
.size ntruplus1152_exp001_official_to_f0, .-ntruplus1152_exp001_official_to_f0

.section .rodata
#include "f0-official-to-f0-constants.inc"

.section .note.GNU-stack,"",@progbits
