.include "generated/d3-vpmaddwd-asm-masks.inc"

.text

.macro D3_P_TO_MEM src, dst
  vmovdqa   0(\src), %ymm0
  vmovdqa  32(\src), %ymm1
  vmovdqa  64(\src), %ymm2
  vperm2i128 $0x30, %ymm1, %ymm0, %ymm3
  vperm2i128 $0x21, %ymm2, %ymm0, %ymm4
  vperm2i128 $0x30, %ymm2, %ymm1, %ymm5
  vpshufb d3_p_j0_c0(%rip), %ymm3, %ymm6
  vpshufb d3_p_j0_c1(%rip), %ymm4, %ymm7
  vpshufb d3_p_j0_c2(%rip), %ymm5, %ymm8
  vpor %ymm7, %ymm6, %ymm6
  vpor %ymm8, %ymm6, %ymm6
  vmovdqa %ymm6, 0(\dst)
  vpshufb d3_p_j1_c0(%rip), %ymm3, %ymm6
  vpshufb d3_p_j1_c1(%rip), %ymm4, %ymm7
  vpshufb d3_p_j1_c2(%rip), %ymm5, %ymm8
  vpor %ymm7, %ymm6, %ymm6
  vpor %ymm8, %ymm6, %ymm6
  vmovdqa %ymm6, 32(\dst)
  vpshufb d3_p_j2_c0(%rip), %ymm3, %ymm6
  vpshufb d3_p_j2_c1(%rip), %ymm4, %ymm7
  vpshufb d3_p_j2_c2(%rip), %ymm5, %ymm8
  vpor %ymm7, %ymm6, %ymm6
  vpor %ymm8, %ymm6, %ymm6
  vmovdqa %ymm6, 64(\dst)
.endm

.macro D3_MR32 value, temp
  vpmullw d3_qinv_words(%rip), \value, \temp
  vpmaddwd d3_q_even_words(%rip), \temp, \temp
  vpsubd \temp, \value, \value
  vpsrad $16, \value, \value
.endm

.macro D3_PAIR_SUM out, t1, t2, t3, name
  vpshufb d3_pair_a_\name\()_lo_c0(%rip), %ymm0, \out
  vpshufb d3_pair_a_\name\()_lo_c1(%rip), %ymm6, \t1
  vpor \t1, \out, \out
  vpshufb d3_pair_b_\name\()_lo_c0(%rip), %ymm3, \t1
  vpshufb d3_pair_b_\name\()_lo_c1(%rip), %ymm8, \t2
  vpor \t2, \t1, \t1
  vpmaddwd \t1, \out, \out
  D3_MR32 \out, \t1
  vpshufb d3_pair_a_\name\()_hi_c0(%rip), %ymm7, \t1
  vpshufb d3_pair_a_\name\()_hi_c1(%rip), %ymm2, \t2
  vpor \t2, \t1, \t1
  vpshufb d3_pair_b_\name\()_hi_c0(%rip), %ymm9, \t2
  vpshufb d3_pair_b_\name\()_hi_c1(%rip), %ymm5, \t3
  vpor \t3, \t2, \t2
  vpmaddwd \t2, \t1, \t1
  D3_MR32 \t1, \t2
  vpackssdw \t1, \out, \out
  vpermq $0xd8, \out, \out
.endm

.macro D3_MONT_PACKED out, a, b, aq, lo, hi
  vpmullw d3_qinv_words(%rip), \a, \aq
  vpmullw \b, \aq, \lo
  vpmulhw \b, \a, \hi
  vpmulhw d3_q_words(%rip), \lo, \lo
  vpsubw \lo, \hi, \out
.endm

.macro D3_MONT_CONST out, x, table, lo, hi
  vpmullw 0(\table), \x, \lo
  vpmulhw 32(\table), \x, \hi
  vpmulhw d3_q_words(%rip), \lo, \lo
  vpsubw \lo, \hi, \out
.endm

.p2align 5
.global ntruplus864_exp001_d3_tile_baseline
.type ntruplus864_exp001_d3_tile_baseline,@function
ntruplus864_exp001_d3_tile_baseline:
  D3_P_TO_MEM %rsi, %r8
  lea 96(%r8), %r9
  D3_P_TO_MEM %rdx, %r9

  vmovdqa d3_q_words(%rip), %ymm0
  vmovdqa d3_qinv_words(%rip), %ymm15
  vmovdqa   0(%r8), %ymm1
  vmovdqa  32(%r8), %ymm3
  vmovdqa  64(%r8), %ymm5
  vmovdqa  96(%r8), %ymm7
  vmovdqa 128(%r8), %ymm8
  vmovdqa 160(%r8), %ymm9
  vpmullw %ymm15, %ymm5, %ymm6
  vpmullw %ymm15, %ymm3, %ymm4
  vpmullw %ymm15, %ymm1, %ymm2
  vpmullw %ymm6, %ymm7, %ymm10
  vpmullw %ymm4, %ymm8, %ymm12
  vpmullw %ymm2, %ymm9, %ymm14
  vpmulhw %ymm5, %ymm7, %ymm11
  vpmulhw %ymm3, %ymm8, %ymm13
  vpmulhw %ymm1, %ymm9, %ymm15
  vpmulhw %ymm0, %ymm10, %ymm10
  vpmulhw %ymm0, %ymm12, %ymm12
  vpmulhw %ymm0, %ymm14, %ymm14
  vpsubw %ymm10, %ymm11, %ymm10
  vpsubw %ymm12, %ymm13, %ymm12
  vpsubw %ymm14, %ymm15, %ymm14
  vpaddw %ymm10, %ymm12, %ymm10
  vpaddw %ymm10, %ymm14, %ymm10
  vmovdqa %ymm10, 64(%rdi)
  vpmullw %ymm2, %ymm7, %ymm10
  vpmullw %ymm2, %ymm8, %ymm12
  vpmullw %ymm4, %ymm7, %ymm14
  vpmulhw %ymm1, %ymm7, %ymm11
  vpmulhw %ymm1, %ymm8, %ymm13
  vpmulhw %ymm3, %ymm7, %ymm15
  vpmulhw %ymm0, %ymm10, %ymm10
  vpmulhw %ymm0, %ymm12, %ymm12
  vpmulhw %ymm0, %ymm14, %ymm14
  vpsubw %ymm10, %ymm11, %ymm10
  vpsubw %ymm12, %ymm13, %ymm12
  vpsubw %ymm14, %ymm15, %ymm14
  vpaddw %ymm12, %ymm14, %ymm11
  vpmullw %ymm6, %ymm8, %ymm12
  vpmullw %ymm4, %ymm9, %ymm14
  vpmullw %ymm6, %ymm9, %ymm7
  vpmulhw %ymm5, %ymm8, %ymm13
  vpmulhw %ymm3, %ymm9, %ymm15
  vpmulhw %ymm5, %ymm9, %ymm8
  vpmulhw %ymm0, %ymm12, %ymm12
  vpmulhw %ymm0, %ymm14, %ymm14
  vpmulhw %ymm0, %ymm7, %ymm7
  vpsubw %ymm12, %ymm13, %ymm12
  vpsubw %ymm14, %ymm15, %ymm14
  vpsubw %ymm7, %ymm8, %ymm7
  vpaddw %ymm12, %ymm14, %ymm12
  vpmullw 0(%rcx), %ymm12, %ymm3
  vpmullw 0(%rcx), %ymm7, %ymm4
  vpmulhw 32(%rcx), %ymm12, %ymm12
  vpmulhw 32(%rcx), %ymm7, %ymm7
  vpmulhw %ymm0, %ymm3, %ymm3
  vpmulhw %ymm0, %ymm4, %ymm4
  vpsubw %ymm3, %ymm12, %ymm12
  vpsubw %ymm4, %ymm7, %ymm7
  vpaddw %ymm10, %ymm12, %ymm10
  vpaddw %ymm11, %ymm7, %ymm11
  vmovdqa %ymm10, 0(%rdi)
  vmovdqa %ymm11, 32(%rdi)
  vzeroupper
  ret
.size ntruplus864_exp001_d3_tile_baseline, .-ntruplus864_exp001_d3_tile_baseline

.p2align 5
.global ntruplus864_exp001_d3_tile_vpmaddwd
.type ntruplus864_exp001_d3_tile_vpmaddwd,@function
ntruplus864_exp001_d3_tile_vpmaddwd:
  vmovdqa 0(%rsi), %ymm0
  vmovdqa 32(%rsi), %ymm1
  vmovdqa 64(%rsi), %ymm2
  vmovdqa 0(%rdx), %ymm3
  vmovdqa 32(%rdx), %ymm4
  vmovdqa 64(%rdx), %ymm5
  vperm2i128 $0x21, %ymm1, %ymm0, %ymm6
  vperm2i128 $0x21, %ymm2, %ymm1, %ymm7
  vperm2i128 $0x21, %ymm4, %ymm3, %ymm8
  vperm2i128 $0x21, %ymm5, %ymm4, %ymm9
  D3_PAIR_SUM %ymm10, %ymm11, %ymm12, %ymm13, s0
  D3_PAIR_SUM %ymm11, %ymm12, %ymm13, %ymm14, s1
  D3_PAIR_SUM %ymm12, %ymm13, %ymm14, %ymm15, s2

  D3_MONT_PACKED %ymm0, %ymm0, %ymm3, %ymm6, %ymm7, %ymm8
  D3_MONT_PACKED %ymm1, %ymm1, %ymm4, %ymm6, %ymm7, %ymm8
  D3_MONT_PACKED %ymm2, %ymm2, %ymm5, %ymm6, %ymm7, %ymm8

  vperm2i128 $0x30, %ymm1, %ymm0, %ymm3
  vperm2i128 $0x21, %ymm2, %ymm0, %ymm4
  vperm2i128 $0x30, %ymm2, %ymm1, %ymm5
  vpshufb d3_p_j0_c0(%rip), %ymm3, %ymm6
  vpshufb d3_p_j0_c1(%rip), %ymm4, %ymm7
  vpshufb d3_p_j0_c2(%rip), %ymm5, %ymm8
  vpor %ymm7, %ymm6, %ymm6
  vpor %ymm8, %ymm6, %ymm6
  vpshufb d3_p_j1_c0(%rip), %ymm3, %ymm7
  vpshufb d3_p_j1_c1(%rip), %ymm4, %ymm8
  vpshufb d3_p_j1_c2(%rip), %ymm5, %ymm9
  vpor %ymm8, %ymm7, %ymm7
  vpor %ymm9, %ymm7, %ymm7
  vpshufb d3_p_j2_c0(%rip), %ymm3, %ymm8
  vpshufb d3_p_j2_c1(%rip), %ymm4, %ymm9
  vpshufb d3_p_j2_c2(%rip), %ymm5, %ymm13
  vpor %ymm9, %ymm8, %ymm8
  vpor %ymm13, %ymm8, %ymm8

  D3_MONT_CONST %ymm3, %ymm10, %rcx, %ymm4, %ymm5
  D3_MONT_CONST %ymm4, %ymm8, %rcx, %ymm5, %ymm9
  vpaddw %ymm3, %ymm6, %ymm3
  vpaddw %ymm4, %ymm11, %ymm4
  vpaddw %ymm7, %ymm12, %ymm5
  vmovdqa %ymm3, 0(%rdi)
  vmovdqa %ymm4, 32(%rdi)
  vmovdqa %ymm5, 64(%rdi)
  vzeroupper
  ret
.size ntruplus864_exp001_d3_tile_vpmaddwd, .-ntruplus864_exp001_d3_tile_vpmaddwd

.section .note.GNU-stack,"",@progbits
